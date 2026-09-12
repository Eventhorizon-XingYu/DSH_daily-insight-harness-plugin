"""Generator formatting tests."""
from datetime import date

from daily_insight.generator import format_materials
from daily_insight.searcher import SearchResult


def test_format_materials():
    text = format_materials(date(2026,1,1), [SearchResult("T","https://e.test","S","e.test")], [])
    assert "当前日期：2026-01-01" in text and "暂无相关视频" in text

def test_format_video():
    text = format_materials(date.today(), [], [])
    assert "## 网页搜索结果" in text and "## 视频搜索结果" in text
