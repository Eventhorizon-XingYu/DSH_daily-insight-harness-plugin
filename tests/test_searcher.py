"""Search behavior tests."""
from daily_insight.searcher import keywords_for_topic, search_topics


class Fake:
    def search(self, keyword, max_results): return [{"title":"A","href":"https://example.com/a","body":"x"},{"title":"A","href":"https://example.com/a","body":"x"}]
def test_keywords(): assert keywords_for_topic("AI", 2026) == ["AI", "AI 最新进展", "AI 2026"]
def test_dedup(): assert len(search_topics(["AI"], Fake())) == 1
