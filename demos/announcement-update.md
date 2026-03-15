# amplifier-bundle-dot-graph is Complete: All Three Tiers Shipped

**TL;DR:** The DOT/Graphviz bundle for Amplifier now ships validation, rendering, and graph intelligence on top of the original knowledge layer. Any bundle gets DOT authoring, quality review, rendering to SVG/PNG/PDF, *and* algorithmic graph analysis (reachability, cycles, critical paths, diffs) with one include line. The graph intelligence layer is the key differentiator: parse DOT into graph objects and run algorithms at code speed, zero LLM tokens.

**Repo:** [microsoft/amplifier-bundle-dot-graph](https://github.com/microsoft/amplifier-bundle-dot-graph)

---

## What shipped since Phase 1

Phase 1 delivered the knowledge layer — skills, docs, agents, and context that made any Amplifier session DOT-literate. Phases 2 and 3 add the tool layers that turn DOT from a documentation format into a programmable analysis substrate.

### Phase 2 — Validation & Rendering Tools

Three new Python modules, all with graceful degradation when system dependencies are absent:

**`dot_validate` — Three-layer DOT validation**

Validation happens in three independent passes:

| Layer | Engine | Checks | Requires |
|-------|--------|--------|----------|
| Syntax | pydot (pure Python) | Parse errors, malformed attributes, encoding issues | Nothing extra |
| Structural | Custom analysis | Unreachable nodes, orphan clusters, missing legends, hub concentration | Nothing extra |
| Render quality | Graphviz CLI | Layout warnings, overlaps, engine compatibility | `graphviz` installed |

Returns structured JSON: every issue has a severity, location, message, and suggested fix. Graph stats (node count, edge count, cluster count, density) are always included. The syntax layer works everywhere — no graphviz install needed for basic validation.

**`dot_render` — Graphviz CLI wrapper**

Renders DOT to SVG, PNG, PDF, or JSON with any layout engine (`dot`, `neato`, `fdp`, `circo`, `twopi`, `sfdp`). Returns the rendered bytes or saves to a file path. When graphviz isn't installed, returns a structured error with platform-specific install instructions instead of a cryptic traceback.

**`dot_setup` — Environment detection**

Probes the environment for graphviz, pydot, and networkx availability. Reports versions, paths, and capabilities. When something is missing, provides platform-specific install guidance (apt, brew, pip, conda). Designed for the "first 5 minutes" experience — an agent can call `dot_setup` to understand what's available before attempting operations that need external tools.

### Phase 3 — NetworkX-backed Graph Intelligence

This is the differentiating layer. Eight analysis operations, all pure Python, zero LLM cost, millisecond execution:

| Operation | What it does | Use case |
|-----------|-------------|----------|
| `stats` | Node/edge count, density, connected components, diameter | Quick structural overview |
| `reachability` | BFS from a source node — what can be reached | Impact analysis: "if this breaks, what's affected?" |
| `unreachable` | Nodes with no incoming edges | Dead code detection, orphan identification |
| `cycles` | Detect and list all cycles | Circular dependency detection |
| `paths` | All simple paths between two nodes | Dependency chain analysis |
| `critical_path` | Longest path through a DAG | Bottleneck identification in pipelines |
| `subgraph_extract` | Pull a cluster out as standalone DOT | Focus analysis, documentation extraction |
| `diff` | Structural diff between two DOT graphs | What changed? Added/removed nodes and edges |

Every operation produces `annotated_dot` output — the original DOT source with findings highlighted through colors, styles, and labels. An agent can show the annotated graph to a user without any additional formatting work.

**Why this matters:** Before Phase 3, answering "what nodes can reach X?" required an LLM to mentally trace edges through a DOT file — slow, expensive, error-prone. Now it's a function call that returns in milliseconds with a highlighted graph.

### Systemic Bug Fix — Module mount() Protocol

During development, we discovered that agents consistently produce broken `mount()` stubs when creating new Amplifier modules. The root cause was a 5-link failure chain:

1. The `mount()` → `coordinator.mount()` contract exists in amplifier-core
2. But amplifier-foundation's context had zero mention of it
3. So agents generating modules had no knowledge of the protocol
4. They produced syntactically valid but semantically empty `mount()` functions
5. These passed linting but failed at runtime — silent breakage

**Fix:** Created a `creating-amplifier-modules` skill in amplifier-foundation with:
- The Iron Law: "Every module must register at least one capability in mount()"
- A placeholder pattern for modules that aren't ready yet
- An anti-rationalization table (common agent excuses mapped to correct behavior)

Updated `BUNDLE_GUIDE.md` with a 122-line "Creating Tool Modules" section. Wired skill discovery in both foundation and dot-graph behavior YAMLs. Sessions now see 24 skills (up from 18).

### Skill Discovery Fix

Both amplifier-foundation's and amplifier-bundle-dot-graph's `skills/` directories were committed but unreachable — the behavior YAML files didn't register them with `tool-skills`. Added `config.skills` entries to both behavior YAMLs. Six previously invisible skills are now discoverable:

- `creating-amplifier-modules` (foundation)
- `dot-syntax`, `dot-patterns`, `dot-as-analysis`, `dot-quality`, `dot-graph-intelligence` (dot-graph)

### Demo Artifacts

Eight demo diagrams with DOT source + PNG + SVG renders:

| Demo | Demonstrates |
|------|-------------|
| Bundle Architecture | Self-documenting the bundle's own three-tier structure |
| 7 Use Cases | Hub-and-spoke taxonomy of DOT in Amplifier |
| Reconciliation Before/After | The killer demo — drawing reveals 7 bugs in a belief vs. reality comparison |
| Multi-Scale Navigation | Same system at overview and detail zoom levels |
| Recipe Visualization | Multi-step agent workflows as graphs |
| Ecosystem Composition | How the bundle propagates capabilities across consuming bundles |

The reconciliation before/after demo is the best showcase: it visually demonstrates how the act of constructing a graph forces you to confront gaps between what you believe exists and what actually exists. The "before" diagram shows a developer's mental model of a cloud service; the "after" diagram highlights 7 findings (missing retry logic, synchronous queues masquerading as async, write-only caches, dead code) using color-coded annotations.

A self-contained HTML announcement deck with embedded images is included for easy Teams/browser sharing.

### Ecosystem Integration

The bundle is now listed in `MODULES.md` in the main [amplifier](https://github.com/microsoft/amplifier) repo, making it discoverable alongside all other official bundles.

---

## By the numbers

| Metric | Value |
|--------|-------|
| Test count | 620 (502 Phase 1 + 66 Phase 2 + 52 Phase 3) |
| All passing | Yes |
| Commits since Phase 1 | 15 |
| Files changed | 55 |
| Lines added | ~14,900 |
| Skills now discoverable | 6 (from 0) |
| Analysis operations | 8 |
| Demo diagrams | 8 (with DOT + PNG + SVG) |
| External dependencies added | 0 required (pydot, networkx are optional) |

---

## How to use it

### Add to your bundle

```yaml
# In your bundle's behavior YAML
includes:
  - bundle: dot-graph:behaviors/dot-graph
```

That's it. Your sessions now have access to:
- `dot-author` agent for graph creation and editing
- `diagram-reviewer` agent for quality review with PASS/WARN/FAIL verdicts
- `dot_validate` tool for three-layer validation
- `dot_render` tool for SVG/PNG/PDF output
- `dot_analyze` tool for graph intelligence operations
- 5 skills covering syntax, patterns, analysis methodology, quality standards, and graph intelligence
- Full DOT language reference and pattern catalog in context

### Run analysis on any DOT graph

```
# In an Amplifier session with the bundle included:

"Analyze this graph for cycles"
→ dot_analyze(operation="cycles", dot_content="digraph { a -> b -> c -> a }")

"What can node X reach?"
→ dot_analyze(operation="reachability", dot_content="...", source="X")

"Diff these two versions"
→ dot_analyze(operation="diff", dot_content="...", dot_content_b="...")
```

### Validate before committing

```
"Validate my diagram"
→ dot_validate(dot_content="digraph { ... }")
# Returns structured JSON with syntax, structural, and render quality findings
```

---

## Architecture

```
amplifier-bundle-dot-graph/
├── bundle.md                          # Manifest
├── behaviors/dot-graph.yaml           # Wiring unit (one include = everything)
│
├── Tier 1 — Knowledge Layer
│   ├── agents/                        # dot-author, diagram-reviewer
│   ├── skills/                        # 5 skills (syntax, patterns, analysis, quality, intelligence)
│   ├── docs/                          # DOT reference, patterns catalog, quality gates
│   └── context/                       # Awareness + instructions for agents
│
├── Tier 2 — Validation & Rendering
│   └── modules/tool-dot-graph/
│       ├── dot_validate()             # Three-layer validation (pydot → structural → graphviz)
│       ├── dot_render()               # SVG/PNG/PDF/JSON output
│       └── dot_setup()                # Environment detection + install guidance
│
└── Tier 3 — Graph Intelligence
    └── modules/tool-dot-graph/
        └── dot_analyze()              # 8 NetworkX-backed operations
            ├── stats                  # Graph metrics
            ├── reachability           # BFS from source
            ├── unreachable            # No-incoming-edge nodes
            ├── cycles                 # Cycle detection
            ├── paths                  # All simple paths
            ├── critical_path          # Longest DAG path
            ├── subgraph_extract       # Cluster extraction
            └── diff                   # Structural comparison
```

---

## What's next

The bundle is feature-complete for its original scope. Potential future work:

- **More analysis operations** — centrality metrics, community detection, topological sort
- **Interactive exploration** — step-through graph traversal in agent sessions
- **Graph-to-DOT generation** — produce DOT from dependency manifests, API schemas, or code analysis
- **Cross-bundle analysis** — analyze the Amplifier bundle dependency graph itself using these tools

---

*Built with [Amplifier](https://github.com/microsoft/amplifier). 620 tests. Zero required external dependencies. One include line.*
