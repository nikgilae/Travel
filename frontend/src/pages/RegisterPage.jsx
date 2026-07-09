import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register, login } from '../api/auth'
import { setToken } from '../utils/authToken'
import './AuthPage.css'

const PW_RULES = [
  { key: 'len',     label: 'Минимум 12 символов',      test: pw => pw.length >= 12 },
  { key: 'upper',   label: 'Заглавная буква (A–Z)',     test: pw => /[A-Z]/.test(pw) },
  { key: 'lower',   label: 'Строчная буква (a–z)',      test: pw => /[a-z]/.test(pw) },
  { key: 'digit',   label: 'Цифра (0–9)',               test: pw => /[0-9]/.test(pw) },
  { key: 'special', label: 'Специальный символ (!@#…)', test: pw => /[^A-Za-z0-9]/.test(pw) },
]

function pwValid(pw) {
  return PW_RULES.every(r => r.test(pw))
}

function PasswordRules({ password, touched }) {
  if (!touched) return null
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', gap: 5,
      padding: '10px 12px',
      background: '#F6F7F9',
      borderRadius: 10,
      border: '1px solid #E8EAEC',
    }}>
      {PW_RULES.map(r => {
        const ok = r.test(password)
        return (
          <div key={r.key} style={{
            display: 'flex', alignItems: 'center', gap: 8,
            fontSize: 12,
            color: ok ? '#1E7A4B' : '#5B6066',
            fontFamily: 'Onest, sans-serif',
            transition: 'color 0.15s',
          }}>
            <span style={{
              width: 16, height: 16, borderRadius: '50%', flexShrink: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: ok ? '#E4F4EB' : '#F1F3F5',
              border: `1px solid ${ok ? '#1E7A4B' : '#D6D9DD'}`,
              fontSize: 9, fontWeight: 700,
              transition: 'all 0.15s',
            }}>
              {ok ? '✓' : '·'}
            </span>
            {r.label}
          </div>
        )
      })}
    </div>
  )
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [pwTouched, setPwTouched] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const isValid = pwValid(password)
  const showError = pwTouched && !isValid && password.length > 0

  async function handleSubmit(e) {
    e.preventDefault()
    setPwTouched(true)
    if (!isValid) return
    setError('')
    setLoading(true)
    try {
      await register(email, password)
      const data = await login(email, password)
      setToken(data.access_token)
      localStorage.setItem('user_email', email)
      // После регистрации всегда на онбординг
      navigate('/onboarding')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="auth-app">
      <div className="auth-card">
        <div className="auth-logo">TourRhythm</div>
        <h1 className="auth-title">Создать аккаунт</h1>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-field">
            <label className="auth-label" htmlFor="register-email">EMAIL</label>
            <input
              id="register-email"
              className="auth-input"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              autoComplete="email"
            />
          </div>

          <div className="auth-field">
            <label className="auth-label" htmlFor="register-password">ПАРОЛЬ</label>
            <input
              id="register-password"
              className={`auth-input${showError ? ' auth-input--error' : pwTouched && isValid ? ' auth-input--ok' : ''}`}
              type="password"
              value={password}
              onChange={e => { setPassword(e.target.value); setPwTouched(true) }}
              onBlur={() => setPwTouched(true)}
              placeholder="Например: Traveller#2025"
              required
              autoComplete="new-password"
            />
            <PasswordRules password={password} touched={pwTouched} />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button
            className="auth-btn"
            type="submit"
            disabled={loading}
          >
            {loading ? '···' : 'ЗАРЕГИСТРИРОВАТЬСЯ →'}
          </button>
        </form>

        <p className="auth-switch">
          Уже есть аккаунт?{' '}
          <Link to="/" className="auth-link">Войти</Link>
        </p>
      </div>
    </div>
  )
}
