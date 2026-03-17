"""
Tests for context/discovery-integration-mapper-instructions.md existence and required content.
Covers the Integration Mapping Methodology for the integration-mapper agent.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
INTEGRATION_MAPPER_INSTRUCTIONS_PATH = (
    REPO_ROOT / "context" / "discovery-integration-mapper-instructions.md"
)


def test_integration_mapper_instructions_exists():
    """context/discovery-integration-mapper-instructions.md must exist."""
    assert INTEGRATION_MAPPER_INSTRUCTIONS_PATH.exists(), (
        f"context/discovery-integration-mapper-instructions.md not found at "
        f"{INTEGRATION_MAPPER_INSTRUCTIONS_PATH}"
    )


def test_integration_mapper_instructions_line_count():
    """File must be between 80 and 180 lines (spec: 80-180 lines)."""
    content = INTEGRATION_MAPPER_INSTRUCTIONS_PATH.read_text()
    lines = content.splitlines()
    assert 80 <= len(lines) <= 180, f"Expected 80-180 lines, got {len(lines)}"


def test_integration_mapper_instructions_has_heading():
    """File must contain a heading about integration mapping."""
    content = INTEGRATION_MAPPER_INSTRUCTIONS_PATH.read_text()
    assert any(
        keyword in content
        for keyword in [
            "Integration Mapper",
            "integration mapper",
            "Integration Mapping",
            "integration mapping",
            "Integration-Mapper",
        ]
    ), "Must contain a heading about integration mapping"


def test_integration_mapper_instructions_mentions_boundaries():
    """File must discuss boundaries between components."""
    content = INTEGRATION_MAPPER_INSTRUCTIONS_PATH.read_text()
    assert "boundar" in content.lower(), "Must mention boundaries between components"


def test_integration_mapper_instructions_mentions_composition():
    """File must discuss composition effects."""
    content = INTEGRATION_MAPPER_INSTRUCTIONS_PATH.read_text()
    assert "composition" in content.lower(), "Must mention composition effects"


def test_integration_mapper_instructions_mentions_cross_boundary():
    """File must mention cross-boundary analysis."""
    content = INTEGRATION_MAPPER_INSTRUCTIONS_PATH.read_text()
    assert any(
        phrase in content.lower()
        for phrase in ["cross-boundary", "cross boundary", "crosses", "what crosses"]
    ), "Must mention cross-boundary or what crosses boundaries"


def test_integration_mapper_instructions_mentions_dot_output():
    """File must mention diagram.dot or DOT output."""
    content = INTEGRATION_MAPPER_INSTRUCTIONS_PATH.read_text()
    assert "diagram.dot" in content or (
        "DOT" in content and "diagram" in content.lower()
    ), "Must mention diagram.dot or DOT diagram output"


def test_integration_mapper_instructions_mentions_integration_map_md():
    """File must mention integration-map.md as a required output artifact."""
    content = INTEGRATION_MAPPER_INSTRUCTIONS_PATH.read_text()
    assert "integration-map.md" in content, (
        "Must mention integration-map.md as a required output artifact"
    )


def test_integration_mapper_instructions_mentions_evidence():
    """File must discuss evidence requirements for boundary analysis."""
    content = INTEGRATION_MAPPER_INSTRUCTIONS_PATH.read_text()
    assert "evidence" in content.lower(), "Must mention evidence requirements"
