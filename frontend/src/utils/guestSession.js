// Гостевая сессия: аккаунт, который завёл фронт, а не человек.
//
// Флаг нужен на клиенте, потому что от него зависит одна вещь — показывать ли
// плашку «сохраните маршрут». Сервер знает то же самое (users.is_guest), но
// спрашивать его на каждое действие с местом дорого и незачем: ошибка в
// сторону лишней плашки безобиднее, чем лишний запрос на каждый тап.

const GUEST_KEY = 'is_guest'
const PROMPT_KEY = 'claim_prompt_dismissed'

export function markGuest() {
  localStorage.setItem(GUEST_KEY, '1')
}

export function isGuest() {
  return localStorage.getItem(GUEST_KEY) === '1'
}

// Гость стал настоящим (вписал почту) либо вошёл в существующий аккаунт.
export function clearGuest() {
  localStorage.removeItem(GUEST_KEY)
  localStorage.removeItem(PROMPT_KEY)
}

// Плашку закрыли крестиком. Больше в этой сессии не показываем: человек уже
// ответил, повторять — это выпрашивать.
export function dismissClaimPrompt() {
  sessionStorage.setItem(PROMPT_KEY, '1')
}

export function claimPromptDismissed() {
  return sessionStorage.getItem(PROMPT_KEY) === '1'
}

// Показывать ли плашку прямо сейчас: человек — гость, и он ещё не закрывал её.
export function shouldAskToClaim() {
  return isGuest() && !claimPromptDismissed()
}
