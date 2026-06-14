import { useState, useEffect, useRef } from 'react'
import './OnboardingStep1.css'
import { useOnboarding } from '../store/onboardingStore.jsx'

const API_BASE = import.meta.env.VITE_API_URL

const TR = {
  bg:         '#F6F7F9',
  surface:    '#FFFFFF',
  surface2:   '#F1F3F5',
  fg:         '#0A0B0C',
  fgMute:     '#5B6066',
  hairline:   '#E8EAEC',
  hairlineSt: '#D6D9DD',
  lime:       '#B9FF3D',
  warn:       '#B43340',
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

// ── Country visual card ────────────────────────────────────────

const CountryPhoto = ({ visual, name, height = 110 }) => {
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

// ── Shared layout pieces ───────────────────────────────────────

function SearchInput({ value, onChange, placeholder }) {
  return (
    <div style={{ position: 'relative' }}>
      <input
        className="tr-search-input"
        placeholder={placeholder}
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{
          width: '100%', height: 50, paddingLeft: 42, paddingRight: value ? 40 : 14,
          borderRadius: 99, border: '1.5px solid ' + TR.fg,
          background: TR.surface, fontFamily: 'Onest, sans-serif', fontSize: 15,
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
      {value && (
        <button
          onClick={() => onChange('')}
          style={{
            position: 'absolute', right: 14, top: '50%',
            transform: 'translateY(-50%)',
            background: 'none', border: 'none', cursor: 'pointer',
            color: TR.fgMute, fontSize: 18, lineHeight: 1, padding: 0,
          }}
        >×</button>
      )}
    </div>
  )
}

function CtaBar({ onClick, disabled, label, icon }) {
  return (
    <div style={{
      flexShrink: 0,
      padding: '12px 22px 28px',
      background: TR.bg,
      borderTop: '1px solid ' + TR.hairline,
    }}>
      <button
        className="tr-cta-btn"
        onClick={onClick}
        disabled={disabled}
        style={{
          width: '100%', height: 48, borderRadius: 12,
          background: !disabled ? TR.lime : TR.surface2,
          color: TR.fg,
          border: '1px solid ' + (!disabled ? TR.fg : TR.hairlineSt),
          fontFamily: 'Onest, sans-serif',
          fontSize: 15, fontWeight: 600,
          letterSpacing: '-0.01em',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
          cursor: !disabled ? 'pointer' : 'default',
          opacity: !disabled ? 1 : 0.45,
          transition: 'background 0.12s ease, opacity 0.12s ease',
        }}
      >
        {label}
        {!disabled && icon}
      </button>
    </div>
  )
}

// ── Main component ─────────────────────────────────────────────

export default function OnboardingStep1({ onContinue }) {
  const { update } = useOnboarding()

  const [phase, setPhase] = useState('country')
  const [countrySearch, setCountrySearch] = useState('')
  const [citySearch, setCitySearch] = useState('')
  const [allCountries, setAllCountries] = useState([])
  const [citiesMap, setCitiesMap] = useState({})
  const [selectedCountry, setSelectedCountry] = useState(null)
  const [selectedCity, setSelectedCity] = useState(null)
  const [loading, setLoading] = useState(true)
  const [citiesLoading, setCitiesLoading] = useState(false)
  const [error, setError] = useState(null)
  const cityScrollRef = useRef(null)
  const countryScrollRef = useRef(null)

  useEffect(() => {
    apiFetch('/countries')
      .then(data => { setAllCountries(data); setLoading(false) })
      .catch(() => { setError('Не удалось загрузить страны. Проверьте подключение.'); setLoading(false) })
  }, [])

  async function loadCities(country) {
    if (citiesMap[country.id] !== undefined) return
    setCitiesLoading(true)
    try {
      const cities = await apiFetch(`/countries/${country.id}/cities`)
      setCitiesMap(prev => ({ ...prev, [country.id]: cities }))
    } catch {
      setCitiesMap(prev => ({ ...prev, [country.id]: [] }))
    } finally {
      setCitiesLoading(false)
    }
  }

  function handleSelectCountry(country) {
    setSelectedCountry(prev => prev?.id === country.id ? null : country)
    setSelectedCity(null)
    update({ city_id: null })
    loadCities(country)
  }

  function handleGoToCity() {
    if (!selectedCountry) return
    setPhase('city')
    setCitySearch('')
    if (cityScrollRef.current) cityScrollRef.current.scrollTop = 0
  }

  function handleSelectCity(city) {
    setSelectedCity(prev => prev?.id === city.id ? null : city)
    // Only update city_id if it's a real city from the database
    if (city.id) {
      update({ city_id: city.id })
    }
  }

  function handleSelectCustomCity(customName) {
    // Create a temporary city object for custom cities
    const customCity = {
      id: `custom_${customName.toLowerCase().replace(/\s+/g, '_')}`,
      name: customName,
      isCustom: true,
    }
    setSelectedCity(customCity)
    update({ city_id: null }) // Custom cities don't have real IDs
  }

  function handleContinue() {
    if (!selectedCountry || !selectedCity) return
    onContinue?.({
      n: selectedCity.name,
      sub: selectedCountry.name,
      days: '7–10 дней',
      code: selectedCity.name.slice(0, 3).toUpperCase(),
      cityId: selectedCity.isCustom ? null : selectedCity.id,
      countryId: selectedCountry.id,
    })
  }

  // ── Computed lists ──────────────────────────────────────────

  const cq = countrySearch.trim().toLowerCase()
  let displayedCountries
  if (!cq) {
    const top9List = TOP9.map(name => allCountries.find(c => c.name === name)).filter(Boolean)
    const top9Ids = new Set(top9List.map(c => c.id))
    const rest = allCountries
      .filter(c => !top9Ids.has(c.id))
      .sort((a, b) => a.name.localeCompare(b.name, 'ru'))
    displayedCountries = [...top9List, ...rest]
  } else {
    displayedCountries = allCountries
      .filter(c => c.name.toLowerCase().includes(cq))
      .sort((a, b) => a.name.localeCompare(b.name, 'ru'))
  }

  const cities = selectedCountry ? (citiesMap[selectedCountry.id] ?? []) : []
  const dq = citySearch.trim().toLowerCase()
  const displayedCities = !dq ? cities : cities.filter(c => c.name.toLowerCase().includes(dq))

  // Determine if user can create a custom city
  const canCreateCustomCity = dq && displayedCities.length === 0 && dq.length >= 2 && /^[а-яА-ЯёЁa-zA-Z\s\-]+$/.test(citySearch.trim())
  const customCityName = canCreateCustomCity ? citySearch.trim() : null

  // ── Phone shell (flex column, full height) ─────────────────

  const phoneShell = {
    width: '100%', maxWidth: 430,
    display: 'flex', flexDirection: 'column',
    height: '100dvh', overflow: 'hidden',
    background: TR.bg,
    fontFamily: 'Onest, sans-serif',
    WebkitFontSmoothing: 'antialiased',
  }

  // ── CITY PHASE ─────────────────────────────────────────────

  if (phase === 'city') {
    return (
      <div className="tr-onb-app">
        <div style={phoneShell}>

          {/* Header */}
          <div style={{
            flexShrink: 0, height: 52, padding: '0 16px 0 8px',
            display: 'flex', alignItems: 'center', gap: 4,
          }}>
            <button
              onClick={() => setPhase('country')}
              style={{
                width: 40, height: 40, borderRadius: '50%',
                background: 'transparent', border: 'none',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                cursor: 'pointer', color: TR.fg, flexShrink: 0,
              }}
            >
              <IconChevronLeft />
            </button>
            <div style={{
              fontFamily: 'Onest, sans-serif',
              fontSize: 15, fontWeight: 600, letterSpacing: '-0.01em',
              color: TR.fg, flex: 1,
            }}>
              {selectedCountry?.name}
            </div>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              color: TR.fgMute, letterSpacing: 0.8,
            }}>
              STEP 01 / 05
            </div>
          </div>

          {/* Title */}
          <div style={{ flexShrink: 0, padding: '0 22px 14px' }}>
            <h1 style={{
              fontFamily: 'Onest, sans-serif',
              fontWeight: 600, fontSize: 28, lineHeight: 1.1,
              letterSpacing: '-0.02em', color: TR.fg, margin: 0,
            }}>
              ВЫБЕРИТЕ ГОРОД
            </h1>
          </div>

          {/* Search */}
          <div style={{ flexShrink: 0, padding: '0 22px 12px' }}>
            <SearchInput
              value={citySearch}
              onChange={setCitySearch}
              placeholder="Поиск города"
            />
          </div>

          {/* Section label */}
          {dq && (
            <div style={{
              flexShrink: 0, padding: '0 22px 8px',
              display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
            }}>
              <div style={{
                fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
                letterSpacing: '0.22em', textTransform: 'uppercase',
                color: TR.fg, fontWeight: 600,
              }}>
                РЕЗУЛЬТАТЫ / {displayedCities.length + (canCreateCustomCity ? 1 : 0)}
              </div>
            </div>
          )}

          {/* Scrollable city list */}
          <div
            ref={cityScrollRef}
            style={{ flex: 1, overflowY: 'auto', padding: '0 22px 8px' }}
          >
            {citiesLoading && (
              <div style={{
                padding: '40px 0', textAlign: 'center',
                fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                color: TR.fgMute, letterSpacing: 1,
              }}>
                ЗАГРУЗКА···
              </div>
            )}

            {!citiesLoading && displayedCities.length === 0 && (
              <div style={{
                padding: '24px 0', textAlign: 'center',
                fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                color: TR.fgMute, letterSpacing: 1,
              }}>
                {dq ? 'НИЧЕГО НЕ НАЙДЕНО' : 'НЕТ ГОРОДОВ'}
              </div>
            )}

            {!citiesLoading && displayedCities.map(city => {
              const isSel = city.id === selectedCity?.id
              return (
                <div
                  key={city.id}
                  className="tr-city-row"
                  onClick={() => handleSelectCity(city)}
                  style={{
                    padding: '14px 16px',
                    borderRadius: 12,
                    background: isSel ? TR.lime : TR.surface,
                    border: '1px solid ' + (isSel ? TR.fg : TR.hairline),
                    marginBottom: 8,
                    cursor: 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    transition: 'background 0.15s ease, border-color 0.15s ease',
                    boxShadow: isSel ? '0 0 0 3px rgba(185,255,61,0.3)' : 'none',
                  }}
                >
                  <span style={{
                    fontFamily: 'Onest, sans-serif',
                    fontSize: 16, fontWeight: isSel ? 600 : 500,
                    color: TR.fg, letterSpacing: '-0.005em',
                  }}>
                    {city.name}
                  </span>
                  {isSel && (
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path d="M3 8 L7 12 L13 4" stroke={TR.fg} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </div>
              )
            })}

            {canCreateCustomCity && (
              <div
                className="tr-city-row"
                onClick={() => handleSelectCustomCity(customCityName)}
                style={{
                  padding: '14px 16px',
                  borderRadius: 12,
                  background: selectedCity?.isCustom ? TR.lime : TR.surface,
                  border: '1px solid ' + (selectedCity?.isCustom ? TR.fg : TR.hairlineSt),
                  marginBottom: 8,
                  cursor: 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  transition: 'background 0.15s ease, border-color 0.15s ease',
                  boxShadow: selectedCity?.isCustom ? '0 0 0 3px rgba(185,255,61,0.3)' : 'none',
                }}
              >
                <span style={{
                  fontFamily: 'Onest, sans-serif',
                  fontSize: 16, fontWeight: selectedCity?.isCustom ? 600 : 500,
                  color: TR.fg, letterSpacing: '-0.005em',
                }}>
                  {customCityName}
                </span>
                {selectedCity?.isCustom && (
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M3 8 L7 12 L13 4" stroke={TR.fg} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
              </div>
            )}

            <div style={{ height: 8 }} />
          </div>

          {/* CTA — always visible */}
          <CtaBar
            onClick={handleContinue}
            disabled={!selectedCity}
            label={selectedCity ? `Продолжить с ${selectedCity.name}` : 'Выберите город'}
            icon={<IconArrowRight />}
          />

        </div>
      </div>
    )
  }

  // ── COUNTRY PHASE ──────────────────────────────────────────

  const top9Count = TOP9.filter(name => allCountries.find(c => c.name === name)).length

  return (
    <div className="tr-onb-app">
      <div style={phoneShell}>

        {/* Top bar */}
        <div style={{
          flexShrink: 0,
          height: 52, padding: '0 22px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ width: 38, height: 38 }} />
          <div style={{
            fontFamily: 'Onest, sans-serif',
            fontSize: 13, fontWeight: 600, letterSpacing: '-0.01em', color: TR.fg,
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

        {/* Progress ledger */}
        <div style={{
          flexShrink: 0,
          margin: '0 22px 12px',
          padding: '10px 14px',
          border: '1px solid ' + TR.hairline,
          borderRadius: 10,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
          color: TR.fgMute, letterSpacing: 1, textTransform: 'uppercase',
        }}>
          <span>STEP 01 / 05</span>
        </div>

        {/* Hero */}
        <div style={{ flexShrink: 0, padding: '4px 22px 14px' }}>
          <h1 style={{
            fontFamily: 'Onest, sans-serif',
            fontWeight: 600, fontSize: 42, lineHeight: 1.05,
            letterSpacing: '-0.02em',
            color: TR.fg, margin: 0,
          }}>
            КУДА<br/>ЕДЕМ?
          </h1>
        </div>

        {/* Search */}
        <div style={{ flexShrink: 0, padding: '0 22px 12px' }}>
          <SearchInput
            value={countrySearch}
            onChange={setCountrySearch}
            placeholder="Страна"
          />
        </div>

        {/* Section label */}
        {!loading && !error && (
          <div style={{
            flexShrink: 0,
            padding: '0 22px 10px',
            display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
          }}>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              letterSpacing: '0.22em', textTransform: 'uppercase',
              color: TR.fg, fontWeight: 600,
            }}>
              {cq ? `РЕЗУЛЬТАТЫ / ${displayedCountries.length}` : `РАБОТАЕТ ${allCountries.length} СТРАН`}
            </div>
            {!cq && (
              <div style={{
                fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
                color: TR.fgMute, letterSpacing: 1,
              }}>↓ ВСЕ СТРАНЫ НИЖЕ</div>
            )}
          </div>
        )}

        {/* Scrollable country list */}
        <div
          ref={countryScrollRef}
          style={{ flex: 1, overflowY: 'auto', padding: '0 22px 8px' }}
        >

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

          {!loading && !error && displayedCountries.length === 0 && (
            <div style={{
              padding: '24px 0', textAlign: 'center',
              fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
              color: TR.fgMute, letterSpacing: 1,
            }}>
              НИЧЕГО НЕ НАЙДЕНО — ПОПРОБУЙТЕ ЕЩЁ
            </div>
          )}

          {!loading && !error && (
            <>
              {/* Top-9 divider label when not searching */}
              {!cq && (
                <div style={{
                  fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                  letterSpacing: '0.2em', color: TR.fgMute, textTransform: 'uppercase',
                  marginBottom: 10,
                }}>
                  ПОПУЛЯРНЫЕ
                </div>
              )}

              {displayedCountries.map((country, idx) => {
                const isSel = country.id === selectedCountry?.id
                const visual = getVisual(country.name)
                const isFirstNonTop9 = !cq && idx === top9Count

                return (
                  <div key={country.id}>
                    {/* Divider before "all countries" section */}
                    {isFirstNonTop9 && (
                      <div style={{
                        display: 'flex', alignItems: 'center', gap: 10,
                        margin: '16px 0 12px',
                      }}>
                        <div style={{ flex: 1, height: 1, background: TR.hairline }} />
                        <div style={{
                          fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                          letterSpacing: '0.2em', color: TR.fgMute, textTransform: 'uppercase',
                          flexShrink: 0,
                        }}>
                          ВСЕ СТРАНЫ
                        </div>
                        <div style={{ flex: 1, height: 1, background: TR.hairline }} />
                      </div>
                    )}

                    <div
                      className="tr-city-card"
                      onClick={() => handleSelectCountry(country)}
                      style={{
                        background: TR.surface,
                        borderRadius: 16,
                        border: '1.5px solid ' + (isSel ? TR.fg : TR.hairline),
                        overflow: 'hidden',
                        boxShadow: isSel ? '0 0 0 3px rgba(185,255,61,0.35)' : 'none',
                        transition: 'box-shadow 0.2s ease, border-color 0.2s ease',
                        cursor: 'pointer',
                        marginBottom: 10,
                      }}
                    >
                      <CountryPhoto visual={visual} name={country.name} height={110} />

                      <div style={{
                        padding: '12px 16px 14px',
                      }}>
                        <div>
                          <div style={{
                            fontFamily: 'Onest, sans-serif',
                            fontSize: 17, fontWeight: 600, lineHeight: 1.2,
                            letterSpacing: '-0.005em', color: TR.fg,
                          }}>
                            {country.name}
                          </div>
                          {country.description && (
                            <div style={{
                              fontSize: 12, color: TR.fgMute, marginTop: 3,
                              lineHeight: 1.4, maxWidth: 240,
                            }}>
                              {country.description}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </>
          )}

          <div style={{ height: 8 }} />
        </div>

        {/* CTA — always visible */}
        <CtaBar
          onClick={handleGoToCity}
          disabled={!selectedCountry}
          label={selectedCountry ? `Выбрать город в ${selectedCountry.name}` : 'Выберите страну'}
          icon={<IconArrowRight />}
        />

      </div>
    </div>
  )
}
