"""
Tests for behaviors/dot-graph.yaml existence and required content.
TDD: This test is written BEFORE the behaviors/dot-graph.yaml file is created.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
BEHAVIOR_PATH = REPO_ROOT / "behaviors" / "dot-graph.yaml"


def _load_yaml(path: Path) -> dict:
    """Load and parse a YAML file. Returns the parsed dict."""
    return yaml.safe_load(path.read_text())


# --- File existence ---


def test_behavior_file_exists():
    """behaviors/dot-graph.yaml must exist."""
    assert BEHAVIOR_PATH.exists(), (
        f"behaviors/dot-graph.yaml not found at {BEHAVIOR_PATH}"
    )


def test_behavior_file_is_valid_yaml():
    """behaviors/dot-graph.yaml must be valid YAML."""
    content = BEHAVIOR_PATH.read_text()
    parsed = yaml.safe_load(content)
    assert isinstance(parsed, dict), "behaviors/dot-graph.yaml must parse to a dict"


# --- Top-level keys ---


def test_behavior_has_bundle_key():
    """behaviors/dot-graph.yaml must have a top-level 'bundle' key."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert "bundle" in data, "behaviors/dot-graph.yaml must have 'bundle' key"


def test_behavior_has_tools_key():
    """behaviors/dot-graph.yaml must have a top-level 'tools' key."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert "tools" in data, "behaviors/dot-graph.yaml must have 'tools' key"


def test_behavior_has_agents_key():
    """behaviors/dot-graph.yaml must have a top-level 'agents' key."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert "agents" in data, "behaviors/dot-graph.yaml must have 'agents' key"


def test_behavior_has_context_key():
    """behaviors/dot-graph.yaml must have a top-level 'context' key."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert "context" in data, "behaviors/dot-graph.yaml must have 'context' key"


# --- bundle section ---


def test_behavior_bundle_name():
    """bundle.name must be 'dot-graph-behavior'."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert data["bundle"]["name"] == "dot-graph-behavior", (
        f"bundle.name must be 'dot-graph-behavior', got: {data['bundle'].get('name')}"
    )


def test_behavior_bundle_version():
    """bundle.version must be '0.1.0'."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert data["bundle"]["version"] == "0.1.0", (
        f"bundle.version must be '0.1.0', got: {data['bundle'].get('version')}"
    )


def test_behavior_bundle_description():
    """bundle.description must be present and non-empty."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert "description" in data["bundle"], "bundle must have 'description' key"
    assert data["bundle"]["description"], "bundle.description must not be empty"


# --- tools section ---


def test_behavior_tools_is_list():
    """tools must be a list."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert isinstance(data["tools"], list), "tools must be a list"


def test_behavior_tools_has_tool_dot_graph():
    """tools must contain a module entry with module 'tool-dot-graph'."""
    data = _load_yaml(BEHAVIOR_PATH)
    module_names = [t.get("module") for t in data["tools"] if isinstance(t, dict)]
    assert "tool-dot-graph" in module_names, (
        f"tools must contain module 'tool-dot-graph', found: {module_names}"
    )


def test_behavior_tools_dot_graph_has_source():
    """tool-dot-graph entry must have a source field."""
    data = _load_yaml(BEHAVIOR_PATH)
    tool = next(
        (
            t
            for t in data["tools"]
            if isinstance(t, dict) and t.get("module") == "tool-dot-graph"
        ),
        None,
    )
    assert tool is not None, "Must have tool-dot-graph entry"
    assert "source" in tool, "tool-dot-graph must have a 'source' field"


def test_behavior_tools_dot_graph_source_value():
    """tool-dot-graph source must point to the correct git URL with subdirectory."""
    data = _load_yaml(BEHAVIOR_PATH)
    tool = next(
        (
            t
            for t in data["tools"]
            if isinstance(t, dict) and t.get("module") == "tool-dot-graph"
        ),
        None,
    )
    assert tool is not None, "Must have tool-dot-graph entry"
    expected_source = "git+https://github.com/microsoft/amplifier-bundle-dot-graph@main#subdirectory=modules/tool-dot-graph"
    assert tool["source"] == expected_source, (
        f"tool-dot-graph source must be '{expected_source}', got: {tool.get('source')}"
    )


# --- agents section ---


def test_behavior_agents_has_include():
    """agents must have an 'include' key."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert "include" in data["agents"], "agents must have an 'include' key"


def test_behavior_agents_include_is_list():
    """agents.include must be a list."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert isinstance(data["agents"]["include"], list), "agents.include must be a list"


def test_behavior_agents_includes_dot_author():
    """agents.include must contain 'dot-graph:dot-author'."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert "dot-graph:dot-author" in data["agents"]["include"], (
        f"agents.include must contain 'dot-graph:dot-author', got: {data['agents']['include']}"
    )


def test_behavior_agents_includes_diagram_reviewer():
    """agents.include must contain 'dot-graph:diagram-reviewer'."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert "dot-graph:diagram-reviewer" in data["agents"]["include"], (
        f"agents.include must contain 'dot-graph:diagram-reviewer', got: {data['agents']['include']}"
    )


# --- context section ---


def test_behavior_context_has_include():
    """context must have an 'include' key."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert "include" in data["context"], "context must have an 'include' key"


def test_behavior_context_include_is_list():
    """context.include must be a list."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert isinstance(data["context"]["include"], list), (
        "context.include must be a list"
    )


def test_behavior_context_includes_dot_awareness():
    """context.include must contain 'dot-graph:context/dot-awareness.md'."""
    data = _load_yaml(BEHAVIOR_PATH)
    assert "dot-graph:context/dot-awareness.md" in data["context"]["include"], (
        f"context.include must contain 'dot-graph:context/dot-awareness.md', "
        f"got: {data['context']['include']}"
    )
