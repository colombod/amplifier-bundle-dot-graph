"""
Tests for context/discovery-behavior-observer-instructions.md existence and required content.
Covers the Behavioral Observation Methodology for the behavior-observer agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-behavior-observer-instructions.md"
)


def test_behavior_observer_instructions_exists():
    """context/discovery-behavior-observer-instructions.md must exist."""
    assert BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-behavior-observer-instructions.md not found at "
        f"{BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH}"
    )


def test_behavior_observer_instructions_line_count():
    """File must be between 80 and 180 lines (spec: 80-180 lines)."""
    content = BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80-180 lines, got {len(lines)}"


def test_behavior_observer_instructions_has_heading():
    """File must contain a heading about behavioral observation."""
    content = BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in [
            "Behavior Observer",
            "behavior observer",
            "Behavioral Observation",
            "behavioral observation",
            "Behavior-Observer",
        ]
    ), "Must contain a heading about behavioral observation"


def test_behavior_observer_instructions_mentions_10_instances():
    """File must mention the 10-instance minimum rule."""
    content = BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content
        for phrase in [
            "10 instance",
            "10-instance",
            "ten instance",
            "minimum 10",
            "at least 10",
        ]
    ), "Must mention the 10-instance minimum rule"


def test_behavior_observer_instructions_mentions_catalog():
    """File must discuss catalog building methodology."""
    content = BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH.read_text()
    assert "catalog" in content.lower(), "Must mention building a catalog"


def test_behavior_observer_instructions_mentions_quantification():
    """File must discuss quantification (counts, percentages)."""
    content = BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in ["quantif", "counts", "percentages", "percentage", "count and"]
    ), "Must mention quantification with counts and percentages"


def test_behavior_observer_instructions_mentions_patterns():
    """File must discuss pattern identification."""
    content = BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH.read_text()
    assert "pattern" in content.lower(), "Must mention identifying patterns"


def test_behavior_observer_instructions_mentions_dot_output():
    """File must mention diagram.dot or DOT output."""
    content = BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content or (
        "DOT" in content and "diagram" in content.lower()
    ), "Must mention diagram.dot or DOT diagram output"


def test_behavior_observer_instructions_mentions_catalog_md_output():
    """File must mention catalog.md as a required output artifact."""
    content = BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH.read_text()
    assert "catalog.md" in content, (
        "Must mention catalog.md as a required output artifact"
    )


def test_behavior_observer_instructions_mentions_patterns_md_output():
    """File must mention patterns.md as a required output artifact."""
    content = BEHAVIOR_OBSERVER_INSTRUCTIONS_PATH.read_text()
    assert "patterns.md" in content, (
        "Must mention patterns.md as a required output artifact"
    )
