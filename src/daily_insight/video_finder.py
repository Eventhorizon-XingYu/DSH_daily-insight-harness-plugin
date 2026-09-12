"""Video search and platform normalization."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from urllib.parse import urlparse

from .utils import retry


@dataclass
class VideoResult:
    """A discovered video with a verified source URL."""
    title: str
    platform: str
    url: str
    description: str

class VideoFinder:
    """Find and normalize videos from configured supported platforms."""
    def __init__(self, platforms: list[str] | None = None, max_videos: int = 3) -> None:
        self.platforms = {p.lower() for p in (platforms or ["youtube", "bilibili"])}
        self.max_videos = max_videos

    def find(self, topic: str) -> list[VideoResult]:
        """Search videos, returning an empty list after logged provider failure."""
        try:
            return self._find(topic)
        except Exception as exc:
            logging.warning("视频搜索失败: %s", exc)
            return []

    @retry(3)
    def _find(self, topic: str) -> list[VideoResult]:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            raw = list(ddgs.videos(f"{topic} 最新视频", max_results=max(1, self.max_videos * 3)))
        results = []
        seen: set[str] = set()
        for item in raw:
            url = str(item.get("content") or item.get("url") or "").strip()
            parsed = urlparse(url)
            host = parsed.netloc.lower().split(":")[0]
            if parsed.scheme not in {"http", "https"} or not host or url in seen:
                continue
            platform = "YouTube" if host in {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be"} else "Bilibili" if host.endswith("bilibili.com") else "Other"
            if platform.lower() not in self.platforms:
                continue
            seen.add(url)
            results.append(VideoResult(str(item.get("title", "")), platform, url, str(item.get("description", ""))))
        return results[:self.max_videos]
