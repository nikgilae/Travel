import { useState, useEffect, useCallback, useRef, useMemo } from 'react'
import {
  GoogleMap,
  useJsApiLoader,
  OverlayView,
  InfoWindow,
  Polyline,
} from '@react-google-maps/api'

const LIBRARIES = ['places', 'geometry']
const LIME = '#C8FF00'
const GREY = '#9e9e9e'
const BG = '#f5f0e8'
const FG = '#1a1f1a'
const MUTED = '#666'
const LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

function fmtTime(dt) {
  if (!dt) return null
  try { return new Date(dt).toTimeString().slice(0, 5) } catch { return null }
}

export default function TripMap({ allPois, numDays, activeDay, setActiveDay, cityName, finalizedDays = new Set() }) {
  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries: LIBRARIES,
  })

  const [selectedId, setSelectedId] = useState(null)
  const [geocached, setGeocached] = useState({})
  const [userPos, setUserPos] = useState(null)
  const [mapReady, setMapReady] = useState(false)

  const mapRef = useRef(null)
  const geocoderRef = useRef(null)

  const isFinalized = finalizedDays.has(activeDay)

  const dayPois = useMemo(() =>
    allPois
      .filter(p => p.day_number === activeDay)
      .sort((a, b) => (a.sequence_order ?? 999) - (b.sequence_order ?? 999)),
    [allPois, activeDay]
  )

  const mainPois = useMemo(() => dayPois.filter(p => p.poi_status === 'main'), [dayPois])
  const altPois = useMemo(() =>
    isFinalized ? [] : dayPois.filter(p => p.poi_status === 'additional'),
    [dayPois, isFinalized]
  )

  const getCoords = useCallback(p => {
    if (p.poi.lat != null && p.poi.lon != null) return { lat: p.poi.lat, lng: p.poi.lon }
    return geocached[p.poi.id] ?? null
  }, [geocached])

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

  useEffect(() => {
    if (!mapReady || !mapRef.current) return
    const pts = dayPois.filter(p => getCoords(p))
    if (!pts.length) return
    const bounds = new window.google.maps.LatLngBounds()
    pts.forEach(p => bounds.extend(getCoords(p)))
    mapRef.current.fitBounds(bounds, 48)
  }, [mapReady, dayPois, geocached]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!navigator.geolocation) return
    navigator.geolocation.getCurrentPosition(
      pos => setUserPos({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => {},
      { timeout: 8000, maximumAge: 60000 },
    )
  }, [])

  const dayPoisRef = useRef(dayPois)
  useEffect(() => { dayPoisRef.current = dayPois }, [dayPois])

  const geocachedRef = useRef(geocached)
  useEffect(() => { geocachedRef.current = geocached }, [geocached])

  const onMapLoad = useCallback(map => {
    mapRef.current = map
    setMapReady(true)
    // Fit bounds immediately on load — no waiting for state update cycle
    const current = dayPoisRef.current
    const getC = p => {
      if (p.poi.lat != null && p.poi.lon != null) return { lat: p.poi.lat, lng: p.poi.lon }
      return geocachedRef.current[p.poi.id] ?? null
    }
    const pts = current.filter(p => getC(p))
    if (!pts.length) return
    const bounds = new window.google.maps.LatLngBounds()
    pts.forEach(p => bounds.extend(getC(p)))
    map.fitBounds(bounds, 48)
  }, [])

  const selectedPoi = useMemo(() =>
    selectedId ? dayPois.find(p => p.poi.id === selectedId) : null,
    [selectedId, dayPois]
  )

  const polylinePath = useMemo(() => {
    if (!isFinalized) return []
    return mainPois.map(p => getCoords(p)).filter(Boolean)
  }, [isFinalized, mainPois, getCoords]) // eslint-disable-line react-hooks/exhaustive-deps

  // First available coord from day POIs — used as initial map center to avoid showing 0,0
  const defaultCenter = useMemo(() => {
    for (const p of dayPois) {
      if (p.poi.lat != null && p.poi.lon != null) return { lat: p.poi.lat, lng: p.poi.lon }
      const c = geocached[p.poi.id]
      if (c) return c
    }
    return null
  }, [dayPois, geocached])

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
          const fin = finalizedDays.has(d)
          return (
            <button key={d}
              onClick={() => { setActiveDay(d); setSelectedId(null) }}
              style={{
                flexShrink: 0, padding: '5px 14px', borderRadius: 99,
                fontSize: 11, fontFamily: 'JetBrains Mono, monospace',
                border: '1.5px solid ' + (active ? FG : 'rgba(26,31,26,0.2)'),
                background: active ? LIME : 'transparent',
                color: FG, cursor: 'pointer',
                fontWeight: active ? 700 : 400,
                transition: 'all 0.15s',
              }}>
              ДЕНЬ {d}{fin ? ' ✓' : ''}
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
            center={defaultCenter ?? { lat: 40, lng: 30 }}
            zoom={defaultCenter ? 13 : 4}
            options={{
              zoomControl: true,
              mapTypeControl: false,
              streetViewControl: false,
              fullscreenControl: false,
              clickableIcons: false,
            }}
          >
            {/* Polyline between main POIs when finalized */}
            {isFinalized && polylinePath.length > 1 && (
              <Polyline
                path={polylinePath}
                options={{
                  strokeColor: LIME,
                  strokeOpacity: 0.85,
                  strokeWeight: 2.5,
                }}
              />
            )}

            {/* Main POI markers — lime with number */}
            {mainPois.filter(p => getCoords(p)).map((p, i) => {
              const isActive = selectedId === p.poi.id
              return (
                <OverlayView
                  key={p.poi.id}
                  position={getCoords(p)}
                  mapPaneName="overlayMouseTarget"
                >
                  <div
                    onClick={() => setSelectedId(isActive ? null : p.poi.id)}
                    style={{
                      width: 30, height: 30, borderRadius: '50%',
                      background: LIME, border: '2px solid ' + FG,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 11, fontWeight: 800, color: FG,
                      cursor: 'pointer',
                      transform: `translate(-50%, -50%)${isActive ? ' scale(1.2)' : ''}`,
                      boxShadow: isActive
                        ? '0 4px 14px rgba(0,0,0,0.35), 0 0 0 3px rgba(200,255,0,0.4)'
                        : '0 2px 6px rgba(0,0,0,0.25)',
                      fontFamily: 'JetBrains Mono, monospace',
                      userSelect: 'none',
                      position: 'relative',
                      zIndex: isActive ? 20 : 5,
                      transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                    }}>
                    {i + 1}
                  </div>
                </OverlayView>
              )
            })}

            {/* Alt POI markers — grey with letter (only before finalization) */}
            {!isFinalized && altPois.filter(p => getCoords(p)).map((p, i) => {
              const isActive = selectedId === p.poi.id
              return (
                <OverlayView
                  key={p.poi.id}
                  position={getCoords(p)}
                  mapPaneName="overlayMouseTarget"
                >
                  <div
                    onClick={() => setSelectedId(isActive ? null : p.poi.id)}
                    style={{
                      width: 26, height: 26, borderRadius: '50%',
                      background: GREY, border: '2px solid rgba(26,31,26,0.5)',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 10, fontWeight: 700, color: '#fff',
                      cursor: 'pointer',
                      transform: `translate(-50%, -50%)${isActive ? ' scale(1.2)' : ''}`,
                      boxShadow: isActive
                        ? '0 4px 12px rgba(0,0,0,0.3)'
                        : '0 2px 4px rgba(0,0,0,0.18)',
                      fontFamily: 'JetBrains Mono, monospace',
                      userSelect: 'none',
                      position: 'relative',
                      zIndex: isActive ? 20 : 2,
                      transition: 'transform 0.15s ease, box-shadow 0.15s ease',
                    }}>
                    {LETTERS[i % 26]}
                  </div>
                </OverlayView>
              )
            })}

            {/* User location — blue dot */}
            {userPos && (
              <OverlayView position={userPos} mapPaneName="overlayLayer">
                <div style={{
                  width: 16, height: 16, borderRadius: '50%',
                  background: '#2979ff', border: '2.5px solid #fff',
                  boxShadow: '0 0 0 3px rgba(41,121,255,0.25)',
                  transform: 'translate(-50%, -50%)',
                }} />
              </OverlayView>
            )}

            {/* InfoWindow on selected marker */}
            {selectedPoi && getCoords(selectedPoi) && (
              <InfoWindow
                position={getCoords(selectedPoi)}
                onCloseClick={() => setSelectedId(null)}
                options={{ pixelOffset: new window.google.maps.Size(0, -22) }}
              >
                <div style={{
                  background: '#fff', borderRadius: 10,
                  padding: '10px 14px', minWidth: 150, maxWidth: 220,
                  fontFamily: 'system-ui, sans-serif',
                  boxShadow: '0 2px 12px rgba(0,0,0,0.15)',
                }}>
                  <div style={{ fontWeight: 700, fontSize: 14, color: FG, marginBottom: 5, lineHeight: 1.3 }}>
                    {selectedPoi.poi.name}
                  </div>
                  {fmtTime(selectedPoi.planned_start_time) && (
                    <div style={{ fontSize: 12, color: MUTED, marginBottom: 3 }}>
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
                      background: FG, color: LIME, borderRadius: 6,
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
        alignItems: 'center',
      }}>
        {dayPois.length === 0 ? (
          <div style={{ padding: '12px 0', color: MUTED, fontSize: 11, fontFamily: 'JetBrains Mono, monospace', letterSpacing: 1 }}>
            НЕТ МЕСТ ДЛЯ ЭТОГО ДНЯ
          </div>
        ) : (
          <>
            {/* Main POI cards */}
            {mainPois.map((p, i) => {
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
                    background: isSelected ? LIME : '#fff',
                    border: '1.5px solid ' + (isSelected ? FG : 'rgba(26,31,26,0.12)'),
                    borderRadius: 12, cursor: 'pointer',
                    boxShadow: isSelected ? `2px 2px 0 ${FG}` : '0 1px 4px rgba(0,0,0,0.07)',
                    transition: 'all 0.15s',
                  }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 5 }}>
                    <div style={{
                      width: 20, height: 20, borderRadius: '50%', flexShrink: 0,
                      background: isSelected ? FG : LIME,
                      border: '1.5px solid ' + FG,
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: 9, fontWeight: 800, color: isSelected ? LIME : FG,
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

            {/* Divider + Alt POI cards (only before finalization) */}
            {!isFinalized && altPois.length > 0 && (
              <>
                <div style={{ flexShrink: 0, width: 1, height: 60, background: 'rgba(26,31,26,0.15)', margin: '0 2px' }} />
                {altPois.map((p, i) => {
                  const isSelected = selectedId === p.poi.id
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
                        flexShrink: 0, width: 128, padding: '10px 12px',
                        background: isSelected ? 'rgba(158,158,158,0.18)' : 'rgba(26,31,26,0.04)',
                        border: '1.5px dashed ' + (isSelected ? GREY : 'rgba(26,31,26,0.2)'),
                        borderRadius: 12, cursor: 'pointer',
                        transition: 'all 0.15s', opacity: 0.82,
                      }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 5 }}>
                        <div style={{
                          width: 18, height: 18, borderRadius: '50%', flexShrink: 0,
                          background: GREY, border: '1.5px solid rgba(26,31,26,0.4)',
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: 8, fontWeight: 700, color: '#fff',
                          fontFamily: 'JetBrains Mono, monospace',
                        }}>{LETTERS[i % 26]}</div>
                        <div style={{
                          fontWeight: 600, fontSize: 10, color: 'rgba(26,31,26,0.6)',
                          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', flex: 1,
                        }}>{p.poi.name}</div>
                      </div>
                      <div style={{ fontSize: 9, color: 'rgba(26,31,26,0.42)' }}>
                        {p.poi.is_indoor ? 'Закрытое' : 'На улице'}
                      </div>
                    </div>
                  )
                })}
              </>
            )}
          </>
        )}
      </div>

    </div>
  )
}
