"""Configuration behavior tests."""
from daily_insight.config import ConfigError, init_config, load_config


def test_init_config(tmp_path):
    path = init_config(tmp_path / "config.yaml"); assert path.exists()

def test_missing_api_key(tmp_path):
    path = init_config(tmp_path / "config.yaml")
    try: load_config(path, {})
    except ConfigError as exc: assert "DEEPSEEK_API_KEY" in str(exc)
    else: assert False

def test_missing_section(tmp_path):
    path = tmp_path / "bad.yaml"; path.write_text("topics: []")
    try: load_config(path, {"DEEPSEEK_API_KEY":"x"})
    except ConfigError as exc: assert "缺少" in str(exc)
    else: assert False
