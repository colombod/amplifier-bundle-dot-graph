# DOT-Docs Session Mining: Comprehensive Findings

> **Mined:** 2026-03-13
> **Source:** ~160 sessions in `~/.amplifier/projects/-home-bkrabach-dev-dot-docs/sessions/` plus ~14 sessions in `~/.amplifier/projects/-home-bkrabach-dev-dot-graph-bundle/sessions/`
> **Primary session:** `71295782-20c0-4905-a737-2ed63a30aa3f` (23 turns, the core design+implementation session)
> **Supporting sessions:** brainstormer, zen-architect, plan-writer, 50+ parallax-discovery agent sessions, and the dot-graph-bundle bootstrap session

---

## Executive Summary

The dot-docs project workspace produced a remarkably complete body of evidence across a single intensive session (Mar 12–13, 2026) that ran the full cycle from research through design through implementation (247 passing tests). The session empirically validated DOT as far more than a diagramming format — it functions as a **bug discovery mechanism**, a **reconciliation forcing function**, a **multi-scale navigation system**, and a **context compression format** for agent consumption. The most surprising finding: building DOT representations of real codebases surfaced **7 confirmed bugs** that LSP, compilers, type checkers, and unit tests had all missed.

---

## 1. DOT as a Bug/Gap Discovery Mechanism

### The Core Finding

Building DOT graph representations of the `microsoft/amplifier-bundle-attractor` codebase (11 Python packages, ~19K LOC) surfaced bugs that **no other tool caught**. This was not a theoretical exercise — the Parallax Discovery investigation ran 18+ agent invocations across 3 waves and produced execution-based evidence for every confirmed bug.

### Bugs Discovered Through DOT Representation

| Bug ID | Description | How DOT Surfaced It | Why Other Tools Missed It |
|--------|-------------|---------------------|---------------------------|
| **D-01** | Token metrics always zero — schema mismatch between nested producer keys (`usage.input_tokens`) and flat consumer keys (`tokens_in`) | Integration mappers drawing cross-boundary data flows were forced to trace the actual key names across producer→consumer edges. The DOT diagram made the mismatch visually obvious. | Unit tests used manually-crafted inputs that didn't match real upstream output. Tests passed because they tested the wrong schema. |
| **D-03** | Truncation hook bypass — `_build_unified_tools()` never calls `wrap_tool_with_hooks()`, silently bypassing all tool-level hooks in the pipeline path | Drawing the execution flow DOT required tracing which functions actually call which. The DOT diagram showed `wrap_tool_with_hooks()` as an **isolated node** — connected to nothing. | The function existed, was tested, and had full coverage. But it was **dead production code** — never called by any real code path. Tests created an illusion of coverage for a feature that doesn't exist. |
| **D-04** | Backend/engine state divergence — `AmplifierBackend._completed_nodes` diverges from `PipelineEngine.node_outcomes` under specific conditions | Drawing the state machine DOT required committing to which component owns which state. Two agents independently drew contradictory ownership diagrams, which the reconciliation process flagged. | The divergence only manifests with `auto_status=true` (unquoted) on failing nodes — an obscure edge case. Static analysis can't detect runtime state divergence. |
| **D-05** | `preferred_label` shadowing — latent hazard in routing labels | Drawing routing decision diamonds forced the agent to enumerate all edge conditions. The shadowing was visible in the graph. | Intentional design, but undocumented. No current pipelines affected, but a latent hazard. |
| **Bonus** | `auto_status` parsing bug — `auto_status="true"` (quoted, the natural DOT style) stores Python string `'true'` and the `is True` check never fires. Only unquoted `auto_status=true` activates the feature. | Discovered during adversarial execution testing of D-04. The DOT parser's type coercion was a cross-cutting concern visible only when testing the graph end-to-end. | Python's `is True` vs truthy check is invisible to type checkers. The DOT parser silently converts between string and bool representations. |
| **CI-07** | Test isolation is systemic — D-01, D-04, and D-05 all independently discovered unit tests using manually-crafted inputs that don't match real upstream output | Cross-cutting insight that only emerged from looking at all three bugs together in the reconciliation DOT. | Each test file looked correct in isolation. The pattern was only visible across multiple components. |
| **CI-08** | Observability is doubly compromised — token metrics always zero (D-01) + tool events never emitted (D-03) = the only accurate pipeline metric is `total_llm_calls` | The integration DOT diagram showed both observability paths terminating in dead ends. | Each observability subsystem appeared functional when tested alone. |

### Why DOT Catches What Other Tools Don't

The key insight from the lead investigator reconciliation sessions:

> *"Adversarial testing corrects mechanisms without overturning conclusions — All three challenges show the same pattern: the 'what' survives but the 'how' needs correction. This validates the methodology."*

DOT catches bugs at **integration seams** — the boundaries between components where:
- LSP operates within single files/modules and can't see cross-boundary data flow mismatches
- Type checkers validate signatures but not runtime key schemas
- Unit tests validate individual components with mocked inputs that may not match real upstream output
- Compilers validate syntax and types but not behavioral contracts

The act of drawing edges between components in DOT forces the agent to answer: "What data actually crosses this boundary, in which direction, using which keys?" That question — asked rigorously across every boundary — is what surfaces bugs like D-01 (key schema mismatch) and D-03 (function never called).

### The Dead Code Discovery Pattern

The `wrap_tool_with_hooks()` finding (D-03) is particularly striking:

> *"Dead code creates false confidence — `wrap_tool_with_hooks()` is tested but never called in production. Tests create an illusion of coverage for a feature that doesn't exist."*

DOT representation naturally surfaces dead code because **isolated nodes are visually obvious**. When you draw a function's callers and callees as edges, a function with no incoming edges from production code paths stands out immediately — even if it has 100% test coverage.

---

## 2. DOT as a Reconciliation Forcing Function

### The Core Mechanism

In order to create a valid DOT graph, agents must **commit to specific nodes, edges, and relationships**. This prevents vague or hand-wavy analysis. When multiple agents independently produce DOT representations of the same system, contradictions between their graphs become **mechanically detectable**.

From the Parallax methodology:

> *"DOT diagrams are discovery tools, not just documentation."*

### How Reconciliation Works in Practice

The dot-docs session ran the full Parallax Discovery pipeline — 3 waves of investigation:

**Wave 1 (9 agents, 3 triplicate teams):** Each team of 3 agents (Code Tracer, Behavior Observer, Integration Mapper) independently produced DOT diagrams. The lead investigator then reconciled across all 9 outputs.

Reconciliation revealed **7 discrepancies** (2 HIGH, 3 MEDIUM, 2 LOW):
- Where agents **agreed** on a node or edge (appeared in multiple outputs) → high confidence
- Where agents **disagreed** on edge direction or label → flagged for verification
- Where agents **contradicted** each other → prioritized for Wave 2

**Wave 2 (6 targeted verification agents):** Each high-priority discrepancy got a dedicated agent with the specific mandate: "Resolve this contradiction." All 5 original discrepancies were definitively resolved, with 3 bugs confirmed.

**Wave 3 (3 adversarial antagonist agents):** Each confirmed bug got an agent whose mandate was: "Try to **disprove** this bug using execution-based evidence." Result: 1 fully confirmed, 2 partially refuted (conclusions confirmed but mechanisms corrected).

### The Quality Gap Between Approaches

The session empirically compared three approaches:

| Metric | Manual Wave 1 | Recipe Wave 1 Only | Full 3-Wave Investigation |
|--------|:---:|:---:|:---:|
| Agent invocations | 6 | 9 | 18+ |
| DOT files produced | 6 | 9 | 9 + synthesis |
| Total DOT lines | 1,912 | 2,147 | 2,147 + 1,102 synthesis |
| Bugs confirmed | 2 potential | 2 + 5 flagged | **5 confirmed, 2 bonus** |
| Mechanism corrections | None | None | **3 corrected** |
| Best overview file | None (manual) | None (no synthesis) | **252 lines — the right answer** |

### Key Reconciliation Insight

> *"The 252-line synthesized diagram is qualitatively different from any Wave 1 diagram because it incorporates corrections. Wave 2 confirmed 3 bugs. Wave 3 then corrected the mechanisms of those bugs — `wrap_tool_with_hooks()` is dead code (not 'missing a call'), D-04 divergence only affects mixed pipelines (not all pipelines), and there's a 4th producer path for the token metric bug that code reading missed entirely."*

The reconciliation process is not just "merge the best parts" — it actively discovers information that no single agent could find alone, because the contradictions between agents point precisely at where the truth is non-obvious.

### Cross-Cutting Insights from Reconciliation

These findings **only** emerged from looking across all agents' DOT outputs:

1. **"Two Worlds" architecture** — 3 integration mappers independently discovered the same pipeline-vs-agent architectural divide from different angles
2. **PipelineContext is an implicit coupling bus** — no single agent saw all readers/writers; only cross-team synthesis reveals it's touched by every subsystem
3. **report_outcome bottleneck convergence** — 3 agents with different mandates independently found the same weakest point
4. **Fidelity touches 7 subsystems** — the most pervasive cross-cutting concern, with silent behavioral changes between parallel and sequential execution

---

## 3. Multi-Scale Navigation

### The Progressive Disclosure Pattern

The dot-docs session established a three-layer progressive disclosure architecture for DOT files, explicitly compared to a "Google Maps for code":

```
Layer 0 — overview.dot (~200 lines)
  Agent reads ONE file and knows the shape of the system.
  Like zooming out to see the whole map.
  
Layer 1 — architecture.dot, sequence.dot, state-machines.dot, integration.dot
  Agent reads only the perspectives relevant to its current task.
  Like zooming into a neighborhood.
  
Layer 2 — .investigation/ raw agent outputs
  Full raw agent findings, only read for deep forensics.
  Like zooming to street view.
```

### The overview.dot Contract

The user's key insight that drove the design:

> *"Maybe there needs to be ONE top level file that is the most appropriate representation per repo (giving some agency to the 'agent' or other process that does this work) and then everything else is linked/crawlable from there?"*

This became the `overview.dot` contract:
- **150–250 lines**, under 15KB
- **Renders standalone** as a readable image at normal viewing size
- **Agent-scannable** in minimal tokens — concise node labels (name + one-liner)
- **Uses cluster subgraphs** for logical groupings (zoom targets)
- **Includes a rendered legend subgraph** (not comment-only — agents can't read comments)
- **Annotates known issues** — confirmed bugs get red nodes/edges
- **Shape vocabulary enforces type semantics** (box=module, ellipse=process, hexagon=hook, etc.)

### Subgraph-Based Zoom

The cluster subgraph mechanism provides the zoom capability:

- `overview.dot` defines `subgraph cluster_core { ... }`, `subgraph cluster_utils { ... }`, etc.
- Detail files (`architecture.dot`, `sequence.dot`) use **matching cluster names** so agents can cross-reference
- An agent reading `overview.dot` sees `cluster_core` and knows it can load `architecture.dot` to zoom into that cluster
- This is mechanical navigation, not heuristic — the names must match exactly

### The "Gem" Discovery — Optimal Zoom Level

The session empirically discovered the optimal file sizes across the 6 DOT files from Wave 1:

| File | Lines | Rendering Quality | Token Efficiency | Best Use |
|------|------:|:-:|:-:|---|
| β-agent-2 (state machines) | **158** | ★★★★★ | ★★★★★ | Top-level overview |
| α-agent-2 (composition) | 212 | ★★★★ | ★★★★★ | Top-level architecture |
| α-agent-3 (integration) | 259 | ★★★ | ★★★★ | Detail subgraph |
| β-agent-3 (boundary analysis) | 285 | ★★★ | ★★★ | Detail subgraph |
| β-agent-1 (sequence flow) | 411 | ★ | ★★ | Deep-dive only |
| α-agent-1 (full architecture) | 587 | ★★ | ★★ | Deep-dive only |

> *"The **gem** was β-agent-2's state machine diagram — 158 lines, ~9KB, renders beautifully, and an agent could consume it in minimal tokens. The **walls** were the code-tracer outputs (411 and 587 lines) — forensically thorough but would never render as a readable image."*

This established the empirical basis for the 150–250 line target: compact enough to render and scan, detailed enough to be useful.

---

## 4. Use Cases Beyond Simple Diagramming

The dot-docs sessions and the broader dot-graph-bundle bootstrap discovery identified **9 distinct use cases** for DOT in the Amplifier ecosystem:

### UC-1: Pipeline Definition Language (Attractor DSL)
DOT as the **native runtime format** for AI workflow execution. The most mature use case: 54 DOT pipeline files, daily production use. Each node is an LLM agent task, edges define flow control, shapes map to handler types.

### UC-2: Architecture Documentation (Parallax Discovery Output)
DOT as the **standard output artifact** of every Parallax Discovery investigation. Each agent produces `diagram.dot` alongside textual findings. The dot-docs tooling synthesizes these into final architecture representations.

### UC-3: Event System Specification
DOT as **formal specifications** for system event flows. 13+ numbered DOT files documenting the Amplifier event system. Key insight: DOT revealed a cancellation gap (G2) that was *"invisible because no diagram showed all exit paths."*

### UC-4: Progressive Disclosure Architecture (Dotfiles)
DOT as per-person, per-repo architecture representations in a team knowledge base, designed for progressive LLM consumption. The "dual-purpose format thesis" — simultaneously human-renderable AND agent-scannable.

### UC-5: Recipe Visualization
DOT used to visualize YAML recipe structures. User reaction: *"this is REALLY helpful"* — immediately proposed it as a standard recipe-author capability. Visual encoding: blue=bash, green=agent, purple=foreach, yellow=condition, dashed orange=sub-recipe.

### UC-6: Context Compression for Agents
DOT as a **token-efficient context format**. An `overview.dot` at 150–250 lines (~10KB) gives an agent the same architectural understanding as reading thousands of lines of source code. This is context compression: the DOT file is a lossy but highly informative encoding of the full codebase.

### UC-7: Investigation Management
DOT diagrams as **investigation tracking artifacts**. During Parallax Discovery, the reconciliation DOT visualizes which discrepancies have been resolved, which are pending, and which bugs are confirmed. The investigation itself is managed through the graph.

### UC-8: Code Analysis via Graph Algorithms
DOT parsed into NetworkX for **algorithmic analysis**: cycle detection, DAG verification, topological sort, path analysis, connected components, isolated node detection. Dead code detection (isolated nodes) and dependency analysis (critical paths) become mechanical rather than heuristic.

### UC-9: Stigmergic Coordination Surface
DOT files as part of a **stigmergic coordination** pattern from the team knowledge base design — agents coordinating through shared state rather than direct messaging. The per-person dotfiles directory is a shared landscape that agents read to understand what exists.

---

## 5. The Dotfiles Discovery Pipeline

### Architecture Overview

The pipeline has two layers:

1. **Discovery Orchestrator** (outer loop) — manages per-person/per-repo lifecycle, determines which tier of investigation each repo needs
2. **Parallax Discovery Recipe** (inner loop, pre-existing) — performs the actual multi-agent investigation

### Pipeline Stages

```
profile.yaml ──► Discovery Orchestrator ──► Tier Selection
                        │                        │
                        │         ┌───────────────┼───────────────┐
                        │         ▼               ▼               ▼
                        │    Tier 1: Full    Tier 2: Wave 1   Tier 3: Diff
                        │    Parallax (3     + Synthesis      Patch (1
                        │    waves, gates)   (auto-approve)   agent)
                        │         │               │               │
                        │         ▼               ▼               ▼
                        │    ┌─────────────────────────────────────────┐
                        │    │         Synthesis Agent                 │
                        │    │  - Reconcile all DOT outputs           │
                        │    │  - Choose overview perspective         │
                        │    │  - Produce overview.dot                │
                        │    └─────────────────────────────────────────┘
                        │                    │
                        ▼                    ▼
                  dotfiles/<handle>/<repo>/overview.dot
```

### Tiered Refresh Logic

| Condition | Tier | Process | Cost |
|-----------|------|---------|------|
| No previous discovery run | **Tier 1: Full Parallax** | 3 waves with approval gates | ~18 agent invocations |
| Structural change detected (new/removed modules, >20% churn) | **Tier 2: Single-wave refresh** | Wave 1 triplicates + synthesis, auto-approved | ~9 agent invocations |
| Minor changes only | **Tier 3: Targeted update** | Single agent reads diff, patches affected subgraphs | 1 agent invocation |
| No changes since last run | **Skip** | No action | 0 |

Structural change detection uses `git diff --stat` filtered to source files (`*.py`, `*.rs`, `*.ts`) and config files (`pyproject.toml`, `Cargo.toml`, `package.json`, `*.yaml`). If module root files (`__init__.py`, `Cargo.toml`) were added or removed, or >20% of tracked files changed, it's structural.

### Pre-Scan Topic Selection

Before any investigation waves, a pre-scan agent reads repo metadata to determine which topics are relevant:

| Condition | Topic |
|-----------|-------|
| Always | `module_architecture` |
| CLI entry points, servers, orchestrators | `execution_flows` |
| State enums, lifecycle transitions, event systems | `state_machines` |
| >3 packages, plugin architectures, cross-boundary integration | `integration` |

### Synthesis Step

The synthesis agent:
1. Reads ALL raw DOT files from the investigation workspace
2. Reconciles overlapping content (keeps nodes/edges appearing in multiple agents as high-confidence)
3. Chooses the overview perspective based on repo type
4. Produces `overview.dot` (mandatory) plus detail files (optional)

The overview perspective heuristic:
- **Composition systems** → architecture/composition diagram
- **Execution engines** → execution flow or state-machine diagram
- **Libraries/toolkits** → architecture/dependency diagram
- **Repos with confirmed bugs** → whichever diagram best annotates them

### Output Directory Structure

```
dotfiles/<github-handle>/
  <repo-name>/
    overview.dot          # THE top-level file — mandatory
    architecture.dot      # Module boundaries, dependencies
    sequence.dot          # Key execution flows
    state-machines.dot    # State enums, transitions
    integration.dot       # Cross-boundary data flows
    .discovery/
      last-run.json       # Timestamp, tier, commit hash
      manifest.json       # Topics investigated, agent count
```

### Implementation Status

Fully implemented in the dot-docs workspace with **247 passing tests**:

| Component | Files |
|-----------|-------|
| Python utilities | `structural_change.py`, `dot_validation.py`, `discovery_metadata.py` |
| Recipes | `dotfiles-prescan.yaml`, `dotfiles-synthesis.yaml`, `dotfiles-discovery.yaml` |
| Agent prompts | `prescan-prompt.md`, `synthesis-prompt.md`, `dot-quality-standards.md` |
| Tests | 8 test files, 247 passing, 0 failures |

---

## 6. Quality Standards and Conventions

### Shape Vocabulary (Architecture Documentation Dialect)

| Shape | Meaning |
|-------|---------|
| `box` | Module / package |
| `ellipse` | Process / runtime entity |
| `component` | Orchestrator / coordinator |
| `hexagon` | Hook / interceptor |
| `diamond` | Decision / transform |
| `cylinder` | State store |
| `note` | Config file |
| `box3d` | External dependency |

**Note:** This vocabulary is distinct from the Attractor pipeline DSL vocabulary, where shapes map to execution handlers (box=codergen, diamond=conditional, hexagon=human-gate). The two overlap but disagree on what shapes mean — an open design question for the dot-graph-bundle.

### Edge Style Semantics

| Style | Meaning |
|-------|---------|
| `solid` (default) | Declared / direct dependency or call |
| `dashed` | Runtime / optional relationship |
| `dotted` | Coordinator-mediated / indirect relationship |
| `bold` | Critical path |

### Color Conventions

| Color | Meaning |
|-------|---------|
| `red` | Confirmed bug (execution-proven) |
| `orange` | Suspected issue / bypass path |
| `green` | Spec-correct / healthy path |

### Node ID Convention

All node IDs use `snake_case` prefixed by the cluster name: `core_session_manager`, `utils_retry_helper`. This avoids collisions and makes provenance obvious when cross-referencing between files.

### Anti-Patterns (Documented from Empirical Evidence)

| Anti-pattern | Why it fails |
|---|---|
| Multi-line inline doc labels | Breaks DOT layout; use `\n` within label strings |
| More than 80 nodes per graph | Graph becomes unreadable; split into detail files |
| `splines=ortho` with high node counts | Graphviz rendering time explodes above ~30 nodes |
| Comment-only legends | Agents cannot read DOT comments; legend must be rendered as a real `subgraph cluster_legend` |
| 400+ line single-file DOT | Forensically thorough but unrenderable; target 150–250 for overview, 200–400 for detail |
| Node IDs without cluster prefix | Creates collision risk across files |

### The overview.dot Checklist

- [ ] 150–250 lines and under 15KB
- [ ] All cluster subgraphs present with `cluster_` prefix
- [ ] Legend is a rendered subgraph, not a comment
- [ ] All node IDs follow `snake_case` with cluster prefix
- [ ] Every shape matches the shape vocabulary table
- [ ] Edge styles follow the semantics table
- [ ] Red for confirmed bugs; orange for suspected
- [ ] `dot -Tsvg overview.dot` renders without errors
- [ ] No anti-patterns present

---

## 7. "Aha Moments" — Surprising Discoveries and Philosophical Insights

### Aha #1: DOT Catches Bugs That Tests, LSP, and Type Checkers All Miss

The single most important discovery. The `wrap_tool_with_hooks()` dead code finding is the canonical example: a function with tests, full coverage, and correct types — but never called from any production code path. **Only** by drawing the call graph in DOT (which forces you to trace actual callers) does the isolation become visible.

> *"Dead code creates false confidence — `wrap_tool_with_hooks()` is tested but never called in production. Tests create an illusion of coverage for a feature that doesn't exist."*

### Aha #2: The Act of Creating DOT IS the Discovery

This is the philosophical core. DOT diagrams are not documentation of what you already know — they are the mechanism by which you discover what you don't know. The agent must commit to specific nodes, edges, and labels, and any vagueness or gap in understanding immediately manifests as a missing node or contradictory edge.

> *"DOT diagrams are discovery tools, not just documentation."*

### Aha #3: Contradictions Between Agents Are the Signal, Not the Noise

When two agents produce different DOT representations of the same system, the natural instinct is to pick the "better" one. But the Parallax methodology discovered that **the contradictions themselves are the most valuable data** — they point precisely at where the truth is non-obvious. Every confirmed bug in the attractor investigation was found at a point of inter-agent disagreement.

### Aha #4: The 158-Line "Gem" vs. the 587-Line "Wall"

The empirical discovery that DOT quality is not proportional to thoroughness. The best DOT file from Wave 1 was the shortest (158 lines, state-machine diagram). The worst were the longest (411 and 587 lines). This isn't just aesthetic — longer files don't render as readable images and consume unnecessary tokens when loaded as agent context.

> *"The gem was β-agent-2's state machine diagram — 158 lines, ~9KB, renders beautifully, and an agent could consume it in minimal tokens."*

### Aha #5: The Synthesized Diagram Is Categorically Different

The 252-line synthesized overview produced after 3 waves of investigation is not just a "better" version of any single agent's output — it's a qualitatively different artifact. It incorporates mechanism corrections that Wave 3 discovered (dead code identification, narrowed scope of divergence, discovery of a 4th producer path), making it **trustworthy** rather than merely **plausible**.

### Aha #6: DOT as Cancellation Gap Revealer

During event system specification work, DOT diagrams revealed a cancellation gap (G2) that was entirely invisible to code reading:

> *"The cancellation gap (G2) was invisible because no diagram showed all exit paths."*

This is the "forcing function" aspect in action: drawing all exit paths in DOT forces completeness that prose descriptions never enforce.

### Aha #7: LLMs Are Naturally Good at DOT

From ecosystem research: due to training data prevalence, DOT is one of the most reliably LLM-generated diagram formats. The challenge isn't getting LLMs to produce DOT — it's getting them to produce **correct, well-structured, convention-compliant** DOT. This is why the quality standards and review agents matter more than basic generation capabilities.

### Aha #8: The Dual-Purpose Format — No Compromise Needed

The original design question was whether DOT should be optimized for human rendering or agent consumption. The surprising answer was **both, without compromise** — because the same properties that make DOT render well (concise labels, logical grouping, limited node count) also make it token-efficient for agents. The constraints are complementary, not competing.

### Aha #9: Stigmergic Coordination Through DOT

The team knowledge base design positions DOT files as **stigmergic coordination surfaces** — agents coordinate through shared artifacts rather than direct messaging. This is philosophically significant: the DOT files in `dotfiles/<handle>/<repo>/` are not just documentation — they are the **coordination medium** through which agents understand what exists, what patterns to follow, and who owns what.

### Aha #10: The Evolution Arc Only Expands

DOT's role across the Amplifier ecosystem has only expanded over time:

```
Pipeline DSL → Investigation Artifact → System Specification →
Architecture Representation → Composable Workflow Primitive →
Ecosystem-Wide Format
```

Each phase **added** a new use case without replacing previous ones. No other format in the ecosystem spans all these roles.

---

## Appendix A: Session Inventory

### Primary Session (dot-docs project)
| Session ID | Type | Turns | Date | Description |
|------------|------|-------|------|-------------|
| `71295782-20c0-4905-a737-2ed63a30aa3f` | Root | 23 | Mar 12–13 | THE session — research, design, implementation of entire dot-docs system |
| `03d3e873-ef27-41f6-ae23-49fe538aa5ea` | Root | 1 | Mar 13 | Session repair request |

### Key Sub-Sessions (dot-docs project)
| Session ID | Agent | Description |
|------------|-------|-------------|
| `...-a58a3a32a0be406d` | brainstormer | Design brainstorming for dotfiles discovery system |
| `...-4023efedb4914339` | zen-architect | Final verification and merge options |
| `...-02b026a96be14ae7` | plan-writer | Implementation plan generation (2,818 lines) |
| `...-e71d7289a3d14b06` | plan-writer | Additional planning |
| `...-d937a96eab854f29` | explorer | Initial repo exploration |
| `...-ff51b45a8ce64baf` | web-research | Team knowledge base document retrieval |

### Parallax Discovery Sessions (dot-docs project, ~100 sessions)
| Agent Type | Count | Purpose |
|------------|-------|---------|
| `code-tracer` | ~20 | LSP-based code structure tracing, DOT diagram production |
| `behavior-observer` | ~10 | Runtime behavior analysis, artifact reading |
| `integration-mapper` | ~10 | Cross-boundary data flow analysis |
| `lead-investigator` | ~15 | Reconciliation across agents, discrepancy identification |
| `antagonist` | ~8 | Adversarial execution-based bug verification |
| `file-ops` | ~8 | File write operations for investigation artifacts |

### Implementation Sessions (dot-docs project, ~50 sessions)
| Agent Type | Count | Purpose |
|------------|-------|---------|
| `implementer` | ~20 | TDD implementation of 9 tasks |
| `code-quality-reviewer` | ~15 | Quality review of implementations |
| `spec-reviewer` | ~10 | Spec compliance review |
| `git-ops` | ~10 | Git commit operations |

### dot-graph-bundle Bootstrap Session
| Session ID | Type | Turns | Date | Description |
|------------|------|-------|------|-------------|
| `a31d8d0c-a01c-4bb8-8c3d-f72db174bf61` | Root | 1 | Mar 13 | Bootstrap discovery for dot-graph-bundle — dispatched 12 agent investigations |

---

## Appendix B: File Locations

### dot-docs Project Documentation
| File | Description |
|------|-------------|
| `/home/bkrabach/dev/dot-docs/docs/plans/2026-03-12-dotfiles-discovery-design.md` | Design document (207 lines) |
| `/home/bkrabach/dev/dot-docs/dot-docs/docs/plans/2026-03-12-dotfiles-discovery-implementation.md` | Implementation plan (2,818 lines) |
| `/home/bkrabach/dev/dot-docs/dot-docs/docs/plans/2026-03-12-task-2-dot-validation-utilities.md` | DOT validation task plan |
| `/home/bkrabach/dev/dot-docs/dot-docs/context/dot-quality-standards.md` | Quality standards reference |
| `/home/bkrabach/dev/dot-docs/dot-docs/context/synthesis-prompt.md` | Synthesis agent prompt |
| `/home/bkrabach/dev/dot-docs/dot-docs/context/prescan-prompt.md` | Pre-scan agent prompt |

### dot-graph-bundle Project Documentation
| File | Description |
|------|-------------|
| `/home/bkrabach/dev/dot-graph-bundle/BOOTSTRAP-SYNTHESIS.md` | Grand synthesis: 9 use cases, capability map, 4-phase roadmap |
| `/home/bkrabach/dev/dot-graph-bundle/DOT-CONCEPTS-DEEP-DIVE.md` | Conceptual visions, 7 use cases, design decisions, aha moments |
| `/home/bkrabach/dev/dot-graph-bundle/SESSION-INDEX.md` | All sessions from past 2 weeks with DOT references |
| `/home/bkrabach/dev/dot-graph-bundle/DOT-ARTIFACTS-CATALOG.md` | Catalog of 19+ existing DOT artifact files |
| `/home/bkrabach/dev/dot-graph-bundle/DOT-DIALECT-COMPARISON.md` | Attractor vs architecture documentation dialect comparison |
| `/home/bkrabach/dev/dot-graph-bundle/DOT-ECOSYSTEM-RESEARCH.md` | External DOT/Graphviz ecosystem research |
| `/home/bkrabach/dev/dot-graph-bundle/ATTRACTOR-DOT-EXPERTISE.md` | Attractor-specific DOT patterns and anti-patterns |
| `/home/bkrabach/dev/dot-graph-bundle/BUNDLE-GUIDANCE.md` | Foundation expert's bundle creation playbook |

---

## Appendix C: Open Questions (Carried Forward)

These questions were raised during the dot-docs sessions but not resolved:

1. **Auto-approve thresholds** — At what confidence level should Tier 2 refreshes auto-approve Wave 1 findings?
2. **Cross-repo DOT references** — When repos depend on each other, should DOT files reference each other via URL or subgraph include?
3. **SVG rendering pipeline** — Should the pipeline produce rendered SVG/PNG alongside DOT source?
4. **Parallelism across repos** — Can multiple repos be investigated simultaneously without hitting LLM rate limits?
5. **Two shape vocabularies** — Should the bundle establish one unified vocabulary or document two separate ones (pipeline vs. architecture)?
6. **Hand-maintained vs. generated DOT** — Where's the boundary between generated-from-source (cheap, limited) and LLM-synthesized (expensive, richer)?
7. **Context variable injection** — Does the PipelineHandler support `context.*` attributes for parameterized subgraph invocation?
8. **The events.dot convention** — Rejected for hand-maintenance, but viable if generated from source?
