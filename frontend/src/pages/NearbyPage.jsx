import { useState, useEffect, useCallback, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import './NearbyPage.css'

const API_BASE = 'http://localhost:8000'
function getToken() { return localStorage.getItem('access_token') ?? '' }

const TR = {
  bg:       '#f1ede0',
  surface:  '#fbf7ea',
  surface2: '#e8e2cf',
  fg:       '#0d2818',
  fgMute:   '#5e6e58',
  hairline: 'rgba(13,40,24,0.12)',
  lime:     '#b9ff3d',
  limeText: '#3d6600',
  warn:     '#c8553d',
}

// ── Filter → Google Places type ────────────────────────────────────────────────

const FILTERS = [
  { key: 'all',           label: 'Все',         emoji: '🗺️', type: null },
  { key: 'food',          label: 'Поесть',      emoji: '🍽️', type: 'restaurant' },
  { key: 'culture',       label: 'Культура',    emoji: '🏛️', type: 'museum' },
  { key: 'walk',          label: 'Погулять',    emoji: '🌳', type: 'park' },
  { key: 'coffee',        label: 'Кофе',        emoji: '☕', type: 'cafe' },
  { key: 'shopping',      label: 'Шоппинг',     emoji: '🛍️', type: 'shopping_mall' },
  { key: 'entertainment', label: 'Развлечения', emoji: '🎭', type: 'night_club' },
]

// Human-readable label for the first meaningful Google Places type
const TYPE_LABELS = {
  restaurant: 'Ресторан', cafe: 'Кафе', bar: 'Бар', bakery: 'Пекарня',
  museum: 'Музей', art_gallery: 'Галерея', church: 'Церковь',
  tourist_attraction: 'Достопримечательность', stadium: 'Стадион',
  park: 'Парк', natural_feature: 'Природа',
  shopping_mall: 'ТЦ', store: 'Магазин', supermarket: 'Супермаркет',
  night_club: 'Ночной клуб', movie_theater: 'Кинотеатр',
  amusement_park: 'Парк аттракционов', bowling_alley: 'Боулинг',
  lodging: 'Отель', hospital: 'Больница', pharmacy: 'Аптека',
  bank: 'Банк', atm: 'Банкомат', gas_station: 'АЗС',
  gym: 'Спортзал', spa: 'Спа',
}

function placeTypeLabel(types = []) {
  const skip = new Set(['point_of_interest', 'establishment', 'food', 'premise'])
  const t = types.find(t => !skip.has(t))
  return t ? (TYPE_LABELS[t] ?? t.replace(/_/g, ' ')) : 'Место'
}

// ── Distance helpers ──────────────────────────────────────────────────────────

function haversineM(lat1, lon1, lat2, lon2) {
  const R = 6371000
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function fmtDist(m) {
  return m < 1000 ? `${Math.round(m)} м` : `${(m / 1000).toFixed(1)} км`
}

// ── Icons ──────────────────────────────────────────────────────────────────────

const RefreshIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M13.5 8A5.5 5.5 0 1 1 10.5 3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
    <path d="M13.5 3v3h-3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

// ── Sub-components ─────────────────────────────────────────────────────────────

function SkeletonCard() {
  return (
    <div className="nearby-skeleton" style={{
      background: TR.surface, borderRadius: 16,
      border: `1px solid ${TR.hairline}`, padding: '16px',
    }}>
      <div style={{ height: 14, width: '55%', background: TR.surface2, borderRadius: 6, marginBottom: 7 }} />
      <div style={{ height: 11, width: '38%', background: TR.surface2, borderRadius: 6, marginBottom: 6 }} />
      <div style={{ height: 10, width: '60%', background: TR.surface2, borderRadius: 6, marginBottom: 14 }} />
      <div style={{ display: 'flex', gap: 8 }}>
        <div style={{ height: 30, width: 80, background: TR.surface2, borderRadius: 8 }} />
        <div style={{ height: 30, width: 80, background: TR.surface2, borderRadius: 8 }} />
      </div>
    </div>
  )
}

function StarRating({ rating }) {
  if (!rating) return null
  return (
    <span style={{ color: '#b8860b', fontSize: 11, fontFamily: 'JetBrains Mono, monospace' }}>
      ★ {rating.toFixed(1)}
    </span>
  )
}

function PlaceCard({ place, userPos, tripId }) {
  const navigate = useNavigate()
  const lat = place.geometry?.location?.lat
  const lng = place.geometry?.location?.lng
  const dist = userPos && lat != null ? haversineM(userPos.lat, userPos.lon, lat, lng) : null
  const isOpen = place.opening_hours?.open_now
  const typeLabel = placeTypeLabel(place.types)
  const mapsUrl = `https://www.google.com/maps/place/?q=place_id:${place.place_id}`

  return (
    <div style={{
      background: TR.surface, borderRadius: 16,
      border: `1px solid ${TR.hairline}`,
      padding: '14px 16px',
      boxShadow: '0 1px 6px rgba(13,40,24,0.05)',
    }}>
      {/* Title + distance */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, marginBottom: 4 }}>
        <div style={{
          flex: 1, fontFamily: 'Archivo, sans-serif',
          fontWeight: 800, fontSize: 14, color: TR.fg, lineHeight: 1.25,
        }}>
          {place.name}
        </div>
        {dist != null && (
          <span style={{
            flexShrink: 0, fontSize: 10, fontWeight: 700,
            fontFamily: 'JetBrains Mono, monospace',
            color: TR.limeText,
            background: 'rgba(185,255,61,0.22)',
            padding: '2px 7px', borderRadius: 99, marginTop: 1,
          }}>
            {fmtDist(dist)}
          </span>
        )}
      </div>

      {/* Type · rating · open status */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 8,
        fontSize: 11, color: TR.fgMute,
        fontFamily: 'JetBrains Mono, monospace',
        letterSpacing: '0.03em', marginBottom: 6, flexWrap: 'wrap',
      }}>
        <span>{typeLabel}</span>
        {place.rating && <><span style={{ opacity: 0.4 }}>·</span><StarRating rating={place.rating} /></>}
        {place.opening_hours != null && (
          <>
            <span style={{ opacity: 0.4 }}>·</span>
            <span style={{ color: isOpen ? '#4a7c59' : TR.warn }}>
              {isOpen ? 'Открыто' : 'Закрыто'}
            </span>
          </>
        )}
      </div>

      {/* Vicinity */}
      {place.vicinity && (
        <div style={{
          fontSize: 11, color: TR.fgMute,
          fontFamily: 'Inter, sans-serif', lineHeight: 1.4,
          marginBottom: 12,
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>
          {place.vicinity}
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 8 }}>
        <a
          href={mapsUrl}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            padding: '6px 14px', borderRadius: 8,
            fontSize: 11, fontFamily: 'Archivo, sans-serif',
            fontWeight: 800, letterSpacing: '0.04em',
            border: `1.5px solid ${TR.fg}`,
            background: TR.lime, color: TR.fg,
            textDecoration: 'none', display: 'inline-block',
            lineHeight: '18px',
          }}
        >
          ОТКРЫТЬ ↗
        </a>

        {tripId && (
          <button
            onClick={() => navigate(`/trip/${tripId}/chat`, {
              state: { prefill: `Добавь "${place.name}" в мой маршрут` },
            })}
            style={{
              padding: '6px 14px', borderRadius: 8,
              fontSize: 11, fontFamily: 'Archivo, sans-serif',
              fontWeight: 700, letterSpacing: '0.04em',
              border: `1.5px solid ${TR.hairline}`,
              background: 'transparent', color: TR.fgMute, cursor: 'pointer',
            }}
          >
            В ЧАТ →
          </button>
        )}
      </div>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────────────────────────

export default function NearbyPage() {
  const { id: tripId } = useParams()

  const [filter,    setFilter]    = useState('all')
  const [geoStatus, setGeoStatus] = useState('idle')
  const [userPos,   setUserPos]   = useState(null)   // { lat, lon }
  const [places,    setPlaces]    = useState([])
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState(null)

  const abortRef = useRef(null)

  // ── Geolocation ─────────────────────────────────────────────────────────────

  const requestGeo = useCallback(() => {
    if (!navigator.geolocation) { setGeoStatus('denied'); return }
    setGeoStatus('requesting')
    navigator.geolocation.getCurrentPosition(
      pos => {
        setUserPos({ lat: pos.coords.latitude, lon: pos.coords.longitude })
        setGeoStatus('ok')
      },
      () => setGeoStatus('denied'),
      { timeout: 10000, maximumAge: 60000 },
    )
  }, [])

  useEffect(() => { requestGeo() }, []) // eslint-disable-line

  // ── Fetch from Google Places via backend proxy ───────────────────────────────

  const fetchPlaces = useCallback(async (pos, filterKey) => {
    abortRef.current?.abort()
    const ctrl = new AbortController()
    abortRef.current = ctrl

    setLoading(true)
    setError(null)

    const activeFilter = FILTERS.find(f => f.key === filterKey)
    const url = new URL(`${API_BASE}/places/nearby`)
    url.searchParams.set('lat', pos.lat)
    url.searchParams.set('lon', pos.lon)
    url.searchParams.set('radius', 1000)
    if (activeFilter?.type) url.searchParams.set('type', activeFilter.type)

    try {
      const res = await fetch(url.toString(), {
        headers: { Authorization: `Bearer ${getToken()}` },
        signal: ctrl.signal,
      })
      if (!res.ok) throw new Error(res.status)
      setPlaces(await res.json())
    } catch (e) {
      if (e.name !== 'AbortError')
        setError('Не удалось загрузить места. Проверь соединение.')
    } finally {
      setLoading(false)
    }
  }, [])

  // Re-fetch when geo ready or filter changes
  useEffect(() => {
    if (geoStatus === 'ok' && userPos) fetchPlaces(userPos, filter)
  }, [geoStatus, userPos, filter]) // eslint-disable-line

  function handleRefresh() {
    if (geoStatus === 'denied') { requestGeo(); return }
    if (userPos) fetchPlaces(userPos, filter)
  }

  // Sort by distance
  const sorted = [...places].sort((a, b) => {
    if (!userPos) return 0
    const la = a.geometry?.location, lb = b.geometry?.location
    if (!la || !lb) return 0
    return haversineM(userPos.lat, userPos.lon, la.lat, la.lng)
         - haversineM(userPos.lat, userPos.lon, lb.lat, lb.lng)
  })

  // ── Render ───────────────────────────────────────────────────────────────────

  return (
    <div style={{
      display: 'flex', flexDirection: 'column',
      height: '100%', minHeight: 'calc(100svh - 64px)',
      background: TR.bg,
    }}>

      {/* ── Header ── */}
      <div style={{
        padding: '18px 22px 12px',
        borderBottom: `1px solid ${TR.hairline}`,
        display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between',
        flexShrink: 0,
      }}>
        <div>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
            letterSpacing: '0.2em', color: TR.fgMute,
            textTransform: 'uppercase', marginBottom: 4,
          }}>
            РЯДОМ С ВАМИ
          </div>
          <div style={{
            fontFamily: 'Archivo, sans-serif', fontWeight: 900,
            fontSize: 26, letterSpacing: '-0.03em',
            color: TR.fg, textTransform: 'uppercase', lineHeight: 1,
          }}>
            Что рядом?
          </div>
        </div>

        <button
          onClick={handleRefresh}
          disabled={loading || geoStatus === 'requesting'}
          title="Обновить"
          style={{
            width: 36, height: 36, borderRadius: '50%',
            background: 'transparent', border: `1.5px solid ${TR.hairline}`,
            color: TR.fgMute, cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            opacity: loading || geoStatus === 'requesting' ? 0.4 : 1,
            transition: 'opacity 0.15s',
          }}
        >
          <RefreshIcon />
        </button>
      </div>

      {/* ── Filter chips ── */}
      <div
        className="nearby-chips"
        style={{
          display: 'flex', gap: 6, overflowX: 'auto',
          padding: '10px 22px', flexShrink: 0,
          borderBottom: `1px solid ${TR.hairline}`,
        }}
      >
        {FILTERS.map(f => {
          const active = filter === f.key
          return (
            <button
              key={f.key}
              onClick={() => setFilter(f.key)}
              style={{
                flexShrink: 0, padding: '7px 14px', borderRadius: 99,
                cursor: 'pointer',
                border: `1.5px solid ${active ? TR.fg : TR.hairline}`,
                background: active ? TR.lime : 'transparent',
                color: TR.fg,
                fontFamily: 'Archivo, sans-serif',
                fontWeight: 700, fontSize: 12, letterSpacing: '0.03em',
                transition: 'background 0.13s, border-color 0.13s',
                WebkitTapHighlightColor: 'transparent',
              }}
            >
              {f.emoji} {f.label}
            </button>
          )
        })}
      </div>

      {/* ── Content ── */}
      <div style={{
        flex: 1, overflowY: 'auto',
        padding: '14px 16px 28px',
        display: 'flex', flexDirection: 'column',
      }}>

        {/* Geo denied */}
        {geoStatus === 'denied' && (
          <div style={{
            flex: 1, display: 'flex', flexDirection: 'column',
            alignItems: 'center', justifyContent: 'center',
            padding: '40px 24px', gap: 16, textAlign: 'center',
          }}>
            <div style={{ fontSize: 40 }}>📍</div>
            <div>
              <div style={{
                fontFamily: 'Archivo, sans-serif', fontWeight: 800,
                fontSize: 16, textTransform: 'uppercase', color: TR.fg, marginBottom: 8,
              }}>
                Геолокация недоступна
              </div>
              <div style={{
                fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                color: TR.fgMute, lineHeight: 1.65, maxWidth: 270,
              }}>
                Разреши доступ к геолокации в браузере, чтобы найти реальные места рядом с тобой
              </div>
            </div>
            <button
              onClick={requestGeo}
              style={{
                padding: '11px 24px',
                background: TR.lime, color: TR.fg,
                border: `1.5px solid ${TR.fg}`, borderRadius: 10,
                fontFamily: 'Archivo, sans-serif',
                fontWeight: 800, fontSize: 12, letterSpacing: '0.05em',
                cursor: 'pointer', boxShadow: `2px 2px 0 0 ${TR.fg}`,
              }}
            >
              РАЗРЕШИТЬ ДОСТУП
            </button>
          </div>
        )}

        {/* Waiting for geo */}
        {geoStatus === 'requesting' && (
          <div style={{
            flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
              color: TR.fgMute, letterSpacing: '0.1em', textTransform: 'uppercase',
            }}>
              Определяем местоположение...
            </div>
          </div>
        )}

        {/* Skeletons */}
        {geoStatus === 'ok' && loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              color: TR.fgMute, letterSpacing: '0.1em',
              textTransform: 'uppercase', marginBottom: 4,
            }}>
              Ищем места рядом...
            </div>
            <SkeletonCard /><SkeletonCard /><SkeletonCard />
          </div>
        )}

        {/* Error */}
        {!loading && error && (
          <div style={{
            padding: '14px 16px', borderRadius: 12, marginBottom: 12,
            background: 'rgba(200,85,61,0.08)', border: '1px solid rgba(200,85,61,0.22)',
            fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: TR.warn,
          }}>
            {error}
          </div>
        )}

        {/* Results */}
        {geoStatus === 'ok' && !loading && !error && (
          sorted.length === 0 ? (
            <div style={{
              flex: 1, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center',
              padding: '40px 24px', gap: 10, textAlign: 'center',
            }}>
              <div style={{ fontSize: 32 }}>🔍</div>
              <div style={{
                fontFamily: 'Archivo, sans-serif', fontWeight: 800,
                fontSize: 15, textTransform: 'uppercase', color: TR.fg,
              }}>
                Ничего не нашлось
              </div>
              <div style={{
                fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                color: TR.fgMute, lineHeight: 1.6, maxWidth: 260,
              }}>
                {filter === 'all'
                  ? 'В радиусе 1 км ничего нет. Попробуй обновить или сменить фильтр.'
                  : 'Нет мест этой категории рядом. Попробуй другой фильтр.'}
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              <div style={{
                fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
                color: TR.fgMute, letterSpacing: '0.08em',
                textTransform: 'uppercase', marginBottom: 2,
              }}>
                {sorted.length} {sorted.length === 1 ? 'место' : sorted.length < 5 ? 'места' : 'мест'} · по расстоянию
              </div>
              {sorted.map(place => (
                <PlaceCard
                  key={place.place_id}
                  place={place}
                  userPos={userPos}
                  tripId={tripId}
                />
              ))}
            </div>
          )
        )}

      </div>
    </div>
  )
}
