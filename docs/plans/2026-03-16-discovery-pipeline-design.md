# Discovery Pipeline Design

## Goal

Add a discovery pipeline to `amplifier-bundle-dot-graph` that systematically walks codebases and generates DOT graph representations of their architecture. The pipeline builds bottom-up (file → module → subsystem → overview), uses multi-agent consensus at each level with tiered fidelity (quick/standard/deep), and produces a persistent hierarchy of DOT files that enables "Google Maps-style" navigation — zoom in, zoom out, pan around — with the context window as the fixed "screen size."

Starts as single-repo focused, designed for multi-repo extension.

## Background

The existing `dot-graph` bundle provides tools for validating, analyzing, and rendering DOT files, plus agents for authoring and reviewing diagrams. What it lacks is the ability to *discover* architecture from a codebase — users must manually describe what they want diagrammed.

For any non-trivial codebase, manual diagramming misses structure. Developers forget about integration points, miss implicit dependencies, and produce diagrams that reflect intent rather than reality. A systematic discovery pipeline solves this by walking the code, building architectural understanding from the bottom up, and reconciling multiple agent perspectives into consensus diagrams.

Three multi-agent consensus patterns from the ecosystem inform this design:

1. **Fan-out/Consolidate** — 3 parallel agents, provider-diverse, file-glob reconciliation
2. **Cross-Provider Editorial Chain** — sequential specialist handoff, failure analysis by different provider
3. **Triplicate Investigation** (Parallax Discovery) — role-specialized agents, fresh context independence, discrepancy-driven reconciliation, progressive rigor waves

The fidelity tiers map these patterns to cost: quick uses none, standard uses fan-out/consolidate, deep uses the full triplicate pattern.

## Approach

Hybrid static analysis + LLM enrichment with multi-agent consensus. Static tools produce deterministic structural facts (directory trees, file counts, module boundaries). LLM agents enrich those facts with architectural judgment (component relationships, data flow, integration patterns). Multiple agents investigate independently with fresh context, and a synthesizer reconciles their outputs — treating discrepancies as signals, not noise.

The pipeline is orchestrated by Amplifier recipes with approval gates, giving users control over cost before expensive investigation steps. Fidelity tiers (quick/standard/deep) scale the number of agents and iteration depth based on the scope of changes detected.

## Architecture

### Bundle Behavior Decomposition

The existing `behaviors/dot-graph.yaml` is split into sub-behaviors:

```
behaviors/
├── dot-graph.yaml          # "Everything" — includes core + discovery
├── dot-core.yaml           # Tools + authoring/review agents + skills (what exists today)
└── dot-discovery.yaml      # Discovery pipeline + investigation agents (NEW)
```

How consumers pick what they want:

- `amplifier bundle add ...behaviors/dot-graph.yaml --app` → everything (default)
- `...behaviors/dot-core.yaml` → just tools + authoring agents (no discovery pipeline)
- `...behaviors/dot-discovery.yaml` → discovery pipeline (auto-includes core)

`dot-graph.yaml` (everything):

```yaml
includes:
  - bundle: dot-graph:behaviors/dot-core
  - bundle: dot-graph:behaviors/dot-discovery
```

`dot-discovery.yaml` internally includes `dot-core` — so consumers never need to include both. Composition is idempotent (modules merge by ID). This follows the `sessions.yaml` → `logging` precedent from foundation.

### Pipeline Stages & Mechanism Map

Each stage uses the appropriate Amplifier mechanism:

| Stage | Mechanism | Why |
|-------|-----------|-----|
| **1. Change Detection** | **Bash step** (git diff) | Git diffing, file counting, tier assignment — 100% deterministic. Identifies what changed, assigns fidelity tier, computes ancestor invalidation chain. |
| **2. Prescan** | **Tool** (structural scan) + **Agent** (topic selection) | Tool walks directory tree, detects language, counts files, identifies modules — deterministic facts. Agent reads the structural inventory + README and selects 3-7 investigation topics — requires judgment. |
| **3. Investigation** | **Agents** (defined in bundle, dispatched by recipe) | Per-topic, dispatch 1-3 agents depending on fidelity tier. Each produces independent DOT + findings. Fresh context (`context_depth="none"`) for genuine independence. |
| **4. Reconciliation** | **Agent** (as recipe step) | Reads all investigation DOT outputs, synthesizes into coherent per-module DOT with discrepancy tracking. Quality gate loop (synthesize → validate → fix, max 3 iterations). |
| **5. Validation** | **Tool** (already exists — `dot_graph validate + analyze`) | Three-layer validation + graph intelligence checks. Already shipped in Phases 2/3. |
| **6. Assembly** | **Tool** (new Python code) | Merge per-module DOT into subsystem and overview graphs with subgraph hierarchy. Deterministic graph manipulation. Handles ancestor invalidation — regenerates parent graphs up the chain. |
| **Outer Orchestration** | **Recipe** | Stage sequencing, approval gates, foreach loops over topics/modules, conditional routing based on fidelity tier, checkpointing for resumability. |

The recipe is the policy layer — it reads the fidelity tier and activates the right mechanisms via conditional steps. The agents and tools don't know about tiers. This is mechanism/policy separation.

### Fidelity Tiers

Fidelity tiers control which mechanisms activate at each stage:

| Stage | `quick` | `standard` | `deep` |
|-------|---------|-----------|--------|
| Change Detection | Full (same at all tiers) | Full | Full |
| Prescan | Tool only (reuse last topics) | Tool + Agent | Tool + Agent (more topics) |
| Investigation | Skip (patch affected files only) | 2 agents per topic (code-tracer + integration-mapper) | 3 agents per topic (full triplicate) |
| Reconciliation | Skip | Single-pass synthesis | Synthesis + quality gate loop (max 3) |
| Validation | Syntax only | Syntax + structural | Syntax + structural + graph intelligence |
| Assembly | Patch affected subgraphs only | Regen affected subsystem + overview | Full regen of all levels |

Estimated agent dispatch budget per tier: quick = 0-1, standard = 10-15, deep = 25-30. Budget is shown in the approval gate so users can make informed cost decisions.

## Components

### Investigation Agents

Five new agents defined in the bundle, all name-prefixed with `discovery-` and living flat in `agents/` alongside existing `dot-author` and `diagram-reviewer`:

#### `discovery-prescan`

**Role:** Topic selector — reads structural inventory + README, selects investigation topics.

**Produces:** Topic list as structured JSON.

**Fidelity:** standard + deep.

The prescan agent receives the structural scan output (language, file counts, module boundaries, directory tree) and applies judgment to select 3-7 investigation topics. Each topic maps to a module or cross-cutting concern that warrants architectural investigation.

#### `discovery-code-tracer`

**Role:** **HOW** — traces execution paths, call chains, data flow.

**Produces:** `findings.md` + `diagram.dot` with file:line evidence.

**Fidelity:** standard + deep.

LSP-oriented instructions guide this agent to trace actual code paths rather than guessing from file names. The agent uses `goToDefinition`, `findReferences`, `incomingCalls`, and `outgoingCalls` to build evidence-backed call graphs.

#### `discovery-behavior-observer`

**Role:** **WHAT** — catalogs real instances, quantifies patterns.

**Produces:** `catalog.md` + `patterns.md` + `diagram.dot`.

**Fidelity:** deep only.

This agent catalogs concrete instances of architectural patterns (e.g., "there are 7 API endpoints in this module, 3 use middleware X, 4 use middleware Y"). Quantified observations ground the architecture in reality rather than aspirational descriptions.

#### `discovery-integration-mapper`

**Role:** **WHERE/WHY** — maps cross-boundary connections.

**Produces:** `integration-map.md` + `diagram.dot`.

**Fidelity:** standard + deep.

Focuses on the seams between modules — API boundaries, shared databases, message queues, file-based integration, environment variable coupling. Maps both explicit and implicit dependencies.

#### `discovery-synthesizer`

**Role:** Reconciler — reads all agent DOT outputs, produces consensus.

**Produces:** Reconciled `diagram.dot` + `discrepancies.md`.

**Fidelity:** standard + deep.

Reads all investigation agent outputs for a given module and produces a single consensus DOT file. Discrepancies between agent outputs are tracked in `discrepancies.md` — these are signals about architectural ambiguity, not errors to suppress.

#### Agent Design Decisions

- **Agents are static definitions** — carefully crafted prompts in `agents/`, not dynamically generated. The code-tracer needs LSP-oriented instructions, the behavior-observer needs catalog methodology, the integration-mapper needs boundary analysis techniques. These are distinct personas.
- **Fresh context per agent** (`context_depth="none"`) — critical for genuine independence. No agent sees another's work during investigation.
- **Heavy instructions live in context files** — each agent's definition `@mentions` a corresponding `context/discovery-*-instructions.md` file with detailed methodology.
- **The recipe controls which agents fire** — at `quick` tier, no investigation agents. At `standard`, code-tracer + integration-mapper. At `deep`, all three.

### New Tool Operations

Two new operations added to the existing `tool-dot-graph` module:

#### `prescan` — Structural Codebase Scan

- **Input:** `repo_path`
- **Output:** Structured JSON inventory — language, file counts by type, detected modules/packages, build manifests, entry points, directory tree with depth
- **Implementation:** Pure Python (`os.walk`, file parsing), no LLM, no graphviz

This gives the prescan agent the deterministic facts it needs to select investigation topics without burning tokens on directory traversal.

Module boundary detection uses directory structure + language-specific heuristics:

- Python packages with `__init__.py`
- Rust crates with `Cargo.toml`
- Go modules with `go.mod`
- Node packages with `package.json`

For monorepos, the prescan detects multiple packages and produces per-package entries. For single-package repos, one module entry. No user configuration needed for common cases.

#### `assemble` — Hierarchical DOT Assembly

- **Input:** `manifest` (JSON mapping module DOT files → subsystem groupings → overview), `output_dir`
- **Output:** Assembled subsystem DOT files + `overview.dot` with subgraph hierarchy
- **Implementation:** Pure pydot graph manipulation — deterministic, no LLM

Takes per-module DOT files (the building blocks), groups them into subsystem clusters based on the manifest, generates `subgraph` wrappers with proper edge routing between clusters, produces a bounded overview (≤250 lines, ≤80 nodes) with rendered legend.

Handles **ancestor invalidation** — the manifest tracks the dependency tree (which modules → which subsystems → overview), so when a module DOT changes, the tool knows which parent graphs to regenerate.

#### Change Detection (Bash Step)

Change detection is a recipe bash step rather than a tool operation — it's `git log --since` and `git diff --stat` against a stored commit hash. Simple enough that wrapping it in a tool adds indirection without value. The output is a tier assignment (quick/standard/deep) that the recipe uses for conditional routing.

## Data Flow

### Output Artifact Hierarchy

The pipeline builds DOT bottom-up into a persistent `.discovery/` directory inside the target repo:

```
.discovery/
├── last-run.json                    # Metadata: commit hash, timestamp, tier used
├── manifest.json                    # Map: which source dirs → which DOT files
├── modules/
│   ├── auth/
│   │   ├── diagram.dot              # Per-module DOT (atomic building block)
│   │   ├── findings.md              # What was discovered about this module
│   │   └── agents/                  # Raw agent outputs (standard/deep fidelity)
│   │       ├── code-tracer/
│   │       │   ├── diagram.dot
│   │       │   └── findings.md
│   │       └── integration-mapper/
│   │           ├── diagram.dot
│   │           └── findings.md
│   ├── payments/
│   │   ├── diagram.dot
│   │   ├── findings.md
│   │   └── agents/...
│   └── ...
├── subsystems/
│   ├── identity.dot                 # Subsystem DOT (modules as subgraphs)
│   ├── billing.dot
│   └── ...
└── overview.dot                     # Top-level architecture (subsystems as subgraphs)
```

### Information Flow Through Stages

```
Source Code
    │
    ▼
[Change Detection] ──► fidelity tier (quick/standard/deep)
    │                   + list of changed files
    ▼
[Prescan Tool] ──► structural JSON inventory
    │               (language, modules, file counts, tree)
    ▼
[Prescan Agent] ──► selected topics (3-7 investigation targets)
    │
    ▼ (approval gate — user reviews topics)
    │
[Investigation Agents] ──► per-topic DOT + findings
    │  (1-3 agents per topic,     (each agent writes to
    │   fresh context each)        modules/<name>/agents/<agent>/)
    ▼
[Synthesizer Agent] ──► per-module consensus DOT + discrepancies
    │  (reads all agent outputs     (writes to modules/<name>/diagram.dot)
    │   for each module)
    ▼
[Validation Tool] ──► pass/fail (quality gate loop, max 3 iterations)
    │
    ▼
[Assembly Tool] ──► subsystem DOTs + overview.dot
    │  (reads manifest,              (writes to subsystems/ and overview.dot)
    │   groups modules into
    │   subgraph clusters)
    ▼
[Final Validation] ──► all outputs validated
```

### Manifest and Invalidation

`manifest.json` tracks the dependency graph at module/directory level:

- Source directories → module DOT files (e.g., `src/auth/**` → `modules/auth/diagram.dot`)
- Module DOT files → subsystem DOT files (e.g., `modules/auth` + `modules/users` → `subsystems/identity.dot`)
- Subsystem DOT files → `overview.dot`

When change detection finds modified files, it walks this manifest upward to determine the full invalidation chain. A change in `src/auth/` invalidates `modules/auth/diagram.dot`, which invalidates `subsystems/identity.dot`, which invalidates `overview.dot`.

Module/directory level granularity is the default. File-level glob patterns may be added as a future enhancement.

## Recipe Structure

### Outer Recipe: `recipes/discovery-pipeline.yaml`

Main entry point. Staged recipe with approval gates.

```
Stage 1: "scan" (no approval needed)
├── Step: change-detect (bash) — git diff against .discovery/last-run.json
├── Step: structural-scan (bash) — dot_graph operation="prescan" on repo
└── Step: topic-select (agent) — discovery-prescan reads inventory, selects topics
    └── Conditional: if fidelity=quick AND no new topics, exit early

[Approval Gate — user reviews topics before expensive investigation]

Stage 2: "investigate" (approval required)
└── Step: investigate-topics (foreach over topics)
    └── Sub-recipe: recipes/discovery-investigate-topic.yaml
        ├── Step: code-tracer (agent, when: standard|deep)
        ├── Step: behavior-observer (agent, when: deep)
        └── Step: integration-mapper (agent, when: standard|deep)
        All dispatched with context_depth="none" for independence

Stage 3: "synthesize" (approval required)
├── Step: reconcile (foreach over modules)
│   └── Sub-recipe: recipes/discovery-synthesize-module.yaml
│       ├── Step: synthesize (agent — discovery-synthesizer)
│       ├── Step: validate (bash — dot_graph validate)
│       └── While: validation fails, max 3 iterations
├── Step: assemble (bash — dot_graph operation="assemble")
└── Step: final-validate (bash — validate + analyze on all outputs)
```

### Sub-Recipes

**`recipes/discovery-investigate-topic.yaml`** — Per-topic investigation. Dispatches 1-3 agents depending on fidelity tier. Each agent gets fresh context and writes to `modules/<name>/agents/<agent>/`.

**`recipes/discovery-synthesize-module.yaml`** — Per-module reconciliation. Runs the synthesizer agent, validates the output, and loops up to 3 times if validation fails (quality gate).

### Recipe Design Decisions

- **Two sub-recipes** keep the outer recipe clean. The outer recipe handles stage sequencing and approval gates. Sub-recipes handle per-topic and per-module work.
- **Approval gate after topic selection** — before spending tokens on multi-agent investigation, the user reviews and can adjust the topic list. This is cheap to show, expensive to skip.
- **No approval gate between investigate and synthesize** — once the user approves investigation, synthesis follows naturally. The quality gate loop handles self-correction without human intervention.
- **Fidelity is a recipe context variable** — `{{fidelity}}` set by change detection or user override. The recipe uses `when:` conditionals to skip steps at lower fidelity tiers.

## Error Handling

### Quality Gate Loop

The synthesis stage uses a validate-and-retry loop:

1. Synthesizer agent produces `diagram.dot`
2. `dot_graph validate` checks syntax, structure, and (at deep fidelity) graph intelligence
3. If validation fails, the synthesizer receives the error report and regenerates
4. Maximum 3 iterations — after that, the best attempt is kept with a warning in `discrepancies.md`

### Change Detection Failures

If `.discovery/last-run.json` is missing or corrupted, change detection falls back to treating the entire repo as changed — equivalent to a fresh run at whatever fidelity tier is configured.

### Agent Failures

If an investigation agent fails (timeout, context overflow, tool errors):

- The recipe continues with remaining agents for that topic
- The synthesizer works with whatever outputs are available
- Missing agent perspectives are noted in `discrepancies.md`

At `standard` fidelity, losing one of two agents still produces useful output. At `deep` fidelity, losing one of three still has two-agent consensus.

### Assembly Failures

If assembly fails (malformed module DOT, pydot errors), the tool reports which specific module DOT caused the issue. The recipe can re-run synthesis for just that module.

## Testing Strategy

### Tool Operations

- **Prescan:** Unit tests with fixture repos (Python package, Rust crate, monorepo, empty repo). Assert correct language detection, module boundary identification, and file counting.
- **Assemble:** Unit tests with fixture DOT files. Assert correct subgraph wrapping, edge routing between clusters, overview bounds (≤250 lines, ≤80 nodes), and ancestor invalidation logic.

### Agent Definitions

- Validate agent YAML schema (required fields, correct `@mention` paths)
- Verify context files exist and are referenced correctly
- Smoke test each agent against a small fixture repo to confirm it produces valid DOT output

### Recipe Integration

- Validate recipe YAML structure (`recipes validate`)
- End-to-end test: run the full pipeline against a known fixture repo and assert the `.discovery/` directory structure matches expected output
- Test each fidelity tier to verify correct agent dispatch (quick skips investigation, standard dispatches 2, deep dispatches 3)
- Test approval gates pause at the right points
- Test quality gate loop by providing intentionally invalid DOT to verify retry behavior

### Regression

- Store golden `.discovery/` output for fixture repos
- Compare pipeline output against golden files to catch regressions in agent prompts, tool logic, or recipe flow

## Design Decisions

All resolved during brainstorming:

| # | Decision | Resolution |
|---|----------|-----------|
| 1 | Scope | Single-repo first, designed for multi-repo extension |
| 2 | Output model | Per-module DOT + assembled overview — build up from atomic level |
| 3 | Pipeline trigger | Manual/on-demand first, incremental with change detection later |
| 4 | Invalidation | Changes cascade upward through the hierarchy — module → subsystem → overview |
| 5 | Investigation approach | Hybrid static + LLM with multi-agent consensus |
| 6 | Fidelity tiers | quick (single-agent/patch), standard (2-3 agents/consensus), deep (full triplicate/adversarial); default is standard |
| 7 | Bundle location | Inside dot-graph with separate behaviors — `dot-core` / `dot-discovery` / `dot-graph` |
| 8 | `.discovery/` location | Inside the target repo being analyzed |
| 9 | Manifest granularity | Module/directory level (file-level globs as future enhancement) |
| 10 | Module boundary detection | Directory structure + language-specific heuristics; user config override deferred to post-v1 |
| 11 | Monorepo handling | Prescan auto-detects; no configuration needed for common cases |
| 12 | Agent dispatch budget | quick=0-1, standard=10-15, deep=25-30; shown in approval gate |

## Prior Art Reused

### From dot-docs project

- Tier system (-1/0/1/2/3) for incremental refresh — adapted for the change detection step
- Synthesis prompt methodology (4-phase reconciliation) — adapted for `discovery-synthesizer` agent
- Quality gate loop (synthesize → review → fix, max 3) — used in synthesis sub-recipe
- `discovery_metadata.py` — clean dataclass-based JSON persistence pattern for `.discovery/` directories
- `dot_validation.py` — already adapted into the bundle's tool module

### From the dot-graph bundle (already shipped)

- `dot_graph validate` — three-layer validation (syntax, structural, render-quality)
- `dot_graph analyze` — 8 NetworkX operations (reachability, cycles, unreachable nodes, etc.)
- `dot_graph render` — graphviz CLI wrapper for SVG/PNG/PDF output
- `dot-as-analysis` skill — reconciliation methodology
- `dot-quality` skill — quality standards for DOT diagrams
