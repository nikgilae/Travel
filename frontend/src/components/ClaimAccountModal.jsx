import { useState } from 'react'

import { claimAccount } from '../api/auth'
import { setToken } from '../utils/authToken'
import { clearGuest, dismissClaimPrompt } from '../utils/guestSession'
import { ymGoal } from '../utils/metrika'

// Те же правила, что в RegisterPage и в валидаторе на бэкенде. Дублируются
// осознанно: держать их в общем модуле пришлось бы вместе с вёрсткой списка,
// а формы выглядят по-разному.
const PW_MIN = 8

function pwValid(pw) {
  return pw.length >= PW_MIN
    && /[A-Z]/.test(pw)
    && /[a-z]/.test(pw)
    && /[0-9]/.test(pw)
}

/**
 * Просьба оставить почту, приходящая на готовом маршруте.
 *
 * Появляется не по счётчику касаний, а после первого осознанного действия с
 * маршрутом (убрал место, заменил место, зафиксировал день) — в этот момент
 * маршрут перестаёт быть выданным и становится своим. Закрывается крестиком
 * и в этой сессии больше не возвращается.
 */
export default function ClaimAccountModal({ open, onClose, onClaimed }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [touched, setTouched] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  if (!open) return null

  const valid = pwValid(password)

  function handleClose() {
    dismissClaimPrompt()
    onClose?.()
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setTouched(true)
    if (!valid) return
    setError('')
    setLoading(true)
    try {
      const data = await claimAccount(email, password)
      setToken(data.access_token)
      clearGuest()
      localStorage.setItem('user_email', email)
      ymGoal('signup')
      onClaimed?.()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Сохранить маршрут"
      style={{
        position: 'fixed', inset: 0, zIndex: 1000,
        background: 'rgba(16,17,19,0.45)',
        display: 'flex', alignItems: 'flex-end', justifyContent: 'center',
      }}
      onClick={handleClose}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          width: '100%', maxWidth: 430,
          background: '#fff',
          borderRadius: '20px 20px 0 0',
          padding: '22px 22px 26px',
          fontFamily: 'Onest, sans-serif',
          boxShadow: '0 -8px 40px rgba(0,0,0,0.18)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
          <div style={{ fontSize: 20, fontWeight: 600, letterSpacing: '-0.02em', lineHeight: 1.25 }}>
            Теперь это ваш маршрут.<br />
            <span style={{ fontWeight: 500, color: '#5B6066' }}>
              Чтобы не потерять его, оставьте почту и пароль.
            </span>
          </div>
          <button
            type="button"
            onClick={handleClose}
            aria-label="Закрыть"
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              fontSize: 22, lineHeight: 1, color: '#9AA0A6', padding: 0,
            }}
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 10, marginTop: 18 }}>
          <input
            type="email"
            value={email}
            onChange={e => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
            autoComplete="email"
            style={inputStyle}
          />
          <input
            type="password"
            value={password}
            onChange={e => { setPassword(e.target.value); setTouched(true) }}
            placeholder="Пароль"
            required
            autoComplete="new-password"
            style={inputStyle}
          />

          {touched && !valid && password.length > 0 && (
            <div style={{ fontSize: 12, color: '#5B6066' }}>
              Минимум {PW_MIN} символов, заглавная и строчная буква, цифра.
            </div>
          )}
          {error && <div style={{ fontSize: 13, color: '#C0392B' }}>{error}</div>}

          <button
            type="submit"
            disabled={loading}
            style={{
              height: 52, borderRadius: 99, border: 'none',
              background: '#B9FF3D', color: '#101113',
              fontFamily: 'Onest, sans-serif', fontSize: 16, fontWeight: 600,
              cursor: loading ? 'default' : 'pointer',
              opacity: loading ? 0.6 : 1,
              marginTop: 4,
            }}
          >
            {loading ? '···' : 'Сохранить маршрут'}
          </button>
        </form>

        <button
          type="button"
          onClick={handleClose}
          style={{
            width: '100%', marginTop: 10,
            background: 'none', border: 'none', cursor: 'pointer',
            fontFamily: 'Onest, sans-serif', fontSize: 14, color: '#9AA0A6',
          }}
        >
          Позже
        </button>
      </div>
    </div>
  )
}

const inputStyle = {
  height: 50, padding: '0 16px',
  borderRadius: 12, border: '1.5px solid #E8EAEC',
  fontFamily: 'Onest, sans-serif', fontSize: 15,
  color: '#101113', outline: 'none', boxSizing: 'border-box',
  width: '100%',
}
