"""Tests for render.py — graphviz CLI rendering wrapper."""

import os
import shutil
import tempfile
from unittest.mock import patch

import pytest

# Detect graphviz availability once for skip markers.
_GRAPHVIZ_INSTALLED = shutil.which("dot") is not None

skip_if_no_graphviz = pytest.mark.skipif(
    not _GRAPHVIZ_INSTALLED,
    reason="graphviz CLI not installed",
)

# Minimal valid DOT content for rendering tests.
_SIMPLE_DOT = "digraph G { A -> B; }"


# ---------------------------------------------------------------------------
# Successful rendering (requires graphviz)
# ---------------------------------------------------------------------------


@skip_if_no_graphviz
def test_render_svg_default():
    """render_dot() with default args produces SVG output file."""
    from amplifier_module_tool_dot_graph.render import render_dot

    result = render_dot(_SIMPLE_DOT)

    assert result["success"] is True
    assert result["output_path"].endswith(".svg")
    assert os.path.exists(result["output_path"])
    assert result["size_bytes"] > 0

    # Cleanup
    os.unlink(result["output_path"])


@skip_if_no_graphviz
def test_render_png():
    """render_dot() with format='png' produces a PNG output file."""
    from amplifier_module_tool_dot_graph.render import render_dot

    result = render_dot(_SIMPLE_DOT, output_format="png")

    assert result["success"] is True
    assert result["output_path"].endswith(".png")
    assert os.path.exists(result["output_path"])
    assert result["size_bytes"] > 0

    # Cleanup
    os.unlink(result["output_path"])


@skip_if_no_graphviz
def test_render_with_neato_engine():
    """render_dot() with engine='neato' uses neato for layout."""
    from amplifier_module_tool_dot_graph.render import render_dot

    result = render_dot(_SIMPLE_DOT, engine="neato")

    assert result["success"] is True
    assert result["engine"] == "neato"
    assert os.path.exists(result["output_path"])

    # Cleanup
    os.unlink(result["output_path"])


@skip_if_no_graphviz
def test_render_custom_output_path():
    """render_dot() with explicit output_path writes to that path."""
    from amplifier_module_tool_dot_graph.render import render_dot

    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as f:
        custom_path = f.name

    try:
        result = render_dot(_SIMPLE_DOT, output_path=custom_path)

        assert result["success"] is True
        assert result["output_path"] == custom_path
        assert os.path.exists(custom_path)
        assert result["size_bytes"] > 0
    finally:
        if os.path.exists(custom_path):
            os.unlink(custom_path)


# ---------------------------------------------------------------------------
# Input validation (no graphviz needed)
# ---------------------------------------------------------------------------


def test_unsupported_format_returns_error():
    """render_dot() with unsupported format returns error dict immediately."""
    from amplifier_module_tool_dot_graph.render import render_dot

    result = render_dot(_SIMPLE_DOT, output_format="gif")

    assert result["success"] is False
    assert "error" in result
    assert "Unsupported format" in result["error"]


def test_unsupported_engine_returns_error():
    """render_dot() with unsupported engine returns error dict immediately."""
    from amplifier_module_tool_dot_graph.render import render_dot

    result = render_dot(_SIMPLE_DOT, engine="invalid_engine")

    assert result["success"] is False
    assert "error" in result
    assert "Unsupported engine" in result["error"]


# ---------------------------------------------------------------------------
# Graceful degradation
# ---------------------------------------------------------------------------


def test_no_graphviz_returns_install_hint():
    """When graphviz not installed (mocked), result contains install hint."""
    from amplifier_module_tool_dot_graph.render import render_dot

    mock_env = {
        "graphviz": {
            "installed": False,
            "version": None,
            "engines": [],
            "install_hint": "Install Graphviz via package manager",
        },
        "pydot": {"installed": True, "version": "3.0.0"},
        "networkx": {"installed": True, "version": "3.0.0"},
    }

    with patch(
        "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
        return_value=mock_env,
    ):
        result = render_dot(_SIMPLE_DOT)

    assert result["success"] is False
    assert "error" in result
    assert "Graphviz not installed" in result["error"]
    assert "Install Graphviz" in result["error"]


def test_engine_not_available_returns_error():
    """When engine not on PATH (mocked), result includes available engines."""
    from amplifier_module_tool_dot_graph.render import render_dot

    mock_env = {
        "graphviz": {
            "installed": True,
            "version": "2.43.0",
            "engines": ["dot", "fdp"],  # neato not available
        },
        "pydot": {"installed": True, "version": "3.0.0"},
        "networkx": {"installed": True, "version": "3.0.0"},
    }

    with patch(
        "amplifier_module_tool_dot_graph.render.setup_helper.check_environment",
        return_value=mock_env,
    ):
        result = render_dot(_SIMPLE_DOT, engine="neato")

    assert result["success"] is False
    assert "error" in result
    assert "Engine not found on PATH" in result["error"]
    assert "dot" in result["error"]  # available engines listed


# ---------------------------------------------------------------------------
# Result structure
# ---------------------------------------------------------------------------


@skip_if_no_graphviz
def test_success_result_has_required_keys():
    """Successful render result contains all required keys."""
    from amplifier_module_tool_dot_graph.render import render_dot

    result = render_dot(_SIMPLE_DOT)

    assert result["success"] is True
    assert "output_path" in result
    assert "format" in result
    assert "engine" in result
    assert "size_bytes" in result

    # Values are sensible types
    assert isinstance(result["output_path"], str)
    assert isinstance(result["format"], str)
    assert isinstance(result["engine"], str)
    assert isinstance(result["size_bytes"], int)

    # Cleanup
    os.unlink(result["output_path"])


def test_error_result_has_required_keys():
    """Error result always contains 'success' (False) and 'error' keys."""
    from amplifier_module_tool_dot_graph.render import render_dot

    # Use unsupported format to trigger an error without needing graphviz.
    result = render_dot(_SIMPLE_DOT, output_format="bmp")

    assert "success" in result
    assert result["success"] is False
    assert "error" in result
    assert isinstance(result["error"], str)
    assert len(result["error"]) > 0
