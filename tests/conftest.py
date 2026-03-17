"""
Shared test helpers for the dot-graph bundle test suite.
"""

import yaml


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (frontmatter_dict, body)."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    yaml_block = content[3:end].strip()
    body = content[end + 3 :].strip()
    return yaml.safe_load(yaml_block), body
