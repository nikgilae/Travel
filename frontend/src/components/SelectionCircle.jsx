export default function SelectionCircle({ isSelected, onToggle }) {
  return (
    <button
      onClick={onToggle}
      style={{
        position: 'absolute', top: 8, right: 8,
        width: 24, height: 24, borderRadius: '50%',
        border: '2px solid #D6D9DD',
        background: isSelected ? '#B9FF3D' : 'transparent',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        cursor: 'pointer', padding: 0,
        transition: 'all 0.2s ease',
        fontSize: 12,
        fontWeight: 600,
        color: isSelected ? '#0A0B0C' : 'transparent',
        fontFamily: 'inherit',
      }}
      title="Выбрать"
    >
      {isSelected ? '⭐' : ''}
    </button>
  )
}
