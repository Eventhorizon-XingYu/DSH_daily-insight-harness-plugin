"""Mocked tests for the DeepSeek article generation boundary."""
from datetime import date
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from daily_insight.generator import ArticleGenerator
from daily_insight.searcher import SearchResult
from daily_insight.video_finder import VideoResult


def _response(content, usage=None):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
        usage=usage,
    )


def _generator(client, tmp_path):
    fake_openai = ModuleType("openai")
    fake_openai.OpenAI = Mock(return_value=client)
    prompt = tmp_path / "system.md"
    prompt.write_text("system instructions", encoding="utf-8")
    with patch.dict("sys.modules", {"openai": fake_openai}):
        generator = ArticleGenerator("secret", "https://api.example/v1", "model-x", prompt_path=prompt)
    return generator, fake_openai


def test_generator_sends_materials_and_returns_usage(tmp_path):
    client = Mock()
    client.chat.completions.create.return_value = _response(
        "  # Article\n", SimpleNamespace(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    )
    generator, openai_module = _generator(client, tmp_path)
    article, usage = generator.generate(
        [SearchResult("Title", "https://example.test", "Summary", "example.test")],
        [VideoResult("Video", "YouTube", "https://youtube.com/watch?v=1", "")],
        date(2026, 1, 2),
    )
    assert article == "# Article"
    assert usage == {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
    openai_module.OpenAI.assert_called_once_with(api_key="secret", base_url="https://api.example/v1", timeout=10.0)
    request = client.chat.completions.create.call_args.kwargs
    assert request["model"] == "model-x"
    assert request["temperature"] == pytest.approx(0.7)
    assert request["max_tokens"] == 4096
    assert request["messages"][0] == {"role": "system", "content": "system instructions"}
    assert "当前日期：2026-01-02" in request["messages"][1]["content"]
    assert "https://youtube.com/watch?v=1" in request["messages"][1]["content"]


def test_generator_retries_empty_response_then_succeeds(tmp_path):
    client = Mock()
    client.chat.completions.create.side_effect = [_response(""), _response("usable")]
    generator, _ = _generator(client, tmp_path)
    article, usage = generator.generate([], [])
    assert article == "usable"
    assert usage == {}
    assert client.chat.completions.create.call_count == 2


def test_generator_raises_after_two_empty_responses(tmp_path):
    client = Mock()
    client.chat.completions.create.side_effect = [_response(None), _response("  ")]
    generator, _ = _generator(client, tmp_path)
    with pytest.raises(RuntimeError, match="空文章"):
        generator.generate([], [])
    assert client.chat.completions.create.call_count == 2


def test_generator_handles_partial_usage_object(tmp_path):
    client = Mock()
    client.chat.completions.create.return_value = _response(
        "ok", SimpleNamespace(total_tokens=7)
    )
    generator, _ = _generator(client, tmp_path)
    _, usage = generator.generate([], [])
    assert usage == {"total_tokens": 7}
