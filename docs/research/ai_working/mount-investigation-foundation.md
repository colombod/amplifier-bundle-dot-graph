# mount() Investigation: Foundation Documentation Gap Analysis

**Investigator**: foundation-expert agent  
**Date**: 2026-03-14  
**Scope**: amplifier-foundation documentation, context files, examples, and their coverage of the `mount()` → `coordinator.mount()` contract for tool modules

---

## Executive Summary

There is a **clear and systemic documentation gap** between where the `mount()` contract is authoritatively documented (amplifier-core) and what agents actually see when building tool modules (amplifier-foundation context). The TOOL_CONTRACT.md in amplifier-core clearly shows the correct pattern, but **no foundation context file, agent instruction, or skill teaches agents how to write a proper `mount()` function**. The modular-builder agent — the primary implementation agent — has zero knowledge of the Amplifier module `mount()` contract. When agents are asked to create tool modules, they're operating from general Python knowledge, not Amplifier-specific guidance, which produces the broken `mount()` stubs.

---

## 1. Where is the Tool Module Contract Documented?

### TOOL_CONTRACT.md — Lives in amplifier-core

**Location**: `amplifier-core/docs/contracts/TOOL_CONTRACT.md`  
**Size**: 317 lines, 7120 bytes  

The contract is clear, correct, and complete. The critical section (lines 96-113):

```python
## Entry Point Pattern

### mount() Function

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

### contracts/README.md Quick Start — Also correct

```python
# 2. Provide mount() function
async def mount(coordinator, config):
    """Initialize and register module."""
    instance = MyModule(config)
    await coordinator.mount("category", instance, name="my-module")
    return instance  # or cleanup function
```

### Verdict: The contract IS documented — but in amplifier-core, not amplifier-foundation

The documentation exists in `amplifier-core/docs/contracts/`. There are 5 contract documents:
- TOOL_CONTRACT.md
- HOOK_CONTRACT.md  
- PROVIDER_CONTRACT.md
- ORCHESTRATOR_CONTRACT.md
- CONTEXT_CONTRACT.md

Every single one shows the `coordinator.mount()` call pattern correctly. **But agents building modules through foundation never see these files.**

---

## 2. What Does BUNDLE_GUIDE.md Say About Creating Tool Modules?

### Answer: Almost nothing about mount()

The BUNDLE_GUIDE.md (1314 lines) is comprehensive about **bundle composition** but says almost nothing about **module implementation**. The only mention of `mount()` is in the Troubleshooting section (line 1287):

> ```
> ### "Module not found" errors
> - Verify `source:` path is correct relative to bundle location
> - Check module has `pyproject.toml` with entry point
> - Ensure `mount()` function exists in module
> ```

That's it. One bullet point. No example of what `mount()` should look like. No mention of `coordinator.mount()`. No mention of the Tool protocol. No link to TOOL_CONTRACT.md.

The guide shows how to **declare** tools in YAML:
```yaml
tools:
  - module: tool-my-capability
    source: git+https://...
```

But never shows how to **implement** the Python module that this YAML references.

### PATTERNS.md — Shows mount at the application level only

The PATTERNS.md file (492 lines) shows `coordinator.mount()` only in the context of **application-level programmatic mounting** (example 03_custom_tool.py pattern), not in the context of writing a proper module `mount()` function.

### CONCEPTS.md — Mentions mount() in passing

```python
# In mount() or tool execute()
working_dir = get_working_dir(coordinator)  # Returns Path
```

One line. No explanation of what `mount()` is or how to write one.

---

## 3. What Context Do Agents See When Creating Modules?

### modular-builder agent — ZERO Amplifier module knowledge

The modular-builder agent (630 lines, the primary implementation agent) loads these context files:
- `@foundation:context/IMPLEMENTATION_PHILOSOPHY.md`
- `@foundation:context/LANGUAGE_PHILOSOPHY.md`
- `@foundation:context/MODULAR_DESIGN_PHILOSOPHY.md`
- `@foundation:context/shared/PROBLEM_SOLVING_PHILOSOPHY.md`
- `@foundation:context/KERNEL_PHILOSOPHY.md`
- `@foundation:context/ISSUE_HANDLING.md`
- `@foundation:context/shared/common-agent-base.md`

**None of these files mention `mount()`, `coordinator.mount()`, the Tool protocol, or the Amplifier module contract.**

The modular-builder's concept of "module" is the generic software engineering concept (self-contained directory with `__init__.py`, public interface, tests). It shows this module structure:

```
module_name/
├── __init__.py       # Public interface via __all__
├── core.py          # Main implementation
├── models.py        # Data models if needed
├── utils.py         # Internal utilities
└── tests/
```

This is a generic Python module, not an Amplifier tool module. There is no mention of:
- `pyproject.toml` with `[project.entry-points."amplifier.modules"]`
- The `async def mount(coordinator, config)` signature
- The `await coordinator.mount("tools", tool, name=...)` call
- The `__amplifier_module_type__ = "tool"` metadata
- The Tool protocol (`name`, `description`, `execute()`, `input_schema`)
- `ToolResult` return type

### ecosystem-expert agent — Also no module creation knowledge

Knows about multi-repo workflows but nothing about writing module code.

### foundation-expert agent (me) — I know about bundles, not module internals

My context covers bundle composition, behavior patterns, and context architecture. I reference the TOOL_CONTRACT.md existence but don't carry its contents.

### context/shared/ files — Zero mount() guidance

Checked `common-system-base.md` and `common-agent-base.md` — neither mentions module creation patterns.

### IMPLEMENTATION_PHILOSOPHY.md — Mentions "tool modules" twice

Only in passing:
1. Line 199: About conventions via instructions for modules
2. Line 420: A code comment `# ✅ In tool modules that accept a path parameter`

Neither teaches the mount() contract.

### Skills — No module creation skill exists

Searched for skills related to "module" and "tool" — none exist. There is no skill for creating Amplifier modules.

---

## 4. What Are the Canonical Examples?

### tool-delegate (foundation's own tool) — The best example

**File**: `amplifier-foundation/modules/tool-delegate/amplifier_module_tool_delegate/__init__.py`

```python
__amplifier_module_type__ = "tool"

async def mount(coordinator: ModuleCoordinator, config: dict[str, Any] | None = None):
    """Mount the agent delegation tool."""
    config = config or {}
    tool = DelegateTool(coordinator, config)
    await coordinator.mount("tools", tool, name=tool.name)
    return  # No cleanup needed
```

This is a **correct, canonical example** that shows:
- `__amplifier_module_type__` metadata
- Proper `mount()` signature
- The critical `await coordinator.mount("tools", tool, name=...)` call
- Clean pattern

### example 03_custom_tool.py — Good but uses non-standard function name

```python
async def mount_custom_tools(coordinator, config: dict):
    weather = WeatherTool()
    database = DatabaseTool()
    await coordinator.mount("tools", weather, name=weather.name)
    await coordinator.mount("tools", database, name=database.name)
    return cleanup
```

This shows the correct `coordinator.mount()` pattern but the function is named `mount_custom_tools`, not `mount`, and it's used for programmatic post-session mounting, not as a module entry point.

### ai-os-repo modules — 13 correct examples from agent-created modules

Interestingly, these modules in the ai-os-repo were apparently created by agents and all follow the correct pattern:

```python
__amplifier_module_type__ = "tool"

async def mount(coordinator, config):
    """Mount the calendar tool."""
    from .tool import CalendarTool
    tool = CalendarTool(db_path=db_path)
    await coordinator.mount("tools", tool, name=tool.name)
```

These are all correct. But they were likely created during sessions where the agent had access to existing module examples to copy from. **The problem manifests when agents create modules in greenfield projects without existing examples to reference.**

### router-orchestrator example module — Correct

```python
async def mount(coordinator, config: dict[str, Any] | None = None):
    orchestrator = RoutingOrchestrator(config=config)
    await coordinator.mount("orchestrator", orchestrator)
    return cleanup
```

---

## 5. The Specific Gap: Where It SHOULD Be But ISN'T

### Gap 1: BUNDLE_GUIDE.md "Creating Local Modules" section is missing

The BUNDLE_GUIDE.md has a "Bundle with Local Modules" directory structure section (lines 409-426) and mentions `modules/` directories repeatedly, but **never shows what goes inside a module's `__init__.py`**. There should be a section like:

> ### Creating a Local Tool Module
> 
> When your behavior needs a custom tool, create it in `modules/`:
> ```
> modules/tool-my-capability/
> ├── pyproject.toml
> └── amplifier_module_tool_my_capability/
>     └── __init__.py
> ```
> 
> The `__init__.py` must export an async `mount()` function:
> ```python
> async def mount(coordinator, config=None):
>     tool = MyTool(config)
>     await coordinator.mount("tools", tool, name="my-tool")
> ```

This section doesn't exist.

### Gap 2: No foundation context file teaches the mount() contract

There is no file in `foundation/context/` that an agent could `@mention` to learn the module contract. The TOOL_CONTRACT.md lives in amplifier-core, which foundation agents can't reference via `@core:docs/contracts/TOOL_CONTRACT.md` because core isn't composed as a bundle.

### Gap 3: modular-builder has no Amplifier module knowledge

The modular-builder agent is the primary implementation agent, but its instructions are purely about generic software engineering modules. It has no concept of:
- Amplifier's module mount protocol
- The coordinator pattern
- Tool/Hook/Provider protocols
- pyproject.toml entry points

### Gap 4: No skill for creating Amplifier modules

There is no skill that an agent could load to learn the module creation pattern. A skill like `creating-amplifier-modules` would be the natural place for this knowledge.

### Gap 5: Example 03_custom_tool.py teaches the wrong pattern name

The example uses `mount_custom_tools()` as the function name and shows programmatic mounting, not the module entry point pattern. An agent reading this would learn `coordinator.mount()` but wouldn't know the function must be named exactly `mount` and exported from `__init__.py`.

---

## 6. The Validation Code Shows the Exact Error Path

**File**: `amplifier-core/python/amplifier_core/validation/tool.py` (lines 230-263)

```python
tools = coordinator.mount_points.get("tools", {})
if not tools:
    # Module might return the instance directly
    if mount_result is not None and isinstance(mount_result, Tool):
        # PASS: mount() returned a Tool instance directly
        ...
    if callable(mount_result):
        # WARNING: returned a cleanup callable but no tool mounted
        ...
    # FAIL: "No tool was mounted and mount() did not return a Tool instance"
    result.add(ValidationCheck(
        name="protocol_compliance",
        passed=False,
        message="No tool was mounted and mount() did not return a Tool instance",
        severity="error",
    ))
```

The validator checks:
1. Did something get mounted into `coordinator.mount_points["tools"]`? (via `coordinator.mount("tools", ...)`)
2. If not, did `mount()` return a Tool instance directly?
3. If not, did it return a callable (cleanup function)?
4. If none of the above → **FAIL**

A `mount()` that returns `None` and never calls `coordinator.mount()` hits case 4 every time.

---

## 7. Recommendations

### Immediate (Fix the most common failure mode)

#### 7A. Add a "Creating Tool Modules" section to BUNDLE_GUIDE.md

In the "Creating a Bundle Step-by-Step" section, after "Step 2: Create Behavior", add guidance for when the behavior includes a tool module:

```markdown
### Step 2b: Create Tool Module (if behavior includes custom tools)

If your behavior adds a tool, create the module in `modules/`:

\`\`\`
modules/tool-my-capability/
├── pyproject.toml
└── amplifier_module_tool_my_capability/
    └── __init__.py
\`\`\`

**pyproject.toml:**
\`\`\`toml
[project]
name = "amplifier-module-tool-my-capability"
version = "0.1.0"
dependencies = []  # amplifier-core is a peer dependency

[project.entry-points."amplifier.modules"]
tool-my-capability = "amplifier_module_tool_my_capability:mount"
\`\`\`

**__init__.py — The mount() function is CRITICAL:**
\`\`\`python
__amplifier_module_type__ = "tool"

from typing import Any
from amplifier_core import ModuleCoordinator, ToolResult

async def mount(coordinator: ModuleCoordinator, config: dict[str, Any] | None = None):
    """Mount the tool. MUST call coordinator.mount() to register the tool."""
    config = config or {}
    tool = MyCapabilityTool(config)
    await coordinator.mount("tools", tool, name="my_capability")

class MyCapabilityTool:
    name = "my_capability"
    
    @property
    def description(self) -> str:
        return "Description of what this tool does"
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param": {"type": "string", "description": "..."}
            },
            "required": ["param"]
        }
    
    async def execute(self, input: dict[str, Any]) -> ToolResult:
        # Implementation
        return ToolResult(success=True, output="result")
\`\`\`

**⚠️ Common mistake:** The `mount()` function MUST call `await coordinator.mount("tools", tool, name=...)`. 
A mount() that returns None without calling coordinator.mount() will fail validation with:
"protocol_compliance: No tool was mounted and mount() did not return a Tool instance."
```

#### 7B. Create a skill: `creating-amplifier-modules`

Create a skill that agents can load when creating modules. This is the **most impactful fix** because skills are loaded on-demand and don't bloat every session.

**Content should include:**
1. The mount() contract for each module type (tool, hook, provider, orchestrator, context)
2. Complete working examples (copy-pasteable)
3. pyproject.toml template with entry points
4. The validation command (`amplifier module validate ./my-tool --type tool`)
5. Common mistakes (returning None, not calling coordinator.mount(), wrong mount point name)

#### 7C. Add mount() knowledge to modular-builder agent

Add a small section to `agents/modular-builder.md`:

```markdown
## Amplifier Module Pattern

When building Amplifier tool modules (modules/ directory in a bundle), follow this pattern:

**Critical**: The `mount()` function MUST call `await coordinator.mount("tools", tool, name=...)`.
See `amplifier-core/docs/contracts/TOOL_CONTRACT.md` for the full contract.
See `amplifier-foundation/modules/tool-delegate/` for the canonical example.
```

This is a "thin awareness pointer" — enough for the agent to know the pattern exists and where to look.

### Medium-term

#### 7D. Create a MODULE_AUTHORING.md in foundation docs

Similar to how AGENT_AUTHORING.md teaches agent creation, create MODULE_AUTHORING.md that teaches module creation. This would be the foundation-side complement to core's TOOL_CONTRACT.md, focused on practical "how to create a module for your bundle."

#### 7E. Fix example 03_custom_tool.py

Rename `mount_custom_tools` to `mount` and restructure the example to show the proper module entry point pattern alongside the programmatic pattern. Or add a new `03b_custom_module.py` that shows the full module-as-package pattern.

### Longer-term

#### 7F. Consider a `amplifier module new` CLI scaffolding command

The CLI already has `amplifier module validate`. A `amplifier module new tool-my-thing` command that generates the correct boilerplate would prevent this class of errors entirely.

---

## 8. Root Cause Summary

| Factor | Status | Impact |
|--------|--------|--------|
| TOOL_CONTRACT.md exists and is correct | ✅ In amplifier-core | Not loaded by agents working through foundation |
| BUNDLE_GUIDE.md covers module creation | ❌ Only mentions modules exist | Agents don't know mount() contract |
| Foundation context files teach mount() | ❌ Zero coverage | Agents have no mount() knowledge in context |
| modular-builder knows Amplifier modules | ❌ Only generic Python modules | Primary builder agent is blind to the contract |
| Skills exist for module creation | ❌ No such skill | No on-demand knowledge source |
| Example 03 shows the correct pattern | ⚠️ Non-standard function name | Teaching the right concept but wrong entry point |
| Canonical module examples exist | ✅ tool-delegate, ai-os-repo | But agents must discover them; no pointer exists |

**The systemic failure**: The mount() contract documentation lives in amplifier-core, but module creation happens in the amplifier-foundation context. There is no bridge between these two knowledge bases. Agents building modules through foundation have zero access to core's contract documentation and zero local documentation about the mount() pattern.

---

## Appendix: Evidence Files Examined

### amplifier-core (contract source of truth)
- `docs/contracts/TOOL_CONTRACT.md` — Complete, correct mount() example
- `docs/contracts/README.md` — Quick start with mount() pattern
- `python/amplifier_core/validation/tool.py` — Validation code producing the error
- `docs/contracts/HOOK_CONTRACT.md`, `PROVIDER_CONTRACT.md`, etc. — All show coordinator.mount()

### amplifier-foundation (what agents see)
- `docs/BUNDLE_GUIDE.md` — 1314 lines, 1 mention of mount() (troubleshooting)
- `docs/PATTERNS.md` — Application-level mounting only
- `docs/CONCEPTS.md` — One-line mention in passing
- `agents/modular-builder.md` — 630 lines, zero Amplifier module knowledge
- `agents/ecosystem-expert.md` — No module creation guidance
- `context/shared/common-system-base.md` — No mount() mention
- `context/shared/common-agent-base.md` — No mount() mention
- `context/IMPLEMENTATION_PHILOSOPHY.md` — "tool modules" mentioned 2x, no mount() guidance

### Working examples (correct patterns)
- `modules/tool-delegate/amplifier_module_tool_delegate/__init__.py` — Canonical
- `examples/03_custom_tool.py` — Correct concept, non-standard function name
- `examples/modules/router-orchestrator/` — Correct orchestrator mount
- `ai-os-repo/modules/tool_*/` — 13 correct tool modules (agent-created with examples to copy from)
