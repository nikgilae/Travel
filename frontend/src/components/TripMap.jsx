import { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import {
  GoogleMap,
  useJsApiLoader,
  OverlayView,
  InfoWindow,
} from '@react-google-maps/api'

const LIBRARIES = ['places', 'geometry']
const ACCENT = '#b8ff4f'
const BG = '#f5f0e8'
const FG = '#1a1f1a'
const MUTED = '#666'

function fmtTime(dt) {
  if (!dt) return null
  try { return new Date(dt).toTimeString().slice(0, 5) } catch { return null }
}

export default function TripMap({ allPois, numDays, activeDay, setActiveDay, cityName }) {
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries: LIBRARIES,
  })

  const [selectedId, setSelectedId] = useState(null)
  const [geocached, setGeocached] = useState({})

  const mapRef = useRef(null)
  const geocoderRef = useRef(null)

  const dayPois = useMemo(() =>
    allPois
      .filter(p => p.day_number === activeDay)
      .sort((a, b) => (a.sequence_order ?? 999) - (b.sequence_order ?? 999)),
    [allPois, activeDay]
  )

  const getCoords = useCallback(p => {
    if (p.poi.lat != null && p.poi.lon != null) return { lat: p.poi.lat, lng: p.poi.lon }
    return geocached[p.poi.id] ?? null
  }, [geocached])

  // Geocode POIs that have no coordinates
  useEffect(() => {
    if (!isLoaded) return
    if (!geocoderRef.current) geocoderRef.current = new window.google.maps.Geocoder()
    const geocoder = geocoderRef.current

    dayPois
      .filter(p => (p.poi.lat == null || p.poi.lon == null) && !geocached[p.poi.id])
      .forEach(p => {
        const q = cityName ? `${p.poi.name}, ${cityName}` : p.poi.name
        geocoder.geocode({ address: q }, (results, status) => {
          if (status === 'OK' && results[0]) {
            const loc = results[0].geometry.location
            setGeocached(prev => ({ ...prev, [p.poi.id]: { lat: loc.lat(), lng: loc.lng() } }))
          }
        })
      })
  }, [isLoaded, dayPois, cityName]) // eslint-disable-line react-hooks/exhaustive-deps

  // Fit map to all visible markers when day or coords change
  useEffect(() => {
    if (!isLoaded || !mapRef.current) return
    const pts = dayPois.filter(p => getCoords(p))
    if (!pts.length) return
    const bounds = new window.google.maps.LatLngBounds()
    pts.forEach(p => bounds.extend(getCoords(p)))
    mapRef.current.fitBounds(bounds, 60)
  }, [isLoaded, dayPois, geocached]) // eslint-disable-line react-hooks/exhaustive-deps

  const onMapLoad = useCallback(map => { mapRef.current = map }, [])

  const selectedPoi = useMemo(() =>
    selectedId ? dayPois.find(p => p.poi.id === selectedId) : null,
    [selectedId, dayPois]
  )

  const poisWithCoords = useMemo(() => dayPois.filter(p => getCoords(p)), [dayPois, getCoords])

  if (loadError) return (
    <div style={{ padding: '24px 16px', textAlign: 'center', color: '#c8553d', fontFamily: 'JetBrains Mono, monospace', fontSize: 12, letterSpacing: 1 }}>
      ОШИБКА ЗАГРУЗКИ КАРТЫ
    </div>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', background: BG }}>

      {/* Day tabs */}
      <div style={{
        display: 'flex', gap: 6, overflowX: 'auto',
        padding: '10px 16px 8px', scrollbarWidth: 'none',
      }}>
        {Array.from({ length: numDays }, (_, i) => i + 1).map(d => {
          const active = activeDay === d
          return (
            <button key={d}
              onClick={() => { setActiveDay(d); setSelectedId(null) }}
              style={{
                flexShrink: 0, padding: '5px 14px', borderRadius: 99,
                fontSize: 11, fontFamily: 'JetBrains Mono, monospace',
                border: '1.5px solid ' + (active ? FG : 'rgba(26,31,26,0.2)'),
                background: active ? ACCENT : 'transparent',
                color: FG, cursor: 'pointer',
                fontWeight: active ? 700 : 400,
                transition: 'all 0.15s',
              }}>
              ДЕНЬ {d}
            </button>
          )
        })}
      </div>

      {/* Map */}
      <div style={{ height: 320, position: 'relative' }}>
        {!isLoaded ? (
          <div style={{
            height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: '#e8e5dc', fontFamily: 'JetBrains Mono, monospace',
            fontSize: 11, color: MUTED, letterSpacing: 1,
          }}>
            ЗАГРУЗКА КАРТЫ...
          </div>
        ) : (
          <GoogleMap
            onLoad={onMapLoad}
            mapContainerStyle={{ width: '100%', height: '100%' }}
            center={{ lat: 48.8566, lng: 2.3522 }}
            zoom={12}
            options={{
              zoomControl: true,
              mapTypeControl: false,
              streetViewControl: false,
              fullscreenControl: false,
              clickableIcons: false,
            }}
          >
            {/* Numbered circle markers */}
            {poisWithCoords.map((p, i) => (
              <OverlayView
                key={p.poi.id}
                position={getCoords(p)}
                mapPaneName="overlayMouseTarget"
              >
                <div
                  onClick={() => setSelectedId(selectedId === p.poi.id ? null : p.poi.id)}
                  style={{
                    width: 28, height: 28, borderRadius: '50%',
                    background: ACCENT, border: '2px solid ' + FG,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 11, fontWeight: 800, color: FG,
                    cursor: 'pointer',
                    transform: 'translate(-50%, -50%)',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.25)',
                    fontFamily: 'JetBrains Mono, monospace',
                    userSelect: 'none',
                    position: 'relative',
                    zIndex: selectedId === p.poi.id ? 10 : 1,
                    outline: selectedId === p.poi.id ? '3px solid ' + FG : 'none',
                    outlineOffset: 2,
                  }}>
                  {i + 1}
                </div>
              </OverlayView>
            ))}

            {/* InfoWindow on selected marker */}
            {selectedPoi && getCoords(selectedPoi) && (
              <InfoWindow
                position={getCoords(selectedPoi)}
                onCloseClick={() => setSelectedId(null)}
                options={{ pixelOffset: new window.google.maps.Size(0, -20) }}
              >
                <div style={{ maxWidth: 220, padding: '2px 2px 4px', fontFamily: 'system-ui, sans-serif' }}>
                  <div style={{ fontWeight: 700, fontSize: 14, color: FG, marginBottom: 5 }}>
                    {selectedPoi.poi.name}
                  </div>
                  {fmtTime(selectedPoi.planned_start_time) && (
                    <div style={{ fontSize: 12, color: MUTED, marginBottom: 2 }}>
                      🕐 {fmtTime(selectedPoi.planned_start_time)}
                    </div>
                  )}
                  <div style={{ fontSize: 12, color: MUTED, marginBottom: 10 }}>
                    {selectedPoi.poi.is_indoor ? '🏛 Закрытое место' : '🌳 На улице'}
                  </div>
                  <a
                    href={`https://maps.google.com/?daddr=${getCoords(selectedPoi).lat},${getCoords(selectedPoi).lng}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'inline-block', padding: '5px 12px',
                      background: FG, color: ACCENT, borderRadius: 6,
                      fontSize: 11, fontWeight: 700, textDecoration: 'none',
                    }}>
                    Как добраться →
                  </a>
                </div>
              </InfoWindow>
            )}
          </GoogleMap>
        )}
      </div>

      {/* Bottom POI cards (horizontal scroll) */}
      <div style={{
        display: 'flex', gap: 8, overflowX: 'auto',
        padding: '10px 16px 20px', scrollbarWidth: 'none',
      }}>
        {dayPois.length === 0 ? (
          <div style={{ padding: '12px 0', color: MUTED, fontSize: 11, fontFamily: 'JetBrains Mono, monospace', letterSpacing: 1 }}>
            НЕТ МЕСТ ДЛЯ ЭТОГО ДНЯ
          </div>
        ) : dayPois.map((p, i) => {
          const isSelected = selectedId === p.poi.id
          const t = fmtTime(p.planned_start_time)
          const coords = getCoords(p)
          return (
            <div
              key={p.poi.id}
              onClick={() => {
                if (coords && mapRef.current) {
                  mapRef.current.panTo(coords)
                  mapRef.current.setZoom(16)
                }
                setSelectedId(isSelected ? null : p.poi.id)
              }}
              style={{
                flexShrink: 0, width: 140, padding: '10px 12px',
                background: isSelected ? ACCENT : '#fff',
                border: '1.5px solid ' + (isSelected ? FG : 'rgba(26,31,26,0.12)'),
                borderRadius: 12, cursor: 'pointer',
                boxShadow: isSelected ? `2px 2px 0 ${FG}` : '0 1px 4px rgba(0,0,0,0.07)',
                transition: 'all 0.15s',
              }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 5 }}>
                <div style={{
                  width: 20, height: 20, borderRadius: '50%', flexShrink: 0,
                  background: isSelected ? FG : ACCENT,
                  border: '1.5px solid ' + FG,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 9, fontWeight: 800, color: isSelected ? ACCENT : FG,
                  fontFamily: 'JetBrains Mono, monospace',
                }}>{i + 1}</div>
                <div style={{
                  fontWeight: 700, fontSize: 11, color: FG,
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1,
                }}>{p.poi.name}</div>
              </div>
              {t && (
                <div style={{ fontSize: 10, color: isSelected ? FG : MUTED, marginBottom: 2 }}>
                  🕐 {t}
                </div>
              )}
              <div style={{ fontSize: 10, color: isSelected ? FG : MUTED }}>
                {p.poi.is_indoor ? 'Закрытое' : 'На улице'}
              </div>
            </div>
          )
        })}
      </div>

    </div>
  )
}
