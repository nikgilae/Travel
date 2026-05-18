import { useState, useEffect } from 'react'
import './OnboardingStep1.css'
import { useOnboarding } from '../store/onboardingStore.jsx'

const API_BASE = 'http://localhost:8000'

const TR = {
  bg:         '#f1ede0',
  surface:    '#fbf7ea',
  surface2:   '#e8e2cf',
  fg:         '#0d2818',
  fgMute:     '#5e6e58',
  hairline:   'rgba(13,40,24,0.12)',
  hairlineSt: 'rgba(13,40,24,0.22)',
  lime:       '#C8FF00',
  warn:       '#c8553d',
}

const TOP9 = [
  'Турция', 'Китай', 'ОАЭ', 'Абхазия',
  'Таиланд', 'Египет', 'Беларусь', 'Казахстан', 'Армения',
]

const PALETTES = [
  { hueA: '#e8a370', hueB: '#8b3f2a', hueDeep: '#3a1d14' },
  { hueA: '#f0c4a0', hueB: '#c87555', hueDeep: '#5a2a1f' },
  { hueA: '#d8a8b8', hueB: '#5a3a4f', hueDeep: '#1f1424' },
  { hueA: '#f0c878', hueB: '#c87a4a', hueDeep: '#4a2818' },
  { hueA: '#a8c4d8', hueB: '#3a5a6a', hueDeep: '#1a2a34' },
  { hueA: '#c8d8a0', hueB: '#4a6a2a', hueDeep: '#1a2a0a' },
  { hueA: '#d4b8e8', hueB: '#6a3a8a', hueDeep: '#2a1a3a' },
  { hueA: '#f0d898', hueB: '#b89040', hueDeep: '#4a3810' },
  { hueA: '#b8d4c8', hueB: '#3a6a5a', hueDeep: '#1a2a24' },
]

const SILHOUETTES = [
  'M0,200 L0,150 L40,150 L42,140 L80,140 L80,120 L100,120 L100,100 L130,90 L160,80 L190,90 L210,100 L220,120 L240,120 L240,140 L290,140 L290,130 L320,130 L320,150 L380,150 L380,200 Z',
  'M0,200 L0,160 L30,160 L40,150 L70,150 L75,135 L120,135 L130,120 L160,110 L180,90 L200,80 L220,90 L240,110 L260,120 L290,130 L310,135 L340,140 L380,150 L380,200 Z',
  'M0,200 L0,160 L20,160 L20,120 L50,120 L50,140 L80,140 L80,100 L110,100 L115,40 L160,10 L190,30 L195,100 L220,100 L220,140 L250,140 L250,120 L290,120 L290,160 L380,160 L380,200 Z',
  'M0,200 L0,170 L30,170 L40,150 L70,148 L100,140 L130,135 L160,130 L190,120 L220,125 L250,130 L280,135 L310,140 L340,145 L380,150 L380,200 Z',
]

function getVisual(name) {
  let hash = 0
  for (const ch of name) hash = (hash * 31 + ch.charCodeAt(0)) & 0xffff
  const idx = hash % PALETTES.length
  return {
    ...PALETTES[idx],
    silhouette: SILHOUETTES[idx % SILHOUETTES.length],
  }
}

function getToken() {
  return localStorage.getItem('access_token') ?? ''
}

async function apiFetch(path) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Authorization: `Bearer ${getToken()}` },
  })
  if (!res.ok) throw new Error(res.status)
  return res.json()
}

// ── Icons ──────────────────────────────────────────────────────

const IconSearch = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.6"/>
    <path d="M14 14 L11 11" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/>
  </svg>
)

const IconArrowRight = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M3 8 H13 M9 4 L13 8 L9 12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const IconChevronLeft = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M11.5 4 L6.5 9 L11.5 14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const IconDots = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <circle cx="3" cy="8" r="1.4" fill="currentColor"/>
    <circle cx="8" cy="8" r="1.4" fill="currentColor"/>
    <circle cx="13" cy="8" r="1.4" fill="currentColor"/>
  </svg>
)

// ── Country photo ──────────────────────────────────────────────

const CountryPhoto = ({ visual, name, height = 140 }) => {
  const id = name.replace(/\s/g, '-')
  return (
    <svg
      viewBox={`0 0 380 ${height}`}
      preserveAspectRatio="xMidYMid slice"
      style={{ display: 'block', width: '100%', height }}
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={`sky-${id}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={visual.hueA} stopOpacity="0.95"/>
          <stop offset="60%" stopColor={visual.hueA} stopOpacity="0.7"/>
          <stop offset="100%" stopColor={visual.hueB} stopOpacity="0.85"/>
        </linearGradient>
        <radialGradient id={`sun-${id}`} cx="0.78" cy="0.32" r="0.35">
          <stop offset="0%" stopColor="#fff7e0" stopOpacity="0.95"/>
          <stop offset="100%" stopColor="#fff7e0" stopOpacity="0"/>
        </radialGradient>
      </defs>
      <rect width="380" height={height} fill={`url(#sky-${id})`}/>
      <rect width="380" height={height} fill={`url(#sun-${id})`}/>
      <circle cx="296" cy={height * 0.32} r="22" fill="#fff5d6" opacity="0.85"/>
      <rect y={height * 0.55} width="380" height={height * 0.45} fill={visual.hueB} opacity="0.18"/>
      <g transform={`translate(0, ${height - 180})`}>
        <path d={visual.silhouette} fill={visual.hueDeep} opacity="0.95"/>
      </g>
      <rect width="380" height={height} fill="#000" opacity="0.04"/>
    </svg>
  )
}

// ── Main component ─────────────────────────────────────────────

export default function OnboardingStep1({ onContinue }) {
  const { update } = useOnboarding()

  const [search, setSearch] = useState('')
  const [allCountries, setAllCountries] = useState([])
  const [citiesMap, setCitiesMap] = useState({})
  const [selectedCountryId, setSelectedCountryId] = useState(null)
  const [selectedCityId, setSelectedCityId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Load all countries on mount, then pre-fetch top-9 cities
  useEffect(() => {
    apiFetch('/countries')
      .then(async data => {
        setAllCountries(data)
        setLoading(false)

        // Pre-fetch cities for top-9 countries in parallel
        const top9 = TOP9.map(name => data.find(c => c.name === name)).filter(Boolean)
        const results = await Promise.allSettled(
          top9.map(c => apiFetch(`/countries/${c.id}/cities`).then(cities => ({ id: c.id, cities })))
        )
        const newMap = {}
        for (const r of results) {
          if (r.status === 'fulfilled') {
            newMap[r.value.id] = r.value.cities
          }
        }
        setCitiesMap(newMap)
      })
      .catch(() => {
        setError('Не удалось загрузить страны. Проверьте подключение.')
        setLoading(false)
      })
  }, [])

  // Load cities for a country if not yet loaded
  async function ensureCities(country) {
    if (citiesMap[country.id] !== undefined) return
    try {
      const cities = await apiFetch(`/countries/${country.id}/cities`)
      setCitiesMap(prev => ({ ...prev, [country.id]: cities }))
    } catch {
      setCitiesMap(prev => ({ ...prev, [country.id]: [] }))
    }
  }

  function handleSelectCountry(country) {
    if (selectedCountryId === country.id) {
      setSelectedCountryId(null)
      setSelectedCityId(null)
      update({ city_id: null })
      return
    }
    setSelectedCountryId(country.id)
    setSelectedCityId(null)
    update({ city_id: null })
    ensureCities(country)
  }

  // Compute displayed countries + highlighted city per country
  const q = search.trim().toLowerCase()

  let displayed = []
  let highlightedCityByCountry = {} // { countryId: cityId }

  if (!q) {
    // Top-9 in fixed order
    displayed = TOP9
      .map(name => allCountries.find(c => c.name === name))
      .filter(Boolean)
  } else {
    const seen = new Set()
    const result = []

    for (const c of allCountries) {
      if (c.name.toLowerCase().includes(q)) {
        if (!seen.has(c.id)) { seen.add(c.id); result.push(c) }
      }
    }

    // Also search pre-loaded cities
    for (const [countryId, cities] of Object.entries(citiesMap)) {
      const matchCity = cities.find(city => city.name.toLowerCase().includes(q))
      if (matchCity) {
        const country = allCountries.find(c => c.id === countryId)
        if (country && !seen.has(country.id)) {
          seen.add(country.id)
          result.push(country)
        }
        if (matchCity) {
          highlightedCityByCountry[countryId] = matchCity.id
        }
      }
    }

    displayed = result
  }

  const selectedCountry = allCountries.find(c => c.id === selectedCountryId)
  const selectedCity = selectedCountryId
    ? (citiesMap[selectedCountryId] ?? []).find(c => c.id === selectedCityId)
    : null

  const canContinue = !!(selectedCountry && selectedCity)

  function handleContinue() {
    if (!canContinue) return
    update({ city_id: selectedCity.id })
    onContinue?.({
      n: selectedCity.name,
      sub: selectedCountry.name,
      days: '7–10 дней',
      code: selectedCity.name.slice(0, 3).toUpperCase(),
      cityId: selectedCity.id,
      countryId: selectedCountry.id,
    })
  }

  return (
    <div className="tr-app">
      <div className="tr-phone">

        {/* ── Top bar ── */}
        <div style={{
          height: 52, padding: '0 22px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexShrink: 0,
        }}>
          <div style={{ width: 38, height: 38 }} />
          <div style={{
            fontFamily: 'Archivo, sans-serif',
            fontSize: 13, fontWeight: 800, letterSpacing: '0.04em', color: TR.fg,
          }}>
            TOUR<span style={{ color: TR.fgMute }}>·</span>RHYTHM
          </div>
          <button style={{
            width: 38, height: 38, borderRadius: '50%',
            background: 'transparent', color: TR.fg,
            border: '1.5px solid ' + TR.fg,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer',
          }}>
            <IconDots />
          </button>
        </div>

        {/* ── Ledger ── */}
        <div style={{
          margin: '8px 22px 12px',
          padding: '10px 14px',
          border: '1px solid ' + TR.hairline,
          borderRadius: 10,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
          color: TR.fgMute, letterSpacing: 1, textTransform: 'uppercase',
        }}>
          <span>STEP 01 / 05</span>
        </div>

        {/* ── Hero ── */}
        <div style={{ padding: '4px 22px 18px' }}>
          <h1 style={{
            fontFamily: 'Archivo, sans-serif',
            fontWeight: 900, fontSize: 56, lineHeight: 0.86,
            letterSpacing: '-0.04em', textTransform: 'uppercase',
            color: TR.fg, margin: 0,
          }}>
            КУДА<br/>ЕДЕМ?
          </h1>
        </div>

        {/* ── Search ── */}
        <div style={{ padding: '0 22px 14px' }}>
          <div style={{ position: 'relative' }}>
            <input
              className="tr-search-input"
              placeholder="Страна или город"
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{
                width: '100%', height: 50, paddingLeft: 42, paddingRight: 14,
                borderRadius: 99, border: '1.5px solid ' + TR.fg,
                background: TR.surface, fontFamily: 'Inter, sans-serif', fontSize: 15,
                color: TR.fg, outline: 'none', boxSizing: 'border-box',
              }}
            />
            <span style={{
              position: 'absolute', left: 16, top: '50%',
              transform: 'translateY(-50%)', color: TR.fg,
              display: 'flex', pointerEvents: 'none',
            }}>
              <IconSearch />
            </span>
            {search && (
              <button
                onClick={() => setSearch('')}
                style={{
                  position: 'absolute', right: 14, top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none', border: 'none', cursor: 'pointer',
                  color: TR.fgMute, fontSize: 18, lineHeight: 1, padding: 0,
                }}
              >
                ×
              </button>
            )}
          </div>
        </div>

        {/* ── Section label ── */}
        {!q && !loading && !error && (
          <div style={{
            padding: '0 22px 10px',
            display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
          }}>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              letterSpacing: '0.22em', textTransform: 'uppercase',
              color: TR.fg, fontWeight: 600,
            }}>
              ТОП / {displayed.length}
            </div>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              color: TR.fgMute, letterSpacing: 1,
            }}>↓</div>
          </div>
        )}
        {q && !loading && !error && (
          <div style={{
            padding: '0 22px 10px',
            fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
            letterSpacing: '0.22em', textTransform: 'uppercase',
            color: TR.fg, fontWeight: 600,
          }}>
            РЕЗУЛЬТАТЫ / {displayed.length}
          </div>
        )}

        {/* ── Body ── */}
        <div style={{ padding: '0 22px', display: 'flex', flexDirection: 'column', gap: 12 }}>

          {loading && (
            <div style={{
              padding: '40px 0', textAlign: 'center',
              fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
              color: TR.fgMute, letterSpacing: 1,
            }}>
              ЗАГРУЗКА···
            </div>
          )}

          {error && (
            <div style={{
              padding: '18px 16px', borderRadius: 12,
              border: '1.5px solid ' + TR.warn,
              background: TR.surface,
              fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
              color: TR.warn, letterSpacing: 0.8,
            }}>
              {error}
            </div>
          )}

          {!loading && !error && displayed.length === 0 && (
            <div style={{
              padding: '24px 0', textAlign: 'center',
              fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
              color: TR.fgMute, letterSpacing: 1,
            }}>
              НИЧЕГО НЕ НАЙДЕНО — ПОПРОБУЙТЕ ЕЩЁ
            </div>
          )}

          {!loading && !error && displayed.map(country => {
            const isSel = country.id === selectedCountryId
            const visual = getVisual(country.name)
            const cities = citiesMap[country.id] ?? []
            const highlightedCity = highlightedCityByCountry[country.id] ?? null

            return (
              <div
                key={country.id}
                className="tr-city-card"
                style={{
                  background: TR.surface,
                  borderRadius: 16,
                  border: '1.5px solid ' + (isSel ? TR.fg : TR.hairline),
                  overflow: 'hidden',
                  boxShadow: isSel ? '4px 4px 0 0 ' + TR.fg : 'none',
                  transform: isSel ? 'translate(-2px,-2px)' : 'none',
                  transition: 'box-shadow 0.2s ease, transform 0.2s ease, border-color 0.2s ease',
                  cursor: 'pointer',
                }}
                onClick={() => handleSelectCountry(country)}
              >
                {/* Photo */}
                <CountryPhoto visual={visual} name={country.name} height={130} />

                {/* Name bar */}
                <div style={{
                  padding: '12px 16px 0',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                }}>
                  <div style={{
                    fontFamily: 'Archivo, sans-serif',
                    fontSize: 22, fontWeight: 900, lineHeight: 1,
                    letterSpacing: '-0.02em', textTransform: 'uppercase',
                    color: TR.fg,
                  }}>
                    {country.name}
                  </div>
                  <div style={{
                    fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
                    color: TR.fgMute, letterSpacing: 1,
                    transition: 'transform 0.25s ease',
                    transform: isSel ? 'rotate(180deg)' : 'none',
                  }}>
                    ↓
                  </div>
                </div>

                {/* Expandable section */}
                <div className={`tr-expand${isSel ? ' tr-expand--open' : ''}`}>
                  <div className="tr-expand-inner">

                    {/* Description */}
                    {country.description && (
                      <div style={{
                        padding: '10px 16px 0',
                        fontSize: 13, lineHeight: 1.5, color: TR.fgMute,
                      }}>
                        {country.description}
                      </div>
                    )}

                    {/* City pills */}
                    {cities.length > 0 && (
                      <div style={{ padding: '10px 0 14px' }}>
                        <div style={{
                          fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                          letterSpacing: '0.2em', textTransform: 'uppercase',
                          color: TR.fgMute, padding: '0 16px', marginBottom: 8,
                        }}>
                          ВЫБЕРИТЕ ГОРОД
                        </div>
                        <div className="tr-city-scroll">
                          {cities.map(city => {
                            const isCitySel = city.id === selectedCityId
                            const isHighlighted = city.id === highlightedCity && !isCitySel
                            return (
                              <button
                                key={city.id}
                                onClick={e => {
                                  e.stopPropagation()
                                  const next = isCitySel ? null : city.id
                                  setSelectedCityId(next)
                                  update({ city_id: next })
                                }}
                                className="tr-city-pill"
                                style={{
                                  background: isCitySel
                                    ? TR.lime
                                    : isHighlighted
                                      ? 'rgba(200,255,0,0.18)'
                                      : 'transparent',
                                  color: TR.fg,
                                  border: '1.5px solid ' + (isCitySel ? TR.fg : TR.hairlineSt),
                                  boxShadow: isCitySel ? '2px 2px 0 0 ' + TR.fg : 'none',
                                  transform: isCitySel ? 'translate(-1px,-1px)' : 'none',
                                }}
                              >
                                {city.name}
                              </button>
                            )
                          })}
                        </div>
                      </div>
                    )}

                    {isSel && cities.length === 0 && (
                      <div style={{
                        padding: '10px 16px 14px',
                        fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
                        color: TR.fgMute, letterSpacing: 0.8,
                      }}>
                        ЗАГРУЗКА ГОРОДОВ···
                      </div>
                    )}

                  </div>
                </div>

                {/* Bottom padding for closed card */}
                {!isSel && <div style={{ height: 14 }} />}
              </div>
            )
          })}
        </div>

        <div style={{ height: 24 }} />

        {/* ── Sticky CTA ── */}
        <div style={{
          position: 'sticky', bottom: 0,
          padding: '14px 22px 22px',
          background: `linear-gradient(to top, ${TR.bg} 75%, transparent)`,
        }}>
          <button
            className="tr-cta-btn"
            onClick={handleContinue}
            disabled={!canContinue}
            style={{
              width: '100%', height: 60, borderRadius: 14,
              background: canContinue ? TR.lime : TR.surface2,
              color: TR.fg,
              border: '2px solid ' + (canContinue ? TR.fg : TR.hairlineSt),
              fontFamily: 'Archivo, sans-serif',
              fontSize: 15, fontWeight: 800,
              letterSpacing: '0.04em', textTransform: 'uppercase',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
              boxShadow: canContinue ? '4px 4px 0 0 ' + TR.fg : 'none',
              cursor: canContinue ? 'pointer' : 'default',
              opacity: canContinue ? 1 : 0.6,
              transition: 'all 0.2s ease',
            }}
          >
            {canContinue
              ? <>Продолжить с {selectedCity.name} <IconArrowRight /></>
              : 'Выберите страну и город'}
          </button>
        </div>

      </div>
    </div>
  )
}
