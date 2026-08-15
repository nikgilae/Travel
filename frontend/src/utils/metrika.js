// Обёртка над Яндекс.Метрикой. Сам счётчик подключается в index.html,
// здесь только вызовы из приложения.
//
// Зачем обёртка: фронт это SPA на BrowserRouter, поэтому Метрика видит один
// просмотр при первой загрузке и больше ничего. Переход с лендинга на
// /register происходит без перезагрузки страницы и без ручного hit не
// засчитывается вовсе.
//
// Все вызовы best-effort: window.ym нет при статическом рендере на сборке,
// в dev без счётчика и у людей с блокировщиками рекламы. Молча выходим.

export const YM_ID = 111624537

function call(...args) {
  if (typeof window === 'undefined' || typeof window.ym !== 'function') return
  try {
    window.ym(YM_ID, ...args)
  } catch {
    // Аналитика не имеет права ронять интерфейс.
  }
}

/**
 * Просмотр страницы при переходе внутри SPA.
 * @param {string} url  новый адрес, например "/register"
 * @param {string} [referer]  адрес, с которого ушли
 */
export function ymHit(url, referer) {
  call('hit', url, {
    title: typeof document !== 'undefined' ? document.title : undefined,
    referer,
  })
}

/**
 * Достижение цели. Цель с таким же идентификатором должна быть заведена
 * в интерфейсе Метрики (Настройка → Цели → JavaScript-событие),
 * иначе вызов просто никуда не запишется.
 * @param {string} name
 */
export function ymGoal(name) {
  call('reachGoal', name)
}
