# Daily Insight Harness Plugin

Official DeepSeek Harness bundle package for the Daily Insight Python worker.

## Prerequisites

Install the Python worker in the same environment used by the Harness host:

```powershell
python -m pip install daily-insight-plugin
```

The worker reads `DEEPSEEK_API_KEY` only from its process environment. The Harness client sends the key to the loopback host bridge for one run; it is not stored in YAML or browser storage.

## Harness installation

This package follows the official DSH bundle contract (`dsh.bundle.patch`, ESM host entry, and `exports["./client"]`). Install it into the active profile with the Harness plugin command using an exact npm package version, then restart the profile. A package must be published to npm before the managed Plugin Market can verify and install it; the local workspace is not automatically installed by the Market.

The UI contributes a Daily Insight settings card with connection health, one-click generation, busy-state protection, and a redacted output panel. The host exposes only loopback `/daily-insight/health` and `/daily-insight/run` routes and redacts `sk-...` patterns from output. The package ships the DSH manifest and configuration schema under `harness/`.

Set `DAILY_INSIGHT_ROOT` to the Python worker checkout. If DSH stores configuration outside the checkout, set `DAILY_INSIGHT_CONFIG` to the YAML file path as well; the bridge passes that path to the worker instead of silently falling back to a different configuration.

## Development

```powershell
node --check lib/index.js
node --check client/client.js
python -m compileall -q src tests
```

The current package is an integration bridge, not a replacement for the Python worker. Search results and generated Markdown remain untrusted external data and should be reviewed before publication.
