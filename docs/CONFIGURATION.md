# 配置说明

配置文件默认位于 `config/default.yaml`，可通过 `--config` 传入其他路径。YAML 中的凭据字段不受支持；所有密钥必须由环境变量提供。

## 完整配置

```yaml
schedule:
  time: "08:00"                 # 24 小时制 HH:MM
  timezone: "Asia/Shanghai"     # IANA 时区名
topics: ["AI Agent", "大模型"]  # 至少一个主题
search:
  engine: "duckduckgo"          # duckduckgo、serpapi 或 tavily
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
```

## 字段参考

| 路径 | 类型/示例 | 说明 |
| --- | --- | --- |
| `schedule.time` | `08:00` | 每日触发时间，必须为 `HH:MM`。 |
| `schedule.timezone` | `Asia/Shanghai` | [IANA 时区](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)。 |
| `topics` | 字符串列表 | 搜索主题；首个主题用于标题和输出文件名。 |
| `search.engine` | `duckduckgo` | 搜索后端；SerpAPI/Tavily 需要密钥。 |
| `search.max_results_per_keyword` | 正整数 | 每个查询最多返回的素材数量。 |
| `video.platforms` | `youtube`, `bilibili` | 视频发现平台。 |
| `llm.base_url` | URL | OpenAI-compatible API 地址。 |
| `llm.model` | `deepseek-chat` | 生成模型名称。 |
| `output.naming` | 模板字符串 | 支持 `{date}`、`{topic_slug}`；重名时自动追加序号。 |

## 环境变量

- `DEEPSEEK_API_KEY`：必填，用于文章生成。
- `SERPAPI_KEY`：当 `search.engine: serpapi` 时必填。
- `TAVILY_KEY`：当 `search.engine: tavily` 时必填。

配置无效或缺少必填凭据时，CLI 会显示错误并返回退出码 `2`。
