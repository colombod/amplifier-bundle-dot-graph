# DOT/Graphviz Session Index

> **Generated:** 2026-03-13 by session-analyst
> **Search scope:** All Amplifier sessions March 1–13, 2026 (~6,240 sessions scanned)
> **Keywords:** graphviz, digraph, subgraph, rankdir, .dot, DOT language/syntax/format/file/diagram, graph visualization
> **Strong matches (graphviz|digraph|subgraph|rankdir):** 696 sessions
> **Context matches (.dot files, graph visualization):** 1,424 unique sessions total
> **Root (user-initiated) sessions with matches in date range:** 38

---

## How to Read This Index

Each entry is classified by **DOT relevance tier**:

| Tier | Meaning |
|------|---------|
| **TIER 1: Core DOT** | Session is *about* DOT — creating DOT files, designing DOT tooling, DOT as primary subject |
| **TIER 2: DOT as Pipeline DSL** | Session uses DOT as the Attractor pipeline definition format — authoring/debugging `.dot` pipeline files |
| **TIER 3: DOT Output/Artifact** | Session produces DOT diagrams as investigation/documentation artifacts (e.g., Parallax Discovery output) |
| **TIER 4: Embedded DOT** | DOT syntax appears embedded in skill/mode documentation (e.g., process flow diagrams in brainstormer skill) |
| **TIER 5: Incidental** | The word ".dot" appears in file listings or code but DOT language is not the subject |

---

## TIER 1: Core DOT Sessions (DOT as Primary Subject)

### 1. `a31d8d0c` — dot-graph-bundle Bootstrap *(current session's parent)*
- **Date:** 2026-03-13T19:04
- **Project:** `/home/bkrabach/dev/dot-graph-bundle`
- **Model:** claude-opus-4-6 | **Turns:** 1+ (in progress)
- **DOT Relevance:** TIER 1 — Core DOT
- **Reference Type:** Conceptual design + orchestration

**Summary:** The session that spawned this index. User initiated a multi-agent investigation to bootstrap the `dot-graph-bundle` Amplifier bundle — a dedicated DOT/Graphviz capability bundle for the ecosystem. Dispatched session-analyst (this search), foundation-expert (bundle guidance), and explorer (workspace survey) in parallel.

**Key DOT Topics:**
- Bundle design for DOT/Graphviz capabilities across Amplifier
- DOT authoring, validation, rendering as agent tools
- DOT as an output format from investigations
- Bundle structure patterns for DOT knowledge

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-dot-graph-bundle/sessions/a31d8d0c-a01c-4bb8-8c3d-f72db174bf61/`

---

### 2. `71295782` — Dotfiles Discovery Design Document
- **Date:** 2026-03-12T22:04
- **Project:** `/home/bkrabach/dev/dot-docs`
- **Model:** claude-opus-4-6 | **Turns:** 23
- **DOT Relevance:** TIER 1 — Core DOT
- **Reference Type:** Design + practical generation + investigation evidence

**Summary:** Comprehensive design session for a per-person DOT file generation system within the Team Knowledge Base. The user (Brian) defined a vision for a `/dotfiles/<github-handle>/<repo-name>/` directory structure where each repo gets DOT representations across four perspectives: architecture, sequence, state-machine, and integration.

**Key DOT Topics:**
- **Directory structure:** `overview.dot` (mandatory, 150-250 lines), `architecture.dot`, `sequence.dot`, `state-machines.dot`, `integration.dot` per repo
- **DOT quality standards:** Shape-as-type vocabulary (box=module, ellipse=process, component=orchestrator, hexagon=hook, diamond=decision, cylinder=state store), multi-style edges (solid=declared, dashed=runtime, dotted=coordinator-mediated, bold=critical path), legend subgraphs
- **Progressive disclosure:** Top-level overview.dot is compact/renderable, detail files expand with extensive edge labels and cross-boundary annotations
- **Tiered discovery pipeline:** Full Parallax (Tier 1) → Single-wave refresh (Tier 2) → Targeted update (Tier 3) → Skip
- **Evidence from experiments:** Ran Parallax Discovery against `microsoft/amplifier-bundle-attractor` — synthesized architecture diagram (252 lines, 15KB) was qualitatively superior to any single-agent output; state-machine diagram at 158 lines identified as the "gem" for compactness
- **Anti-patterns documented:** Node labels with multi-line inline docs, >80 nodes per graph, splines=ortho with high node counts
- **Testing strategy:** `dot -Tsvg` validation, line count gates, render tests (non-zero bounding box), fixture-based regression tests

**Specific DOT Content Discussed:**
- Shape vocabulary: `box`, `ellipse`, `component`, `hexagon`, `diamond`, `cylinder`, `note`, `box3d`
- Edge styles: solid, dashed, dotted, bold with semantic meanings
- Red nodes/edges for confirmed bugs
- Cluster subgraphs for logical groupings

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-dot-docs/sessions/71295782-20c0-4905-a737-2ed63a30aa3f/`

---

### 3. `1fe54592` — Superpowers Test: DOT Repo Analysis Tool
- **Date:** 2026-03-12T00:15
- **Project:** `/home/bkrabach/dev/superpowers-test`
- **Model:** claude-opus-4-6 | **Turns:** 5
- **DOT Relevance:** TIER 1 — Core DOT
- **Reference Type:** Conceptual design + practical investigation of existing DOT patterns

**Summary:** User initiated brainstorming for a tool that takes a given repo, does a deep-dive analysis, and produces GraphViz DOT file representations of the system(s) within. Goal: point an LLM at the top-level DOT file to get rich project understanding, with subsystem subgraph files loaded JIT based on interest.

**Key DOT Topics:**
- **DOT as LLM-readable architecture format** — the core concept that DOT files are both human-renderable AND agent-scannable
- **Progressive DOT disclosure** — top-level overview DOT → subsystem subgraph DOT files loaded on demand
- **Studied existing DOT files** from `amplifier-resolve` and `amplifier-resolver-*` repos to understand existing patterns
- Examined `consensus_task.dot` and `semport.dot` as reference examples

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-superpowers-test/sessions/1fe54592-e4e5-4b36-9366-efc2789f6a6d/`

---

### 4. `bc1547a8` — Recipe Testing: GraphViz DOT of Amplifier Recipe
- **Date:** 2026-03-13T13:53
- **Project:** `/home/bkrabach/dev/recipe-testing`
- **Model:** claude-opus-4-6 | **Turns:** 10
- **DOT Relevance:** TIER 1 — Core DOT
- **Reference Type:** Practical generation — creating DOT from non-DOT source

**Summary:** User asked the agent to create a GraphViz DOT representation of the bundle validation recipe from amplifier-foundation. This is DOT as a *visualization output format* for understanding YAML recipe structures.

**Key DOT Topics:**
- Converting YAML recipe definitions into GraphViz DOT diagrams
- DOT as a visualization tool for understanding complex multi-step workflows
- Recipe step dependencies rendered as directed graph edges

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-recipe-testing/sessions/bc1547a8-7cf6-4f4a-ae75-cfd6bd1117e4/`

---

### 5. `588e215d` — Attractor Dev Machine: Testing DOT Files
- **Date:** 2026-03-12T19:44
- **Project:** `/home/bkrabach/dev/attractor-dev-machine`
- **Model:** claude-opus-4-6 | **Turns:** 3
- **DOT Relevance:** TIER 1 — Core DOT
- **Reference Type:** Practical testing — running DOT pipeline files

**Summary:** User asked "do you have an attractor dot file we can test?" — exploring the DOT pipeline files available in the attractor bundle. Explorer agent found **54 DOT files** across the workspace.

**Key DOT Topics:**
- **54 DOT files cataloged** across examples/pipelines (10 tutorial + 5 practical + 5 patterns), test fixtures (12 unit + 7 integration + 4 E2E), and 13 investigation diagrams
- Tutorial ladder from `01-simple-linear.dot` to `10-full-attractor.dot`
- Practical templates: `pr-review.dot`, `feature-build.dot`, `bug-fix.dot`, `refactor.dot`, `test-gen.dot`
- Pattern pipelines: `conversational-gate.dot`, `convergence-factory.dot`
- Complex real-world pipelines: `semport.dot` (7-node semantic porting), `consensus_task.dot` (18-node multi-LLM consensus)

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-attractor-dev-machine/sessions/588e215d-15c0-42d8-9c2c-6ac63cf584c6/`

---

## TIER 2: DOT as Pipeline DSL

### 6. `4e7e1d72` — Attractor Dev Machine: Full Parallax Discovery (279 DOT matches)
- **Date:** 2026-03-10T20:01
- **Project:** `/home/bkrabach/dev/attractor-dev-machine`
- **Model:** claude-opus-4-6 | **Turns:** 73
- **DOT Relevance:** TIER 2 — DOT as Pipeline DSL + TIER 3 — DOT Output
- **Reference Type:** Design pattern + practical usage + DOT-as-investigation-output

**Summary:** Major session running full Parallax Discovery against the attractor bundle. The attractor system uses **Graphviz DOT digraphs as its pipeline definition format** — this is the defining characteristic of the attractor engine. Session produced extensive DOT investigation diagrams AND discussed the DOT DSL design extensively.

**Key DOT Topics:**
- **DOT as pipeline DSL:** "Attractor lets pipeline authors express workflows as Graphviz DOT digraphs. Each node is an AI task (or control node), edges define flow."
- **Constrained DOT subset:** One digraph per file, strict shape-to-handler mapping, node attributes for LLM configuration
- **Shape semantics in DOT DSL:** `box`=codergen handler, `diamond`=conditional routing, `component`=fan-out, `tripleoctagon`=fan-in, `hexagon`=human gate, `house`=manager, `folder`=child pipeline
- **Model stylesheet in DOT:** CSS-like selectors (`*`, `.class`, `#id`) for assigning LLM models
- **54 DOT files** across examples, tests, patterns
- **13 investigation DOT diagrams** produced by Parallax agents analyzing the system architecture

**Specific DOT DSL Features Discussed:**
- `llm_prompt`, `llm_provider`, `goal_gate`, `max_turns`, `steer_prompt` node attributes
- `condition`, `weight`, `loop_restart`, `fidelity` edge attributes
- `model_stylesheet` graph-level attribute
- Pipeline composition via `shape=folder` (child pipeline invocation)

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-attractor-dev-machine/sessions/4e7e1d72-41b3-419e-b0d0-f008f78dcec5/`

---

### 7. `b174ff67` — Resolve Stabilize: DotGraphResolver Integration (251 DOT matches)
- **Date:** 2026-03-03T17:38
- **Project:** `/home/bkrabach/dev/resolve-stabilize`
- **Model:** claude-opus-4-6 | **Turns:** 239
- **DOT Relevance:** TIER 2 — DOT as Pipeline DSL
- **Reference Type:** Practical implementation — building DOT pipeline execution engine

**Summary:** Massive 239-turn session building `amplifier-resolve` — a system that takes briefs and produces GitHub PRs using DOT-defined pipelines. The `DotGraphResolver` is the active default resolver, loading `.dot` files and executing them through the attractor pipeline engine.

**Key DOT Topics:**
- **`DotGraphResolver`** — production-default resolver that loads DOT graph pipeline files, parses into graph, executes via `PipelineEngine`
- **Built-in pipelines:** `resolve_quick.dot` (8 nodes, single-model linear) and `resolve_consensus.dot` (15 nodes, multi-model fan-out/fan-in)
- **`ResolveConfig.pipeline`** field: `"quick"`, `"consensus"`, or custom path to `.dot` file
- **DOT context variables:** `$task`, `$goal`, `$brief_id`, `$test_command`, `$state_dir` expanded in `llm_prompt` attributes
- **User-provided DOT files** — shifted from generating DOT strings to loading DOT from disk, supporting custom pipelines
- **Cross-team integration pain points:** `llm_prompt` vs `prompt` confusion in DOT attributes, `shape="diamond"` silently mapping to wrong handler, custom outcome conditions not matching
- **Dashboard DOT rendering:** `graph.dot` files generated for visualization, `ts-graphviz` parsing issues in React frontend
- **Reference DOT files:** `consensus_task.dot` and `semport.dot` from `~/dev/`

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-resolve-stabilize/sessions/b174ff67-755d-43c3-a2b3-fe6acb4e7eb0/`

---

### 8. `b6381c4b` — Task Builder v1: Resolve Architecture Deep Dive (47 DOT matches)
- **Date:** 2026-03-03T17:37
- **Project:** `/home/bkrabach/dev/task-builder-v1`
- **Model:** claude-opus-4-6 | **Turns:** 36
- **DOT Relevance:** TIER 2 — DOT as Pipeline DSL
- **Reference Type:** Architecture documentation + practical debugging

**Summary:** Deep exploration of the Amplifier Resolve architecture, including the DOT pipeline system. Session analyst dispatched to create comprehensive documentation covering the Resolver Protocol, DotGraphResolver, pipeline DOT files, and demo setup.

**Key DOT Topics:**
- **Pipeline DOT files** in `src/amplifier_resolve/core/pipelines/` — the main DOT pipeline definitions
- **Hardening Deliver/Test node prompts** in DOT files as a key action item
- **DOT pipeline architecture:** `resolve_quick.dot` (8 nodes) and `resolve_consensus.dot` (15 nodes, multi-model)
- **Pipeline system documentation** covering DOT-based resolver workflow

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-task-builder-v1/sessions/b6381c4b-9672-42e5-a8ad-94e09d20e8c3/`

---

### 9. `2d7eecf6` — Task Builder v1: Resolve Comprehensive Doc (68 DOT matches)
- **Date:** 2026-03-03T14:50
- **Project:** `/home/bkrabach/dev/task-builder-v1`
- **Model:** claude-opus-4-6 | **Turns:** 11
- **DOT Relevance:** TIER 2 — DOT as Pipeline DSL
- **Reference Type:** Documentation — comprehensive architecture doc

**Summary:** Created exhaustive documentation of the Amplifier Resolve project including the pipeline system. Covers `DotGraphResolver` as the active default, DOT graph pipelines via the attractor engine, and Docker container execution.

**Key DOT Topics:**
- Complete documentation of the DOT-based pipeline architecture
- `DotGraphResolver` as production default resolver
- Attractor pipeline engine as the DOT execution runtime

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-task-builder-v1/sessions/2d7eecf6-a7e5-4f9b-b27f-cbaeb6a9e35b/`

---

### 10. Resolve-Stabilize Continuation Sessions (8 sessions)

Multiple shorter sessions continuing the resolve-stabilize work, each touching DOT pipeline infrastructure:

| Session ID | Date | Turns | DOT Matches | Key DOT Activity |
|-----------|------|-------|-------------|-----------------|
| `08ded5a9` | 2026-03-04T17:03 | 3 | 22 | Exploring attractor bundle pipeline plans and DOT pipeline event specs |
| `e19aa7ed` | 2026-03-05T15:27 | 4 | 23 | Wiring `BriefCreate.resolver` through the DOT pipeline; default → "dot-graph" |
| `b0b4744f` | 2026-03-05T10:38 | 6 | 15 | `dot_graph.py` as production default; legacy five-phase fallback |
| `40f77743` | 2026-03-05T06:21 | 4 | 11 | `resolver: str = "dot-graph"`, `pipeline: str = "quick"` in ResolveConfig |
| `ff0d3265` | 2026-03-05T01:54 | 3 | 11 | DOT pipeline changes, `create-pr` script replacements |
| `222e7626` | 2026-03-04T19:17 | 4 | 5 | Reading plan/design documents for resolve pipeline implementation |
| `8d363f1a` | 2026-03-06T18:23 | 3 | 5 | Resolver pipeline execution, CWD inheritance for pipeline nodes |
| `b2e55739` | 2026-03-07T02:16 | 7 | 6 | Comic pipeline investigation (different pipeline, not DOT-focused) |

**Project:** `/home/bkrabach/dev/resolve-stabilize`
**Session Base Path:** `~/.amplifier/projects/-home-bkrabach-dev-resolve-stabilize/sessions/`

---

## TIER 2.5: DOT Pipeline + Change Proposals

### 11. `c95ce204` — Change Proposal: Event System DOT Specifications (20 DOT matches)
- **Date:** 2026-03-05T00:18
- **Project:** `/home/bkrabach/dev/change-proposal`
- **Model:** claude-opus-4-6 | **Turns:** 47
- **DOT Relevance:** TIER 2 — DOT as specification format
- **Reference Type:** Practical creation — DOT files as event flow specifications

**Summary:** Created a comprehensive set of DOT files documenting the Amplifier event system. Produced **13+ numbered DOT diagram files** as formal specifications.

**Key DOT Topics:**
- **DOT files created as event specifications:**
  - `02-session-state-machine.dot` — session lifecycle states
  - `03-single-turn-event-flow.dot` — single turn event sequence
  - `04-child-session-complete-lifecycle.dot` — child session lifecycle
  - `05-orchestrator-variants.dot` — different orchestrator event sets
  - `06-recipe-session-tree.dot` — recipe session hierarchy
  - `08-empirical-delegation-tree.dot` — delegation patterns
  - `09-hook-dispatch-flow.dot` — hook dispatch sequence
  - `10-provider-vs-llm-events.dot` — provider/LLM event comparison
  - `11-parallel-agent-mechanism.dot` — parallel agent coordination
  - `13-navigation-graph-model.dot` — navigation graph structure
  - `14-session-instance-55c8841a.dot` — specific session instance diagram
  - `15-query-parallel-tool-batches.dot` — parallel tool batch queries
- **Proposed convention:** Modules that emit custom events should ship an `events.dot` file at the module root
- **Verified:** Zero `.dot` files existed in `amplifier-foundation` before this session — this was greenfield DOT specification work
- **Key insight:** DOT diagrams revealed a cancellation gap (G2) that was "invisible because no diagram showed all exit paths"

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-change-proposal/sessions/c95ce204-1c62-4068-9c22-77aa2dda0bd0/`

---

### 12. `8ca877b9` — Change Proposal: Follow-up DOT Specification Work
- **Date:** 2026-03-05T14:17
- **Project:** `/home/bkrabach/dev/change-proposal`
- **Model:** claude-opus-4-6 | **Turns:** 6
- **DOT Relevance:** TIER 2 — DOT as specification format
- **Reference Type:** Practical creation continuation

**Summary:** Follow-up session referencing the DOT event specifications. Noted that zero `.dot` files existed in amplifier-foundation, proposed creating `modules/tool-delegate/events.dot` and DOT template docs.

**Key DOT Topics:**
- Proposed `events.dot` convention for module-level event flow specifications
- DOT template documentation for the foundation bundle

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-change-proposal/sessions/8ca877b9-6fcf-4f3f-8087-45374f0d1ec4/`

---

## TIER 3: DOT as Investigation Output (Parallax Discovery)

### 13. `9ed2c49f` — Superpowers 3: Parallax Discovery Methodology (56 DOT matches)
- **Date:** 2026-03-10T19:47
- **Project:** `/home/bkrabach/dev/superpowers-3`
- **Model:** claude-opus-4-6 | **Turns:** 65
- **DOT Relevance:** TIER 3 — DOT as investigation artifact
- **Reference Type:** Methodology design — DOT as standard output format

**Summary:** Designing the Parallax Discovery methodology. DOT diagrams are a *standard output artifact* of every investigation — each agent produces `diagram.dot` alongside `findings.md`, `evidence.md`, and `unknowns.md`.

**Key DOT Topics:**
- **DOT as discovery tool:** "DOT diagrams are discovery tools, not just documentation"
- **Standard investigation output:** Every Parallax agent produces `diagram.dot` as part of their deliverables
- **Agent output specs:**
  - Code Tracer → `findings.md`, `evidence.md`, `diagram.dot`, `unknowns.md`
  - Behavior Observer → `findings.md`, `catalog.md`, `patterns.md`, `diagram.dot`, `unknowns.md`
  - Integration Mapper → `integration-map.md`, `diagram.dot`, `unknowns.md`

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-superpowers-3/sessions/9ed2c49f-638a-4346-bf66-1a9bb135a328/`

---

### 14. `eb589d37` — Parallax Demo (25 DOT matches)
- **Date:** 2026-03-09T18:33
- **Project:** `/home/bkrabach/dev/parallax-demo`
- **Model:** claude-opus-4-6 | **Turns:** 2
- **DOT Relevance:** TIER 3 — DOT as investigation artifact
- **Reference Type:** Methodology documentation

**Summary:** Short session referencing the Parallax Discovery methodology with DOT diagrams as standard investigation output. Same agent output specification pattern as session `9ed2c49f`.

**Session Path:** `~/.amplifier/projects/-home-bkrabach-dev-parallax-demo/sessions/eb589d37-a7a8-485a-820d-98445f57d3ad/`

---

## TIER 4: Embedded DOT in Skills/Documentation

### 15. Sessions with Brainstormer/Superpowers Skill DOT Diagrams

Multiple sessions contain DOT syntax embedded in the brainstormer skill documentation — process flow diagrams rendered as `digraph brainstorming {...}` and `digraph when_to_use {...}` and `digraph process {...}`. These are DOT used *within* Amplifier skill files to visualize agent workflow processes.

| Session ID | Date | Project | Turns | Context |
|-----------|------|---------|-------|---------|
| `71b67e02` | 2026-03-06 | tui | 119 | Brainstormer process flow DOT in skill docs |
| `df4315c0` | 2026-03-06 | gpt-5-4 | 35 | Brainstormer + superpowers when_to_use DOT |
| `62713d0a` | 2026-03-09 | rust-devrust-core | 87 | Brainstormer process flow DOT (4 occurrences) |
| `40a2ec44` | 2026-03-04 | rust-devrust-core | 115 | Brainstormer process flow DOT (4 occurrences) |
| `4f63147f` | 2026-03-03 | ghcp-improve | 43 | Brainstormer + superpowers DOT diagrams (3 skill loads) |
| `3a263cf5` | 2026-03-07 | dev-machine-amplifier-tui | 61 | Brainstormer process flow DOT |
| `f3de3a7c` | 2026-03-05 | init-scope | 109 | Brainstormer process flow DOT (3 occurrences) |
| `320261ba` | 2026-03-05 | browser-content-sync | 50 | Brainstormer process flow DOT |
| `43a209e6` | 2026-03-10 | voice-update | 31 | Brainstormer process flow DOT |
| `a5dc1a5e` | 2026-03-10 | python-dev-prereqs | 20 | Brainstormer process flow DOT |
| `18595cbb` | 2026-03-01 | rust-devrust-core | 42 | Brainstormer process flow DOT |
| `5159fd15` | 2026-03-02 | rust-devrust-core | 60 | Brainstormer process flow DOT |
| `ab8d835c` | 2026-03-03 | rust-devrust-core | 22 | Brainstormer process flow DOT |
| `e96e75ce` | 2026-03-03 | ghcp-improve | 30 | Brainstormer process flow DOT |

**DOT Content Pattern (repeated across all):**
```dot
digraph brainstorming {
    "Explore project context" [shape=box];
    "Ask clarifying questions" [shape=diamond];
    ...
}

digraph when_to_use {
    "Have implementation plan?" [shape=diamond];
    ...
}

digraph process {
    rankdir=TB;
    subgraph cluster_per_task { ... }
    ...
}
```

**Significance:** This demonstrates DOT is already embedded in the Amplifier skill ecosystem as a documentation/visualization format. The brainstormer and superpowers skills use DOT to define their own process flows, making DOT a natural fit for the ecosystem.

---

## TIER 5: Incidental/Contextual DOT References

### 16. `1a26bdf9` — Superpowers Dev 1: DOT File Discovery
- **Date:** 2026-03-05T01:45
- **Project:** `/home/bkrabach/dev/superpowers-dev-1`
- **Model:** qwen3-coder-next | **Turns:** 11
- **DOT Relevance:** TIER 5 — Incidental
- **Reference Type:** File listing — `consensus_task.dot` and `semport.dot` visible in directory listing

**Summary:** DOT files (`consensus_task.dot`, `semport.dot`) appeared in directory listings of `~/dev/`. These are the reference pipeline DOT files used across multiple other sessions.

---

### 17. Other Incidental Sessions

Sessions with low DOT match counts (1-4) where DOT appears only in:
- File listings showing `.dot` extensions
- Brainstormer skill embedded diagrams (single occurrence)
- Pipeline infrastructure references without substantive DOT discussion

| Session ID | Date | Project | Matches | Context |
|-----------|------|---------|---------|---------|
| `870faf60` | 2026-03-01 | model-class-routing | 0 | False positive — matched via graph visualization terms only |
| `79e5acdd` | 2026-03-01 | model-class-routing | 0 | False positive — matched via graph visualization terms only |
| `1372e916` | 2026-03-05 | superpowers-dev-2 | 3 | Git log mention of brainstorming pipeline DOT |
| `667a06f5` | 2026-03-04 | modes-adherence | 4 | Pipeline/recipe references, not DOT-specific |
| `cdddf2b6` | 2026-03-03 | task-builder-v1 | 4 | Consensus pipeline test mention, Phase 2 shadow instance |

---

## Cross-Session Analysis: DOT Usage Patterns

### Pattern 1: DOT as Pipeline Definition Language (Attractor)
**Sessions:** `4e7e1d72`, `b174ff67`, `b6381c4b`, `2d7eecf6`, `588e215d`, `08ded5a9`, `e19aa7ed`, `b0b4744f`, `40f77743`, `ff0d3265`

The Attractor pipeline engine uses Graphviz DOT as its **native pipeline definition format**. This is the most mature and extensive use of DOT in the ecosystem. Key characteristics:
- Each `.dot` file defines a complete AI workflow as a directed graph
- Nodes map to LLM agent tasks via shape-to-handler mapping
- Edges define flow control, conditional routing, loops, and fan-out/fan-in
- Node attributes configure LLM behavior (`llm_prompt`, `llm_provider`, `goal_gate`, `max_turns`)
- `model_stylesheet` enables CSS-like multi-provider routing
- **54 DOT pipeline files** exist in the attractor bundle alone

### Pattern 2: DOT as Architecture Documentation (Parallax Discovery)
**Sessions:** `9ed2c49f`, `eb589d37`, `4e7e1d72`, `71295782`

Every Parallax Discovery investigation produces `diagram.dot` files as standard output. These are architecture/integration/state-machine diagrams, not pipeline definitions. The Parallax methodology treats DOT as a **discovery tool** — agents use DOT creation as a forcing function for precise understanding.

### Pattern 3: DOT as Event/System Specification
**Sessions:** `c95ce204`, `8ca877b9`

DOT files created as formal specifications for the Amplifier event system. 13+ numbered DOT files documenting session state machines, event flows, orchestrator variants, delegation trees, and navigation models. Proposed convention: every module ships an `events.dot` file.

### Pattern 4: DOT as Skill/Process Visualization
**Sessions:** 14+ sessions with embedded brainstormer/superpowers DOT

DOT syntax embedded in Amplifier skill files to visualize agent workflow processes. The brainstormer skill contains `digraph brainstorming`, `digraph when_to_use`, and `digraph process` diagrams that appear in every session loading those skills.

### Pattern 5: DOT as LLM-Readable Architecture Format (Dotfiles Vision)
**Sessions:** `71295782`, `1fe54592`

The emerging vision: DOT as a **dual-purpose format** — simultaneously renderable for human viewing AND parseable for LLM consumption. The dotfiles design explicitly targets "agent-scannable" DOT files with concise node labels, structured subgraphs, and progressive disclosure.

---

## Summary Statistics

| Category | Count |
|----------|-------|
| Total sessions scanned (March 1-13) | ~6,240 |
| Sessions with any DOT/Graphviz keyword match | 1,424 |
| Root (user-initiated) sessions with matches | 38 |
| **TIER 1: Core DOT** sessions | 5 |
| **TIER 2: DOT as Pipeline DSL** sessions | 12 |
| **TIER 3: DOT as Investigation Output** sessions | 2 |
| **TIER 4: Embedded DOT in Skills** sessions | 14+ |
| **TIER 5: Incidental** sessions | 5+ |
| Unique projects with DOT activity | 15 |
| DOT files in attractor bundle | 54 |
| DOT specification files created (change-proposal) | 13+ |

---

## Key Reference DOT Files (on disk)

These are the DOT files that appear most frequently across sessions:

| File | Location | Description |
|------|----------|-------------|
| `consensus_task.dot` | `~/dev/consensus_task.dot` | 18-node multi-LLM consensus pipeline (7,365 bytes) |
| `semport.dot` | `~/dev/semport.dot` | 7-node semantic porting loop pipeline (10,355 bytes) |
| `resolve_quick.dot` | `amplifier-resolve/core/pipelines/` | 8-node single-model linear resolver pipeline |
| `resolve_consensus.dot` | `amplifier-resolve/core/pipelines/` | 15-node multi-model fan-out resolver pipeline |
| `01-simple-linear.dot` → `10-full-attractor.dot` | `amplifier-bundle-attractor/examples/pipelines/` | 10 tutorial pipeline examples |
| `pr-review.dot`, `feature-build.dot`, etc. | `amplifier-bundle-attractor/examples/pipelines/practical/` | 5 real-world pipeline templates |
| `02-session-state-machine.dot` → `15-*.dot` | `change-proposal` workspace | 13+ event system specification DOTs |
