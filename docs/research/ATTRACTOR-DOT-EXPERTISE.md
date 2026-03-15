# Attractor DOT Expertise: Design Analysis for `amplifier-bundle-dot-graph`

> **Author:** attractor-expert (sub-session of dot-graph-bundle design)
> **Date:** 2026-03-13
> **Source material:** Attractor engine source (`engine.py`, `validation.py`, `handlers/`, `stylesheet.py`, `graph.py`, `transforms.py`), 54+ DOT pipeline files, `dot-reference.md`, `pipeline-awareness.md`, DOT-CONCEPTS-DEEP-DIVE.md, DOT-DIALECT-COMPARISON.md, DOT-ARTIFACTS-CATALOG.md, DOT-ECOSYSTEM-RESEARCH.md, and real-world consensus/semport pipelines.
> **Purpose:** Extract every hard-won lesson from Attractor's DOT usage to inform the design of a general-purpose DOT bundle for the entire Amplifier ecosystem.

---

## Table of Contents

1. [DOT as Pipeline DSL — Key Design Decisions](#1-dot-as-pipeline-dsl--key-design-decisions)
2. [DOT Authoring Patterns for LLM Generation](#2-dot-authoring-patterns-for-llm-generation)
3. [The Model Stylesheet Pattern](#3-the-model-stylesheet-pattern)
4. [Validation — What Exists and What's Missing](#4-validation--what-exists-and-whats-missing)
5. [What Should Be Generalized](#5-what-should-be-generalized)
6. [The General-Purpose DOT Reference Card](#6-the-general-purpose-dot-reference-card)
7. [Progressive Disclosure for Agents](#7-progressive-disclosure-for-agents)
8. [Anti-Patterns and Warnings](#8-anti-patterns-and-warnings)

---

## 1. DOT as Pipeline DSL — Key Design Decisions

### 1.1 Why DOT Was Chosen

The choice of DOT as the pipeline definition language was not accidental. Five properties made it the right fit:

1. **Dual-purpose format** — A single DOT file is simultaneously machine-parseable (the engine walks it) AND human-renderable (paste into any Graphviz viewer to see the workflow). No other format achieves this. YAML describes structure but can't render. Mermaid renders but has no formal grammar robust enough for machine parsing.

2. **LLMs already know it** — DOT has been in public training corpora since 1991. LLMs generate syntactically valid DOT far more reliably than any alternative. The formal BNF grammar means there's an unambiguous "right answer" for every construct — unlike Mermaid, where implicit rules create ambiguity.

3. **Custom attributes for free** — DOT allows arbitrary `key=value` attributes on nodes, edges, and graphs. Graphviz silently ignores attributes it doesn't recognize. This means Attractor can store `prompt`, `goal_gate`, `fidelity`, `model_stylesheet`, and every other pipeline-specific attribute directly in the DOT file without breaking rendering. No schema extension needed.

4. **Graph topology IS the execution model** — Directed edges naturally express "what runs after what." Conditional branching is just conditional edges. Parallel execution is just multiple outgoing edges from a fan-out node. The visual representation _is_ the control flow — there's no translation layer.

5. **Separation of structure and layout** — DOT describes structure; layout engines handle positioning. LLMs don't need to reason about pixel coordinates or line routing. They describe _what connects to what_, and Graphviz figures out where to put everything.

### 1.2 The Shape-to-Handler Mapping

This is the single most important design decision in the Attractor DOT dialect. The canonical mapping lives in `validation.py`:

```python
SHAPE_TO_HANDLER: dict[str, str] = {
    "Mdiamond":      "start",              # Pipeline entry point (exactly one)
    "Msquare":       "exit",               # Pipeline exit point (at least one)
    "box":           "codergen",            # LLM agent with full tool access
    "ellipse":       "codergen",            # Alias for box (readability)
    "diamond":       "conditional",         # Pure router — NO LLM call
    "component":     "parallel",            # Fan-out: concurrent branches
    "tripleoctagon": "parallel.fan_in",     # Fan-in: collect parallel results
    "parallelogram": "tool",               # Direct tool/shell execution
    "hexagon":       "wait.human",          # Human-in-the-loop gate
    "house":         "stack.manager_loop",  # Supervisor loop over sub-pipeline
    "folder":        "pipeline",            # Nested pipeline invocation
}
```

**Why shapes instead of explicit `node_type` attributes?**

The alternative (used by the `node_type` dialect in `consensus_task.dot` and `semport.dot`) requires every node to carry an explicit `node_type="stack.observe"` attribute plus `is_codergen="true"`, `llm_provider="..."`, `llm_model="..."`, `max_agent_turns="..."`, and `timeout="..."` — 5-7 boilerplate attributes per node.

The shape-based approach eliminates all of that. A node with `shape=box` (or no explicit shape at all, since box is the default) _is_ a codergen node. The shape carries the semantic meaning visually and semantically at zero attribute cost. This reduced per-node token count from ~180 tokens to ~50 tokens — a 3-4× improvement.

**The critical insight:** Convention over configuration. The shape vocabulary is finite (11 shapes) and well-defined. An LLM only needs to memorize one mapping table, not a protocol of required attributes.

### 1.3 The Handler Resolution Order

The `HandlerRegistry.get()` method resolves handlers with a three-level fallback:

```
1. Node's explicit `type` attribute (highest priority — explicit override)
2. Node's `node_type` attribute if it matches a registered handler (compatibility)
3. SHAPE_TO_HANDLER mapping on the node's shape (default path)
4. Fallback: "codergen" (if shape is unrecognized)
```

This means:
- **New pipelines** use shape-based dispatch (the idiomatic path)
- **Legacy `node_type` pipelines** work without modification (backward compatibility)
- **Explicit `type` overrides** allow advanced users to bypass the shape vocabulary entirely
- **Unknown shapes** don't crash — they gracefully default to codergen

### 1.4 Critical Design Constraint: `diamond` Is NOT an LLM Node

This caused real bugs in production. The `diamond` shape maps to the `conditional` handler, which does **not** call an LLM. It's a pure routing node that evaluates outgoing edge conditions against the previous node's outcome.

The correct pattern is always:

```dot
// WRONG: Expecting diamond to do LLM work
gate [shape=diamond, prompt="Evaluate whether tests pass"]

// CORRECT: Box does the work, diamond routes
test [prompt="Run tests. Report outcome=success if all pass, outcome=fail if not."]
gate [shape=diamond, label="Tests Pass?"]
test -> gate
gate -> done      [condition="outcome=success"]
gate -> implement [condition="outcome!=success"]
```

This separation is architectural — work nodes produce outcomes; routing nodes consume outcomes. The `node_type` dialect's `stack.steer` conflates both into one node, which is more compact but couples concerns.

### 1.5 Conventions That Emerged as Essential

| Convention | Why It Matters |
|-----------|---------------|
| **Exactly one `Mdiamond` (start) per graph** | Engine uses `_find_start_node()` — multiple starts are ambiguous |
| **At least one `Msquare` (exit) per graph** | Engine checks `is_exit_node()` — missing exit = infinite walk |
| **`$goal` expansion in prompts** | The `graph [goal="..."]` value replaces `$goal` in every node's prompt — single source of truth |
| **`outcome=success` / `outcome!=success` in conditions** | Simple key=value matching, NOT Python expressions. `&&` for conjunction. No `||`. |
| **`weight` on conditional edges for tiebreaking** | Higher weight = preferred when multiple edges match. Without weights, selection is nondeterministic |
| **`loop_restart=true` on cycle-back edges** | Resets iteration state to prevent infinite context accumulation |
| **Cluster subgraphs start with `cluster_`** | Standard Graphviz convention — only `cluster_`-prefixed subgraphs render with bounding boxes |

---

## 2. DOT Authoring Patterns for LLM Generation

### 2.1 Patterns That Work Well

**The Tutorial Ladder (10 progressive examples):**

Attractor ships a numbered tutorial sequence from minimal to maximal complexity. This turned out to be the single most effective teaching tool for both humans and LLMs:

| File | What It Teaches |
|------|----------------|
| `01-simple-linear.dot` | Minimal: start → work → done |
| `02-plan-implement-test.dot` | Multi-step traversal, context flow |
| `03-conditional-routing.dot` | Diamond gates, edge conditions |
| `04-retry-with-fallback.dot` | `max_retries`, `retry_target`, `fallback_retry_target` |
| `05-parallel-fan-out.dot` | Fan-out/fan-in, `join_policy`, `error_policy` |
| `06-model-stylesheet.dot` | CSS-like multi-provider routing |
| `07-fidelity-modes.dot` | Context fidelity modes |
| `08-human-gate.dot` | Hexagon human gates with accelerator keys |
| `09-manager-supervisor.dot` | House-shape manager loop |
| `10-full-attractor.dot` | Kitchen-sink demo — every feature combined |

**The "3 Patterns" Reference:**

For inline LLM generation, three copy-paste patterns cover ~80% of use cases:

1. **Linear** — `start → a → b → done` (simplest possible)
2. **Conditional Loop** — work → test → diamond gate → (success: done, fail: retry)
3. **Parallel Fan-Out** — component → branches → tripleoctagon → done

These three patterns appear in the `dot-reference.md` context card and are the foundation of all LLM-generated pipelines.

**The Convergence Factory Pattern:**

A reusable generate → validate → assess → feedback → loop pattern that appears in multiple production pipelines. The key insight: the pattern can be parameterized via `$variable` expansion and invoked as a nested sub-pipeline via `shape=folder`.

**The Conversational Gate Pattern:**

Composes hexagon (human gate) + box (evaluator) + diamond (routing) + loop_restart edges to create iterative human-AI Q&A loops entirely within DOT — no new handler needed.

### 2.2 Common LLM Mistakes When Generating DOT

These are the actual bugs encountered across dozens of sessions:

| Mistake | Frequency | Impact | Prevention |
|---------|-----------|--------|-----------|
| **Using `prompt` on a diamond node** | Very common | Prompt is silently ignored — diamond does no LLM work | Reference card must emphasize "diamond = pure router, NO LLM" |
| **Forgetting `shape=Mdiamond` on start node** | Common | Parse error / engine can't find entry point | Validator catches this as ERROR |
| **Using `status=success` instead of `outcome=success`** | Common | Condition never matches — node has no outgoing path | Condition syntax validator catches malformed keys |
| **Missing `weight` on competing edges** | Common | Nondeterministic edge selection | Validator warns about ambiguous edge selection |
| **Using Python expressions in conditions** | Occasional | `if outcome == "success"` doesn't parse — conditions are `key=value`, not Python | Reference card shows the exact syntax |
| **`llm_prompt` instead of `prompt`** | Occasional (when LLM has seen node_type dialect) | Attribute is silently ignored — node has no prompt | Validator could warn about unrecognized `llm_prompt` |
| **Quoting attribute values inconsistently** | Occasional | `shape="diamond"` works but `shape=diamond` is more idiomatic for simple values | Not a bug per se, but the reference card should show idiomatic style |
| **Too many nodes (>10)** | Occasional | Cost explosion — each codergen node is a full LLM session | Reference card advises "prefer fewer, well-prompted nodes" |
| **`full` fidelity everywhere** | Occasional | Every node reuses the full conversation history — expensive and slow | Reference card explains fidelity modes with cost implications |
| **Self-referencing retry_target** | Rare | `implement [retry_target="implement"]` can work but is confusing vs using a diamond loop | Style guidance, not a hard error |
| **Fan-in without fan-out** | Rare | `tripleoctagon` expects `parallel.results` context — fails without a preceding `component` | Validator checks topology |

### 2.3 What Makes a Good LLM-Generated Pipeline

From analyzing all 54+ DOT files in the Attractor ecosystem:

1. **3-7 nodes is the sweet spot** — Below 3, just do it directly. Above 7, cost and complexity dominate. Production pipelines cluster around 5-8 nodes.

2. **Prompts should be self-contained** — Each node's prompt should make sense even if the agent has no prior context. Use `$goal` for the objective, be specific about inputs/outputs/actions.

3. **Goal gates on critical nodes** — `goal_gate=true` with `retry_target` ensures the pipeline doesn't exit with incomplete work. But don't put goal gates on every node — just the critical deliverables.

4. **Use the pipeline decision heuristic:**
   - Single file edit, simple question → No pipeline
   - 2-4 ordered steps, clear sequence → Inline pipeline with `dot_source`
   - Branches, retries, parallel work, human review → Full pipeline file

---

## 3. The Model Stylesheet Pattern

### 3.1 How It Works

The `model_stylesheet` is a graph-level attribute containing CSS-like rules that assign LLM provider/model configuration to nodes by selector:

```dot
graph [
    model_stylesheet="
        * { llm_provider: anthropic; llm_model: claude-sonnet-4-20250514; }
        .planning { llm_provider: openai; llm_model: o3; reasoning_effort: high; }
        .fast { llm_provider: gemini; llm_model: gemini-2.5-flash-preview-05-20; }
        #critical_review { llm_provider: anthropic; llm_model: claude-opus-4-20250514; }
    "
]
```

Nodes declare their class: `plan [class="planning"]`. The engine resolves the model at execution time.

### 3.2 Selector Specificity

The resolution order mirrors CSS specificity:

```
1. Explicit node attribute (llm_model="..." on the node itself)   — highest
2. #node_id selector match
3. .class selector match
4. shape selector match (box, ellipse, diamond, etc.)
5. * wildcard match                                                — lowest
```

Properties: `llm_model`, `llm_provider`, `reasoning_effort`, `max_retries`, `fidelity`.

### 3.3 Why This Design Instead of Per-Node Attributes

Three reasons:

**1. DRY (Don't Repeat Yourself):** In the `consensus_task.dot` file (node_type dialect), the string `is_codergen="true"` appears 14 times, `llm_provider="anthropic"` appears 10 times, and `timeout="300"` appears 7 times. The stylesheet eliminates this entirely — model config is declared once, applied everywhere.

**2. Easy model swapping:** Changing from Claude to GPT for all nodes requires editing ONE line in the stylesheet, not 14 node definitions. For A/B testing different models, you clone the pipeline and change one stylesheet rule.

**3. Token efficiency for LLM generation:** An LLM generating a pipeline doesn't need to remember which model each node should use — it just assigns semantic classes (`.planning`, `.code`, `.fast`, `.review`) and the stylesheet maps those to concrete models. This separation of _what kind of work_ from _which model does it_ dramatically reduces generation errors.

### 3.4 The Provider Extraction Challenge

The engine needs `_extract_required_providers()` to parse `llm_provider` values from both node attributes AND stylesheet rules before execution begins — it must know which providers to initialize. This was a non-trivial implementation that required parsing the stylesheet independently of node resolution.

**Lesson for the general bundle:** Any DOT processing system that uses custom attributes needs to consider "which attributes need pre-scan before graph walking?" versus "which can be resolved lazily during traversal?"

---

## 4. Validation — What Exists and What's Missing

### 4.1 What Exists Today

Attractor has two validation systems:

**Pipeline Validation (`validation.py` — 400+ lines, 15+ rules):**

| Rule | Severity | What It Checks |
|------|----------|----------------|
| `single_start` | ERROR | Exactly one `Mdiamond` node |
| `has_exit` | ERROR | At least one `Msquare` node |
| `start_reachable` | ERROR | Start node has outgoing edges |
| `exit_reachable` | ERROR | Exit node(s) reachable from start |
| `no_orphan_nodes` | WARNING | Every node reachable from start |
| `prompt_on_llm_nodes` | WARNING | Codergen nodes have a prompt or explicit label |
| `condition_syntax` | ERROR | Edge conditions parse correctly (key=value format) |
| `type_known` | WARNING | Explicit `type` attribute maps to a registered handler |
| `goal_gate_retry` | WARNING | Nodes with `goal_gate=true` have a `retry_target` |
| `fan_in_has_fan_out` | WARNING | `tripleoctagon` is preceded by `component` |
| `diamond_no_prompt` | INFO | Diamond nodes shouldn't have prompts (they're ignored) |
| `stylesheet_syntax` | WARNING | Model stylesheet parses without errors |
| `unreachable_edges` | WARNING | Edges whose conditions can never match |
| `folder_has_dot_file` | WARNING | Folder nodes have `dot_file` attribute |

**Architecture DOT Validation (`dot_validation.py` — 216 lines, 3 checks):**

| Check | Method | What It Does |
|-------|--------|-------------|
| Syntax validation | `dot -Tsvg <file>` | Shells out to Graphviz — invalid DOT is a hard fail |
| Line count | Count lines, check range | 150-250 for overview.dot, 200-400 for detail files |
| SVG render quality | Check SVG file | Non-zero size, non-degenerate bounding box |

### 4.2 What's MISSING That Would Be Valuable

These are validation gaps identified through real-world experience:

**1. Cross-dialect attribute warnings:**
When an LLM generates `llm_prompt="..."` (node_type dialect) in an Attractor pipeline, the attribute is silently ignored. The validator should warn: _"Node 'X' has `llm_prompt` attribute — did you mean `prompt`? (See: Attractor dialect uses `prompt`, not `llm_prompt`)"_

Similarly for `context_fidelity_default` (should be `default_fidelity`), `context_thread_default` (should be `default_thread_id`), and `is_codergen` (unnecessary in Attractor — shape implies handler).

**2. Cycle detection with exit-path verification:**
NetworkX can detect cycles, but the real question is: "Does every cycle have a conditional exit edge?" A cycle without a conditional exit is an infinite loop. Currently, cycles are legal (and necessary for retry patterns), but the validator doesn't verify that the cycle can terminate.

**3. Unused model stylesheet classes:**
If the stylesheet defines `.planning` but no node uses `class="planning"`, the class is dead code. Conversely, if a node uses `class="review"` but no stylesheet rule matches `.review`, the node silently falls back to `*` — which may not be the intent.

**4. Edge coverage analysis:**
For a diamond node with two outgoing edges (`condition="outcome=success"` and `condition="outcome!=success"`), the validator could verify that the conditions are exhaustive. If there are three edges with `=success`, `=fail`, and `=partial_success`, it could warn that `outcome=retry` and `outcome=skipped` are unhandled.

**5. Prompt variable expansion verification:**
If a prompt contains `$language` but the graph has no `params` declaration and no context mechanism to inject `$language`, the variable will remain un-expanded at runtime. The validator could warn about unresolvable `$variables`.

**6. Token cost estimation:**
Based on node count, fidelity modes, and model assignments, the validator could estimate the total token cost of a pipeline run — enabling budget-aware pipeline design.

**7. Rendering readability check:**
Render to SVG and check for overlapping node labels, edge crossings, or degenerate bounding boxes. This goes beyond "does it parse?" to "will a human be able to read it?"

**8. General-purpose DOT schema validation:**
For non-pipeline DOT (architecture diagrams, event specs, recipe visualizations), validate against a declared schema: "All nodes must have `label`. All `cluster_` subgraphs must have `label`. Shape must be from this vocabulary: [box, ellipse, cylinder, diamond, ...]."

---

## 5. What Should Be Generalized

### 5.1 Attractor-Specific (Should Stay in Attractor Bundle)

These are tightly coupled to the pipeline execution engine and have no meaning outside that context:

| Feature | Why It's Attractor-Specific |
|---------|----------------------------|
| `SHAPE_TO_HANDLER` mapping | Shapes → pipeline handlers is a runtime dispatch mechanism |
| `prompt` attribute semantics | Only meaningful when a node triggers an LLM call |
| `goal_gate`, `retry_target`, `fallback_retry_target` | Pipeline retry/gate logic |
| `fidelity` modes (full/compact/truncate/summary:*) | Pipeline context management |
| `model_stylesheet` | Pipeline model routing |
| `join_policy`, `error_policy`, `max_parallel` | Pipeline parallelism control |
| `manager.*` attributes | Pipeline supervisor pattern |
| `dot_file`, `context.*` on folder nodes | Pipeline composition |
| Edge selection algorithm (condition → preferred_label → weight → lexical) | Pipeline routing |

### 5.2 Generalizable (Should Move to DOT Bundle)

These provide value to ANY Amplifier agent or bundle working with DOT:

**Core DOT capabilities:**

| Capability | Value for General Ecosystem |
|-----------|---------------------------|
| **DOT syntax validation** (parse with pydot or `dot -Tcanon`) | Every DOT consumer needs this |
| **DOT rendering** (SVG, PNG, PDF via Graphviz CLI) | Universal visualization need |
| **DOT structural analysis** (cycles, connectivity, reachability via NetworkX) | Any graph-based workflow needs this |
| **Node/edge/graph attribute extraction** | Parse DOT → structured data for any purpose |
| **Line count / file size validation** | Quality gating for generated DOT |
| **Cluster naming validation** (`cluster_` prefix enforcement) | Standard Graphviz convention |
| **JSON round-tripping** (`dot -Tjson` for machine processing) | Programmatic DOT manipulation |
| **Layout engine selection guidance** (dot vs neato vs fdp vs sfdp) | Applies to all DOT rendering |

**DOT authoring patterns (shape vocabularies):**

The ecosystem has TWO distinct shape vocabularies — and the bundle should document BOTH:

| Context | Shape Vocabulary | Owner |
|---------|-----------------|-------|
| **Pipeline execution** | Mdiamond=start, box=LLM, diamond=route, component=parallel, etc. | Attractor bundle |
| **Architecture documentation** | box=module, ellipse=process, cylinder=store, diamond=decision, etc. | dot-graph bundle |
| **Recipe visualization** | box=bash step, hexagon=foreach, diamond=condition, etc. | recipes bundle |

The dot-graph bundle should establish the **architecture documentation** vocabulary as the general-purpose default, and provide extension points for domain-specific vocabularies like Attractor's.

**CSS-like stylesheet pattern (generalized):**

The `model_stylesheet` concept is Attractor-specific, but the _pattern_ of "CSS-like rules applied to DOT nodes by selector" is generalizable. A general `dot_stylesheet` could apply:
- Visual styling (colors, shapes, fonts) by node class
- Custom metadata by node class
- Validation rules by node class

**The dual-purpose format principle:**

The insight that DOT files serve both human rendering AND machine parsing is general. The dot-graph bundle should codify this as a design principle with guidance:
- Token-efficient node labels (name + one-liner, not paragraphs)
- Rendered legends as real subgraphs (not comments)
- Cluster subgraphs for logical groupings
- Shape-as-type semantic vocabularies

### 5.3 Architecture DOT Conventions to Standardize

From the dot-docs work, these conventions should be the dot-graph bundle's primary offering:

**Shape vocabulary for architecture diagrams:**

| Shape | Meaning |
|-------|---------|
| `box` | Module / package |
| `ellipse` | Process / function / runtime entity |
| `component` | Orchestrator / coordinator |
| `hexagon` | Hook / interceptor |
| `diamond` | Decision / transform |
| `cylinder` | State store / database |
| `note` | Config file |
| `box3d` | External dependency |
| `folder` | Filesystem path |
| `record` | Data structure |
| `circle` | Start state |
| `doublecircle` | Terminal state |

**Edge style semantics:**

| Style | Meaning |
|-------|---------|
| solid | Declared / direct dependency |
| dashed | Runtime / optional relationship |
| dotted | Coordinator-mediated / indirect |
| bold | Critical path |

**Color conventions:**

| Color | Meaning |
|-------|---------|
| red (#D32F2F) | Confirmed bug (execution-proven) |
| orange (#FF6F00) | Suspected issue / bypass path |
| green | Spec-correct / healthy |
| blue | Core/kernel layer |

**File size targets:**

| File Type | Line Count | Max Size |
|-----------|-----------|----------|
| overview.dot | 150-250 lines | <15KB |
| detail files | 200-400 lines | — |
| Inline snippets | <50 lines | — |

---

## 6. The General-Purpose DOT Reference Card

The Attractor `dot-reference.md` is 138 lines — a compact quick-reference for pipeline DOT. A general-purpose DOT reference card for the broader ecosystem should follow the same design principles (compact, copy-pasteable, decision-oriented) but cover general DOT authoring.

### 6.1 Proposed Structure

```
# DOT Graph Reference Card

## Quick Start
- digraph G { A -> B }                    // directed
- graph G { A -- B }                      // undirected

## Graph Types
| Type | Edge Operator | Use Case |
|------|--------------|----------|
| digraph | -> | Workflows, dependencies, state machines |
| graph   | -- | Networks, relationships, undirected graphs |

## Node Shapes (Architecture Vocabulary)
[table: shape → meaning — the 12 architecture shapes from Section 5.3]

## Essential Attributes
[compact tables: node attrs, edge attrs, graph attrs — no pipeline-specific ones]

## Layout Engines
[decision tree: DAG? → dot. Undirected <100? → neato. Large? → sfdp. Cyclic? → circo.]

## Cluster Subgraphs
[example showing cluster_ prefix, styling, label]

## 3 Copy-Paste Patterns
1. Simple directed graph (5 lines)
2. Clustered architecture diagram (15 lines)
3. State machine (10 lines)

## Color & Style Reference
[compact table of colors, line styles, fill patterns]

## Rendering Commands
dot -Tsvg input.dot -o output.svg
dot -Tpng input.dot -o output.png
dot -Tjson input.dot -o output.json

## Common Mistakes
[5-line checklist of the top errors]
```

### 6.2 Key Differences from the Attractor Reference Card

| Aspect | Attractor Card | General Card |
|--------|---------------|-------------|
| Shape vocabulary | Pipeline handlers (Mdiamond, box, diamond, component...) | Architecture types (box=module, cylinder=store...) |
| Node attributes | `prompt`, `goal_gate`, `fidelity`, `model_stylesheet` | `label`, `shape`, `color`, `style`, `fillcolor`, `URL` |
| Edge attributes | `condition`, `weight`, `loop_restart` | `label`, `style`, `color`, `arrowhead`, `constraint` |
| Graph attributes | `goal`, `default_fidelity`, `model_stylesheet` | `rankdir`, `splines`, `compound`, `fontname` |
| Patterns | Linear, Conditional Loop, Parallel Fan-Out | Directed graph, Clustered architecture, State machine |
| Decision heuristic | "Pipeline vs Direct Execution" | "Which layout engine?" and "Graph type?" |

---

## 7. Progressive Disclosure for Agents

### 7.1 The Three Layers

DOT knowledge should be layered so agents get exactly what they need:

**Layer 0: Awareness (~30 lines, loaded for every session via behavior context)**

```
"DOT/Graphviz capabilities exist. For diagram work, delegate to dot-graph:dot-author.
For review, delegate to dot-graph:diagram-reviewer. Don't attempt DOT work yourself."
```

This is the thin pointer pattern — the agent knows DOT exists and knows to delegate. No DOT syntax knowledge needed. Token cost: ~30 lines.

**Layer 1: Quick Reference (~140 lines, loaded on demand via skill or inline)**

The general-purpose reference card from Section 6. Enough for an agent to:
- Generate a simple DOT diagram inline
- Validate basic syntax choices
- Choose the right layout engine
- Use the shape vocabulary correctly

This is the "I need to produce a diagram right now and I know roughly what I want" level. Token cost: ~140 lines.

**Layer 2: Deep Expertise (~1500+ lines, loaded only in specialist agent sessions)**

Full documentation covering:
- Complete DOT language specification
- All 60+ node shapes with visual examples
- HTML-like label syntax
- Advanced layout control (rank constraints, splines, compound edges)
- Domain-specific patterns (architecture diagrams, state machines, ERDs, flowcharts)
- Accessibility guidelines
- Rendering optimization

This is the context-sink pattern — loaded only when `dot-graph:dot-author` is spawned as a sub-agent. Token cost: ~1500 lines, but only burns tokens in the specialist sub-session, never in the root session.

### 7.2 The Pipeline Layer (Attractor-Specific Addition)

For agents that need to generate Attractor pipelines, a fourth layer exists:

**Layer 1.5: Pipeline Reference (~140 lines, the existing `dot-reference.md`)**

This is loaded alongside the general reference when a pipeline is being authored. It adds:
- Shape-to-handler mapping (the pipeline vocabulary)
- `prompt`, `goal_gate`, `model_stylesheet` attributes
- Condition expression syntax
- The 3 pipeline patterns (linear, conditional, parallel)
- The pipeline decision heuristic

This layer is the Attractor bundle's context contribution, composed alongside the dot-graph bundle's general awareness.

### 7.3 Knowledge Layering Decision Matrix

| Agent Task | Layer 0 | Layer 1 | Layer 1.5 | Layer 2 |
|-----------|---------|---------|-----------|---------|
| "Create a simple flowchart" | ✓ (delegate) | ✓ (in sub-agent) | — | — |
| "Run a multi-step coding pipeline" | ✓ (delegate to Attractor) | — | ✓ (in Attractor context) | — |
| "Create a complex architecture diagram with HTML labels" | ✓ (delegate) | — | — | ✓ (in dot-author) |
| "Debug why my DOT file doesn't render" | ✓ (delegate) | — | — | ✓ (in dot-author) |
| "Convert this state machine description to DOT" | ✓ (delegate) | ✓ (might be enough) | — | — |

---

## 8. Anti-Patterns and Warnings

### 8.1 DOT Syntax Anti-Patterns (General)

| Anti-Pattern | What Goes Wrong | Fix |
|-------------|----------------|-----|
| **Missing `cluster_` prefix on subgraphs** | Subgraph renders as invisible grouping, not as a bounding box | Always use `subgraph cluster_name { ... }` |
| **Comment-only legends** | Agents cannot read DOT comments — only node labels and attributes | Make legends as real `subgraph cluster_legend` with actual nodes |
| **`splines=ortho` with >30 nodes** | Rendering time explodes exponentially | Use `splines=true` (default) or `splines=polyline` |
| **Node labels with inline paragraphs** | Labels overflow, layout breaks, unreadable when rendered | Keep labels to name + one-liner. Use companion markdown for prose. |
| **More than 80 nodes in one file** | Unreadable rendered output, slow layout | Split into overview.dot + detail files |
| **400+ line single DOT file** | "Forensically thorough but unrenderable." Target 150-250 for top-level, 200-400 for detail. | Break into multiple files with cross-references |
| **Using `->` in undirected graphs** | Parse error (`graph` uses `--`, `digraph` uses `->`) | Check graph type declaration |
| **Unquoted labels with special characters** | Parse errors on `&`, `<`, `>`, newlines | Quote all labels: `label="Auth & Auth"` |
| **Global `node [shape=X]` overriding everything** | All nodes get the same shape — loses semantic vocabulary | Use defaults sparingly; set shape per-node when shapes carry meaning |
| **Inline prose in DOT comments** | Comments are stripped by many parsers and invisible to agents | Move documentation to companion files or node labels |

### 8.2 Pipeline DOT Anti-Patterns (Attractor-Specific)

| Anti-Pattern | What Goes Wrong | Fix |
|-------------|----------------|-----|
| **`goal_gate=true` without `retry_target`** | Gate fails with no recovery path | Always pair with `retry_target` |
| **Using `status=success` instead of `outcome=success`** | Condition never matches — falls through to default edge | Use `outcome=` for pipeline outcomes |
| **`full` fidelity on all nodes** | Every node reuses full conversation history — expensive, slow, context explosion | Use `full` only where session continuity matters; `compact` is the default for a reason |
| **Fan-in (`tripleoctagon`) without fan-out (`component`)** | Fan-in handler expects `parallel.results` in context — crashes | Always pair component → branches → tripleoctagon |
| **Circular dependency without conditional exit** | Infinite loop — the engine walks forever | Every cycle must have a diamond gate with an exit-path edge |
| **>10 nodes in a pipeline** | Cost explosion (each codergen node = full LLM session + tool calls) | Combine related steps; prefer fewer well-prompted nodes |
| **Mixing Attractor and architecture shape vocabularies** | `diamond` means "conditional router" in pipelines but "decision/transform" in architecture docs | Declare which vocabulary is in use (pipeline vs documentation) |
| **`$goal` not expanding** | Missing `graph [goal="..."]` attribute | Ensure the graph has a `goal` attribute or pass `goal` via tool input |
| **Prompt in diamond node** | Prompt is silently ignored — diamond does no LLM work | Move prompt to a preceding box node |

### 8.3 LLM Generation Anti-Patterns

| Anti-Pattern | Why LLMs Do This | How to Prevent |
|-------------|-------------------|---------------|
| **Generating visual styling as content** | LLMs over-index on making things "look nice" | Reference card should emphasize: structure first, styling optional |
| **Inventing shapes** | LLMs hallucinate shapes like `rounded_box` or `process` | Reference card lists ONLY valid shapes; validator flags unknowns |
| **Mixing dialects** | LLM has seen both `node_type` and shape-based pipelines in context | Load ONLY one dialect's reference; Attractor reference card shows only shapes |
| **Over-engineering** | LLM generates a 15-node pipeline for a 3-step task | Pipeline decision heuristic: "No pipeline for < 2 steps. Inline for 2-4. Full for complex." |
| **Duplicating graph attributes on nodes** | LLM copies `llm_model` to every node instead of using stylesheet | Reference card shows stylesheet as the primary mechanism, per-node as override only |
| **Using Python/JS expressions in conditions** | LLMs default to familiar programming syntax | Reference card shows exact condition syntax with examples of what NOT to write |
| **Generating DOT for human viewing only** | LLM optimizes for visual appearance (colors, fonts) but neglects machine-parseability | Dual-purpose principle: "Every DOT file must be both renderable AND parseable" |

### 8.4 Warning Triggers for a General DOT Bundle

A `dot-graph` tool should emit warnings for these patterns:

```
WARNING: Subgraph 'my_group' does not start with 'cluster_' — it won't render
         as a bounding box. Did you mean 'cluster_my_group'?

WARNING: DOT file exceeds 300 lines (actual: 412). Consider splitting into
         overview.dot (150-250 lines) and detail files (200-400 lines each).

WARNING: Node 'big_node' has a label exceeding 80 characters. Long labels
         cause layout problems. Consider using a shorter label with detail
         in a companion document.

WARNING: Graph uses 'splines=ortho' with 45 nodes. Orthogonal routing
         becomes very slow above ~30 nodes. Consider 'splines=true' or
         'splines=polyline'.

WARNING: Found 3 isolated nodes (no incoming or outgoing edges):
         'orphan_a', 'orphan_b', 'orphan_c'. These won't participate in
         any graph traversal.

WARNING: Cluster 'cluster_legend' contains no nodes. Legends should have
         real nodes showing the shape/color vocabulary — agents cannot
         read DOT comments.

INFO:    Detected pipeline-style DOT (has Mdiamond/Msquare shapes).
         Loading Attractor pipeline validation rules...
```

---

## Appendix A: The Two Vocabularies Side-by-Side

This is the most important table for the dot-graph bundle to document, because the **same shape can mean different things** depending on context:

| Shape | Pipeline Meaning (Attractor) | Architecture Meaning (dot-graph) |
|-------|------------------------------|----------------------------------|
| `box` | LLM agent work node (codergen) | Module / package |
| `ellipse` | LLM agent (box alias) | Process / function |
| `diamond` | **Pure routing** (no LLM!) | Decision / transform |
| `hexagon` | Human-in-the-loop gate | Hook / interceptor |
| `component` | Parallel fan-out | Orchestrator / coordinator |
| `folder` | Nested sub-pipeline | Filesystem path |
| `cylinder` | _(not used)_ | State store / database |
| `note` | _(not used)_ | Config file |
| `box3d` | _(not used)_ | External dependency |
| `Mdiamond` | Pipeline start | _(not used)_ |
| `Msquare` | Pipeline exit | _(not used)_ |
| `tripleoctagon` | Parallel fan-in | _(not used)_ |
| `parallelogram` | Tool execution | _(not used)_ |
| `house` | Manager/supervisor loop | _(not used)_ |

**The risk:** An LLM reading a DOT file can't tell which vocabulary is in use. The dot-graph bundle should establish a convention — perhaps a graph-level `vocabulary="pipeline"` or `vocabulary="architecture"` attribute — to disambiguate.

---

## Appendix B: File Inventory — DOT Across the Ecosystem

| Category | Count | Location |
|----------|-------|---------|
| Tutorial pipelines | 10 | `attractor/examples/pipelines/01-*.dot` through `10-*.dot` |
| Practical pipelines | 5 | `attractor/examples/pipelines/practical/*.dot` |
| Pattern templates | 5 | `attractor/examples/patterns/*.dot` |
| Test fixtures | 20+ | `attractor/modules/loop-pipeline/tests/fixtures/*.dot` |
| Resolve pipelines | 4 | `amplifier-resolver-dot-graph/pipelines/*.dot` + `resolve_quick.dot` |
| Architecture diagrams | 4 | `dotfiles/bkrabach/*/overview.dot` + `architecture.dot` |
| Event system specs | 13+ | Created in session `c95ce204` (not committed as files) |
| Recipe visualization | 1 | `recipe-testing/bundle-validation-recipes.dot` |
| Native Rust examples | 9 | `attractor-native/examples/*.dot` + `pipelines/*.dot` |
| **Total** | **70+** | Across the full Amplifier ecosystem |

---

## Appendix C: Key Quotes That Should Inform Bundle Design

> *"DOT diagrams are discovery tools, not just documentation."*
> — The act of creating a DOT diagram forces commitment to specific nodes and edges, preventing vague analysis.

> *"We don't need a new handler — the composition of hexagon + box + diamond + loop_restart edges gives us conversational loops within pure DOT."*
> — Complex behaviors emerge from composing simple primitives.

> *"Hand-maintained DOT files won't be maintained. Generate from source."*
> — Three independent experts rejected hand-maintained DOT conventions. The bundle should emphasize generated DOT over hand-maintained DOT.

> *"The 252-line synthesized diagram is qualitatively different from any Wave 1 diagram because it incorporates corrections."*
> — Multi-pass synthesis produces better DOT than single-pass generation.

> *"The gem was the 158-line state machine diagram — renders beautifully, agent could consume it in minimal tokens. The walls were the 411 and 587 line outputs — forensically thorough but would never render as a readable image."*
> — The 150-250 line sweet spot is empirically validated.

> *"The cancellation gap was invisible because no diagram showed all exit paths."*
> — DOT diagrams reveal structural completeness problems that prose descriptions miss.

> *"A DOT pipeline foundry that produces DOT pipelines. Beautiful recursion."*
> — DOT can be both the tool and the output — a self-referential capability the bundle should embrace.

---

## Appendix D: Recommendations for the Bundle

Based on this entire analysis, here are the concrete recommendations:

### Must-Have for v1

1. **General-purpose DOT reference card** (~140 lines) with the architecture vocabulary
2. **`dot-author` agent** that knows DOT syntax, patterns, layout engines, and best practices
3. **`diagram-reviewer` agent** that evaluates DOT quality against standards
4. **DOT validation tool** — syntax (via Graphviz), structure (via NetworkX), quality (line count, cluster naming, legend presence)
5. **DOT rendering tool** — SVG, PNG, PDF output via Graphviz CLI
6. **Thin awareness context** (~30 lines) for behavior injection

### Should-Have for v2

7. **Domain-specific vocabulary extension points** — mechanism for Attractor and others to register their shape vocabularies
8. **Schema-based validation** — validate DOT against a declared shape/attribute schema
9. **Cross-dialect warnings** — detect `llm_prompt`, `node_type`, `is_codergen` in contexts where `prompt`, `shape`, defaults are expected
10. **Recipe-to-DOT visualization** — generate DOT from YAML recipe structures (user explicitly requested this)

### Nice-to-Have for v3

11. **DOT diff tool** — structural comparison between two DOT files (added/removed/changed nodes and edges)
12. **Progressive DOT generation** — generate overview.dot first, then detail files on demand
13. **DOT-from-source generation** — introspect Python/Rust/TS source to generate architecture DOT
14. **Interactive DOT exploration** — TUI or web-based interactive graph viewer

### What NOT to Build

- **Don't generalize `model_stylesheet`** — it's tightly coupled to pipeline model routing. The _pattern_ is documented for learning, but the implementation stays in Attractor.
- **Don't generalize pipeline validation rules** — start/exit node checks, condition syntax, goal gates are Attractor-specific.
- **Don't try to unify the shape vocabularies** — explicitly document them as separate contexts. Disambiguation is better than forced unification.
- **Don't hand-maintain DOT documentation files** — follow the expert consensus and prefer generated DOT where possible.
