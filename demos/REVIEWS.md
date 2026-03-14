# Demo DOT Files — Diagram Reviewer Verdicts

Reviewed by: `dot-graph:diagram-reviewer` agent (5-level checklist: Syntax, Structure, Quality, Style, Reconciliation)
Date: 2026-03-14

Reviews 01, 03b, 04b are post-fix re-reviews. Earlier reviews for 02, 03a, 04a, 05, 06 remain in prior session context.

---

## 01-bundle-architecture.dot

## Diagram Review

**File:** 01-bundle-architecture.dot (post-fix: context: labels differentiated, color key added to legend)
**Type:** digraph
**Size:** 210 lines, 21 content nodes (28 total including legend), ~32 edges

---

### Strengths

- **Graph-level attributes are complete**: `rankdir=TB`, `compound=true`, `fontname`, `fontsize`, `bgcolor`, `label`, `labelloc`, `labeljust`, `pad`, `nodesep`, `ranksep` — the layout engine has full context.
- **HTML labels used throughout**: All structured content uses `<< >>` HTML labels with bold titles and `POINT-SIZE` sub-text. No `shape=record` usage anywhere.
- **All node IDs use snake_case**: `bundle_md`, `dot_author`, `diagram_reviewer`, `tool_module`, `dot_validate`, `sk_syntax`, `ctx_awareness` — consistent and stable.
- **No orphan nodes**: Every content node participates in at least one edge. All 21 content nodes are reachable from `bundle_md`.
- **Legend covers all shape types AND color tiers**: 7 shape entries + 4 color-tier plaintext entries. Post-fix addition of color key makes the diagram fully self-contained.
- **Context edge labels now differentiated**: `"context: awareness"` and `"context: instructions"` replace the duplicate `"context:"` labels — readers can trace which context file each edge references.
- **Nested cluster hierarchy accurate**: `cluster_tier1` containing `cluster_skills`, `cluster_docs`, and `cluster_context` mirrors the 3-tier architecture correctly.
- **No `pos=` attributes**: Layout fully delegated to the engine.

---

### Warnings

- **All structural relationship types share `style=dashed`**: The diagram uses dashed edges for four semantically distinct relationships — `"includes"` (bundle wiring), `"tools:"` (module registration), `"context: awareness/instructions"` (context injection), and `"loads on demand"` (agent skill access). While edge colour partially differentiates them (`#E65100` for agents, `#0097A7` for context, `#90CAF9` for skill loads), the shape vocabulary of the edge itself carries no differentiation. Per Level 4 standards: solid = data flow, dashed = optional/conditional, bold = critical path. Using `style=dotted` for runtime `"loads on demand"` edges vs `style=dashed` for compile-time `"includes"` wiring would sharpen the vocabulary.

---

### Errors

None.

Graph declaration is valid. All braces and brackets are balanced. All edges correctly use `->`. HTML labels are syntactically correct throughout.

---

### Reconciliation Notes

- **No hub nodes with 10+ edges**: `behavior` is the most connected node with 6 edges (3 in, 3 out for includes/tools/context). Well below the 10-edge SPOF threshold.
- **No long sequential chains**: The longest trace is 4 nodes (`bundle_md → behavior → dot_author → sk_syntax`). No pipeline bottleneck concern.
- **`cluster_legend` structurally isolated**: Nodes connected only via `style=invis` edges — the standard legend idiom. Not an integration gap.
- **`dir=none` edges inside a digraph**: Used for `tool_module → dot_validate/render/setup/analyze` to model "is composed of" membership. Intentional and semantically correct — avoids implying directed data flow where none exists.
- **No cycles detected**: The graph is a DAG. No undocumented feedback loops.

---

**Verdict: WARN**
Rationale: The diagram is syntactically valid, structurally sound, and meets all hard quality requirements (legend present with color key, differentiated context: labels, snake_case IDs, no `shape=record`, no orphans, no `pos=`). One style inconsistency remains: all structural relationship types share `style=dashed` without edge-style differentiation between compile-time wiring and runtime skill loads.

---

## 03b-reconciliation-after.dot

## Diagram Review

**File:** 03b-reconciliation-after.dot (post-fix: ext_idp moved outside clusters, cache self-loop added, edge-style legend extended)
**Type:** digraph
**Size:** 240 lines, 18 content nodes (22 total including legend), ~22 edges

---

### Strengths

- **All three WARN items from the previous review are resolved**:
  1. `ext_idp` is now placed outside all clusters — its external, uncontrolled nature is immediately visually apparent. No longer normalised within the Ingestion cluster boundary.
  2. The ambiguous `cache → order_api` back-edge (which implied reverse data flow) is replaced with a `cache → cache` self-loop labelled `"write-only / no readers"`. This makes the dead-end unambiguous without implying consumption.
  3. The legend now includes four edge-style semantic entries: `"─── Live call / data flow"`, `"- - Dead / conditional / delegated"`, `"···· Reference / annotation"`, `"━━━ Blocking / critical path"` — readers can now look up any edge style in the legend.
- **Findings summary table is outstanding**: The HTML table in `cluster_findings` documents all 7 issues with Finding + Impact columns. This is exemplary reconciliation artifact design.
- **Dead code is visually encoded on multiple channels**: `retry_logic` uses `style="dashed,filled"`, grey fill, grey font, AND an annotation label `"should call (never does)"`. `analytics_svc` + `reporting_db` use the same treatment. Multi-channel encoding ensures the dead status is never ambiguous.
- **Severity levels are encoded and legended**: Green (verified), orange (differs from belief), red (missing/wrong), grey-dashed (dead/orphaned) — all documented in the node-type legend.
- **HTML labels used throughout**: No `shape=record`. Structured content on all complex nodes uses `<< >>` HTML with POINT-SIZE sub-labels.
- **Graph-level attributes complete**: `rankdir=LR`, `compound=true`, `fontname`, `fontsize`, `bgcolor`, `label`, `labelloc`, `pad`, `nodesep`, `ranksep`.

---

### Warnings

None.

---

### Errors

None.

Graph declaration is valid. All braces and brackets are balanced. `ext_idp` placement outside clusters is syntactically correct — standalone nodes in `digraph` scope are fully valid. The self-loop `cache -> cache` is valid DOT syntax. HTML labels are syntactically correct.

---

### Reconciliation Notes

- **`payment_svc` remains the reconciliation nexus** (4 edges: inbound from `pricing_engine`; outbound to `order_db`, `event_queue`, `findings`; dashed to `retry_logic`). Four of the 7 findings originate at or pass through `payment_svc`. This is the structural centre of the investigation and the highest-priority remediation target.
- **`retry_logic` dead module**: The `"should call (never does)"` dashed edge from `payment_svc` documents original intent AND the gap simultaneously. System implication: transient payment failures are silently dropped — the highest-severity operational finding.
- **`event_queue` synchronous blocking call**: The `penwidth=2` edge `payment_svc → event_queue [label="BLOCKING call"]` combined with `event_queue → fulfilment_svc [label="triggers\n(synchronous)"]` shows a two-hop blocking chain on the critical payment thread.
- **`cache` self-loop documents 100% cold miss**: The self-loop `cache → cache [label="write-only\nno readers"]` cleanly documents the resource leak without implying a reverse consumer. This is a structurally superior representation compared to the prior back-edge.
- **`ext_idp` isolation confirms undocumented dependency**: Placed outside all clusters, `ext_idp` now reads as a foreign body — visually consistent with Finding #4 ("undocumented IdP dep / hidden outage risk").
- **`cluster_analytics` remains intentionally isolated**: Zero cross-cluster edges to the live graph. The `"removed in commit a3f2c"` annotation on `analytics_svc` provides forensic depth for the disconnection.

---

**Verdict: PASS**
Rationale: All three WARN items from the prior review have been resolved. The diagram is syntactically valid, structurally sound, meets all hard quality requirements, and now achieves the highest reconciliation signal of the demo set — every visual element (node colour, edge style, cluster placement, label annotation) encodes a specific finding.

---

## 04b-multiscale-detail.dot

## Diagram Review

**File:** 04b-multiscale-detail.dot (unchanged — this review confirms prior PASS verdict)
**Type:** digraph
**Size:** 243 lines, 22 content nodes (27 total including legend), ~35 edges

---

### Strengths

- **Graph-level attributes are complete**: `rankdir=LR`, `compound=true`, `fontname`, `fontsize`, `bgcolor`, `label`, `labelloc`, `labeljust`, `pad`, `nodesep`, `ranksep`.
- **Multi-scale navigation intent is explicit**: Header label reads `"Zoom-in: cluster_gateway from overview · Full internal structure"` — a reader immediately knows where this diagram sits in the zoom hierarchy.
- **Boundary clusters correctly mark context**: `cluster_external` (sources) and `cluster_downstream` (sinks) use `style="rounded,dashed"` with grey fill to visually distinguish them from the expanded internal structure. This is the correct multi-scale navigation idiom.
- **Shape vocabulary is semantically precise**: `diamond` for all decision gates (`waf`, `token_type_gate`), `cylinder` for all data stores (`auth_cache`, `jwks_store`, `policy_store`), `box` for services. Shapes carry meaning throughout.
- **Error paths are present and distinct**: `auth_denied` (401/403) and `rate_limited` (429) are red-filled nodes reached by red-styled dashed edges. Error/rejection paths are shown from every decision gate.
- **Auth cache hit path documented**: `auth_cache → authz_engine [label="hit: skip validate"]` + write-back edges `jwt_validator → auth_cache` and `apikey_validator → auth_cache` complete the cache lifecycle. No orphan cache patterns.
- **Legend covers all 5 shape/colour types**: `Service`, `Decision gate`, `Data store`, `Boundary`, `Error response` — all rendered shapes are explained.
- **HTML labels throughout**: Rich sub-labels on complex nodes (implementation details: Redis TTL, JWKS refresh interval, OPA bundle config) add operational value without cluttering the layout.
- **No orphan nodes**: All 22 content nodes participate in at least one edge.
- **No `pos=` attributes**: Layout fully delegated to the engine.

---

### Warnings

None.

---

### Errors

None.

---

### Reconciliation Notes

- **`token_type_gate` diamond is the auth pipeline's structural bottleneck**: All three auth paths (JWT, API-key, mTLS) fan out from this single decision node. If `token_type_gate` fails (e.g. header parsing error), all authentication fails simultaneously. This is the single narrowest point in the auth funnel — worth an abstraction or redundancy analysis.
- **`auth_cache` creates a shortcut path that bypasses the validator pipeline**: The edge `auth_cache → authz_engine [label="hit: skip validate"]` means a cache hit completely bypasses `token_type_gate`, all three validators, and JWKS lookup. System implication: any token revocation before cache TTL expiry (5 min) would not be caught — a security surface worth documenting in operational runbooks.
- **`waf` is a diamond (decision gate) but acts as a sequential processing step**: The WAF evaluates requests and either allows or blocks — this is correct use of diamond for a gate. But WAF also modifies requests (e.g., sanitises inputs) in real deployments. The diagram shows only the block/allow path, not any request mutation path. This is a deliberate simplification worth noting in the diagram if WAF mutation is in scope.
- **`partner_api` path reaches `mtls_validator` but no API-key or JWT path**: This is architecturally correct if partner auth is exclusively mTLS, but represents an integration constraint that should be verified — if a partner ever rotates to API-key auth, the gateway has no path to support it without a new `token_type_gate` branch.

---

**Verdict: PASS**
Rationale: The diagram is syntactically valid, structurally complete, meets all quality standards (legend, snake_case IDs, no `shape=record`, no orphans, no `pos=`), and demonstrates exemplary multi-scale navigation design. All shape, color, and edge-style choices are semantically consistent. The Reconciliation Notes surface meaningful operational concerns worth investigation.

---
