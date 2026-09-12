"""DeepSeek article generation using the OpenAI-compatible SDK."""
from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

from .searcher import SearchResult
from .video_finder import VideoResult


def format_materials(day: date, articles: Sequence[SearchResult], videos: Sequence[VideoResult]) -> str:
    """Format search materials into the documented user prompt."""
    lines = [f"当前日期：{day.isoformat()}", "", "## 网页搜索结果"]
    for i, item in enumerate(articles, 1): lines += [f"[{i}] 标题：{item.title}", f"    链接：{item.url}", f"    摘要：{item.snippet}", f"    来源：{item.domain}", ""]
    lines.append("## 视频搜索结果")
    lines += [f"- 标题：{v.title} | 平台：{v.platform} | 链接：{v.url}" for v in videos] or ["暂无相关视频"]
    lines.append("\n请根据以上素材，撰写今日文章。"); return "\n".join(lines)
class ArticleGenerator:
    """Generate a Markdown article and expose usage metadata."""
    def __init__(self, api_key: str, base_url: str, model: str, temperature: float = .7, max_tokens: int = 4096, prompt_path: str | Path | None = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=10.0)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.prompt_path = Path(prompt_path) if prompt_path else Path(__file__).parent / "prompts" / "daily_article.md"
    def generate(self, articles: Sequence[SearchResult], videos: Sequence[VideoResult], day: date | None = None) -> tuple[str, dict[str, Any]]:
        """Call the model, retry once on empty content, and return usage."""
        system = self.prompt_path.read_text(encoding="utf-8"); user = format_materials(day or date.today(), articles, videos)
        for _ in range(2):
            logging.info("调用 DeepSeek API")
            response = self.client.chat.completions.create(model=self.model, temperature=self.temperature, max_tokens=self.max_tokens, messages=[{"role":"system","content":system},{"role":"user","content":user}])
            content = (response.choices[0].message.content or "").strip()
            if content:
                usage_obj = getattr(response, "usage", None)
                usage = {}
                if usage_obj is not None:
                    for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
                        value = getattr(usage_obj, field, None)
                        if value is not None: usage[field] = value
                return content, usage
        raise RuntimeError("DeepSeek 返回空文章内容")
