import { useEffect, useState } from 'react'

import { guestLogin } from '../api/auth'
import { getToken, setToken } from '../utils/authToken'
import { markGuest } from '../utils/guestSession'

/**
 * Пускает в онбординг без регистрации.
 *
 * Раньше здесь стоял ProtectedRoute, и человек без токена улетал на /login.
 * То есть первым экраном продукта была форма, до всякой ценности. Теперь,
 * если токена нет, фронт молча заводит гостевой аккаунт и идёт дальше —
 * человек этого не видит. Почту у него спросят на готовом маршруте.
 *
 * Тем, у кого токен уже есть (вошли раньше), ничего не меняется.
 */
export default function GuestGate({ children }) {
  const [ready, setReady] = useState(() => !!getToken())
  const [error, setError] = useState('')

  useEffect(() => {
    if (ready) return

    let cancelled = false
    guestLogin()
      .then(data => {
        if (cancelled) return
        setToken(data.access_token)
        markGuest()
        setReady(true)
      })
      .catch(() => {
        if (!cancelled) setError('Не удалось начать. Проверьте подключение.')
      })

    return () => { cancelled = true }
  }, [ready])

  if (error) {
    return (
      <div style={{
        minHeight: '100dvh', display: 'flex',
        alignItems: 'center', justifyContent: 'center',
        padding: 24, textAlign: 'center',
        fontFamily: 'Onest, sans-serif', fontSize: 15,
      }}>
        {error}
      </div>
    )
  }

  if (!ready) return null

  return children
}
