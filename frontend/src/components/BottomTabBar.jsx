import { useNavigate, useLocation } from 'react-router-dom'

const RouteIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
    <circle cx="5" cy="18" r="2.5" stroke="currentColor" strokeWidth="1.8"/>
    <circle cx="19" cy="6" r="2.5" stroke="currentColor" strokeWidth="1.8"/>
    <path d="M7.5 16.5 L12 12 L16 15 L21.5 8.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const ChatIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
      stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

const NearbyIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"
      stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx="12" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.8"/>
  </svg>
)

export { RouteIcon, ChatIcon, NearbyIcon }

export default function BottomTabBar({ tabs, theme = 'light' }) {
  const navigate = useNavigate()
  const { pathname } = useLocation()

  const isDark = theme === 'dark'
  const bg = isDark ? '#1a1f1a' : '#f1ede0'
  const borderColor = isDark ? 'rgba(255,255,255,0.08)' : 'rgba(13,40,24,0.12)'
  const inactive = isDark ? 'rgba(255,255,255,0.32)' : 'rgba(13,40,24,0.38)'
  const active = '#b9ff3d'

  return (
    <div style={{
      flexShrink: 0,
      height: 64,
      background: bg,
      borderTop: `1px solid ${borderColor}`,
      display: 'flex',
      alignItems: 'stretch',
      boxShadow: isDark
        ? '0 -4px 20px rgba(0,0,0,0.25)'
        : '0 -4px 20px rgba(13,40,24,0.07)',
    }}>
      {tabs.map(tab => {
        const isActive = pathname === tab.route
        return (
          <button
            key={tab.route}
            onClick={() => navigate(tab.route)}
            style={{
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 3,
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: isActive ? active : inactive,
              transition: 'color 0.15s',
              padding: '6px 0 10px',
              WebkitTapHighlightColor: 'transparent',
            }}
          >
            {tab.icon}
            <span style={{
              fontSize: 10,
              fontFamily: 'Archivo, sans-serif',
              fontWeight: 700,
              letterSpacing: '0.07em',
              textTransform: 'uppercase',
              lineHeight: 1,
            }}>
              {tab.label}
            </span>
          </button>
        )
      })}
    </div>
  )
}
