"""Exporter behavior tests."""
from daily_insight.exporter import export_article


def test_export_and_suffix(tmp_path):
    first = export_article("one", tmp_path, "AI Agent"); second = export_article("two", tmp_path, "AI Agent")
    assert first.exists() and second.name.endswith("_2.md")
def test_export_content(tmp_path):
    path = export_article("hello", tmp_path, "topic"); assert path.read_text() == "hello"
