// Daily Insight browser half: registers a plugin settings card in DSH.
// Hand-written lazy-CJS bundle (no build step) following the modlens pattern.
window.__ModuleLoader__.load({
  id: 'daily-insight-harness-plugin',
  factory: (require) => {
    var module = { exports: {} }
    var exports = module.exports

    function DailyInsightCard(props) {
      var react = require('react')
      var h = react.createElement
      var useState = react.useState

      var openState = useState(false)
      var keyState = useState('')
      var statusState = useState('')
      var healthState = useState({ label: '尚未检查', ok: null, running: false, detail: '' })
      var runningState = useState(false)
      var open = openState[0]
      var setOpen = openState[1]
      var key = keyState[0]
      var setKey = keyState[1]
      var status = statusState[0]
      var setStatus = statusState[1]
      var health = healthState[0]
      var setHealth = healthState[1]
      var running = runningState[0]
      var setRunning = runningState[1]

      function checkHealth() {
        fetch('/daily-insight/health')
          .then(function (response) {
            return response.json().then(function (body) {
              return { response: response, body: body }
            })
          })
          .then(function (result) {
            var body = result.body || {}
            var ready = result.response.ok && body.workerAvailable && body.configAvailable
            var label = !result.response.ok
              ? '无法连接'
              : !body.workerAvailable
                ? 'Worker 不可用'
                : !body.configAvailable
                  ? '配置文件缺失'
                  : '服务可用'
            setHealth({
              label: label,
              ok: ready,
              running: !!body.running,
              detail: 'Worker ' + (body.workerAvailable ? '✓' : '✗')
                + ' · 配置 ' + (body.configAvailable ? '✓' : '✗')
                + ' · 环境密钥 ' + (body.apiKeyAvailable ? '✓' : '可临时输入'),
            })
          })
          .catch(function () {
            setHealth({ label: '无法连接', ok: false, running: false, detail: '请确认 DSH 插件已正确安装并重启' })
          })
      }

      function run() {
        if (running) return
        setRunning(true)
        setStatus('正在生成……')
        var headers = {}
        if (key) headers['x-daily-insight-key'] = key
        fetch('/daily-insight/run', { method: 'POST', headers: headers })
          .then(function (response) {
            return response.json().then(function (body) {
              return { response: response, body: body }
            })
          })
          .then(function (result) {
            if (!result.response.ok) throw new Error(result.body.error || '生成失败')
            var text = result.body.output || (result.body.ok ? '生成完成' : '生成失败')
            setStatus(text.slice(0, 800))
          })
          .catch(function (error) {
            setStatus('错误：' + (error && error.message ? error.message : String(error)))
          })
          .finally(function () {
            setRunning(false)
            checkHealth()
          })
      }

      var cardStyle = {
        border: '1px solid var(--dsw-alias-border-l2, rgba(127,127,127,0.35))',
        background: open
          ? 'var(--dsw-alias-bg-layer-2, rgba(127,127,127,0.10))'
          : 'var(--dsw-alias-bg-layer-3, rgba(127,127,127,0.05))',
        borderRadius: '12px',
        transition: 'border-color .16s, background .16s',
      }

      var headerStyle = {
        appearance: 'none',
        width: '100%',
        font: 'inherit',
        color: 'inherit',
        textAlign: 'left',
        cursor: 'pointer',
        background: 'none',
        border: 0,
        borderRadius: '12px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        padding: '14px 16px',
      }

      var titleStyle = {
        fontSize: '14px',
        fontWeight: 600,
        lineHeight: 1.4,
      }

      var descStyle = {
        color: 'var(--dsw-alias-label-tertiary, rgba(127,127,127,0.8))',
        fontSize: '13px',
        lineHeight: 1.5,
      }

      var bodyStyle = {
        margin: '0 16px',
        paddingBottom: '8px',
      }

      var inputStyle = {
        width: '100%',
        boxSizing: 'border-box',
        margin: '8px 0',
        padding: '8px 12px',
        font: 'inherit',
        fontSize: '13px',
        border: '1px solid var(--dsw-alias-border-l2, rgba(127,127,127,0.35))',
        borderRadius: '8px',
        background: 'var(--dsw-alias-bg-layer-3, rgba(127,127,127,0.05))',
        color: 'inherit',
      }

      var buttonStyle = {
        margin: '8px 0',
        padding: '6px 14px',
        font: 'inherit',
        fontSize: '13px',
        cursor: 'pointer',
        border: '1px solid transparent',
        borderRadius: '8px',
        background: 'var(--dsw-alias-label-primary, currentColor)',
        color: 'var(--dsw-alias-bg-layer-3, rgba(255,255,255,0.95))',
      }

      var hintStyle = {
        fontSize: '12px',
        color: 'var(--dsw-alias-label-tertiary, rgba(127,127,127,0.8))',
        margin: '4px 0 8px',
      }

      var healthStyle = {
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        fontSize: '12px',
        color: 'var(--dsw-alias-label-secondary, inherit)',
        margin: '4px 0 10px',
      }

      var statusStyle = {
        whiteSpace: 'pre-wrap',
        fontSize: '12px',
        color: 'var(--dsw-alias-label-secondary, inherit)',
        margin: '8px 0',
        padding: '8px',
        background: 'var(--dsw-alias-bg-module-platform, rgba(127,127,127,0.05))',
        borderRadius: '8px',
      }

      return h(
        'div',
        { style: cardStyle },
        h(
          'button',
          {
            type: 'button',
            'aria-expanded': open,
            onClick: function () {
              if (!open) checkHealth()
              setOpen(!open)
            },
            style: headerStyle,
          },
          h(
            'div',
            { style: { flex: 1, minWidth: 0 } },
            h('div', { style: titleStyle }, 'Daily Insight'),
            h('div', { style: descStyle }, '每日 AI 趋势洞察生成')
          ),
          h('span', {
            title: health.label,
            style: {
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: health.ok === true ? '#22c55e' : health.ok === false ? '#ef4444' : '#a3a3a3',
              flex: '0 0 auto',
            },
          })
        ),
        open
          ? h(
              'div',
              { style: bodyStyle },
              h('p', { style: hintStyle }, '留空则自动使用 DSH 凭证中的 DEEPSEEK_API_KEY。手动填写仅用于本次生成，不会保存。'),
              h('div', { style: healthStyle },
                h('span', null, '连接状态：' + health.label),
                health.running ? h('span', null, '（正在生成）') : null,
                h('button', {
                  type: 'button',
                  onClick: checkHealth,
                  style: { marginLeft: 'auto', padding: '0', border: '0', background: 'none', color: 'inherit', cursor: 'pointer' },
                }, '刷新')
              ),
              health.detail ? h('div', { style: { fontSize: '12px', color: 'var(--dsw-alias-label-tertiary, rgba(127,127,127,0.8))', margin: '-4px 0 8px' } }, health.detail) : null,
              h('input', {
                type: 'password',
                autocomplete: 'off',
                value: key,
                onChange: function (e) {
                  setKey(e.target.value)
                },
                placeholder: 'DeepSeek API Key（可选）',
                style: inputStyle,
              }),
              h(
                'button',
                {
                  type: 'button',
                  onClick: run,
                  disabled: running,
                  style: Object.assign({}, buttonStyle, running ? { opacity: 0.6, cursor: 'wait' } : null),
                },
                running ? '生成中……' : '立即生成'
              ),
              status ? h('pre', { style: statusStyle }, status) : null
            )
          : null
      )
    }

    function registerCard(ctx) {
      if (typeof ctx.inject !== 'function') return
      ctx.inject(['slots'], function (scope) {
        scope.slots.inject('settings.plugin.item', function* () {
          yield ctx.slots.register(
            {
              name: 'settings.plugin.item',
              id: 'daily-insight',
              key: 'daily-insight',
              order: 50,
            },
            DailyInsightCard
          )
        })
      })
    }

    function apply(ctx) {
      registerCard(ctx)
    }

    exports.inject = []
    exports.apply = apply
    return module.exports
  },
})
