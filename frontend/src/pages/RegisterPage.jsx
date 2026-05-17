import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { register, login } from '../api/auth'
import { setToken } from '../utils/authToken'
import './AuthPage.css'

function validatePassword(pw) {
  if (pw.length < 8) return 'Минимум 8 символов'
  if (!/[A-Z]/.test(pw)) return 'Нужна хотя бы одна заглавная буква'
  return null
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function handlePasswordChange(e) {
    const val = e.target.value
    setPassword(val)
    setPasswordError(val ? (validatePassword(val) ?? '') : '')
  }

  async function handleSubmit(e) {
    e.preventDefault()
    const pwErr = validatePassword(password)
    if (pwErr) { setPasswordError(pwErr); return }
    setError('')
    setLoading(true)
    try {
      await register(email, password)
      const data = await login(email, password)
      setToken(data.access_token)
      localStorage.setItem('user_email', email)
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
        <div className="auth-logo">✦ TOURRHYTHM</div>
        <h1 className="auth-title">Создать аккаунт</h1>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="auth-field">
            <label className="auth-label">EMAIL</label>
            <input
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
            <label className="auth-label">ПАРОЛЬ</label>
            <input
              className={`auth-input${passwordError ? ' auth-input--error' : ''}`}
              type="password"
              value={password}
              onChange={handlePasswordChange}
              placeholder="••••••••"
              required
              autoComplete="new-password"
            />
            {passwordError && <p className="auth-field-error">{passwordError}</p>}
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button
            className="auth-btn"
            type="submit"
            disabled={loading || !!passwordError}
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
