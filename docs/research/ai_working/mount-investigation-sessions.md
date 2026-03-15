# Mount() Stub Investigation: Systemic Pattern Analysis

> **Investigation date:** 2026-03-14
> **Scope:** All Amplifier sessions in last 2-3 weeks involving tool module creation, mount() stubs, and protocol_compliance errors
> **Primary case:** `amplifier-bundle-dot-graph` Phase 1 implementation
> **Verdict:** The broken mount() stub is caused by a **spec-driven knowledge gap** that propagates through the entire plan→implement→review pipeline unchallenged.

---

## Executive Summary

When agents create new Amplifier tool modules, they consistently produce broken `mount()` stubs that return `None` and never call `coordinator.mount()`. This investigation traced the root cause through 6 session layers of the dot-graph-bundle creation to identify the exact failure chain. The pattern is **not** caused by agent incompetence — it is caused by **precise but incorrect specifications** that the entire review pipeline validates against rather than questioning.

**The bug survives because every checkpoint asks "does this match the spec?" but no checkpoint asks "is the spec correct?"**

---

## Timeline of the Dot-Graph-Bundle Failure

| Time (UTC) | Agent | Session ID | Event |
|---|---|---|---|
| Mar 13 19:04 | human | `a31d8d0c` (root) | Started dot-graph-bundle creation session |
| ~Mar 13 20:00 | zen-architect | `0000000000000000-22d21e24ef5745fb` | Created BOOTSTRAP-SYNTHESIS.md — explicitly said "No tool module needed" for Phase 1 |
| ~Mar 14 01:00 | plan-writer or parent | — | Created implementation plan with Task 3: tool module skeleton with `-> None` stub |
| Mar 14 01:33 | implementer | `0000000000000000-23a56ada378744f4` | Created broken mount() stub — commit `f4414f6` |
| Mar 14 ~01:35 | spec-reviewer | `0000000000000000-2dca302fed134d86` | Approved — "all 14 spec requirements precisely implemented" |
| Mar 14 ~04:05 | code-quality-reviewer | `0000000000000000-6b230157850f4091` | Approved — "zero issues found" across all 18 tasks |
| Mar 14 ~07:09 | diagram-reviewer | `4bf61db075134e71-*` | **Bug surfaced** — spawning the agent loaded the behavior YAML, which referenced tool-dot-graph, triggering module validation failure |
| Mar 14 07:46 | human/agent | `a31d8d0c` (root) | Fix committed — `a1be900` — added DotGraphTool placeholder, proper coordinator.mount() |

---

## Session-by-Session Analysis

### Session 1: Design Spec (zen-architect)

**Session:** `0000000000000000-22d21e24ef5745fb_foundation-zen-architect`
**Project:** `-home-bkrabach-dev-dot-graph-bundle`
**Created:** 2026-03-13T12:33 UTC (approx)

**Instructions received:** Synthesize 6 research documents into a BOOTSTRAP-SYNTHESIS.md with use-case taxonomy, capability map, architecture, and phased implementation plan.

**What it said about mount():**
The zen-architect's BOOTSTRAP-SYNTHESIS.md was **explicit** that Phase 1 should NOT have a tool module:

> "**No tool module needed — agents carry all knowledge**"
> "No `tools:` section until Phase 2. Agents use existing `bash` tool to run `dot` commands."

The Phase 1 file tree showed no `modules/` directory. The tool module was listed under "Phase 2+" with a full structure including `tool.py` and `validate.py`.

**Key quote from Section 3.7:**
> "### 3.7 Tool Module (Phase 2+)"

**Assessment:** The design spec was CORRECT that Phase 1 didn't need a tool module. The problem arose when the implementation plan added one anyway as a "skeleton."

---

### Session 2: Implementation Plan

**Document:** `/home/bkrabach/dev/dot-graph-bundle/docs/plans/2026-03-13-dot-graph-bundle-phase1-implementation.md`
**Created by:** plan-writer agent (`0000000000000000-24feba9596144809_superpowers-plan-writer`) or parent session

**What it said about mount():**

The implementation plan's **Task 3** explicitly specified the broken mount():

```python
async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> None:
    """
    Mount tool-dot-graph module.

    Phase 1: Stub only. Phase 2 will register validation and rendering tools.
    Phase 3 will add graph intelligence (analyze) tools.

    Args:
        coordinator: Amplifier module coordinator
        config: Optional tool configuration
    """
    logger.info("tool-dot-graph mounted (stub — tools not yet registered)")
```

**Critical instruction:** "The stub does nothing yet; Phase 2 fills in the implementation."

**Acceptance criteria:** Only checked `mount is function: OK` — never tested runtime protocol compliance.

**Assessment:** The plan INTRODUCED the broken pattern by:
1. Adding a tool module to Phase 1 (contradicting the design spec)
2. Specifying `-> None` return type explicitly
3. Specifying the stub should "only log" — no mention of `coordinator.mount()`
4. Having acceptance criteria that tested importability, not protocol compliance

The plan referenced "the exact pattern from amplifier-bundle-recipes and amplifier-bundle-python-dev" for pyproject.toml but showed a stub that follows NO existing module's mount() pattern.

---

### Session 3: Implementation (superpowers:implementer)

**Session:** `0000000000000000-23a56ada378744f4_superpowers-implementer`
**Created:** 2026-03-14T01:33 UTC
**Commit:** `f4414f6 feat: add tool module skeleton with stub mount()`

**Exact instructions received (from SUBAGE NT IMPLEMENTATION TASK):**
```json
{
  "task_id": "task-3-tool-module-skeleton",
  "spec": "...stub async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> None 
           that only logs 'tool-dot-graph mounted (stub — tools not yet registered)'. 
           Phase 2 will fill in implementation.",
  "acceptance_criteria": "...Python import works: `cd modules/tool-dot-graph && 
           python -c \"from amplifier_module_tool_dot_graph import mount; 
           print(f'mount is {type(mount).__name__}: OK')\"` outputs 'mount is function: OK'..."
}
```

**What examples the implementer referenced:**
The session transcript shows the implementer explored:
1. `amplifier-foundation/modules/tool-delegate/` — has proper `coordinator.mount()` call
2. `amplifier-bundle-attractor/modules/tool-pipeline-run/` — has `await coordinator.mount("tools", tool, name=tool.name)`

**Why the implementer didn't follow the examples:**
The task instructions said: **"FOLLOW THE SPEC EXACTLY: Implement exactly what the spec says. Do not add features not in the spec."**

The implementer was trapped: it saw working examples with `coordinator.mount()`, but the spec explicitly said `-> None` and "only logs". Following the spec exactly meant creating a broken module.

**What tests were written:**
```python
async def test_mount_returns_none():
    """mount() stub returns None when called."""
    coordinator = MagicMock()
    result = await mount(coordinator)
    assert result is None  # <-- Testing for the BROKEN behavior
```

**Assessment:** The implementer did exactly what it was told. The instructions were precise, explicit, and wrong. The TDD approach actually locked in the broken behavior by writing tests that asserted `result is None`.

---

### Session 4: Spec Review (superpowers:spec-reviewer)

**Session:** `0000000000000000-2dca302fed134d86_superpowers-spec-reviewer`

**What was reviewed:** Task 3 implementation vs. Task 3 spec

**Verdict:** "APPROVED" — all 14 spec requirements precisely implemented.

**What was checked:**
- [x] Build backend: hatchling ✓
- [x] Entry-points: amplifier.modules ✓
- [x] Stub `async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> None` ✓
- [x] Log message: "tool-dot-graph mounted (stub — tools not yet registered)" ✓
- [x] Import check outputs "mount is function: OK" ✓

**What was NOT checked:**
- ❌ Whether mount() satisfies Amplifier module protocol_compliance
- ❌ Whether coordinator.mount() is called
- ❌ Whether the module would load in a real session
- ❌ Whether the spec itself was correct

**Assessment:** The spec reviewer compared implementation to spec and found perfect compliance. It had no knowledge of module protocol requirements and no mandate to question whether the spec was correct.

---

### Session 5: Code Quality Review (superpowers:code-quality-reviewer)

**Session:** `0000000000000000-6b230157850f4091_superpowers-code-quality-reviewer`

**Verdict:** "Approved (1 iteration)" for Task 3

**What it said about the mount stub:**
> "Tests: 7 tests in modules/tool-dot-graph/tests/test_mount_stub.py"
> "Notes: Used dependency-groups.dev (PEP 735) to match attractor bundle pattern; asyncio_mode = 'auto' per spec"

No mention of coordinator.mount(), protocol compliance, or runtime validation.

**Assessment:** Like the spec reviewer, the code quality reviewer checked code quality metrics (formatting, linting, types, test coverage) but had no visibility into whether the module would work at runtime.

---

### Session 6: Bug Discovery (during demo creation)

**Session:** `0000000000000000-4bf61db075134e71_self`
**Created:** 2026-03-14T07:31 UTC

**How the bug surfaced:**
When creating demo artifacts, the session tried to use the `dot-graph:diagram-reviewer` agent. Spawning this agent loaded the `behaviors/dot-graph.yaml` behavior, which references `tool-dot-graph`. The Amplifier module validator ran on mount and rejected the module:

```
protocol_compliance: No tool was mounted and mount() did not return a Tool instance
```

**The fix (commit `a1be900`):**
```python
class DotGraphTool:
    """Placeholder tool for DOT graph operations (Phase 1)."""
    
    @property
    def name(self) -> str:
        return "dot_graph"
    
    # ... name, description, input_schema properties ...
    
    async def execute(self, input_data: dict[str, Any]) -> ToolResult:
        return ToolResult(success=False, output="dot_graph tool not yet implemented...")

async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> dict[str, Any]:
    tool = DotGraphTool()
    await coordinator.mount("tools", tool, name=tool.name)  # <-- THE MISSING LINE
    return {"name": "tool-dot-graph", "version": "0.1.0", "provides": ["dot_graph"]}
```

---

## The Reference Modules (What a Correct mount() Looks Like)

The implementer explored two reference modules. Both have proper `coordinator.mount()` calls:

### tool-delegate (amplifier-foundation)
```python
async def mount(coordinator: ModuleCoordinator, config: dict[str, Any] | None = None):
    # ... creates DelegateTool instance ...
    await coordinator.mount("tools", tool, name=tool.name)
```

### tool-pipeline-run (amplifier-bundle-attractor)
```python
async def mount(coordinator: Any, config: dict[str, Any] | None = None) -> None:
    config = config or {}
    tool = PipelineRunTool(config, coordinator)
    await coordinator.mount("tools", tool, name=tool.name)
    logger.info("Mounted run_pipeline tool")
```

Both follow the same pattern:
1. Create a tool instance
2. Call `await coordinator.mount("tools", tool, name=tool.name)`
3. Log success

The broken stub omitted steps 1 and 2 entirely.

---

## Other Projects Searched

| Project | Sessions Found | Mount Stub Related? |
|---|---|---|
| `attractor-dev-machine` | 5 sessions mentioning mount/stub | No — about existing working modules, not broken stubs |
| `superpowers-3` | 3 sessions | No — session analyst investigating mount() behavior for different issue |
| `superpowers-adherence` | 1 session | No — about proper mount() config parsing, not broken stubs |
| All other projects | 0 matches for "No tool was mounted" or "protocol_compliance" errors | — |

**Conclusion:** The dot-graph-bundle is the **first and primary instance** of this specific failure in the session history. However, the pattern is **inherently reproducible** because the root cause is in the plan/spec generation logic, not in a one-off error.

---

## Root Cause Analysis: The Five-Link Failure Chain

### Link 1: Design-to-Plan Translation Error
**BOOTSTRAP-SYNTHESIS said:** "No tool module needed" for Phase 1
**Implementation plan said:** Create a tool module skeleton with stub mount()

The plan added a tool module that the design didn't call for, but specified it as a "stub" — implying it should be inert. This created the contradiction: a module that exists (so the behavior YAML references it) but does nothing (so it fails validation).

### Link 2: "Stub" is Ambiguous — and the Wrong Concept
The word "stub" in the Amplifier module context means fundamentally different things:
- **What the plan meant:** "Empty function that does nothing — placeholder for future code"
- **What the runtime requires:** "Minimal implementation that satisfies the protocol — register at least one tool"

In Amplifier, there is no such thing as a valid "do-nothing" tool module. A module that doesn't call `coordinator.mount()` is not a stub — it's broken. The correct concept is "placeholder tool" (registers a tool that explains it's not yet implemented), not "stub mount" (empty function).

### Link 3: Spec Precision in the Wrong Direction
The spec was maximally precise about the wrong thing:
- ✅ Precise about: function signature, return type (`-> None`), log message text, pyproject.toml structure
- ❌ Silent about: `coordinator.mount()` call, tool registration, protocol compliance

This created a "precisely wrong" specification — so detailed that the implementer had no room to deviate, even after seeing correct examples.

### Link 4: TDD Locked in the Bug
The test `test_mount_returns_none` with `assert result is None` codified the broken behavior. Once tests pass, the review pipeline treats the implementation as correct. TDD is only as good as the spec the tests are written from.

### Link 5: Review Checkpoint Blindness
Both spec-reviewer and code-quality-reviewer compared implementation to spec. Neither had:
- Knowledge of module protocol requirements
- Mandate to test runtime behavior
- Access to the module validator
- Reason to question whether the spec was correct

---

## The Systemic Pattern

This is not a one-off bug. It is a **repeatable failure mode** in any plan-driven agent workflow where:

1. **A plan specifies a "stub" or "skeleton" for a system with protocol requirements**
2. **The plan author doesn't know the protocol requirements**
3. **The spec is precise enough to suppress implementer judgment**
4. **Review checkpoints validate against the spec, not the runtime**

### Why This Will Happen Again

Every time an agent writes an implementation plan that includes creating a new Amplifier tool module, it will likely specify a mount() stub that:
- Returns `None`
- Only logs a message
- Doesn't call `coordinator.mount()`
- Has tests that assert the broken behavior

...because:
- No plan-writing agent has been taught the module protocol
- No spec-review agent checks specs against the module protocol
- No code-quality agent runs the module validator
- The word "stub" naturally implies "does nothing"

---

## Recommendations

### Immediate: Add to Plan-Writing Context
Any plan that includes creating an Amplifier tool module MUST include this constraint:

> **CRITICAL: Amplifier module protocol requires mount() to call `coordinator.mount()`.** A tool module that doesn't register at least one tool will be rejected by the validator with `protocol_compliance: No tool was mounted`. Even Phase 1 "placeholder" modules must register a minimal tool. There is no such thing as a valid "do-nothing" mount() stub.

### Medium-term: Add Protocol Compliance to Review Agents
The spec-reviewer and code-quality-reviewer should have awareness of Amplifier module protocol requirements as part of their review context. Specifically:
- mount() MUST call `coordinator.mount("tools", tool, name=tool.name)`
- mount() SHOULD return a metadata dict (not None)
- Tests should assert `coordinator.mount.called` (not `result is None`)

### Long-term: Add Protocol Validator to Hooks
A pre-commit or post-implementation hook that runs the module validator against any newly created tool module would catch this at the source, regardless of what the spec says.

### Pattern Fix: Redefine "Stub" in Module Context
In all module-related documentation and planning context, replace the word "stub" with "placeholder":
- ❌ "stub mount() that does nothing"
- ✅ "placeholder tool that registers with coordinator.mount() but returns a not-yet-implemented message"

---

## Session Index

| Session ID | Agent | Role in Chain | Location |
|---|---|---|---|
| `a31d8d0c-a01c-4bb8-8c3d-f72db174bf61` | root (human) | Orchestrator | `~/.amplifier/projects/-home-bkrabach-dev-dot-graph-bundle/sessions/a31d8d0c-*/` |
| `0000000000000000-22d21e24ef5745fb` | zen-architect | Created design spec | `~/.amplifier/projects/-home-bkrabach-dev-dot-graph-bundle/sessions/0000000000000000-22d21e24ef5745fb_*/` |
| `0000000000000000-24feba9596144809` | plan-writer | Compiled execution summary | `~/.amplifier/projects/-home-bkrabach-dev-dot-graph-bundle/sessions/0000000000000000-24feba9596144809_*/` |
| `0000000000000000-23a56ada378744f4` | implementer | Created broken mount() | `~/.amplifier/projects/-home-bkrabach-dev-dot-graph-bundle/sessions/0000000000000000-23a56ada378744f4_*/` |
| `0000000000000000-2dca302fed134d86` | spec-reviewer | Approved broken spec | `~/.amplifier/projects/-home-bkrabach-dev-dot-graph-bundle/sessions/0000000000000000-2dca302fed134d86_*/` |
| `0000000000000000-6b230157850f4091` | code-quality-reviewer | Approved broken code | `~/.amplifier/projects/-home-bkrabach-dev-dot-graph-bundle/sessions/0000000000000000-6b230157850f4091_*/` |
| `0000000000000000-4bf61db075134e71` | self (demo creation) | Bug discovered | `~/.amplifier/projects/-home-bkrabach-dev-dot-graph-bundle/sessions/0000000000000000-4bf61db075134e71_*/` |

**Git commits:**
- `f4414f6` — `feat: add tool module skeleton with stub mount()` (the broken commit)
- `a1be900` — `fix: register placeholder tool in mount() to pass module validation` (the fix)

**Key documents:**
- Design spec: `/home/bkrabach/dev/dot-graph-bundle/BOOTSTRAP-SYNTHESIS.md`
- Implementation plan: `/home/bkrabach/dev/dot-graph-bundle/docs/plans/2026-03-13-dot-graph-bundle-phase1-implementation.md`
- Broken mount: `git show f4414f6 -- modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py`
- Fixed mount: `git show a1be900 -- modules/tool-dot-graph/amplifier_module_tool_dot_graph/__init__.py`
