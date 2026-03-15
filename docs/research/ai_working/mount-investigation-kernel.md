# Kernel Internals Investigation: Tool Module mount() Validation

**Date**: 2026-03-14
**Investigator**: Core Expert (Kernel Specialist)
**Scope**: amplifier-core validation subsystem — why agents produce broken mount() stubs

---

## Executive Summary

The amplifier-core kernel has a **rigorous, multi-step validation pipeline** for tool modules. The specific error `"protocol_compliance: No tool was mounted and mount() did not return a Tool instance"` is produced by `ToolValidator._check_protocol_compliance()` in `python/amplifier_core/validation/tool.py` (line 260). It fires when mount() both:

1. Does NOT call `coordinator.mount("tools", ...)` to register anything, AND
2. Returns `None` (or a non-Tool value) instead of returning a Tool instance directly.

**Root cause of broken agent-generated stubs**: Agents write `mount()` as a placeholder that returns `None` without calling `coordinator.mount()`. The validator **actually executes mount()** against a `MockCoordinator` and inspects what happened. A no-op mount() triggers a hard validation failure.

---

## 1. What Does the Module Validator Check?

The `ToolValidator` (in `python/amplifier_core/validation/tool.py`) runs **4 sequential checks**. Each can short-circuit on failure:

### Check 1: `module_importable`
- Can the module be imported at all?
- For directories: requires `__init__.py`
- For files: uses `importlib.util.spec_from_file_location()`
- **Short-circuits on failure** — remaining checks are skipped

### Check 2: `mount_exists`
- Does the module have a `mount` attribute?
- Is it callable?
- **Short-circuits on failure**

### Check 3: `mount_signature`
- Does `mount()` have at least 2 parameters? (coordinator, config)
- Is it `async`? (`asyncio.iscoroutinefunction()`)
- **Does NOT short-circuit** — continues even on failure

### Check 4: `protocol_compliance` (THE CRITICAL ONE)
- Creates a `MockCoordinator` (from `amplifier_core.testing`)
- **Actually calls `await mount_fn(coordinator, config)`**
- Then inspects `coordinator.mount_points.get("tools", {})` to see what was mounted
- If nothing was mounted, checks whether `mount()` returned a Tool instance directly
- If neither path produced a Tool → **ERROR**: `"No tool was mounted and mount() did not return a Tool instance"`

If tools WERE mounted via coordinator, it additionally checks each mounted object:
- **`tool_name`**: `tool.name` must be a non-empty string
- **`tool_description`**: `tool.description` must be a non-empty string (warning, not error)
- **`tool_execute`**: `tool.execute` must exist, be async, and accept an `input` parameter

### Validation Severity Levels

From `python/amplifier_core/validation/base.py`:

| Severity | Impact |
|----------|--------|
| `error` | Causes `result.passed` to be `False` — validation fails |
| `warning` | Recorded but does NOT fail validation |
| `info` | Informational, always passes |

`ValidationResult.passed` is `True` only if **all error-severity checks passed**.

---

## 2. Minimum Viable mount() Function

There are **two valid patterns** that pass validation. Both are accepted by `_check_protocol_compliance()`:

### Pattern A: Mount via Coordinator (PREFERRED)

```python
from amplifier_core import ModuleCoordinator, ToolResult

class MyTool:
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "Does a thing."

    async def execute(self, input: dict) -> ToolResult:
        return ToolResult(success=True, output="done")

async def mount(coordinator: ModuleCoordinator, config: dict):
    tool = MyTool()
    await coordinator.mount("tools", tool, name="my_tool")
    return tool
```

The validator checks `coordinator.mount_points.get("tools", {})` — this is how it finds what was mounted.

### Pattern B: Return Tool Instance Directly (ALTERNATIVE)

```python
async def mount(coordinator: ModuleCoordinator, config: dict):
    tool = MyTool()
    # No coordinator.mount() call — but returning the Tool satisfies validation
    return tool
```

The validator falls through to `isinstance(mount_result, Tool)` check at line 235.

### What Does NOT Work (The Broken Stub)

```python
async def mount(coordinator, config):
    return None  # FAILS: nothing mounted AND no Tool returned
```

```python
async def mount(coordinator, config):
    pass  # FAILS: implicit None return, nothing mounted
```

### Edge Case: Cleanup Callable

```python
async def mount(coordinator, config):
    # Mount nothing, but return a callable
    return lambda: None  # WARNING (not error): "returned a cleanup callable (no tool mounted yet)"
```

This produces a **warning**, not an error. The validator gives this a pass since it might be conditional mounting.

---

## 3. Formal Contract Document

**Location**: `amplifier-core/docs/contracts/TOOL_CONTRACT.md`

Key sections relevant to mount():

### Entry Point Pattern (lines 98-113)

The contract specifies the mount() signature and its return semantics:

```python
async def mount(coordinator: ModuleCoordinator, config: dict) -> Tool | Callable | None:
    """
    Initialize and register tool.

    Returns:
        - Tool instance
        - Cleanup callable (for resource cleanup)
        - None for graceful degradation
    """
    tool = MyTool(config=config)
    await coordinator.mount("tools", tool, name="my-tool")
    return tool
```

### Validation Checklist (lines 253-268)

The contract documents what's required vs recommended:

**Required:**
- Implements Tool protocol (name, description, execute)
- `mount()` function with entry point in pyproject.toml
- Returns `ToolResult` from execute()
- Handles errors gracefully

**Recommended:**
- Provides JSON schema via `get_schema()`
- Validates input before processing
- Logs operations
- Registers observability events

### Quick Validation Command (line 310)

```bash
amplifier-core validate tool ./my-tool --type tool
```

**IMPORTANT NOTE**: The contract says `None` is valid for "graceful degradation" — but the validator treats a bare `None` return (with nothing mounted) as an ERROR. This is a **documentation/behavior mismatch** that contributes to agent confusion. The contract implies `None` is acceptable; the validator says it isn't (unless a callable cleanup was returned).

---

## 4. Exact Validation Flow

### At Module Load Time (ModuleLoader)

File: `python/amplifier_core/loader.py`

The flow when loading via source resolver (the common path):

```
ModuleLoader.load(module_id, config, source_hint, coordinator)
  │
  ├── Resolve source (via ModuleSourceResolver or direct discovery)
  │     └── source.resolve() → module_path
  │
  ├── Add module_path to sys.path
  │
  ├── Check transport (wasm/grpc/python) — non-Python skips validation
  │
  ├── _validate_module(module_id, module_path, config)    ← VALIDATION HAPPENS HERE
  │     │
  │     ├── _get_module_metadata() → (module_type, mount_point)
  │     │     Uses __amplifier_module_type__ attribute or naming convention fallback
  │     │
  │     ├── Select validator: {"tool": ToolValidator, "provider": ProviderValidator, ...}
  │     │
  │     ├── _find_package_dir() → Python package path
  │     │
  │     └── validator.validate(package_path, config=config)
  │           │
  │           ├── Check 1: _check_importable()
  │           ├── Check 2: _check_mount_exists()
  │           ├── Check 3: _check_mount_signature()
  │           └── Check 4: _check_protocol_compliance()   ← The critical check
  │                 │
  │                 ├── Create MockCoordinator
  │                 ├── await mount_fn(coordinator, config or {})
  │                 ├── Inspect coordinator.mount_points["tools"]
  │                 ├── If empty: check mount_result isinstance(Tool)
  │                 ├── If still nothing: ERROR "No tool was mounted..."
  │                 └── If found: _check_tool_methods() on each
  │
  ├── If validation FAILS → raise ModuleValidationError
  │     Error message: "Module '{id}' failed validation: {summary}. Errors: {details}"
  │
  └── Load entry point or filesystem mount function → return mount closure
```

### Error Message Formatting (loader.py line 582-584)

```python
error_details = "; ".join(f"{e.name}: {e.message}" for e in result.errors)
raise ModuleValidationError(
    f"Module '{module_id}' failed validation: {result.summary()}. Errors: {error_details}"
)
```

This produces the exact error the user reported:
```
Module 'my-tool' failed validation: FAILED: 3/4 checks passed (1 errors, 0 warnings).
Errors: protocol_compliance: No tool was mounted and mount() did not return a Tool instance
```

---

## 5. Examples of Stub/Placeholder Modules in Core

### In test_validation.py — The Minimal Passing Tool Module

```python
# From TestValidatorWithConfig (line 753-773)
# This is the CANONICAL test fixture showing a minimal valid tool mount()

from amplifier_core import ModuleCoordinator, ToolResult

async def mount(coordinator: ModuleCoordinator, config):
    enabled = config.get("enabled", True)
    if not enabled:
        return None  # Graceful degradation — but FAILS validation!

    class MockTool:
        name = "mock-tool"
        description = "A mock tool"

        async def execute(self, input):
            return ToolResult(success=True, output={"result": "mock"})

    tool = MockTool()
    await coordinator.mount("tools", tool, name="mock")
    return None
```

### In testing.py — MockTool (line 67-80)

```python
class MockTool:
    """Mock tool for testing."""

    def __init__(self, name: str = "mock_tool", output: Any = "Success"):
        self.name = name
        self.description = f"Mock tool: {name}"
        self.output = output
        self.input_schema = {"type": "object", "properties": {}}
        self.execute = AsyncMock(side_effect=self._execute)
        self.call_count = 0

    async def _execute(self, input: dict) -> ToolResult:
        self.call_count += 1
        return ToolResult(success=True, output=self.output)
```

### In pytest_plugin.py — How Tests Load Modules (line 478-507)

The pytest plugin's `tool_module` fixture calls `_load_module()` then checks:
```python
tools = coordinator.mount_points.get("tools", {})
if not tools:
    pytest.fail("No tool was mounted")
```

This is the SAME check pattern as the validator — confirming that `coordinator.mount("tools", ...)` is the expected path.

---

## 6. Error Messages Produced by the Validator

### Complete Error Catalog (for tool modules)

| Check Name | Error Message | When Triggered |
|-----------|---------------|----------------|
| `module_importable` | `"No __init__.py found in {path}"` | Directory without __init__.py |
| `module_importable` | `"Failed to import module: {e}"` | ImportError during load |
| `module_importable` | `"Error loading module: {e}"` | Any exception during load |
| `mount_exists` | `"No mount() function found in module"` | No `mount` attribute |
| `mount_exists` | `"mount is not callable"` | `mount` exists but isn't callable |
| `mount_signature` | `"mount() should have at least 2 parameters (coordinator, config), found {n}"` | Too few params |
| `mount_signature` | `"mount() should be async (async def mount(...))"` | Sync mount function |
| `protocol_compliance` | `"No tool was mounted and mount() did not return a Tool instance"` | **THE ERROR** — nothing mounted, nothing returned |
| `protocol_compliance` | `"Tool '{name}' does not implement Tool protocol"` | Mounted object fails isinstance(Tool) |
| `protocol_compliance` | `"Error during protocol compliance check: {e}"` | Exception during mount() execution |
| `tool_name` | `"Tool.name should be a non-empty string"` | name is empty or wrong type |
| `tool_name` | `"Error accessing Tool.name: {e}"` | name property raises |
| `tool_description` | `"Tool.description should be a non-empty string"` | (warning only) |
| `tool_execute` | `"Tool missing execute() method"` | No execute attribute |
| `tool_execute` | `"Tool.execute() should be async"` | Sync execute method |
| `tool_execute` | `"Tool.execute() should accept input parameter"` | Missing input param |

### Clarity Assessment

The error messages are **adequate for a human developer** but **problematic for an AI agent** because:

1. **"No tool was mounted and mount() did not return a Tool instance"** — This tells you WHAT failed but not HOW to fix it. An agent needs to know: "call `await coordinator.mount('tools', tool, name='my-tool')`"

2. **The contract document says `None` is valid** ("None for graceful degradation") but the validator rejects it. An agent reading the contract might reasonably produce `return None`.

3. **No positive example in the error message** — The validator could say "Hint: call `await coordinator.mount('tools', your_tool, name='tool-name')` inside mount()" but doesn't.

---

## 7. Discoverability Analysis

### Where Would an Agent Look?

| Source | Findable? | Quality for AI? |
|--------|-----------|----------------|
| `TOOL_CONTRACT.md` | Yes (in docs/contracts/) | Shows correct pattern but also says `None` is valid |
| `amplifier-core validate` CLI | Yes | Only useful after code is written |
| `validation/tool.py` source | Requires source diving | Very clear if you read it |
| `testing.py` MockTool | Yes (referenced in contract) | Good structural example |
| Test fixtures in `test_validation.py` | Requires finding tests | Best minimal examples |
| Error messages at runtime | Yes (after failure) | Tell what's wrong, not how to fix |

### The Gap

The **contract document** (TOOL_CONTRACT.md) is the right place for agents to learn, and it DOES show the correct pattern. But:

1. **The mount() docstring in the contract says `-> Tool | Callable | None`** — implying all three are equally valid returns. In reality, `None` without a `coordinator.mount()` call is an error.

2. **No "anti-pattern" section** — The contract doesn't show what NOT to do. For AI agents, showing the broken pattern alongside the correct one would be highly effective.

3. **The two valid paths (coordinator.mount vs. direct return) aren't explicitly contrasted** — An agent doesn't know that at least one MUST happen.

---

## 8. Root Cause Analysis: Why Agents Produce Broken Stubs

### The Failure Mode

Agents generate:
```python
async def mount(coordinator, config):
    # TODO: implement
    return None
```

This passes checks 1-3 (importable, mount exists, correct signature) but fails check 4 (protocol compliance).

### Why This Happens

1. **`mount()` looks like a lifecycle hook** — Agents familiar with frameworks like pytest fixtures or Django middleware assume `mount()` is called by the framework and just needs to exist. They don't understand it must ACTIVELY register something.

2. **The return type `Tool | Callable | None` is misleading** — `None` appears to be a valid return, and it IS according to the docstring, but only if you've already called `coordinator.mount()`.

3. **No structural enforcement** — The signature `mount(coordinator, config)` doesn't communicate that `coordinator.mount()` MUST be called. The coordinator is just a parameter, not a required interaction point.

4. **The "mount" name is overloaded** — The module-level `mount()` function and `coordinator.mount()` method share a name but serve different purposes. The module mount() is "initialize yourself", the coordinator mount() is "register yourself with the system."

### Recommendations for Upstream

1. **Clarify the contract**: The TOOL_CONTRACT.md should explicitly state: "mount() MUST either call `await coordinator.mount('tools', tool, name=...)` OR return a Tool instance. Returning None without mounting is a validation error."

2. **Improve the error message**: Change from:
   > "No tool was mounted and mount() did not return a Tool instance"

   To:
   > "No tool was mounted. mount() must either call `await coordinator.mount('tools', tool_instance, name='tool-name')` or return a Tool instance directly. See TOOL_CONTRACT.md."

3. **Add anti-patterns to contract docs**: Show the broken stub and explain why it fails.

4. **Consider a stub generator**: `amplifier-core scaffold tool my-tool` that produces a valid skeleton.

---

## 9. The Protocol Compliance Check — Detailed Code Walkthrough

From `python/amplifier_core/validation/tool.py`, lines 205-296:

```python
async def _check_protocol_compliance(self, result, mount_fn, config=None):
    coordinator = MockCoordinator()       # Fresh mock coordinator
    mount_result = None

    try:
        actual_config = config if config is not None else {}
        mount_result = await mount_fn(coordinator, actual_config)  # ACTUALLY CALLS mount()

        tools = coordinator.mount_points.get("tools", {})  # Check what was mounted
        if not tools:
            # Path 1: Nothing mounted via coordinator — check return value
            if mount_result is not None and isinstance(mount_result, Tool):
                # OK: returned a Tool directly
                self._check_tool_methods(result, mount_result)
                return
            if callable(mount_result):
                # WARNING: returned a cleanup callable, no tool
                return
            # FAIL: nothing mounted AND nothing useful returned
            result.add(ValidationCheck(
                name="protocol_compliance",
                passed=False,
                message="No tool was mounted and mount() did not return a Tool instance",
                severity="error",
            ))
            return

        # Path 2: Something was mounted — check each one
        for name, tool in tools.items():
            if isinstance(tool, Tool):
                self._check_tool_methods(result, tool)
            else:
                result.add(ValidationCheck(..., passed=False, ...))

    except Exception as e:
        result.add(ValidationCheck(..., passed=False, message=f"Error during protocol compliance check: {e}"))
    finally:
        # Cleanup: call any cleanup function returned or registered
        if mount_result is not None and callable(mount_result):
            await mount_result()
        if hasattr(coordinator, "_cleanup_functions"):
            for cleanup_fn in coordinator._cleanup_functions:
                await cleanup_fn()
```

Key insight: The validator uses `MockCoordinator` which is a real subclass of `ModuleCoordinator` (the Rust-backed coordinator). It tracks `mount_history` and delegates to the real `super().mount()`. This means `coordinator.mount_points["tools"]` reflects what the module actually registered.

---

## 10. The Tool Protocol (isinstance check)

From `python/amplifier_core/interfaces.py`, lines 134-158:

```python
@runtime_checkable
class Tool(Protocol):
    @property
    def name(self) -> str: ...

    @property
    def description(self) -> str: ...

    async def execute(self, input: dict[str, Any]) -> ToolResult: ...
```

Because this is `@runtime_checkable`, `isinstance(obj, Tool)` works at runtime. The validator uses this to verify that what was mounted actually satisfies the protocol structurally. A class needs `name`, `description`, and `execute` to pass the isinstance check.

**Note**: `@runtime_checkable` only checks method/property EXISTENCE, not signatures or return types. The validator does additional signature checks in `_check_tool_methods()`.

---

## 11. Summary: The Absolute Minimum Valid Tool Module

```python
"""Minimal valid Amplifier tool module."""
from amplifier_core import ModuleCoordinator, ToolResult

class MinimalTool:
    @property
    def name(self) -> str:
        return "minimal"

    @property
    def description(self) -> str:
        return "A minimal tool."

    async def execute(self, input: dict) -> ToolResult:
        return ToolResult(success=True, output="ok")

async def mount(coordinator: ModuleCoordinator, config: dict):
    tool = MinimalTool()
    await coordinator.mount("tools", tool, name="minimal")
    return tool
```

This passes all 4 validation checks plus all sub-checks (tool_name, tool_description, tool_execute).
