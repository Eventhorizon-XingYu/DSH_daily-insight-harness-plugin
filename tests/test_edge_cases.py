"""Additional edge-case and failure-path coverage."""
from unittest.mock import Mock, patch

import pytest

from daily_insight.config import ConfigError, init_config, load_config
from daily_insight.searcher import search_topics
from daily_insight.utils import retry, slugify
from daily_insight.video_finder import VideoFinder


def test_search_skips_provider_error_and_continues():
    provider = Mock()
    provider.search.side_effect = [RuntimeError("temporary"), [{"link": "https://example.test/ok", "title": "OK", "snippet": "summary"}]]
    results = search_topics(["AI"], provider, max_keywords=2)
    assert [result.url for result in results] == ["https://example.test/ok"]
    assert provider.search.call_count == 2


def test_search_maps_link_and_domain_and_ignores_empty_urls():
    provider = Mock()
    provider.search.return_value = [
        {"title": "missing", "body": "no url"},
        {"title": "valid", "link": " https://news.example.test/story ", "snippet": "brief"},
    ]
    result = search_topics(["topic"], provider, max_keywords=1)[0]
    assert result.title == "valid"
    assert result.url == "https://news.example.test/story"
    assert result.domain == "news.example.test"
    assert result.snippet == "brief"


def test_video_finder_normalizes_platform_and_prioritizes_configured_platforms():
    raw = [
        {"title": "other", "content": "https://example.test/v"},
        {"title": "youtube", "content": "https://youtube.com/watch?v=1", "description": "desc"},
    ]
    with patch("duckduckgo_search.DDGS") as ddgs:
        ddgs.return_value.__enter__.return_value.videos.return_value = raw
        videos = VideoFinder(platforms=["youtube"], max_videos=1).find("AI")
    assert len(videos) == 1
    assert videos[0].platform == "YouTube"
    assert videos[0].url.startswith("https://youtube.com/")


def test_video_finder_returns_empty_when_provider_raises():
    with patch("duckduckgo_search.DDGS", side_effect=RuntimeError("offline")):
        assert VideoFinder().find("AI") == []


def test_load_config_requires_search_provider_key(tmp_path):
    path = init_config(tmp_path / "config.yaml")
    text = path.read_text(encoding="utf-8").replace('engine: "duckduckgo"', 'engine: "tavily"')
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match="TAVILY_KEY"):
        load_config(path, {"DEEPSEEK_API_KEY": "secret"})


def test_load_config_rejects_invalid_time(tmp_path):
    path = init_config(tmp_path / "config.yaml")
    text = path.read_text(encoding="utf-8").replace('time: "08:00"', 'time: "25:00"')
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ConfigError, match="HH:MM"):
        load_config(path, {"DEEPSEEK_API_KEY": "secret"})


def test_retry_retries_then_returns():
    calls = []

    @retry(attempts=3, delay=0)
    def flaky():
        calls.append(1)
        if len(calls) < 3:
            raise ValueError("not yet")
        return "ok"

    assert flaky() == "ok"
    assert len(calls) == 3


def test_retry_preserves_final_exception():
    @retry(attempts=2, delay=0)
    def always_fails():
        raise RuntimeError("final")

    with pytest.raises(RuntimeError, match="final"):
        always_fails()


def test_slugify_handles_unicode_and_empty_values():
    assert slugify("AI Agent!") == "ai-agent"
    assert slugify("中文主题") == "topic"
    assert slugify("   ") == "topic"
