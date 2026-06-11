"""Tests for the optional ABACUS-agent-tools backend integration."""

from abacus_lsp.agent import CAPABILITIES, get_agent_tools_status


def test_agent_tools_status_returns_dict():
    status = get_agent_tools_status()
    assert isinstance(status, dict)
    assert "available" in status
    assert isinstance(status["available"], bool)


def test_agent_tools_status_has_backend_key():
    status = get_agent_tools_status()
    assert "backend" in status
    # backend is either the string name or None when unavailable
    assert status["backend"] is None or isinstance(status["backend"], str)


def test_capabilities_includes_agent_tools_backend():
    assert "agent_tools_backend" in CAPABILITIES
    entry = CAPABILITIES["agent_tools_backend"]
    assert entry["optional"] is True
    assert "description" in entry
