# Bootstrap Synthesis: amplifier-bundle-dot-graph

> **Synthesized:** 2026-03-13
> **Sources:** 6 research documents from multi-agent discovery effort
> **Scope:** Complete blueprint for a DOT/Graphviz capability bundle for the Amplifier ecosystem

---

## Table of Contents

1. [Use-Case Taxonomy](#1-use-case-taxonomy)
2. [Capability Map](#2-capability-map)
3. [Architecture Recommendation](#3-architecture-recommendation)
4. [Implementation Phases](#4-implementation-phases)
5. [Open Questions & Design Decisions](#5-open-questions--design-decisions)
6. [Existing Asset Inventory](#6-existing-asset-inventory)

---

## 1. Use-Case Taxonomy

Nine distinct ways DOT is used or could be used in the Amplifier ecosystem, grouped by maturity.

### UC-1: Pipeline Definition Language (Attractor DSL)

**Maturity:** Production — 54 DOT pipeline files, active daily use
**Sessions:** `4e7e1d72`, `b174ff67`, `588e215d`, `b6381c4b`, `2d7eecf6`, 8 resolve-stabilize sessions
**Dialect:** Attractor shape-based (primary) + node_type attribute-based (secondary)

DOT is the **native runtime format** for the Attractor pipeline engine. Each `.dot` file defines a complete AI workflow as a directed graph. Nodes map to LLM agent tasks via a shape-to-handler vocabulary (10 shapes). Edges define flow control: sequential, conditional, looping, fan-out/fan-in. The `model_stylesheet` enables CSS-like multi-provider routing.

**Key artifacts:** Tutorial ladder (`01-simple-linear.dot` → `10-full-attractor.dot`), practical templates (`pr-review.dot`, `feature-build.dot`, `bug-fix.dot`), reusable patterns (`conversational-gate.dot`, `convergence-factory.dot`), real-world pipelines (`consensus_task.dot`, `semport.dot`, `resolve_quick.dot`, `resolve_consensus.dot`).

**Bundle relevance:** The bundle must understand and support this dialect — it's the highest-volume DOT use case. Validation, authoring guidance, and pattern libraries should prioritize pipeline DOT.

### UC-2: Architecture Documentation (Parallax Discovery Output)

**Maturity:** Validated — 4 production architecture DOT files, working tooling with 247 tests
**Sessions:** `9ed2c49f`, `71295782`, `4e7e1d72`
**Dialect:** Architecture documentation DOT (shape = component type, not handler)

Every Parallax Discovery investigation produces `diagram.dot` files as standard output. These are architecture/integration/state-machine diagrams showing module boundaries, data flows, and confirmed bugs. The dot-docs workspace has a working discovery pipeline that generates, synthesizes, and validates these artifacts.

**Key artifacts:** `amplifier-bundle-modes/overview.dot` (173 lines), `amplifier-resolve/overview.dot` (236 lines), plus `architecture.dot` detail files for each.

**Bundle relevance:** The bundle's authoring agent and quality standards must support this dialect alongside pipeline DOT. The two dialects have **different shape vocabularies** — this is a critical awareness point.

### UC-3: Event System Specification

**Maturity:** Proven — 13+ DOT specification files created in one session
**Sessions:** `c95ce204`, `8ca877b9`
**Dialect:** Architecture documentation DOT (state machines + flow diagrams)

DOT files created as formal specifications for the Amplifier event system: session state machines, event flows, orchestrator variants, delegation trees, navigation models. A key finding: DOT diagrams revealed a cancellation gap (G2) that was "invisible because no diagram showed all exit paths."

**Proposed convention:** Every module ships an `events.dot` — rejected for hand-maintenance ("hand-maintained DOT files won't be maintained"), but the generated-from-source variant remains viable.

**Bundle relevance:** The bundle should support state-machine and event-flow DOT patterns. A potential future tool: generate `events.dot` from source code introspection (a working prototype exists in `generate_event_dot.py`).

### UC-4: Progressive Disclosure Architecture (Dotfiles Vision)

**Maturity:** Designed — directory structure defined, quality standards written, pipeline prototyped
**Sessions:** `71295782`, `1fe54592`
**Dialect:** Architecture documentation DOT

The emerging vision: per-person, per-repo DOT architecture files in a team knowledge base (`/dotfiles/<handle>/<repo>/`), designed for progressive LLM consumption:

- **Layer 0:** `overview.dot` (~200 lines) — agent reads ONE file, knows the system shape
- **Layer 1:** `architecture.dot`, `sequence.dot`, `state-machines.dot`, `integration.dot` — load by topic
- **Layer 2:** `.investigation/` raw agent outputs — deep forensics only

The dual-purpose format thesis: DOT simultaneously renderable for humans AND parseable for LLMs. Optimized for both audiences without compromise.

**Bundle relevance:** Quality standards for `overview.dot` (150–250 lines, rendered legend, cluster subgraphs) should be encoded in the bundle's review agent and validation tool.

### UC-5: Recipe Visualization

**Maturity:** Proven — working example, user requested as standard capability
**Sessions:** `bc1547a8`
**Dialect:** Architecture documentation DOT (visual encoding of recipe structure)

DOT used to visualize YAML recipe structures: blue boxes for bash steps, green for agent steps, purple hexagons for foreach loops, yellow diamonds for condition gates, dashed orange edges for sub-recipe invocations. User reaction: *"this is REALLY helpful"* — immediately proposed it as a standard recipe-author capability.

**Bundle relevance:** A recipe-to-DOT generation capability (either as a tool or as agent knowledge) is a high-value use case. The visual encoding conventions should be documented in the bundle's pattern library.

### UC-6: Process Flow Visualization (Skills)

**Maturity:** Production — embedded in 14+ sessions via brainstormer/superpowers skills
**Sessions:** 14+ sessions loading brainstormer and superpowers skills
**Dialect:** Simple documentation DOT

DOT syntax embedded directly in Amplifier skill markdown files to define agent workflow processes: `digraph brainstorming`, `digraph when_to_use`, `digraph process`. These appear in every session that loads the brainstormer or superpowers skills.

**Bundle relevance:** Demonstrates DOT is already a natural documentation format within the skill ecosystem. The bundle's authoring agent should know this pattern for embedding DOT in skill definitions.

### UC-7: Knowledge Graphs

**Maturity:** Emerging — referenced in ecosystem research, used in RAG pipelines externally
**Sessions:** Ecosystem research
**Dialect:** Standard DOT (undirected or directed)

Multiple external projects use DOT/Graphviz for visualizing LLM-generated knowledge graphs, ontologies, and concept maps. NetworkX integration makes DOT a natural format for knowledge representation and analysis.

**Bundle relevance:** The bundle's DOT patterns library should include knowledge graph templates. The analysis tool (cycle detection, path analysis) directly supports this use case.

### UC-8: Dependency Visualization

**Maturity:** Implicit — present in architecture DOT files, not formalized as distinct use case
**Sessions:** `71295782` (architecture DOT files show module dependencies)
**Dialect:** Architecture documentation DOT

DOT diagrams showing import relationships, package dependencies, and module boundaries. Currently embedded within broader architecture diagrams rather than generated as standalone dependency graphs.

**Bundle relevance:** A potential future tool: generate dependency DOT from `pyproject.toml`, `Cargo.toml`, `package.json`, or import analysis. The `generate_event_dot.py` script demonstrates the source-introspection pattern.

### UC-9: State Machine Representation

**Maturity:** Validated — multiple state-machine DOTs created, identified as "the gem"
**Sessions:** `71295782` (158-line state machine was the optimal-size discovery), `c95ce204` (session state machine DOT)
**Dialect:** Architecture documentation DOT (`circle` = start state, `doublecircle` = terminal state)

State machine diagrams for session lifecycles, brief status transitions, and component state management. The 158-line state-machine diagram from Parallax Discovery was identified as the optimal artifact: compact, renderable, and agent-scannable.

**Bundle relevance:** State machine is a first-class DOT pattern. The bundle's pattern library should include state-machine templates with the `circle`/`doublecircle` convention.

### Use-Case Summary Matrix

| UC | Name | Maturity | Dialect | Volume | Bundle Priority |
|----|------|----------|---------|--------|-----------------|
| 1 | Pipeline Definition (Attractor) | Production | Attractor shape | 54+ files | **Critical** |
| 2 | Architecture Documentation | Validated | Architecture doc | 4+ files | **High** |
| 3 | Event System Specification | Proven | Architecture doc | 13+ files | Medium |
| 4 | Progressive Disclosure (Dotfiles) | Designed | Architecture doc | Planned | Medium |
| 5 | Recipe Visualization | Proven | Architecture doc | Ad hoc | Medium |
| 6 | Skill Process Flows | Production | Simple doc | Embedded | Low |
| 7 | Knowledge Graphs | Emerging | Standard DOT | External | Low |
| 8 | Dependency Visualization | Implicit | Architecture doc | Embedded | Low |
| 9 | State Machine Representation | Validated | Architecture doc | Embedded | Medium |

---

## 2. Capability Map

What the bundle should provide, mapped to use cases served.

### 2.1 DOT Authoring Assistance (Agent: `dot-author`)

**Type:** Agent (context sink)
**Use cases served:** UC-1 through UC-9 (all)

An expert agent for creating, debugging, and optimizing DOT graph definitions. Carries heavy documentation (DOT syntax reference, patterns, best practices) that loads only when the agent is spawned.

**Must know:**
- Both DOT dialects (Attractor pipeline + architecture documentation) and when to use each
- Shape-to-handler mapping for pipeline DOT
- Shape-to-type mapping for architecture DOT
- Layout engine selection (`dot` for hierarchies, `neato` for networks, `circo` for cycles, etc.)
- Anti-patterns (>80 nodes, `splines=ortho` with high node counts, multi-line inline labels)
- Progressive disclosure conventions (`overview.dot` at 150–250 lines)
- Model stylesheet syntax (CSS-like selectors)
- The "dual-purpose format" principle (human-renderable + agent-scannable)

**Capability gaps filled:** Currently, agents creating DOT across the ecosystem have no shared knowledge base. Each session reinvents conventions. This agent centralizes DOT expertise.

### 2.2 DOT Validation (Tool: `dot_validate`)

**Type:** Tool (Python module)
**Use cases served:** UC-1 (pipeline validation), UC-2/UC-4 (architecture quality), UC-3 (specification completeness)

Three-tier validation:

| Tier | Check | Method | Use Cases |
|------|-------|--------|-----------|
| **Syntax** | Valid DOT grammar | `dot -Tcanon` or `pydot.graph_from_dot_data()` | All |
| **Structure** | DAG check, connectivity, reachability, isolated nodes | `networkx` graph algorithms | UC-1 (pipelines), UC-3 (specs) |
| **Semantic** | Domain-specific rules per dialect | Custom validation logic | UC-1 (start/exit nodes, shape vocabulary), UC-2/UC-4 (line count, legend, cluster naming) |

**Pipeline-specific validation (Attractor dialect):**
- Exactly one `Mdiamond` (start) and at least one `Msquare` (exit) node
- All nodes reachable from start; exit reachable from all non-dead-end nodes
- Valid shape names from the 10-shape vocabulary
- `goal_gate=true` nodes have `retry_target`
- Conditional edges have valid `condition` syntax
- No fan-in without corresponding fan-out

**Architecture-specific validation:**
- `overview.dot` is 150–250 lines, under 15KB
- Rendered legend is a `subgraph cluster_legend` with real nodes (not comment-only)
- All cluster subgraphs use `cluster_` prefix
- Node IDs follow `snake_case` with cluster prefix
- `dot -Tsvg` renders without errors and produces non-zero bounding box

**Existing implementation to adapt:** `dot-docs/dot-docs/tools/dotfiles_discovery/dot_validation.py` (216 lines) — already implements syntax validation, line count check, and SVG render quality check.

### 2.3 DOT Rendering (Tool: `dot_render`)

**Type:** Tool (Python module)
**Use cases served:** All visual use cases (UC-2, UC-4, UC-5, UC-6, UC-9)

Render DOT source to visual formats:

| Format | Flag | Best For |
|--------|------|----------|
| SVG | `-Tsvg` | Web embedding, interactive viewing, primary output |
| PNG | `-Tpng` | Simple embedding in docs/chat |
| PDF | `-Tpdf` | Print-quality output |
| JSON | `-Tjson` | Machine processing, round-tripping |
| Canon DOT | `-Tcanon` | Normalized DOT source with layout info |

**Implementation:** Thin wrapper around Graphviz CLI (`dot`, `neato`, `fdp`, etc.) with engine auto-selection based on graph type. Could also leverage the `graphviz` Python package for programmatic generation.

**Key insight from research:** SVG is the recommended primary format — scalable, interactive (supports tooltips and hyperlinks), and web-friendly.

### 2.4 DOT Quality Review (Agent: `diagram-reviewer`)

**Type:** Agent (context sink)
**Use cases served:** UC-2 (architecture review), UC-4 (dotfiles quality), UC-1 (pipeline review)

A specialist review agent that evaluates existing DOT files against quality standards:

1. Syntax validity
2. Structural clarity (subgraphs/clusters used appropriately)
3. Visual readability (will the rendered output be legible?)
4. Layout engine choice (right engine for graph type)
5. Attribute hygiene (correct, consistent usage)
6. Convention compliance (shape vocabulary, edge semantics, color conventions)
7. Size constraints (overview.dot within 150–250 lines)

**Output contract:** Verdict (PASS / NEEDS WORK / FAIL), numbered issues with severity, corrected DOT if issues found.

### 2.5 DOT-to-Analysis Conversion (Tool: `dot_analyze`)

**Type:** Tool (Python module, Phase 3)
**Use cases served:** UC-1 (pipeline validation), UC-7 (knowledge graphs), UC-8 (dependency analysis)

Graph analysis algorithms via NetworkX integration:

| Analysis | NetworkX Function | Use Case |
|----------|------------------|----------|
| Cycle detection | `nx.simple_cycles(G)` | Pipeline validation, dependency analysis |
| DAG verification | `nx.is_directed_acyclic_graph(G)` | Pipeline validation |
| Topological sort | `nx.topological_sort(G)` | Execution ordering |
| Path analysis | `nx.has_path(G, source, target)` | Reachability checking |
| Connected components | `nx.weakly_connected_components(G)` | Finding disconnected subgraphs |
| Isolated nodes | `nx.isolates(G)` | Dead node detection |
| Node degree analysis | `G.in_degree()`, `G.out_degree()` | Entry/exit point detection |

**Python library stack:** `pydot` for parsing DOT → `networkx` for analysis → structured results.

### 2.6 DOT Templates & Patterns (Context/Skills)

**Type:** Context files (docs/) + Skills
**Use cases served:** All

**Pattern library (`docs/DOT_PATTERNS.md`):**

| Pattern | Category | Source |
|---------|----------|--------|
| Linear pipeline | Pipeline | `01-simple-linear.dot` |
| Conditional routing | Pipeline | `03-conditional-routing.dot` |
| Parallel fan-out/fan-in | Pipeline | `05-parallel-fan-out.dot` |
| Conversational gate | Pipeline | `patterns/conversational-gate.dot` |
| Convergence factory | Pipeline | `patterns/convergence-factory.dot` |
| Model stylesheet | Pipeline | `06-model-stylesheet.dot` |
| Architecture overview | Documentation | `amplifier-bundle-modes/overview.dot` |
| State machine | Documentation | `02-session-state-machine.dot` |
| Event flow | Documentation | `03-single-turn-event-flow.dot` |
| Recipe visualization | Visualization | `bc1547a8` session patterns |
| Knowledge graph | General | Standard template |

**Skills (`skills/dot-graph-syntax/`, `skills/dot-graph-patterns/`):**
- Quick-reference syntax lookup (attribute names, engine selection, common mistakes)
- Copy-paste pattern templates for common graph types
- Anti-pattern catalog with fixes

### 2.7 DOT Convention Enforcement (Context)

**Type:** Context files
**Use cases served:** UC-1 (pipeline conventions), UC-2/UC-4 (architecture conventions)

**Two convention sets (reflecting the two dialects):**

| Convention | Pipeline DOT | Architecture DOT |
|------------|-------------|-----------------|
| **Shape vocabulary** | 10 shapes → handlers | 12+ shapes → component types |
| **Edge semantics** | `condition`, `weight`, `loop_restart` | `solid`/`dashed`/`dotted`/`bold` styles |
| **Color conventions** | Minimal (shapes are semantic) | Red=bug, orange=suspected, green=healthy |
| **Size constraints** | Prefer <10 nodes per pipeline | overview.dot: 150–250 lines |
| **Naming** | Descriptive node IDs | `snake_case` with cluster prefix |
| **Legend** | Not applicable | Required rendered `subgraph cluster_legend` |

### Capability Summary Matrix

| Capability | Type | Phase | Use Cases | Priority |
|-----------|------|-------|-----------|----------|
| DOT Authoring (dot-author) | Agent | 1 | All | **Critical** |
| DOT Review (diagram-reviewer) | Agent | 1 | UC-1,2,4 | **High** |
| Convention Context | Context | 1 | All | **Critical** |
| Pattern Library | Docs | 1 | All | **High** |
| Syntax Quick Reference | Skill | 1 | All | **High** |
| DOT Validation | Tool | 2 | UC-1,2,3,4 | **High** |
| DOT Rendering | Tool | 3 | UC-2,4,5,9 | Medium |
| DOT Analysis | Tool | 3 | UC-1,7,8 | Medium |
| Source-to-DOT Generation | Tool | 4 | UC-3,8 | Low |

---

## 3. Architecture Recommendation

### 3.1 Bundle Structure

Following the thin bundle pattern from BUNDLE-GUIDANCE.md, with the `amplifier-bundle-recipes` exemplar as the canonical reference:

```
amplifier-bundle-dot-graph/
├── bundle.md                              # Thin root (~15 lines YAML)
├── behaviors/
│   └── dot-graph.yaml                     # Reusable behavior (agents + context)
├── agents/
│   ├── dot-author.md                      # DOT authoring expert (context sink)
│   └── diagram-reviewer.md                # DOT quality reviewer (context sink)
├── context/
│   ├── dot-graph-awareness.md             # Thin pointer for root sessions (~30 lines)
│   └── dot-graph-instructions.md          # Consolidated instructions (~50 lines)
├── docs/
│   ├── DOT_SYNTAX_REFERENCE.md            # Complete DOT language reference
│   ├── DOT_PATTERNS.md                    # Common patterns with templates
│   ├── DOT_BEST_PRACTICES.md             # Layout tips, anti-patterns, conventions
│   ├── PIPELINE_DOT_GUIDE.md             # Attractor pipeline dialect guide
│   └── ARCHITECTURE_DOT_GUIDE.md         # Architecture documentation dialect guide
├── skills/                                # Complementary quick-reference skills
│   ├── dot-graph-syntax/
│   │   └── SKILL.md
│   └── dot-graph-patterns/
│       └── SKILL.md
├── modules/                               # Tool modules (Phase 2+)
│   └── tool-dot-graph/
│       ├── pyproject.toml
│       └── tool_dot_graph/
│           ├── __init__.py
│           ├── tool.py                    # Tool entry point with mount()
│           ├── validate.py                # Validation logic
│           ├── render.py                  # Rendering wrapper
│           └── analyze.py                 # Graph analysis (Phase 3)
├── README.md
├── LICENSE
└── SECURITY.md
```

### 3.2 Bundle Configuration

**`bundle.md`** — Thin root, ~15 lines YAML:

```yaml
bundle:
  name: dot-graph
  version: 1.0.0
  description: DOT/Graphviz diagram capabilities for creating, validating, rendering, and reasoning about graphs

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: dot-graph:behaviors/dot-graph
```

Body references `@dot-graph:context/dot-graph-instructions.md` and `@foundation:context/shared/common-system-base.md`.

**`behaviors/dot-graph.yaml`** — The reusable value:

```yaml
bundle:
  name: dot-graph-behavior
  version: 1.0.0
  description: DOT/Graphviz diagram capabilities with authoring and review agents

agents:
  include:
    - dot-graph:dot-author
    - dot-graph:diagram-reviewer

context:
  include:
    - dot-graph:context/dot-graph-awareness.md    # THIN pointer only
```

No `tools:` section until Phase 2. Agents use existing `bash` tool to run `dot` commands.

### 3.3 Agents

**Agent: `dot-author`**

| Aspect | Value |
|--------|-------|
| Purpose | Expert DOT/Graphviz authoring consultant |
| Model role | `[coding, general]` |
| Heavy context | `@dot-graph:docs/DOT_SYNTAX_REFERENCE.md`, `@dot-graph:docs/DOT_PATTERNS.md`, `@dot-graph:docs/DOT_BEST_PRACTICES.md`, `@dot-graph:docs/PIPELINE_DOT_GUIDE.md` |
| Output contract | Complete valid DOT source + explanation + render command |

Key distinction from generic agents: knows **both dialects**, chooses appropriately based on whether the user is building a pipeline or documenting architecture. Knows the shape vocabularies are different and warns against confusion.

**Agent: `diagram-reviewer`**

| Aspect | Value |
|--------|-------|
| Purpose | DOT diagram quality reviewer and optimization specialist |
| Model role | `[critique, general]` |
| Heavy context | `@dot-graph:docs/DOT_SYNTAX_REFERENCE.md`, `@dot-graph:docs/DOT_BEST_PRACTICES.md` |
| Output contract | Verdict (PASS/NEEDS WORK/FAIL) + numbered issues + corrected DOT |

### 3.4 Context Files

**Three-layer context sink pattern:**

| Layer | File | Lines | Loaded When |
|-------|------|-------|-------------|
| 1 (Behavior) | `context/dot-graph-awareness.md` | ~30 | Every session that includes behavior |
| 2 (Bundle) | `context/dot-graph-instructions.md` | ~50 | Root bundle sessions |
| 3 (Agent) | `docs/DOT_SYNTAX_REFERENCE.md` etc. | ~2000+ total | Only when agent spawns |

**Root session token cost:** ~80 lines (awareness + instructions)
**Agent session token cost:** ~1500 lines (loaded only on demand)

### 3.5 Documentation Files (Heavy Context)

| File | Lines (est.) | Content Source |
|------|-------------|----------------|
| `DOT_SYNTAX_REFERENCE.md` | 500–800 | Adapt from `dot-docs/amplifier-bundle-attractor/docs/DOT-SYNTAX.md` + ecosystem research |
| `DOT_PATTERNS.md` | 300–500 | Synthesize from attractor examples + architecture patterns |
| `DOT_BEST_PRACTICES.md` | 200–400 | Consolidate anti-patterns from DOT-CONCEPTS-DEEP-DIVE + DOT-ARTIFACTS-CATALOG |
| `PIPELINE_DOT_GUIDE.md` | 400–600 | Adapt from `DOT-AUTHORING-GUIDE.md` (541 lines) |
| `ARCHITECTURE_DOT_GUIDE.md` | 200–400 | Synthesize from `dot-quality-standards.md` + `synthesis-prompt.md` + real artifacts |

### 3.6 Skills

**`skills/dot-graph-syntax/SKILL.md`** — Quick reference for attribute names, engine selection, common mistakes. Use case: agent needs a syntax lookup without spawning the full dot-author agent.

**`skills/dot-graph-patterns/SKILL.md`** — Copy-paste templates for common graph types: state machine, architecture overview, pipeline, knowledge graph. Use case: agent building a DOT file wants a starting template.

### 3.7 Tool Module (Phase 2+)

**`modules/tool-dot-graph/`** — Python module with `mount()` entry point.

Dependencies (all pure Python, pip-installable):
- `pydot` — DOT parsing and manipulation
- `networkx` — Graph analysis algorithms (optional, Phase 3)

No dependency on `amplifier-core` (peer dependency only). No dependency on `pygraphviz` (requires C headers — too fragile for broad deployment). Graphviz CLI (`dot`) is a runtime dependency (expected on PATH).

**Tool operations:**

| Operation | Phase | Description |
|-----------|-------|-------------|
| `validate` | 2 | Syntax + structural + semantic validation |
| `render` | 3 | Render DOT to SVG/PNG/PDF |
| `analyze` | 3 | Cycle detection, path analysis, connectivity |
| `info` | 2 | Node/edge/subgraph counts, graph metadata |

### 3.8 What to Reuse vs. Create New

| Asset | Action | Rationale |
|-------|--------|-----------|
| `dot-docs/DOT-AUTHORING-GUIDE.md` (541 lines) | **Adapt** → `PIPELINE_DOT_GUIDE.md` | Comprehensive attractor pipeline authoring guide — restructure for bundle context |
| `dot-docs/DOT-SYNTAX.md` (167 lines) | **Adapt** → `DOT_SYNTAX_REFERENCE.md` | Good base — expand with ecosystem research (layout engines, advanced features) |
| `dot-docs/dot-reference.md` (138 lines) | **Adapt** → `skills/dot-graph-syntax/SKILL.md` | Compact quick reference — perfect skill format |
| `dot-docs/dot-quality-standards.md` (148 lines) | **Adapt** → `DOT_BEST_PRACTICES.md` + `ARCHITECTURE_DOT_GUIDE.md` | Quality rules for architecture DOT — split into best practices and dialect guide |
| `dot-docs/dot_validation.py` (216 lines) | **Reuse** → `modules/tool-dot-graph/validate.py` | Working validation implementation — adapt for tool module API |
| `dot-docs/structural_change.py` (212 lines) | **Reference only** | Useful pattern for tiered refresh — not directly needed in bundle |
| `dot-docs/discovery_metadata.py` (112 lines) | **Reference only** | Metadata management — not directly needed in bundle |
| `dot-docs/synthesis-prompt.md` (145 lines) | **Adapt** → `ARCHITECTURE_DOT_GUIDE.md` | Synthesis instructions — incorporate into architecture DOT guide |
| `dot-docs/prescan-prompt.md` (114 lines) | **Reference only** | Topic selection — specific to dotfiles-discovery pipeline |
| `amplifier-foundation/generate_event_dot.py` (379 lines) | **Reference for Phase 4** | Source-introspection DOT generation — pattern to follow for future tools |
| `consensus_task.dot` (158 lines) | **Reference** | Canonical node_type dialect example for compatibility documentation |
| `semport.dot` (33 lines) | **Reference** | Compact autonomous loop example |
| Attractor example pipelines (15 files) | **Reference** | Pattern examples for `DOT_PATTERNS.md` |
| Architecture DOT files (4 files) | **Reference** | Real-world examples for `ARCHITECTURE_DOT_GUIDE.md` |
| DOT-DIALECT-COMPARISON.md research | **Incorporate** | Dialect awareness must be embedded in agent instructions |

---

## 4. Implementation Phases

### Phase 1: Minimum Viable Bundle (Agents + Context Only)

**Goal:** DOT expertise available via agent delegation, zero custom tooling.
**Effort:** Medium (primarily content authoring)
**Value:** Immediate — centralizes DOT knowledge, prevents convention drift

**Deliverables:**

```
amplifier-bundle-dot-graph/
├── bundle.md
├── behaviors/
│   └── dot-graph.yaml              # agents + context only (no tools)
├── agents/
│   ├── dot-author.md
│   └── diagram-reviewer.md
├── context/
│   ├── dot-graph-awareness.md
│   └── dot-graph-instructions.md
├── docs/
│   ├── DOT_SYNTAX_REFERENCE.md
│   ├── DOT_PATTERNS.md
│   ├── DOT_BEST_PRACTICES.md
│   ├── PIPELINE_DOT_GUIDE.md
│   └── ARCHITECTURE_DOT_GUIDE.md
├── skills/
│   ├── dot-graph-syntax/
│   │   └── SKILL.md
│   └── dot-graph-patterns/
│       └── SKILL.md
└── README.md
```

**Key decisions for Phase 1:**
- Agents use `bash` tool to run `dot -Tsvg` for validation/rendering
- Both dialects documented explicitly with "when to use which" guidance
- No tool module needed — agents carry all knowledge
- Skills provide quick-reference lookups without spawning full agents

**Success criteria:**
- `dot-graph:dot-author` can create correct pipeline DOT and architecture DOT
- `dot-graph:diagram-reviewer` can review DOT files against quality standards
- Agents correctly identify which dialect is appropriate for each use case
- Root sessions delegate DOT work rather than attempting it directly

### Phase 2: Add Validation Tool

**Goal:** Programmatic DOT validation without spawning an agent.
**Effort:** Low-Medium (adapt existing `dot_validation.py`)
**Value:** High — enables quick validation in pipelines, recipes, and CI

**Deliverables:**

```
+ modules/
+   └── tool-dot-graph/
+       ├── pyproject.toml            # deps: pydot
+       └── tool_dot_graph/
+           ├── __init__.py
+           ├── tool.py               # mount() with validate + info operations
+           └── validate.py           # Adapted from dot_validation.py
```

**Tool operations:**

```
dot_graph validate <file_or_content> [--dialect=pipeline|architecture|auto]
dot_graph info <file_or_content>
```

Update `behaviors/dot-graph.yaml` to include `tools:` section.

**Validation tiers:**

| Tier | Checks | Pipeline Dialect | Architecture Dialect |
|------|--------|-----------------|---------------------|
| Syntax | Grammar validity | ✓ | ✓ |
| Structure | Entry/exit nodes, reachability | ✓ | — |
| Quality | Line count, render test | — | ✓ |
| Convention | Shape vocabulary, naming | ✓ | ✓ |

**Success criteria:**
- `dot_graph validate pipeline.dot` catches missing start/exit nodes
- `dot_graph validate overview.dot --dialect=architecture` checks line count + legend
- `dot_graph info graph.dot` returns node count, edge count, subgraph list
- Recipe steps can call `dot_graph validate` without spawning an agent

### Phase 3: Add Rendering and Analysis Tools

**Goal:** Full render + graph analysis pipeline.
**Effort:** Medium
**Value:** Medium — rendering currently works via `bash` + `dot`; analysis adds novel capability

**Deliverables:**

```
+ tool_dot_graph/
+     ├── render.py               # SVG/PNG/PDF rendering wrapper
+     └── analyze.py              # NetworkX-based graph analysis
```

**New tool operations:**

```
dot_graph render <file> [--format=svg|png|pdf] [--engine=dot|neato|fdp|circo]
dot_graph analyze <file> [--checks=cycles,paths,connectivity,isolated]
```

**Dependencies added:** `networkx` (for analysis), `graphviz` Python package (for rendering).

**Analysis capabilities:**
- Cycle detection with cycle path reporting
- DAG verification
- Topological sort (execution ordering)
- Path reachability (can node X reach node Y?)
- Connected component identification
- Isolated node detection
- Entry/exit point identification (in-degree 0 / out-degree 0)

**Success criteria:**
- `dot_graph render overview.dot --format=svg` produces valid SVG
- `dot_graph analyze pipeline.dot` reports cycles and unreachable nodes
- Analysis results are structured (JSON-like) for programmatic consumption

### Phase 4: Advanced Features

**Goal:** Dialect unification, source-to-DOT generation, discovery pipeline integration.
**Effort:** High
**Value:** Strategic — enables ecosystem-wide DOT standardization

**Deliverables:**

1. **Dialect unification support:**
   - Validation tool accepts both dialects transparently
   - Handler resolution order: `node_type` > `shape` > default
   - Attribute aliases: `llm_prompt` → `prompt`, `context_fidelity_default` → `default_fidelity`
   - Migration guidance: convert node_type DOT to Attractor dialect

2. **Source-to-DOT generation (new agent or tool):**
   - Generate `events.dot` from Python source introspection (adapt `generate_event_dot.py`)
   - Generate dependency DOT from package manifests
   - Recipe-to-DOT visualization (adapter for recipe-author)

3. **Discovery pipeline integration:**
   - Bundle behavior composable into dotfiles-discovery pipeline
   - Validation tool callable from synthesis recipe
   - Quality standards enforceable as recipe gates

4. **Additional agents (if warranted by usage):**
   - `dot-converter` — Convert between DOT and other formats (Mermaid, PlantUML)
   - `pipeline-author` — Specialized for Attractor pipeline DOT (if dot-author proves too broad)

**Success criteria:**
- Existing `consensus_task.dot` (node_type dialect) validates without modification
- `generate_event_dot` pattern generalized into reusable source-introspection tool
- Dotfiles-discovery pipeline uses bundle's validation tool instead of inline validation

### Phase Summary

| Phase | Scope | Effort | Value | Dependencies |
|-------|-------|--------|-------|-------------|
| 1 | Agents + context + skills + docs | Medium | **Immediate** | None — content authoring only |
| 2 | Validation tool | Low-Medium | **High** | Graphviz CLI on PATH, `pydot` |
| 3 | Rendering + analysis tools | Medium | Medium | `networkx`, `graphviz` Python pkg |
| 4 | Dialect unification + generation | High | Strategic | Phase 2-3 complete, design decisions resolved |

---

## 5. Open Questions & Design Decisions

### Q1: Dialect Documentation Strategy

**Question:** Should the bundle present DOT as "one language with two usage profiles" or "two distinct dialects that share syntax"?

**Context:** The Attractor pipeline dialect and architecture documentation dialect use the same DOT syntax but with fundamentally different shape vocabularies and attribute conventions. A `diamond` means "conditional routing gate (no LLM)" in pipeline DOT but "decision/transform component" in architecture DOT.

**Options:**
- **A) Unified presentation:** One syntax reference with a "Usage Profile" section explaining the two contexts. Simpler for agents, but risks confusion when shapes overlap.
- **B) Separate guides:** Dedicated `PIPELINE_DOT_GUIDE.md` and `ARCHITECTURE_DOT_GUIDE.md` with shared syntax reference. Clearer separation, but more docs to maintain.
- **C) Unified with dialect annotations:** One reference with inline callouts like "⚡ Pipeline: conditional gate | 📐 Architecture: decision point" for each shape.

**Recommendation:** Option B — separate guides plus shared syntax reference. The dialects serve fundamentally different purposes (runtime execution vs. visual documentation), and mixing them in one guide creates confusion. The shared syntax reference covers DOT-the-language; the dialect guides cover DOT-for-purpose.

**Decision needed:** Confirm approach before Phase 1 content authoring.

### Q2: Should the Bundle Own the Attractor DOT Reference?

**Question:** The most comprehensive DOT authoring documentation currently lives in `amplifier-bundle-attractor/docs/DOT-AUTHORING-GUIDE.md`. Should the dot-graph bundle absorb this content, or should it reference the attractor bundle's docs?

**Context:** The attractor bundle owns the runtime that executes pipeline DOT. The dot-graph bundle owns DOT expertise broadly. There's a natural tension: pipeline DOT semantics are defined by the attractor engine, but DOT authoring best practices are general knowledge.

**Options:**
- **A) dot-graph owns all DOT docs:** Attractor bundle's DOT guide moves to or is replaced by dot-graph bundle's `PIPELINE_DOT_GUIDE.md`. Attractor references `@dot-graph:docs/PIPELINE_DOT_GUIDE.md`.
- **B) Parallel docs:** Both bundles maintain their own DOT docs. Risk of drift, but each bundle owns its domain.
- **C) Layered ownership:** dot-graph owns general DOT (syntax, patterns, best practices). Attractor owns pipeline-specific semantics (shape-to-handler mapping, node attributes, edge conditions). dot-graph's pipeline guide references attractor's docs for runtime specifics.

**Recommendation:** Option C — layered ownership. dot-graph is the DOT language expert; attractor is the pipeline runtime expert. The `PIPELINE_DOT_GUIDE.md` in dot-graph covers "how to write good pipeline DOT" while deferring to attractor for "what each shape does at runtime."

**Decision needed:** Confirm ownership boundary before Phase 1.

### Q3: Tool Scope — Validate Only vs. Full Lifecycle

**Question:** Should the Phase 2 tool be narrowly scoped (validation only) or include rendering from the start?

**Context:** Rendering already works via `bash` + `dot -Tsvg`. A custom tool adds convenience (structured output, engine auto-selection) but not new capability. Validation, however, enables novel workflow gates (recipe validation steps, CI checks).

**Options:**
- **A) Validate-only Phase 2, render in Phase 3:** Fastest path to novel value. Rendering stays as bash for now.
- **B) Validate + render in Phase 2:** More complete tool from the start. Slightly more effort but avoids a "partially useful" tool.

**Recommendation:** Option A — validation is the novel value. Rendering via bash works fine and doesn't justify delaying validation.

**Decision needed:** Confirm scope before Phase 2 implementation.

### Q4: node_type Dialect Compatibility

**Question:** Should the bundle's validation tool accept node_type dialect DOT files, or only Attractor dialect?

**Context:** The DOT-DIALECT-COMPARISON research recommends "Attractor as the primary dialect with node_type as a supported compatibility alias." Two production files (`consensus_task.dot`, `semport.dot`) use the node_type dialect.

**Options:**
- **A) Attractor-only:** Simpler validation. node_type files would need migration. Risk: breaks existing pipelines.
- **B) Both with auto-detection:** Detect dialect from presence of `node_type` attribute. Apply appropriate validation rules. More complex but backward-compatible.
- **C) Both with explicit flag:** `--dialect=attractor|node_type|auto`. User must specify. Clear but adds friction.

**Recommendation:** Option B — auto-detect with explicit override available. The handler resolution order (`node_type` > `shape` > default) makes this feasible. Existing files work unchanged.

**Decision needed:** Confirm before Phase 2 implementation.

### Q5: Hand-Maintained vs. Generated DOT — Bundle's Position

**Question:** Should the bundle take a position on hand-maintained vs. generated DOT?

**Context:** Expert consensus from session `c95ce204`: "Hand-maintained DOT files won't be maintained. Generate from source." But LLM-synthesized DOT from Parallax Discovery is neither hand-maintained nor deterministically generated — it's a third category.

**Three categories of DOT production:**
1. **Hand-maintained:** Written by humans, committed to repo. Rots without discipline.
2. **Deterministically generated:** Script introspects source → produces DOT. Cheap, deterministic, limited to structural relationships.
3. **LLM-synthesized:** Agent investigates repo → produces DOT. Expensive, richer, captures behavioral insights.

**Options:**
- **A) Neutral:** Bundle provides tools for all approaches. No position.
- **B) Opinionated:** Bundle recommends LLM-synthesized for architecture DOT, generated-from-source for structural DOT, hand-maintained for pipeline DOT (since pipelines are inherently authored artifacts).
- **C) Pragmatic:** Bundle documents the tradeoffs and provides guidance per use case.

**Recommendation:** Option C — pragmatic guidance per use case. Pipeline DOT (UC-1) is authored by definition. Architecture DOT (UC-2) benefits from LLM synthesis. Event DOT (UC-3) should be generated from source. The bundle should encode this guidance without being dogmatic.

**Decision needed:** Confirm approach before writing `DOT_BEST_PRACTICES.md`.

### Q6: Bundle Registration — Standalone vs. Foundation-Included

**Question:** Should the dot-graph behavior be included in the default foundation bundle?

**Context:** Including it in foundation means every Amplifier session gets DOT awareness (~30 lines of context). Not including it means users must explicitly add the bundle.

**Options:**
- **A) Foundation-included from Phase 1:** Maximum reach. Every session can delegate DOT work.
- **B) Standalone first, foundation later:** Prove value independently. Avoids adding context cost to sessions that never use DOT.
- **C) Foundation-included after Phase 2:** Include once the validation tool provides novel programmatic value beyond agent delegation.

**Recommendation:** Option B for Phase 1, then evaluate after proving value. The thin awareness pointer (~30 lines) is cheap, but the principle of minimal context loading suggests proving the bundle's value before propagating it to every session.

**Decision needed:** Confirm registration strategy.

### Q7: Rendering Target for Non-Terminal Environments

**Question:** When an agent renders DOT to SVG, how does the user see it?

**Context:** Amplifier sessions run in terminals. SVG files can be written to disk but not displayed inline. The TUI doesn't render images. The resolve dashboard had rendering issues with `ts-graphviz`.

**Options:**
- **A) File output only:** Render to file, provide path. User opens in browser/viewer.
- **B) ASCII art fallback:** Use `dot -Tascii` for terminal preview, SVG for full quality.
- **C) Web viewer integration:** Generate SVG + open in browser automatically (if available).

**Recommendation:** Option A for now, with Option B as enhancement. The primary value is the DOT source itself (agents read DOT, not images). Rendering is a convenience for human verification.

**Decision needed:** Not blocking — can iterate.

### Q8: Skill Installation — Bundle-Shipped vs. User-Level

**Question:** Should skills be shipped inside the bundle or installed to `~/.amplifier/skills/`?

**Context:** Skills in the bundle are available only when the bundle is loaded. Skills in `~/.amplifier/skills/` are available in all sessions regardless of bundle.

**Options:**
- **A) Bundle-only:** Skills are part of the bundle. Available only when dot-graph is loaded.
- **B) User-level:** Skills installed to `~/.amplifier/skills/`. Available everywhere.
- **C) Both:** Ship in bundle + provide install script for user-level.

**Recommendation:** Option A — bundle-shipped. Skills complement the agent expertise; having them without the agents creates incomplete capability. If the bundle is included in foundation (Q6), skills would be universally available anyway.

**Decision needed:** Minor — can adjust later.

---

## 6. Existing Asset Inventory

### 6.1 From dot-docs Workspace (`/home/bkrabach/dev/dot-docs/`)

**Documentation — High reuse value:**

| File | Lines | Reuse Action | Target |
|------|-------|-------------|--------|
| `amplifier-bundle-attractor/docs/DOT-AUTHORING-GUIDE.md` | 541 | **Adapt** | `docs/PIPELINE_DOT_GUIDE.md` |
| `amplifier-bundle-attractor/docs/DOT-SYNTAX.md` | 167 | **Adapt** | `docs/DOT_SYNTAX_REFERENCE.md` |
| `amplifier-bundle-attractor/context/dot-reference.md` | 138 | **Adapt** | `skills/dot-graph-syntax/SKILL.md` |
| `dot-docs/context/dot-quality-standards.md` | 148 | **Adapt** | `docs/DOT_BEST_PRACTICES.md` + `docs/ARCHITECTURE_DOT_GUIDE.md` |
| `dot-docs/context/synthesis-prompt.md` | 145 | **Incorporate** | `docs/ARCHITECTURE_DOT_GUIDE.md` (synthesis conventions) |
| `dot-docs/context/prescan-prompt.md` | 114 | **Reference** | Phase 4 discovery integration |

**Tooling — Direct reuse:**

| File | Lines | Reuse Action | Target |
|------|-------|-------------|--------|
| `dot-docs/tools/dotfiles_discovery/dot_validation.py` | 216 | **Adapt** | `modules/tool-dot-graph/validate.py` |
| `dot-docs/tools/dotfiles_discovery/structural_change.py` | 212 | **Reference** | Phase 4 tiered refresh |
| `dot-docs/tools/dotfiles_discovery/discovery_metadata.py` | 112 | **Reference** | Phase 4 discovery integration |

**Recipes — Reference for integration:**

| File | Lines | Reuse Action | Notes |
|------|-------|-------------|-------|
| `dot-docs/recipes/dotfiles-discovery.yaml` | 500 | **Reference** | Orchestrator recipe — Phase 4 integration point |
| `dot-docs/recipes/dotfiles-prescan.yaml` | 86 | **Reference** | Per-repo topic selection |
| `dot-docs/recipes/dotfiles-synthesis.yaml` | 177 | **Reference** | Synthesis recipe — will use bundle's validation tool |

**Real-world DOT artifacts — Examples:**

| File | Lines | Reuse Action | Notes |
|------|-------|-------------|-------|
| `dotfiles/bkrabach/amplifier-bundle-modes/overview.dot` | 173 | **Example** | Reference architecture overview in docs |
| `dotfiles/bkrabach/amplifier-bundle-modes/architecture.dot` | 350 | **Example** | Reference architecture detail in docs |
| `dotfiles/bkrabach/amplifier-resolve/overview.dot` | 236 | **Example** | Reference architecture overview in docs |
| `dotfiles/bkrabach/amplifier-resolve/architecture.dot` | 260 | **Example** | Reference architecture detail in docs |

### 6.2 From amplifier-bundle-attractor

**Pipeline DOT examples — Pattern library source:**

| Category | Files | Reuse Action |
|----------|-------|-------------|
| Tutorial ladder | `01-simple-linear.dot` → `10-full-attractor.dot` (10 files) | **Reference** for `DOT_PATTERNS.md` |
| Practical templates | `pr-review.dot`, `feature-build.dot`, `bug-fix.dot`, `refactor.dot`, `test-gen.dot` | **Reference** for pattern examples |
| Reusable patterns | `convergence-factory.dot`, `conversational-gate.dot` + 3 demos | **Reference** for composable pattern docs |
| Test fixtures | 12 unit + 7 integration + 4 E2E DOT files | **Reference** for validation test cases |

### 6.3 From amplifier-foundation

| File | Lines | Reuse Action | Notes |
|------|-------|-------------|-------|
| `scripts/generate_event_dot.py` | 379 | **Pattern reference** for Phase 4 | Source-introspection DOT generation |

Key functions to reference:
- `scan_emitted_events(content)` — regex extraction of `hooks.emit()` calls
- `scan_registered_events(content)` — finds `register_capability` calls
- `is_canonical_event(name)` — core namespace check
- `generate_dot(data)` — DOT string generation from scan results

### 6.4 From amplifier-resolve

| File | Lines | Reuse Action | Notes |
|------|-------|-------------|-------|
| `core/pipelines/resolve_quick.dot` | ~50 | **Example** | Production pipeline DOT |
| `core/pipelines/resolve_consensus.dot` | ~100 | **Example** | Multi-model pipeline DOT |
| DOT test infrastructure | Various | **Reference** | Patterns for testing DOT validation |

### 6.5 From Root Dev Directory

| File | Lines | Reuse Action | Notes |
|------|-------|-------------|-------|
| `~/dev/consensus_task.dot` | 158 | **Example** | Canonical node_type dialect example |
| `~/dev/semport.dot` | 33 | **Example** | Compact autonomous loop example |

### 6.6 From This Research Effort

| File | Reuse Action | Target |
|------|-------------|--------|
| `DOT-ECOSYSTEM-RESEARCH.md` | **Extract** | Layout engine guide → `DOT_SYNTAX_REFERENCE.md`; Python library recommendations → `modules/tool-dot-graph/`; validation approaches → `validate.py` |
| `DOT-DIALECT-COMPARISON.md` | **Extract** | Dialect awareness sections → `PIPELINE_DOT_GUIDE.md` + agent instructions; unification spec → Phase 4 |
| `DOT-ARTIFACTS-CATALOG.md` | **Extract** | Anti-pattern lists → `DOT_BEST_PRACTICES.md`; pattern catalog → `DOT_PATTERNS.md` |
| `DOT-CONCEPTS-DEEP-DIVE.md` | **Extract** | Philosophical principles → agent instructions; tool/capability ideas → capability map |
| `SESSION-INDEX.md` | **Reference** | Usage pattern data for prioritization |
| `BUNDLE-GUIDANCE.md` | **Apply** | Direct application to bundle structure |

### Asset Reuse Summary

| Action | Count | Description |
|--------|-------|-------------|
| **Adapt** (restructure for bundle) | 7 files | DOT docs, quality standards, validation tool |
| **Reference** (patterns/examples) | 30+ files | Pipeline examples, architecture DOTs, recipes |
| **Extract** (pull sections into new docs) | 6 files | This research effort's output |
| **Direct reuse** | 1 file | `dot_validation.py` core logic |

**Estimated new content to author:** ~60% — most documentation needs restructuring and synthesis rather than writing from scratch. The heavy lifting is adapting existing content to the bundle's context-sink architecture and consolidating scattered conventions into authoritative references.

---

## Appendix: Key Design Principles

Distilled from all six research documents, these principles should guide all phases:

1. **DOT is a dual-purpose format** — simultaneously human-renderable and agent-scannable. Every design decision should preserve both audiences.

2. **Two dialects, one language** — Pipeline DOT and architecture DOT share syntax but diverge on semantics. The bundle must serve both without conflating them.

3. **Context sink pattern** — Heavy DOT knowledge lives in agents, not root sessions. Keep the awareness pointer thin (~30 lines).

4. **Generate over hand-maintain** — For documentation DOT, prefer LLM-synthesized or source-generated over hand-maintained. For pipeline DOT, authoring is inherent.

5. **DOT diagrams are discovery tools** — The act of creating a DOT diagram forces precise understanding. The bundle should promote DOT creation as an analytical practice, not just a documentation chore.

6. **Progressive disclosure** — `overview.dot` (150–250 lines) → detail files (200–400 lines) → raw investigation artifacts. The bundle's quality standards encode this hierarchy.

7. **Attractor dialect is primary for pipelines** — More expressive, more LLM-friendly, lower error surface, ~3-4× more token-efficient. The node_type dialect is supported for backward compatibility.

8. **Thin bundle pattern** — The bundle declares nothing that foundation provides. Value comes from agents, context, and (eventually) tools.

9. **Simplest thing that works first** — Phase 1 has no custom tool. Agents use `bash` + `dot`. Value comes from centralized expertise, not machinery.

10. **Build for the ecosystem** — The behavior pattern ensures any bundle can compose DOT capabilities. This isn't a standalone product; it's a capability that flows through the Amplifier graph.
