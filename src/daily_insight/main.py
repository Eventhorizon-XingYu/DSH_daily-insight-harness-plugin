"""Command-line entry point for Daily Insight Plugin."""
from __future__ import annotations

import argparse
import logging
import time

from .config import ConfigError, init_config, load_config
from .exporter import export_article
from .generator import ArticleGenerator
from .scheduler import run_daemon
from .searcher import DuckDuckGoStrategy, SerpApiStrategy, TavilyStrategy, search_topics
from .utils import setup_logging
from .video_finder import VideoFinder


def generate_once(settings) -> str:
    """Search, generate, and export one article."""
    started = time.perf_counter(); engine = settings.search["engine"]
    strategy = DuckDuckGoStrategy() if engine == "duckduckgo" else SerpApiStrategy(settings.search_api_key) if engine == "serpapi" else TavilyStrategy(settings.search_api_key)
    articles = search_topics(settings.topics, strategy, settings.search["max_results_per_keyword"], settings.search["max_keywords"])
    topic = settings.topics[0]; videos = VideoFinder(settings.video["platforms"], settings.video["max_videos"]).find(topic)
    generator = ArticleGenerator(settings.api_key, settings.llm["base_url"], settings.llm["model"], settings.llm["temperature"], settings.llm["max_tokens"])
    content, usage = generator.generate(articles, videos); path = export_article(content, settings.output["dir"], topic, naming=settings.output["naming"])
    print(f"文章已保存：{path.resolve()}（耗时 {time.perf_counter()-started:.2f}s，token 用量：{usage}）"); return str(path)

def main(argv: list[str] | None = None) -> int:
    """Parse and execute a CLI command."""
    setup_logging(); parser = argparse.ArgumentParser(prog="daily-insight"); sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init"); init.add_argument("--path", default="config/default.yaml")
    for command in ("run", "daemon"):
        sub.add_parser(command).add_argument("--config", default="config/default.yaml")
    args = parser.parse_args(argv)
    if args.command == "init": print(f"已创建配置：{init_config(args.path)}"); return 0
    try: settings = load_config(args.config)
    except ConfigError as exc: print(f"配置错误：{exc}"); return 2
    if args.command == "run":
        try:
            generate_once(settings)
        except Exception as exc:
            logging.error("生成文章失败: %s", exc)
            print(f"运行失败：{exc}")
            return 1
        return 0
    hour, minute = map(int, settings.schedule["time"].split(":"))
    try:
        run_daemon(hour, minute, settings.schedule["timezone"], lambda: generate_once(settings))
    except Exception as exc:
        logging.error("守护进程失败: %s", exc)
        print(f"守护进程失败：{exc}")
        return 1
    return 0
if __name__ == "__main__": raise SystemExit(main())
