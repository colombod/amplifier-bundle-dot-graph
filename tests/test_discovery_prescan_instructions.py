"""
Tests for context/discovery-prescan-instructions.md existence and required content.
Covers the Topic Selection Methodology for the prescan agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PRESCAN_INSTRUCTIONS_PATH = REPO_ROOT / "context" / "discovery-prescan-instructions.md"


def test_prescan_instructions_exists():
    """context/discovery-prescan-instructions.md must exist."""
    assert PRESCAN_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-prescan-instructions.md not found at {PRESCAN_INSTRUCTIONS_PATH}"
    )


def test_prescan_instructions_line_count():
    """File must be between 60 and 150 lines (spec: 60-150 lines)."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 60 <= len(lines) <= 150, f"Expected 60-150 lines, got {len(lines)}"


def test_prescan_instructions_has_heading():
    """File must contain a heading about prescan/topic selection."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in ["prescan", "Prescan", "Topic Selection", "topic selection"]
    ), "Must contain a heading about prescan or topic selection"


def test_prescan_instructions_has_topic_selection_criteria():
    """File must contain a topic selection criteria table with required signals."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    # Must mention the required signals from the spec
    required_signals = [
        "entry point",
        "config",
        "test",
    ]
    for signal in required_signals:
        assert signal.lower() in content.lower(), (
            f"Must contain topic selection signal: '{signal}'"
        )
    # Must also mention the 'What Is NOT a Good Topic' section
    assert any(
        phrase in content.lower()
        for phrase in ["not a good topic", "not good topic", "what is not", "avoid"]
    ), "Must contain 'What Is NOT a Good Topic' guidance"


def test_prescan_instructions_has_fidelity_guidance():
    """File must contain fidelity tier guidance table."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    assert "fidelity" in content.lower(), "Must mention fidelity tiers"
    # Must mention both standard and deep tiers
    assert "standard" in content.lower(), "Must mention standard fidelity tier"
    assert "deep" in content.lower(), "Must mention deep fidelity tier"


def test_prescan_instructions_has_json_output_format():
    """File must contain structured JSON output format with schema."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    assert "json" in content.lower(), "Must contain JSON output format"
    # Must contain required schema fields
    required_fields = ["topics", "name", "description", "directories"]
    for field in required_fields:
        assert field in content, f"JSON schema must include field: '{field}'"


def test_prescan_instructions_mentions_structural_inventory():
    """File must reference 'structural inventory' as input."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    assert "structural inventory" in content.lower(), (
        "Must reference 'structural inventory' as input"
    )


def test_prescan_instructions_has_topic_count_range():
    """File must specify 3-7 topic range."""
    content = PRESCAN_INSTRUCTIONS_PATH.read_text()
    assert any(phrase in content for phrase in ["3-7", "3–7", "3 to 7", "3 and 7"]), (
        "Must specify '3-7' or '3–7' topic range"
    )
