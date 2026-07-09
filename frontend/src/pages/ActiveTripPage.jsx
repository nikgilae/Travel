import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import SelectionCircle from '../components/SelectionCircle'
import './ActiveTripPage.css'

const DAY_COLORS = ['#e84040','#e87010','#d4a000','#30a050','#2080d0','#8040c0','#c040a0']

const POIS = [
  { t: '9:00',  n: 'Завтрак · Bar del Fico',       status: 'done' },
  { t: '11:00', n: 'Пантеон',                        status: 'now'  },
  { t: '14:00', n: 'Обед: Armando al Pantheon',      status: 'next' },
  { t: '17:00', n: 'Фонтан Треви',                   status: 'next' },
  { t: '20:00', n: 'Ужин в Трастевере',              status: 'next' },
]

const STATUS_ICON = { done: '✓', now: '→', next: '○' }

const NEARBY_CATS = ['Всё', 'Еда', 'Парки', 'Музеи', 'Кафе']

export default function ActiveTripPage() {
  const navigate = useNavigate()
  const [nearbyFilter, setNearbyFilter] = useState('Всё')
  const [selectedPOIs, setSelectedPOIs] = useState(new Set())

  const togglePOISelection = (index) => {
    const newSelected = new Set(selectedPOIs)
    if (newSelected.has(index)) {
      newSelected.delete(index)
    } else {
      newSelected.add(index)
    }
    setSelectedPOIs(newSelected)
  }

  return (
    <div className="at-app">
      <div className="at-phone">

        {/* Welcome banner */}
        <div style={{
          padding: '20px 22px 16px',
          background: '#F0FFD6',
          borderBottom: '1px solid #E8EAEC',
        }}>
          <div style={{ fontSize: 11, color: '#5B6066', fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.06em', marginBottom: 6 }}>
            TourRhythm · День 3
          </div>
          <div style={{ fontSize: 20, fontWeight: 600, color: '#0A0B0C', lineHeight: 1.2 }}>
            Добро пожаловать<br/>назад!
          </div>
          <div style={{ fontSize: 13, color: '#5B6066', marginTop: 6 }}>
            Ты сейчас в Риме? Продолжим маршрут.
          </div>
          <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
            <button
              onClick={() => navigate('/onboarding')}
              style={{
                flex: 1, height: 40,
                background: '#FFFFFF', color: '#0A0B0C',
                border: '1px solid #D6D9DD',
                borderRadius: 10, fontWeight: 500, fontSize: 13,
                cursor: 'pointer', fontFamily: 'inherit',
              }}
            >
              + Новый маршрут
            </button>
            <button
              style={{
                flex: 1, height: 40,
                background: '#B9FF3D', color: '#0A0B0C',
                border: '1px solid #B9FF3D', borderRadius: 10,
                fontWeight: 600, fontSize: 13,
                cursor: 'pointer', fontFamily: 'inherit',
              }}
            >
              → Мой Рим
            </button>
          </div>
        </div>

        <div style={{ padding: '20px 22px', display: 'flex', flexDirection: 'column', gap: 20 }}>

          {/* Rhythm chart */}
          <div>
            <div style={{ fontSize: 10, fontFamily: 'JetBrains Mono, monospace', color: '#9097A0', letterSpacing: '0.06em', marginBottom: 10 }}>
              РИТМ ДНЯ — ДЕНЬ 3
            </div>
            <div style={{
              background: '#FFFFFF', borderRadius: 14, padding: '16px',
              border: '1px solid #E8EAEC',
            }}>
              <svg viewBox="0 0 280 56" style={{ width: '100%', height: 56, display: 'block' }}>
                <defs>
                  <linearGradient id="at-grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={DAY_COLORS[2]} stopOpacity="0.3"/>
                    <stop offset="100%" stopColor={DAY_COLORS[2]} stopOpacity="0"/>
                  </linearGradient>
                </defs>
                {[0,1,2,3].map(i => (
                  <line key={i} x1={i*70+20} y1="0" x2={i*70+20} y2="46"
                    stroke="rgba(10,11,12,0.08)" strokeWidth="1" strokeDasharray="2,3"/>
                ))}
                <path d="M10,40 C30,38 40,15 50,15 C60,15 70,25 90,25 C110,25 125,10 130,10 C135,10 150,30 170,30 C190,30 210,20 230,20 C250,20 265,30 270,35 L270,52 L10,52 Z"
                  fill="url(#at-grad)"/>
                <path d="M10,40 C30,38 40,15 50,15 C60,15 70,25 90,25 C110,25 125,10 130,10 C135,10 150,30 170,30 C190,30 210,20 230,20 C250,20 265,30 270,35"
                  fill="none" stroke={DAY_COLORS[2]} strokeWidth="2" strokeLinecap="round"/>
                <circle cx="130" cy="10" r="5" fill={DAY_COLORS[2]} stroke="#FFFFFF" strokeWidth="2"/>
                <circle cx="50" cy="15" r="3.5" fill={DAY_COLORS[2]} stroke="#FFFFFF" strokeWidth="2"/>
                <circle cx="230" cy="20" r="3.5" fill={DAY_COLORS[2]} stroke="#FFFFFF" strokeWidth="2"/>
                {['09','12','16','20'].map((h,i) => (
                  <text key={h} x={i*70+20} y="54" textAnchor="middle"
                    fontFamily="JetBrains Mono, monospace" fontSize="8" fill="#9097A0">{h}</text>
                ))}
              </svg>
            </div>
          </div>

          {/* Today's POIs */}
          <div>
            <div style={{ fontSize: 10, fontFamily: 'JetBrains Mono, monospace', color: '#9097A0', letterSpacing: '0.06em', marginBottom: 10 }}>
              СЕГОДНЯ · ДЕНЬ 3
            </div>
            <div style={{ background: '#FFFFFF', borderRadius: 14, overflow: 'hidden', border: '1px solid #E8EAEC' }}>
              {POIS.map((p, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '12px 16px',
                  borderBottom: i < POIS.length - 1 ? '1px solid #E8EAEC' : 'none',
                  background: p.status === 'done' ? '#F6F7F9'
                    : p.status === 'now' ? '#F0FFD6'
                    : 'transparent',
                  position: 'relative',
                }}>
                  <SelectionCircle
                    isSelected={selectedPOIs.has(i)}
                    onToggle={() => togglePOISelection(i)}
                  />
                  <span style={{
                    width: 22, height: 22, borderRadius: '50%',
                    background: p.status === 'done' ? '#F1F3F5'
                      : p.status === 'now' ? '#B9FF3D'
                      : 'transparent',
                    border: p.status === 'next' ? '1px solid #D6D9DD' : 'none',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 11, fontWeight: 600, color: '#0A0B0C',
                    flexShrink: 0,
                  }}>
                    {STATUS_ICON[p.status]}
                  </span>
                  <div style={{ flex: 1 }}>
                    <div style={{
                      fontSize: 14, fontWeight: p.status === 'now' ? 600 : 500,
                      color: p.status === 'done' ? '#9097A0' : '#0A0B0C',
                      textDecoration: p.status === 'done' ? 'line-through' : 'none',
                    }}>{p.n}</div>
                    <div style={{ fontSize: 11, color: '#9097A0', fontFamily: 'JetBrains Mono, monospace', marginTop: 2 }}>
                      {p.t}
                    </div>
                  </div>
                  {p.status !== 'done' && (
                    <div style={{ display: 'flex', gap: 8 }}>
                      <span style={{ fontSize: 16, cursor: 'pointer' }}>🔄</span>
                      {p.status === 'now' && <span style={{ fontSize: 16, cursor: 'pointer' }}>🗺</span>}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Find nearby */}
          <div>
            <div style={{ fontSize: 10, fontFamily: 'JetBrains Mono, monospace', color: '#9097A0', letterSpacing: '0.06em', marginBottom: 10 }}>
              НАЙТИ РЯДОМ · 500М
            </div>
            <div style={{ background: '#FFFFFF', borderRadius: 14, overflow: 'hidden', border: '1px solid #E8EAEC' }}>
              <div style={{
                display: 'flex', overflowX: 'auto', gap: 0,
                borderBottom: '1px solid #E8EAEC',
              }}>
                {NEARBY_CATS.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setNearbyFilter(cat)}
                    style={{
                      padding: '10px 14px', fontSize: 12, whiteSpace: 'nowrap',
                      background: nearbyFilter === cat ? '#0A0B0C' : 'transparent',
                      color: nearbyFilter === cat ? '#B9FF3D' : '#5B6066',
                      border: 'none', cursor: 'pointer',
                      fontWeight: nearbyFilter === cat ? 600 : 400,
                      fontFamily: 'inherit',
                    }}
                  >{cat}</button>
                ))}
              </div>
              <div style={{ padding: '14px 16px', color: '#9097A0', fontSize: 13, textAlign: 'center' }}>
                Поиск мест рядом — подключится с API карт
              </div>
            </div>
          </div>

        </div>

        {/* Back to dashboard */}
        <div style={{ padding: '0 22px 40px', textAlign: 'center' }}>
          <button
            onClick={() => navigate('/dashboard')}
            style={{
              background: 'none', border: 'none',
              color: '#9097A0', fontSize: 13,
              cursor: 'pointer', textDecoration: 'underline',
              fontFamily: 'inherit',
            }}
          >
            ← Все маршруты
          </button>
        </div>

      </div>
    </div>
  )
}
