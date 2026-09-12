"""Markdown article export with collision-safe filenames."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from .utils import slugify


def export_article(content: str, output_dir: str | Path, topic: str, day: date | None = None, naming: str = "{date}_{topic_slug}.md") -> Path:
    """Write an article and append a numeric suffix when the name exists."""
    target_dir = Path(output_dir); target_dir.mkdir(parents=True, exist_ok=True); day = day or date.today()
    name = naming.format(date=day.isoformat(), topic_slug=slugify(topic))
    if Path(name).name != name or name in {".", ".."}:
        raise ValueError("output.naming 只能生成单层文件名")
    path = target_dir / name
    original_stem = path.stem
    index = 2
    while path.exists():
        path = target_dir / f"{original_stem}_{index}{path.suffix}"
        index += 1
    path.write_text(content, encoding="utf-8")
    return path
