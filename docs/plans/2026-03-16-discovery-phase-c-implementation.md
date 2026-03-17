# Discovery Phase C: Discovery Agents — Implementation Plan

> **Execution:** Use the subagent-driven-development workflow to implement this plan.

**Goal:** Create the 5 discovery agent definitions and their corresponding context instruction files, then wire them into the `dot-discovery` behavior.

**Architecture:** Each agent is a markdown file with YAML frontmatter (meta, model_role, optional tools) and a markdown body with investigation methodology. Heavy methodology content lives in separate `context/discovery-*-instructions.md` files that agents `@mention`. The agents are declared in `behaviors/dot-discovery.yaml` so they activate when consumers use the discovery behavior.

**Tech Stack:** Markdown agent definitions, YAML behavior config, Python pytest for content validation.

---

## Task 1: Create context instruction files for prescan and code-tracer

**Files:**
- Create: `context/discovery-prescan-instructions.md`
- Create: `context/discovery-code-tracer-instructions.md`
- Test: `tests/test_discovery_prescan_instructions.py`
- Test: `tests/test_discovery_code_tracer_instructions.py`

### Step 1: Write the prescan instructions test

Create `tests/test_discovery_prescan_instructions.py`:

```python
"""
Tests for context/discovery-prescan-instructions.md existence and required content.
This context file carries the heavy methodology for the discovery-prescan agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
INSTRUCTIONS_PATH = REPO_ROOT / "context" / "discovery-prescan-instructions.md"


def test_prescan_instructions_exists():
    """context/discovery-prescan-instructions.md must exist."""
    assert INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-prescan-instructions.md not found at {INSTRUCTIONS_PATH}"
    )


def test_prescan_instructions_line_count_in_range():
    """File must be between 60 and 150 lines."""
    content = INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 60 <= len(lines) <= 150, f"Expected 60–150 lines, got {len(lines)}"


def test_prescan_instructions_has_heading():
    """File must have a heading about prescan or topic selection."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "# " in content, "Must contain a markdown heading"
    assert "topic" in content.lower() or "prescan" in content.lower(), (
        "Heading must relate to prescan or topic selection"
    )


def test_prescan_instructions_has_topic_selection_criteria():
    """File must describe what makes a good investigation topic."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "topic" in content.lower(), "Must discuss topic selection"
    # Should mention criteria for selecting topics
    assert "module" in content.lower() or "boundary" in content.lower(), (
        "Must mention module boundaries or modules as topic candidates"
    )


def test_prescan_instructions_has_fidelity_guidance():
    """File must mention fidelity tiers affecting topic count."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "fidelity" in content.lower() or "tier" in content.lower(), (
        "Must mention fidelity tiers"
    )


def test_prescan_instructions_has_output_format():
    """File must specify the structured JSON output format."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "json" in content.lower() or "JSON" in content, (
        "Must specify JSON output format"
    )


def test_prescan_instructions_mentions_structural_inventory():
    """File must reference the structural inventory as input."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "inventory" in content.lower() or "structural" in content.lower(), (
        "Must reference structural inventory as input"
    )


def test_prescan_instructions_has_topic_count_range():
    """File must specify 3-7 topics as the target range."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "3" in content and "7" in content, (
        "Must specify 3-7 topic range"
    )
```

### Step 2: Write the code-tracer instructions test

Create `tests/test_discovery_code_tracer_instructions.py`:

```python
"""
Tests for context/discovery-code-tracer-instructions.md existence and required content.
This context file carries the heavy methodology for the discovery-code-tracer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
INSTRUCTIONS_PATH = REPO_ROOT / "context" / "discovery-code-tracer-instructions.md"


def test_code_tracer_instructions_exists():
    """context/discovery-code-tracer-instructions.md must exist."""
    assert INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-code-tracer-instructions.md not found at {INSTRUCTIONS_PATH}"
    )


def test_code_tracer_instructions_line_count_in_range():
    """File must be between 80 and 180 lines."""
    content = INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80–180 lines, got {len(lines)}"


def test_code_tracer_instructions_has_heading():
    """File must have a heading about code tracing methodology."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "# " in content, "Must contain a markdown heading"


def test_code_tracer_instructions_mentions_lsp():
    """File must mention LSP as the primary tool for code tracing."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "LSP" in content, "Must mention LSP"


def test_code_tracer_instructions_mentions_lsp_operations():
    """File must mention specific LSP operations."""
    content = INSTRUCTIONS_PATH.read_text()
    operations = ["goToDefinition", "findReferences", "incomingCalls"]
    found = sum(1 for op in operations if op in content)
    assert found >= 2, (
        f"Must mention at least 2 LSP operations (goToDefinition, findReferences, incomingCalls), found {found}"
    )


def test_code_tracer_instructions_mentions_file_line_evidence():
    """File must require file:line citations."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "file:line" in content.lower() or "file_line" in content.lower() or ("file" in content.lower() and "line" in content.lower()), (
        "Must require file:line citation evidence"
    )


def test_code_tracer_instructions_mentions_dot_output():
    """File must specify DOT diagram as a required output."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content or "DOT" in content, (
        "Must specify DOT diagram output"
    )


def test_code_tracer_instructions_mentions_findings_output():
    """File must specify findings.md as a required output."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "findings.md" in content, "Must specify findings.md as output"


def test_code_tracer_instructions_mentions_execution_paths():
    """File must discuss tracing execution paths."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "execution" in content.lower() or "call chain" in content.lower(), (
        "Must discuss tracing execution paths or call chains"
    )
```

### Step 3: Run tests to verify they fail

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_prescan_instructions.py tests/test_discovery_code_tracer_instructions.py -v --tb=short`

Expected: ALL FAIL — files don't exist yet.

### Step 4: Create `context/discovery-prescan-instructions.md`

Create `context/discovery-prescan-instructions.md` with this content:

```markdown
# Topic Selection Methodology

Instructions for selecting investigation topics from a structural codebase inventory. Load via @mention when dispatched as the prescan agent.

## Input

You receive a **structural inventory** (JSON) from the `prescan` tool containing:
- Language detection and file counts by type
- Module boundaries (Python packages, Rust crates, Go modules, Node packages)
- Build manifests and entry points
- Directory tree with depth

You also have access to the repository itself — read the README and key config files for context.

## Topic Selection Criteria

Select **3–7 investigation topics**. Each topic maps to a module or cross-cutting concern that warrants architectural investigation.

### What Makes a Good Topic

| Signal | Why It Matters |
|--------|---------------|
| Module with many files (>20) | Likely has internal structure worth mapping |
| Module with external dependencies | Integration boundaries need investigation |
| Cross-cutting directory (e.g., `shared/`, `common/`, `utils/`) | Used by many modules — architecture linchpin |
| Entry points (main, CLI, API routes) | Starting points for execution path tracing |
| Configuration layer (env vars, config files, manifests) | Implicit coupling between modules |
| Test directories with complex fixtures | Reveal actual usage patterns |

### What Is NOT a Good Topic

- Generated code directories (e.g., `node_modules/`, `dist/`, `build/`)
- Vendor directories with third-party code
- Documentation-only directories
- Empty or near-empty modules (<3 source files)

## Fidelity Tier Guidance

The number of topics should scale with fidelity tier:

| Tier | Topic Count | Focus |
|------|------------|-------|
| `standard` | 3–5 topics | Core modules and key integration points |
| `deep` | 5–7 topics | Core + peripheral modules + cross-cutting concerns |

At `quick` fidelity, the prescan agent is not invoked — the pipeline reuses the last topic list from `.discovery/manifest.json`.

## Output Format

Produce a structured JSON response with this schema:

```json
{
  "topics": [
    {
      "name": "short-kebab-case-name",
      "description": "One sentence describing the investigation focus",
      "directories": ["src/auth/", "src/middleware/auth.py"],
      "investigation_focus": "How authentication middleware integrates with route handlers",
      "suggested_agents": ["code-tracer", "integration-mapper"]
    }
  ],
  "module_boundaries": [
    {
      "name": "auth",
      "path": "src/auth/",
      "type": "python-package",
      "file_count": 12
    }
  ],
  "rationale": "Brief explanation of why these topics were selected and what was excluded"
}
```

### Field Descriptions

- **name**: Short, stable identifier for the topic (used as directory name in `.discovery/modules/`)
- **description**: Human-readable summary for the approval gate
- **directories**: Source directories and key files relevant to this topic
- **investigation_focus**: Specific question or area the investigation agents should focus on
- **suggested_agents**: Which investigation agents are most relevant (informational — the recipe controls dispatch)
- **module_boundaries**: Detected module boundaries from the structural inventory (passed through for the manifest)
- **rationale**: Why these topics — helps the user at the approval gate

## Process

1. **Read the structural inventory** — understand language, module count, file distribution
2. **Read the README** — understand the project's stated purpose and architecture
3. **Identify module boundaries** — use the inventory's detected modules as candidates
4. **Assess each candidate** — apply the topic selection criteria above
5. **Select topics** — pick 3–7 based on fidelity tier guidance
6. **Produce the JSON output** — follow the schema exactly
```

### Step 5: Create `context/discovery-code-tracer-instructions.md`

Create `context/discovery-code-tracer-instructions.md` with this content:

```markdown
# Code Tracing Methodology

HOW-focused investigation instructions for tracing execution paths through source code. Load via @mention when dispatched as the code-tracer agent.

## Core Principle

You trace **actual code execution paths** — not documentation, not file names, not guesses. Every finding must have file:line evidence from the real source code.

## LSP-First Investigation

Use Language Server Protocol operations as your primary investigation tool. LSP gives you semantic understanding that grep cannot.

| Task | LSP Operation | Why Not Grep |
|------|--------------|-------------|
| Find where a function is defined | `goToDefinition` | Grep returns multiple matches including comments |
| Find all callers of a function | `incomingCalls` | Grep matches string occurrences, not actual calls |
| Understand a function's type signature | `hover` | Grep cannot provide type information |
| Find all usages of a symbol | `findReferences` | Grep includes false positives from strings/comments |
| Trace the call hierarchy outward | `outgoingCalls` | Grep cannot follow call chains semantically |

**Use grep for:** finding text patterns, searching for string literals, locating configuration values. Grep is the right tool for text search — LSP is the right tool for code understanding.

## Evidence Standard

Every claim in your findings MUST have a file:line citation. Format:

```
path/to/file.py:42-58 — Function `process_request` dispatches to handler based on route match
```

A claim without a citation is an assumption, not a finding. In your `findings.md`, every significant observation gets its own section with specific file:line references and an explanation of what the code shows.

## Tracing Methodology

### 1. Identify Entry Points

Start from the entry points relevant to your investigation topic:
- Main functions, CLI entry points, API route handlers
- Public module interfaces (`__init__.py` exports, public functions)
- Event handlers, callback registrations

### 2. Follow the Execution Path

From each entry point, trace forward through:
- **Function calls** — use `goToDefinition` to jump to implementations
- **Conditional branches** — trace both the happy path and error paths
- **Error handling** — what happens when things fail? Follow try/except, Result types, error returns
- **Async boundaries** — where does control flow yield or resume?

### 3. Build the Call Graph

Use `incomingCalls` and `outgoingCalls` to build call hierarchies. Record:
- Which functions call which other functions
- What data flows through the call chain (parameter types, return types)
- Where the call chain crosses module boundaries

### 4. Capture Data Flow

Track how data transforms as it moves through the system:
- What types enter a function vs. what types exit
- Where data is validated, transformed, or enriched
- Where data is persisted or transmitted externally

## Required Artifacts

Write these files to your assigned output directory:

### `findings.md`
Your main analysis — a code-level narrative of how the mechanism works. Organize by execution path or component. Every claim cites file:line evidence.

### `diagram.dot`
A valid DOT diagram showing execution flow, call hierarchy, or data flow. The diagram must:
- Use `digraph` (directed graph) — execution has direction
- Show key functions/components as nodes
- Show call relationships or data flow as edges
- Use `cluster_` subgraphs for module boundaries
- Include a legend if >15 nodes
- Stay within 50–150 lines

## Fresh Context Mandate

You are dispatched with zero prior context about this codebase. Form your own understanding from primary sources — the actual code. Do not attempt to read other agents' output. Your value is your independent, code-level perspective.
```

### Step 6: Run tests to verify they pass

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_prescan_instructions.py tests/test_discovery_code_tracer_instructions.py -v --tb=short`

Expected: ALL PASS

### Step 7: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add context/discovery-prescan-instructions.md context/discovery-code-tracer-instructions.md tests/test_discovery_prescan_instructions.py tests/test_discovery_code_tracer_instructions.py && git commit -m "feat: add prescan and code-tracer instruction context files"
```

---

## Task 2: Create context instruction files for behavior-observer, integration-mapper, and synthesizer

**Files:**
- Create: `context/discovery-behavior-observer-instructions.md`
- Create: `context/discovery-integration-mapper-instructions.md`
- Create: `context/discovery-synthesizer-instructions.md`
- Test: `tests/test_discovery_behavior_observer_instructions.py`
- Test: `tests/test_discovery_integration_mapper_instructions.py`
- Test: `tests/test_discovery_synthesizer_instructions.py`

### Step 1: Write the behavior-observer instructions test

Create `tests/test_discovery_behavior_observer_instructions.py`:

```python
"""
Tests for context/discovery-behavior-observer-instructions.md existence and required content.
This context file carries the heavy methodology for the discovery-behavior-observer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
INSTRUCTIONS_PATH = REPO_ROOT / "context" / "discovery-behavior-observer-instructions.md"


def test_behavior_observer_instructions_exists():
    """context/discovery-behavior-observer-instructions.md must exist."""
    assert INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-behavior-observer-instructions.md not found at {INSTRUCTIONS_PATH}"
    )


def test_behavior_observer_instructions_line_count_in_range():
    """File must be between 80 and 180 lines."""
    content = INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80–180 lines, got {len(lines)}"


def test_behavior_observer_instructions_has_heading():
    """File must have a heading about behavioral observation."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "# " in content, "Must contain a markdown heading"


def test_behavior_observer_instructions_mentions_10_instances():
    """File must require examining 10+ real instances."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "10" in content, "Must mention 10+ instances minimum"


def test_behavior_observer_instructions_mentions_catalog():
    """File must discuss building a catalog."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "catalog" in content.lower(), "Must discuss catalog building"


def test_behavior_observer_instructions_mentions_quantification():
    """File must require quantitative observations."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "quantif" in content.lower() or "count" in content.lower(), (
        "Must require quantitative observations"
    )


def test_behavior_observer_instructions_mentions_patterns():
    """File must discuss identifying patterns."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "pattern" in content.lower(), "Must discuss pattern identification"


def test_behavior_observer_instructions_mentions_dot_output():
    """File must specify DOT diagram as a required output."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content or "DOT" in content, (
        "Must specify DOT diagram output"
    )


def test_behavior_observer_instructions_mentions_catalog_output():
    """File must specify catalog.md as a required output."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "catalog.md" in content, "Must specify catalog.md as output"


def test_behavior_observer_instructions_mentions_patterns_output():
    """File must specify patterns.md as a required output."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "patterns.md" in content, "Must specify patterns.md as output"
```

### Step 2: Write the integration-mapper instructions test

Create `tests/test_discovery_integration_mapper_instructions.py`:

```python
"""
Tests for context/discovery-integration-mapper-instructions.md existence and required content.
This context file carries the heavy methodology for the discovery-integration-mapper agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
INSTRUCTIONS_PATH = REPO_ROOT / "context" / "discovery-integration-mapper-instructions.md"


def test_integration_mapper_instructions_exists():
    """context/discovery-integration-mapper-instructions.md must exist."""
    assert INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-integration-mapper-instructions.md not found at {INSTRUCTIONS_PATH}"
    )


def test_integration_mapper_instructions_line_count_in_range():
    """File must be between 80 and 180 lines."""
    content = INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80–180 lines, got {len(lines)}"


def test_integration_mapper_instructions_has_heading():
    """File must have a heading about integration mapping."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "# " in content, "Must contain a markdown heading"


def test_integration_mapper_instructions_mentions_boundaries():
    """File must discuss cross-boundary analysis."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "boundar" in content.lower(), "Must discuss boundaries"


def test_integration_mapper_instructions_mentions_composition():
    """File must discuss composition effects."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "composition" in content.lower() or "compos" in content.lower(), (
        "Must discuss composition effects"
    )


def test_integration_mapper_instructions_mentions_cross_boundary():
    """File must discuss cross-boundary connections."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "cross" in content.lower(), "Must discuss cross-boundary connections"


def test_integration_mapper_instructions_mentions_dot_output():
    """File must specify DOT diagram as a required output."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content or "DOT" in content, (
        "Must specify DOT diagram output"
    )


def test_integration_mapper_instructions_mentions_integration_map():
    """File must specify integration-map.md as a required output."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "integration-map.md" in content, "Must specify integration-map.md as output"


def test_integration_mapper_instructions_mentions_evidence():
    """File must require evidence at boundaries."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "evidence" in content.lower(), "Must require evidence"
```

### Step 3: Write the synthesizer instructions test

Create `tests/test_discovery_synthesizer_instructions.py`:

```python
"""
Tests for context/discovery-synthesizer-instructions.md existence and required content.
This context file carries the heavy methodology for the discovery-synthesizer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
INSTRUCTIONS_PATH = REPO_ROOT / "context" / "discovery-synthesizer-instructions.md"


def test_synthesizer_instructions_exists():
    """context/discovery-synthesizer-instructions.md must exist."""
    assert INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-synthesizer-instructions.md not found at {INSTRUCTIONS_PATH}"
    )


def test_synthesizer_instructions_line_count_in_range():
    """File must be between 100 and 220 lines."""
    content = INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 100 <= len(lines) <= 220, f"Expected 100–220 lines, got {len(lines)}"


def test_synthesizer_instructions_has_heading():
    """File must have a heading about reconciliation or synthesis."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "# " in content, "Must contain a markdown heading"


def test_synthesizer_instructions_mentions_reconciliation():
    """File must discuss reconciliation methodology."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "reconcil" in content.lower(), "Must discuss reconciliation"


def test_synthesizer_instructions_mentions_four_phases():
    """File must describe a multi-phase reconciliation process."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "phase" in content.lower(), "Must describe phases of reconciliation"


def test_synthesizer_instructions_mentions_discrepancy_tracking():
    """File must require discrepancy tracking with IDs."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "discrepanc" in content.lower(), "Must mention discrepancy tracking"
    assert "D-0" in content or "d-0" in content, (
        "Must show discrepancy ID format (D-01, D-02, etc.)"
    )


def test_synthesizer_instructions_mentions_no_reconciliation_by_fiat():
    """File must prohibit reconciliation by fiat."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "fiat" in content.lower() or "never pick" in content.lower(), (
        "Must prohibit reconciliation by fiat"
    )


def test_synthesizer_instructions_mentions_consensus_dot():
    """File must specify producing a consensus DOT diagram."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content or "consensus" in content.lower(), (
        "Must specify consensus DOT output"
    )


def test_synthesizer_instructions_mentions_bounded_output():
    """File must specify output bounds (line count, node count)."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "250" in content or "80" in content, (
        "Must specify output bounds (≤250 lines or ≤80 nodes)"
    )


def test_synthesizer_instructions_mentions_quality_gate():
    """File must mention the quality gate / validation loop."""
    content = INSTRUCTIONS_PATH.read_text()
    assert "quality gate" in content.lower() or "validation" in content.lower(), (
        "Must mention quality gate or validation loop"
    )


def test_synthesizer_instructions_mentions_all_agent_outputs():
    """File must require reading ALL agent outputs."""
    content = INSTRUCTIONS_PATH.read_text()
    content_upper = content.upper()
    assert "ALL" in content_upper or "every" in content.lower(), (
        "Must require reading ALL agent outputs"
    )
```

### Step 4: Run tests to verify they fail

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_behavior_observer_instructions.py tests/test_discovery_integration_mapper_instructions.py tests/test_discovery_synthesizer_instructions.py -v --tb=short`

Expected: ALL FAIL — files don't exist yet.

### Step 5: Create `context/discovery-behavior-observer-instructions.md`

Create `context/discovery-behavior-observer-instructions.md` with this content:

```markdown
# Behavioral Observation Methodology

WHAT-focused investigation instructions for cataloging real instances and quantifying patterns. Load via @mention when dispatched as the behavior-observer agent.

## Core Principle

You observe **what actually exists** — not what documentation says should exist. Patterns only emerge from examining MANY instances. A single file read misses the forest for the trees.

## The 10-Instance Minimum

This is non-negotiable. Read at LEAST 10 real instances of whatever you are investigating. If fewer than 10 exist, read ALL of them and note the small sample size.

Patterns identified from fewer than 10 instances are hypotheses, not findings.

## Observation Methodology

### 1. Find All Instances

Use filesystem search (glob, grep) to locate ALL instances of the mechanism or artifact type you are investigating. Do not stop at the first few — find them all. Record the total count.

### 2. Build the Catalog First

Do not start with a hypothesis. Build a structured catalog of everything you find:

For each instance, record:
- **Name/location** — file path and identifier
- **Key structural attributes** — size (lines), type, complexity indicators
- **Notable features** — anything unusual or distinctive
- **Category** — classification based on what you observe

The catalog is your evidence base. Build it before you draw conclusions.

### 3. Quantify Everything

Do not say "most" — say "14 of 24 (58%)."
Do not say "large files" — say "median 89 lines, range 12–414."

Quantitative claims are verifiable. Qualitative impressions are not. Every pattern claim must have a count or percentage behind it.

### 4. Identify Patterns from the Catalog

After building the complete catalog, look for:
- **Common patterns** — what do most instances share?
- **Variations** — what are the distinct categories or approaches?
- **Anti-patterns** — what appears problematic or inconsistent?
- **Outliers** — what instances don't fit any pattern? (Often the most interesting.)

### 5. Distinguish Intent from Reality

When documentation and reality disagree, reality wins. If the README says "all modules use pattern X" but your catalog shows 58% do, your number is the finding. Document the gap between stated intent and observed reality.

## Required Artifacts

Write these files to your assigned output directory:

### `catalog.md`
Structured inventory of every instance you examined. For each: name, location, key attributes, classification. This is your evidence base — it must be comprehensive.

### `patterns.md`
Cross-cutting patterns and anti-patterns observed across instances. Each pattern includes: where observed, frequency (count and percentage), and implications.

### `findings.md`
Your main analysis — behavioral observations organized by topic, with quantitative support from the catalog. This is what the synthesizer reads first.

### `diagram.dot`
A valid DOT diagram showing taxonomy, relationships, or pattern distribution. The diagram must:
- Show categories or patterns as clusters
- Show instances or components as nodes
- Show relationships or data flow as edges
- Include counts or percentages as labels where relevant
- Include a legend if >15 nodes
- Stay within 50–150 lines

## Fresh Context Mandate

You are dispatched with zero prior context about this codebase. Form your own understanding from primary sources — the actual artifacts. Do not attempt to read other agents' output. Your value is your independent, breadth-of-observation perspective.
```

### Step 6: Create `context/discovery-integration-mapper-instructions.md`

Create `context/discovery-integration-mapper-instructions.md` with this content:

```markdown
# Integration Mapping Methodology

WHERE/WHY-focused investigation instructions for mapping cross-boundary connections and composition effects. Load via @mention when dispatched as the integration-mapper agent.

## Core Principle

The most architecturally significant insights live at **boundaries** between components. You find what the other agents miss — the cross-cutting concerns, composition effects, and emergent behavior that only appear when mechanisms interact.

## Boundary Analysis Method

### 1. Identify All Mechanisms in Scope

List every module, subsystem, or component that touches your investigation topic. This is your boundary map — the starting point for systematic analysis.

### 2. For Every Mechanism, Ask About Every Other Mechanism

This is your core method. For every pair of mechanisms that interact, ask:
- **What crosses the boundary?** — data, control flow, configuration, events
- **In which direction?** — unidirectional, bidirectional, or asymmetric
- **What gets transformed?** — type conversions, data enrichment, format changes
- **What assumptions does each side make?** — about types, ordering, availability, error handling

### 3. Find Composition Effects

Look for behavior that only emerges when mechanisms interact:
- Does combining two working components produce unexpected results?
- Are there ordering dependencies between mechanisms?
- Do mechanisms compete for shared resources?
- Does mechanism A assume something that mechanism B violates?

### 4. Map Both Explicit and Implicit Dependencies

**Explicit dependencies** are visible: imports, API calls, function parameters.

**Implicit dependencies** are hidden but equally important:
- Shared databases or file paths
- Environment variable coupling
- Message queues or event buses
- Shared configuration that both sides read
- Naming conventions that create coupling
- Ordering assumptions (A must run before B)

### 5. Use Both Code and Architecture

Use LSP to trace specific integration points (`findReferences` across module boundaries, `hover` to check type contracts at boundaries). Use architectural reasoning to identify where boundaries SHOULD be and check if they match where they ARE.

## Evidence Standard

For every integration point, cite evidence on BOTH sides of the boundary:
- What one mechanism sends (with file:line)
- What the other receives (with file:line)
- Where transformations happen (with file:line)

Single-sided evidence is incomplete. Cross-boundary claims require cross-boundary citations.

## Required Artifacts

Write these files to your assigned output directory:

### `integration-map.md`
Comprehensive cross-boundary analysis. For every integration point: what crosses the boundary, in which direction, what gets transformed, and what the architectural implications are.

### `diagram.dot`
A valid DOT diagram showing integration points and data flow. The diagram must:
- Show mechanisms/modules as nodes or cluster subgraphs
- Show boundaries as edges with labels describing what crosses them
- Show direction of data/control flow with arrow direction
- Distinguish explicit dependencies (solid lines) from implicit ones (dashed lines)
- Include a legend if >15 nodes
- Stay within 50–150 lines

## Fresh Context Mandate

You are dispatched with zero prior context about this codebase. Form your own understanding from primary sources — the actual code and configuration. Do not attempt to read other agents' output. Your value is your independent, boundary-focused perspective.
```

### Step 7: Create `context/discovery-synthesizer-instructions.md`

Create `context/discovery-synthesizer-instructions.md` with this content:

```markdown
# Reconciliation Methodology

4-phase reconciliation instructions for synthesizing multi-agent investigation outputs into a consensus DOT diagram. Load via @mention when dispatched as the synthesizer agent.

## Core Principle

You reconcile — you do not investigate. Your input is the output of 1–3 investigation agents who each examined the same module from different angles. Your job is to synthesize their findings into a single consensus DOT diagram, tracking discrepancies as first-class artifacts.

**The cardinal rule: never reconcile by fiat.** When agents disagree, the disagreement itself is information. If you pick "the more plausible answer," you destroy the signal the discrepancy carries.

## 4-Phase Reconciliation Process

### Phase 1: Survey

Read ALL agent outputs for this module. Never skip any agent's work. Read in this order:
1. `findings.md` from each agent — the narrative analysis
2. `diagram.dot` from each agent — the structural model
3. Supporting artifacts (`catalog.md`, `patterns.md`, `integration-map.md`) if present

Build a mental model of what each agent found. Note where they agree and where they differ.

### Phase 2: Convergence Identification

Identify findings that multiple agents independently confirm:
- Same component identified by 2+ agents → high confidence → include in consensus
- Same relationship identified by 2+ agents → high confidence → include in consensus
- Component identified by only 1 agent → medium confidence → include with annotation

Multi-agent confirmation is the strongest evidence available. Prioritize these findings.

### Phase 3: Discrepancy Tracking

For every disagreement between agents, create a discrepancy record:

```
**D-01: [Short description]**
- Agent A claims: [specific claim with reference to their artifact]
- Agent B claims: [specific claim with reference to their artifact]
- Impact: HIGH / MEDIUM / LOW
- Resolution: [Do NOT resolve — note what evidence would be needed]
```

Assign sequential IDs: D-01, D-02, D-03, etc. Never merge or suppress discrepancies. Every disagreement gets an ID and stays visible.

**Impact levels:**
- **HIGH** — affects the diagram's structural representation (missing component, wrong relationship direction)
- **MEDIUM** — affects understanding but not structure (different labeling, disputed importance)
- **LOW** — cosmetic or informational (naming preferences, documentation gaps)

### Phase 4: Consensus Synthesis

Produce the consensus `diagram.dot` by:
1. Starting with multi-agent confirmed nodes and edges (Phase 2)
2. Adding single-agent nodes with appropriate annotation (lower visual weight)
3. Representing HIGH discrepancies visually (e.g., dashed edges for disputed relationships)
4. Including a legend that explains confidence levels

## Anti-Rationalization Table

Before finalizing, check your work against these anti-patterns:

| Anti-Pattern | What It Looks Like | What to Do Instead |
|-------------|-------------------|-------------------|
| Reconciliation by fiat | "Agent A's version seems more complete, so I'll use it" | Track as discrepancy D-XX, include both perspectives |
| Suppressing minority findings | Omitting something only one agent found | Include with single-agent annotation, lower visual weight |
| Inventing connections | Adding edges not supported by any agent's findings | Only include what agents actually found |
| Over-merging | Combining distinct concepts into one node | If agents distinguished them, keep them separate |
| Ignoring unknowns | Not mentioning what agents couldn't determine | Consolidate unknowns — they inform future investigation |

## Output Bounds

The consensus diagram must stay bounded:
- **Line count:** 150–250 lines maximum
- **Node count:** ≤80 nodes
- **Must include:** a rendered legend explaining shapes, colors, and confidence levels
- **Must include:** graph-level `label` with module name and agent count

If the combined agent findings would exceed these bounds, prioritize:
1. Multi-agent confirmed components (always include)
2. HIGH-impact single-agent findings (include)
3. MEDIUM-impact findings (include if within bounds)
4. LOW-impact findings (omit with note in discrepancies)

## Quality Gate Awareness

After you produce the consensus `diagram.dot`, the pipeline runs `dot_graph validate` on it. If validation fails, you will receive the error report and must regenerate. This loop runs up to 3 iterations.

Common validation failures to avoid:
- Unbalanced braces or missing semicolons
- `shape=record` usage (use HTML labels instead)
- Orphan nodes (every node must have at least one edge)
- Missing `cluster_` prefix on subgraph names
- Missing graph-level `fontname` and `rankdir` attributes

## Required Artifacts

### `diagram.dot`
The consensus DOT diagram — your primary output. Must be valid DOT syntax, bounded as specified above.

### `discrepancies.md`
All discrepancies tracked with IDs. For each: what the agents disagree on, impact level, and what evidence would resolve it. This is a first-class artifact, not a footnote.

### `findings.md`
Reconciliation narrative — what the agents collectively discovered about this module, what was confirmed by multiple perspectives, and what remains uncertain.
```

### Step 8: Run tests to verify they pass

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_behavior_observer_instructions.py tests/test_discovery_integration_mapper_instructions.py tests/test_discovery_synthesizer_instructions.py -v --tb=short`

Expected: ALL PASS

### Step 9: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add context/discovery-behavior-observer-instructions.md context/discovery-integration-mapper-instructions.md context/discovery-synthesizer-instructions.md tests/test_discovery_behavior_observer_instructions.py tests/test_discovery_integration_mapper_instructions.py tests/test_discovery_synthesizer_instructions.py && git commit -m "feat: add behavior-observer, integration-mapper, synthesizer instruction context files"
```

---

## Task 3: Create the 5 discovery agent definitions

**Files:**
- Create: `agents/discovery-prescan.md`
- Create: `agents/discovery-code-tracer.md`
- Create: `agents/discovery-behavior-observer.md`
- Create: `agents/discovery-integration-mapper.md`
- Create: `agents/discovery-synthesizer.md`
- Test: `tests/test_discovery_prescan_agent.py`
- Test: `tests/test_discovery_code_tracer_agent.py`
- Test: `tests/test_discovery_behavior_observer_agent.py`
- Test: `tests/test_discovery_integration_mapper_agent.py`
- Test: `tests/test_discovery_synthesizer_agent.py`

### Step 1: Write the agent test files

All 5 agent tests follow the same pattern established by `tests/test_dot_author_agent.py`. Create each test file.

Create `tests/test_discovery_prescan_agent.py`:

```python
"""
Tests for agents/discovery-prescan.md existence and required content.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
AGENT_PATH = REPO_ROOT / "agents" / "discovery-prescan.md"


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (frontmatter_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    yaml_block = content[3:end].strip()
    body = content[end + 3 :].strip()
    return yaml.safe_load(yaml_block), body


def test_agent_exists():
    """agents/discovery-prescan.md must exist."""
    assert AGENT_PATH.exists(), f"agents/discovery-prescan.md not found at {AGENT_PATH}"


def test_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = AGENT_PATH.read_text()
    assert content.startswith("---"), "Must start with YAML frontmatter (---)"
    assert content.count("---") >= 2, "Must have closing --- for frontmatter"


def test_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-prescan'."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-prescan", (
        f"meta.name must be 'discovery-prescan', got: {frontmatter['meta'].get('name')}"
    )


def test_frontmatter_has_description():
    """Frontmatter must have meta.description."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], "meta must have 'description'"
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_description_has_examples():
    """Description must contain at least 2 <example> blocks."""
    content = AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_frontmatter_model_role():
    """Frontmatter must have model_role: reasoning."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert frontmatter.get("model_role") == "reasoning", (
        f"model_role must be 'reasoning', got: {frontmatter.get('model_role')}"
    )


def test_body_has_main_heading():
    """Markdown body must contain a heading with 'Prescan'."""
    content = AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "# " in body, "Body must contain a heading"
    assert "prescan" in body.lower() or "Prescan" in body, (
        "Body heading must relate to prescan"
    )


def test_body_mentions_structural_inventory():
    """Body must mention structural inventory as input."""
    content = AGENT_PATH.read_text()
    assert "structural" in content.lower() or "inventory" in content.lower(), (
        "Must mention structural inventory"
    )


def test_body_mentions_topic_selection():
    """Body must discuss topic selection."""
    content = AGENT_PATH.read_text()
    assert "topic" in content.lower(), "Must discuss topic selection"


def test_body_references_instructions():
    """Body must @mention the prescan instructions context file."""
    content = AGENT_PATH.read_text()
    assert "discovery-prescan-instructions" in content, (
        "Must @mention discovery-prescan-instructions context file"
    )


def test_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "Must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "Must END with @foundation:context/shared/common-agent-base.md"
    )
```

Create `tests/test_discovery_code_tracer_agent.py`:

```python
"""
Tests for agents/discovery-code-tracer.md existence and required content.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
AGENT_PATH = REPO_ROOT / "agents" / "discovery-code-tracer.md"


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (frontmatter_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    yaml_block = content[3:end].strip()
    body = content[end + 3 :].strip()
    return yaml.safe_load(yaml_block), body


def test_agent_exists():
    """agents/discovery-code-tracer.md must exist."""
    assert AGENT_PATH.exists(), f"agents/discovery-code-tracer.md not found at {AGENT_PATH}"


def test_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = AGENT_PATH.read_text()
    assert content.startswith("---"), "Must start with YAML frontmatter (---)"
    assert content.count("---") >= 2, "Must have closing --- for frontmatter"


def test_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-code-tracer'."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-code-tracer", (
        f"meta.name must be 'discovery-code-tracer', got: {frontmatter['meta'].get('name')}"
    )


def test_frontmatter_has_description():
    """Frontmatter must have meta.description."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], "meta must have 'description'"
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_description_has_examples():
    """Description must contain at least 2 <example> blocks."""
    content = AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_frontmatter_model_role():
    """Frontmatter must have model_role: coding."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert frontmatter.get("model_role") == "coding", (
        f"model_role must be 'coding', got: {frontmatter.get('model_role')}"
    )


def test_frontmatter_has_tools():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"


def test_body_has_main_heading():
    """Markdown body must contain a heading about code tracing."""
    content = AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "# " in body, "Body must contain a heading"


def test_body_mentions_how():
    """Body must identify this agent as the HOW agent."""
    content = AGENT_PATH.read_text()
    assert "HOW" in content, "Must identify as the HOW agent"


def test_body_mentions_fresh_context():
    """Body must contain fresh context mandate."""
    content = AGENT_PATH.read_text()
    assert "fresh context" in content.lower() or "zero prior context" in content.lower(), (
        "Must contain fresh context mandate"
    )


def test_body_mentions_independent_perspective():
    """Body must emphasize independent perspective."""
    content = AGENT_PATH.read_text()
    assert "independent" in content.lower(), "Must mention independent perspective"


def test_body_references_instructions():
    """Body must @mention the code-tracer instructions context file."""
    content = AGENT_PATH.read_text()
    assert "discovery-code-tracer-instructions" in content, (
        "Must @mention discovery-code-tracer-instructions context file"
    )


def test_body_mentions_dot_output():
    """Body must require diagram.dot as output."""
    content = AGENT_PATH.read_text()
    assert "diagram.dot" in content, "Must require diagram.dot output"


def test_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "Must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "Must END with @foundation:context/shared/common-agent-base.md"
    )
```

Create `tests/test_discovery_behavior_observer_agent.py`:

```python
"""
Tests for agents/discovery-behavior-observer.md existence and required content.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
AGENT_PATH = REPO_ROOT / "agents" / "discovery-behavior-observer.md"


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (frontmatter_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    yaml_block = content[3:end].strip()
    body = content[end + 3 :].strip()
    return yaml.safe_load(yaml_block), body


def test_agent_exists():
    """agents/discovery-behavior-observer.md must exist."""
    assert AGENT_PATH.exists(), f"agents/discovery-behavior-observer.md not found at {AGENT_PATH}"


def test_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = AGENT_PATH.read_text()
    assert content.startswith("---"), "Must start with YAML frontmatter (---)"
    assert content.count("---") >= 2, "Must have closing --- for frontmatter"


def test_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-behavior-observer'."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-behavior-observer", (
        f"meta.name must be 'discovery-behavior-observer', got: {frontmatter['meta'].get('name')}"
    )


def test_frontmatter_has_description():
    """Frontmatter must have meta.description."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], "meta must have 'description'"
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_description_has_examples():
    """Description must contain at least 2 <example> blocks."""
    content = AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_frontmatter_model_role():
    """Frontmatter must have model_role: research."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert frontmatter.get("model_role") == "research", (
        f"model_role must be 'research', got: {frontmatter.get('model_role')}"
    )


def test_body_has_main_heading():
    """Markdown body must contain a heading."""
    content = AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "# " in body, "Body must contain a heading"


def test_body_mentions_what():
    """Body must identify this agent as the WHAT agent."""
    content = AGENT_PATH.read_text()
    assert "WHAT" in content, "Must identify as the WHAT agent"


def test_body_mentions_fresh_context():
    """Body must contain fresh context mandate."""
    content = AGENT_PATH.read_text()
    assert "fresh context" in content.lower() or "zero prior context" in content.lower(), (
        "Must contain fresh context mandate"
    )


def test_body_mentions_10_instances():
    """Body must require 10+ real instances."""
    content = AGENT_PATH.read_text()
    assert "10" in content, "Must mention 10+ instances"


def test_body_references_instructions():
    """Body must @mention the behavior-observer instructions context file."""
    content = AGENT_PATH.read_text()
    assert "discovery-behavior-observer-instructions" in content, (
        "Must @mention discovery-behavior-observer-instructions context file"
    )


def test_body_mentions_dot_output():
    """Body must require diagram.dot as output."""
    content = AGENT_PATH.read_text()
    assert "diagram.dot" in content, "Must require diagram.dot output"


def test_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "Must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "Must END with @foundation:context/shared/common-agent-base.md"
    )
```

Create `tests/test_discovery_integration_mapper_agent.py`:

```python
"""
Tests for agents/discovery-integration-mapper.md existence and required content.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
AGENT_PATH = REPO_ROOT / "agents" / "discovery-integration-mapper.md"


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (frontmatter_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    yaml_block = content[3:end].strip()
    body = content[end + 3 :].strip()
    return yaml.safe_load(yaml_block), body


def test_agent_exists():
    """agents/discovery-integration-mapper.md must exist."""
    assert AGENT_PATH.exists(), f"agents/discovery-integration-mapper.md not found at {AGENT_PATH}"


def test_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = AGENT_PATH.read_text()
    assert content.startswith("---"), "Must start with YAML frontmatter (---)"
    assert content.count("---") >= 2, "Must have closing --- for frontmatter"


def test_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-integration-mapper'."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-integration-mapper", (
        f"meta.name must be 'discovery-integration-mapper', got: {frontmatter['meta'].get('name')}"
    )


def test_frontmatter_has_description():
    """Frontmatter must have meta.description."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], "meta must have 'description'"
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_description_has_examples():
    """Description must contain at least 2 <example> blocks."""
    content = AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_frontmatter_model_role():
    """Frontmatter must have model_role: reasoning."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert frontmatter.get("model_role") == "reasoning", (
        f"model_role must be 'reasoning', got: {frontmatter.get('model_role')}"
    )


def test_frontmatter_has_tools():
    """Frontmatter must declare tools."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"


def test_body_has_main_heading():
    """Markdown body must contain a heading."""
    content = AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "# " in body, "Body must contain a heading"


def test_body_mentions_where_why():
    """Body must identify this agent as the WHERE/WHY agent."""
    content = AGENT_PATH.read_text()
    assert "WHERE" in content or "WHY" in content, "Must identify as WHERE/WHY agent"


def test_body_mentions_fresh_context():
    """Body must contain fresh context mandate."""
    content = AGENT_PATH.read_text()
    assert "fresh context" in content.lower() or "zero prior context" in content.lower(), (
        "Must contain fresh context mandate"
    )


def test_body_mentions_boundaries():
    """Body must discuss cross-boundary investigation."""
    content = AGENT_PATH.read_text()
    assert "boundar" in content.lower(), "Must discuss boundaries"


def test_body_references_instructions():
    """Body must @mention the integration-mapper instructions context file."""
    content = AGENT_PATH.read_text()
    assert "discovery-integration-mapper-instructions" in content, (
        "Must @mention discovery-integration-mapper-instructions context file"
    )


def test_body_mentions_dot_output():
    """Body must require diagram.dot as output."""
    content = AGENT_PATH.read_text()
    assert "diagram.dot" in content, "Must require diagram.dot output"


def test_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "Must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "Must END with @foundation:context/shared/common-agent-base.md"
    )
```

Create `tests/test_discovery_synthesizer_agent.py`:

```python
"""
Tests for agents/discovery-synthesizer.md existence and required content.
"""

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
AGENT_PATH = REPO_ROOT / "agents" / "discovery-synthesizer.md"


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (frontmatter_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    yaml_block = content[3:end].strip()
    body = content[end + 3 :].strip()
    return yaml.safe_load(yaml_block), body


def test_agent_exists():
    """agents/discovery-synthesizer.md must exist."""
    assert AGENT_PATH.exists(), f"agents/discovery-synthesizer.md not found at {AGENT_PATH}"


def test_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = AGENT_PATH.read_text()
    assert content.startswith("---"), "Must start with YAML frontmatter (---)"
    assert content.count("---") >= 2, "Must have closing --- for frontmatter"


def test_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-synthesizer'."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-synthesizer", (
        f"meta.name must be 'discovery-synthesizer', got: {frontmatter['meta'].get('name')}"
    )


def test_frontmatter_has_description():
    """Frontmatter must have meta.description."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], "meta must have 'description'"
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_description_has_examples():
    """Description must contain at least 2 <example> blocks."""
    content = AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_frontmatter_model_role():
    """Frontmatter must have model_role: reasoning."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert frontmatter.get("model_role") == "reasoning", (
        f"model_role must be 'reasoning', got: {frontmatter.get('model_role')}"
    )


def test_frontmatter_has_tools():
    """Frontmatter must declare tools."""
    content = AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"


def test_body_has_main_heading():
    """Markdown body must contain a heading."""
    content = AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert "# " in body, "Body must contain a heading"


def test_body_mentions_reconciliation():
    """Body must discuss reconciliation."""
    content = AGENT_PATH.read_text()
    assert "reconcil" in content.lower(), "Must discuss reconciliation"


def test_body_mentions_discrepancy_tracking():
    """Body must mention discrepancy tracking."""
    content = AGENT_PATH.read_text()
    assert "discrepanc" in content.lower(), "Must mention discrepancy tracking"


def test_body_mentions_consensus():
    """Body must mention consensus diagram."""
    content = AGENT_PATH.read_text()
    assert "consensus" in content.lower(), "Must mention consensus"


def test_body_mentions_no_fiat():
    """Body must prohibit reconciliation by fiat."""
    content = AGENT_PATH.read_text()
    assert "fiat" in content.lower(), "Must prohibit reconciliation by fiat"


def test_body_references_instructions():
    """Body must @mention the synthesizer instructions context file."""
    content = AGENT_PATH.read_text()
    assert "discovery-synthesizer-instructions" in content, (
        "Must @mention discovery-synthesizer-instructions context file"
    )


def test_body_mentions_dot_output():
    """Body must require diagram.dot as output."""
    content = AGENT_PATH.read_text()
    assert "diagram.dot" in content, "Must require diagram.dot output"


def test_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "Must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "Must END with @foundation:context/shared/common-agent-base.md"
    )
```

### Step 2: Run tests to verify they fail

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_prescan_agent.py tests/test_discovery_code_tracer_agent.py tests/test_discovery_behavior_observer_agent.py tests/test_discovery_integration_mapper_agent.py tests/test_discovery_synthesizer_agent.py -v --tb=short`

Expected: ALL FAIL — agent files don't exist yet.

### Step 3: Create the 5 agent files

Each agent file follows the exact frontmatter format from `agents/dot-author.md`. The description field uses the WHY/WHEN/WHAT/HOW pattern with `<example>` blocks. The body `@mentions` the corresponding instruction file and `@foundation:context/shared/common-agent-base.md` at the end.

**Key patterns from the Parallax Discovery agents to adapt:**
- Fresh context mandate: "You run as a sub-session with fresh context. You have NO knowledge of what other agents have found."
- Independent perspective: "Your perspective must be genuinely yours, formed from primary sources only."
- Role boundaries: Explicitly state what IS and IS NOT this agent's job
- Required artifacts: Exact file names and formats
- DOT as primary output: Every investigation agent must produce `diagram.dot`

**Key differences from Parallax agents:**
- Our agents use `@dot-graph:context/discovery-*-instructions.md` instead of `@parallax-discovery:context/methodology.md`
- Our agents use `tool-dot-graph` for DOT validation, not separate filesystem/search/bash/lsp tools
- Our agents write to `.discovery/modules/<name>/agents/<agent>/` instead of `.investigation/wave-*/team-*/agent-*/`
- Our prescan agent is new (not in Parallax) — it's a topic selector, not an investigator

**Create `agents/discovery-prescan.md`** — The topic selector agent. Reads structural inventory JSON + README, selects 3–7 investigation topics. model_role: reasoning. No tools needed (receives inventory as input). @mentions `discovery-prescan-instructions.md`.

**Create `agents/discovery-code-tracer.md`** — The HOW agent. Traces execution paths, call chains, data flow. Produces findings.md + diagram.dot with file:line evidence. model_role: coding. Tools: tool-dot-graph. @mentions `discovery-code-tracer-instructions.md`. Adapted from Parallax `code-tracer.md`.

**Create `agents/discovery-behavior-observer.md`** — The WHAT agent. Catalogs real instances (10+ minimum), quantifies patterns. Produces catalog.md + patterns.md + diagram.dot. model_role: research. Tools: tool-dot-graph. @mentions `discovery-behavior-observer-instructions.md`. Adapted from Parallax `behavior-observer.md`.

**Create `agents/discovery-integration-mapper.md`** — The WHERE/WHY agent. Maps cross-boundary connections, finds composition effects at boundaries. Produces integration-map.md + diagram.dot. model_role: reasoning. Tools: tool-dot-graph. @mentions `discovery-integration-mapper-instructions.md`. Adapted from Parallax `integration-mapper.md`.

**Create `agents/discovery-synthesizer.md`** — The reconciler. Reads all agent DOT outputs, synthesizes consensus diagram.dot, tracks discrepancies. Anti-rationalization discipline. model_role: reasoning. Tools: tool-dot-graph. @mentions `discovery-synthesizer-instructions.md`. Adapted from Parallax `lead-investigator.md` combined with dot-docs synthesis methodology.

For each agent, the frontmatter description must include:
1. One-sentence role description
2. When to use (dispatched by recipe, which fidelity tiers)
3. What it's authoritative on
4. What it MUST be used for (bullet list)
5. At least 2 `<example>` blocks with `<commentary>`

The body must include:
1. `# Agent Name` heading
2. Bold one-line summary
3. Execution model statement (one-shot, fresh context)
4. `## Your Knowledge` section with @mention to instruction file
5. `## Your Role` section describing this agent's focus and what's NOT its job
6. Brief operating principles (delegate heavy methodology to the instruction file)
7. `## Required Artifacts` section listing exact output file names
8. `## Final Response Contract` section
9. `---` separator
10. `@foundation:context/shared/common-agent-base.md`

### Step 4: Run tests to verify they pass

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_prescan_agent.py tests/test_discovery_code_tracer_agent.py tests/test_discovery_behavior_observer_agent.py tests/test_discovery_integration_mapper_agent.py tests/test_discovery_synthesizer_agent.py -v --tb=short`

Expected: ALL PASS

### Step 5: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add agents/discovery-prescan.md agents/discovery-code-tracer.md agents/discovery-behavior-observer.md agents/discovery-integration-mapper.md agents/discovery-synthesizer.md tests/test_discovery_prescan_agent.py tests/test_discovery_code_tracer_agent.py tests/test_discovery_behavior_observer_agent.py tests/test_discovery_integration_mapper_agent.py tests/test_discovery_synthesizer_agent.py && git commit -m "feat: add 5 discovery agent definitions"
```

---

## Task 4: Update `behaviors/dot-discovery.yaml` to declare the 5 agents

**Files:**
- Modify: `behaviors/dot-discovery.yaml`
- Modify: `tests/test_dot_discovery_behavior.py`

### Step 1: Update the behavior test to require agents

Add these tests to the end of `tests/test_dot_discovery_behavior.py`:

```python
# --- agents section ---


def test_behavior_has_agents_key(data):
    """behaviors/dot-discovery.yaml must have an 'agents' key."""
    assert "agents" in data, "behaviors/dot-discovery.yaml must have 'agents' key"


def test_behavior_agents_has_include(data):
    """agents must have an 'include' key."""
    assert "include" in data["agents"], "agents must have an 'include' key"


def test_behavior_agents_includes_all_discovery_agents(data):
    """agents.include must contain all 5 discovery agents."""
    expected_agents = [
        "dot-graph:discovery-prescan",
        "dot-graph:discovery-code-tracer",
        "dot-graph:discovery-behavior-observer",
        "dot-graph:discovery-integration-mapper",
        "dot-graph:discovery-synthesizer",
    ]
    for agent in expected_agents:
        assert agent in data["agents"]["include"], (
            f"agents.include must contain '{agent}', got: {data['agents']['include']}"
        )
```

### Step 2: Run the updated test to verify it fails

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_dot_discovery_behavior.py -v --tb=short`

Expected: The 3 new tests FAIL (no agents key in current YAML), existing tests PASS.

### Step 3: Update `behaviors/dot-discovery.yaml`

Replace the entire content of `behaviors/dot-discovery.yaml` with:

```yaml
bundle:
  name: dot-graph-discovery
  version: 0.1.0
  description: DOT/Graphviz codebase discovery pipeline

includes:
  - bundle: dot-graph:behaviors/dot-core

agents:
  include:
    - dot-graph:discovery-prescan
    - dot-graph:discovery-code-tracer
    - dot-graph:discovery-behavior-observer
    - dot-graph:discovery-integration-mapper
    - dot-graph:discovery-synthesizer

context:
  include:
    - dot-graph:context/discovery-awareness.md
```

### Step 4: Run test to verify it passes

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_dot_discovery_behavior.py -v --tb=short`

Expected: ALL PASS

### Step 5: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add behaviors/dot-discovery.yaml tests/test_dot_discovery_behavior.py && git commit -m "feat: declare 5 discovery agents in dot-discovery behavior"
```

---

## Task 5: Update `context/discovery-awareness.md` with real content

**Files:**
- Modify: `context/discovery-awareness.md`
- Modify: `tests/test_discovery_awareness.py`

### Step 1: Update the discovery awareness test

The current test at `tests/test_discovery_awareness.py` has a line count limit of `< 25`. The updated content will be slightly larger to properly describe the 5 agents and their roles. Update the line count test and add new tests.

Replace the entire content of `tests/test_discovery_awareness.py` with:

```python
"""
Tests for context/discovery-awareness.md existence and required content.
This context file describes the discovery pipeline capability and its agents.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DISCOVERY_AWARENESS_PATH = REPO_ROOT / "context" / "discovery-awareness.md"


def test_discovery_awareness_exists():
    """context/discovery-awareness.md must exist."""
    assert DISCOVERY_AWARENESS_PATH.exists(), (
        f"context/discovery-awareness.md not found at {DISCOVERY_AWARENESS_PATH}"
    )


def test_discovery_awareness_line_count_under_50():
    """File must be under 50 lines (concise context pointer)."""
    content = DISCOVERY_AWARENESS_PATH.read_text()
    lines = content.splitlines()
    assert len(lines) < 50, f"Expected < 50 lines, got {len(lines)}"


def test_discovery_awareness_has_heading():
    """File must start with a heading containing 'Discovery'."""
    content = DISCOVERY_AWARENESS_PATH.read_text()
    assert "# Discovery Pipeline" in content, (
        "Must contain heading '# Discovery Pipeline'"
    )


def test_discovery_awareness_has_when_to_use():
    """File must contain guidance on when to use discovery."""
    content = DISCOVERY_AWARENESS_PATH.read_text()
    assert "When to Use" in content, "Must contain 'When to Use' section"


def test_discovery_awareness_mentions_all_five_agents():
    """File must reference all 5 discovery agents."""
    content = DISCOVERY_AWARENESS_PATH.read_text()
    agents = [
        "discovery-prescan",
        "discovery-code-tracer",
        "discovery-behavior-observer",
        "discovery-integration-mapper",
        "discovery-synthesizer",
    ]
    for agent in agents:
        assert agent in content, f"Must mention {agent} agent"


def test_discovery_awareness_mentions_recipe():
    """File must reference the discovery pipeline recipe."""
    content = DISCOVERY_AWARENESS_PATH.read_text()
    assert "discovery-pipeline" in content, "Must mention discovery-pipeline recipe"


def test_discovery_awareness_has_delegation_guidance():
    """File must contain delegation guidance."""
    content = DISCOVERY_AWARENESS_PATH.read_text()
    assert any(word in content for word in ["delegate", "delegation", "Delegate"]), (
        "Must contain delegation guidance"
    )


def test_discovery_awareness_mentions_fidelity():
    """File must mention fidelity tiers."""
    content = DISCOVERY_AWARENESS_PATH.read_text()
    assert "fidelity" in content.lower() or "tier" in content.lower(), (
        "Must mention fidelity tiers"
    )
```

### Step 2: Run test to verify the line count test fails

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_awareness.py -v --tb=short`

Expected: `test_discovery_awareness_mentions_fidelity` FAIL (stub doesn't mention fidelity), and possibly the all-five-agents test passes since the stub already lists them. The line count test changes from <25 to <50.

### Step 3: Update `context/discovery-awareness.md`

Replace the entire content of `context/discovery-awareness.md` with:

```markdown
# Discovery Pipeline

You have access to a codebase discovery pipeline that systematically generates DOT graph representations of code architecture.

## When to Use Discovery

- **New codebase onboarding** — automatically map the architecture before diving in
- **Architecture documentation** — generate and maintain up-to-date architectural diagrams
- **Change impact analysis** — understand how changes propagate through the system
- **Multi-module understanding** — map how components integrate across boundaries

## Fidelity Tiers

Discovery runs at three fidelity tiers: `quick` (patch affected files only), `standard` (2 agents per topic with consensus), `deep` (3 agents per topic with full reconciliation). Default is `standard`.

## Available Capabilities

**Investigation Agents:**
- `discovery-prescan` — selects investigation topics from structural inventory
- `discovery-code-tracer` — HOW: traces execution paths with file:line evidence
- `discovery-behavior-observer` — WHAT: catalogs 10+ real instances, quantifies patterns
- `discovery-integration-mapper` — WHERE/WHY: maps cross-boundary connections
- `discovery-synthesizer` — reconciles multi-agent outputs into consensus DOT

**Recipes:** `discovery-pipeline` (full orchestrated pipeline with approval gates)

## Delegation

- **Codebase discovery** (generate architecture diagrams from code): delegate to the discovery pipeline recipe. It handles prescan, multi-agent investigation, consensus reconciliation, and hierarchical DOT assembly.
- **Do NOT** invoke discovery agents directly — the recipe controls agent dispatch based on fidelity tier and topic selection.
```

### Step 4: Run test to verify it passes

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_discovery_awareness.py -v --tb=short`

Expected: ALL PASS

### Step 5: Commit

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add context/discovery-awareness.md tests/test_discovery_awareness.py && git commit -m "feat: update discovery-awareness with agent descriptions and fidelity tiers"
```

---

## Task 6: Run full test suite and final verification

**Files:** None (verification only)

### Step 1: Run the full test suite

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/ -v --tb=short`

Expected: ALL PASS (should be ~770+ tests — the existing 722 plus the ~50 new tests from this phase)

### Step 2: Verify all new files exist

Run: `ls -la agents/discovery-*.md context/discovery-*-instructions.md`

Expected output should show:
- `agents/discovery-prescan.md`
- `agents/discovery-code-tracer.md`
- `agents/discovery-behavior-observer.md`
- `agents/discovery-integration-mapper.md`
- `agents/discovery-synthesizer.md`
- `context/discovery-prescan-instructions.md`
- `context/discovery-code-tracer-instructions.md`
- `context/discovery-behavior-observer-instructions.md`
- `context/discovery-integration-mapper-instructions.md`
- `context/discovery-synthesizer-instructions.md`

### Step 3: Verify the behavior YAML declares all agents

Run: `cat behaviors/dot-discovery.yaml`

Expected: Shows `agents:` section with all 5 `dot-graph:discovery-*` includes.

### Step 4: Verify no regressions in existing tests

Run: `cd /home/bkrabach/dev/amplifier-bundle-dot-graph && python -m pytest tests/test_dot_core_behavior.py tests/test_dot_graph_behavior.py tests/test_dot_author_agent.py tests/test_diagram_reviewer_agent.py -v --tb=short`

Expected: ALL PASS — existing functionality not broken.

### Step 5: Final commit if any cleanup needed

If all tests pass and no cleanup is needed, this step is a no-op. Otherwise:

```bash
cd /home/bkrabach/dev/amplifier-bundle-dot-graph && git add -A && git commit -m "fix: Phase C cleanup"
```
