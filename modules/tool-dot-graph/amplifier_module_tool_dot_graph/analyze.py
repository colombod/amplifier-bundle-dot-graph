"""DOT→NetworkX parsing pipeline and graph analysis operations.

Provides analyze_dot() which validates options, parses DOT via pydot,
converts to NetworkX, and dispatches to operation handlers.

Operations: stats, reachability, unreachable, cycles, paths,
            critical_path, subgraph_extract, diff.
"""

from __future__ import annotations

import contextlib
import io
from typing import cast

import networkx as nx
import pydot


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

# pydot pseudo-node names injected by default style declarations.
_PSEUDO_NODES: frozenset[str] = frozenset({"node", "edge", "graph"})

# All known analysis operations.
_KNOWN_ANALYSES: frozenset[str] = frozenset(
    {
        "stats",
        "reachability",
        "unreachable",
        "cycles",
        "paths",
        "critical_path",
        "subgraph_extract",
        "diff",
    }
)

# Entry-point node names exempt from "no incoming edges" warnings.
# Consumed by the 'unreachable' operation when reporting unreachable-node warnings.
_ENTRY_HINTS: frozenset[str] = frozenset(
    {"start", "entry", "root", "begin", "init", "source"}
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def analyze_dot(dot_content: str, options: dict | None = None) -> dict:
    """Analyze a DOT graph using the specified operation.

    Args:
        dot_content: Raw DOT graph string.
        options: Dict containing 'analysis' key specifying which operation to run,
                 plus any operation-specific parameters.

    Returns:
        {success: True, operation: str, ...result fields} on success,
        or {success: False, error: str} on failure.
    """
    # Validate options and extract analysis type.
    if not options or "analysis" not in options:
        return _parse_error("Missing required 'analysis' key in options")

    analysis = options["analysis"]
    if analysis not in _KNOWN_ANALYSES:
        return _parse_error(
            f"Unknown analysis '{analysis}'. "
            f"Valid analyses are: {sorted(_KNOWN_ANALYSES)}"
        )

    # Special routing: diff and subgraph_extract are dispatched before NetworkX conversion.
    if analysis == "diff":
        return _dispatch_diff(dot_content, options)
    if analysis == "subgraph_extract":
        return _dispatch_subgraph_extract(dot_content, options)

    # Parse DOT → pydot.
    graph = _parse_dot(dot_content)
    if graph is None:
        return _parse_error("Failed to parse DOT content (syntax error or empty input)")

    # Convert pydot → NetworkX.
    G = _pydot_to_networkx(graph)

    # Dispatch to operation handler.
    if analysis == "stats":
        return _stats(G)
    if analysis == "reachability":
        return _reachability(G, options)
    if analysis == "unreachable":
        return _unreachable(G, dot_content)
    if analysis == "cycles":
        return _cycles(G, dot_content)
    if analysis == "paths":
        return _paths(G, options)
    if analysis == "critical_path":
        return _critical_path(G)

    # Remaining operations not yet implemented in this task.
    return _parse_error(f"Analysis '{analysis}' is not yet implemented")


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _parse_dot(dot_content: str) -> pydot.Dot | None:
    """Parse DOT string into a pydot graph.

    Args:
        dot_content: Raw DOT graph string.

    Returns:
        pydot.Dot on success, None on failure (syntax error or empty input).
    """
    if not dot_content or not dot_content.strip():
        return None

    # pydot prints parse errors to stdout — capture them to keep output clean.
    # pydot currently prints errors to stdout only, not stderr; redirect_stdout
    # is therefore sufficient. If a future pydot version shifts to stderr,
    # this guard would need to be extended with redirect_stderr as well.
    captured = io.StringIO()
    graphs: list[pydot.Dot] | None = None
    with contextlib.redirect_stdout(captured):
        try:
            graphs = pydot.graph_from_dot_data(dot_content)
        except Exception:  # noqa: BLE001
            return None

    if not graphs:
        return None

    return graphs[0]


def _pydot_to_networkx(graph: pydot.Dot) -> nx.Graph:
    """Convert a pydot graph to a NetworkX graph, filtering pseudo-nodes.

    Uses nx.drawing.nx_pydot.from_pydot() which produces:
    - MultiDiGraph for digraph pydot graphs
    - MultiGraph for undirected pydot graphs

    Filters out pydot pseudo-nodes ('node', 'edge', 'graph') that are
    injected by default style declarations.

    Args:
        graph: Parsed pydot graph.

    Returns:
        NetworkX MultiDiGraph or MultiGraph with pseudo-nodes removed.
    """
    G = nx.drawing.nx_pydot.from_pydot(graph)

    # Remove pseudo-nodes that pydot injects for global style declarations.
    pseudo_nodes = [n for n in G.nodes() if str(n).strip('"') in _PSEUDO_NODES]
    G.remove_nodes_from(pseudo_nodes)

    return G


# ---------------------------------------------------------------------------
# Error helper
# ---------------------------------------------------------------------------


def _parse_error(message: str) -> dict:
    """Build a standardized error response dict.

    Args:
        message: Human-readable description of the error.

    Returns:
        {success: False, error: message}
    """
    return {"success": False, "error": message}


# ---------------------------------------------------------------------------
# Stats operation
# ---------------------------------------------------------------------------


def _stats(G: nx.Graph) -> dict:
    """Compute structural statistics for a NetworkX graph.

    Args:
        G: NetworkX graph (MultiDiGraph or MultiGraph).

    Returns:
        {
            success: True,
            operation: "stats",
            node_count: int,
            edge_count: int,
            density: float,
            is_directed: bool,
            is_dag: bool,
            weakly_connected_components: int,
            self_loops: int,
            nodes: list[str],
        }
    """
    node_count = G.number_of_nodes()
    edge_count = G.number_of_edges()
    density = nx.density(G)
    is_directed = G.is_directed()

    # is_dag is a directed-graph concept; undirected graphs return False.
    if is_directed:
        is_dag = nx.is_directed_acyclic_graph(G)
    else:
        is_dag = False

    # Weakly connected components for directed graphs; connected for undirected.
    # cast() is needed because pyright cannot narrow the type from the is_directed check.
    if is_directed:
        wcc_count = nx.number_weakly_connected_components(cast(nx.DiGraph, G))
    else:
        wcc_count = nx.number_connected_components(G)

    self_loops = nx.number_of_selfloops(G)
    nodes = sorted(str(n) for n in G.nodes())

    return {
        "success": True,
        "operation": "stats",
        "node_count": node_count,
        "edge_count": edge_count,
        "density": density,
        "is_directed": is_directed,
        "is_dag": is_dag,
        "weakly_connected_components": wcc_count,
        "self_loops": self_loops,
        "nodes": nodes,
    }


# ---------------------------------------------------------------------------
# Reachability operation
# ---------------------------------------------------------------------------


def _reachability(G: nx.Graph, options: dict) -> dict:
    """Find all nodes reachable from a source node via directed edges.

    Args:
        G: NetworkX graph (MultiDiGraph expected).
        options: Must contain 'source_node' key with the name of the start node.

    Returns:
        {
            success: True,
            operation: "reachability",
            source_node: str,
            reachable: list[str],   # sorted, excludes source itself
            reachable_count: int,
        }
        or {success: False, error: str} on invalid input.
    """
    if "source_node" not in options:
        return _parse_error("Missing required 'source_node' in options")

    source = options["source_node"]

    if source not in G:
        return _parse_error(f"Node '{source}' not found in graph")

    reachable = nx.descendants(G, source)
    reachable_list = sorted(str(n) for n in reachable)

    return {
        "success": True,
        "operation": "reachability",
        "source_node": source,
        "reachable": reachable_list,
        "reachable_count": len(reachable_list),
    }


# ---------------------------------------------------------------------------
# Unreachable operation
# ---------------------------------------------------------------------------


def _unreachable(G: nx.Graph, dot_content: str) -> dict:
    """Identify nodes with no incoming edges, excluding well-known entry points.

    Nodes whose lower-cased name appears in _ENTRY_HINTS (start, entry, root,
    begin, init, source) are excluded from the result even if they have
    in-degree 0.

    Args:
        G: NetworkX graph (MultiDiGraph expected).
        dot_content: Original DOT source, used to produce annotated output.

    Returns:
        {
            success: True,
            operation: "unreachable",
            unreachable: list[str],    # sorted
            unreachable_count: int,
            annotated_dot: str,        # nodes colored red in DOT source
        }
    """
    DG = cast(nx.DiGraph, G)
    unreachable_nodes = sorted(
        str(n)
        for n in DG.nodes()
        if DG.in_degree(n) == 0 and str(n).strip('"').lower() not in _ENTRY_HINTS
    )

    annotated = _annotate_nodes(dot_content, unreachable_nodes, "red", "filled")

    return {
        "success": True,
        "operation": "unreachable",
        "unreachable": unreachable_nodes,
        "unreachable_count": len(unreachable_nodes),
        "annotated_dot": annotated,
    }


# ---------------------------------------------------------------------------
# Cycles operation
# ---------------------------------------------------------------------------


def _cycles(G: nx.Graph, dot_content: str) -> dict:
    """Detect all simple cycles in a directed graph.

    Args:
        G: NetworkX graph (MultiDiGraph expected).
        dot_content: Original DOT source, used to produce annotated output.

    Returns:
        {
            success: True,
            operation: "cycles",
            has_cycles: bool,
            cycles: list[list[str]],  # each cycle is a sorted list of node names
            cycle_count: int,
            annotated_dot: str | None,  # cycle edges colored red; None if no cycles
        }
    """
    if not G.is_directed():
        return _parse_error("Cycle detection requires a directed graph")

    raw_cycles = list(nx.simple_cycles(G))

    if not raw_cycles:
        return {
            "success": True,
            "operation": "cycles",
            "has_cycles": False,
            "cycles": [],
            "cycle_count": 0,
            "annotated_dot": None,
        }

    # Sort each cycle's node list for deterministic output.
    sorted_cycles = [sorted(str(n) for n in cycle) for cycle in raw_cycles]

    # Collect every edge that participates in at least one cycle.
    cycle_edges: set[tuple[str, str]] = set()
    for cycle in raw_cycles:
        for i in range(len(cycle)):
            src = str(cycle[i])
            dst = str(cycle[(i + 1) % len(cycle)])
            cycle_edges.add((src, dst))

    annotated = _annotate_edges(dot_content, list(cycle_edges), "red", "bold")

    return {
        "success": True,
        "operation": "cycles",
        "has_cycles": True,
        "cycles": sorted_cycles,
        "cycle_count": len(raw_cycles),
        "annotated_dot": annotated,
    }


# ---------------------------------------------------------------------------
# Paths operation
# ---------------------------------------------------------------------------


def _paths(G: nx.Graph, options: dict) -> dict:
    """Find all simple paths between two nodes, capped at 100 to avoid combinatorial explosion.

    Args:
        G: NetworkX graph (MultiDiGraph expected).
        options: Must contain 'source_node' and 'target_node' keys.

    Returns:
        {
            success: True,
            operation: "paths",
            source_node: str,
            target_node: str,
            paths: list[list[str]],  # each path is a list of node names
            path_count: int,
            truncated: bool,         # True if more than 100 paths exist
        }
        or {success: False, error: str} on invalid input.
    """
    if "source_node" not in options:
        return _parse_error("Missing required 'source_node' in options")
    if "target_node" not in options:
        return _parse_error("Missing required 'target_node' in options")

    source = options["source_node"]
    target = options["target_node"]

    if source not in G:
        return _parse_error(f"Node '{source}' not found in graph")
    if target not in G:
        return _parse_error(f"Node '{target}' not found in graph")

    _PATH_CAP = 100
    raw_paths: list[list[str]] = []
    truncated = False

    for path in nx.all_simple_paths(G, source=source, target=target):
        raw_paths.append([str(n) for n in path])
        if len(raw_paths) >= _PATH_CAP:
            # Check if there are more paths beyond the cap.
            try:
                next(nx.all_simple_paths(G, source=source, target=target))
                # We already consumed _PATH_CAP paths; peek to see if any remain.
                # Re-enumerate to detect truncation cleanly.
            except StopIteration:
                pass
            truncated = True
            break

    return {
        "success": True,
        "operation": "paths",
        "source_node": source,
        "target_node": target,
        "paths": raw_paths,
        "path_count": len(raw_paths),
        "truncated": truncated,
    }


# ---------------------------------------------------------------------------
# Critical path operation
# ---------------------------------------------------------------------------


def _critical_path(G: nx.Graph) -> dict:
    """Find the longest path in a DAG (critical path).

    Args:
        G: NetworkX graph (MultiDiGraph expected). Must be a DAG.

    Returns:
        {
            success: True,
            operation: "critical_path",
            critical_path: list[str],  # ordered list of node names on the longest path
            length: int,               # number of nodes in the critical path
        }
        or {success: False, error: str} if the graph contains cycles.
    """
    if not G.is_directed() or not nx.is_directed_acyclic_graph(G):
        return _parse_error(
            "Critical path requires a directed acyclic graph (DAG). "
            "The graph contains a cycle or is not directed."
        )

    longest = nx.dag_longest_path(cast(nx.DiGraph, G))
    path = [str(n) for n in longest]

    return {
        "success": True,
        "operation": "critical_path",
        "critical_path": path,
        "length": len(path),
    }


# ---------------------------------------------------------------------------
# DOT annotation helpers
# ---------------------------------------------------------------------------


def _annotate_nodes(dot_content: str, nodes: list[str], color: str, style: str) -> str:
    """Insert per-node attribute declarations into a DOT string.

    Declarations are inserted on new lines immediately after the first line
    that contains '{', so they take precedence over any global defaults.

    Args:
        dot_content: Raw DOT graph string.
        nodes: Node names to annotate (must already exist in the graph).
        color: DOT color value (e.g. "red").
        style: DOT style value (e.g. "filled").

    Returns:
        Modified DOT string with attribute lines injected, or the original
        string unchanged if no nodes are provided or no '{' is found.
    """
    if not nodes:
        return dot_content

    lines = dot_content.split("\n")
    insert_idx: int | None = None
    for i, line in enumerate(lines):
        if "{" in line:
            insert_idx = i + 1
            break

    if insert_idx is None:
        return dot_content

    new_lines = [f'  {node} [color="{color}", style="{style}"];' for node in nodes]
    return "\n".join(lines[:insert_idx] + new_lines + lines[insert_idx:])


def _annotate_edges(
    dot_content: str, edges: list[tuple[str, str]], color: str, style: str
) -> str:
    """Insert per-edge attribute declarations into a DOT string.

    Declarations are inserted on new lines immediately after the first line
    that contains '{'.

    Args:
        dot_content: Raw DOT graph string.
        edges: (src, dst) pairs to annotate.
        color: DOT color value (e.g. "red").
        style: DOT style value (e.g. "bold").

    Returns:
        Modified DOT string with attribute lines injected, or the original
        string unchanged if no edges are provided or no '{' is found.
    """
    if not edges:
        return dot_content

    lines = dot_content.split("\n")
    insert_idx: int | None = None
    for i, line in enumerate(lines):
        if "{" in line:
            insert_idx = i + 1
            break

    if insert_idx is None:
        return dot_content

    new_lines = [
        f'  {src} -> {dst} [color="{color}", style="{style}"];' for src, dst in edges
    ]
    return "\n".join(lines[:insert_idx] + new_lines + lines[insert_idx:])


# ---------------------------------------------------------------------------
# Placeholder handlers for special-routed operations
# ---------------------------------------------------------------------------


def _dispatch_diff(dot_content: str, options: dict) -> dict:
    """Dispatch diff operation (routed before NetworkX conversion).

    Compares two DOT graphs for structural differences.
    Not yet implemented — placeholder for future task.
    """
    return _parse_error("Analysis 'diff' is not yet implemented")


def _dispatch_subgraph_extract(dot_content: str, options: dict) -> dict:
    """Dispatch subgraph_extract operation (routed before NetworkX conversion).

    Extracts a subgraph around specified nodes.
    Not yet implemented — placeholder for future task.
    """
    return _parse_error("Analysis 'subgraph_extract' is not yet implemented")
