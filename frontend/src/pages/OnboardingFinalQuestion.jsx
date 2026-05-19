import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './OnboardingFinalQuestion.css'
import { useOnboarding } from '../store/onboardingStore.jsx'

const API_BASE = import.meta.env.VITE_API_URL

function getToken() {
  return localStorage.getItem('access_token') ?? ''
}

// ── Loading screen ─────────────────────────────────────────

function LoadingScreen({ cityName }) {
  return (
    <div className="ofq-app">
      <div className="ofq-phone" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100svh' }}>
        <div style={{
          width: 64, height: 64, borderRadius: '50%',
          border: '3px solid rgba(185,255,61,0.2)',
          borderTopColor: '#B9FF3D',
          animation: 'ofq-spin 0.9s linear infinite',
          marginBottom: 28,
        }} />
        <div style={{
          fontFamily: 'var(--font-ui)', fontWeight: 600, fontSize: 20,
          color: '#0A0B0C', letterSpacing: '-0.005em',
          marginBottom: 10, textAlign: 'center',
        }}>
          Складываю маршрут…
        </div>
        <div style={{
          fontFamily: 'var(--font-mono)', fontSize: 11,
          color: '#9097A0', letterSpacing: '0.12em', textTransform: 'uppercase',
        }}>
          {cityName ? cityName : '···'}
        </div>
      </div>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────

export default function OnboardingFinalQuestion({ city, groupType, rhythm, onBack }) {
  const navigate             = useNavigate()
  const { data, update }     = useOnboarding()

  const [text, setText]       = useState('')
  const [loading, setLoading] = useState(false)
  const [apiError, setApiError] = useState(null)

  const cityName = city?.n ?? 'город'

  async function handleSubmit(notes) {
    update({ notes })
    setLoading(true)
    setApiError(null)

    const body = {
      country_id:        data.country_id,
      city_id:           data.city_id,
      purpose:           data.purpose           ?? 'leisure',
      budget:            data.budget            ?? 'medium',
      group_size:        data.group_size        ?? 1,
      other_information: data.other_information ?? [],
      start_date:        data.start_date        ?? null,
      end_date:          data.end_date          ?? null,
    }

    try {
      const res = await fetch(`${API_BASE}/trips`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify(body),
      })

      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail ?? `Ошибка сервера (${res.status})`)
      }

      const trip = await res.json()
      localStorage.setItem('current_trip_id', trip.id)
      localStorage.setItem('trip_display_data', JSON.stringify({ city, groupType, rhythm }))

      const tripMeta = JSON.parse(localStorage.getItem('trip_meta') ?? '{}')
      tripMeta[trip.id] = { cityName: city?.n ?? null, city, groupType, rhythm }
      localStorage.setItem('trip_meta', JSON.stringify(tripMeta))

      const genRes = await fetch(`${API_BASE}/trips/${trip.id}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({
          interests: data.interests ?? [],
          notes: notes || null,
        }),
      })

      if (!genRes.ok) {
        const errBody = await genRes.json().catch(() => ({}))
        throw new Error(errBody.detail ?? `Не удалось сгенерировать маршрут (${genRes.status})`)
      }

      navigate(`/trip/${trip.id}/plan`, { state: { city, groupType, rhythm } })
    } catch (err) {
      setApiError(err.message)
      setLoading(false)
    }
  }

  if (loading) return <LoadingScreen cityName={cityName} />

  return (
    <div className="ofq-app">
      <div className="ofq-phone">

        {/* Progress bar */}
        <div style={{ padding: '20px 22px 0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <button onClick={onBack} style={{
              background: 'none', border: 'none', color: '#5B6066',
              fontSize: 13, cursor: 'pointer', padding: 0, fontFamily: 'inherit',
            }}>← Назад</button>
            <span style={{
              fontFamily: 'var(--font-mono)', fontSize: 11, color: '#9097A0',
              letterSpacing: '0.1em',
            }}>ШАГ 5 / 5</span>
          </div>
          <div style={{ height: 4, background: '#F1F3F5', borderRadius: 2, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: '100%', background: '#B9FF3D', borderRadius: 2 }} />
          </div>
        </div>

        {/* Content */}
        <div style={{ padding: '28px 22px 24px' }}>
          <div style={{
            fontFamily: 'var(--font-mono)', fontSize: 11, letterSpacing: '0.14em',
            textTransform: 'uppercase', color: '#9097A0', marginBottom: 10,
          }}>
            ПОЧТИ ГОТОВО
          </div>
          <h1 style={{
            fontSize: 26, fontWeight: 600, lineHeight: 1.2,
            letterSpacing: '-0.012em',
            color: '#0A0B0C', margin: '0 0 8px', fontFamily: 'var(--font-ui)',
          }}>
            Зачем ты едешь<br/>в {cityName}?
          </h1>
          <p style={{
            fontSize: 14, color: '#5B6066', lineHeight: 1.55, margin: '0 0 20px',
          }}>
            Чем честнее ответ — тем точнее маршрут.
          </p>

          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="Хочу отдохнуть от работы, почувствовать другой ритм жизни…"
            rows={5}
            style={{
              width: '100%', padding: '14px 16px',
              background: '#FFFFFF',
              border: '1px solid #E8EAEC',
              borderRadius: 14, resize: 'none', outline: 'none',
              fontFamily: 'var(--font-ui)', fontSize: 14, lineHeight: 1.55,
              color: '#0A0B0C', boxSizing: 'border-box',
              transition: 'border-color 0.12s ease, box-shadow 0.12s ease',
            }}
            onFocus={e => {
              e.target.style.borderColor = '#0A0B0C'
              e.target.style.boxShadow = '0 0 0 3px rgba(185,255,61,0.45)'
            }}
            onBlur={e => {
              e.target.style.borderColor = '#E8EAEC'
              e.target.style.boxShadow = 'none'
            }}
          />

          {text.length > 0 && (
            <div style={{
              marginTop: 10, padding: '10px 14px',
              background: '#F0FFD6',
              border: '1px solid rgba(185,255,61,0.4)',
              borderRadius: 10, fontSize: 12, color: '#1B2A0A', lineHeight: 1.4,
            }}>
              ИИ учтёт твой запрос при составлении маршрута
            </div>
          )}

          {apiError && (
            <div style={{
              marginTop: 12, padding: '12px 14px',
              background: '#FBE5E7',
              border: '1px solid rgba(180,51,64,0.3)',
              borderRadius: 10, fontSize: 13, color: '#B43340', lineHeight: 1.4,
            }}>
              {apiError}
            </div>
          )}
        </div>

        {/* Sticky CTA */}
        <div style={{
          position: 'sticky', bottom: 0,
          padding: '16px 22px 28px',
          background: 'linear-gradient(to top, #F6F7F9 75%, transparent)',
        }}>
          <button
            onClick={() => handleSubmit(text)}
            style={{
              width: '100%', height: 44,
              background: '#B9FF3D',
              border: '1px solid #B9FF3D',
              borderRadius: 10,
              fontWeight: 500, fontSize: 14, letterSpacing: '-0.005em',
              color: '#0A0B0C',
              cursor: 'pointer',
              transition: 'background 0.12s ease, transform 0.06s ease',
              fontFamily: 'var(--font-ui)',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = '#A8F02C'; e.currentTarget.style.borderColor = '#A8F02C' }}
            onMouseLeave={e => { e.currentTarget.style.background = '#B9FF3D'; e.currentTarget.style.borderColor = '#B9FF3D' }}
          >
            Создать маршрут
          </button>
        </div>

      </div>
    </div>
  )
}
