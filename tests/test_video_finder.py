"""Video behavior tests."""
from unittest.mock import patch

from daily_insight.video_finder import VideoFinder


def test_empty_videos():
    with patch("duckduckgo_search.DDGS") as cls:
        cls.return_value.__enter__.return_value.videos.return_value = []
        assert VideoFinder().find("AI") == []

def test_video_limit():
    with patch("duckduckgo_search.DDGS") as cls:
        cls.return_value.__enter__.return_value.videos.return_value = [{"title":str(i),"content":f"https://youtube.com/{i}"} for i in range(5)]
        assert len(VideoFinder(max_videos=2).find("AI")) == 2
