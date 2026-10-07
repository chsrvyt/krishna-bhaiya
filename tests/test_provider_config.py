import os
from pathlib import Path
from agent.llm import LLM
from agent.llm import _json_payload
from agent.tools import RunLogger


def test_openrouter_uses_configured_openai_compatible_base(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_PROVIDER", "openrouter")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    monkeypatch.setenv("OPENROUTER_MODEL", "openai/gpt-4.1-mini")
    monkeypatch.setenv("OPENROUTER_MAX_TOKENS", "1000")
    llm = LLM(RunLogger(tmp_path))
    assert llm.provider == "openrouter"
    assert llm.model == "openai/gpt-4.1-mini"
    assert llm.max_tokens == 1000
    assert str(llm.client.base_url).rstrip("/") == "https://openrouter.ai/api/v1"


def test_fenced_json_is_normalized_before_schema_validation():
    assert _json_payload("```json\n{\"ok\": true}\n```") == '{"ok": true}'
