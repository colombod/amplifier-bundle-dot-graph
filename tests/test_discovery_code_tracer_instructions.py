"""
Tests for context/discovery-code-tracer-instructions.md existence and required content.
Covers the Code Tracing Methodology for the code-tracer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
CODE_TRACER_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-code-tracer-instructions.md"
)


def test_code_tracer_instructions_exists():
    """context/discovery-code-tracer-instructions.md must exist."""
    assert CODE_TRACER_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-code-tracer-instructions.md not found at {CODE_TRACER_INSTRUCTIONS_PATH}"
    )


def test_code_tracer_instructions_line_count():
    """File must be between 80 and 180 lines (spec: 80-180 lines)."""
    content = CODE_TRACER_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80-180 lines, got {len(lines)}"


def test_code_tracer_instructions_has_heading():
    """File must contain a heading about code tracing."""
    content = CODE_TRACER_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in ["Code Tracer", "code tracer", "Code Tracing", "code tracing"]
    ), "Must contain a heading about code tracing"


def test_code_tracer_instructions_mentions_lsp():
    """File must mention LSP (Language Server Protocol)."""
    content = CODE_TRACER_INSTRUCTIONS_PATH.read_text()
    assert "LSP" in content or "Language Server" in content, (
        "Must mention LSP (Language Server Protocol)"
    )


def test_code_tracer_instructions_mentions_lsp_operations():
    """File must mention at least 2 of the required LSP operations."""
    content = CODE_TRACER_INSTRUCTIONS_PATH.read_text()
    lsp_operations = [
        "goToDefinition",
        "findReferences",
        "incomingCalls",
        "outgoingCalls",
        "hover",
    ]
    found = [op for op in lsp_operations if op in content]
    assert len(found) >= 2, f"Must mention at least 2 LSP operations, found: {found}"


def test_code_tracer_instructions_mentions_file_line_evidence():
    """File must mention file:line evidence format."""
    content = CODE_TRACER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content for phrase in ["file:line", "file:42", ":line", "file.py:"]
    ), "Must mention file:line evidence format"


def test_code_tracer_instructions_mentions_dot_output():
    """File must mention diagram.dot or DOT output."""
    content = CODE_TRACER_INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content or (
        "DOT" in content and "diagram" in content.lower()
    ), "Must mention diagram.dot or DOT diagram output"


def test_code_tracer_instructions_mentions_findings_md():
    """File must mention findings.md output artifact."""
    content = CODE_TRACER_INSTRUCTIONS_PATH.read_text()
    assert "findings.md" in content, "Must mention findings.md as an output artifact"


def test_code_tracer_instructions_mentions_execution_paths():
    """File must discuss execution paths or call chains."""
    content = CODE_TRACER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in ["execution path", "call chain", "call graph", "execution flow"]
    ), "Must mention execution paths or call chains"
