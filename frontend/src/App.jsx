import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, Outlet, useParams } from 'react-router-dom'
import { useOnboarding } from './store/onboardingStore.jsx'

import LoginPage            from './pages/LoginPage'
import RegisterPage         from './pages/RegisterPage'
import DashboardPage        from './pages/DashboardPage'
import GeneralChatPage      from './pages/GeneralChatPage'
import TripChatPage         from './pages/TripChatPage'
import NearbyPage           from './pages/NearbyPage'
import TripPlanScreen       from './pages/TripPlanScreen'
import OnboardingStep1      from './pages/OnboardingStep1'
import OnboardingStep2      from './pages/OnboardingStep2'
import OnboardingDates      from './pages/OnboardingDates'
import OnboardingStyle      from './pages/OnboardingStyle'
import OnboardingStep3      from './pages/OnboardingStep3'
import OnboardingBudget     from './pages/OnboardingBudget'
import OnboardingFinalQuestion from './pages/OnboardingFinalQuestion'
import BottomTabBar, { RouteIcon, ChatIcon, NearbyIcon } from './components/BottomTabBar'

// ── Helpers ────────────────────────────────────────────────

const GROUP_SIZE_MAP = { solo: 1, duo: 2, family: 4, friends: 3, group: 6 }
const BUDGET_MAP     = { economy: 'low', comfort: 'medium', lux: 'high' }
const RHYTHM_MAP     = { slow: 'relaxed', balanced: 'balanced', intense: 'active' }

function fmtDate({ year, month, day }) {
  return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
}

function calcEndDate(startDay, duration) {
  const d = new Date(startDay.year, startDay.month, startDay.day)
  d.setDate(d.getDate() + duration - 1)
  return fmtDate({ year: d.getFullYear(), month: d.getMonth(), day: d.getDate() })
}

// ── Layouts ────────────────────────────────────────────────

function DashboardLayout() {
  const tabs = [
    { route: '/dashboard/routes', label: 'Маршруты', icon: <RouteIcon /> },
    { route: '/dashboard/chat',   label: 'Чат',      icon: <ChatIcon /> },
  ]
  return (
    <div className="dash-app">
      <div className="dash-phone">
        <div className="dash-phone__scroll">
          <Outlet />
        </div>
        <BottomTabBar tabs={tabs} theme="dark" />
      </div>
    </div>
  )
}

function TripLayout() {
  const { id } = useParams()
  const tabs = [
    { route: `/trip/${id}/plan`, label: 'Маршрут', icon: <RouteIcon /> },
    { route: `/trip/${id}/chat`, label: 'Чат',     icon: <ChatIcon /> },
  ]
  return (
    <div className="tr-app">
      <div className="tr-phone">
        <div className="tr-phone__scroll">
          <Outlet />
        </div>
        <BottomTabBar tabs={tabs} theme="light" />
      </div>
    </div>
  )
}

function TripLiveLayout() {
  const { id } = useParams()
  const tabs = [
    { route: `/trip/${id}/live/plan`,   label: 'Маршрут', icon: <RouteIcon /> },
    { route: `/trip/${id}/live/chat`,   label: 'Чат',     icon: <ChatIcon /> },
    { route: `/trip/${id}/live/nearby`, label: 'Рядом',   icon: <NearbyIcon /> },
  ]
  return (
    <div className="tr-app">
      <div className="tr-phone">
        <div className="tr-phone__scroll">
          <Outlet />
        </div>
        <BottomTabBar tabs={tabs} theme="light" />
      </div>
    </div>
  )
}

// ── Onboarding flow ────────────────────────────────────────

function OnboardingFlow() {
  const { update } = useOnboarding()
  const [step, setStep] = useState(1)

  const [city,      setCity]      = useState(null)
  const [groupType, setGroupType] = useState(null)
  const [rhythm,    setRhythm]    = useState(null)

  if (step === 7) return (
    <OnboardingFinalQuestion
      city={city} groupType={groupType} rhythm={rhythm}
      onBack={() => setStep(6)}
    />
  )

  if (step === 6) return (
    <OnboardingBudget
      city={city} groupType={groupType}
      onBack={() => setStep(5)}
      onContinue={(level) => {
        update({ budget: BUDGET_MAP[level] ?? 'medium' })
        setStep(7)
      }}
    />
  )

  if (step === 5) return (
    <OnboardingStep3
      city={city} groupType={groupType}
      onBack={() => setStep(4)}
      onContinue={(r) => {
        setRhythm(r)
        update({ other_information: [RHYTHM_MAP[r] ?? r] })
        setStep(6)
      }}
    />
  )

  if (step === 4) return (
    <OnboardingStyle
      city={city} groupType={groupType}
      onBack={() => setStep(3)}
      onContinue={(selected) => {
        update({ interests: selected })
        setStep(5)
      }}
    />
  )

  if (step === 3) return (
    <OnboardingDates
      city={city} groupType={groupType}
      onBack={() => setStep(2)}
      onContinue={(dates) => {
        if (dates.startDay) {
          update({
            start_date: fmtDate(dates.startDay),
            end_date:   calcEndDate(dates.startDay, dates.duration),
          })
        }
        setStep(4)
      }}
    />
  )

  if (step === 2) return (
    <OnboardingStep2
      city={city}
      onBack={() => setStep(1)}
      onContinue={(group) => {
        setGroupType(group)
        update({ group_size: GROUP_SIZE_MAP[group] ?? 1 })
        setStep(3)
      }}
    />
  )

  return (
    <OnboardingStep1
      onContinue={(selectedCity) => {
        setCity(selectedCity)
        update({
          city_id:    selectedCity.cityId,
          country_id: selectedCity.countryId,
        })
        setStep(2)
      }}
    />
  )
}

// ── App ────────────────────────────────────────────────────

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Auth */}
        <Route path="/"         element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Onboarding (no nav bar) */}
        <Route path="/onboarding" element={<OnboardingFlow />} />

        {/* Level 1 — Dashboard */}
        <Route path="/dashboard" element={<Navigate to="/dashboard/routes" replace />} />
        <Route element={<DashboardLayout />}>
          <Route path="/dashboard/routes" element={<DashboardPage />} />
          <Route path="/dashboard/chat"   element={<GeneralChatPage />} />
        </Route>

        {/* Level 2 — Trip (pre-trip) */}
        <Route path="/trip/:id" element={<TripLayout />}>
          <Route index                    element={<Navigate to="plan" replace />} />
          <Route path="plan"              element={<TripPlanScreen />} />
          <Route path="chat"              element={<TripChatPage />} />
        </Route>

        {/* Level 3 — Trip Live (in-trip) */}
        <Route path="/trip/:id/live" element={<TripLiveLayout />}>
          <Route index                    element={<Navigate to="plan" replace />} />
          <Route path="plan"              element={<TripPlanScreen live />} />
          <Route path="chat"              element={<TripChatPage />} />
          <Route path="nearby"            element={<NearbyPage />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
