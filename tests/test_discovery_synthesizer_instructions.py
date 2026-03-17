"""
Tests for context/discovery-synthesizer-instructions.md existence and required content.
Covers the Reconciliation Methodology for the synthesizer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SYNTHESIZER_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-synthesizer-instructions.md"
)


def test_synthesizer_instructions_exists():
    """context/discovery-synthesizer-instructions.md must exist."""
    assert SYNTHESIZER_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-synthesizer-instructions.md not found at "
        f"{SYNTHESIZER_INSTRUCTIONS_PATH}"
    )


def test_synthesizer_instructions_line_count():
    """File must be between 100 and 220 lines (spec: 100-220 lines)."""
    content = SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 100 <= len(lines) <= 220, f"Expected 100-220 lines, got {len(lines)}"


def test_synthesizer_instructions_has_heading():
    """File must contain a heading about reconciliation or synthesis."""
    content = SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in [
            "Synthesizer",
            "synthesizer",
            "Reconciliation",
            "reconciliation",
            "Synthesis",
            "synthesis",
        ]
    ), "Must contain a heading about reconciliation or synthesis"


def test_synthesizer_instructions_mentions_reconciliation():
    """File must discuss the reconciliation process."""
    content = SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert "reconcil" in content.lower(), "Must discuss the reconciliation process"


def test_synthesizer_instructions_mentions_phases():
    """File must describe phases (e.g., Phase 1, Phase 2 etc.)."""
    content = SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content
        for phrase in ["Phase 1", "Phase 2", "Phase 3", "Phase 4", "phase 1", "phase 2"]
    ), "Must describe phases of the reconciliation process"


def test_synthesizer_instructions_mentions_discrepancy_tracking():
    """File must mention discrepancy tracking with D-0x ID format."""
    content = SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content
        for phrase in ["D-01", "D-02", "D-03", "D-0x", "D-0", "discrepancy"]
    ) and any(fmt in content for fmt in ["D-01", "D-02", "D-0x"]), (
        "Must mention discrepancy tracking with D-0x ID format"
    )


def test_synthesizer_instructions_mentions_no_fiat():
    """File must prohibit reconciliation by fiat."""
    content = SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in ["never reconcile by fiat", "reconcile by fiat", "by fiat"]
    ), "Must prohibit reconciliation by fiat"


def test_synthesizer_instructions_mentions_consensus_dot():
    """File must mention producing a consensus DOT diagram."""
    content = SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content or (
        "DOT" in content
        and ("consensus" in content.lower() or "diagram" in content.lower())
    ), "Must mention producing a consensus DOT diagram"


def test_synthesizer_instructions_mentions_bounded_output():
    """File must specify output bounds (250 lines or 80 nodes)."""
    content = SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert "250" in content or "80" in content, (
        "Must specify output bounds (250 lines max or 80 nodes max)"
    )


def test_synthesizer_instructions_mentions_quality_gate():
    """File must mention quality gate or validation."""
    content = SYNTHESIZER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in ["quality gate", "validate", "validation", "dot_graph"]
    ), "Must mention quality gate or validation loop"
