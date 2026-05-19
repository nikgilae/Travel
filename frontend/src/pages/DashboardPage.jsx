import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import './DashboardPage.css'

const API_BASE = import.meta.env.VITE_API_URL
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

// ── Icons ──────────────────────────────────────────────────────────────────────

const TrashIcon = () => (
  <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
    <path d="M2 4h10M5 4V2.5h4V4M5.5 6.5v4M8.5 6.5v4M3 4l.8 7.2A1 1 0 0 0 4.8 12h4.4a1 1 0 0 0 1-.8L11 4"
      stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

// ── Skeleton card ──────────────────────────────────────────────────────────────

function SkeletonCard() {
  return (
    <div style={{ background: '#FFFFFF', borderRadius: 14, padding: '16px 18px', boxShadow: '0 0 0 1px #E8EAEC' }}>
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

// ── Trip card ──────────────────────────────────────────────────────────────────

function TripCard({ trip, meta, onClick, onDelete, isDeleting }) {
  const days    = calcDays(trip.start_date, trip.end_date)
  const dateStr = formatDateRange(trip.start_date, trip.end_date)
  const city    = meta?.cityName ?? 'Маршрут'

  return (
    <div
      onClick={onClick}
      style={{
        background: '#FFFFFF', borderRadius: 14, padding: '16px 18px',
        cursor: 'pointer', border: '1px solid #E8EAEC',
        transition: 'border-color 0.15s, opacity 0.3s, transform 0.3s',
        opacity: isDeleting ? 0 : 1,
        transform: isDeleting ? 'translateX(16px)' : 'none',
        pointerEvents: isDeleting ? 'none' : 'auto',
      }}
      onMouseEnter={e => { if (!isDeleting) e.currentTarget.style.borderColor = '#B9FF3D' }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = '#E8EAEC' }}
    >
      {/* Top row: city + days badge */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
        <div>
          <div style={{
            fontSize: 18, fontWeight: 600,
            color: '#0A0B0C', lineHeight: 1.2, letterSpacing: '-0.01em',
          }}>{city}</div>
          <div style={{ fontSize: 12, color: '#5B6066', marginTop: 2 }}>
            {PURPOSE_LABEL[trip.purpose] ?? trip.purpose}
          </div>
        </div>
        {days && (
          <div style={{
            background: '#0A0B0C', color: '#B9FF3D',
            borderRadius: 6, padding: '3px 8px',
            fontSize: 11, fontWeight: 500, fontFamily: 'var(--font-mono)', flexShrink: 0,
          }}>
            {days} дн
          </div>
        )}
      </div>

      {/* Tags */}
      <div style={{
        display: 'flex', gap: 6, flexWrap: 'wrap',
        fontFamily: 'var(--font-mono)', fontSize: 10, color: '#5B6066',
      }}>
        {[groupLabel(trip.group_size), BUDGET_LABEL[trip.budget] ?? trip.budget].map(tag => (
          <span key={tag} style={{
            padding: '3px 8px', background: '#F1F3F5',
            borderRadius: 99, border: '1px solid #E8EAEC',
          }}>{tag}</span>
        ))}
      </div>

      {/* Footer row: date + delete + open */}
      <div style={{
        marginTop: 12, paddingTop: 10, borderTop: '1px solid #E8EAEC',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <span style={{ fontSize: 12, color: '#9097A0' }}>
          {dateStr ?? new Date(trip.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <button
            onClick={e => { e.stopPropagation(); onDelete(trip.id, city) }}
            title="Удалить маршрут"
            style={{
              width: 26, height: 26, borderRadius: '50%',
              background: 'transparent',
              border: '1px solid #E8EAEC',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', color: '#9097A0',
              transition: 'background 0.15s, color 0.15s, border-color 0.15s',
              flexShrink: 0,
            }}
            onMouseEnter={e => {
              e.currentTarget.style.background     = '#FBE5E7'
              e.currentTarget.style.color          = '#B43340'
              e.currentTarget.style.borderColor    = 'rgba(180,51,64,0.3)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background     = 'transparent'
              e.currentTarget.style.color          = '#9097A0'
              e.currentTarget.style.borderColor    = '#E8EAEC'
            }}
          >
            <TrashIcon />
          </button>
          <span style={{ fontSize: 12, color: '#0A0B0C', fontWeight: 600 }}>Открыть →</span>
        </div>
      </div>
    </div>
  )
}

// ── Confirm delete modal ───────────────────────────────────────────────────────

function ConfirmDeleteModal({ cityName, onCancel, onConfirm, loading }) {
  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 200,
      background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '0 24px',
    }}>
      <div style={{
        background: '#FFFFFF', border: '1px solid #E8EAEC',
        borderRadius: 20, padding: '24px 22px',
        width: '100%', maxWidth: 360,
        boxShadow: '0 8px 28px -10px rgba(15,20,30,.18), 0 0 0 1px rgba(15,20,30,.04)',
      }}>
        <div style={{
          fontFamily: 'var(--font-ui)', fontWeight: 600, fontSize: 17,
          color: '#0A0B0C', marginBottom: 10,
          letterSpacing: '-0.005em',
        }}>
          Удалить маршрут?
        </div>
        <div style={{
          fontSize: 13, color: '#5B6066', lineHeight: 1.55,
          fontFamily: 'var(--font-ui)', marginBottom: 22,
        }}>
          Маршрут «{cityName}» будет удалён без возможности восстановления.
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button
            onClick={onCancel}
            disabled={loading}
            style={{
              flex: 1, height: 44,
              background: 'transparent',
              border: '1px solid #E8EAEC',
              borderRadius: 10, cursor: 'pointer',
              color: '#5B6066',
              fontFamily: 'var(--font-ui)',
              fontWeight: 500, fontSize: 13, letterSpacing: 0,
            }}
          >
            Отмена
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            style={{
              flex: 1, height: 44,
              background: loading ? '#FBE5E7' : '#B43340',
              border: '1px solid transparent',
              borderRadius: 10, cursor: loading ? 'wait' : 'pointer',
              color: '#fff',
              fontFamily: 'var(--font-ui)',
              fontWeight: 500, fontSize: 13, letterSpacing: 0,
              transition: 'background 0.15s',
            }}
          >
            {loading ? '...' : 'Удалить'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Profile button ─────────────────────────────────────────────────────────────

function ProfileButton({ onLogout }) {
  const [open, setOpen] = useState(false)
  const ref   = useRef(null)
  const email = localStorage.getItem('user_email') ?? ''
  const letter = email ? email[0].toUpperCase() : '?'

  useEffect(() => {
    if (!open) return
    function handleClick(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  return (
    <div ref={ref} style={{ position: 'relative', flexShrink: 0 }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          width: 36, height: 36, borderRadius: '50%',
          background: open ? '#B9FF3D' : '#F1F3F5',
          border: '1px solid ' + (open ? '#B9FF3D' : '#E8EAEC'),
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', transition: 'background 0.15s, border-color 0.15s',
          color: '#0A0B0C',
          fontFamily: 'var(--font-ui)',
          fontWeight: 600, fontSize: 14, letterSpacing: 0,
        }}
      >
        {letter}
      </button>

      {open && (
        <div style={{
          position: 'absolute', top: 44, right: 0,
          background: '#FFFFFF', border: '1px solid #E8EAEC',
          borderRadius: 14, padding: '14px 16px',
          minWidth: 210, zIndex: 100,
          boxShadow: '0 8px 28px -10px rgba(15,20,30,.18), 0 0 0 1px rgba(15,20,30,.04)',
        }}>
          <div style={{
            fontSize: 10, color: '#9097A0',
            fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.1em',
            marginBottom: 6, textTransform: 'uppercase',
          }}>
            Аккаунт
          </div>
          <div style={{
            fontSize: 13, color: '#0A0B0C', fontWeight: 500,
            marginBottom: 14, wordBreak: 'break-all', lineHeight: 1.3,
            fontFamily: 'Onest, sans-serif',
          }}>
            {email || '—'}
          </div>
          <div style={{ height: 1, background: '#E8EAEC', marginBottom: 12 }} />
          <button
            onClick={() => { setOpen(false); onLogout() }}
            style={{
              width: '100%', height: 36,
              background: 'rgba(200,85,61,0.12)',
              border: '1px solid rgba(200,85,61,0.3)',
              borderRadius: 8, cursor: 'pointer',
              color: '#e87460', fontSize: 12, fontWeight: 700,
              letterSpacing: '0.05em',
              fontFamily: 'Onest, sans-serif',
            }}
          >
            Выйти
          </button>
        </div>
      )}
    </div>
  )
}

// ── Main ───────────────────────────────────────────────────────────────────────

export default function DashboardPage() {
  const navigate = useNavigate()

  const [trips,   setTrips]   = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)

  // Delete state
  const [confirmDelete, setConfirmDelete] = useState(null) // { tripId, cityName }
  const [deletingId,    setDeletingId]    = useState(null) // animating out
  const [deleteLoading, setDeleteLoading] = useState(false)

  const tripMeta = JSON.parse(localStorage.getItem('trip_meta') ?? '{}')

  useEffect(() => {
    fetch(`${API_BASE}/trips`, { headers: { Authorization: `Bearer ${getToken()}` } })
      .then(r => { if (!r.ok) throw new Error(`Ошибка загрузки (${r.status})`); return r.json() })
      .then(data => { setTrips(data); setLoading(false) })
      .catch(err => { setError(err.message); setLoading(false) })
  }, [])

  function openTrip(trip) {
    const meta = tripMeta[trip.id]
    navigate(`/trip/${trip.id}/plan`, {
      state: {
        city:      meta?.city      ?? null,
        groupType: meta?.groupType ?? null,
        rhythm:    meta?.rhythm    ?? null,
      },
    })
  }

  function requestDelete(tripId, cityName) {
    setConfirmDelete({ tripId, cityName })
  }

  async function confirmDeleteAction() {
    const { tripId } = confirmDelete
    setDeleteLoading(true)
    try {
      const res = await fetch(`${API_BASE}/trips/${tripId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${getToken()}` },
      })
      if (!res.ok && res.status !== 404) throw new Error(res.status)

      setConfirmDelete(null)
      setDeleteLoading(false)
      setDeletingId(tripId)

      // Let the fade-out animate, then remove from list
      setTimeout(() => {
        setTrips(prev => prev.filter(t => t.id !== tripId))
        setDeletingId(null)
      }, 320)
    } catch {
      setDeleteLoading(false)
      setConfirmDelete(null)
    }
  }

  return (
    <>
      {/* ── Header ── */}
      <div style={{ padding: '28px 22px 20px' }}>
        <div style={{
          display: 'flex', alignItems: 'flex-start',
          justifyContent: 'space-between', marginBottom: 8,
        }}>
          <div style={{
            fontSize: 11, color: '#9097A0',
            fontFamily: 'var(--font-mono)', letterSpacing: '0.14em', textTransform: 'uppercase',
          }}>
            TOURRHYTHM
          </div>
          <ProfileButton onLogout={() => {
            localStorage.removeItem('access_token')
            localStorage.removeItem('user_email')
            navigate('/')
          }} />
        </div>
        <h1 style={{
          fontSize: 28, fontWeight: 600,
          color: '#0A0B0C', margin: 0, lineHeight: 1.15, letterSpacing: '-0.012em',
          fontFamily: 'var(--font-ui)',
        }}>
          Мои<br/>маршруты
        </h1>
      </div>

      {/* ── New trip CTA ── */}
      <div style={{ padding: '0 22px 24px' }}>
        <button
          onClick={() => navigate('/onboarding')}
          style={{
            width: '100%', height: 52,
            background: '#B9FF3D',
            border: '1px solid #B9FF3D',
            borderRadius: 10,
            fontWeight: 500, fontSize: 14, letterSpacing: '-0.005em',
            color: '#0A0B0C',
            cursor: 'pointer', fontFamily: 'var(--font-ui)',
          }}
        >
          + Создать маршрут
        </button>
      </div>

      {/* ── Trips list ── */}
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
            background: '#FBE5E7',
            border: '1px solid rgba(180,51,64,0.25)',
            fontSize: 13, color: '#B43340', lineHeight: 1.5,
            fontFamily: 'var(--font-ui)',
          }}>
            {error}
          </div>
        ) : trips.length === 0 ? (
          // ── Empty state ──
          <div style={{ padding: '36px 0 20px', textAlign: 'center' }}>
            <div style={{ fontSize: 40, marginBottom: 16 }}>🗺️</div>
            <div style={{
              fontFamily: 'var(--font-ui)', fontWeight: 600, fontSize: 22,
              color: '#0A0B0C',
              lineHeight: 1.15, letterSpacing: '-0.012em', marginBottom: 10,
            }}>
              Пока пусто
            </div>
            <div style={{
              fontSize: 13, color: '#5B6066',
              fontFamily: 'var(--font-ui)', lineHeight: 1.55,
              marginBottom: 28, maxWidth: 240, margin: '0 auto 28px',
            }}>
              Создай первый маршрут или спроси AI-чат о любой стране
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <button
                onClick={() => navigate('/onboarding')}
                style={{
                  height: 48,
                  background: '#B9FF3D', color: '#0A0B0C',
                  border: '1px solid #B9FF3D', borderRadius: 10,
                  fontFamily: 'var(--font-ui)',
                  fontWeight: 500, fontSize: 14, letterSpacing: '-0.005em',
                  cursor: 'pointer',
                }}
              >
                Создать маршрут
              </button>
              <button
                onClick={() => navigate('/dashboard/chat')}
                style={{
                  height: 48,
                  background: 'transparent', color: '#0A0B0C',
                  border: '1px solid #E8EAEC', borderRadius: 10,
                  fontFamily: 'var(--font-ui)',
                  fontWeight: 500, fontSize: 14, letterSpacing: '-0.005em',
                  cursor: 'pointer',
                }}
              >
                Открыть чат
              </button>
            </div>
          </div>
        ) : (
          <>
            <div style={{
              fontSize: 11, color: '#9097A0',
              fontFamily: 'var(--font-mono)', letterSpacing: '0.14em', marginBottom: 4,
            }}>
              СОХРАНЁННЫЕ · {trips.length}
            </div>
            {trips.map(trip => (
              <TripCard
                key={trip.id}
                trip={trip}
                meta={tripMeta[trip.id]}
                onClick={() => openTrip(trip)}
                onDelete={requestDelete}
                isDeleting={deletingId === trip.id}
              />
            ))}
          </>
        )}
      </div>

      <div style={{ height: 24 }} />

      {/* ── Confirm delete modal ── */}
      {confirmDelete && (
        <ConfirmDeleteModal
          cityName={confirmDelete.cityName}
          loading={deleteLoading}
          onCancel={() => { if (!deleteLoading) setConfirmDelete(null) }}
          onConfirm={confirmDeleteAction}
        />
      )}
    </>
  )
}
