import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './DashboardPage.css'

const API_BASE = 'http://localhost:8000'
function getToken() { return localStorage.getItem('access_token') ?? '' }

const MONTHS_RU = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
const BUDGET_LABEL  = { low: 'Экономно', medium: 'Комфортно', high: 'Люкс' }
const PURPOSE_LABEL = { leisure: 'Отдых', business: 'Работа', education: 'Учёба', other: 'Другое' }

function groupLabel(n) {
  if (n === 1) return 'Соло'
  if (n === 2) return 'Вдвоём'
  if (n <= 3) return 'Друзья'
  if (n <= 4) return 'Семья'
  return 'Группа'
}

function calcDays(start, end) {
  if (!start || !end) return null
  return Math.round((new Date(end) - new Date(start)) / 86400000) + 1
}

function formatDateRange(start, end) {
  if (!start) return null
  const s = new Date(start)
  const e = end ? new Date(end) : null
  if (e && s.getMonth() === e.getMonth() && s.getFullYear() === e.getFullYear()) {
    return `${s.getDate()}–${e.getDate()} ${MONTHS_RU[s.getMonth()]}`
  }
  if (e) {
    return `${s.getDate()} ${MONTHS_RU[s.getMonth()]} – ${e.getDate()} ${MONTHS_RU[e.getMonth()]}`
  }
  return `${s.getDate()} ${MONTHS_RU[s.getMonth()]}`
}

// ── Skeleton card ──────────────────────────────────────────

function SkeletonCard() {
  return (
    <div style={{ background: '#f5f0e8', borderRadius: 16, padding: '16px 18px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
        <div>
          <div className="dash-shimmer" style={{ width: 120, height: 20, borderRadius: 6, marginBottom: 7 }} />
          <div className="dash-shimmer" style={{ width: 70, height: 13, borderRadius: 4 }} />
        </div>
        <div className="dash-shimmer" style={{ width: 44, height: 28, borderRadius: 8 }} />
      </div>
      <div style={{ display: 'flex', gap: 6, marginBottom: 14 }}>
        <div className="dash-shimmer" style={{ width: 72, height: 22, borderRadius: 99 }} />
        <div className="dash-shimmer" style={{ width: 82, height: 22, borderRadius: 99 }} />
      </div>
      <div className="dash-shimmer" style={{ width: '65%', height: 13, borderRadius: 4 }} />
    </div>
  )
}

// ── Trip card ──────────────────────────────────────────────

function TripCard({ trip, meta, onClick }) {
  const days    = calcDays(trip.start_date, trip.end_date)
  const dateStr = formatDateRange(trip.start_date, trip.end_date)
  const city    = meta?.cityName ?? 'Маршрут'

  return (
    <div
      onClick={onClick}
      style={{
        background: '#f5f0e8', borderRadius: 16, padding: '16px 18px',
        cursor: 'pointer', border: '1.5px solid transparent',
        transition: 'border-color 0.15s',
      }}
      onMouseEnter={e => e.currentTarget.style.borderColor = '#b8ff4f'}
      onMouseLeave={e => e.currentTarget.style.borderColor = 'transparent'}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
        <div>
          <div style={{
            fontSize: 20, fontWeight: 900, textTransform: 'uppercase',
            color: '#1a1f1a', lineHeight: 1.1, letterSpacing: '-0.02em',
          }}>{city}</div>
          <div style={{ fontSize: 12, color: '#666', marginTop: 2 }}>
            {PURPOSE_LABEL[trip.purpose] ?? trip.purpose}
          </div>
        </div>
        {days && (
          <div style={{
            background: '#1a1f1a', color: '#b8ff4f',
            borderRadius: 8, padding: '4px 10px',
            fontSize: 11, fontWeight: 700, fontFamily: 'monospace', flexShrink: 0,
          }}>
            {days} дн
          </div>
        )}
      </div>

      <div style={{
        display: 'flex', gap: 6, flexWrap: 'wrap',
        fontFamily: 'monospace', fontSize: 10, color: '#555',
      }}>
        {[groupLabel(trip.group_size), BUDGET_LABEL[trip.budget] ?? trip.budget].map(tag => (
          <span key={tag} style={{
            padding: '3px 8px', background: 'rgba(26,31,26,0.07)',
            borderRadius: 99, border: '1px solid rgba(26,31,26,0.1)',
          }}>{tag}</span>
        ))}
      </div>

      <div style={{
        marginTop: 12, paddingTop: 10, borderTop: '1px solid rgba(26,31,26,0.1)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <span style={{ fontSize: 12, color: '#888' }}>
          {dateStr ?? new Date(trip.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })}
        </span>
        <span style={{ fontSize: 12, color: '#1a1f1a', fontWeight: 700 }}>Открыть →</span>
      </div>
    </div>
  )
}

// ── Main ───────────────────────────────────────────────────

export default function DashboardPage() {
  const navigate = useNavigate()
  const [trips, setTrips]     = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  const tripMeta = JSON.parse(localStorage.getItem('trip_meta') ?? '{}')

  useEffect(() => {
    fetch(`${API_BASE}/trips`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    })
      .then(r => {
        if (!r.ok) throw new Error(`Ошибка загрузки (${r.status})`)
        return r.json()
      })
      .then(data => { setTrips(data); setLoading(false) })
      .catch(err => { setError(err.message); setLoading(false) })
  }, [])

  function openTrip(trip) {
    localStorage.setItem('current_trip_id', trip.id)
    const meta = tripMeta[trip.id]
    if (meta) {
      localStorage.setItem('trip_display_data', JSON.stringify({
        city:      meta.city,
        groupType: meta.groupType,
        rhythm:    meta.rhythm,
      }))
    }
    navigate('/trip-plan')
  }

  return (
    <div className="dash-app">
      <div className="dash-phone">

        {/* Header */}
        <div style={{ padding: '28px 22px 20px' }}>
          <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.45)', fontFamily: 'monospace', letterSpacing: '0.12em', marginBottom: 8 }}>
            ✦ TOURRHYTHM
          </div>
          <h1 style={{
            fontSize: 32, fontWeight: 900, textTransform: 'uppercase',
            color: '#fff', margin: 0, lineHeight: 1.05, letterSpacing: '-0.02em',
          }}>
            Мои<br/>маршруты
          </h1>
        </div>

        {/* New trip CTA */}
        <div style={{ padding: '0 22px 24px' }}>
          <button
            onClick={() => navigate('/onboarding')}
            style={{
              width: '100%', height: 52,
              background: '#b8ff4f',
              border: '2px solid rgba(255,255,255,0.1)',
              borderRadius: 14,
              fontWeight: 900, fontSize: 14, letterSpacing: '0.05em',
              textTransform: 'uppercase', color: '#1a1f1a',
              cursor: 'pointer', fontFamily: 'inherit',
            }}
          >
            + Создать новый маршрут
          </button>
        </div>

        {/* Trips list */}
        <div style={{ padding: '0 22px', display: 'flex', flexDirection: 'column', gap: 12 }}>
          {loading ? (
            <>
              <div className="dash-shimmer" style={{ width: 130, height: 13, borderRadius: 4, marginBottom: 4 }} />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : error ? (
            <div style={{
              padding: '16px', borderRadius: 12,
              background: 'rgba(255,80,80,0.12)',
              border: '1px solid rgba(255,80,80,0.25)',
              fontSize: 13, color: '#ff8080', lineHeight: 1.5,
            }}>
              {error}
            </div>
          ) : trips.length === 0 ? (
            <div style={{
              padding: '40px 0', textAlign: 'center',
              color: 'rgba(255,255,255,0.35)', fontSize: 14, lineHeight: 1.6,
            }}>
              У вас пока нет сохранённых маршрутов.<br/>Создайте первый!
            </div>
          ) : (
            <>
              <div style={{
                fontSize: 11, color: 'rgba(255,255,255,0.45)',
                fontFamily: 'monospace', letterSpacing: '0.1em', marginBottom: 4,
              }}>
                СОХРАНЁННЫЕ · {trips.length}
              </div>
              {trips.map(trip => (
                <TripCard
                  key={trip.id}
                  trip={trip}
                  meta={tripMeta[trip.id]}
                  onClick={() => openTrip(trip)}
                />
              ))}
            </>
          )}
        </div>

        {/* Logout */}
        <div style={{ padding: '32px 22px 40px', textAlign: 'center' }}>
          <button
            onClick={() => {
              localStorage.removeItem('access_token')
              navigate('/')
            }}
            style={{
              background: 'none', border: 'none',
              color: 'rgba(255,255,255,0.35)', fontSize: 13,
              cursor: 'pointer', textDecoration: 'underline',
              fontFamily: 'inherit',
            }}
          >
            Выйти из аккаунта
          </button>
        </div>

      </div>
    </div>
  )
}
