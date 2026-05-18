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

// ── Trip card ──────────────────────────────────────────────────────────────────

function TripCard({ trip, meta, onClick, onDelete, isDeleting }) {
  const days    = calcDays(trip.start_date, trip.end_date)
  const dateStr = formatDateRange(trip.start_date, trip.end_date)
  const city    = meta?.cityName ?? 'Маршрут'

  return (
    <div
      onClick={onClick}
      style={{
        background: '#f5f0e8', borderRadius: 16, padding: '16px 18px',
        cursor: 'pointer', border: '1.5px solid transparent',
        transition: 'border-color 0.15s, opacity 0.3s, transform 0.3s',
        opacity: isDeleting ? 0 : 1,
        transform: isDeleting ? 'translateX(16px)' : 'none',
        pointerEvents: isDeleting ? 'none' : 'auto',
      }}
      onMouseEnter={e => { if (!isDeleting) e.currentTarget.style.borderColor = '#b8ff4f' }}
      onMouseLeave={e => { e.currentTarget.style.borderColor = 'transparent' }}
    >
      {/* Top row: city + days badge */}
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

      {/* Tags */}
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

      {/* Footer row: date + delete + open */}
      <div style={{
        marginTop: 12, paddingTop: 10, borderTop: '1px solid rgba(26,31,26,0.1)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <span style={{ fontSize: 12, color: '#888' }}>
          {dateStr ?? new Date(trip.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', year: 'numeric' })}
        </span>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <button
            onClick={e => { e.stopPropagation(); onDelete(trip.id, city) }}
            title="Удалить маршрут"
            style={{
              width: 26, height: 26, borderRadius: '50%',
              background: 'transparent',
              border: '1px solid rgba(26,31,26,0.15)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', color: 'rgba(26,31,26,0.3)',
              transition: 'background 0.15s, color 0.15s, border-color 0.15s',
              flexShrink: 0,
            }}
            onMouseEnter={e => {
              e.currentTarget.style.background     = 'rgba(200,85,61,0.1)'
              e.currentTarget.style.color          = '#c8553d'
              e.currentTarget.style.borderColor    = 'rgba(200,85,61,0.35)'
            }}
            onMouseLeave={e => {
              e.currentTarget.style.background     = 'transparent'
              e.currentTarget.style.color          = 'rgba(26,31,26,0.3)'
              e.currentTarget.style.borderColor    = 'rgba(26,31,26,0.15)'
            }}
          >
            <TrashIcon />
          </button>
          <span style={{ fontSize: 12, color: '#1a1f1a', fontWeight: 700 }}>Открыть →</span>
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
        background: '#1a1f1a', border: '1.5px solid rgba(255,255,255,0.1)',
        borderRadius: 20, padding: '24px 22px',
        width: '100%', maxWidth: 360,
        boxShadow: '0 24px 64px rgba(0,0,0,0.5)',
      }}>
        <div style={{
          fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 17,
          textTransform: 'uppercase', color: '#fff', marginBottom: 10,
          letterSpacing: '-0.01em',
        }}>
          Удалить маршрут?
        </div>
        <div style={{
          fontSize: 13, color: 'rgba(255,255,255,0.5)', lineHeight: 1.55,
          fontFamily: 'JetBrains Mono, monospace', marginBottom: 22,
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
              border: '1.5px solid rgba(255,255,255,0.15)',
              borderRadius: 10, cursor: 'pointer',
              color: 'rgba(255,255,255,0.6)',
              fontFamily: 'Archivo, sans-serif',
              fontWeight: 700, fontSize: 12, letterSpacing: '0.04em',
            }}
          >
            ОТМЕНА
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            style={{
              flex: 1, height: 44,
              background: loading ? 'rgba(200,85,61,0.4)' : 'rgba(200,85,61,0.85)',
              border: '1.5px solid rgba(200,85,61,0.5)',
              borderRadius: 10, cursor: loading ? 'wait' : 'pointer',
              color: '#fff',
              fontFamily: 'Archivo, sans-serif',
              fontWeight: 800, fontSize: 12, letterSpacing: '0.04em',
              transition: 'background 0.15s',
            }}
          >
            {loading ? '...' : 'УДАЛИТЬ'}
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
          background: open ? '#b8ff4f' : 'rgba(184,255,79,0.15)',
          border: '1.5px solid rgba(184,255,79,0.35)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          cursor: 'pointer', transition: 'background 0.15s, border-color 0.15s',
          color: open ? '#1a1f1a' : '#b8ff4f',
          fontFamily: 'Archivo, sans-serif',
          fontWeight: 900, fontSize: 14, letterSpacing: 0,
        }}
      >
        {letter}
      </button>

      {open && (
        <div style={{
          position: 'absolute', top: 44, right: 0,
          background: '#1a1f1a', border: '1.5px solid rgba(255,255,255,0.12)',
          borderRadius: 14, padding: '14px 16px',
          minWidth: 210, zIndex: 100,
          boxShadow: '0 8px 32px rgba(0,0,0,0.45)',
        }}>
          <div style={{
            fontSize: 10, color: 'rgba(255,255,255,0.38)',
            fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.1em',
            marginBottom: 6, textTransform: 'uppercase',
          }}>
            Аккаунт
          </div>
          <div style={{
            fontSize: 13, color: '#fff', fontWeight: 600,
            marginBottom: 14, wordBreak: 'break-all', lineHeight: 1.3,
            fontFamily: 'Inter, sans-serif',
          }}>
            {email || '—'}
          </div>
          <div style={{ height: 1, background: 'rgba(255,255,255,0.08)', marginBottom: 12 }} />
          <button
            onClick={() => { setOpen(false); onLogout() }}
            style={{
              width: '100%', height: 36,
              background: 'rgba(200,85,61,0.12)',
              border: '1px solid rgba(200,85,61,0.3)',
              borderRadius: 8, cursor: 'pointer',
              color: '#e87460', fontSize: 12, fontWeight: 700,
              letterSpacing: '0.05em',
              fontFamily: 'Archivo, sans-serif',
            }}
          >
            ВЫЙТИ
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
            fontSize: 11, color: 'rgba(255,255,255,0.45)',
            fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.12em',
          }}>
            ✦ TOURRHYTHM
          </div>
          <ProfileButton onLogout={() => {
            localStorage.removeItem('access_token')
            localStorage.removeItem('user_email')
            navigate('/')
          }} />
        </div>
        <h1 style={{
          fontSize: 32, fontWeight: 900, textTransform: 'uppercase',
          color: '#fff', margin: 0, lineHeight: 1.05, letterSpacing: '-0.02em',
          fontFamily: 'Archivo, sans-serif',
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
            background: '#b8ff4f',
            border: '2px solid rgba(255,255,255,0.1)',
            borderRadius: 14,
            fontWeight: 900, fontSize: 14, letterSpacing: '0.05em',
            textTransform: 'uppercase', color: '#1a1f1a',
            cursor: 'pointer', fontFamily: 'Archivo, sans-serif',
          }}
        >
          + Создать новый маршрут
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
            background: 'rgba(255,80,80,0.12)',
            border: '1px solid rgba(255,80,80,0.25)',
            fontSize: 13, color: '#ff8080', lineHeight: 1.5,
            fontFamily: 'JetBrains Mono, monospace',
          }}>
            {error}
          </div>
        ) : trips.length === 0 ? (
          // ── Empty state ──
          <div style={{ padding: '36px 0 20px', textAlign: 'center' }}>
            <div style={{ fontSize: 40, marginBottom: 16 }}>🗺️</div>
            <div style={{
              fontFamily: 'Archivo, sans-serif', fontWeight: 900, fontSize: 22,
              textTransform: 'uppercase', color: '#fff',
              lineHeight: 1, letterSpacing: '-0.02em', marginBottom: 10,
            }}>
              Пока пусто
            </div>
            <div style={{
              fontSize: 12, color: 'rgba(255,255,255,0.42)',
              fontFamily: 'JetBrains Mono, monospace', lineHeight: 1.65,
              marginBottom: 28, maxWidth: 240, margin: '0 auto 28px',
            }}>
              Создай первый маршрут или спроси AI-чат о любой стране
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <button
                onClick={() => navigate('/onboarding')}
                style={{
                  height: 48,
                  background: '#b8ff4f', color: '#1a1f1a',
                  border: 'none', borderRadius: 12,
                  fontFamily: 'Archivo, sans-serif',
                  fontWeight: 900, fontSize: 13, letterSpacing: '0.05em',
                  textTransform: 'uppercase', cursor: 'pointer',
                }}
              >
                СОЗДАТЬ МАРШРУТ
              </button>
              <button
                onClick={() => navigate('/dashboard/chat')}
                style={{
                  height: 48,
                  background: 'transparent', color: 'rgba(255,255,255,0.65)',
                  border: '1.5px solid rgba(255,255,255,0.14)', borderRadius: 12,
                  fontFamily: 'Archivo, sans-serif',
                  fontWeight: 700, fontSize: 13, letterSpacing: '0.05em',
                  textTransform: 'uppercase', cursor: 'pointer',
                }}
              >
                ОТКРЫТЬ ЧАТ
              </button>
            </div>
          </div>
        ) : (
          <>
            <div style={{
              fontSize: 11, color: 'rgba(255,255,255,0.45)',
              fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.1em', marginBottom: 4,
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
