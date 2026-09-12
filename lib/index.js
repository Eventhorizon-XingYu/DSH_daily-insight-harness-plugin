import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

export const name = 'daily-insight-harness-plugin';

function json(response, status, value) {
  response.writeHead(status, { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' });
  response.end(JSON.stringify(value));
}

function sameOrigin(request) {
  const origin = request.headers?.origin;
  if (!origin) return true;
  try {
    const url = new URL(origin);
    return (url.protocol === 'http:' || url.protocol === 'https:')
      && new Set(['localhost', '127.0.0.1', '[::1]']).has(url.hostname);
  } catch {
    return false;
  }
}

function redact(value) {
  return String(value).replace(/sk-[A-Za-z0-9_-]+/g, '[redacted]');
}

export function apply(ctx) {
  ctx.inject(['webServer'], (hostCtx) => {
    const host = hostCtx;
    const workerRoot = process.env.DAILY_INSIGHT_ROOT || process.cwd();
    const entry = resolve(workerRoot, 'src', 'daily_insight', 'main.py');
    const configPath = resolve(workerRoot, process.env.DAILY_INSIGHT_CONFIG || resolve(workerRoot, 'config', 'default.yaml'));
    const disposers = [];
    let running = false;
    disposers.push(host.webServer.register({
      kind: 'exact', path: '/daily-insight/health',
      handler: (request, response) => {
        if (request.method && request.method !== 'GET') return json(response, 405, { error: 'method not allowed' });
        return json(response, 200, {
          ok: true,
          name,
          workerAvailable: existsSync(entry),
          configAvailable: existsSync(configPath),
          apiKeyAvailable: !!process.env.DEEPSEEK_API_KEY,
          pythonConfigured: !!process.env.PYTHON,
          running,
        });
      },
    }));
    disposers.push(host.webServer.register({
      kind: 'exact', path: '/daily-insight/run',
      handler: (request, response) => {
        if (request.method !== 'POST' || !sameOrigin(request)) return json(response, 405, { error: 'method or origin not allowed' });
        if (running) return json(response, 409, { error: '已有一次生成正在运行，请稍后再试' });
        const headerKey = typeof request.headers['x-daily-insight-key'] === 'string' ? request.headers['x-daily-insight-key'] : '';
        const apiKey = (headerKey || process.env.DEEPSEEK_API_KEY || '').trim();
        if (!apiKey || apiKey.length > 512) return json(response, 400, { error: 'API key is required (enter it below or set DEEPSEEK_API_KEY in DSH credentials)' });
        if (!existsSync(entry)) return json(response, 503, { error: 'Daily Insight worker unavailable; set DAILY_INSIGHT_ROOT.' });
        running = true;
        const env = { ...process.env, DEEPSEEK_API_KEY: apiKey, PYTHONPATH: [resolve(workerRoot, 'src'), process.env.PYTHONPATH].filter(Boolean).join(';') };
        const child = spawn(process.env.PYTHON || 'python', ['-m', 'daily_insight.main', 'run', '--config', configPath], { cwd: workerRoot, env, stdio: ['ignore', 'pipe', 'pipe'] });
        let output = '';
        let settled = false;
        const finish = (status, value) => {
          if (settled) return;
          settled = true;
          running = false;
          if (!response.writableEnded) json(response, status, value);
        };
        child.stdout.on('data', (chunk) => { output += String(chunk); });
        child.stderr.on('data', (chunk) => { output += String(chunk); });
        const timer = setTimeout(() => {
          child.kill();
          finish(504, { error: '生成超时，请检查搜索服务和模型接口后重试', output: redact(output) });
        }, 10 * 60 * 1000);
        child.on('close', (code) => {
          clearTimeout(timer);
          finish(code === 0 ? 200 : 500, { ok: code === 0, output: redact(output) });
        });
        child.on('error', (error) => {
          clearTimeout(timer);
          finish(500, { error: redact(error.message) });
        });
      },
    }));
    return () => disposers.forEach((dispose) => dispose?.());
  });
}
