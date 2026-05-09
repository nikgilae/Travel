import { useState } from 'react'
import './TripPlanScreen.css'

const TR = {
  bg:         '#f1ede0',
  surface:    '#fbf7ea',
  surface2:   '#e8e2cf',
  fg:         '#0d2818',
  fgMute:     '#5e6e58',
  hairline:   'rgba(13,40,24,0.12)',
  hairlineSt: 'rgba(13,40,24,0.22)',
  lime:       '#b9ff3d',
  warn:       '#c8553d',
}

const DAY_COLORS = [
  '#c8553d', '#4a7c59', '#5a6e9a', '#8a5a2a', '#6a4a8a', '#3a7a6a', '#7a5a3a',
]

const WEEKDAYS = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

const TABS = ['ДНИ', 'КАРТА', 'СПИСОК', 'БЮДЖЕТ']

// ── Day 1 data — Roma ──────────────────────────────────────

const DAY1 = {
  label: 'ПРИЛЁТ · ЗНАКОМСТВО',
  cost: 50,
  items: 4,
  poi: [
    { t: '09:00', dur: '30 МИН', n: "Tazza d'Oro",         sub: 'эспрессо у Пантеона',               tag: 'КОФЕ',      cost: '8 €'  },
    { t: '11:00', dur: '2 Ч',    n: 'Колизей и Форум',     sub: 'без очереди, утром меньше людей',   tag: 'ИСТОРИЯ',   cost: '18 €', peak: true },
    { t: '13:30', dur: '90 МИН', n: 'Trattoria Lilli',     sub: 'обед в семейной траттории',         tag: 'ОБЕД',      cost: '24 €' },
    { t: '17:30', dur: '2 Ч',    n: 'Прогулка по Трастевере', sub: 'на закате, без расписания',      tag: 'ПРОГУЛКА',  cost: '0 €'  },
  ],
  // SVG curve: amp values per hour slot
  curvePath: 'M0,45 C20,42 30,42 40,38 C50,30 60,15 80,12 C100,9 120,18 140,28 C160,38 175,40 195,30 C215,20 230,18 250,22 C265,25 275,30 280,35',
  curveFill: 'M0,45 C20,42 30,42 40,38 C50,30 60,15 80,12 C100,9 120,18 140,28 C160,38 175,40 195,30 C215,20 230,18 250,22 C265,25 275,30 280,35 L280,55 L0,55 Z',
  curveDots: [
    { x: 8,   y: 43, peak: false },
    { x: 80,  y: 12, peak: true  },
    { x: 140, y: 28, peak: false },
    { x: 230, y: 18, peak: false },
  ],
  rhythmLabels: ['УТРО · СПОКОЙНО', '↑ ПИК 11:00', 'ВЕЧЕР · МЯГКО'],
}

// ── Icons ──────────────────────────────────────────────────

const ChevronLeft = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M11.5 4 L6.5 9 L11.5 14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const StarIcon = ({ size = 18 }) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill="none">
    <path d="M8 1 L9 7 L15 8 L9 9 L8 15 L7 9 L1 8 L7 7 Z" fill="currentColor"/>
  </svg>
)

// ── Rhythm chart ───────────────────────────────────────────

function RhythmChart({ day, color }) {
  const gradId = `grad-${day}`
  return (
    <svg viewBox="0 0 280 62" style={{ width: '100%', height: 62, display: 'block' }}>
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.30"/>
          <stop offset="100%" stopColor={color} stopOpacity="0"/>
        </linearGradient>
      </defs>
      {[0, 1, 2, 3].map(i => (
        <line key={i}
          x1={i * 70 + 20} y1="0" x2={i * 70 + 20} y2="50"
          stroke={TR.hairlineSt} strokeWidth="1" strokeDasharray="2,3"
        />
      ))}
      <path d={DAY1.curveFill} fill={`url(#${gradId})`}/>
      <path d={DAY1.curvePath} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round"/>
      {DAY1.curveDots.map((dot, i) => (
        <circle key={i} cx={dot.x} cy={dot.y} r={dot.peak ? 5 : 3.5}
          fill={color} stroke={TR.surface} strokeWidth="2"/>
      ))}
      {['08', '12', '16', '20'].map((h, i) => (
        <text key={h} x={i * 70 + 20} y="61" textAnchor="middle"
          fontFamily="JetBrains Mono, monospace" fontSize="8" fill={TR.fgMute}>{h}
        </text>
      ))}
    </svg>
  )
}

// ── Main component ─────────────────────────────────────────

export default function TripPlanScreen({ city, groupType, rhythm, onBack }) {
  const [activeTab, setActiveTab] = useState(0)
  const [activeDay, setActiveDay] = useState(1)

  const cityName    = city?.n    ?? 'Рим'
  const cityCode    = city?.code ?? 'ROM'
  const color       = DAY_COLORS[(activeDay - 1) % DAY_COLORS.length]
  const rhythmLabel = rhythm === 'slow' ? 'СПОКОЙНО' : rhythm === 'intense' ? 'НАСЫЩЕННО' : 'СБАЛАНСИРОВАННО'
  const groupLabel  = { solo: 'СОЛО', duo: 'ВДВОЁМ', family: 'СЕМЬЯ', friends: 'ДРУЗЬЯ', group: 'ГРУППА' }[groupType] ?? 'ВДВОЁМ'

  return (
    <div className="tr-app">
      <div className="tr-phone">

        {/* ── Top bar ── */}
        <div style={{
          height: 52, padding: '0 22px',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexShrink: 0,
        }}>
          <button className="tr-icon-btn" onClick={onBack}
            style={{ color: TR.fg, border: '1.5px solid ' + TR.fg }}>
            <ChevronLeft />
          </button>
          <div style={{
            fontFamily: 'Archivo, sans-serif',
            fontSize: 13, fontWeight: 800, letterSpacing: '0.04em', color: TR.fg,
          }}>
            ВАШ<span style={{ color: TR.fgMute }}>·</span>МАРШРУТ
          </div>
          <div style={{ width: 38 }} />
        </div>

        {/* ── Trip header ── */}
        <div style={{ padding: '4px 22px 14px' }}>
          <div style={{
            fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
            letterSpacing: '0.22em', color: TR.fgMute, marginBottom: 6,
            textTransform: 'uppercase',
          }}>
            {cityCode} · 41.90°N · 12.49°E · 7 ДНЕЙ
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10 }}>
            <h1 style={{
              fontFamily: 'Archivo, sans-serif',
              fontWeight: 900, fontSize: 42, lineHeight: 0.86,
              letterSpacing: '-0.04em', textTransform: 'uppercase',
              color: TR.fg, margin: 0,
            }}>
              {cityName.toUpperCase()},<br/>НЕ СПЕША
            </h1>
            <button style={{
              width: 46, height: 46, borderRadius: '50%',
              background: TR.lime, color: TR.fg,
              border: '1.5px solid ' + TR.fg,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '2px 2px 0 0 ' + TR.fg,
              cursor: 'pointer', flexShrink: 0,
            }}>
              <StarIcon size={18} />
            </button>
          </div>
          <div style={{
            marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap',
            fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
            color: TR.fg, letterSpacing: 0.6,
          }}>
            {[groupLabel, rhythmLabel, '~1 200 €'].map(tag => (
              <span key={tag} style={{
                padding: '4px 10px',
                background: TR.surface, border: '1px solid ' + TR.hairline,
                borderRadius: 99,
              }}>{tag}</span>
            ))}
          </div>
        </div>

        {/* ── Tabs ── */}
        <div style={{
          margin: '0 22px',
          padding: 4,
          background: TR.surface2, borderRadius: 12,
          display: 'flex', gap: 2,
          border: '1px solid ' + TR.hairline,
        }}>
          {TABS.map((tab, i) => (
            <button
              key={tab}
              onClick={() => setActiveTab(i)}
              style={{
                flex: 1, height: 36,
                background: activeTab === i ? TR.bg : 'transparent',
                color: TR.fg, border: 'none',
                borderRadius: 9,
                fontFamily: 'Archivo, sans-serif',
                fontSize: 11, fontWeight: activeTab === i ? 800 : 600,
                letterSpacing: '0.06em',
                boxShadow: activeTab === i ? '0 1px 3px rgba(13,40,24,0.12)' : 'none',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              {tab}
            </button>
          ))}
        </div>

        {activeTab !== 0 ? (
          <div style={{
            padding: '40px 22px', textAlign: 'center',
            fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
            color: TR.fgMute, letterSpacing: 1,
          }}>
            {TABS[activeTab]} — В РАЗРАБОТКЕ
          </div>
        ) : (
          <>
            {/* ── Day pills ── */}
            <div className="tr-day-scroll" style={{
              display: 'flex', gap: 4,
              padding: '14px 22px 4px',
              overflowX: 'auto',
            }}>
              {Array.from({ length: 7 }, (_, i) => i + 1).map(d => {
                const isSel = d === activeDay
                return (
                  <div
                    key={d}
                    onClick={() => setActiveDay(d)}
                    style={{
                      flexShrink: 0,
                      display: 'flex', flexDirection: 'column',
                      alignItems: 'center', gap: 5,
                      padding: '8px 4px',
                      minWidth: 38, cursor: 'pointer',
                    }}
                  >
                    <div style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                      color: TR.fgMute, letterSpacing: 0.6,
                    }}>{WEEKDAYS[d - 1]}</div>
                    <div style={{
                      width: 32, height: 32, borderRadius: 8,
                      background: isSel ? TR.fg : 'transparent',
                      color: isSel ? TR.lime : TR.fg,
                      border: '1.5px solid ' + (isSel ? TR.fg : TR.hairline),
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontFamily: 'Archivo, sans-serif', fontSize: 14, fontWeight: 800,
                      boxShadow: isSel ? '2px 2px 0 0 ' + TR.fg : 'none',
                      transform: isSel ? 'translate(-1px,-1px)' : 'none',
                      transition: 'all 0.15s ease',
                    }}>
                      0{d}
                    </div>
                  </div>
                )
              })}
            </div>

            {/* ── Day rhythm chart ── */}
            <div style={{ padding: '4px 22px 0' }}>
              <div style={{
                padding: '14px 16px',
                background: TR.surface, borderRadius: 14,
                border: '1.5px solid ' + TR.hairline,
              }}>
                <div style={{
                  display: 'flex', justifyContent: 'space-between',
                  alignItems: 'baseline', marginBottom: 10,
                }}>
                  <div>
                    <div style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                      letterSpacing: '0.22em', color: TR.fgMute,
                      textTransform: 'uppercase',
                    }}>
                      ДЕНЬ 0{activeDay} · РИТМ
                    </div>
                    <div style={{
                      fontFamily: 'Archivo, sans-serif',
                      fontSize: 18, fontWeight: 800, lineHeight: 1.05,
                      letterSpacing: '-0.02em', color: TR.fg, marginTop: 4,
                    }}>
                      {activeDay === 1 ? DAY1.label : 'ИЗУЧЕНИЕ ГОРОДА'}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                      color: TR.fg, fontWeight: 700, letterSpacing: 0.4,
                    }}>{activeDay === 1 ? DAY1.cost : '—'} €</div>
                    <div style={{ fontSize: 11, color: TR.fgMute, marginTop: 2 }}>
                      {activeDay === 1 ? DAY1.items : '—'} событий
                    </div>
                  </div>
                </div>

                <RhythmChart day={activeDay} color={color} />

                <div style={{
                  display: 'flex', justifyContent: 'space-between',
                  marginTop: 6,
                  fontFamily: 'JetBrains Mono, monospace',
                  fontSize: 9, letterSpacing: 0.6,
                }}>
                  <span style={{ color: TR.fgMute }}>{DAY1.rhythmLabels[0]}</span>
                  <span style={{ color, fontWeight: 700 }}>{DAY1.rhythmLabels[1]}</span>
                  <span style={{ color: TR.fgMute }}>{DAY1.rhythmLabels[2]}</span>
                </div>
              </div>
            </div>

            {/* ── POI timeline ── */}
            {activeDay === 1 ? (
              <div style={{ padding: '18px 22px 32px', position: 'relative' }}>
                {/* Vertical line */}
                <div style={{
                  position: 'absolute',
                  left: 22 + 46 + 12 + 6,
                  top: 24, bottom: 24,
                  width: 1, background: TR.hairlineSt,
                }} />

                {DAY1.poi.map((p, i) => (
                  <div key={i} style={{
                    display: 'flex', gap: 12, alignItems: 'flex-start',
                    paddingBottom: i < DAY1.poi.length - 1 ? 18 : 0,
                  }}>
                    {/* Time column */}
                    <div style={{ width: 46, flexShrink: 0, textAlign: 'right', paddingTop: 4 }}>
                      <div style={{
                        fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                        color: TR.fg, fontWeight: 700, letterSpacing: 0.4,
                      }}>{p.t}</div>
                      <div style={{
                        fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                        color: TR.fgMute, letterSpacing: 0.6, marginTop: 2,
                      }}>{p.dur}</div>
                    </div>

                    {/* Timeline dot */}
                    <div style={{
                      width: 14, flexShrink: 0, paddingTop: 8,
                      display: 'flex', justifyContent: 'center',
                      position: 'relative', zIndex: 1,
                    }}>
                      {p.peak ? (
                        <div style={{
                          width: 14, height: 14, borderRadius: '50%',
                          background: color,
                          border: '2px solid ' + TR.bg,
                          boxShadow: '0 0 0 1.5px ' + color,
                        }} />
                      ) : (
                        <div style={{
                          width: 10, height: 10, borderRadius: '50%',
                          background: TR.bg,
                          border: '1.8px solid ' + color,
                        }} />
                      )}
                    </div>

                    {/* POI card */}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{
                        padding: p.peak ? '12px 14px' : '6px 0',
                        background: p.peak ? TR.surface : 'transparent',
                        border: p.peak ? '1.5px solid ' + TR.fg : 'none',
                        borderRadius: p.peak ? 12 : 0,
                        boxShadow: p.peak ? '3px 3px 0 0 ' + TR.fg : 'none',
                        transform: p.peak ? 'translate(-1px,-1px)' : 'none',
                      }}>
                        <div style={{
                          display: 'flex', justifyContent: 'space-between',
                          alignItems: 'baseline', gap: 8,
                        }}>
                          <div style={{
                            fontFamily: 'Archivo, sans-serif',
                            fontSize: p.peak ? 18 : 15, fontWeight: 800,
                            lineHeight: 1.1, letterSpacing: '-0.02em',
                            textTransform: 'uppercase', flex: 1,
                            color: TR.fg,
                          }}>{p.n}</div>
                          <div style={{
                            fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                            color: TR.fg, fontWeight: 600, letterSpacing: 0.3,
                            flexShrink: 0,
                          }}>{p.cost}</div>
                        </div>
                        <div style={{
                          marginTop: 4, fontSize: 13, color: TR.fgMute, lineHeight: 1.4,
                          fontStyle: p.peak ? 'normal' : 'italic',
                        }}>{p.sub}</div>
                        <div style={{
                          marginTop: 6,
                          fontFamily: 'JetBrains Mono, monospace',
                          fontSize: 9, color: TR.fgMute, letterSpacing: 1,
                        }}>↳ {p.tag}</div>

                        {p.peak && (
                          <div style={{
                            marginTop: 10, paddingTop: 10,
                            borderTop: '1px dashed ' + TR.hairlineSt,
                            display: 'flex', gap: 8,
                          }}>
                            <button className="tr-action-btn tr-action-btn--primary">
                              ЗАМЕНИТЬ
                            </button>
                            <button className="tr-action-btn">
                              АЛЬТЕРНАТИВЫ · 3
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{
                padding: '32px 22px', textAlign: 'center',
                fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
                color: TR.fgMute, letterSpacing: 1,
              }}>
                ДЕНЬ 0{activeDay} — МАРШРУТ ФОРМИРУЕТСЯ
              </div>
            )}
          </>
        )}

      </div>
    </div>
  )
}
