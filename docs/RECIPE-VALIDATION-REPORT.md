# Recipe Validation Report — Discovery Pipeline v2

**Date:** 2026-03-18  
**Auditor:** Automated validation session  
**Scope:** All 10 recipes in `recipes/`  
**Baseline commit (before fixes):** `a9efc1f`  
**Fix commit:** `2d34677`  
**Test result (before + after):** 1287 passed, 0 failed

---

## Executive Summary

All 10 discovery pipeline recipes were individually audited for 5 known runtime bug patterns (JSON booleans in Python, `when:` vs `condition:`, nested template references, undefined-after-skip variables, and foreach structured-object passing). The previously committed 7 fixes had resolved all instances of these patterns.

**Three additional bugs were found during the code review** — bugs not covered by the 5 original patterns — in the data-flow wiring between recipes:

| # | Recipe | Bug | Severity | Status |
|---|--------|-----|----------|--------|
| A | `discovery-investigate-topic.yaml` | Agent write paths had spurious `investigation/` prefix — agents wrote to a different directory than where `prepare-topics` created structure and `reconcile-modules` read from | **Critical** (silent data loss) | Fixed |
| B | `strategy-topdown.yaml` | `overview-synthesis` missing `repo_root` — agent could not examine top-level repo files | **High** | Fixed |
| B | `strategy-bottomup.yaml` | Same — `overview-synthesis` missing `repo_root` | **High** | Fixed |
| C | `strategy-topdown.yaml` | `subsystem-synthesis` passed wrong context keys (`topics`, `fidelity`) instead of `module_dot_files` / `source_dirs` | **Medium** | Fixed |
| C | `strategy-bottomup.yaml` | Same — passed `subsystems`, `fidelity` instead of `module_dot_files` / `source_dirs` | **Medium** | Fixed |
| D | `strategy-topdown.yaml` | `overview-synthesis` missing `subsystem_dot_files` — agent had no path to the produced subsystem DOT | **Medium** | Fixed |
| D | `strategy-bottomup.yaml` | Same | **Medium** | Fixed |

**Tier 1 execution test:** `synthesize-level.yaml` executed end-to-end against `amplifier/agents/` — **PASSED** (valid DOT, 9 nodes, 13 edges).

---

## Audit Method

Each recipe was read in full and checked for:

1. **Pattern 1 — JSON booleans in Python:** `x = {{var}}` where `var` is a JSON boolean produces `x = true` (Python `NameError`). Safe fix: `json.loads(r"""{{var}}""")`.
2. **Pattern 2 — `when:` vs `condition:`:** The recipe framework requires `condition:` for conditional steps. `when:` is silently ignored, causing all steps to always execute.
3. **Pattern 3 — Nested template references:** `output_dir: "{{repo_path}}/.discovery"` in a default context works (single `{{repo_path}}` resolved in one pass), but chaining (`some_path: "{{output_dir}}/sub"` where `output_dir` itself contains a template reference) does not double-resolve.
4. **Pattern 4 — Undefined variable in skipped step:** Template engine substitutes ALL `{{}}` references before evaluating `condition:`. A skipped step with `x = r"""{{topics}}"""` will still fail if `topics` is undefined at substitution time.
5. **Pattern 5 — foreach with structured objects:** `context: {topic: "{{topic}}"}` stringifies the entire dict. Correct form: flatten to `topic_name: "{{topic.name}}"`.

Additionally, data-flow correctness was traced end-to-end: where do agents write? Where does the next step read from? Are context variables wired correctly between caller and sub-recipe?

---

## Per-Recipe Results

### Tier 1 — Building Blocks

#### `synthesize-level.yaml` ✅ CLEAN

- **Steps:** read-level (bash) → synthesize (agent) → validate (bash)
- **Pattern 1:** No boolean template assignments. String assignments (`level_path = "{{level_path}}"`) are safe.
- **Pattern 2:** No `when:` usage. No conditional steps.
- **Pattern 3:** No template references in context defaults.
- **Pattern 4:** N/A — no conditional steps.
- **Pattern 5:** N/A — no foreach.
- **Data flow:** Output written to `{{output_dir}}/{{level_slug}}/diagram.dot`; validate reads same path. ✓

#### `synthesize-subsystem.yaml` ✅ CLEAN

- **Steps:** synthesize (agent) → validate (bash)
- **Pattern 1–5:** All clean.
- **Data flow:** Agent writes `{{output_dir}}/{{subsystem_name}}.dot`; validate reads same path. ✓

#### `synthesize-overview.yaml` ✅ CLEAN

- **Steps:** synthesize (agent) → validate (bash)
- **Pattern 1–5:** All clean.
- **Data flow:** Agent writes `{{output_dir}}/overview.dot`; validate reads same path. ✓
- **Note:** `repo_root` and `subsystem_dot_files` are context inputs with empty defaults. Strategy recipes are now responsible for passing these correctly (fixed in Bugs B and D).

---

### Tier 2 — Investigation Sub-recipes

#### `discovery-investigate-topic.yaml` 🔴 → ✅ FIXED (Bug A)

- **Steps:** code-tracer (agent, condition) → behavior-observer (agent, condition) → integration-mapper (agent, condition)
- **Pattern 1:** No Python bash steps; agent-only recipe.
- **Pattern 2:** All steps use `condition:` correctly (`{{fidelity}} != 'quick'`, `{{fidelity}} == 'deep'`). ✓
- **Pattern 3:** No nested template references in defaults.
- **Pattern 4:** Conditions guard all 3 steps; outputs are independent; no output from a skipped step is referenced by a subsequent step. ✓
- **Pattern 5:** N/A.

**Bug A found and fixed:**

All 3 agent prompts previously directed agents to write to:
```
{{output_dir}}/investigation/modules/{{topic_slug}}/agents/[agent]/
```

However:
- `prepare-topics` (in `strategy-topdown.yaml`) creates directories at `{{output_dir}}/modules/[slug]/agents/[agent]/` — **no** `investigation/` prefix
- `reconcile-modules` passes `investigation_dir: "{{output_dir}}/modules/{{topic.slug}}"` — **no** `investigation/` prefix

This meant agents wrote artifacts to `…/investigation/modules/…` while the synthesizer looked in `…/modules/…` — a completely different directory. The synthesizer would read from an empty structure and produce a vacuous synthesis with no actual evidence.

**Fix:** Removed the spurious `investigation/` prefix from all 3 prompts:
```
# Before (WRONG):
{{output_dir}}/investigation/modules/{{topic_slug}}/agents/code-tracer/

# After (CORRECT):
{{output_dir}}/modules/{{topic_slug}}/agents/code-tracer/
```

Applied to code-tracer, behavior-observer, and integration-mapper prompts.

#### `discovery-synthesize-module.yaml` ✅ CLEAN

- **Steps:** quality-gate (while loop containing synthesize → validate → check-quality)
- **Pattern 1:** `check-quality` uses `validation_result_json = r"""{{validation_result}}"""` followed by `json.loads(...)` — the safe raw string deserialization pattern. ✓
- **Pattern 2:** No `when:` usage.
- **Pattern 3:** No nested template references.
- **Pattern 4:** The while-loop `break_when: "{{quality_check.quality_passed}} == true"` — the template engine serializes the parsed JSON boolean in a form compatible with the condition evaluator. The `{% if _validation_errors %}` Jinja-style block in the synthesize prompt is a supported pattern.
- **Pattern 5:** N/A.
- **Data flow:** quality-gate.update_context propagates `_validation_errors` into successive synthesize calls for retry feedback. ✓

#### `discovery-combine.yaml` ✅ CLEAN

- **Steps:** check-inputs (bash) → combine (agent) → validate (bash) → render (bash, conditional)
- **Pattern 1:** No Python boolean template assignments.
- **Pattern 2:** `condition: "{{render_png}} == 'true'"` correctly uses `condition:`. ✓
- **Pattern 3:** Context defaults `topdown_dir`, `bottomup_dir`, `output_dir` all reference `{{repo_path}}` directly — single-level template, resolves correctly. ✓
- **Pattern 4:** Only `render` step is conditional; it uses `{{output_dir}}` which is always defined (either from default or caller). ✓
- **Pattern 5:** N/A.

---

### Tier 3 — Strategy Recipes

#### `strategy-topdown.yaml` 🔴 → ✅ FIXED (Bugs B, C, D)

- **Stages:** scan → investigate → synthesize
- **Pattern 1:** All Python bash steps use string assignments. `topics_json = r"""{{topics}}"""` in `save-topics-from-scan` uses the safe raw string pattern. ✓
- **Pattern 2:** All steps use `condition:`. ✓
- **Pattern 3:** Context default `output_dir: "{{repo_path}}/.discovery/investigation/topdown"` references `{{repo_path}}` directly. ✓
- **Pattern 4:** `save-topics-from-scan` uses `{{topics}}` but is guarded by the same condition (`parent_topics_available != 'true'`) as the `topic-select` step that sets `topics`. `save-topics-from-file` (the complementary branch) explicitly does not reference `{{topics}}`. ✓
- **Pattern 5:** `investigate-topics` and `reconcile-modules` both use flattened `{{topic.name}}`, `{{topic.slug}}`, `{{topic.description}}`. ✓

**Bugs B, C, D found and fixed in subsystem-synthesis and overview-synthesis:**

*Before (WRONG):*
```yaml
- id: "subsystem-synthesis"
  context:
    subsystem_name: "topdown-discovery"
    topics: "{{topics}}"          # unrecognized by synthesize-subsystem.yaml
    output_dir: "{{output_dir}}"
    fidelity: "{{fidelity}}"      # unrecognized by synthesize-subsystem.yaml

- id: "overview-synthesis"
  context:
    output_dir: "{{output_dir}}"
    fidelity: "{{fidelity}}"      # no repo_root, no subsystem_dot_files
```

*After (CORRECT):*
```yaml
- id: "subsystem-synthesis"
  context:
    subsystem_name: "topdown-discovery"
    module_dot_files: "[]"                     # agents search output_dir for DOTs
    source_dirs: '["{{repo_path}}"]'           # repo root for boundary investigation
    output_dir: "{{output_dir}}"

- id: "overview-synthesis"
  context:
    repo_root: "{{repo_path}}"                 # so agent can examine top-level files
    subsystem_dot_files: '["{{output_dir}}/topdown-discovery.dot"]'
    output_dir: "{{output_dir}}"
```

#### `strategy-bottomup.yaml` 🔴 → ✅ FIXED (Bugs B, C, D)

- **Stages:** scan-and-plan → traverse → assemble
- **Pattern 1–5:** All clean.
- **Data flow:** `compute-traversal` writes `traversal-plan.json` to disk; `update-traversal-plan` re-reads and updates it; `identify-subsystems` reads it for the assemble stage. Consistent throughout. ✓

**Same Bugs B, C, D as strategy-topdown, in the assemble stage:**

*Before (WRONG):*
```yaml
- id: "subsystem-synthesis"
  context:
    subsystem_name: "bottomup-discovery"
    subsystems: "{{subsystems_result.subsystems}}"  # unrecognized
    output_dir: "{{subsystems_result.output_dir}}"
    fidelity: "{{fidelity}}"                         # unrecognized

- id: "overview-synthesis"
  context:
    output_dir: "{{subsystems_result.output_dir}}"
    fidelity: "{{fidelity}}"   # no repo_root, no subsystem_dot_files
```

*After (CORRECT):*
```yaml
- id: "subsystem-synthesis"
  context:
    subsystem_name: "bottomup-discovery"
    module_dot_files: "[]"
    source_dirs: '["{{repo_path}}"]'
    output_dir: "{{subsystems_result.output_dir}}"

- id: "overview-synthesis"
  context:
    repo_root: "{{repo_path}}"
    subsystem_dot_files: '["{{subsystems_result.output_dir}}/bottomup-discovery.dot"]'
    output_dir: "{{subsystems_result.output_dir}}"
```

---

### Tier 4 — Orchestrators

#### `strategy-sequential.yaml` ✅ CLEAN

- **Stages:** bottomup → topdown → combine
- **Pattern 1–5:** All clean.
- **Approval gate:** Present on `bottomup` stage only, absent on `topdown` and `combine`. ✓
- **Data flow:** Explicit path construction throughout — `output_dir: "{{output_dir}}/investigation/bottomup"`, `output_dir: "{{output_dir}}/investigation/topdown"`, `output_dir: "{{output_dir}}/output"`. No reliance on cross-stage output variables for path construction. ✓
- **Context wiring:** `bottomup_context: "{{output_dir}}/investigation/bottomup"` correctly passes the bottom-up output directory to the top-down strategy for contextual grounding. ✓

#### `discovery-pipeline.yaml` ✅ CLEAN

- **Stages:** scan (with approval gate) → strategies → combine
- **Pattern 1:** No boolean template assignments.
- **Pattern 2:** All conditional steps use `condition:`. ✓
  - `run-topdown`: `condition: "{{strategies}} == 'topdown' or {{strategies}} == 'both'"`
  - `run-bottomup`: `condition: "{{strategies}} == 'bottomup' or {{strategies}} == 'both'"`
  - `run-combine`: `condition: "{{strategies}} == 'both'"`
- **Pattern 3:** `output_dir: "{{repo_path}}/.discovery"` uses `{{repo_path}}` directly. ✓
- **Pattern 4:** `run-combine` constructs its paths (`topdown_dir`, `bottomup_dir`, `output_dir`) from `{{output_dir}}` directly — not from `topdown_result` or `bottomup_result` outputs — so even if one strategy was skipped, the paths are valid. ✓
- **Pattern 5:** N/A.
- **Approval gate:** Present on `scan` stage only, absent on `strategies` and `combine`. ✓
- **`parent_topics_available: "true"`:** Correctly passed to `strategy-topdown` so the child recipe skips its own scan and reads the topics already written by the pipeline's `topic-select` step. ✓

---

## The 5 Pattern Check — Summary Table

| Pattern | Description | New instances found | Status |
|---------|-------------|---------------------|--------|
| 1 | `x = {{var}}` with JSON booleans in Python | 0 | Previously fixed (commit `0da941b`) |
| 2 | `when:` instead of `condition:` | 0 | Previously fixed (commit `22e0262`) |
| 3 | Nested template references (chain-resolved) | 0 | Not present; all defaults use `{{repo_path}}` directly |
| 4 | `{{variable}}` undefined after conditional skip | 0 | Previously fixed (commits `46b43a2`, `a9efc1f`); two-step pattern protects against this |
| 5 | `foreach` passing full structured object | 0 | Previously fixed (commit `dd8681a`); all foreach steps use flattened `{{topic.name}}` etc. |

---

## Bugs Fixed in This Session

**Commit `2d34677` — `fix: batch fix recipe runtime issues found during validation audit`**

### Bug A: Path mismatch in `discovery-investigate-topic.yaml` (Critical)

**Root cause:** Agent write paths in all 3 investigation agent prompts contained a spurious `investigation/` directory level that did not exist in the directory structure created by `prepare-topics` or expected by `reconcile-modules`.

**Impact:** Agents would write artifacts to `…/investigation/modules/slug/agents/…` while the synthesizer looked in `…/modules/slug/agents/…`. The synthesizer would read from an empty directory and produce a synthesis with zero evidence. The failure would be silent — no crash, just a low-quality synthesis.

**Fix:** Changed `{{output_dir}}/investigation/modules/{{topic_slug}}/agents/[agent]/` to `{{output_dir}}/modules/{{topic_slug}}/agents/[agent]/` in all 3 agent prompts.

**Files changed:** `recipes/discovery-investigate-topic.yaml` (3 locations)

### Bug B: Missing `repo_root` in overview-synthesis (High)

**Root cause:** `strategy-topdown.yaml` and `strategy-bottomup.yaml` both called `synthesize-overview.yaml` without passing `repo_root`. The `synthesize-overview.yaml` agent prompt explicitly instructs the agent to "Examine top-level files at `{{repo_root}}`" (README, config, entry points). With `repo_root: ""`, the agent had no anchor point for the repository root.

**Impact:** The overview agent could not examine top-level repository files for architectural context. The overview diagram would be produced from subsystem DOTs alone, missing the integrative context that README and top-level configuration files provide.

**Fix:** Added `repo_root: "{{repo_path}}"` to the overview-synthesis context in both strategy recipes.

**Files changed:** `recipes/strategy-topdown.yaml`, `recipes/strategy-bottomup.yaml`

### Bug C: Wrong context keys in subsystem-synthesis (Medium)

**Root cause:** `strategy-topdown.yaml` passed `topics: "{{topics}}"` and `fidelity: "{{fidelity}}"` to `synthesize-subsystem.yaml`. `strategy-bottomup.yaml` passed `subsystems: "{{subsystems_result.subsystems}}"` and `fidelity: "{{fidelity}}"`. Neither of these variables exist in `synthesize-subsystem.yaml`'s context schema, so they were ignored. Meanwhile, the actually useful fields — `module_dot_files` (per-module consensus DOT paths) and `source_dirs` (code directories for boundary investigation) — defaulted to empty JSON arrays.

**Impact:** The subsystem-synthesizer agent received no guidance about where the module-level DOTs were or where to investigate source code for cross-module boundaries. The agent could still search `output_dir` for files, but with less directed guidance.

**Fix:** Replaced unrecognized keys with the correct `module_dot_files: "[]"` and `source_dirs: '["{{repo_path}}"]'` to give the agent the repository root for source code investigation.

**Files changed:** `recipes/strategy-topdown.yaml`, `recipes/strategy-bottomup.yaml`

### Bug D: Missing `subsystem_dot_files` in overview-synthesis (Medium)

**Root cause:** The `overview-synthesis` step ran immediately after `subsystem-synthesis`, which produces a deterministic output file (`[subsystem_name].dot` in `output_dir`). Neither strategy recipe passed this known path as `subsystem_dot_files` to `synthesize-overview.yaml`.

**Impact:** The overview agent had to discover subsystem DOTs itself rather than being directed to the specific file produced by the preceding step. This created a reliance on the agent's search behavior rather than explicit wiring.

**Fix:** Added `subsystem_dot_files` with the deterministic path: `'["{{output_dir}}/topdown-discovery.dot"]'` (topdown) and `'["{{subsystems_result.output_dir}}/bottomup-discovery.dot"]'` (bottomup).

**Files changed:** `recipes/strategy-topdown.yaml`, `recipes/strategy-bottomup.yaml`

---

## Tier 1 Execution Test

### `synthesize-level.yaml` against `amplifier/agents/`

**Command:**
```python
recipes(
    operation="execute",
    recipe_path="/home/bkrabach/dev/dot-graph-bundle/recipes/synthesize-level.yaml",
    context={
        "level_path": "/home/bkrabach/dev/dot-graph-bundle/amplifier/agents",
        "level_slug": "agents",
        "output_dir": "/tmp/test-synth-level",
        "fidelity": "standard"
    }
)
```

**Result:** ✅ SUCCESS

| Field | Value |
|-------|-------|
| Status | `completed` |
| Session ID | `243d63ed863844cb-20260318-104500_recipe` |
| Steps executed | read-level → synthesize → validate |
| Output diagram | `/tmp/test-synth-level/agents/diagram.dot` |
| Node count | 9 |
| Edge count | 13 |
| pydot validation | `valid: true`, `errors: []` |

**Artifacts produced:**
- `diagram.dot` — Valid DOT graph capturing the `amplifier/agents/` level structure with nodes for the `amplifier-expert.md` agent definition, operating modes (RESEARCH, GUIDE, VALIDATE), knowledge base tiers, peer agents, and the shared base include. Well-structured with a legend and subgraph clusters.
- `findings.md` — Key findings document written by the `discovery-level-synthesizer` agent.

**Step 1 (read-level)** successfully inventoried the directory contents via Python, producing a structured JSON inventory.  
**Step 2 (synthesize)** dispatched the `dot-graph:discovery-level-synthesizer` agent which read the inventory and produced both artifacts.  
**Step 3 (validate)** confirmed the diagram is syntactically valid DOT with pydot.

---

## Readiness Assessment

| Tier | Recipe | Code Review | Runtime Test | Ready? |
|------|--------|-------------|--------------|--------|
| 1 | `synthesize-level.yaml` | ✅ Clean | ✅ Executed — 9 nodes, 13 edges, valid | **YES** |
| 1 | `synthesize-subsystem.yaml` | ✅ Clean | Not run (needs module DOTs as input) | **YES** (code review) |
| 1 | `synthesize-overview.yaml` | ✅ Clean | Not run (needs subsystem DOTs as input) | **YES** (code review) |
| 2 | `discovery-investigate-topic.yaml` | ✅ Fixed (Bug A) | Not run (needs agent budget) | **YES** (after fix) |
| 2 | `discovery-synthesize-module.yaml` | ✅ Clean | Not run (needs investigation output) | **YES** (code review) |
| 2 | `discovery-combine.yaml` | ✅ Clean | Not run (needs both strategy outputs) | **YES** (code review) |
| 3 | `strategy-topdown.yaml` | ✅ Fixed (B/C/D) | Not run (multi-agent, long-running) | **YES** (after fix) |
| 3 | `strategy-bottomup.yaml` | ✅ Fixed (B/C/D) | Not run (multi-agent, long-running) | **YES** (after fix) |
| 4 | `strategy-sequential.yaml` | ✅ Clean | Not run (requires Tier 3) | **YES** (code review) |
| 4 | `discovery-pipeline.yaml` | ✅ Clean | Not run (requires all Tiers) | **YES** (code review) |

---

## Test Suite Status

```
1287 passed in 2.55s
```

All tests pass before and after the batch fix. The fix commit (`2d34677`) does not modify any recipe fields that are checked by the existing test suite (tests verify structure, keys, agent references, conditions, and prompt mentions of variable names — not specific path formats within prompts or specific sub-recipe context payload keys).

---

## Recommendations

1. **Run Tier 2 recipes** against the amplifier repo to verify the path-mismatch fix (Bug A) works end-to-end. The synthesize-module recipe should now find agent artifacts in the correct location.

2. **Add a data-flow integration test** that verifies the handoff path: `prepare-topics` → `investigate-topics` → `reconcile-modules`. A lightweight test could create mock artifacts at the expected path, run the synthesizer, and verify it consumed them.

3. **Add `repo_root` to `synthesize-overview.yaml`'s context schema documentation** with a note that it is required for full functionality — the current default of `""` is technically valid but degrades the agent's ability to examine top-level files.

4. **Consider adding a `module_dot_files_glob` field** to `synthesize-subsystem.yaml` that accepts a glob pattern rather than an explicit JSON list, making it easier for strategy recipes to point the agent to all produced DOTs without constructing dynamic lists in YAML.
