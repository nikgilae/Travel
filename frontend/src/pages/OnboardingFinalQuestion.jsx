import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './OnboardingFinalQuestion.css'
import { useOnboarding } from '../store/onboardingStore.jsx'

const API_BASE = 'http://localhost:8000'

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
          border: '3px solid rgba(184,255,79,0.2)',
          borderTopColor: '#b8ff4f',
          animation: 'ofq-spin 0.9s linear infinite',
          marginBottom: 28,
        }} />
        <div style={{
          fontFamily: 'inherit', fontWeight: 900, fontSize: 22,
          textTransform: 'uppercase', color: '#fff', letterSpacing: '-0.01em',
          marginBottom: 10, textAlign: 'center',
        }}>
          Складываю маршрут…
        </div>
        <div style={{
          fontFamily: 'monospace', fontSize: 11,
          color: 'rgba(255,255,255,0.4)', letterSpacing: '0.1em',
        }}>
          {cityName ? cityName.toUpperCase() : '···'}
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

      // Persist city name per trip so the dashboard can display it
      const tripMeta = JSON.parse(localStorage.getItem('trip_meta') ?? '{}')
      tripMeta[trip.id] = { cityName: city?.n ?? null, city, groupType, rhythm }
      localStorage.setItem('trip_meta', JSON.stringify(tripMeta))

      // Generate AI itinerary before navigating
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
              background: 'none', border: 'none', color: '#fff', opacity: 0.6,
              fontSize: 13, cursor: 'pointer', padding: 0, fontFamily: 'inherit',
            }}>← Назад</button>
            <span style={{
              fontFamily: 'monospace', fontSize: 11, color: 'rgba(255,255,255,0.5)',
              letterSpacing: '0.1em',
            }}>ШАГ 5 / 5</span>
          </div>
          <div style={{ height: 4, background: 'rgba(255,255,255,0.15)', borderRadius: 2, overflow: 'hidden' }}>
            <div style={{ height: '100%', width: '100%', background: '#b8ff4f', borderRadius: 2 }} />
          </div>
        </div>

        {/* Content */}
        <div style={{ padding: '28px 22px 24px' }}>
          <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.5)', marginBottom: 6, fontFamily: 'monospace' }}>
            ПОЧТИ ГОТОВО ✦
          </div>
          <h1 style={{
            fontSize: 28, fontWeight: 900, lineHeight: 1.15, textTransform: 'uppercase',
            color: '#fff', margin: '0 0 8px', fontFamily: 'inherit',
          }}>
            Зачем ты едешь<br/>в {cityName}?
          </h1>
          <p style={{
            fontSize: 13, color: 'rgba(255,255,255,0.55)', lineHeight: 1.5, margin: '0 0 20px',
            fontStyle: 'italic',
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
              background: 'rgba(255,255,255,0.08)',
              border: '1.5px solid rgba(255,255,255,0.18)',
              borderRadius: 14, resize: 'none', outline: 'none',
              fontFamily: 'inherit', fontSize: 15, lineHeight: 1.5,
              color: '#fff', boxSizing: 'border-box',
            }}
            onFocus={e => { e.target.style.borderColor = '#b8ff4f' }}
            onBlur={e => { e.target.style.borderColor = 'rgba(255,255,255,0.18)' }}
          />

          {text.length > 0 && (
            <div style={{
              marginTop: 10, padding: '10px 14px',
              background: 'rgba(184,255,79,0.1)',
              border: '1.5px solid rgba(184,255,79,0.3)',
              borderRadius: 10, fontSize: 12, color: '#b8ff4f', lineHeight: 1.4,
            }}>
              ✦ ИИ учтёт твой запрос при составлении маршрута
            </div>
          )}

          {/* API error */}
          {apiError && (
            <div style={{
              marginTop: 12, padding: '12px 14px',
              background: 'rgba(220,50,50,0.15)',
              border: '1.5px solid rgba(220,50,50,0.4)',
              borderRadius: 10, fontSize: 13, color: '#ff8080', lineHeight: 1.4,
            }}>
              {apiError}
            </div>
          )}
        </div>

        {/* Sticky CTA */}
        <div style={{
          position: 'sticky', bottom: 0,
          padding: '16px 22px 28px',
          background: 'linear-gradient(to top, #1a1f1a 75%, transparent)',
        }}>
          <button
            onClick={() => handleSubmit(text)}
            style={{
              width: '100%', height: 54,
              background: '#b8ff4f',
              border: '2px solid #1a1f1a',
              borderRadius: 14,
              fontWeight: 900, fontSize: 15, letterSpacing: '0.05em',
              textTransform: 'uppercase', color: '#1a1f1a',
              cursor: 'pointer',
              boxShadow: '4px 4px 0 0 rgba(184,255,79,0.3)',
              fontFamily: 'inherit',
            }}
          >
            ✦ Создать мой маршрут
          </button>
        </div>

      </div>
    </div>
  )
}
