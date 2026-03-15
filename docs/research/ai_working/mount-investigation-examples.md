# mount() Implementation Investigation — Comprehensive Findings

**Date:** 2026-03-14
**Scope:** All mount() implementations, documentation, context files, skills, and behaviors across the entire Amplifier ecosystem in `~/.amplifier/cache/`
**Purpose:** Identify all sources that could teach an agent how to write mount() — to diagnose why agents produce broken no-op stubs.

---

## EXECUTIVE SUMMARY

**Root cause identified: The implementation plan explicitly instructed the agent to create a no-op stub.** The plan at `docs/plans/2026-03-13-dot-graph-bundle-phase1-implementation.md` lines 246-268 contains a verbatim code block showing a mount() that logs a message and returns None — never calling `coordinator.mount()`. This was presented as the correct Phase 1 pattern.

**The good news:** The dot-graph-bundle's actual current code (`a1be900`) has already been fixed — it now calls `coordinator.mount("tools", tool, name=tool.name)`. But the plan file still contains the bad pattern, which would mislead any future agent reading it.

**Ecosystem-wide finding:** 100% of production mount() implementations in the cache call `coordinator.mount()` or equivalent. There are ZERO production examples of a no-op mount(). The bad pattern exists ONLY in the plan document.

---

## PART 1: ALL mount() IMPLEMENTATIONS IN THE CACHE

### Summary Table

| # | File Path | Calls coordinator.mount()? | Returns? | Registers tool/hook/etc? | Stub? |
|---|-----------|---------------------------|----------|--------------------------|-------|
| 1 | amplifier-bundle-containers `.../tool-containers/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name="containers")` | Tool instance | YES — ContainersTool | NO |
| 2 | amplifier-bundle-containers `.../hooks-container-safety/__init__.py` | NO — uses `coordinator.hooks.register()` directly | Hooks instance | YES — 3 hook handlers | NO |
| 3 | amplifier-module-provider-anthropic `.../provider_anthropic/__init__.py` | **YES** — `await coordinator.mount("providers", provider, name="anthropic")` | Cleanup function | YES — AnthropicProvider | NO |
| 4 | amplifier-bundle-rust-dev `.../tool-rust-check/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` | Metadata dict | YES — RustCheckTool | NO |
| 5 | amplifier-bundle-rust-dev `.../hooks-rust-check/__init__.py` | NO — uses `coordinator.hooks.register()` directly | Metadata dict | YES — tool:post hook | NO |
| 6 | amplifier-bundle-recipes `.../tool-recipes/__init__.py` | YES — `coordinator.mount_points["tools"][tool.name] = tool` (direct) | None (implicit) | YES — RecipesTool | NO |
| 7 | amplifier-bundle-filesystem `.../tool-apply-patch/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` | None (implicit) | YES — ApplyPatchTool | NO |
| 8 | amplifier-bundle-routing-matrix `.../hooks-routing/__init__.py` | NO — uses `coordinator.hooks.register()` for 2 hooks | None (implicit) | YES — 2 hook handlers | NO |
| 9 | amplifier-bundle-execution-environments `.../tools-env-all/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` × 11 tools | Metadata dict | YES — 11 env tools | NO |
| 10 | amplifier-bundle-execution-environments `.../hooks-env-all/__init__.py` | NO — uses `coordinator.hooks.register()` | Metadata dict | YES — session:end hook | NO |
| 11 | amplifier-bundle-attractor `.../tool-pipeline-run/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` | None (implicit) | YES — PipelineRunTool | NO |
| 12 | amplifier-bundle-attractor `.../hooks-pipeline-progress/__init__.py` | NO — uses `hooks.register()` for 18 events | None (implicit) | YES — 18 event handlers | NO |
| 13 | amplifier-bundle-attractor `.../loop-agent/__init__.py` | **YES** — `await coordinator.mount("orchestrator", orchestrator)` | None (implicit) | YES — AgentOrchestrator | NO |
| 14 | amplifier-bundle-attractor `.../tool-apply-patch/__init__.py` (attractor copy) | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` | None (implicit) | YES — ApplyPatchTool | NO |
| 15 | amplifier-bundle-attractor `.../hooks-tool-truncation/__init__.py` | YES — uses `hooks.register()` via coordinator.get("hooks") | Cleanup function | YES — tool:post hook | NO |
| 16 | amplifier-bundle-attractor `.../tool-report-outcome/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` | None (implicit) | YES — ReportOutcomeTool | NO |
| 17 | amplifier-bundle-attractor `.../hooks-pipeline-observability/__init__.py` | NO — uses `hooks.register()` + `coordinator.register_contributor()` | None (implicit) | YES — 18 event handlers + contributors | NO |
| 18 | amplifier-bundle-attractor `.../tool-pipeline-status/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` | None (implicit) | YES — PipelineStatusTool | NO |
| 19 | amplifier-bundle-attractor `.../tool-dashboard-query/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` | None (implicit) | YES — DashboardQueryTool | NO |
| 20 | amplifier-bundle-attractor `.../loop-pipeline/__init__.py` | **YES** — `await coordinator.mount("orchestrator", orchestrator)` | None (implicit) | YES — PipelineOrchestrator | NO |
| 21 | amplifier-bundle-lsp `.../tool-lsp/__init__.py` | YES — `coordinator.mount_points["tools"][tool.name] = tool` (direct) | Cleanup function | YES — LspTool | NO |
| 22 | amplifier-bundle-terminal-tester `.../tool-terminal-inspector/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name="terminal_inspector")` | Tool instance | YES — TerminalInspectorTool | NO |
| 23 | amplifier-bundle-python-dev `.../hooks-python-check/__init__.py` | NO — uses `coordinator.hooks.register()` | Metadata dict | YES — tool:post hook | NO |
| 24 | amplifier-bundle-python-dev `.../tool-python-check/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` | Metadata dict | YES — PythonCheckTool | NO |
| 25 | amplifier-module-tool-todo `.../tool_todo/__init__.py` | YES — `coordinator.mount_points["tools"][tool.name] = tool` (direct) | None (explicit return) | YES — TodoTool | NO |
| 26 | amplifier-module-hooks-streaming-ui `.../hooks_streaming_ui/__init__.py` | NO — uses `coordinator.hooks.register()` × 5 | None (explicit return) | YES — 5 hook handlers | NO |
| 27 | amplifier-module-hooks-status-context `.../hooks_status_context/__init__.py` | NO — uses `hook.register(coordinator.hooks)` | None (explicit return) | YES — provider:request hook | NO |
| 28 | amplifier-module-hook-shell `.../hook_shell/__init__.py` | NO — uses `coordinator.hooks.register()` × 11 | Cleanup function | YES — 11 hook handlers | NO |
| 29 | amplifier-module-hooks-redaction `.../hooks_redaction/__init__.py` | NO — uses `coordinator.hooks.on()` × 20 | None (explicit return) | YES — 20 event handlers | NO |
| 30 | amplifier-module-tool-mcp `.../tool_mcp/__init__.py` | **YES** — `await coordinator.mount("tools", cap_wrapper, name=cap_name)` (loop) | Cleanup function | YES — MCP capabilities | NO |
| 31 | amplifier-module-tool-bash `.../tool_bash/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` | None (explicit return) | YES — BashTool | NO |
| 32 | amplifier-module-hooks-todo-reminder `.../hooks_todo_reminder/__init__.py` | NO — uses `hook.register(coordinator.hooks)` | None (explicit return) | YES — 2 hook handlers | NO |
| 33 | amplifier-module-hooks-approval `.../hooks_approval/__init__.py` | NO — uses `hooks.register()` + `coordinator.register_capability()` | Cleanup function | YES — tool:pre hook | NO |
| 34 | amplifier-module-context-simple `.../context_simple/__init__.py` | **YES** — `await coordinator.mount("context", context)` | None (explicit return) | YES — SimpleContextManager | NO |
| 35 | amplifier-module-provider-github-copilot `.../provider_github_copilot/__init__.py` | **YES** — `await coordinator.mount("providers", provider, name="github-copilot")` | Cleanup function | YES — CopilotSdkProvider | NO |
| 36 | amplifier-module-tool-skills `.../tool_skills/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` | Cleanup function | YES — SkillsTool | NO |
| 37 | amplifier-bundle-shadow `.../tool-shadow/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name="shadow")` | Cleanup function | YES — ShadowTool | NO |
| 38 | amplifier-foundation `.../router-orchestrator/__init__.py` (example) | **YES** — `await coordinator.mount("orchestrator", orchestrator)` | Cleanup function | YES — RoutingOrchestrator | NO |
| 39 | amplifier-foundation `.../tool-delegate/__init__.py` | **YES** — `await coordinator.mount("tools", tool, name=tool.name)` | None (explicit return) | YES — DelegateTool | NO |

### Classification Summary

| Category | Count | Description |
|----------|-------|-------------|
| **GOOD: calls coordinator.mount()** | **24** | Tool/orchestrator/context/provider modules that use `await coordinator.mount(mount_point, instance, name=...)` |
| **GOOD: uses coordinator.hooks.register()** | **15** | Hook modules that register event handlers (correct for hooks — they don't use coordinator.mount("tools")) |
| **BAD: no-op / returns None** | **0** | No production module does nothing in mount() |

### Key Patterns Observed

**Pattern A — Tool modules (most common):**
```python
async def mount(coordinator, config=None):
    tool = MyTool(config)
    await coordinator.mount("tools", tool, name=tool.name)
    # Return: None, tool instance, metadata dict, or cleanup function
```

**Pattern B — Hook modules:**
```python
async def mount(coordinator, config=None):
    hooks = MyHooks(config)
    coordinator.hooks.register("tool:post", hooks.handle_tool_post)
    # Return: None, cleanup function, or metadata dict
```

**Pattern C — Provider modules:**
```python
async def mount(coordinator, config=None):
    provider = MyProvider(config)
    await coordinator.mount("providers", provider, name="my-provider")
    return cleanup_function
```

**Pattern D — Orchestrator modules:**
```python
async def mount(coordinator, config=None):
    orchestrator = MyOrchestrator(config)
    await coordinator.mount("orchestrator", orchestrator)
```

**There are TWO legacy patterns that use direct mount_point assignment:**
1. `amplifier-bundle-recipes/tool-recipes`: `coordinator.mount_points["tools"][tool.name] = tool`
2. `amplifier-bundle-lsp/tool-lsp`: `coordinator.mount_points["tools"][tool.name] = tool`
3. `amplifier-module-tool-todo`: `coordinator.mount_points["tools"][tool.name] = tool`

These work but are the older pattern. The modern pattern is `await coordinator.mount("tools", tool, name=tool.name)`.

---

## PART 2: ALL DOCUMENTATION ABOUT WRITING MODULES

### Source 1: TOOL_CONTRACT.md
**Path:** `~/.amplifier/cache/amplifier-core-61734c2990ff26ac/docs/contracts/TOOL_CONTRACT.md`

**What it says about mount():**
```python
async def mount(coordinator: ModuleCoordinator, config: dict) -> Tool | Callable | None:
    tool = MyTool(config=config)
    await coordinator.mount("tools", tool, name="my-tool")
    return tool
```

- **Shows complete example?** YES — clear, correct example with `coordinator.mount()` call
- **Mentions validation requirement?** YES — "mount() function with entry point in pyproject.toml" in validation checklist
- **Could be misinterpreted as "mount() can be a no-op"?** NO — the example clearly shows registration
- **VERDICT: CORRECT — clearly shows coordinator.mount() is required**

### Source 2: BUNDLE_GUIDE.md
**Path:** `~/.amplifier/cache/amplifier-foundation-c909465861f9d6ce/docs/BUNDLE_GUIDE.md`

**What it says about mount():**
- Mentions `mount()` only in troubleshooting: "Ensure mount() function exists in module"
- Focuses on bundle structure, not module implementation
- Does NOT show any mount() code example
- **Could be misinterpreted?** Not really — it doesn't discuss mount() implementation at all
- **VERDICT: NEUTRAL — doesn't teach mount() patterns, just mentions it exists**

### Source 3: MOUNT_PLAN_SPECIFICATION.md
**Path:** `~/.amplifier/cache/amplifier-core-61734c2990ff26ac/docs/specs/MOUNT_PLAN_SPECIFICATION.md`

**What it says about mount():**
- Describes the Mount Plan schema (what modules to load)
- Does NOT show mount() implementation examples
- **VERDICT: NEUTRAL — specification layer, doesn't teach mount() patterns**

### Source 4: MODULE_SOURCE_PROTOCOL.md
**Path:** `~/.amplifier/cache/amplifier-core-61734c2990ff26ac/docs/MODULE_SOURCE_PROTOCOL.md`

**What it says about mount():**
- Describes how modules are found and loaded
- Does NOT show mount() implementation examples
- **VERDICT: NEUTRAL — loading mechanism, doesn't teach mount() patterns**

### Source 5: amplifier-core validation/tool.py
**Path:** `~/.amplifier/cache/amplifier-core-61734c2990ff26ac/python/amplifier_core/validation/tool.py`

**What it validates:**
1. Module is importable
2. `mount()` function exists
3. `mount()` signature is correct (coordinator, config)
4. `mount()` is async
5. **Protocol compliance — calls mount() and checks if tools were mounted**

**Critical finding (lines 232-260):** The validator calls `mount_fn(coordinator, actual_config)` with a TestCoordinator, then checks `coordinator.mount_points.get("tools", {})`. If the mount_points are empty AND mount() didn't return a Tool instance, it reports:
> "No tool was mounted and mount() did not return a Tool instance"

**This is the enforcement mechanism!** A no-op mount() WOULD fail validation. But the plan told the agent to create a stub before validation was run.

---

## PART 3: CONTEXT FILES MENTIONING mount()

**Search scope:** All `context/*.md` files across all bundles in `~/.amplifier/cache/`

**Result:** Only 2 mentions found:
- `amplifier-core/context/kernel-overview.md:39` — "Module mounting/unmounting" (general description)
- `amplifier-core/context/kernel-overview.md:46` — "mount points" (general description)

**VERDICT: NO context files teach mount() patterns.** This is a significant gap — agents building modules have no context-file-level guidance on how to write mount().

---

## PART 4: SKILLS MENTIONING MODULE CREATION

**Search scope:** All `skills/*/SKILL.md` files in `~/.amplifier/cache/skills/`

**Result:** ZERO skills mention mount(), module creation, or tool module patterns.

**VERDICT: NO skills teach mount() patterns.** Another significant gap.

---

## PART 5: BEHAVIOR YAML FILES

**Search scope:** All `behaviors/*.yaml` files

**What behaviors show:**
Behaviors reference tool modules by `module:` name and `source:` path. They do NOT show mount() implementation. Example from recipes:
```yaml
tools:
  - module: tool-recipes
    source: git+https://github.com/microsoft/amplifier-bundle-recipes@main#subdirectory=modules/tool-recipes
    config:
      session_dir: ~/.amplifier/projects/{project}/recipe-sessions
```

**VERDICT: Behaviors are configuration-only — they specify WHAT to mount, not HOW mount() should be implemented.** No misinterpretation risk.

---

## PART 6: THE PLAN THAT GUIDED THE BAD STUB

**Path:** `/home/bkrabach/dev/dot-graph-bundle/docs/plans/2026-03-13-dot-graph-bundle-phase1-implementation.md`

### What it says (lines 246-268):

> "This follows the mount() signature from `amplifier-bundle-recipes` — `async def mount(coordinator: ModuleCoordinator, config: dict[str, Any] | None = None)`. **The stub does nothing yet; Phase 2 fills in the implementation.**"

The plan then provides this exact code:
```python
async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> None:
    """
    Mount tool-dot-graph module.

    Phase 1: Stub only. Phase 2 will register validation and rendering tools.
    Phase 3 will add graph intelligence (analyze) tools.
    """
    logger.info("tool-dot-graph mounted (stub — tools not yet registered)")
```

### Analysis

1. **The plan explicitly says "The stub does nothing yet"** — this is the direct cause of the broken mount()
2. **It claims to follow the recipes pattern** — but the recipes mount() actually registers a tool via `coordinator.mount_points["tools"][tool.name] = tool`. The plan's code does NOT follow the recipes pattern.
3. **The plan never mentions `coordinator.mount()`** — the critical API call is completely absent
4. **The plan never mentions the validation requirement** — module validation would catch a no-op mount(), but the plan doesn't mention running validation
5. **Line 53 says** `__init__.py` with `async def mount(coordinator, config)` function — but frames it as just having the function signature, not the registration call

### The Fix (already applied in commit a1be900)

The current code in the repo has been fixed to properly register a placeholder tool:
```python
async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> dict[str, Any]:
    tool = DotGraphTool()
    await coordinator.mount("tools", tool, name=tool.name)
    return {"name": "tool-dot-graph", "version": "0.1.0", "provides": ["dot_graph"]}
```

**But the plan file still contains the bad pattern.** Any future agent reading the plan would be guided to create a broken stub.

---

## PART 7: ROOT CAUSE ANALYSIS

### The Causal Chain

```
1. Plan says "stub does nothing yet" ──→ agent writes no-op mount()
2. No context files teach mount() patterns ──→ agent has no counter-signal
3. No skills teach mount() patterns ──→ agent has no counter-signal
4. TOOL_CONTRACT.md shows correct pattern ──→ but agent wasn't directed to read it
5. Validation catches the error ──→ but plan didn't instruct to run validation
6. All 39 production modules show correct patterns ──→ but agent didn't look at them
```

### Why Agents Produce Broken Stubs

**Primary cause:** Plans and instructions explicitly tell agents to create stubs that "do nothing yet."

**Contributing factors:**
1. **No skill or context file teaches "how to write mount()"** — The TOOL_CONTRACT.md exists in docs/contracts/ but is never @mentioned in any context file or agent instruction
2. **The concept of "stub" is ambiguous** — A valid stub mount() registers a placeholder tool that returns "not yet implemented." An invalid stub mount() does nothing.
3. **Phase-based thinking misleads** — "Phase 1 = stub, Phase 2 = real" suggests mount() should be empty, when it should register a placeholder tool instead

### The Correct Stub Pattern

A stub that satisfies the module protocol while indicating "not yet implemented":

```python
class PlaceholderTool:
    @property
    def name(self) -> str:
        return "my_tool"

    @property
    def description(self) -> str:
        return "Placeholder — not yet implemented."

    @property
    def input_schema(self) -> dict:
        return {"type": "object", "properties": {}}

    async def execute(self, input_data: dict) -> ToolResult:
        return ToolResult(success=False, output="Not yet implemented.")


async def mount(coordinator, config=None):
    tool = PlaceholderTool()
    await coordinator.mount("tools", tool, name=tool.name)
```

This is exactly what the fixed dot-graph-bundle now does.

---

## PART 8: RECOMMENDATIONS

### Immediate Actions

1. **Update the plan file** — Replace the bad stub code in `docs/plans/2026-03-13-dot-graph-bundle-phase1-implementation.md` with the correct placeholder pattern that calls `coordinator.mount()`.

2. **Create a skill** — Create a "writing-amplifier-modules" skill that teaches:
   - mount() MUST call `coordinator.mount()` or register hooks
   - How to write valid placeholder/stub tools
   - The difference between tool, hook, provider, orchestrator, and context modules
   - Reference to TOOL_CONTRACT.md

3. **Add mount() guidance to context files** — Add a brief section about mount() to a context file that gets included in relevant agent instructions.

### Systemic Fixes

4. **Never plan "no-op stubs"** — Plans should always specify placeholder implementations that satisfy the protocol, not empty stubs.

5. **Include validation in plans** — Any plan that creates a module should include a validation step: `amplifier module validate ./my-tool --type tool`.

6. **Add a "module authoring" doc to foundation** — Foundation's BUNDLE_GUIDE.md covers bundle configuration but not module implementation. A MODULE_AUTHORING_GUIDE.md would fill this gap.

---

## APPENDIX: COVERAGE & GAPS

### What was explored:
- 39 mount() implementations across all cached bundles/modules (100% coverage)
- 5 documentation files about module contracts and specifications
- 80+ context files across all bundles
- All skills directories
- 50+ behavior YAML files
- The specific plan that guided the bad stub
- The core validation code

### What remains unknown:
- Whether other users' plans have the same "no-op stub" pattern
- Whether the CLI's init/scaffold command generates correct mount() (couldn't find an init command)
- Whether there are additional mount() examples in test files (searched but didn't read all test files)
- The amplifier-d1dda27a16518560 cache directory was not found (may not be cached on this machine)
