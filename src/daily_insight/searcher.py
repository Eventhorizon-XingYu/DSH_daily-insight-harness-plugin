"""Web search strategies and normalized result collection."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from urllib.parse import urlparse

from .utils import retry


@dataclass
class SearchResult:
    """A normalized web search result."""
    title: str; url: str; snippet: str; domain: str
class SearchStrategy(Protocol):
    """Interface implemented by search providers."""
    def search(self, keyword: str, max_results: int) -> list[dict[str, Any]]: ...
class DuckDuckGoStrategy:
    """DuckDuckGo provider loaded lazily to keep imports optional."""
    @retry(3)
    def search(self, keyword: str, max_results: int) -> list[dict[str, Any]]:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs: return list(ddgs.text(keyword, max_results=max_results))
class SerpApiStrategy:
    """SerpAPI adapter placeholder using its HTTP-compatible package."""
    def __init__(self, api_key: str): self.api_key = api_key
    def search(self, keyword: str, max_results: int) -> list[dict[str, Any]]:
        from serpapi import GoogleSearch
        return GoogleSearch({"q": keyword, "api_key": self.api_key, "num": max_results}).get_dict().get("organic_results", [])
class TavilyStrategy:
    """Tavily adapter."""
    def __init__(self, api_key: str): self.api_key = api_key
    def search(self, keyword: str, max_results: int) -> list[dict[str, Any]]:
        from tavily import TavilyClient
        return TavilyClient(api_key=self.api_key).search(keyword, max_results=max_results).get("results", [])

def keywords_for_topic(topic: str, year: int | None = None, max_keywords: int = 3) -> list[str]:
    """Generate current, deterministic keywords for a topic."""
    year = year or datetime.now().year
    return [topic, f"{topic} 最新进展", f"{topic} {year}"][:max_keywords]

def search_topics(topics: list[str], strategy: SearchStrategy, max_results_per_keyword: int = 5, max_keywords: int = 3) -> list[SearchResult]:
    """Search all topics, deduplicate by URL, and skip provider failures."""
    results: list[SearchResult] = []; seen: set[str] = set()
    for topic in topics:
        for keyword in keywords_for_topic(topic, max_keywords=max_keywords):
            logging.info("搜索关键词: %s", keyword)
            try: raw = strategy.search(keyword, max_results_per_keyword)
            except Exception as exc: logging.warning("搜索失败，跳过 %s: %s", keyword, exc); continue
            for item in raw:
                url = str(item.get("href") or item.get("link") or "").strip()
                parsed = urlparse(url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc or url in seen: continue
                seen.add(url); results.append(SearchResult(str(item.get("title", "")), url, str(item.get("body") or item.get("snippet", "")), urlparse(url).netloc))
    logging.info("搜索完成，共 %d 条结果", len(results)); return results
