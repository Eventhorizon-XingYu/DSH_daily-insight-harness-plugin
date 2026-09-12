# 安装指南

## 用户安装

要求 Python 3.10 或更高版本。建议在虚拟环境中安装：

```bash
python -m venv .venv
# Linux/macOS
. .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install daily-insight-plugin
```

从源码安装（包含测试与 lint 工具）：

```bash
git clone https://github.com/your-name/daily-insight-plugin.git
cd daily-insight-plugin
pip install -e '.[test]'
```

## 配置凭据

初始化配置文件，并通过环境变量提供凭据（不要把密钥写入 YAML 或提交到 Git）：

```bash
daily-insight init
# Linux/macOS
export DEEPSEEK_API_KEY='sk-...'
# Windows PowerShell
$env:DEEPSEEK_API_KEY = 'sk-...'
```

使用 SerpAPI 或 Tavily 时，还需设置对应的 `SERPAPI_KEY` 或 `TAVILY_KEY`。

## 运行

```bash
daily-insight run                 # 立即生成一篇文章
daily-insight run --config path/to/config.yaml
daily-insight daemon               # 按配置每日运行，Ctrl-C 停止
daily-insight init --path config/local.yaml
```

输出默认写入 `output/`。命令失败时会返回非零退出码；建议在首次运行前先用默认的 DuckDuckGo 搜索策略验证配置。

## 开发环境

```bash
pip install -e '.[test]'
pytest
ruff check src tests
python -m build
```
