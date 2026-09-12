"""Configuration loading, validation, and environment secret handling."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml

DEFAULT_CONFIG = '''schedule:
  time: "08:00"
  timezone: "Asia/Shanghai"
topics:
  - "AI Agent"
  - "大模型"
  - "开源硬件"
search:
  engine: "duckduckgo"
  max_results_per_keyword: 5
  max_keywords: 3
video:
  platforms: ["youtube", "bilibili"]
  max_videos: 3
llm:
  provider: "deepseek"
  base_url: "https://api.deepseek.com/v1"
  model: "deepseek-chat"
  temperature: 0.7
  max_tokens: 4096
output:
  dir: "./output"
  naming: "{date}_{topic_slug}.md"
'''

class ConfigError(ValueError):
    """Raised when configuration is missing or invalid."""

@dataclass
class Settings:
    """Validated application settings."""
    data: dict[str, Any]
    api_key: str
    search_api_key: str | None = None
    @property
    def schedule(self) -> dict[str, Any]: return self.data["schedule"]
    @property
    def topics(self) -> list[str]: return self.data["topics"]
    @property
    def search(self) -> dict[str, Any]: return self.data["search"]
    @property
    def video(self) -> dict[str, Any]: return self.data["video"]
    @property
    def llm(self) -> dict[str, Any]: return self.data["llm"]
    @property
    def output(self) -> dict[str, Any]: return self.data["output"]

def init_config(path: str | Path = "config/default.yaml") -> Path:
    """Create a default YAML configuration file if absent."""
    target = Path(path); target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists(): target.write_text(DEFAULT_CONFIG, encoding="utf-8")
    return target

def load_config(path: str | Path = "config/default.yaml", environ: dict[str, str] | None = None) -> Settings:
    """Load and validate YAML config, reading credentials only from environment."""
    env = os.environ if environ is None else environ
    target = Path(path)
    if not target.exists(): raise ConfigError(f"配置文件不存在，请先运行 daily-insight init: {target}")
    raw = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict): raise ConfigError("配置文件根节点必须是 YAML 对象")
    required = ("schedule", "topics", "search", "video", "llm", "output")
    missing = [key for key in required if key not in raw]
    if missing: raise ConfigError(f"配置缺少必填项: {', '.join(missing)}")
    # Validate every structured section before reading nested values below.  This
    # keeps malformed YAML from surfacing as an unhelpful KeyError/TypeError.
    for section in ("schedule", "search", "video", "llm", "output"):
        if not isinstance(raw[section], dict):
            raise ConfigError(f"{section} 必须是对象")
    if not isinstance(raw["topics"], list) or not raw["topics"] or not all(isinstance(item, str) and item.strip() for item in raw["topics"]):
        raise ConfigError("topics 必须是非空字符串列表")
    if not isinstance(raw["schedule"].get("timezone"), str) or not raw["schedule"]["timezone"].strip():
        raise ConfigError("schedule.timezone 不能为空")
    try:
        ZoneInfo(str(raw["schedule"]["timezone"]))
    except (ZoneInfoNotFoundError, ValueError):
        raise ConfigError("schedule.timezone 必须是有效的 IANA 时区") from None
    if not isinstance(raw["search"].get("max_results_per_keyword"), int) or raw["search"]["max_results_per_keyword"] < 1:
        raise ConfigError("search.max_results_per_keyword 必须是正整数")
    if raw["search"]["max_results_per_keyword"] > 50:
        raise ConfigError("search.max_results_per_keyword 不能超过 50")
    if not isinstance(raw["search"].get("max_keywords"), int) or raw["search"]["max_keywords"] < 1:
        raise ConfigError("search.max_keywords 必须是正整数")
    if raw["search"]["max_keywords"] > 20:
        raise ConfigError("search.max_keywords 不能超过 20")
    if not isinstance(raw["video"].get("platforms"), list) or not all(isinstance(p, str) for p in raw["video"]["platforms"]):
        raise ConfigError("video.platforms 必须是字符串列表")
    if any(platform not in {"youtube", "bilibili"} for platform in raw["video"]["platforms"]):
        raise ConfigError("video.platforms 只能包含 youtube 或 bilibili")
    if not isinstance(raw["video"].get("max_videos"), int) or raw["video"]["max_videos"] < 0:
        raise ConfigError("video.max_videos 必须是非负整数")
    if raw["video"]["max_videos"] > 20:
        raise ConfigError("video.max_videos 不能超过 20")
    if not isinstance(raw["llm"].get("provider"), str) or not raw["llm"]["provider"].strip():
        raise ConfigError("llm.provider 必须是非空字符串")
    if not isinstance(raw["llm"].get("base_url"), str) or not raw["llm"]["base_url"].strip() or not isinstance(raw["llm"].get("model"), str) or not raw["llm"]["model"].strip():
        raise ConfigError("llm.base_url 和 llm.model 必须是非空字符串")
    parsed_base_url = urlparse(raw["llm"]["base_url"])
    if parsed_base_url.scheme != "https" or not parsed_base_url.netloc:
        raise ConfigError("llm.base_url 必须是 HTTPS 接口地址")
    if not isinstance(raw["llm"].get("temperature"), (int, float)) or not 0 <= raw["llm"]["temperature"] <= 2:
        raise ConfigError("llm.temperature 必须在 0 到 2 之间")
    if not isinstance(raw["llm"].get("max_tokens"), int) or raw["llm"]["max_tokens"] < 1:
        raise ConfigError("llm.max_tokens 必须是正整数")
    if raw["llm"]["max_tokens"] > 32768:
        raise ConfigError("llm.max_tokens 不能超过 32768")
    if not isinstance(raw["output"].get("dir"), str) or not raw["output"]["dir"].strip() or not isinstance(raw["output"].get("naming"), str) or not raw["output"]["naming"].strip():
        raise ConfigError("output.dir 和 output.naming 必须是非空字符串")
    time = str(raw["schedule"].get("time", ""))
    match = re.fullmatch(r"([01]\d|2[0-3]):([0-5]\d)", time)
    if not match: raise ConfigError("schedule.time 必须为有效的 HH:MM（00:00-23:59）")
    timezone = raw["schedule"].get("timezone")
    if not isinstance(timezone, str) or not timezone.strip(): raise ConfigError("schedule.timezone 不能为空")
    engine = raw["search"].get("engine")
    if engine not in {"duckduckgo", "serpapi", "tavily"}: raise ConfigError("search.engine 必须是 duckduckgo、serpapi 或 tavily")
    api_key = env.get("DEEPSEEK_API_KEY", "")
    if not api_key: raise ConfigError("未设置 DEEPSEEK_API_KEY，请先执行 export DEEPSEEK_API_KEY=\"sk-xxx\"")
    extra_env_name = {"serpapi": "SERPAPI_KEY", "tavily": "TAVILY_KEY"}.get(engine, "")
    extra = env.get(extra_env_name) if engine != "duckduckgo" else None
    if engine != "duckduckgo" and not extra:
        raise ConfigError(f"{engine} 搜索引擎需要设置环境变量 {extra_env_name}")
    return Settings(raw, api_key, extra)
