import { useState, useEffect } from 'react'
import './OnboardingStep4.css'

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

const STEPS = [
  { t: 'Читаю ваш профиль' },
  { t: 'Подбираю места под ритм' },
  { t: 'Раскладываю по дням' },
  { t: 'Балансирую бюджет' },
  { t: 'Подбираю альтернативы' },
]

const STEP_DELAY_MS = 1200

const RHYTHM_LABELS = {
  slow:     'СПОКОЙНО',
  balanced: 'СБАЛАНСИРОВАННО',
  intense:  'НАСЫЩЕННО',
}

const GROUP_LABELS = {
  solo:    'СОЛО',
  duo:     'ВДВОЁМ',
  family:  'СЕМЬЯ',
  friends: 'ДРУЗЬЯ',
  group:   'ГРУППА',
}

const CITY_TIPS = {
  ROM: 'Не пытайтесь увидеть всё. Хороший день в Риме — это две сильные точки и одна непланируемая пауза с эспрессо.',
  LIS: 'Лиссабон лучше всего открывается пешком. Трамвай 28 — для туристов, ваши ноги — для настоящего города.',
  TYO: 'В Токио можно потеряться специально. Выберите один район и проведите в нём целый день — это честнее, чем галочки.',
  MEX: 'Мехико — город для завтраков. Самые живые рынки и лучший кофе — до полудня.',
}

const CheckIcon = () => (
  <svg width="12" height="12" viewBox="0 0 14 14" fill="none">
    <path d="M3 7 L6 10 L11 4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

export default function OnboardingStep4({ city, groupType, rhythm, onComplete }) {
  const [activeStep, setActiveStep] = useState(0)
  const [doneCount, setDoneCount] = useState(0)

  const cityName  = city?.n    ?? 'Рим'
  const cityDays  = city?.days ?? '7–10 дней'
  const cityCode  = city?.code ?? 'ROM'
  const tipText   = CITY_TIPS[cityCode] ?? CITY_TIPS.ROM
  const groupLabel  = GROUP_LABELS[groupType]  ?? 'ВДВОЁМ'
  const rhythmLabel = RHYTHM_LABELS[rhythm]    ?? 'СБАЛАНСИРОВАННО'

  useEffect(() => {
    if (activeStep >= STEPS.length) {
      const t = setTimeout(() => onComplete?.(), 600)
      return () => clearTimeout(t)
    }
    const t = setTimeout(() => {
      setDoneCount(activeStep + 1)
      setActiveStep(prev => prev + 1)
    }, STEP_DELAY_MS)
    return () => clearTimeout(t)
  }, [activeStep, onComplete])

  return (
    <div className="tr-app">
      <div className="tr-phone" style={{ display: 'flex', flexDirection: 'column' }}>

        {/* ── Top bar (no back button) ── */}
        <div style={{
          height: 52, padding: '0 22px',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          flexShrink: 0,
        }}>
          <div style={{
            fontFamily: 'Onest, sans-serif',
            fontSize: 13, fontWeight: 500, letterSpacing: '-0.005em', color: TR.fg,
          }}>
            TOUR<span style={{ color: TR.fgMute }}>·</span>RHYTHM
          </div>
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
          <span>{cityName.toUpperCase()} · {cityDays.toUpperCase()} · {groupLabel}</span>
          <span>{rhythmLabel}</span>
        </div>

        {/* ── Spinning star + hero ── */}
        <div style={{
          margin: '10px 22px 18px',
          padding: '28px 22px 18px',
          display: 'flex', flexDirection: 'column', alignItems: 'center',
        }}>
          <div className="tr-spin" style={{ marginBottom: 20, color: TR.fg, lineHeight: 0 }}>
            <svg width="72" height="72" viewBox="0 0 16 16" fill="none">
              <path d="M8 1 L9 7 L15 8 L9 9 L8 15 L7 9 L1 8 L7 7 Z" fill="currentColor"/>
            </svg>
          </div>
          <h1 style={{
            fontFamily: 'Onest, sans-serif',
            fontWeight: 600, fontSize: 42, lineHeight: 0.88,
            letterSpacing: '-0.04em', textTransform: 'uppercase',
            color: TR.fg, textAlign: 'center', margin: 0,
          }}>
            СКЛАДЫВАЮ<br/>МАРШРУТ
          </h1>
          <div style={{
            marginTop: 12,
            fontFamily: 'JetBrains Mono, monospace', fontSize: 11,
            letterSpacing: '0.18em', color: TR.fgMute, textAlign: 'center',
          }}>
            МЕНЬШЕ МИНУТЫ · МОЖНО НЕ ЗАКРЫВАТЬ
          </div>
        </div>

        {/* ── Steps checklist ── */}
        <div style={{ padding: '0 22px' }}>
          <div style={{
            padding: '4px 22px 10px 0',
            display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
          }}>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              letterSpacing: '0.22em', textTransform: 'uppercase',
              color: TR.fg, fontWeight: 600,
            }}>ПРОЦЕСС</div>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              color: TR.fgMute, letterSpacing: 1,
            }}>{Math.min(doneCount, STEPS.length)} / {STEPS.length}</div>
          </div>

          <div style={{
            background: TR.surface, borderRadius: 14,
            border: '1px solid ' + TR.hairline, overflow: 'hidden',
          }}>
            {STEPS.map((s, i) => {
              const isDone   = i < doneCount
              const isActive = i === activeStep && activeStep < STEPS.length
              return (
                <div key={i} style={{
                  padding: '14px 16px',
                  display: 'flex', alignItems: 'center', gap: 14,
                  borderBottom: i < STEPS.length - 1 ? '1px solid ' + TR.hairline : 'none',
                  opacity: isDone || isActive ? 1 : 0.45,
                  transition: 'opacity 0.4s ease',
                }}>
                  {/* Status dot */}
                  <div style={{
                    width: 22, height: 22, flexShrink: 0, borderRadius: '50%',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: isDone ? TR.fg : (isActive ? TR.lime : 'transparent'),
                    border: isActive
                      ? '1.5px solid ' + TR.fg
                      : (isDone ? 'none' : '1.5px solid ' + TR.hairlineSt),
                    color: isDone ? TR.lime : TR.fg,
                    transition: 'background 0.3s ease',
                  }}>
                    {isDone && <CheckIcon />}
                    {isActive && (
                      <div className="tr-pulse" style={{
                        width: 8, height: 8, borderRadius: '50%', background: TR.fg,
                      }} />
                    )}
                  </div>

                  {/* Label */}
                  <div style={{
                    flex: 1, fontSize: 14,
                    fontWeight: isActive ? 600 : 400,
                    color: isActive ? TR.fg : TR.fgMute,
                    textDecoration: isDone ? 'line-through' : 'none',
                    textDecorationThickness: '1px',
                    transition: 'color 0.3s ease',
                  }}>{s.t}</div>

                  {/* Right badge */}
                  {isDone && (
                    <div style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                      color: TR.fgMute, letterSpacing: 1,
                    }}>OK</div>
                  )}
                  {isActive && (
                    <div style={{
                      fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
                      color: TR.fg, letterSpacing: 1, fontWeight: 700,
                    }}>···</div>
                  )}
                </div>
              )
            })}
          </div>

          {/* ── Guide tip ── */}
          <div style={{
            marginTop: 18, padding: '14px 16px',
            borderRadius: 12,
            border: '1px dashed ' + TR.hairlineSt,
            background: TR.surface,
          }}>
            <div style={{
              fontFamily: 'JetBrains Mono, monospace', fontSize: 9,
              letterSpacing: '0.22em', color: TR.fgMute, marginBottom: 6,
              textTransform: 'uppercase',
            }}>ПОКА ЖДЁТЕ — СОВЕТ ГИДА</div>
            <div style={{
              fontFamily: 'Fraunces, serif', fontSize: 15, lineHeight: 1.45,
              color: TR.fg, fontStyle: 'italic',
            }}>
              {tipText}
            </div>
            <div style={{
              marginTop: 8,
              fontFamily: 'JetBrains Mono, monospace', fontSize: 10,
              color: TR.fgMute, letterSpacing: 0.8,
            }}>— ЗАМЕТКИ ЛОКАЛЬНОГО ГИДА</div>
          </div>
        </div>

        {/* ── Spacer + footer ── */}
        <div style={{ flex: 1 }} />

      </div>
    </div>
  )
}
