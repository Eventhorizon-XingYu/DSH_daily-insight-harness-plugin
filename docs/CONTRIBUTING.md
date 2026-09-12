# 贡献指南

感谢贡献 Daily Insight Plugin！Issue、文档改进、搜索策略和修复都欢迎提交。

## 开始开发

```bash
git clone https://github.com/your-name/daily-insight-plugin.git
cd daily-insight-plugin
python -m venv .venv
pip install -e '.[test]'
```

## 提交前检查

请在提交 Pull Request 前运行全部检查：

```bash
pytest
ruff check src tests
python -m build
```

不得提交 API 密钥、`.env` 文件、生成的文章或 `dist/` 构建产物。涉及网络或 LLM 的测试应使用 mock，保证离线、可重复执行。

## 添加搜索策略

在 `src/daily_insight/searcher.py` 中实现 `SearchStrategy.search` 接口，并在 CLI 工厂中注册引擎名称。为正常结果、空结果和异常响应补充测试；搜索结果必须保留真实 URL，不能猜测或拼接不存在的链接。

## Pull Request 约定

- 标题简明描述变更；正文说明动机、实现和测试结果。
- 保持模块职责单一，并更新 README 或 `docs/` 中受影响的配置说明。
- 新增行为应包含回归测试。
- CI 必须通过后再请求评审。
