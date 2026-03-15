"""Integration tests for the real DotGraphTool (Phase 2).

11 tests covering:
- Operation routing: validate, render, setup, analyze, unknown (6 tests including render)
- Input schema: setup operation in enum, options sub-properties (2 tests)
- Mount contract: real tool version, tool can actually validate (2 tests)

These tests verify that __init__.py routes operations to the real
validate, render, and setup_helper modules (Phase 2 implementation).
"""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

SIMPLE_DOT = "digraph G { a -> b }"
INVALID_DOT = "this is not dot content !!!###"


def _parse_output(result: Any) -> dict:
    """Assert result.output is a non-None string and parse it as JSON."""
    assert isinstance(result.output, str), (
        f"result.output must be a str, got {type(result.output)}: {result.output!r}"
    )
    return json.loads(result.output)


# ---------------------------------------------------------------------------
# Operation routing tests (6 tests)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_validate_operation_routes_correctly():
    """validate operation calls validate.validate_dot and returns ToolResult with valid key."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "validate", "dot_content": SIMPLE_DOT})

    assert result.success is True, "Valid DOT must return success=True"
    data = _parse_output(result)
    assert "valid" in data, "Output must contain 'valid' key from validate_dot()"
    assert data["valid"] is True, "Simple valid DOT must return valid=True"


@pytest.mark.asyncio
async def test_validate_invalid_dot_returns_failure():
    """validate operation returns success=False for invalid DOT content."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "validate", "dot_content": INVALID_DOT})

    assert result.success is False, "Invalid DOT must return success=False"
    data = _parse_output(result)
    assert "valid" in data, "Output must contain 'valid' key"
    assert data["valid"] is False, "Invalid DOT must have valid=False"


@pytest.mark.asyncio
async def test_validate_with_layer_option():
    """validate operation passes layers option through to validate_dot."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute(
        {
            "operation": "validate",
            "dot_content": SIMPLE_DOT,
            "options": {"layers": ["syntax"]},
        }
    )

    assert result.success is True
    data = _parse_output(result)
    assert "issues" in data, "Output must contain 'issues' key"
    # Only syntax layer ran — no structural issues should appear
    structural_issues = [i for i in data["issues"] if i["layer"] == "structural"]
    assert len(structural_issues) == 0, (
        f"syntax-only validation must produce no structural issues, got: {structural_issues}"
    )


@pytest.mark.asyncio
async def test_setup_operation_returns_environment():
    """setup operation calls check_environment() and returns environment info."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "setup"})

    assert result.success is True, "setup must return success=True"
    data = _parse_output(result)
    assert "graphviz" in data, "Environment result must include 'graphviz' key"
    assert "pydot" in data, "Environment result must include 'pydot' key"


@pytest.mark.asyncio
async def test_analyze_operation_returns_phase3_pending():
    """analyze operation returns success=False with Phase 3 pending message."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "analyze", "dot_content": SIMPLE_DOT})

    assert result.success is False, (
        "analyze must return success=False (Phase 3 pending)"
    )
    data = _parse_output(result)
    assert "error" in data, "analyze response must have 'error' key"
    error_msg = data["error"]
    assert "Phase 3" in error_msg or "not yet implemented" in error_msg, (
        f"analyze error must mention Phase 3 or 'not yet implemented', got: {error_msg!r}"
    )


@pytest.mark.asyncio
async def test_unknown_operation_returns_error():
    """Unknown operation returns success=False with error containing operation name and supported list."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    result = await tool.execute({"operation": "frobnicate"})

    assert result.success is False, "Unknown operation must return success=False"
    data = _parse_output(result)
    assert "error" in data, "Unknown operation response must have 'error' key"
    assert "frobnicate" in data["error"], (
        f"Error must mention the unknown operation name, got: {data['error']!r}"
    )
    assert "supported" in data, (
        "Unknown operation response must include 'supported' list"
    )
    assert isinstance(data["supported"], list), "'supported' must be a list"


@pytest.mark.asyncio
async def test_render_operation_routes_correctly():
    """render operation calls render.render_dot and returns ToolResult."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    mock_render_result = {
        "success": True,
        "output_path": "/tmp/test_output.svg",
        "format": "svg",
        "engine": "dot",
        "size_bytes": 1234,
    }
    with patch(
        "amplifier_module_tool_dot_graph.render.render_dot",
        return_value=mock_render_result,
    ):
        tool = DotGraphTool()
        result = await tool.execute({"operation": "render", "dot_content": SIMPLE_DOT})

    assert result.success is True, "Mocked render must return success=True"
    data = _parse_output(result)
    assert data["output_path"] == "/tmp/test_output.svg", (
        f"Render output must include output_path, got: {data}"
    )


# ---------------------------------------------------------------------------
# Input schema tests (2 tests)
# ---------------------------------------------------------------------------


def test_input_schema_includes_setup_operation():
    """input_schema operation enum includes all 4 operations: validate, render, setup, analyze."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    schema = tool.input_schema

    op_enum = schema["properties"]["operation"]["enum"]
    assert "validate" in op_enum, "Schema enum must include 'validate'"
    assert "render" in op_enum, "Schema enum must include 'render'"
    assert "setup" in op_enum, "Schema enum must include 'setup'"
    assert "analyze" in op_enum, "Schema enum must include 'analyze'"


def test_input_schema_documents_options():
    """input_schema options property has sub-properties: format, engine, layers."""
    from amplifier_module_tool_dot_graph import DotGraphTool

    tool = DotGraphTool()
    schema = tool.input_schema

    assert "options" in schema["properties"], "Schema must include 'options' property"
    options = schema["properties"]["options"]

    assert "properties" in options, (
        "options must have 'properties' key (sub-schema with format, engine, layers)"
    )
    option_props = options["properties"]

    assert "format" in option_props, "options.properties must include 'format'"
    assert "engine" in option_props, "options.properties must include 'engine'"
    assert "layers" in option_props, "options.properties must include 'layers'"


# ---------------------------------------------------------------------------
# Mount contract tests (2 tests)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mount_registers_real_tool():
    """mount() returns version 0.2.0, indicating the real implementation (not 0.1.0 placeholder)."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    result = await mount(coordinator)

    assert result["version"] == "0.2.0", (
        f"Expected version 0.2.0 (real implementation), got: {result['version']!r}"
    )
    assert result["name"] == "tool-dot-graph", (
        f"Expected name 'tool-dot-graph', got: {result['name']!r}"
    )
    assert "dot_graph" in result["provides"], (
        f"Expected 'dot_graph' in provides, got: {result['provides']}"
    )


@pytest.mark.asyncio
async def test_mounted_tool_can_validate():
    """Tool registered by mount() can actually validate DOT content end-to-end."""
    from amplifier_module_tool_dot_graph import mount

    coordinator = MagicMock()
    coordinator.mount = AsyncMock()

    await mount(coordinator)

    args, _ = coordinator.mount.call_args
    tool = args[1]  # second positional arg is the tool instance

    result = await tool.execute({"operation": "validate", "dot_content": SIMPLE_DOT})

    assert result.success is True, (
        "Mounted tool must validate simple DOT as success=True"
    )
    data = _parse_output(result)
    assert data["valid"] is True, (
        f"Mounted tool validate must return valid=True for simple DOT, got: {data}"
    )
