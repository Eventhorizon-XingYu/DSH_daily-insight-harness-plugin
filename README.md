# Daily Insight Plugin

自动联网搜集每日资讯，调用 DeepSeek 生成结构化 Markdown 文章。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](pyproject.toml) [![PyPI](https://img.shields.io/pypi/v/daily-insight-plugin.svg)](https://pypi.org/project/daily-insight-plugin/)

## 功能特性
- 🔎 DuckDuckGo、SerpAPI、Tavily 策略式搜索
- 🤖 DeepSeek OpenAI-compatible API 文章生成
- 🎬 YouTube/Bilibili 视频发现，绝不编造链接
- ⏰ Asia/Shanghai 时区的 APScheduler 每日调度
- 📄 自动去重、引用、导出和同名文件递增

在 DSH 中，它的价值是把这条流程放到一个可操作的设置卡片里：打开卡片即可检查 worker、配置文件和凭据状态，输入一次性 API Key 后生成文章，结果仍保存到本地 `output/` 目录，方便你回到 Obsidian 或其他知识库继续整理。

## 效果预览
```markdown
# Agent 生态加速演进
> **一句话概述：** 今日素材显示 Agent 正从实验走向工程化落地。
## 📌 总览（Overview）
本文梳理事件背景、技术变化与行业影响。
```

## 快速安装
```bash
pip install daily-insight-plugin
# 或
 git clone https://github.com/your-name/daily-insight-plugin.git
cd daily-insight-plugin && pip install -e .
```

## 配置步骤
```bash
daily-insight init
export DEEPSEEK_API_KEY="sk-xxx"
```
编辑 `config/default.yaml` 自定义主题、时间、引擎和输出目录。

## 使用方法
```bash
daily-insight run
daily-insight daemon
```

## DeepSeek Harness 图形界面

本项目同时提供 DeepSeek Harness（DSH）插件包。安装后，DSH 设置页会显示 Daily Insight 卡片，可查看 worker 连接状态、临时输入 API Key 并点击“立即生成”。API Key 不会写入浏览器存储；生成输出会在界面中显示，并由宿主端脱敏。

DSH 发布包会包含 `lib/`、`client/`、`harness/` 和 `cordis.patch.yml`。其中 `harness/daily-insight.manifest.json` 描述插件能力，`harness/daily-insight.config.schema.json` 描述配置表单契约。

## 配置项说明
| 配置 | 含义 | 可选值 |
|---|---|---|
| schedule.time | 每日执行时间 | HH:MM |
| schedule.timezone | 时区 | IANA 时区 |
| topics | 关注主题 | 字符串列表 |
| search.engine | 搜索引擎 | duckduckgo/serpapi/tavily |
| search.max_results_per_keyword | 每关键词结果数 | 正整数 |
| video.max_videos | 视频上限 | 正整数 |
| llm.model | 模型 | DeepSeek 模型名 |
| output.dir | 输出目录 | 路径 |

## 支持的搜索引擎
| 引擎 | API Key | 特点 |
|---|---|---|
| DuckDuckGo | 无 | 默认免费 |
| SerpAPI | SERPAPI_KEY | 聚合搜索 |
| Tavily | TAVILY_KEY | AI 搜索 |

## 项目结构
见 `src/daily_insight/`、`tests/`、`docs/` 与 `.github/`。

## 开发指南
```bash
pip install -e '.[test]'
pytest
```
新增搜索引擎时实现 `SearchStrategy.search`，并在 CLI 工厂中注册。

## FAQ
**API Key 放哪里？** 仅放在 `DEEPSEEK_API_KEY` 环境变量，不写 YAML。

**没有视频怎么办？** 输出会标注“暂无相关视频”。

**文件重名怎么办？** 自动追加 `_2`、`_3` 等序号。

## License
MIT，详见 [LICENSE](LICENSE)。

## Contributing
欢迎提交 Issue、Pull Request 和新的搜索策略，详见 [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)。

## Star History / 致谢
感谢 DeepSeek、OpenAI SDK、APScheduler 和 DuckDuckGo 社区。
