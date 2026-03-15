# Comprehensive Bundle Guidance: amplifier-bundle-dot-graph

**Purpose**: Complete blueprint for creating a first-class Amplifier bundle that brings DOT/Graphviz capabilities to the ecosystem — enabling agents to create, validate, render, and reason about DOT diagrams.

**Authoritative sources**: This document is derived from the canonical foundation documentation:
- `foundation:docs/BUNDLE_GUIDE.md` — Complete bundle authoring guide
- `foundation:docs/AGENT_AUTHORING.md` — Agent-specific authoring
- `foundation:docs/CONCEPTS.md` — Core concepts
- `foundation:docs/PATTERNS.md` — Common patterns
- `foundation:docs/URI_FORMATS.md` — Source URI formats
- `foundation:context/IMPLEMENTATION_PHILOSOPHY.md` — Ruthless simplicity
- `foundation:context/MODULAR_DESIGN_PHILOSOPHY.md` — Modular design
- `foundation:context/KERNEL_PHILOSOPHY.md` — Mechanism vs policy

---

## Table of Contents

1. [Bundle Structure](#1-bundle-structure)
2. [The Thin Bundle Pattern](#2-the-thin-bundle-pattern)
3. [Behavior Composition](#3-behavior-composition)
4. [Agent Patterns](#4-agent-patterns)
5. [Context Files](#5-context-files)
6. [Tool Integration](#6-tool-integration)
7. [Skills](#7-skills)
8. [Namespace and Registration](#8-namespace-and-registration)
9. [Canonical Examples to Study](#9-canonical-examples-to-study)
10. [Context Sink Pattern](#10-context-sink-pattern)
11. [Complete File Specifications](#11-complete-file-specifications)
12. [Anti-Patterns to Avoid](#12-anti-patterns-to-avoid)
13. [Implementation Roadmap](#13-implementation-roadmap)

---

## 1. Bundle Structure

### Recommended Directory Layout

```
amplifier-bundle-dot-graph/
├── bundle.md                          # Root bundle (THIN - ~15 lines YAML)
├── behaviors/
│   └── dot-graph.yaml                 # Behavior bundle (the reusable value)
├── agents/
│   ├── dot-author.md                  # DOT authoring consultant (context sink)
│   └── diagram-reviewer.md            # Diagram review specialist (context sink)
├── context/
│   ├── dot-graph-awareness.md         # Thin awareness pointer (~30-40 lines)
│   └── dot-graph-instructions.md      # Consolidated instructions for root sessions
├── modules/
│   └── tool-dot-graph/                # Local tool module
│       ├── pyproject.toml             # Module package config (NO amplifier-core dep)
│       └── tool_dot_graph/
│           ├── __init__.py
│           └── tool.py                # Tool implementation with mount() function
├── docs/
│   ├── DOT_SYNTAX_REFERENCE.md        # Complete DOT language reference
│   ├── DOT_PATTERNS.md                # Common graph patterns and idioms
│   ├── DOT_BEST_PRACTICES.md          # Layout tips, styling, accessibility
│   └── RENDERING_GUIDE.md             # Rendering options and output formats
├── README.md
├── LICENSE
├── SECURITY.md
└── CODE_OF_CONDUCT.md
```

### What's Required vs Optional

| File/Directory | Required? | Purpose |
|----------------|-----------|---------|
| `bundle.md` | **Required** | Root bundle entry point, establishes namespace |
| `behaviors/*.yaml` | **Required** | The reusable value — what others compose onto their bundles |
| `agents/*.md` | Recommended | Specialized agent definitions (context sinks) |
| `context/*.md` | **Required** | Instructions and awareness pointers |
| `modules/tool-*/` | Optional | Only if you provide custom tools |
| `docs/` | Recommended | Heavy documentation referenced by agents |
| `README.md` | **Required** | Human-readable documentation |
| `LICENSE` | **Required** | License file |
| `pyproject.toml` (root) | **NO** | Bundles are configuration, NOT Python packages |

### Key Structural Insight

> Bundles are **configuration**, not Python packages. A bundle repo does NOT need a root `pyproject.toml`. Only modules inside `modules/` need their own `pyproject.toml`.

---

## 2. The Thin Bundle Pattern

### The Core Principle

**Most bundles should be thin** — inheriting from foundation and adding only their unique capabilities. Your `bundle.md` should declare NOTHING that foundation already provides.

### What NOT to Declare

When you include foundation, **do not redeclare**:
- `session:` (orchestrator, context manager) — foundation provides these
- Base `tools:` (filesystem, bash, web, search) — foundation provides these
- `hooks:` (streaming UI, logging) — foundation provides these

### Your bundle.md (Target: ~15 lines of YAML)

```markdown
---
bundle:
  name: dot-graph
  version: 1.0.0
  description: DOT/Graphviz diagram capabilities for creating, validating, rendering, and reasoning about graphs

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: dot-graph:behaviors/dot-graph
---

# DOT Graph Capabilities

@dot-graph:context/dot-graph-instructions.md

---

@foundation:context/shared/common-system-base.md
```

**That's it.** All tools, session config, and hooks come from foundation. You add only:
1. Your behavior (via `includes:`)
2. Your consolidated instructions (via `@mention`)
3. Foundation's shared base instructions (via `@mention`)

### Why This Matters

- **No maintenance burden** — foundation updates flow through automatically
- **No version conflicts** — single source of truth for base capabilities
- **No duplication** — you declare only what you uniquely provide

### The Canonical Exemplar

Study `amplifier-bundle-recipes` — its `bundle.md` is only 14 lines of YAML:

```yaml
bundle:
  name: recipes
  version: 1.0.0
  description: Multi-step AI agent orchestration for repeatable workflows

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: recipes:behaviors/recipes
```

---

## 3. Behavior Composition

### Why You Need a Behavior

Behaviors enable **reusability**. Without a behavior, anyone who wants your DOT capabilities must include your entire bundle. With a behavior, they can compose just your capability onto *their* bundle.

The pattern: **Put your main value in `/behaviors/`**. The root bundle includes its own behavior (DRY).

### Your Behavior File: `behaviors/dot-graph.yaml`

```yaml
bundle:
  name: dot-graph-behavior
  version: 1.0.0
  description: DOT/Graphviz diagram capabilities with authoring and review agents

# Tool specific to this capability (only if you build one)
tools:
  - module: tool-dot-graph
    source: git+https://github.com/microsoft/amplifier-bundle-dot-graph@main#subdirectory=modules/tool-dot-graph
    config:
      default_engine: dot
      output_formats: [svg, png, pdf]
      validation: strict

# Agents this behavior provides
agents:
  include:
    - dot-graph:dot-author        # NOTE: no "agents/" prefix - system searches /agents automatically
    - dot-graph:diagram-reviewer

# Context this behavior injects into root sessions
context:
  include:
    - dot-graph:context/dot-graph-awareness.md    # THIN pointer only (~30 lines)
```

### Critical Details

1. **Agent paths**: Use `dot-graph:dot-author`, NOT `dot-graph:agents/dot-author`. The system automatically searches the `/agents` directory.

2. **Context in behaviors must be THIN**: The `context.include` in a behavior propagates (accumulates) to every bundle that includes it. Put only thin awareness pointers here — never heavy documentation.

3. **Tool source URIs**: Use the full git URL with `#subdirectory=` pointing to your module within the repo. Local paths (`./modules/tool-dot-graph`) work for development but won't resolve when others include your behavior remotely.

### How Others Would Use Your Behavior

```yaml
# Someone else's bundle.md
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/microsoft/amplifier-bundle-dot-graph@main#subdirectory=behaviors/dot-graph.yaml
  # Their other behaviors...
```

### `context.include` vs `@mentions` — Different Semantics

This is a critical distinction:

| Pattern | Behavior | Use When |
|---------|----------|----------|
| `context.include` (YAML) | **ACCUMULATES** — propagates to including bundles | Behaviors injecting context into parent sessions |
| `@mentions` (Markdown) | **STAYS** with this instruction only | Direct references in your own bundle.md or agent .md |

- **Behaviors** use `context.include` because they WANT their context to propagate upward.
- **Root bundles** use `@mentions` because they are the final instruction.
- **YAML sections** use bare `namespace:path` (NO `@` prefix).
- **Markdown body** uses `@namespace:path` (WITH `@` prefix).

---

## 4. Agent Patterns

### Agent Fundamentals

**Agents ARE bundles.** They use the same file format (markdown + YAML frontmatter) and are loaded via the same `load_bundle()` function. The only difference is the frontmatter key:

| Aspect | Bundle | Agent |
|--------|--------|-------|
| Frontmatter key | `bundle:` | `meta:` |
| Required fields | `name`, `version` | `name`, `description` |

### Agent: `agents/dot-author.md`

```markdown
---
meta:
  name: dot-author
  description: |
    Expert DOT/Graphviz authoring consultant. MUST be used when creating, editing,
    or troubleshooting DOT graph definitions.

    Use PROACTIVELY when user needs to:
    - Create DOT graph definitions from descriptions or requirements
    - Convert concepts, architectures, or workflows into visual diagrams
    - Debug DOT syntax errors or rendering issues
    - Optimize graph layouts for readability

    **Authoritative on:** DOT language, Graphviz, directed graphs, undirected graphs,
    subgraphs, clusters, node attributes, edge attributes, graph attributes, layout
    engines (dot, neato, fdp, sfdp, circo, twopi), rank constraints, HTML labels,
    record shapes, color schemes, splines, graph styling

    <example>
    user: 'Create a diagram showing our microservices architecture'
    assistant: 'I'll use dot-graph:dot-author to create a well-structured DOT diagram of your microservices architecture.'
    <commentary>Architecture visualization is a core DOT authoring task.</commentary>
    </example>

    <example>
    user: 'My DOT file renders with overlapping nodes, can you fix it?'
    assistant: 'Let me delegate to dot-graph:dot-author to diagnose and fix the layout issues.'
    <commentary>DOT layout debugging requires expertise with rank constraints, engines, and attributes.</commentary>
    </example>

    <example>
    user: 'Convert this state machine description into a Graphviz diagram'
    assistant: 'I'll use dot-graph:dot-author to create a proper state machine diagram in DOT format.'
    <commentary>State machines are a classic DOT use case - the expert knows the right patterns.</commentary>
    </example>

  model_role: [coding, general]
---

# DOT Authoring Expert

You are a specialized expert in DOT/Graphviz diagram authoring. You create, debug,
and optimize DOT graph definitions with deep knowledge of the language and its
rendering engines.

**Execution model:** You run as a one-shot sub-session. Work with what you're given
and return complete, validated DOT output.

## Knowledge Base

@dot-graph:docs/DOT_SYNTAX_REFERENCE.md
@dot-graph:docs/DOT_PATTERNS.md
@dot-graph:docs/DOT_BEST_PRACTICES.md

## Operating Principles

1. **Produce valid DOT** — every output must be syntactically correct
2. **Optimize for readability** — choose layout engines and attributes that make the diagram clear
3. **Explain your choices** — when using advanced features, explain why
4. **Use idiomatic patterns** — prefer standard DOT idioms over clever workarounds

## Workflow

1. Understand the graph requirements (nodes, edges, relationships, hierarchy)
2. Choose the appropriate graph type (digraph vs graph) and layout engine
3. Structure the DOT definition with clear subgraphs and clusters where appropriate
4. Apply styling for readability (colors, shapes, fonts)
5. Validate syntax and explain the output

## Output Contract

Your response MUST include:
- Complete, syntactically valid DOT source code in a code block
- Brief explanation of the graph structure and any design choices
- Suggested rendering command (e.g., `dot -Tsvg input.dot -o output.svg`)

---

@foundation:context/shared/common-agent-base.md
```

### Agent: `agents/diagram-reviewer.md`

```markdown
---
meta:
  name: diagram-reviewer
  description: |
    DOT diagram quality reviewer and optimization specialist. Use when evaluating
    existing DOT diagrams for correctness, clarity, and best practices.

    Use PROACTIVELY when:
    - Reviewing DOT files for quality or correctness
    - Optimizing existing diagrams for better layout or readability
    - Auditing graph definitions against best practices
    - Comparing diagram approaches or suggesting improvements

    **Authoritative on:** DOT validation, graph layout optimization, diagram
    accessibility, visual clarity, Graphviz best practices, anti-patterns in graph
    definitions

    <example>
    user: 'Review this DOT file and suggest improvements'
    assistant: 'I'll delegate to dot-graph:diagram-reviewer for a thorough quality review.'
    <commentary>Diagram review is this agent's core function.</commentary>
    </example>

  model_role: [critique, general]
---

# Diagram Review Specialist

You are a specialized reviewer for DOT/Graphviz diagrams. You evaluate diagrams
for correctness, clarity, accessibility, and adherence to best practices.

**Execution model:** You run as a one-shot sub-session. Analyze what you're given
and return actionable feedback.

## Knowledge Base

@dot-graph:docs/DOT_SYNTAX_REFERENCE.md
@dot-graph:docs/DOT_BEST_PRACTICES.md

## Review Checklist

1. **Syntax validity** — is the DOT syntactically correct?
2. **Structural clarity** — are subgraphs/clusters used appropriately?
3. **Visual readability** — will the rendered output be legible?
4. **Layout engine choice** — is the right engine selected for this graph type?
5. **Attribute hygiene** — are attributes used correctly and consistently?
6. **Naming conventions** — are node/edge IDs descriptive?
7. **Accessibility** — are colors distinguishable? Is there sufficient contrast?

## Output Contract

Your response MUST include:
- **Verdict**: PASS / NEEDS WORK / FAIL with rationale
- **Issues found**: Numbered list with severity (critical/warning/suggestion)
- **Improved DOT**: Corrected version if issues were found
- **Explanation**: What was changed and why

---

@foundation:context/shared/common-agent-base.md
```

### Description Requirements Checklist

Every agent description MUST include (audit against this):

- [ ] **> 100 words** (not a one-liner)
- [ ] **WHY** — clear value proposition
- [ ] **WHEN** — explicit activation triggers with keywords (MUST, REQUIRED, PROACTIVELY)
- [ ] **WHAT** — domain terms ("Authoritative on: ...")
- [ ] **HOW** — at least one `<example>` block with `<commentary>`

Poor descriptions cause delegation failures. This is the ONLY discovery mechanism.

### `model_role` Selection

Agents can declare what *kind* of model they need rather than pinning a specific provider:

| Agent | Recommended `model_role` | Rationale |
|-------|--------------------------|-----------|
| `dot-author` | `[coding, general]` | DOT is a language — coding models excel at syntax |
| `diagram-reviewer` | `[critique, general]` | Review is analytical evaluation |

Available roles: `coding`, `critique`, `reasoning`, `creative`, `writing`, `research`, `vision`, `fast`, `general`, and others. See the routing-matrix bundle for the full list.

### Include vs Inline Agent Definitions

**Use Include (recommended for most cases):**
```yaml
agents:
  include:
    - dot-graph:dot-author      # Loads agents/dot-author.md
```

**Use Inline (when agent needs specific tools):**
```yaml
agents:
  dot-author:
    description: "..."
    instructions: dot-graph:agents/dot-author.md
    tools:
      - module: tool-dot-graph   # This agent gets specific tools
        source: ./modules/tool-dot-graph
```

For this bundle, **Include is the right choice** — agents don't need tool configurations that differ from the parent bundle.

---

## 5. Context Files

### Architecture Overview

Context files serve two distinct purposes:

1. **Thin awareness pointers** — injected into root sessions via behavior `context.include`
2. **Consolidated instructions** — referenced by `@mention` in `bundle.md`

Heavy documentation lives in `docs/` and is loaded ONLY by agents (context sinks).

### File: `context/dot-graph-awareness.md` (~30-40 lines)

This is the thin pointer that root sessions receive. Its job: tell the agent that DOT capabilities exist and to delegate to the expert agents.

```markdown
# DOT/Graphviz Diagram Capabilities

You have access to DOT/Graphviz diagram capabilities for creating, validating,
and reviewing graph definitions.

## When to Delegate

**BEFORE any DOT/Graphviz work**, delegate to the appropriate expert agent:

| Need | Delegate To |
|------|-------------|
| Create or edit DOT diagrams | `dot-graph:dot-author` |
| Review or optimize DOT diagrams | `dot-graph:diagram-reviewer` |

## Why Delegation is Required

DOT graph authoring requires specialized knowledge of:
- DOT syntax, attributes, and layout engines
- Common graph patterns (state machines, architectures, flowcharts)
- Layout optimization and rendering options
- Graphviz best practices and anti-patterns

The expert agents have authoritative access to:
- `dot-graph:docs/DOT_SYNTAX_REFERENCE.md`
- `dot-graph:docs/DOT_PATTERNS.md`
- `dot-graph:docs/DOT_BEST_PRACTICES.md`
```

### File: `context/dot-graph-instructions.md`

This is the consolidated instructions file referenced by both the behavior and `bundle.md`. It provides the root session with operational instructions about how to use the DOT capabilities.

```markdown
# DOT/Graphviz Instructions

You have access to DOT/Graphviz capabilities for creating, validating, rendering,
and reasoning about graph diagrams.

## Available Agents

- **dot-author** — Expert DOT authoring consultant. Creates, debugs, and optimizes
  DOT graph definitions. Delegate any diagram creation or syntax work here.

- **diagram-reviewer** — Diagram quality reviewer. Evaluates existing DOT files for
  correctness, clarity, and best practices. Delegate review requests here.

## Available Tools

- **dot-graph** — Validates DOT syntax, renders diagrams to SVG/PNG/PDF, and provides
  structural analysis of graph definitions.

## Usage Guidelines

1. For diagram **creation**: delegate to `dot-graph:dot-author`
2. For diagram **review**: delegate to `dot-graph:diagram-reviewer`
3. For quick **validation**: use the `dot-graph` tool directly
4. For quick **rendering**: use the `dot-graph` tool directly

## DOT Quick Reference

DOT is the graph description language used by Graphviz. Basic syntax:

- `digraph G { A -> B; }` — directed graph
- `graph G { A -- B; }` — undirected graph
- Attributes: `[shape=box, color=blue, label="My Node"]`
- Subgraphs: `subgraph cluster_0 { ... }` (clusters render as boxes)
- Layout engines: `dot` (hierarchical), `neato` (spring), `fdp` (force-directed),
  `circo` (circular), `twopi` (radial)
```

### Documentation Files in `docs/` (Heavy Context)

These are the heavyweight reference documents. They are NEVER loaded into root sessions. They are loaded ONLY when expert agents are spawned (via `@mentions` in agent files).

| File | Purpose | Approximate Size |
|------|---------|------------------|
| `docs/DOT_SYNTAX_REFERENCE.md` | Complete DOT language reference | 500-1000 lines |
| `docs/DOT_PATTERNS.md` | Common patterns (state machines, architectures, ERDs, flowcharts) | 300-500 lines |
| `docs/DOT_BEST_PRACTICES.md` | Layout tips, styling, accessibility, anti-patterns | 200-400 lines |
| `docs/RENDERING_GUIDE.md` | Rendering options, output formats, engines | 100-200 lines |

### Context Flow Summary

```
Root Session (lean)
├── context/dot-graph-awareness.md    ← via behavior context.include (~30 lines)
├── context/dot-graph-instructions.md ← via @mention in bundle.md (~50 lines)
└── (knows to delegate, does NOT attempt DOT work)

dot-author Agent (heavy, spawned on demand)
├── docs/DOT_SYNTAX_REFERENCE.md      ← via @mention in agent file
├── docs/DOT_PATTERNS.md              ← via @mention in agent file
├── docs/DOT_BEST_PRACTICES.md        ← via @mention in agent file
└── (does the actual work with full knowledge)

diagram-reviewer Agent (heavy, spawned on demand)
├── docs/DOT_SYNTAX_REFERENCE.md      ← via @mention in agent file
├── docs/DOT_BEST_PRACTICES.md        ← via @mention in agent file
└── (does review with full knowledge)
```

---

## 6. Tool Integration

### Should You Build a Tool?

| Capability | Recommendation | Why |
|------------|---------------|-----|
| DOT syntax validation | **Tool** | Deterministic, fast, better done by code than LLM |
| DOT rendering to SVG/PNG | **Tool** | Requires Graphviz binary, not an LLM task |
| Graph structural analysis (node count, cycle detection) | **Tool** | Deterministic computation |
| DOT authoring (creating graphs from descriptions) | **Agent** | Requires reasoning, creativity |
| Diagram review (evaluating quality) | **Agent** | Requires judgment, expertise |
| DOT syntax teaching | **Context** (docs + skills) | Reference material, not runtime logic |

### The Module Pattern

Tools live in `modules/` as self-contained Python packages. Each module has:

1. A `pyproject.toml` with entry point
2. A `mount()` function that registers the tool with the coordinator
3. Tool classes implementing the protocol: `name`, `description`, `input_schema`, `execute()`

### Module Structure: `modules/tool-dot-graph/`

```
modules/tool-dot-graph/
├── pyproject.toml
└── tool_dot_graph/
    ├── __init__.py
    └── tool.py
```

### `modules/tool-dot-graph/pyproject.toml`

```toml
[project]
name = "tool-dot-graph"
version = "0.1.0"
description = "DOT/Graphviz validation and rendering tool for Amplifier"
requires-python = ">=3.11"
dependencies = []    # Do NOT declare amplifier-core - it's a peer dependency

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["tool_dot_graph"]

[project.entry-points."amplifier.modules"]
tool-dot-graph = "tool_dot_graph.tool"
```

**Critical**: Do NOT declare `amplifier-core` as a dependency. Tool modules run inside the host application's process, which already has `amplifier-core` loaded. Declaring it as a dependency causes installation failures because it's not on PyPI.

### `modules/tool-dot-graph/tool_dot_graph/tool.py`

```python
"""DOT/Graphviz validation and rendering tool."""

import subprocess
import tempfile
from pathlib import Path
from typing import Any

from amplifier_core import ToolResult


class DotValidateTool:
    """Validates DOT syntax and reports errors."""

    @property
    def name(self) -> str:
        return "dot_validate"

    @property
    def description(self) -> str:
        return """Validate DOT/Graphviz syntax.

Input: {"dot_source": "digraph G { A -> B; }"}
Returns: Validation result with any syntax errors found."""

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "dot_source": {
                    "type": "string",
                    "description": "DOT source code to validate",
                },
            },
            "required": ["dot_source"],
        }

    async def execute(self, input: dict[str, Any]) -> ToolResult:
        dot_source = input.get("dot_source", "")
        if not dot_source:
            return ToolResult(success=False, error={"message": "No DOT source provided"})

        try:
            # Use Graphviz dot command for validation
            result = subprocess.run(
                ["dot", "-Tcanon"],
                input=dot_source,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                return ToolResult(success=True, output="DOT syntax is valid.")
            else:
                return ToolResult(
                    success=True,
                    output=f"DOT syntax errors found:\n{result.stderr}",
                )
        except FileNotFoundError:
            return ToolResult(
                success=False,
                error={"message": "Graphviz 'dot' command not found. Install with: apt-get install graphviz"},
            )


class DotRenderTool:
    """Renders DOT source to image files."""

    @property
    def name(self) -> str:
        return "dot_render"

    @property
    def description(self) -> str:
        return """Render DOT/Graphviz source to an image file.

Input: {"dot_source": "digraph G { ... }", "output_path": "diagram.svg", "format": "svg", "engine": "dot"}
Returns: Path to the rendered output file."""

    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "dot_source": {"type": "string", "description": "DOT source code to render"},
                "output_path": {"type": "string", "description": "Output file path"},
                "format": {
                    "type": "string",
                    "enum": ["svg", "png", "pdf"],
                    "description": "Output format (default: svg)",
                },
                "engine": {
                    "type": "string",
                    "enum": ["dot", "neato", "fdp", "sfdp", "circo", "twopi"],
                    "description": "Layout engine (default: dot)",
                },
            },
            "required": ["dot_source", "output_path"],
        }

    async def execute(self, input: dict[str, Any]) -> ToolResult:
        dot_source = input.get("dot_source", "")
        output_path = input.get("output_path", "")
        fmt = input.get("format", "svg")
        engine = input.get("engine", "dot")

        if not dot_source or not output_path:
            return ToolResult(success=False, error={"message": "Both dot_source and output_path required"})

        try:
            result = subprocess.run(
                [engine, f"-T{fmt}", "-o", output_path],
                input=dot_source,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return ToolResult(success=True, output=f"Rendered to {output_path} ({fmt} format, {engine} engine)")
            else:
                return ToolResult(success=False, error={"message": f"Render failed: {result.stderr}"})
        except FileNotFoundError:
            return ToolResult(
                success=False,
                error={"message": f"Graphviz '{engine}' command not found. Install with: apt-get install graphviz"},
            )


# =============================================================================
# Mount function - REQUIRED entry point for Amplifier modules
# =============================================================================

async def mount(coordinator, config: dict):
    """Mount DOT graph tools onto the coordinator."""
    validate_tool = DotValidateTool()
    render_tool = DotRenderTool()

    await coordinator.mount("tools", validate_tool, name=validate_tool.name)
    await coordinator.mount("tools", render_tool, name=render_tool.name)

    async def cleanup():
        pass  # No resources to release

    return cleanup
```

### Tool vs Hook vs Context — Decision Framework

| Mechanism | Use For | DOT Example |
|-----------|---------|-------------|
| **Tool** | Runtime actions the agent invokes on demand | Validate DOT, render to SVG |
| **Hook** | Observability and control (events) | NOT needed for DOT capabilities |
| **Context** | Static knowledge injected at session start | DOT syntax reference, patterns |
| **Agent** | Complex reasoning tasks requiring expertise | DOT authoring, diagram review |

For a DOT graph bundle, **tools + agents + context** is the right combination. Hooks would only be needed if you wanted to do something like automatically validate DOT files on every save — that's a policy decision for the application, not the bundle.

---

## 7. Skills

### How Skills Complement Bundles

Skills and bundles serve different purposes and are complementary:

| Aspect | Bundle | Skill |
|--------|--------|-------|
| **What it is** | Composable configuration unit for sessions | Reference guide for techniques and patterns |
| **Loaded how** | Via `includes:` at session start | Via `load_skill` tool, on demand |
| **Provides** | Tools, agents, context, hooks | Knowledge, patterns, best practices |
| **Token cost** | Determined by composition | Loaded only when needed |
| **Persistence** | Active throughout session | Read once, applied as needed |

### Should You Create DOT Skills?

**Yes, as a complement.** Skills are the right place for:

- **DOT syntax quick reference** — patterns agents can look up on demand
- **Common graph recipes** — templates for state machines, ERDs, flowcharts
- **Graphviz tips** — engine selection guide, attribute cheat sheet
- **DOT anti-patterns** — common mistakes and how to avoid them

### Skill Structure

Skills live in `~/.amplifier/skills/` (user-level) or `.amplifier/skills/` (workspace-level):

```
skills/
  dot-graph-syntax/
    SKILL.md              # Main reference (required)
  dot-graph-patterns/
    SKILL.md              # Common patterns
```

### Example Skill: `dot-graph-syntax/SKILL.md`

```markdown
---
name: dot-graph-syntax
description: Use when writing DOT/Graphviz graph definitions, debugging syntax errors, or choosing between graph attributes and layout engines
---

# DOT Graph Syntax Quick Reference

## Overview

Quick reference for DOT graph language syntax. Use when you need to look up
attribute names, syntax patterns, or engine options without spawning a full
DOT expert agent.

## Quick Reference

| Element | Directed | Undirected |
|---------|----------|------------|
| Graph declaration | `digraph G { }` | `graph G { }` |
| Edge | `A -> B` | `A -- B` |
| Subgraph | `subgraph cluster_name { }` | Same |

## Common Attributes

| Attribute | Applies To | Example |
|-----------|-----------|---------|
| `shape` | Node | `[shape=box]`, `[shape=ellipse]`, `[shape=record]` |
| `color` | Node/Edge | `[color=red]`, `[color="#FF0000"]` |
| `label` | Any | `[label="My Label"]` |
| `style` | Any | `[style=dashed]`, `[style=bold]`, `[style=filled]` |
| `rankdir` | Graph | `rankdir=LR` (left-to-right), `rankdir=TB` (top-to-bottom) |

## Layout Engines

| Engine | Best For |
|--------|----------|
| `dot` | Hierarchical/directed graphs (default) |
| `neato` | Undirected graphs, moderate size |
| `fdp` | Large undirected graphs |
| `sfdp` | Very large graphs |
| `circo` | Circular layouts |
| `twopi` | Radial layouts |

## Common Mistakes

- Missing semicolons between statements (optional but recommended)
- Using `->` in undirected graphs (use `--`)
- Forgetting `cluster_` prefix for subgraph boxes to render
- Inline HTML labels need `<` and `>` delimiters, not quotes
```

### Skills vs Agent Context — When to Use Each

| Scenario | Use Skill | Use Agent Context |
|----------|-----------|-------------------|
| Quick syntax lookup during coding | Skill | |
| Creating a complex diagram from scratch | | Agent (dot-author) |
| Remembering attribute names | Skill | |
| Reviewing diagram quality | | Agent (diagram-reviewer) |
| Learning DOT for the first time | Skill | |
| Debugging a rendering issue | | Agent (dot-author) |

**Rule of thumb**: Skills are for *reference lookups*. Agents are for *doing work*.

---

## 8. Namespace and Registration

### How Namespaces Work

The namespace is **always** the `bundle.name` field from YAML frontmatter, NOT the git URL or repo name.

```yaml
# In bundle.md:
bundle:
  name: dot-graph    # <-- THIS is the namespace
```

| Question | Answer |
|----------|--------|
| Namespace is | `dot-graph` (from `bundle.name`) |
| Namespace is NOT | `amplifier-bundle-dot-graph` (the repo name) |

### All Internal References Use the Namespace

```yaml
# Correct references within the bundle:
agents:
  include:
    - dot-graph:dot-author            # Correct
    - amplifier-bundle-dot-graph:dot-author  # WRONG (repo name)
    - dot-graph:agents/dot-author     # WRONG (don't include "agents/" prefix)

context:
  include:
    - dot-graph:context/dot-graph-awareness.md  # Correct (bare namespace:path, no @)
```

### How Others Reference Your Bundle

**As an include (full bundle):**
```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-dot-graph@main
```

**As a behavior include (just the capability):**
```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-bundle-dot-graph@main#subdirectory=behaviors/dot-graph.yaml
```

**Referencing your files after inclusion:**
```markdown
@dot-graph:docs/DOT_SYNTAX_REFERENCE.md    # In markdown (with @)
dot-graph:context/instructions.md           # In YAML (without @)
```

### Path Resolution with Subdirectories

When loaded via `#subdirectory=`, paths are relative to the bundle root (the subdirectory), NOT the git repo root. Don't repeat the subdirectory in paths:

```yaml
# If loaded via: git+https://...@main#subdirectory=behaviors/dot-graph.yaml
# Bundle root is: behaviors/

# WRONG:
context:
  include:
    - dot-graph:behaviors/dot-graph/context/awareness.md   # Duplicates path!

# CORRECT:
context:
  include:
    - dot-graph:context/awareness.md                       # Relative to bundle root
```

### Registering with Foundation

To have your bundle included in the default foundation bundle (like recipes, design-intelligence, etc.), it would be added to foundation's `bundle.md`:

```yaml
includes:
  # ... existing includes ...
  - bundle: git+https://github.com/microsoft/amplifier-bundle-dot-graph@main#subdirectory=behaviors/dot-graph.yaml
```

For standalone use without being part of foundation, users load it directly:

```bash
amplifier run --bundle git+https://github.com/microsoft/amplifier-bundle-dot-graph@main "Create a diagram"
```

---

## 9. Canonical Examples to Study

### Primary Exemplar: `amplifier-bundle-recipes`

**Why study this**: The most complete example of the thin bundle + behavior pattern.

```
amplifier-bundle-recipes/
├── bundle.md                 # THIN: 14 lines of YAML, just includes
├── behaviors/
│   └── recipes.yaml          # Behavior: tool + agents + context
├── agents/
│   ├── recipe-author.md      # Agent with rich description
│   └── result-validator.md   # Agent with output contract
├── context/
│   └── recipe-instructions.md  # Consolidated instructions
├── modules/
│   └── tool-recipes/         # Local tool module with pyproject.toml
├── docs/                     # Heavy documentation
├── examples/                 # Working examples
└── templates/                # Starter templates
```

**Key patterns demonstrated**:
- Thin `bundle.md` — only includes + `@mention` references
- Behavior in `behaviors/` — declares tool + agents + context
- Context de-duplication — single source of truth in `context/`
- Local module — `modules/tool-recipes/` with proper entry point
- Zero duplication of foundation capabilities

**URL**: https://github.com/microsoft/amplifier-bundle-recipes

### Secondary Exemplar: Foundation Itself

Study `foundation:bundle.md` to see how the root foundation bundle composes behaviors:

- Multiple behaviors composed via `includes:`
- External behaviors referenced via full git URLs with `#subdirectory=`
- Internal behaviors referenced via `foundation:behaviors/name`
- Agent declarations via `foundation:agent-name`
- Session, tools, and hooks declared once

### Behavior Exemplars in Foundation

| File | Pattern Demonstrated |
|------|---------------------|
| `foundation:behaviors/foundation-expert.yaml` | Context sink pattern — thin awareness + heavy agent |
| `foundation:behaviors/agents.yaml` | Tool-providing behavior with config |
| `foundation:behaviors/tasks.yaml` | Legacy tool behavior with context injection |
| `foundation:behaviors/streaming-ui.yaml` | Hook-providing behavior |

### Agent Exemplar: `foundation:agents/foundation-expert.md`

Study this for:
- Rich `meta.description` with WHY, WHEN, WHAT, HOW
- Multiple `<example>` blocks with `<commentary>`
- Heavy `@mention` references to docs (context sink)
- `model_role` and `provider_preferences` usage
- Proper ending with `@foundation:context/shared/common-agent-base.md`

---

## 10. Context Sink Pattern

### The Problem

Loading heavyweight DOT documentation (~2000+ lines) into every session wastes tokens. Most sessions don't need DOT knowledge. Those that do should get it on demand.

### The Solution: Agents as Context Sinks

Expert agents carry heavy documentation that loads ONLY when the agent is spawned. Root sessions stay lean.

```
Root Session Token Budget:
├── dot-graph-awareness.md       ~30 lines   (always loaded via behavior)
├── dot-graph-instructions.md    ~50 lines   (loaded via @mention in bundle.md)
└── Total DOT context:           ~80 lines   (<< 2000+ lines of full docs)

dot-author Agent Token Budget (loaded ONLY when spawned):
├── DOT_SYNTAX_REFERENCE.md      ~800 lines  (loaded via @mention in agent)
├── DOT_PATTERNS.md              ~400 lines  (loaded via @mention in agent)
├── DOT_BEST_PRACTICES.md        ~300 lines  (loaded via @mention in agent)
└── Total: ~1500 lines           (burns tokens in sub-session, not root)
```

### Why This Matters

- **Token efficiency**: Heavy docs load ONLY when agent spawns, not in every session
- **Delegation pattern**: Parent sessions stay lean; sub-sessions burn context doing work
- **Results return lean**: The work product (a DOT diagram, a review) returns with far less context than loading all docs into the root session
- **Longer session success**: Critical strategy for sessions that run many turns

### The Three-Layer Structure

**Layer 1: Behavior YAML (thin)**
```yaml
# behaviors/dot-graph.yaml
context:
  include:
    - dot-graph:context/dot-graph-awareness.md    # ~30 lines ONLY
```

**Layer 2: Awareness Pointer (thin)**
```markdown
# context/dot-graph-awareness.md
# "This domain exists. Delegate to these agents. Don't attempt the work yourself."
```

**Layer 3: Agent File (heavy)**
```markdown
# agents/dot-author.md
@dot-graph:docs/DOT_SYNTAX_REFERENCE.md    # Loaded ONLY when agent spawns
@dot-graph:docs/DOT_PATTERNS.md            # Loaded ONLY when agent spawns
@dot-graph:docs/DOT_BEST_PRACTICES.md      # Loaded ONLY when agent spawns
```

### Anti-Pattern: Heavy Context in Behaviors

```yaml
# BAD: Heavy docs in behavior context (loads for EVERYONE who includes this behavior)
context:
  include:
    - dot-graph:docs/DOT_SYNTAX_REFERENCE.md      # 800 lines in every session!
    - dot-graph:docs/DOT_PATTERNS.md               # 400 more lines of bloat!

# GOOD: Thin pointer in behavior, heavy docs in agent
context:
  include:
    - dot-graph:context/dot-graph-awareness.md     # 30 lines: "domain exists, delegate"
```

### Load-on-Demand Alternative

For docs that are SOMETIMES needed but don't warrant a full agent spawn, use **soft references** (text without `@`):

```markdown
# In context/dot-graph-instructions.md

**Documentation (load on demand):**
- Full syntax reference: dot-graph:docs/DOT_SYNTAX_REFERENCE.md
- Common patterns: dot-graph:docs/DOT_PATTERNS.md
- Best practices: dot-graph:docs/DOT_BEST_PRACTICES.md
```

The agent sees these paths and can load them via `read_file` when actually needed, without consuming tokens upfront.

### Token Budget Decision Framework

| Question | If Yes | If No |
|----------|--------|-------|
| Is this content needed for EVERY conversation? | `@mention` (eager load) | |
| Is this content needed for SOME conversations? | Soft reference (load on demand) | |
| Does this content belong to a specific domain? | Move to specialist agent (context sink) | |

---

## 11. Complete File Specifications

### `bundle.md`

```markdown
---
bundle:
  name: dot-graph
  version: 1.0.0
  description: DOT/Graphviz diagram capabilities for creating, validating, rendering, and reasoning about graphs

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: dot-graph:behaviors/dot-graph
---

# DOT Graph Capabilities

@dot-graph:context/dot-graph-instructions.md

---

@foundation:context/shared/common-system-base.md
```

### `behaviors/dot-graph.yaml`

```yaml
bundle:
  name: dot-graph-behavior
  version: 1.0.0
  description: DOT/Graphviz diagram capabilities with authoring and review agents

tools:
  - module: tool-dot-graph
    source: git+https://github.com/microsoft/amplifier-bundle-dot-graph@main#subdirectory=modules/tool-dot-graph
    config:
      default_engine: dot
      output_formats: [svg, png, pdf]

agents:
  include:
    - dot-graph:dot-author
    - dot-graph:diagram-reviewer

context:
  include:
    - dot-graph:context/dot-graph-awareness.md
```

### Standalone Bundle Variant: `bundles/with-anthropic.yaml`

For users who want a ready-to-run bundle:

```yaml
bundle:
  name: dot-graph-anthropic
  version: 1.0.0
  description: DOT/Graphviz capabilities with Anthropic provider

includes:
  - bundle: dot-graph                              # Root bundle (has foundation + behavior)
  - bundle: foundation:providers/anthropic-sonnet   # Add provider choice
```

---

## 12. Anti-Patterns to Avoid

### Duplicating Foundation

```yaml
# DON'T declare tools/session/hooks that foundation provides
tools:
  - module: tool-filesystem     # Foundation has this!
  - module: tool-bash           # Foundation has this!
session:
  orchestrator:                 # Foundation has this!
    module: loop-streaming
```

### Using Repo Name as Namespace

```yaml
# WRONG:
agents:
  include:
    - amplifier-bundle-dot-graph:dot-author   # Repo name

# CORRECT:
agents:
  include:
    - dot-graph:dot-author                    # bundle.name value
```

### Including "agents/" in Agent Paths

```yaml
# WRONG:
agents:
  include:
    - dot-graph:agents/dot-author             # Don't include directory

# CORRECT:
agents:
  include:
    - dot-graph:dot-author                    # System searches /agents automatically
```

### Using `@` in YAML Sections

```yaml
# WRONG (in YAML):
context:
  include:
    - @dot-graph:context/awareness.md         # No @ in YAML!

# CORRECT (in YAML):
context:
  include:
    - dot-graph:context/awareness.md          # Bare namespace:path
```

### Heavy Docs in Behavior Context

```yaml
# WRONG: Loads 1500 lines into every session
context:
  include:
    - dot-graph:docs/DOT_SYNTAX_REFERENCE.md
    - dot-graph:docs/DOT_PATTERNS.md

# CORRECT: Thin pointer, heavy docs in agent
context:
  include:
    - dot-graph:context/dot-graph-awareness.md   # 30 lines
```

### Inline Instructions in bundle.md

```markdown
# WRONG: 200 lines of instructions inline
---
bundle:
  name: dot-graph
---

# DOT Instructions
[200 lines of DOT syntax, patterns, examples...]
```

```markdown
# CORRECT: Reference consolidated context file
---
bundle:
  name: dot-graph
---

@dot-graph:context/dot-graph-instructions.md
```

### Declaring amplifier-core as a Dependency

```toml
# WRONG in modules/tool-dot-graph/pyproject.toml:
dependencies = ["amplifier-core>=1.0.0"]     # Not on PyPI!

# CORRECT:
dependencies = []     # amplifier-core is a peer dependency
```

### Root pyproject.toml

```
# WRONG: Bundle root should not have pyproject.toml
amplifier-bundle-dot-graph/
├── pyproject.toml        # NO - bundles are configuration, not packages
├── bundle.md
└── ...

# CORRECT: Only modules have pyproject.toml
amplifier-bundle-dot-graph/
├── bundle.md             # Root bundle
├── modules/
│   └── tool-dot-graph/
│       ├── pyproject.toml  # Module package config
│       └── ...
└── ...
```

### One-Liner Agent Descriptions

```yaml
# WRONG:
meta:
  description: "Creates DOT diagrams"    # LLM can't match requests to this agent

# CORRECT: 100+ words with WHY, WHEN, WHAT, HOW and examples
meta:
  description: |
    Expert DOT/Graphviz authoring consultant. MUST be used when creating...
    [Full description with activation triggers and examples]
```

---

## 13. Implementation Roadmap

### Phase 1: Minimal Viable Bundle (No Custom Tool)

Start with the simplest thing that works — agents and context only:

```
amplifier-bundle-dot-graph/
├── bundle.md
├── behaviors/
│   └── dot-graph.yaml          # agents + context only (no tools section)
├── agents/
│   ├── dot-author.md
│   └── diagram-reviewer.md
├── context/
│   ├── dot-graph-awareness.md
│   └── dot-graph-instructions.md
├── docs/
│   ├── DOT_SYNTAX_REFERENCE.md
│   └── DOT_BEST_PRACTICES.md
└── README.md
```

This gives you DOT expertise via agents without any custom tooling. The agents can use the existing `bash` tool to run `dot` commands for validation and rendering.

### Phase 2: Add Custom Tool Module

Once the agent pattern is working, add the tool module for better validation and rendering UX:

```
+ modules/
+   └── tool-dot-graph/
+       ├── pyproject.toml
+       └── tool_dot_graph/
+           ├── __init__.py
+           └── tool.py
```

Update `behaviors/dot-graph.yaml` to include the `tools:` section.

### Phase 3: Add Skills

Create complementary skills for quick-reference use cases:

```
+ skills/
+   ├── dot-graph-syntax/
+   │   └── SKILL.md
+   └── dot-graph-patterns/
+       └── SKILL.md
```

### Phase 4: Standalone Variants and Polish

Add pre-composed variants and comprehensive documentation:

```
+ bundles/
+   └── with-anthropic.yaml
+ docs/
+   ├── DOT_PATTERNS.md
+   └── RENDERING_GUIDE.md
+ examples/
+   └── sample-diagrams/
```

### Philosophy Alignment

This roadmap follows the foundational philosophies:

- **Ruthless simplicity**: Start with the minimal structure. Add complexity only when earned.
- **Bricks and studs**: Each component (agent, context file, tool) is modular and regeneratable.
- **Mechanism not policy**: The bundle provides DOT capabilities. Applications decide when and how to use them.

---

## Summary

| Decision | Recommendation |
|----------|---------------|
| Bundle name | `dot-graph` (in `bundle.name`, not repo name) |
| Repo name | `amplifier-bundle-dot-graph` (convention) |
| Pattern | Thin bundle + behavior (like recipes) |
| Agents | `dot-author` (creation) + `diagram-reviewer` (review) |
| Context strategy | Thin awareness in behavior, heavy docs in agents (context sink) |
| Tool | Optional `tool-dot-graph` for validation/rendering |
| Skills | Complementary quick-reference skills |
| Phase 1 focus | Agents + context (no custom tool needed) |

**Your Mantra**: Build with the simplest configuration that meets your needs. Foundation handles the complexity; you add the DOT/Graphviz value.
