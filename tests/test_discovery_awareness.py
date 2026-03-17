"""
Tests for context/discovery-awareness.md existence and required content.
This is a thin context pointer for the discovery pipeline capability.
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
    """File must be under 50 lines."""
    content = DISCOVERY_AWARENESS_PATH.read_text()
    lines = content.splitlines()
    assert len(lines) < 50, f"Expected < 50 lines, got {len(lines)}"


def test_discovery_awareness_has_heading():
    """File must contain '# Discovery Pipeline' heading."""
    content = DISCOVERY_AWARENESS_PATH.read_text()
    assert "# Discovery Pipeline" in content, (
        "Must contain heading '# Discovery Pipeline'"
    )


def test_discovery_awareness_has_when_to_use():
    """File must contain a 'When to Use' section."""
    content = DISCOVERY_AWARENESS_PATH.read_text()
    assert "When to Use" in content, "Must contain 'When to Use' section"


def test_discovery_awareness_mentions_all_five_agents():
    """File must reference all 5 discovery agents."""
    content = DISCOVERY_AWARENESS_PATH.read_text()
    assert "discovery-prescan" in content, "Must mention discovery-prescan agent"
    assert "discovery-code-tracer" in content, (
        "Must mention discovery-code-tracer agent"
    )
    assert "discovery-behavior-observer" in content, (
        "Must mention discovery-behavior-observer agent"
    )
    assert "discovery-integration-mapper" in content, (
        "Must mention discovery-integration-mapper agent"
    )
    assert "discovery-synthesizer" in content, (
        "Must mention discovery-synthesizer agent"
    )


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
    assert any(word in content for word in ["fidelity", "tier", "Fidelity", "Tier"]), (
        "Must mention fidelity or tier"
    )
