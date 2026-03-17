"""
Tests for agents/discovery-behavior-observer.md existence and required content.
TDD: This test is written BEFORE the agents/discovery-behavior-observer.md file is created.
"""

from pathlib import Path

from conftest import _parse_frontmatter

REPO_ROOT = Path(__file__).parent.parent
BEHAVIOR_OBSERVER_AGENT_PATH = REPO_ROOT / "agents" / "discovery-behavior-observer.md"


# --- File existence and frontmatter ---


def test_discovery_behavior_observer_agent_exists():
    """agents/discovery-behavior-observer.md must exist."""
    assert BEHAVIOR_OBSERVER_AGENT_PATH.exists(), (
        f"agents/discovery-behavior-observer.md not found at {BEHAVIOR_OBSERVER_AGENT_PATH}"
    )


def test_discovery_behavior_observer_has_yaml_frontmatter():
    """File must start with YAML frontmatter delimited by ---."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert content.startswith("---"), (
        "agents/discovery-behavior-observer.md must start with YAML frontmatter (---)"
    )
    assert content.count("---") >= 2, (
        "agents/discovery-behavior-observer.md must have closing --- for frontmatter"
    )


def test_discovery_behavior_observer_frontmatter_meta_name():
    """Frontmatter must contain meta.name = 'discovery-behavior-observer'."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "meta" in frontmatter, "Frontmatter must have 'meta' key"
    assert frontmatter["meta"]["name"] == "discovery-behavior-observer", (
        f"meta.name must be 'discovery-behavior-observer', got: {frontmatter['meta'].get('name')}"
    )


def test_discovery_behavior_observer_frontmatter_has_description():
    """Frontmatter must have meta.description (non-empty)."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "description" in frontmatter["meta"], (
        "Frontmatter meta must have 'description' key"
    )
    assert frontmatter["meta"]["description"], "meta.description must not be empty"


def test_discovery_behavior_observer_description_has_two_examples():
    """Description must contain at least 2 <example> blocks."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert content.count("<example>") >= 2, (
        f"Description must contain at least 2 <example> blocks, found {content.count('<example>')}"
    )


def test_discovery_behavior_observer_frontmatter_model_role_research():
    """Frontmatter must have model_role: research."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "model_role" in frontmatter, "Frontmatter must have 'model_role' key"
    assert frontmatter["model_role"] == "research", (
        f"model_role must be 'research', got: {frontmatter['model_role']}"
    )


def test_discovery_behavior_observer_frontmatter_has_tool_dot_graph():
    """Frontmatter must declare tool-dot-graph in tools."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    frontmatter, _ = _parse_frontmatter(content)
    assert "tools" in frontmatter, "Frontmatter must have 'tools' key"
    tool_names = [
        t.get("module", "") for t in frontmatter["tools"] if isinstance(t, dict)
    ]
    assert "tool-dot-graph" in tool_names, (
        f"tools must include 'tool-dot-graph', got: {tool_names}"
    )


# --- Markdown body structure ---


def test_discovery_behavior_observer_body_has_main_heading():
    """Markdown body must contain a heading about behavior observation."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    _, body = _parse_frontmatter(content)
    assert (
        "Behavior Observer" in body or "behavior-observer" in body or "Behavior" in body
    ), "Body must contain a heading about behavior observation"


def test_discovery_behavior_observer_body_identifies_as_what_agent():
    """Body must identify as the WHAT agent."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "WHAT" in content, "Body must identify as the WHAT agent"


def test_discovery_behavior_observer_body_mentions_fresh_context():
    """Body must mention fresh context / zero prior context mandate."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert (
        "fresh context" in content.lower()
        or "zero prior" in content.lower()
        or "fresh" in content.lower()
    ), "Body must mention fresh context / zero prior context mandate"


def test_discovery_behavior_observer_body_mentions_ten_plus_instances():
    """Body must mention examining 10+ instances."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "10" in content or "ten" in content.lower(), (
        "Body must mention examining 10+ instances"
    )


def test_discovery_behavior_observer_references_instruction_file():
    """Body must @mention discovery-behavior-observer-instructions context file."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "discovery-behavior-observer-instructions" in content, (
        "Body must reference @dot-graph:context/discovery-behavior-observer-instructions"
    )


def test_discovery_behavior_observer_requires_diagram_dot_output():
    """Body must require diagram.dot as an output artifact."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "diagram.dot" in content, (
        "Body must require diagram.dot as an output artifact"
    )


def test_discovery_behavior_observer_has_required_artifacts_section():
    """Body must contain 'Required Artifacts' section."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "Required Artifacts" in content, (
        "Body must contain 'Required Artifacts' section"
    )


def test_discovery_behavior_observer_ends_with_common_agent_base():
    """File must end with @foundation:context/shared/common-agent-base.md."""
    content = BEHAVIOR_OBSERVER_AGENT_PATH.read_text()
    assert "@foundation:context/shared/common-agent-base.md" in content, (
        "File must reference @foundation:context/shared/common-agent-base.md"
    )
    last_100 = content.strip()[-100:]
    assert "common-agent-base.md" in last_100, (
        "File must END with @foundation:context/shared/common-agent-base.md"
    )
