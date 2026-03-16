# amplifier-bundle-dot-graph — Demo Artifacts

Six demonstrations of DOT/Graphviz capabilities within the Amplifier ecosystem.
Each demo is a standalone DOT file rendered to PNG and SVG, reviewed by `dot-graph:diagram-reviewer`.

---

## Quick Reference

| # | File | Demonstrates | Lines | Reviewer |
|---|------|-------------|-------|----------|
| 1 | [01-bundle-architecture](#demo-1-bundle-architecture) | DOT as architecture documentation | 210 | WARN |
| 2 | [02-use-cases](#demo-2-the-7-use-cases) | DOT as dense representation | 190 | WARN |
| 3a | [03a-reconciliation-before](#demo-3-reconciliation-beforeafter) | DOT as reconciliation forcing function (belief state) | 160 | WARN |
| 3b | [03b-reconciliation-after](#demo-3-reconciliation-beforeafter) | DOT as reconciliation forcing function (reality) | 240 | **PASS** |
| 4a | [04a-multiscale-overview](#demo-4-multi-scale-navigation) | DOT as multi-scale navigation (overview) | 186 | WARN |
| 4b | [04b-multiscale-detail](#demo-4-multi-scale-navigation) | DOT as multi-scale navigation (detail) | 243 | **PASS** |
| 5 | [05-recipe-visualization](#demo-5-recipe-visualization) | DOT as recipe visualization | 244 | WARN |
| 6 | [06-ecosystem-composition](#demo-6-ecosystem-composition) | DOT as bundle composition model | 241 | WARN |

> Reviewer verdicts are WARN (functional, passes all hard quality gates, minor style issues noted) or **PASS** (no issues).
> All diagrams render correctly and serve their demonstrative purpose. Full verdicts in [REVIEWS.md](REVIEWS.md).
> Demos 01 and 03b received post-review fixes; 03b was upgraded from WARN → **PASS** after fixes.

---

## Demo 1: Bundle Architecture

**File:** `01-bundle-architecture.dot` · `01-bundle-architecture.png` · `01-bundle-architecture.svg`

**Demonstrates:** DOT as architecture documentation — self-documenting the very bundle that provides DOT capabilities.

**What it shows:**

The three-tier architecture of `amplifier-bundle-dot-graph`:

| Tier | Contents | Color |
|------|---------|-------|
| Tier 1 — Knowledge Layer | 5 skills, 5 docs, 2 context files | Blue |
| Tier 2 — Validation & Rendering | `tool-dot-graph` Python package, 4 tool functions | Green |
| Tier 3 — Graph Intelligence | `dot_analyze` (NetworkX-backed) | Dark green |

Also shows the `behaviors/dot-graph.yaml` wiring unit, the two agents (`dot-author`, `diagram-reviewer`), and the `bundle.md` manifest entry point.

**Design decisions:**
- `rankdir=TB` — natural hierarchy from manifest → behavior → agents/tools → knowledge
- Color-coded tiers (blue = knowledge, green = tools, orange = agents, grey = scaffolding)
- `shape=component` for the behavior unit, `shape=tab` for file artifacts, `shape=note` for docs/context
- Dashed edges throughout for "includes/references" relationships (non-data-flow)
- Color key added to legend (post-review fix): blue = Tier 1 Knowledge, green = Tier 2 Tools, orange = Agents, grey = Behavior/config
- Context edge labels differentiated (post-review fix): `"context: awareness"` vs `"context: instructions"`

**Reviewer verdict:** WARN — structurally sound, all hard quality gates pass. Remaining minor warning: all structural relationship types (includes, tools, context, skill loads) share `style=dashed` without edge-style differentiation between compile-time wiring and runtime skill loads.

---

## Demo 2: The 7 Use Cases

**File:** `02-use-cases.dot` · `02-use-cases.png` · `02-use-cases.svg`

**Demonstrates:** DOT as dense representation — encoding a complete conceptual taxonomy in ~190 lines.

**What it shows:**

A hub-and-spoke diagram with **DOT Language** as the central node and the 7 primary use cases of DOT in the Amplifier ecosystem:

1. **Dense Representation** — full system in <300 lines
2. **Reconciliation Forcing Function** — drawing makes claims; gaps reveal bugs
3. **Multi-Scale Navigation** — subgraph zoom in/out
4. **Analysis Substrate** — NetworkX-backed programmatic queries
5. **Multi-Modal Bridge** — same source → PNG/SVG/JSON/text
6. **Workflow Visualization** — DAG pattern for processes and pipelines
7. **Investigation Artifact** — persistent, git-trackable findings

Cross-cutting edges show how use cases interconnect (e.g., Dense Representation → Multi-Scale Navigation → Analysis Substrate → Reconciliation).

A `cluster_bundle_note` shows which capabilities the dot-graph bundle provides for each use case.

**Design decisions:**
- `dot_medium` as central hub with 7 spokes; `constraint=false` on cross-cutting edges prevents layout distortion
- Note nodes (`uc*_ex`) show real-world examples for each use case
- `lhead=cluster_bundle_note` for the bundle capability node

**Reviewer verdict:** WARN — structurally and syntactically correct. Minor warnings: global edge colour could differentiate spoke types; note that `rankdir=TB` produces a layered layout rather than radial (expected `dot` engine behaviour).

---

## Demo 3: Reconciliation Before/After

**Files:**
- `03a-reconciliation-before.dot` · `03a-reconciliation-before.png` · `03a-reconciliation-before.svg`
- `03b-reconciliation-after.dot` · `03b-reconciliation-after.png` · `03b-reconciliation-after.svg`

**Demonstrates:** DOT as reconciliation forcing function — the before/after investigation workflow from the `dot-as-analysis` skill.

**Scenario:** A developer's mental model of a cloud order-processing service versus the actual implementation.

### 3a — Before (Belief State)

Shows what the developer *believed* the system does:
- Retry logic on payment failures (believed: 3 attempts)
- Async event queue to analytics and fulfilment
- Cache warming for orders
- Analytics cluster receiving events

All unverified assumptions are annotated with `(believed: ...)` in node labels. The retry cycle is shown explicitly but not flagged.

### 3b — After (Reality Surfaced)

Shows what reconciliation with the actual code revealed — **7 findings**:

| Status | Finding | Impact |
|--------|---------|--------|
| ✗ Error | `payment_svc`: no retry logic | Silent transaction drops |
| ✗ Error | `event_queue`: synchronous, not async | Blocks payment thread |
| ✗ Error | `cache`: write-only, never read | Wasted CPU + memory |
| ⚠ Warn | `auth_svc`: undocumented external IdP dependency | Hidden outage risk |
| ⚠ Warn | `notification_svc`: SMS path removed silently | Broken customer promise |
| ☠ Dead | `retry_logic` module: dead code | Maintenance confusion |
| ☠ Dead | Analytics cluster: completely disconnected | Stale reporting data |

Color coding: green = verified correct, orange = differs from belief, red = missing/wrong, grey/dashed = dead code.

**Post-review fixes applied to 03b:**
- `ext_idp` moved **outside** all clusters — emphasises its uncontrolled external nature (Finding #4)
- Ambiguous `cache → order_api` back-edge replaced with `cache → cache` self-loop labelled `"write-only / no readers"`
- Legend extended with four edge-style semantic entries (solid/dashed/dotted/bold)

**Reviewer verdicts:**
- 03a: WARN — belief-state diagram appropriately missing dead-code annotations; dashed edge overloading noted
- 03b: **PASS** — all prior WARN items resolved. Every visual element (node colour, edge style, cluster placement, label) encodes a specific reconciliation finding.

---

## Demo 4: Multi-Scale Navigation

**Files:**
- `04a-multiscale-overview.dot` · `04a-multiscale-overview.png` · `04a-multiscale-overview.svg`
- `04b-multiscale-detail.dot` · `04b-multiscale-detail.png` · `04b-multiscale-detail.svg`

**Demonstrates:** DOT as multi-scale navigation — the same system expressed at overview and detail granularity.

**System:** A fictional CloudSaaS platform.

### 4a — Overview (Zoom Out)

5 subsystem clusters with key cross-system edges only:

| Subsystem | Contents |
|-----------|---------|
| Gateway & Auth | API Gateway (boundary node) |
| Core Platform | User Service, Tenant Service, Feature Flags |
| Product Domain | Catalog, Orders, Inventory |
| Data Layer | Primary DB, Read Replicas, Cache, Event Bus |
| Observability | Metrics, Tracing, Log Aggregation |

Labels reference the detail file: `see: 04b-multiscale-detail.dot`

### 4b — Detail (Zoom In: Gateway & Auth)

Full internal pipeline of the Gateway & Auth subsystem — 8 clusters, 22 content nodes:

```
TLS Termination → WAF → Rate Limiter → Token Extraction →
  Token Type Gate ─┬─ JWT Validator ─────┐
                   ├─ API-Key Validator ──┼─ OPA AuthZ Engine → Route Table → Request Enricher → Downstream
                   └─ mTLS Validator ─────┘
```

Boundary clusters (`cluster_external`, `cluster_downstream`) use `style="rounded,dashed"` to show they're "from overview" — a clean multi-scale navigation technique.

**Design decisions:**
- Overview uses `rankdir=TB`; detail uses `rankdir=LR` for pipeline readability
- Decision diamonds for WAF and Token Type gate
- Auth cache shortcut path explicitly modeled (bypasses validators on cache hit)
- Error paths in red throughout detail diagram

**Reviewer verdicts:**
- 04a: WARN — legend documents edge semantics as text only (no visual edge demonstration); external actors are shape-identical to internal services
- 04b: **PASS** — accurate, complete, well-structured, and self-explanatory. Reconciliation notes surface auth cache bypass security surface and token-type gate as structural bottleneck.

---

## Demo 5: Recipe Visualization

**File:** `05-recipe-visualization.dot` · `05-recipe-visualization.png` · `05-recipe-visualization.svg`

**Demonstrates:** DOT as recipe visualization — making multi-step agent workflows comprehensible as graphs.

**What it shows:**

Three related recipes forming the Amplifier Foundation bundle validation family:

| Recipe | Role |
|--------|------|
| `validate-bundle.yaml` v2.0.0 | Multi-bundle orchestrator (foreach loop) |
| `validate-single-bundle.yaml` v2.0.0 | Per-bundle worker (called as sub-recipe) |
| `validate-bundle-repo.yaml` v3.2.0 | Full repo structural validator (independent) |

Shape vocabulary:
- **Hexagon** — `foreach` loops
- **Diamond** — conditional gates (`has_pyproject?`, `requires_llm_analysis?`)
- **Box (blue)** — bash steps
- **Box (green)** — agent steps (LLM)
- **Box (grey)** — default/init steps
- **Box (dark green)** — final output steps

The sub-recipe call edge (`vb_foreach → vs_trace [lhead=cluster_validate_single]`) correctly uses `compound=true` + `lhead` to point at the cluster boundary.

**Renderer:** Use `dot -Tpng -Gdpi=150 -Gsize="20,30"` for full-size PNG (large diagram).

**Reviewer verdict:** WARN — syntactically clean, no orphans. Warnings: Recipe 3 is independent by design but could include a cross-reference annotation edge to Recipes 1/2; ambiguous parallel `"true"` labels on `vr_llm_gate`; sub-recipe call edge style not documented in legend.

---

## Demo 6: Ecosystem Composition

**File:** `06-ecosystem-composition.dot` · `06-ecosystem-composition.png` · `06-ecosystem-composition.svg`

**Demonstrates:** DOT as bundle composition model — showing how the dot-graph behavior propagates capabilities across the Amplifier ecosystem.

**What it shows:**

Four clusters:

1. **amplifier-bundle-dot-graph** (source): bundle.md → behavior → capabilities (agents, tools, context, skills)

2. **Consuming Bundles**: Three bundles that include `dot-graph:behaviors/dot-graph`:
   - `amplifier-foundation` (core platform)
   - `dot-graph-bundle` (development environment — this repo)
   - `your-team-bundle` (hypothetical adopter shown with dashed border)

3. **Context Sink Pattern**: Shows how `dot-awareness.md` propagates to every session that includes the behavior — root behavior → context file → agent sessions (skills loaded on demand)

4. **Adoption Path**: 4-step journey from adding the bundle include to running reviews (connected to `your-team-bundle` via dotted edge)

**The key structural insight:** `dg_behavior` is a hub node with ~10 edges — intentional architecture that exposes it as a structural concentration point. Any change to `dot-graph.yaml` propagates to all consuming bundles simultaneously.

**Design decisions:**
- `shape=tab` for bundle manifests, `shape=component` for behaviors, `shape=ellipse` for tool functions
- Dashed borders for hypothetical (`your-team-bundle`) and "from overview" contexts
- `lhead=cluster_dg_behavior` for composition edges to cluster boundary
- Adoption path cluster connected to main graph via dotted cross-reference edge

**Reviewer verdict:** WARN — structurally sound. Minor warnings: edge style legend could distinguish between hard include (solid), capability propagation (dashed), and cross-reference annotation (dotted) more explicitly.

---

## File Structure

```
demos/
├── README.md                         ← This file
├── REVIEWS.md                        ← Diagram-reviewer verdicts (01, 03b, 04b post-fix)
│
├── 01-bundle-architecture.dot        ← DOT source (210 lines, post-fix)
├── 01-bundle-architecture.png        ← Rendered PNG (150 dpi)
├── 01-bundle-architecture.svg        ← Rendered SVG
│
├── 02-use-cases.dot                  ← DOT source (190 lines)
├── 02-use-cases.png
├── 02-use-cases.svg
│
├── 03a-reconciliation-before.dot     ← DOT source (160 lines)
├── 03a-reconciliation-before.png
├── 03a-reconciliation-before.svg
├── 03b-reconciliation-after.dot      ← DOT source (240 lines, post-fix) — PASS verdict
├── 03b-reconciliation-after.png
├── 03b-reconciliation-after.svg
│
├── 04a-multiscale-overview.dot       ← DOT source (186 lines)
├── 04a-multiscale-overview.png
├── 04a-multiscale-overview.svg
├── 04b-multiscale-detail.dot         ← DOT source (243 lines) — PASS verdict
├── 04b-multiscale-detail.png
├── 04b-multiscale-detail.svg
│
├── 05-recipe-visualization.dot       ← DOT source (244 lines)
├── 05-recipe-visualization.png       ← Rendered at -Gdpi=150 -Gsize="20,30"
├── 05-recipe-visualization.svg       ← Rendered SVG
│
├── 06-ecosystem-composition.dot      ← DOT source (241 lines)
├── 06-ecosystem-composition.png
└── 06-ecosystem-composition.svg
```

---

## Rendering Commands

All files use the standard `dot` layout engine. Reproduce any render:

```bash
# Standard rendering (PNG at 150dpi + SVG)
dot -Tpng -Gdpi=150 01-bundle-architecture.dot -o 01-bundle-architecture.png
dot -Tsvg 01-bundle-architecture.dot -o 01-bundle-architecture.svg

# Recipe visualization (large diagram — needs size hints)
dot -Tpng -Gdpi=150 -Gsize="20,30" 05-recipe-visualization.dot -o 05-recipe-visualization.png
dot -Tsvg 05-recipe-visualization.dot -o 05-recipe-visualization.svg

# Re-render all files at once
for f in *.dot; do
  base="${f%.dot}"
  if [[ "$f" == "05-recipe-visualization.dot" ]]; then
    dot -Tpng -Gdpi=150 -Gsize="20,30" "$f" -o "${base}.png"
  else
    dot -Tpng -Gdpi=150 "$f" -o "${base}.png"
  fi
  dot -Tsvg "$f" -o "${base}.svg"
done
```

---

## Review Process

All DOT files were reviewed by `dot-graph:diagram-reviewer` using the 5-level checklist:

| Level | Checks |
|-------|--------|
| 1 — Syntax | Valid DOT, balanced braces, correct edge operators |
| 2 — Structure | No orphan nodes, proper cluster prefixes, traceable paths |
| 3 — Quality | Line count targets, legend present, snake_case IDs, no `shape=record` |
| 4 — Style | Semantic shapes, consistent edge styles, purposeful colors |
| 5 — Reconciliation | Hub nodes, isolated clusters, long chains, undocumented cycles |

Reviews were executed by delegating each file to the `dot-graph:diagram-reviewer` agent.
Demos 01 and 03b received post-review fixes. 03b was upgraded from WARN → **PASS** after all three
WARN items were resolved (ext_idp placement, cache edge semantics, edge-style legend).
Full structured verdicts for 01, 03b, and 04b are in [REVIEWS.md](REVIEWS.md).

---

## Authoring Notes

All DOT files were authored following the quality standards documented in `docs/DOT-QUALITY-STANDARDS.md`:

- **Line count targets:** overview 100–200 lines, detail 150–300 lines
- **Legend required** for >20 nodes (all demos meet this)
- **Cluster subgraphs** for logical groupings of 3+ related nodes
- **Consistent node IDs** using `snake_case`
- **No `shape=record`** — HTML labels used throughout
- **No hardcoded positions** — layout left to the engine
- **Graph-level attributes** — `fontname`, `rankdir`, `compound` set on all diagrams
