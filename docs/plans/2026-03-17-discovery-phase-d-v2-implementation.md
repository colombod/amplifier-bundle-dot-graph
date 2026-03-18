# Discovery Phase D v2 Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Add `discovery-combine.yaml` and `strategy-sequential.yaml`, then rewrite `discovery-pipeline.yaml` as a thin orchestrator that calls strategy sub-recipes.

**Architecture:** Two new recipes compose the strategy layer: `discovery-combine.yaml` reads top-down + bottom-up investigation directories and invokes the `discovery-combiner` agent to produce a unified DOT with convergence/divergence classification; `strategy-sequential.yaml` sequences bottom-up → [approval gate] → top-down → combine. `discovery-pipeline.yaml` shrinks from a monolith to a 3-stage orchestrator (prescan, strategies, combine) that dispatches standalone strategy recipes. All three are independently callable and compose freely.

**Tech Stack:** YAML (recipes), Python 3 inline scripts (bash steps), pytest + PyYAML (tests)

---

## Prerequisites

All Phase A, B, C v2 files must exist before starting:
- `agents/discovery-combiner.md` ✓ (Phase A v2)
- `context/discovery-combiner-instructions.md` ✓ (Phase A v2)
- `recipes/synthesize-level.yaml`, `synthesize-subsystem.yaml`, `synthesize-overview.yaml` ✓ (Phase B v2)
- `recipes/strategy-topdown.yaml`, `recipes/strategy-bottomup.yaml` ✓ (Phase C v2)

Verify with:
```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
python -m pytest tests/test_strategy_topdown_recipe.py tests/test_strategy_bottomup_recipe.py -v --tb=short
```

Expected: all pass.

---

## Task 1: `discovery-combine.yaml` + `test_discovery_combine_recipe.py`

**Files:**
- Create: `tests/test_discovery_combine_recipe.py`
- Create: `recipes/discovery-combine.yaml`

### Step 1: Write the failing test file

Create `tests/test_discovery_combine_recipe.py`:

```python
"""
Tests for recipes/discovery-combine.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse (2 tests)
- Top-level metadata: name, description, version, author, tags (5 tests)
- Context variables: repo_path, topdown_dir, bottomup_dir, output_dir, render_png (7 tests)
- Flat steps structure (not staged) with at least 4 steps (2 tests)
- check-inputs step: exists, bash type, has output (3 tests)
- combine step: exists, uses discovery-combiner agent, has output (3 tests)
- validate step: exists, bash type (2 tests)
- render step: exists, bash type, has condition on render_png (3 tests)
- Dependency file exists: agents/discovery-combiner.md (1 test)

Total: 28 tests
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-combine.yaml"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _load_recipe() -> dict:
    """Load and return the parsed recipe dict."""
    return yaml.safe_load(RECIPE_PATH.read_text())


def _get_steps(data: dict) -> list:
    return data.get("steps", [])


def _get_step_by_id(data: dict, step_id: str) -> dict | None:
    for step in _get_steps(data):
        if step.get("id") == step_id:
            return step
    return None


# ---------------------------------------------------------------------------
# Module-scoped fixture (caches parsed recipe across all tests)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def recipe_data() -> dict:
    """Module-scoped fixture: load and cache the parsed recipe dict once per test module."""
    return _load_recipe()


# ---------------------------------------------------------------------------
# File existence and parse (2 tests)
# ---------------------------------------------------------------------------


def test_recipe_file_exists():
    """recipes/discovery-combine.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/discovery-combine.yaml not found at {RECIPE_PATH}"
    )


def test_recipe_parses_as_valid_yaml():
    """File must parse as valid YAML and produce a dict."""
    content = RECIPE_PATH.read_text()
    data = yaml.safe_load(content)
    assert isinstance(data, dict), f"Expected YAML dict, got {type(data).__name__}"


# ---------------------------------------------------------------------------
# Top-level metadata (5 tests)
# ---------------------------------------------------------------------------


def test_recipe_name(recipe_data):
    """Recipe must have name='discovery-combine'."""
    assert recipe_data.get("name") == "discovery-combine", (
        f"Expected name='discovery-combine', got: {recipe_data.get('name')!r}"
    )


def test_recipe_description_non_empty(recipe_data):
    """Recipe must have a non-empty description."""
    desc = recipe_data.get("description", "")
    assert isinstance(desc, str) and desc.strip(), (
        "Recipe must have a non-empty string description"
    )


def test_recipe_version(recipe_data):
    """Recipe must have version='1.0.0'."""
    assert recipe_data.get("version") == "1.0.0", (
        f"Expected version='1.0.0', got: {recipe_data.get('version')!r}"
    )


def test_recipe_author(recipe_data):
    """Recipe must have author='DOT Graph Bundle'."""
    assert recipe_data.get("author") == "DOT Graph Bundle", (
        f"Expected author='DOT Graph Bundle', got: {recipe_data.get('author')!r}"
    )


def test_recipe_tags(recipe_data):
    """Recipe tags must include discovery, combination, dot-graph."""
    tags = recipe_data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in ["discovery", "combination", "dot-graph"]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables (7 tests)
# ---------------------------------------------------------------------------


def test_recipe_context_has_repo_path(recipe_data):
    """Context must declare 'repo_path' variable."""
    ctx = recipe_data.get("context", {})
    assert "repo_path" in ctx, (
        f"Context must declare 'repo_path' variable. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_topdown_dir(recipe_data):
    """Context must declare 'topdown_dir' variable with a default."""
    ctx = recipe_data.get("context", {})
    assert "topdown_dir" in ctx, (
        f"Context must declare 'topdown_dir'. Found keys: {list(ctx.keys())}"
    )
    assert ctx["topdown_dir"], "topdown_dir must have a non-empty default"


def test_topdown_dir_default_references_topdown(recipe_data):
    """Context topdown_dir default must reference 'topdown' in its path."""
    ctx = recipe_data.get("context", {})
    val = str(ctx.get("topdown_dir", ""))
    assert "topdown" in val, (
        f"topdown_dir default must reference 'topdown', got: {val!r}"
    )


def test_recipe_context_has_bottomup_dir(recipe_data):
    """Context must declare 'bottomup_dir' variable with a default."""
    ctx = recipe_data.get("context", {})
    assert "bottomup_dir" in ctx, (
        f"Context must declare 'bottomup_dir'. Found keys: {list(ctx.keys())}"
    )
    assert ctx["bottomup_dir"], "bottomup_dir must have a non-empty default"


def test_bottomup_dir_default_references_bottomup(recipe_data):
    """Context bottomup_dir default must reference 'bottomup' in its path."""
    ctx = recipe_data.get("context", {})
    val = str(ctx.get("bottomup_dir", ""))
    assert "bottomup" in val, (
        f"bottomup_dir default must reference 'bottomup', got: {val!r}"
    )


def test_recipe_context_has_output_dir(recipe_data):
    """Context must declare 'output_dir' variable."""
    ctx = recipe_data.get("context", {})
    assert "output_dir" in ctx, (
        f"Context must declare 'output_dir'. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_render_png(recipe_data):
    """Context must declare 'render_png' variable with default 'true'."""
    ctx = recipe_data.get("context", {})
    assert "render_png" in ctx, (
        f"Context must declare 'render_png'. Found keys: {list(ctx.keys())}"
    )
    assert ctx["render_png"] == "true", (
        f"render_png default must be 'true', got: {ctx['render_png']!r}"
    )


# ---------------------------------------------------------------------------
# Flat steps structure (2 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_flat_steps_not_staged(recipe_data):
    """Recipe must use flat steps (steps key), not staged structure."""
    assert "steps" in recipe_data, (
        "Recipe must have a top-level 'steps' key (flat recipe, not staged)"
    )
    assert "stages" not in recipe_data, (
        "Recipe must NOT have a top-level 'stages' key — discovery-combine is a flat recipe"
    )
    assert isinstance(recipe_data["steps"], list), "steps must be a list"


def test_recipe_has_at_least_4_steps(recipe_data):
    """Recipe must have at least 4 steps: check-inputs, combine, validate, render."""
    steps = recipe_data.get("steps", [])
    assert len(steps) >= 4, (
        f"Expected at least 4 steps (check-inputs, combine, validate, render), got {len(steps)}"
    )


# ---------------------------------------------------------------------------
# check-inputs step (3 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_check_inputs_step(recipe_data):
    """Must have a step with id='check-inputs'."""
    step = _get_step_by_id(recipe_data, "check-inputs")
    assert step is not None, (
        f"No step with id='check-inputs' found. "
        f"Step IDs: {[s.get('id') for s in _get_steps(recipe_data)]}"
    )


def test_check_inputs_step_is_bash_type(recipe_data):
    """check-inputs step must have type='bash'."""
    step = _get_step_by_id(recipe_data, "check-inputs")
    assert step is not None
    assert step.get("type") == "bash", (
        f"check-inputs step must have type='bash', got: {step.get('type')!r}"
    )


def test_check_inputs_step_has_output(recipe_data):
    """check-inputs step must declare an output variable."""
    step = _get_step_by_id(recipe_data, "check-inputs")
    assert step is not None
    assert step.get("output"), (
        f"check-inputs step must have a non-empty 'output', got: {step.get('output')!r}"
    )


# ---------------------------------------------------------------------------
# combine step (3 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_combine_step(recipe_data):
    """Must have a step with id='combine'."""
    step = _get_step_by_id(recipe_data, "combine")
    assert step is not None, (
        f"No step with id='combine' found. "
        f"Step IDs: {[s.get('id') for s in _get_steps(recipe_data)]}"
    )


def test_combine_step_uses_discovery_combiner_agent(recipe_data):
    """combine step must use the 'dot-graph:discovery-combiner' agent."""
    step = _get_step_by_id(recipe_data, "combine")
    assert step is not None
    agent = step.get("agent", "")
    assert "discovery-combiner" in agent, (
        f"combine step must use agent containing 'discovery-combiner', got: {agent!r}"
    )


def test_combine_step_has_output(recipe_data):
    """combine step must declare an output variable."""
    step = _get_step_by_id(recipe_data, "combine")
    assert step is not None
    assert step.get("output"), (
        f"combine step must have a non-empty 'output', got: {step.get('output')!r}"
    )


# ---------------------------------------------------------------------------
# validate step (2 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_validate_step(recipe_data):
    """Must have a step with id='validate'."""
    step = _get_step_by_id(recipe_data, "validate")
    assert step is not None, (
        f"No step with id='validate' found. "
        f"Step IDs: {[s.get('id') for s in _get_steps(recipe_data)]}"
    )


def test_validate_step_is_bash_type(recipe_data):
    """validate step must have type='bash'."""
    step = _get_step_by_id(recipe_data, "validate")
    assert step is not None
    assert step.get("type") == "bash", (
        f"validate step must have type='bash', got: {step.get('type')!r}"
    )


# ---------------------------------------------------------------------------
# render step (3 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_render_step(recipe_data):
    """Must have a step with id='render'."""
    step = _get_step_by_id(recipe_data, "render")
    assert step is not None, (
        f"No step with id='render' found. "
        f"Step IDs: {[s.get('id') for s in _get_steps(recipe_data)]}"
    )


def test_render_step_is_bash_type(recipe_data):
    """render step must have type='bash'."""
    step = _get_step_by_id(recipe_data, "render")
    assert step is not None
    assert step.get("type") == "bash", (
        f"render step must have type='bash', got: {step.get('type')!r}"
    )


def test_render_step_has_condition_on_render_png(recipe_data):
    """render step must have a condition referencing render_png."""
    step = _get_step_by_id(recipe_data, "render")
    assert step is not None
    condition = step.get("condition", "")
    assert condition, "render step must have a condition"
    assert "render_png" in condition, (
        f"render step condition must reference 'render_png': {condition!r}"
    )


# ---------------------------------------------------------------------------
# Dependency file existence (1 test)
# ---------------------------------------------------------------------------


def test_discovery_combiner_agent_file_exists():
    """agents/discovery-combiner.md must exist (required by the combine step)."""
    agent_file = REPO_ROOT / "agents" / "discovery-combiner.md"
    assert agent_file.exists(), (
        f"agents/discovery-combiner.md not found at {agent_file}. "
        "This agent file must exist before discovery-combine.yaml can run."
    )
```

### Step 2: Run the test to verify it fails

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
python -m pytest tests/test_discovery_combine_recipe.py -v --tb=short
```

Expected: `test_recipe_file_exists` FAILS with "not found". All subsequent tests also fail.
`test_discovery_combiner_agent_file_exists` should PASS (file was created in Phase A v2).

### Step 3: Implement `recipes/discovery-combine.yaml`

Create `recipes/discovery-combine.yaml`:

```yaml
name: "discovery-combine"
description: >
  Combination recipe for Parallax Discovery. Reads both top-down and
  bottom-up strategy investigation directories, invokes the discovery-combiner
  agent to produce a unified combined.dot diagram and discrepancies.md file.
  Explicitly classifies findings as Convergence (both strategies agree),
  Top-down-only (conceptual but not empirical), Bottom-up-only (empirical but
  not conceptual), or Divergence (same thing characterized differently — highest
  value). In degraded mode (one strategy missing) produces that strategy's
  output directly. Writes to .discovery/output/ by default. Suitable as a
  standalone recipe or as the final stage of discovery-pipeline.yaml and
  strategy-sequential.yaml.
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "combination", "convergence", "dot-graph", "multi-agent"]

context:
  repo_path: ""             # Required: path to target repository
  topdown_dir: "{{repo_path}}/.discovery/investigation/topdown"   # Default: topdown investigation dir
  bottomup_dir: "{{repo_path}}/.discovery/investigation/bottomup" # Default: bottomup investigation dir
  output_dir: "{{repo_path}}/.discovery/output"                   # Default: combined output dir
  render_png: "true"        # Optional: render combined DOT to PNG (default: true)

steps:
  # ---------------------------------------------------------------------------
  # Step 1: check-inputs — verify input directories and resolve paths
  # Checks which strategy directories exist, determines operation mode
  # (full: both available, degraded: one available, empty: none available),
  # and creates the output directory. Never fails — degraded mode is valid.
  # ---------------------------------------------------------------------------
  - id: "check-inputs"
    type: "bash"
    output: "inputs_result"
    parse_json: true
    timeout: 30
    command: |
      python3 - <<'EOF'
      import json
      from pathlib import Path

      topdown_dir = "{{topdown_dir}}"
      bottomup_dir = "{{bottomup_dir}}"
      output_dir = "{{output_dir}}"

      topdown_exists = Path(topdown_dir).exists()
      bottomup_exists = Path(bottomup_dir).exists()

      # Create output directory
      Path(output_dir).mkdir(parents=True, exist_ok=True)

      # Determine available inputs and operation mode
      available = []
      if topdown_exists:
          available.append("topdown")
      if bottomup_exists:
          available.append("bottomup")

      if len(available) == 2:
          mode = "full"
      elif len(available) == 1:
          mode = "degraded"
      else:
          mode = "empty"

      result = {
          "topdown_dir": topdown_dir,
          "bottomup_dir": bottomup_dir,
          "output_dir": output_dir,
          "topdown_exists": topdown_exists,
          "bottomup_exists": bottomup_exists,
          "available": available,
          "mode": mode,
      }

      print(json.dumps(result))
      EOF

  # ---------------------------------------------------------------------------
  # Step 2: combine — dispatch the discovery-combiner agent
  # Reads both investigation directories and produces:
  #   combined.dot    — unified DOT with convergence/divergence visual encoding
  #   discrepancies.md — list of divergences with IDs (D-01, D-02, ...)
  # In degraded mode (one input available) produces that strategy's output
  # directly without convergence/divergence analysis.
  # ---------------------------------------------------------------------------
  - id: "combine"
    agent: "dot-graph:discovery-combiner"
    output: "combine_result"
    parse_json: false
    timeout: 3600
    prompt: |
      You are the discovery-combiner agent for Parallax Discovery.

      Your task: read both the top-down and bottom-up strategy outputs and produce
      a unified combined diagram that explicitly classifies findings.

      Input directories:
        Top-down output:  {{inputs_result.topdown_dir}}
        Bottom-up output: {{inputs_result.bottomup_dir}}
        Available inputs: {{inputs_result.available}}
        Operation mode:   {{inputs_result.mode}}

      Output directory: {{inputs_result.output_dir}}

      Classification categories for FULL mode (both strategies available):
        - Convergence     — things both strategies found (high confidence, colored green)
        - Top-down only   — conceptual structure not reflected in actual code (colored blue)
        - Bottom-up only  — empirical structure missed by conceptual investigation (colored orange)
        - Divergence      — same thing characterized differently by both (highest value, colored red)

      For DEGRADED mode (one strategy available):
        Produce that strategy's output directly. No convergence/divergence analysis.
        Write what is available to combined.dot.

      Required outputs — write both files to: {{inputs_result.output_dir}}
        1. combined.dot     — DOT graph with visual encoding of the classification categories
        2. discrepancies.md — numbered list of divergences (D-01, D-02, ...) with descriptions

      @dot-graph:context/discovery-combiner-instructions

  # ---------------------------------------------------------------------------
  # Step 3: validate — verify combined.dot was produced and is valid DOT
  # Checks that combined.dot exists in the output directory and parses
  # successfully with pydot. Non-fatal if pydot is unavailable.
  # ---------------------------------------------------------------------------
  - id: "validate"
    type: "bash"
    output: "validate_result"
    parse_json: true
    timeout: 30
    command: |
      python3 - <<'EOF'
      import json
      from pathlib import Path

      output_dir = "{{inputs_result.output_dir}}"

      result = {
          "valid": False,
          "combined_dot_exists": False,
          "discrepancies_md_exists": False,
          "error": None,
      }

      combined_dot = Path(output_dir) / "combined.dot"
      discrepancies_md = Path(output_dir) / "discrepancies.md"

      result["combined_dot_exists"] = combined_dot.exists()
      result["discrepancies_md_exists"] = discrepancies_md.exists()

      if combined_dot.exists():
          try:
              import pydot
              graphs = pydot.graph_from_dot_file(str(combined_dot))
              result["valid"] = bool(graphs)
          except ImportError:
              result["valid"] = True   # pydot unavailable — skip validation
          except Exception as e:
              result["error"] = str(e)
      else:
          result["error"] = f"combined.dot not found at {combined_dot}"

      print(json.dumps(result))
      EOF

  # ---------------------------------------------------------------------------
  # Step 4: render — optionally render combined.dot to PNG
  # Skipped when render_png != 'true'. Uses amplifier_module_tool_dot_graph.render
  # with fallback to graphviz CLI. Render failures are non-fatal.
  # ---------------------------------------------------------------------------
  - id: "render"
    type: "bash"
    condition: "{{render_png}} == 'true'"
    output: "render_result"
    parse_json: true
    timeout: 60
    command: |
      python3 - <<'EOF'
      import json
      from pathlib import Path

      output_dir = "{{inputs_result.output_dir}}"
      result = {"rendered": [], "errors": []}

      combined_dot = Path(output_dir) / "combined.dot"
      if not combined_dot.exists():
          result["errors"].append(f"combined.dot not found at {combined_dot}")
          print(json.dumps(result))
          raise SystemExit(0)

      try:
          from amplifier_module_tool_dot_graph import render as dot_render
          png_path = str(combined_dot).replace(".dot", ".png")
          dot_content = combined_dot.read_text()
          render_result = dot_render.render_dot(dot_content, "png", "dot", png_path)
          if render_result.get("success"):
              result["rendered"].append(png_path)
          else:
              result["errors"].append(render_result.get("error", "unknown error"))
      except ImportError as e:
          result["errors"].append(f"render module unavailable: {e}")

      print(json.dumps(result))
      EOF

final_output: "validate_result"
```

### Step 4: Run the test to verify it passes

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
python -m pytest tests/test_discovery_combine_recipe.py -v --tb=short
```

Expected: all 28 tests PASS.

### Step 5: Commit

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
git add recipes/discovery-combine.yaml tests/test_discovery_combine_recipe.py
git commit -m "feat: add discovery-combine.yaml recipe and tests (convergence/divergence combiner)"
```

---

## Task 2: `strategy-sequential.yaml` + `test_strategy_sequential_recipe.py`

**Files:**
- Create: `tests/test_strategy_sequential_recipe.py`
- Create: `recipes/strategy-sequential.yaml`

### Step 1: Write the failing test file

Create `tests/test_strategy_sequential_recipe.py`:

```python
"""
Tests for recipes/strategy-sequential.yaml existence and structure.
TDD: Tests written BEFORE the recipe file is created.

Validates:
- File existence and valid YAML parse (2 tests)
- Top-level metadata: name, description, version, author, tags (5 tests)
- Context variables: repo_path, output_dir, fidelity default (3 tests)
- Staged structure with exactly 3 stages (2 tests)
- Stage names: bottomup, topdown, combine (3 tests)
- bottomup stage: has run-bottomup step, type='recipe', references strategy-bottomup (3 tests)
- bottomup stage: has approval_gate with required=true (2 tests)
- topdown stage: has run-topdown step, type='recipe', references strategy-topdown (3 tests)
- topdown stage context: passes bottomup_context variable (1 test)
- combine stage: has run-combine step, type='recipe', references discovery-combine (3 tests)
- Sub-recipe files exist on disk: strategy-bottomup, strategy-topdown, discovery-combine (3 tests)

Total: 30 tests
"""

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "strategy-sequential.yaml"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _load_recipe() -> dict:
    """Load and return the parsed recipe dict."""
    return yaml.safe_load(RECIPE_PATH.read_text())


def _get_stages(data: dict) -> list:
    return data.get("stages", [])


def _get_stage_by_name(data: dict, stage_name: str) -> dict | None:
    for stage in _get_stages(data):
        if stage.get("name") == stage_name:
            return stage
    return None


def _get_stage_steps(data: dict, stage_name: str) -> list:
    stage = _get_stage_by_name(data, stage_name)
    if stage is None:
        return []
    return stage.get("steps", [])


def _get_stage_step_by_id(data: dict, stage_name: str, step_id: str) -> dict | None:
    for step in _get_stage_steps(data, stage_name):
        if step.get("id") == step_id:
            return step
    return None


# ---------------------------------------------------------------------------
# Module-scoped fixture
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def recipe_data() -> dict:
    """Module-scoped fixture: load and cache the parsed recipe dict once per test module."""
    return _load_recipe()


# ---------------------------------------------------------------------------
# File existence and parse (2 tests)
# ---------------------------------------------------------------------------


def test_recipe_file_exists():
    """recipes/strategy-sequential.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/strategy-sequential.yaml not found at {RECIPE_PATH}"
    )


def test_recipe_parses_as_valid_yaml():
    """File must parse as valid YAML and produce a dict."""
    content = RECIPE_PATH.read_text()
    data = yaml.safe_load(content)
    assert isinstance(data, dict), f"Expected YAML dict, got {type(data).__name__}"


# ---------------------------------------------------------------------------
# Top-level metadata (5 tests)
# ---------------------------------------------------------------------------


def test_recipe_name(recipe_data):
    """Recipe must have name='strategy-sequential'."""
    assert recipe_data.get("name") == "strategy-sequential", (
        f"Expected name='strategy-sequential', got: {recipe_data.get('name')!r}"
    )


def test_recipe_description_non_empty(recipe_data):
    """Recipe must have a non-empty description."""
    desc = recipe_data.get("description", "")
    assert isinstance(desc, str) and desc.strip(), (
        "Recipe must have a non-empty string description"
    )


def test_recipe_version(recipe_data):
    """Recipe must have version='1.0.0'."""
    assert recipe_data.get("version") == "1.0.0", (
        f"Expected version='1.0.0', got: {recipe_data.get('version')!r}"
    )


def test_recipe_author(recipe_data):
    """Recipe must have author='DOT Graph Bundle'."""
    assert recipe_data.get("author") == "DOT Graph Bundle", (
        f"Expected author='DOT Graph Bundle', got: {recipe_data.get('author')!r}"
    )


def test_recipe_tags(recipe_data):
    """Recipe tags must include discovery, strategy, sequential, dot-graph."""
    tags = recipe_data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in ["discovery", "strategy", "sequential", "dot-graph"]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables (3 tests)
# ---------------------------------------------------------------------------


def test_recipe_context_has_repo_path(recipe_data):
    """Context must declare 'repo_path' variable."""
    ctx = recipe_data.get("context", {})
    assert "repo_path" in ctx, (
        f"Context must declare 'repo_path'. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_output_dir(recipe_data):
    """Context must declare 'output_dir' variable."""
    ctx = recipe_data.get("context", {})
    assert "output_dir" in ctx, (
        f"Context must declare 'output_dir'. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_fidelity_default_standard(recipe_data):
    """Context must declare 'fidelity' variable with default 'standard'."""
    ctx = recipe_data.get("context", {})
    assert "fidelity" in ctx, (
        f"Context must declare 'fidelity'. Found keys: {list(ctx.keys())}"
    )
    assert ctx["fidelity"] == "standard", (
        f"fidelity default must be 'standard', got: {ctx['fidelity']!r}"
    )


# ---------------------------------------------------------------------------
# Staged structure (2 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_staged_structure_not_flat(recipe_data):
    """Recipe must use staged structure (stages key), not flat steps."""
    assert "stages" in recipe_data, (
        "Recipe must have a top-level 'stages' key (staged recipe)"
    )
    assert "steps" not in recipe_data, (
        "Recipe must NOT have a top-level 'steps' key — must be staged"
    )
    assert isinstance(recipe_data["stages"], list), "stages must be a list"


def test_recipe_has_exactly_3_stages(recipe_data):
    """Recipe must have exactly 3 stages."""
    stages = recipe_data.get("stages", [])
    assert len(stages) == 3, f"Expected exactly 3 stages, got {len(stages)}"


# ---------------------------------------------------------------------------
# Stage names (3 tests)
# ---------------------------------------------------------------------------


def test_stage_bottomup_exists(recipe_data):
    """Must have a stage named 'bottomup'."""
    stage = _get_stage_by_name(recipe_data, "bottomup")
    assert stage is not None, (
        f"No stage named 'bottomup' found. "
        f"Stage names: {[s.get('name') for s in _get_stages(recipe_data)]}"
    )


def test_stage_topdown_exists(recipe_data):
    """Must have a stage named 'topdown'."""
    stage = _get_stage_by_name(recipe_data, "topdown")
    assert stage is not None, (
        f"No stage named 'topdown' found. "
        f"Stage names: {[s.get('name') for s in _get_stages(recipe_data)]}"
    )


def test_stage_combine_exists(recipe_data):
    """Must have a stage named 'combine'."""
    stage = _get_stage_by_name(recipe_data, "combine")
    assert stage is not None, (
        f"No stage named 'combine' found. "
        f"Stage names: {[s.get('name') for s in _get_stages(recipe_data)]}"
    )


# ---------------------------------------------------------------------------
# bottomup stage (5 tests)
# ---------------------------------------------------------------------------


def test_bottomup_stage_has_run_bottomup_step(recipe_data):
    """bottomup stage must have a step with id='run-bottomup'."""
    step = _get_stage_step_by_id(recipe_data, "bottomup", "run-bottomup")
    assert step is not None, (
        f"No step with id='run-bottomup' found in bottomup stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(recipe_data, 'bottomup')]}"
    )


def test_bottomup_stage_run_bottomup_is_recipe_type(recipe_data):
    """run-bottomup step must have type='recipe'."""
    step = _get_stage_step_by_id(recipe_data, "bottomup", "run-bottomup")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-bottomup step must have type='recipe', got: {step.get('type')!r}"
    )


def test_bottomup_stage_references_strategy_bottomup(recipe_data):
    """run-bottomup step must reference the strategy-bottomup sub-recipe."""
    step = _get_stage_step_by_id(recipe_data, "bottomup", "run-bottomup")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "strategy-bottomup" in recipe_ref, (
        f"run-bottomup must reference strategy-bottomup sub-recipe, got: {recipe_ref!r}"
    )


def test_bottomup_stage_has_approval_gate(recipe_data):
    """bottomup stage must have an approval_gate (review empirical findings before top-down)."""
    stage = _get_stage_by_name(recipe_data, "bottomup")
    assert stage is not None
    assert "approval_gate" in stage, (
        "bottomup stage must have an 'approval_gate' — "
        "user reviews bottom-up findings before top-down investigation begins"
    )


def test_bottomup_approval_gate_is_required(recipe_data):
    """bottomup stage approval_gate must have required=true."""
    stage = _get_stage_by_name(recipe_data, "bottomup")
    assert stage is not None
    gate = stage.get("approval_gate", {})
    assert gate.get("required") is True, (
        f"approval_gate.required must be true, got: {gate.get('required')!r}"
    )


# ---------------------------------------------------------------------------
# topdown stage (4 tests)
# ---------------------------------------------------------------------------


def test_topdown_stage_has_run_topdown_step(recipe_data):
    """topdown stage must have a step with id='run-topdown'."""
    step = _get_stage_step_by_id(recipe_data, "topdown", "run-topdown")
    assert step is not None, (
        f"No step with id='run-topdown' found in topdown stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(recipe_data, 'topdown')]}"
    )


def test_topdown_stage_run_topdown_is_recipe_type(recipe_data):
    """run-topdown step must have type='recipe'."""
    step = _get_stage_step_by_id(recipe_data, "topdown", "run-topdown")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-topdown step must have type='recipe', got: {step.get('type')!r}"
    )


def test_topdown_stage_references_strategy_topdown(recipe_data):
    """run-topdown step must reference the strategy-topdown sub-recipe."""
    step = _get_stage_step_by_id(recipe_data, "topdown", "run-topdown")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "strategy-topdown" in recipe_ref, (
        f"run-topdown must reference strategy-topdown sub-recipe, got: {recipe_ref!r}"
    )


def test_topdown_step_context_passes_bottomup_context(recipe_data):
    """run-topdown step must pass 'bottomup_context' in its context block."""
    step = _get_stage_step_by_id(recipe_data, "topdown", "run-topdown")
    assert step is not None
    context_block = step.get("context", {})
    assert "bottomup_context" in context_block, (
        f"run-topdown step must pass 'bottomup_context' to strategy-topdown. "
        f"Context keys: {list(context_block.keys())}"
    )


# ---------------------------------------------------------------------------
# combine stage (3 tests)
# ---------------------------------------------------------------------------


def test_combine_stage_has_run_combine_step(recipe_data):
    """combine stage must have a step with id='run-combine'."""
    step = _get_stage_step_by_id(recipe_data, "combine", "run-combine")
    assert step is not None, (
        f"No step with id='run-combine' found in combine stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(recipe_data, 'combine')]}"
    )


def test_combine_stage_run_combine_is_recipe_type(recipe_data):
    """run-combine step must have type='recipe'."""
    step = _get_stage_step_by_id(recipe_data, "combine", "run-combine")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-combine step must have type='recipe', got: {step.get('type')!r}"
    )


def test_combine_stage_references_discovery_combine(recipe_data):
    """run-combine step must reference the discovery-combine sub-recipe."""
    step = _get_stage_step_by_id(recipe_data, "combine", "run-combine")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "discovery-combine" in recipe_ref, (
        f"run-combine must reference discovery-combine sub-recipe, got: {recipe_ref!r}"
    )


# ---------------------------------------------------------------------------
# Sub-recipe files exist on disk (3 tests)
# ---------------------------------------------------------------------------


def test_strategy_bottomup_sub_recipe_exists():
    """Sub-recipe file strategy-bottomup.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "strategy-bottomup.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe strategy-bottomup.yaml not found at {sub_recipe}"
    )


def test_strategy_topdown_sub_recipe_exists():
    """Sub-recipe file strategy-topdown.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "strategy-topdown.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe strategy-topdown.yaml not found at {sub_recipe}"
    )


def test_discovery_combine_sub_recipe_exists():
    """Sub-recipe file discovery-combine.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "discovery-combine.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe discovery-combine.yaml not found at {sub_recipe}"
    )
```

### Step 2: Run the test to verify it fails

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
python -m pytest tests/test_strategy_sequential_recipe.py -v --tb=short
```

Expected: `test_recipe_file_exists` FAILS. `test_discovery_combine_sub_recipe_exists` and
the two strategy sub-recipe tests should PASS (files exist from Task 1 and Phase C).

### Step 3: Implement `recipes/strategy-sequential.yaml`

Create `recipes/strategy-sequential.yaml`:

```yaml
name: "strategy-sequential"
description: >
  Sequential composition strategy for Parallax Discovery. Proves composability
  by orchestrating three other recipes in sequence with no novel agents of its
  own. Stage 1 runs strategy-bottomup fully to completion, writing empirical
  ground-truth DOTs to .discovery/investigation/bottomup/. An approval gate
  presents the bottom-up findings before the top-down investigation begins.
  Stage 2 runs strategy-topdown with a 'bottomup_context' variable pointing
  to the bottom-up output — topic selection agents are informed by actual
  structure, and investigation agents are primed to notice divergences. Stage 3
  runs discovery-combine to produce unified output with convergence/divergence
  analysis. Improvements to any component recipe propagate automatically.
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "strategy", "sequential", "dot-graph", "multi-agent"]

recursion:
  max_depth: 4
  max_total_steps: 300

context:
  repo_path: ""             # Required: path to target repository
  output_dir: "{{repo_path}}/.discovery"  # Base discovery directory
  fidelity: "standard"      # Optional: quick | standard | deep (default: standard)

stages:
  # ---------------------------------------------------------------------------
  # Stage 1: bottomup — run strategy-bottomup to completion
  # Produces empirical ground-truth DOTs at every directory level.
  # Writes to .discovery/investigation/bottomup/.
  # [Approval gate] — user reviews what bottom-up actually found before
  # the conceptual investigation begins. Valuable: may identify specific
  # areas to focus top-down investigation on.
  # ---------------------------------------------------------------------------
  - name: "bottomup"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Run strategy-bottomup — full post-order traversal
      # Calls strategy-bottomup.yaml as a sub-recipe. Runs fully unattended
      # (strategy-bottomup has no approval gate). Writes traversal-plan.json,
      # per-level diagram.dot files, subsystem synthesis, and overview synthesis
      # to the bottomup investigation directory.
      # -----------------------------------------------------------------------
      - id: "run-bottomup"
        type: "recipe"
        recipe: "@dot-graph:recipes/strategy-bottomup.yaml"
        context:
          repo_path: "{{repo_path}}"
          fidelity: "{{fidelity}}"
          output_dir: "{{repo_path}}/.discovery/investigation/bottomup"
        output: "bottomup_result"
        timeout: 14400

    approval_gate:
      required: true
      prompt: |
        Sequential Discovery Strategy — Bottom-up Pass Complete

        Repository:   {{repo_path}}
        Fidelity:     {{fidelity}}
        Bottom-up output: {{repo_path}}/.discovery/investigation/bottomup

        The bottom-up empirical traversal has completed. It built understanding
        from the leaf directories upward, synthesizing each directory level before
        its parent — discovering what actually exists rather than what documentation
        claims.

        Review the findings at:
          {{repo_path}}/.discovery/investigation/bottomup/

        Look for:
          - overview.dot / overview.png — the full empirical overview diagram
          - subsystems/ — subsystem-level synthesis DOTs
          - Per-directory diagram.dot files — level-by-level synthesis

        The top-down investigation will use this output as additional context.
        Topic selection will be informed by actual codebase structure, and
        investigation agents will be primed to surface divergences from what
        the bottom-up pass found.

        Type APPROVE to proceed with top-down investigation, or DENY to cancel.

  # ---------------------------------------------------------------------------
  # Stage 2: topdown — run strategy-topdown with bottom-up context
  # Calls strategy-topdown.yaml with an extra 'bottomup_context' variable
  # pointing at the bottom-up output directory. Topic selection and
  # investigation agents can reference specific bottom-up DOTs as starting
  # points and notice divergences from the empirical ground truth.
  # ---------------------------------------------------------------------------
  - name: "topdown"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Run strategy-topdown — contextual investigation
      # Passes bottomup_context so agents know what the empirical pass found.
      # strategy-topdown runs fully unattended (no approval gate of its own).
      # Writes topics, per-topic investigation, subsystem synthesis, and overview
      # to the topdown investigation directory.
      # -----------------------------------------------------------------------
      - id: "run-topdown"
        type: "recipe"
        recipe: "@dot-graph:recipes/strategy-topdown.yaml"
        context:
          repo_path: "{{repo_path}}"
          fidelity: "{{fidelity}}"
          output_dir: "{{repo_path}}/.discovery/investigation/topdown"
          bottomup_context: "{{repo_path}}/.discovery/investigation/bottomup"
        output: "topdown_result"
        timeout: 14400

  # ---------------------------------------------------------------------------
  # Stage 3: combine — produce unified output with convergence/divergence
  # Calls discovery-combine.yaml which reads both investigation directories
  # and invokes the discovery-combiner agent to classify findings.
  # ---------------------------------------------------------------------------
  - name: "combine"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Run discovery-combine — unify both strategy outputs
      # Reads topdown and bottomup investigation directories, invokes the
      # discovery-combiner agent, produces combined.dot + discrepancies.md
      # to .discovery/output/.
      # -----------------------------------------------------------------------
      - id: "run-combine"
        type: "recipe"
        recipe: "@dot-graph:recipes/discovery-combine.yaml"
        context:
          repo_path: "{{repo_path}}"
          output_dir: "{{output_dir}}/output"
          render_png: "true"
        output: "combine_result"
        timeout: 3600

final_output: "combine_result"
```

### Step 4: Run the test to verify it passes

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
python -m pytest tests/test_strategy_sequential_recipe.py -v --tb=short
```

Expected: all 30 tests PASS.

### Step 5: Commit

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
git add recipes/strategy-sequential.yaml tests/test_strategy_sequential_recipe.py
git commit -m "feat: add strategy-sequential.yaml recipe and tests (sequential orchestrator with approval gate)"
```

---

## Task 3: Rewrite `tests/test_discovery_pipeline_recipe.py` + `recipes/discovery-pipeline.yaml`

**Files:**
- Modify: `tests/test_discovery_pipeline_recipe.py` — completely rewritten for new thin-orchestrator structure
- Modify: `recipes/discovery-pipeline.yaml` — rewritten as thin orchestrator

**Why rewrite both together:** The existing test file validates the old monolith (scan/investigate/synthesize with change-detect, topic-select, prepare-topics, assemble, etc.). Writing the new tests first will show many failures against the current monolith. Then implementing the new recipe makes them all pass.

### Step 1: Read the current files first

```
wc -l /home/bkrabach/dev/amplifier-bundle-dot-graph/recipes/discovery-pipeline.yaml
wc -l /home/bkrabach/dev/amplifier-bundle-dot-graph/tests/test_discovery_pipeline_recipe.py
```

These confirm what you are replacing (521-line recipe, 688-line test file).

### Step 2: Write the new test file

Replace `tests/test_discovery_pipeline_recipe.py` entirely with:

```python
"""
Tests for recipes/discovery-pipeline.yaml existence and structure.
Updated for thin orchestrator structure (Phase D v2).
Previously tested monolith (scan/investigate/synthesize). Now tests
thin orchestrator: prescan → strategies → combine.

Validates:
- File existence and valid YAML parse (2 tests)
- Top-level metadata: name, description, version, author, tags (5 tests)
- Context variables: repo_path, fidelity, output_dir, render_png,
  strategies, _approval_message, backward compatibility (8 tests)
- Staged structure (not flat) with exactly 3 stages (2 tests)
- Stage names: prescan, strategies, combine (3 tests)
- prescan stage: approval gate required with prompt (3 tests)
- prescan stage steps: change-detect (bash, parse_json, output=change_result) (4 tests)
- prescan stage steps: structural-scan (exists, has condition on 'skip') (2 tests)
- strategies stage: run-topdown (recipe, references strategy-topdown,
  condition references strategies) (4 tests)
- strategies stage: run-bottomup (recipe, references strategy-bottomup,
  condition references strategies) (4 tests)
- combine stage: run-combine (recipe, references discovery-combine,
  condition references strategies) (4 tests)
- Sub-recipe files exist: strategy-topdown, strategy-bottomup,
  discovery-combine (3 tests)
- final_output declared (1 test)
- strategies context var: declared and defaults to 'both' (2 tests)

Total: 51 tests
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
RECIPE_PATH = REPO_ROOT / "recipes" / "discovery-pipeline.yaml"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _load_recipe() -> dict:
    """Load and return the parsed recipe dict."""
    return yaml.safe_load(RECIPE_PATH.read_text())


def _get_stages(data: dict) -> list:
    return data.get("stages", [])


def _get_stage_by_name(data: dict, stage_name: str) -> dict | None:
    for stage in _get_stages(data):
        if stage.get("name") == stage_name:
            return stage
    return None


def _get_stage_steps(data: dict, stage_name: str) -> list:
    stage = _get_stage_by_name(data, stage_name)
    if stage is None:
        return []
    return stage.get("steps", [])


def _get_stage_step_by_id(data: dict, stage_name: str, step_id: str) -> dict | None:
    for step in _get_stage_steps(data, stage_name):
        if step.get("id") == step_id:
            return step
    return None


# ---------------------------------------------------------------------------
# File existence and parse (2 tests)
# ---------------------------------------------------------------------------


def test_recipe_file_exists():
    """recipes/discovery-pipeline.yaml must exist."""
    assert RECIPE_PATH.exists(), (
        f"recipes/discovery-pipeline.yaml not found at {RECIPE_PATH}"
    )


def test_recipe_parses_as_valid_yaml():
    """File must parse as valid YAML and produce a dict."""
    content = RECIPE_PATH.read_text()
    data = yaml.safe_load(content)
    assert isinstance(data, dict), f"Expected YAML dict, got {type(data).__name__}"


# ---------------------------------------------------------------------------
# Top-level metadata (5 tests)
# ---------------------------------------------------------------------------


def test_recipe_name():
    """Recipe must have name='discovery-pipeline'."""
    data = _load_recipe()
    assert data.get("name") == "discovery-pipeline", (
        f"Expected name='discovery-pipeline', got: {data.get('name')!r}"
    )


def test_recipe_description_non_empty():
    """Recipe must have a non-empty description."""
    data = _load_recipe()
    desc = data.get("description", "")
    assert isinstance(desc, str) and desc.strip(), (
        "Recipe must have a non-empty string description"
    )


def test_recipe_version():
    """Recipe must have version='1.0.0'."""
    data = _load_recipe()
    assert data.get("version") == "1.0.0", (
        f"Expected version='1.0.0', got: {data.get('version')!r}"
    )


def test_recipe_author():
    """Recipe must have author='DOT Graph Bundle'."""
    data = _load_recipe()
    assert data.get("author") == "DOT Graph Bundle", (
        f"Expected author='DOT Graph Bundle', got: {data.get('author')!r}"
    )


def test_recipe_tags():
    """Recipe tags must include discovery, pipeline, architecture, dot-graph, multi-agent."""
    data = _load_recipe()
    tags = data.get("tags", [])
    assert isinstance(tags, list), "tags must be a list"
    for expected_tag in [
        "discovery",
        "pipeline",
        "architecture",
        "dot-graph",
        "multi-agent",
    ]:
        assert expected_tag in tags, (
            f"Expected tag {expected_tag!r} not found in tags: {tags}"
        )


# ---------------------------------------------------------------------------
# Context variables (8 tests)
# ---------------------------------------------------------------------------


def test_recipe_context_has_repo_path():
    """Context must declare 'repo_path' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "repo_path" in ctx, (
        f"Context must declare 'repo_path'. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_fidelity():
    """Context must declare 'fidelity' variable with default 'standard'."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "fidelity" in ctx, (
        f"Context must declare 'fidelity'. Found keys: {list(ctx.keys())}"
    )
    assert ctx["fidelity"] == "standard", (
        f"fidelity default must be 'standard', got: {ctx['fidelity']!r}"
    )


def test_recipe_context_has_output_dir():
    """Context must declare 'output_dir' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "output_dir" in ctx, (
        f"Context must declare 'output_dir'. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_has_render_png():
    """Context must declare 'render_png' variable with default 'true'."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "render_png" in ctx, (
        f"Context must declare 'render_png'. Found keys: {list(ctx.keys())}"
    )
    assert ctx["render_png"] == "true", (
        f"render_png default must be 'true', got: {ctx['render_png']!r}"
    )


def test_recipe_context_has_strategies():
    """Context must declare 'strategies' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "strategies" in ctx, (
        f"Context must declare 'strategies'. Found keys: {list(ctx.keys())}"
    )


def test_strategies_default_is_both():
    """Context 'strategies' variable must default to 'both'."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert ctx.get("strategies") == "both", (
        f"strategies default must be 'both', got: {ctx.get('strategies')!r}"
    )


def test_recipe_context_has_approval_message():
    """Context must declare '_approval_message' variable."""
    data = _load_recipe()
    ctx = data.get("context", {})
    assert "_approval_message" in ctx, (
        f"Context must declare '_approval_message'. Found keys: {list(ctx.keys())}"
    )


def test_recipe_context_backward_compatible_vars():
    """Context must declare all backward-compatible vars: repo_path, fidelity, output_dir, render_png."""
    data = _load_recipe()
    ctx = data.get("context", {})
    for var in ["repo_path", "fidelity", "output_dir", "render_png"]:
        assert var in ctx, (
            f"Context must declare backward-compatible var '{var}'. "
            f"Found keys: {list(ctx.keys())}"
        )


# ---------------------------------------------------------------------------
# Staged structure (2 tests)
# ---------------------------------------------------------------------------


def test_recipe_has_staged_structure_not_flat():
    """Recipe must use staged structure (stages key), not flat steps."""
    data = _load_recipe()
    assert "stages" in data, "Recipe must have a top-level 'stages' key (staged recipe)"
    assert "steps" not in data, (
        "Recipe must NOT have a top-level 'steps' key — must be staged"
    )
    assert isinstance(data["stages"], list), "stages must be a list"


def test_recipe_has_exactly_3_stages():
    """Recipe must have exactly 3 stages."""
    data = _load_recipe()
    stages = data.get("stages", [])
    assert len(stages) == 3, f"Expected exactly 3 stages, got {len(stages)}"


# ---------------------------------------------------------------------------
# Stage names (3 tests)
# ---------------------------------------------------------------------------


def test_stage_prescan_exists():
    """Must have a stage named 'prescan'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "prescan")
    assert stage is not None, (
        f"No stage named 'prescan' found. "
        f"Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


def test_stage_strategies_exists():
    """Must have a stage named 'strategies'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "strategies")
    assert stage is not None, (
        f"No stage named 'strategies' found. "
        f"Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


def test_stage_combine_exists():
    """Must have a stage named 'combine'."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "combine")
    assert stage is not None, (
        f"No stage named 'combine' found. "
        f"Stage names: {[s.get('name') for s in _get_stages(data)]}"
    )


# ---------------------------------------------------------------------------
# prescan stage: approval gate (3 tests)
# ---------------------------------------------------------------------------


def test_prescan_stage_has_approval_gate():
    """prescan stage must have an approval_gate field."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "prescan")
    assert stage is not None
    assert "approval_gate" in stage, (
        "prescan stage must have an 'approval_gate' field"
    )


def test_prescan_approval_gate_is_required():
    """prescan stage approval_gate must have required=true."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "prescan")
    assert stage is not None
    gate = stage.get("approval_gate", {})
    assert gate.get("required") is True, (
        f"approval_gate.required must be true, got: {gate.get('required')!r}"
    )


def test_prescan_approval_gate_has_prompt():
    """prescan stage approval_gate must have a non-empty prompt."""
    data = _load_recipe()
    stage = _get_stage_by_name(data, "prescan")
    assert stage is not None
    gate = stage.get("approval_gate", {})
    prompt = gate.get("prompt", "")
    assert isinstance(prompt, str) and prompt.strip(), (
        "approval_gate must have a non-empty prompt"
    )


# ---------------------------------------------------------------------------
# prescan stage: change-detect step (4 tests)
# ---------------------------------------------------------------------------


def test_prescan_step_change_detect_exists():
    """prescan stage must have a step with id='change-detect'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "prescan", "change-detect")
    assert step is not None, (
        f"No step with id='change-detect' found in prescan stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'prescan')]}"
    )


def test_change_detect_is_bash_type():
    """change-detect step must have type='bash'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "prescan", "change-detect")
    assert step is not None
    assert step.get("type") == "bash", (
        f"change-detect step must have type='bash', got: {step.get('type')!r}"
    )


def test_change_detect_has_parse_json():
    """change-detect step must have parse_json=true."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "prescan", "change-detect")
    assert step is not None
    assert step.get("parse_json") is True, (
        f"change-detect step must have parse_json=true, got: {step.get('parse_json')!r}"
    )


def test_change_detect_output_variable():
    """change-detect step must have output='change_result'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "prescan", "change-detect")
    assert step is not None
    assert step.get("output") == "change_result", (
        f"change-detect output must be 'change_result', got: {step.get('output')!r}"
    )


# ---------------------------------------------------------------------------
# prescan stage: structural-scan step (2 tests)
# ---------------------------------------------------------------------------


def test_prescan_step_structural_scan_exists():
    """prescan stage must have a step with id='structural-scan'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "prescan", "structural-scan")
    assert step is not None, (
        f"No step with id='structural-scan' found in prescan stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'prescan')]}"
    )


def test_structural_scan_has_condition():
    """structural-scan step must have a condition that checks change_result tier."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "prescan", "structural-scan")
    assert step is not None
    condition = step.get("condition", "")
    assert condition, "structural-scan step must have a condition"
    assert "skip" in condition, (
        f"structural-scan condition must reference 'skip': {condition!r}"
    )


# ---------------------------------------------------------------------------
# strategies stage: run-topdown step (4 tests)
# ---------------------------------------------------------------------------


def test_strategies_stage_has_run_topdown_step():
    """strategies stage must have a step with id='run-topdown'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-topdown")
    assert step is not None, (
        f"No step with id='run-topdown' found in strategies stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'strategies')]}"
    )


def test_run_topdown_is_recipe_type():
    """run-topdown step must have type='recipe'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-topdown")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-topdown step must have type='recipe', got: {step.get('type')!r}"
    )


def test_run_topdown_references_strategy_topdown():
    """run-topdown step must reference the strategy-topdown sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-topdown")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "strategy-topdown" in recipe_ref, (
        f"run-topdown must reference strategy-topdown sub-recipe, got: {recipe_ref!r}"
    )


def test_run_topdown_has_condition_referencing_strategies():
    """run-topdown step must have a condition referencing the 'strategies' context var."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-topdown")
    assert step is not None
    condition = step.get("condition", "")
    assert condition, "run-topdown step must have a condition"
    assert "strategies" in condition, (
        f"run-topdown condition must reference 'strategies' context var: {condition!r}"
    )


# ---------------------------------------------------------------------------
# strategies stage: run-bottomup step (4 tests)
# ---------------------------------------------------------------------------


def test_strategies_stage_has_run_bottomup_step():
    """strategies stage must have a step with id='run-bottomup'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-bottomup")
    assert step is not None, (
        f"No step with id='run-bottomup' found in strategies stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'strategies')]}"
    )


def test_run_bottomup_is_recipe_type():
    """run-bottomup step must have type='recipe'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-bottomup")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-bottomup step must have type='recipe', got: {step.get('type')!r}"
    )


def test_run_bottomup_references_strategy_bottomup():
    """run-bottomup step must reference the strategy-bottomup sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-bottomup")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "strategy-bottomup" in recipe_ref, (
        f"run-bottomup must reference strategy-bottomup sub-recipe, got: {recipe_ref!r}"
    )


def test_run_bottomup_has_condition_referencing_strategies():
    """run-bottomup step must have a condition referencing the 'strategies' context var."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "strategies", "run-bottomup")
    assert step is not None
    condition = step.get("condition", "")
    assert condition, "run-bottomup step must have a condition"
    assert "strategies" in condition, (
        f"run-bottomup condition must reference 'strategies' context var: {condition!r}"
    )


# ---------------------------------------------------------------------------
# combine stage: run-combine step (4 tests)
# ---------------------------------------------------------------------------


def test_combine_stage_has_run_combine_step():
    """combine stage must have a step with id='run-combine'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None, (
        f"No step with id='run-combine' found in combine stage. "
        f"Step IDs: {[s.get('id') for s in _get_stage_steps(data, 'combine')]}"
    )


def test_run_combine_is_recipe_type():
    """run-combine step must have type='recipe'."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None
    assert step.get("type") == "recipe", (
        f"run-combine step must have type='recipe', got: {step.get('type')!r}"
    )


def test_run_combine_references_discovery_combine():
    """run-combine step must reference the discovery-combine sub-recipe."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None
    recipe_ref = step.get("recipe", "")
    assert "discovery-combine" in recipe_ref, (
        f"run-combine must reference discovery-combine sub-recipe, got: {recipe_ref!r}"
    )


def test_run_combine_has_condition_referencing_strategies():
    """run-combine step must have a condition referencing the 'strategies' context var."""
    data = _load_recipe()
    step = _get_stage_step_by_id(data, "combine", "run-combine")
    assert step is not None
    condition = step.get("condition", "")
    assert condition, "run-combine step must have a condition"
    assert "strategies" in condition, (
        f"run-combine condition must reference 'strategies' context var: {condition!r}"
    )


# ---------------------------------------------------------------------------
# Sub-recipe files exist on disk (3 tests)
# ---------------------------------------------------------------------------


def test_strategy_topdown_sub_recipe_exists():
    """Sub-recipe file strategy-topdown.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "strategy-topdown.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe strategy-topdown.yaml not found at {sub_recipe}"
    )


def test_strategy_bottomup_sub_recipe_exists():
    """Sub-recipe file strategy-bottomup.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "strategy-bottomup.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe strategy-bottomup.yaml not found at {sub_recipe}"
    )


def test_discovery_combine_sub_recipe_exists():
    """Sub-recipe file discovery-combine.yaml must exist."""
    sub_recipe = REPO_ROOT / "recipes" / "discovery-combine.yaml"
    assert sub_recipe.exists(), (
        f"Sub-recipe discovery-combine.yaml not found at {sub_recipe}"
    )


# ---------------------------------------------------------------------------
# Final output (1 test)
# ---------------------------------------------------------------------------


def test_recipe_has_final_output():
    """Recipe must declare final_output."""
    data = _load_recipe()
    final_output = data.get("final_output", "")
    assert final_output, (
        f"Recipe must declare 'final_output', got: {final_output!r}"
    )
```

### Step 3: Run the new test file against the old recipe to see failures

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
python -m pytest tests/test_discovery_pipeline_recipe.py -v --tb=short 2>&1 | head -60
```

Expected partial output: metadata tests PASS, but `test_stage_prescan_exists`,
`test_stage_strategies_exists`, `test_stage_combine_exists`, `test_recipe_context_has_strategies`,
and all `run-topdown`/`run-bottomup`/`run-combine` step tests FAIL. This is correct TDD behavior
— the test file defines the target, the recipe doesn't match yet.

### Step 4: Rewrite `recipes/discovery-pipeline.yaml`

Replace `recipes/discovery-pipeline.yaml` entirely (the current 521-line file) with:

```yaml
name: "discovery-pipeline"
description: >
  Thin orchestrator for Parallax Discovery. Coordinates prescan, strategy
  dispatch, and combination in three stages. Stage 1 scans the repository
  structure and presents an approval gate so the user can review what was
  found before dispatching agents. Stage 2 dispatches strategy-topdown
  and/or strategy-bottomup as sub-recipes based on the 'strategies' context
  variable (default: 'both' — runs both in sequence). Stage 3 runs
  discovery-combine when both strategies ran, producing a unified output
  with convergence/divergence analysis. Accepts 'strategies' context var:
  'topdown' (conceptual only), 'bottomup' (empirical only), or 'both'
  (full Parallax analysis with comparison). Backward-compatible with the
  previous monolith API — same context vars, same approval gate.
version: "1.0.0"
author: "DOT Graph Bundle"
tags: ["discovery", "pipeline", "architecture", "dot-graph", "multi-agent"]

recursion:
  max_depth: 4
  max_total_steps: 300

context:
  repo_path: ""             # Required: path to target repository
  fidelity: "standard"      # Optional: quick | standard | deep (default: standard)
  output_dir: ""            # Optional: defaults to {{repo_path}}/.discovery
  render_png: "true"        # Optional: render combined DOTs to PNG (default: true)
  strategies: "both"        # Optional: topdown | bottomup | both (default: both)
  _approval_message: ""     # Populated by engine on approval

stages:
  # ---------------------------------------------------------------------------
  # Stage 1: prescan — detect changes and scan repository structure
  # Determines whether a full run is needed (via change detection),
  # maps the repository layout, and presents an approval gate.
  # No strategy-specific logic here — the pipeline stays thin.
  # ---------------------------------------------------------------------------
  - name: "prescan"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Change detection — resolve output_dir and check for changes
      # Resolves default output_dir, reads last-run.json if present, computes
      # git diff to determine tier: 'skip', 'incremental', or 'full'.
      # Always runs (no condition). Always produces change_result.
      # -----------------------------------------------------------------------
      - id: "change-detect"
        type: "bash"
        output: "change_result"
        parse_json: true
        timeout: 30
        command: |
          python3 - <<'EOF'
          import json
          import subprocess
          from pathlib import Path

          repo_path = "{{repo_path}}"
          output_dir = "{{output_dir}}"

          # Resolve default output_dir
          if not output_dir:
              output_dir = str(Path(repo_path) / ".discovery")

          result = {
              "repo_path": repo_path,
              "output_dir": output_dir,
              "tier": "full",
              "current_commit": "",
              "last_commit": "",
              "changed_files": [],
          }

          # Get current git commit
          try:
              current_commit = subprocess.check_output(
                  ["git", "-C", repo_path, "rev-parse", "HEAD"],
                  text=True,
                  stderr=subprocess.DEVNULL,
              ).strip()
              result["current_commit"] = current_commit
          except Exception:
              current_commit = ""

          # Check last-run.json for previous commit
          last_run_path = Path(output_dir) / "last-run.json"
          if last_run_path.exists():
              try:
                  last_run = json.loads(last_run_path.read_text())
                  last_commit = last_run.get("commit_hash", "")
                  result["last_commit"] = last_commit
                  if last_commit and last_commit == current_commit:
                      result["tier"] = "skip"
                  elif last_commit and current_commit:
                      try:
                          changed = subprocess.check_output(
                              ["git", "-C", repo_path, "diff", "--name-only",
                               last_commit, current_commit],
                              text=True,
                              stderr=subprocess.DEVNULL,
                          ).strip().splitlines()
                          result["changed_files"] = changed
                          result["tier"] = "incremental" if changed else "skip"
                      except Exception:
                          result["tier"] = "full"
              except Exception:
                  pass

          # Create output directory
          Path(output_dir).mkdir(parents=True, exist_ok=True)

          print(json.dumps(result))
          EOF

      # -----------------------------------------------------------------------
      # Step 2: Structural scan — map the repository layout
      # Invokes amplifier_module_tool_dot_graph.prescan with fallback to
      # basic directory listing. Skipped if tier=='skip'.
      # Produces scan_result with repo structure for the approval gate prompt.
      # -----------------------------------------------------------------------
      - id: "structural-scan"
        type: "bash"
        condition: "{{change_result.tier}} != 'skip'"
        output: "scan_result"
        parse_json: true
        timeout: 60
        command: |
          python3 - <<'EOF'
          import json
          from pathlib import Path

          repo_path = "{{change_result.repo_path}}"
          output_dir = "{{change_result.output_dir}}"

          result = {
              "repo_path": repo_path,
              "output_dir": output_dir,
              "structure": {},
              "error": None,
          }

          try:
              from amplifier_module_tool_dot_graph import prescan
              structure = prescan.prescan_repo(repo_path)
              result["structure"] = structure
          except Exception as e:
              try:
                  top_level = []
                  for entry in sorted(Path(repo_path).iterdir()):
                      if entry.name.startswith("."):
                          continue
                      top_level.append({
                          "name": entry.name,
                          "type": "dir" if entry.is_dir() else "file",
                      })
                  result["structure"] = {"top_level": top_level, "source": "fallback"}
                  result["error"] = f"prescan unavailable ({e}), used fallback listing"
              except Exception as e2:
                  result["error"] = f"structural scan failed: {e2}"

          # Write prescan-result.json
          prescan_path = Path(output_dir) / "prescan-result.json"
          prescan_path.write_text(json.dumps(result, indent=2))

          print(json.dumps(result))
          EOF

    approval_gate:
      required: true
      prompt: |
        Discovery Pipeline — Prescan Complete

        Repository:  {{change_result.repo_path}}
        Fidelity:    {{fidelity}}
        Strategies:  {{strategies}}
        Output dir:  {{change_result.output_dir}}
        Change tier: {{change_result.tier}}

        What will run:
          strategies='both':     strategy-topdown + strategy-bottomup, then discovery-combine
          strategies='topdown':  strategy-topdown only (no combine stage)
          strategies='bottomup': strategy-bottomup only (no combine stage)

        Type APPROVE to proceed with strategy dispatch, or DENY to cancel.

  # ---------------------------------------------------------------------------
  # Stage 2: strategies — dispatch strategy sub-recipes
  # Calls strategy-topdown and/or strategy-bottomup based on the 'strategies'
  # context variable. Each strategy writes to its own investigation directory
  # and runs fully unattended. Both conditions evaluated independently, so
  # strategies="both" dispatches both in sequence.
  # ---------------------------------------------------------------------------
  - name: "strategies"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Run top-down strategy
      # Runs when strategies == 'topdown' or strategies == 'both'.
      # Calls strategy-topdown.yaml as a sub-recipe. Writes to
      # .discovery/investigation/topdown/ within the output_dir.
      # -----------------------------------------------------------------------
      - id: "run-topdown"
        type: "recipe"
        condition: "{{strategies}} == 'topdown' or {{strategies}} == 'both'"
        recipe: "@dot-graph:recipes/strategy-topdown.yaml"
        context:
          repo_path: "{{change_result.repo_path}}"
          fidelity: "{{fidelity}}"
          output_dir: "{{change_result.output_dir}}/investigation/topdown"
        output: "topdown_result"
        timeout: 14400

      # -----------------------------------------------------------------------
      # Step 2: Run bottom-up strategy
      # Runs when strategies == 'bottomup' or strategies == 'both'.
      # Calls strategy-bottomup.yaml as a sub-recipe. Writes to
      # .discovery/investigation/bottomup/ within the output_dir.
      # -----------------------------------------------------------------------
      - id: "run-bottomup"
        type: "recipe"
        condition: "{{strategies}} == 'bottomup' or {{strategies}} == 'both'"
        recipe: "@dot-graph:recipes/strategy-bottomup.yaml"
        context:
          repo_path: "{{change_result.repo_path}}"
          fidelity: "{{fidelity}}"
          output_dir: "{{change_result.output_dir}}/investigation/bottomup"
        output: "bottomup_result"
        timeout: 14400

  # ---------------------------------------------------------------------------
  # Stage 3: combine — produce unified output with convergence/divergence
  # Runs only when strategies == 'both'. Calls discovery-combine.yaml which
  # reads both investigation directories and invokes the discovery-combiner
  # agent to classify findings. Writes to .discovery/output/.
  # ---------------------------------------------------------------------------
  - name: "combine"
    steps:
      # -----------------------------------------------------------------------
      # Step 1: Run discovery-combine — unify both strategy outputs
      # Reads topdown and bottomup investigation directories, invokes the
      # discovery-combiner agent, produces combined.dot + discrepancies.md.
      # Skipped when strategies != 'both' (only one strategy ran).
      # -----------------------------------------------------------------------
      - id: "run-combine"
        type: "recipe"
        condition: "{{strategies}} == 'both'"
        recipe: "@dot-graph:recipes/discovery-combine.yaml"
        context:
          repo_path: "{{change_result.repo_path}}"
          output_dir: "{{change_result.output_dir}}/output"
          render_png: "{{render_png}}"
        output: "combine_result"
        timeout: 7200

final_output: "combine_result"
```

### Step 5: Run the new pipeline tests to verify they all pass

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
python -m pytest tests/test_discovery_pipeline_recipe.py -v --tb=short
```

Expected: all 51 tests PASS.

### Step 6: Commit both files together

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
git add recipes/discovery-pipeline.yaml tests/test_discovery_pipeline_recipe.py
git commit -m "refactor: rewrite discovery-pipeline.yaml as thin orchestrator + update pipeline tests"
```

---

## Task 4: Update `test_final_verification.py` (40 → 42) + full test suite

**Files:**
- Modify: `tests/test_final_verification.py`

### Step 1: Read the current file

```
cat /home/bkrabach/dev/amplifier-bundle-dot-graph/tests/test_final_verification.py
```

### Step 2: Apply the update

Make these targeted changes to `tests/test_final_verification.py`:

**Change 1 — Update docstring** (lines 1-7):

Old:
```python
"""Final verification of complete file tree, imports, scripts, YAML, skills, and file count.

Task 18: Verifies all 40 bundle files are present and functional.
Phase A v2: Updated to include 8 new discovery agent and context files.
Phase B v2: Updated to include 3 new synthesizer sub-recipes (total 38).
Phase C v2: Updated to include 2 new strategy recipes (total 40).
"""
```

New:
```python
"""Final verification of complete file tree, imports, scripts, YAML, skills, and file count.

Task 18: Verifies all 42 bundle files are present and functional.
Phase A v2: Updated to include 8 new discovery agent and context files.
Phase B v2: Updated to include 3 new synthesizer sub-recipes (total 38).
Phase C v2: Updated to include 2 new strategy recipes (total 40).
Phase D v2: Updated to include 2 new orchestrator recipes (total 42).
"""
```

**Change 2 — Update EXPECTED_FILES comment and add 2 new entries:**

Find the line:
```python
# The 40 expected bundle files (21 original + 3 Phase A + 3 Phase D recipes + 8 Phase A v2 + 3 Phase B v2 + 2 Phase C v2)
```
Replace with:
```python
# The 42 expected bundle files (21 original + 3 Phase A + 3 Phase D recipes + 8 Phase A v2 + 3 Phase B v2 + 2 Phase C v2 + 2 Phase D v2)
```

Find the last line of EXPECTED_FILES (currently):
```python
    # Phase C v2: strategy recipes
    "recipes/strategy-topdown.yaml",
    "recipes/strategy-bottomup.yaml",
]
```
Replace with:
```python
    # Phase C v2: strategy recipes
    "recipes/strategy-topdown.yaml",
    "recipes/strategy-bottomup.yaml",
    # Phase D v2: orchestrator recipes
    "recipes/discovery-combine.yaml",
    "recipes/strategy-sequential.yaml",
]
```

**Change 3 — Update the file count comment:**

Find:
```python
# --- Step 1: Complete file tree (35 files) ---
```
Replace with:
```python
# --- Step 1: Complete file tree (42 files) ---
```

**Change 4 — Update `test_total_file_count`:**

Find:
```python
def test_total_file_count():
    """Step 6: Total bundle file count is exactly 40 (38 prior + 2 Phase C v2)."""
    present = [f for f in EXPECTED_FILES if (REPO_ROOT / f).exists()]
    assert len(present) == 40, (
        f"Expected 40 bundle files, found {len(present)}. "
        f"Missing: {[f for f in EXPECTED_FILES if f not in present]}"
    )
```
Replace with:
```python
def test_total_file_count():
    """Step 6: Total bundle file count is exactly 42 (40 prior + 2 Phase D v2)."""
    present = [f for f in EXPECTED_FILES if (REPO_ROOT / f).exists()]
    assert len(present) == 42, (
        f"Expected 42 bundle files, found {len(present)}. "
        f"Missing: {[f for f in EXPECTED_FILES if f not in present]}"
    )
```

### Step 3: Run the final verification tests

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
python -m pytest tests/test_final_verification.py -v --tb=short
```

Expected: all 53 tests PASS (51 prior + 2 new parametrized file-existence tests for the new recipe files).

### Step 4: Run the complete test suite

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
python -m pytest tests/ modules/tool-dot-graph/tests/ --tb=short 2>&1 | tail -20
```

Expected: all tests pass. If any failures appear:
- `test_discovery_combine_recipe.py` failures → check `recipes/discovery-combine.yaml` from Task 1
- `test_strategy_sequential_recipe.py` failures → check `recipes/strategy-sequential.yaml` from Task 2
- `test_discovery_pipeline_recipe.py` failures → check `recipes/discovery-pipeline.yaml` from Task 3
- `test_final_verification.py::test_total_file_count` failure → confirm both new recipe files exist

### Step 5: Commit

```
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
git add tests/test_final_verification.py
git commit -m "test: update test_final_verification.py to 42 files with Phase D v2 orchestrator recipes"
```

---

## Verification Checklist

After all four tasks, confirm:

```bash
# 1. All tests pass
cd /home/bkrabach/dev/amplifier-bundle-dot-graph
python -m pytest tests/ modules/tool-dot-graph/tests/ -v --tb=short 2>&1 | tail -5

# 2. New recipe files present
ls -la recipes/discovery-combine.yaml recipes/strategy-sequential.yaml

# 3. New test files present
ls -la tests/test_discovery_combine_recipe.py tests/test_strategy_sequential_recipe.py

# 4. Four new commits
git log --oneline -5
```

Expected git log (most recent first):
```
<sha> test: update test_final_verification.py to 42 files with Phase D v2 orchestrator recipes
<sha> refactor: rewrite discovery-pipeline.yaml as thin orchestrator + update pipeline tests
<sha> feat: add strategy-sequential.yaml recipe and tests (sequential orchestrator with approval gate)
<sha> feat: add discovery-combine.yaml recipe and tests (convergence/divergence combiner)
```

---

## Summary of Changes

| File | Action | Description |
|---|---|---|
| `recipes/discovery-combine.yaml` | **Create** | Flat 4-step recipe: check-inputs → combine (discovery-combiner agent) → validate → render |
| `tests/test_discovery_combine_recipe.py` | **Create** | 28 tests: flat structure, context vars, step types, agent reference |
| `recipes/strategy-sequential.yaml` | **Create** | 3-stage orchestrator: bottomup → [approval gate] → topdown → combine; no novel agents |
| `tests/test_strategy_sequential_recipe.py` | **Create** | 30 tests: staged structure, approval gate on bottomup, bottomup_context passthrough |
| `recipes/discovery-pipeline.yaml` | **Rewrite** | 521-line monolith → 3-stage thin orchestrator (prescan/strategies/combine) |
| `tests/test_discovery_pipeline_recipe.py` | **Rewrite** | Old monolith tests (688 lines) → new thin-orchestrator tests (51 tests) |
| `tests/test_final_verification.py` | **Modify** | EXPECTED_FILES 40→42, test_total_file_count assertion 40→42, docstring updated |

**New test counts:**
- `test_discovery_combine_recipe.py`: 28 tests
- `test_strategy_sequential_recipe.py`: 30 tests
- `test_discovery_pipeline_recipe.py`: 51 tests (rewritten from old structure)
- `test_final_verification.py`: 53 tests (was 51; +2 parametrized file checks)

**Key design decisions captured:**
- `discovery-combine.yaml` uses **flat steps** (building-block recipe, like synthesize-*.yaml) not staged
- `strategy-sequential.yaml` uses **staged** structure (strategy recipe, like strategy-topdown/bottomup)
- `discovery-pipeline.yaml` uses **staged** structure with approval gate on the prescan stage
- The approval gate moves from scan→prescan for accuracy: user now sees scan results before dispatch
- `strategies` context var enables single-strategy runs without code changes
- `_approval_message` kept for backward compatibility with scripts that pass it
