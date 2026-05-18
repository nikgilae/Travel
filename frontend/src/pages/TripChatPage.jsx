import { useParams, useLocation } from 'react-router-dom'
import ChatScreen from '../components/ChatScreen'

export default function TripChatPage() {
  const { id }     = useParams()
  const { pathname } = useLocation()
  const live       = pathname.includes('/live/')

  const tripMeta = JSON.parse(localStorage.getItem('trip_meta') ?? '{}')
  const cityName = tripMeta[id]?.city?.n ?? null

  return (
    <ChatScreen
      mode="trip"
      tripId={id}
      cityName={cityName}
      live={live}
    />
  )
}
