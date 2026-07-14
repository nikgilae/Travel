// Глобальный репортер ошибок фронтенда (T8).
// Ловит window.onerror и unhandledrejection и best-effort шлёт на бэкенд
// (POST /client-errors), чтобы «чёрный ящик» видел и клиентские падения.
// UI не меняет: только слушатели + fire-and-forget fetch.

const API_BASE = import.meta.env.VITE_API_URL

// Защита от шторма: не больше N отчётов за сессию (одна ошибка в цикле рендера
// могла бы завалить бэкенд сотнями запросов).
const MAX_REPORTS = 20
let reported = 0

function trunc(value, max) {
  if (value == null) return null
  const s = String(value)
  return s.length > max ? s.slice(0, max) : s
}

function send(payload) {
  if (!API_BASE || reported >= MAX_REPORTS) return
  reported++
  try {
    fetch(`${API_BASE}/client-errors`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true, // отправится даже если вкладку закрывают
    }).catch(() => {}) // best-effort: молча игнорируем сбой отправки
  } catch {
    /* never throw from an error handler */
  }
}

export function installErrorReporter() {
  window.addEventListener('error', (e) => {
    send({
      kind: 'onerror',
      message: trunc(e.message || 'Unknown error', 2000),
      source: trunc(e.filename, 500),
      lineno: e.lineno ?? null,
      colno: e.colno ?? null,
      stack: trunc(e.error && e.error.stack, 8000),
      url: trunc(window.location.href, 1000),
    })
  })

  window.addEventListener('unhandledrejection', (e) => {
    const reason = e.reason
    send({
      kind: 'unhandledrejection',
      message: trunc((reason && reason.message) || reason || 'Unhandled rejection', 2000),
      stack: trunc(reason && reason.stack, 8000),
      url: trunc(window.location.href, 1000),
    })
  })
}
