const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export async function register(email, password) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail ?? 'Ошибка регистрации')
  return data
}

// Гостевой вход: аккаунт заводится молча, чтобы человек попал в онбординг
// без единого поля. Настоящую почту он вписывает позже, на готовом маршруте
// (claimAccount ниже) — там у аккаунта уже есть, что терять.
export async function guestLogin() {
  const res = await fetch(`${API_BASE}/auth/guest`, { method: 'POST' })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail ?? 'Не удалось начать сессию')
  return data
}

// Дописывает почту и пароль к текущему гостевому аккаунту. Поездки никуда
// не переезжают: аккаунт тот же самый, у него просто появляется вход.
export async function claimAccount(email, password) {
  const res = await fetch(`${API_BASE}/auth/claim`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('access_token') ?? ''}`,
    },
    body: JSON.stringify({ email, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail ?? 'Не удалось сохранить маршрут')
  return data
}

export async function login(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail ?? 'Ошибка входа')
  return data
}