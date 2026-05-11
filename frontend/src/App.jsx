import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useOnboarding } from './store/onboardingStore.jsx'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import ActiveTripPage from './pages/ActiveTripPage'
import OnboardingStep1 from './pages/OnboardingStep1'
import OnboardingStep2 from './pages/OnboardingStep2'
import OnboardingDates from './pages/OnboardingDates'
import OnboardingStyle from './pages/OnboardingStyle'
import OnboardingStep3 from './pages/OnboardingStep3'
import OnboardingBudget from './pages/OnboardingBudget'
import OnboardingFinalQuestion from './pages/OnboardingFinalQuestion'
import TripPlanScreen from './pages/TripPlanScreen'

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

// ── Onboarding flow ────────────────────────────────────────

// step map:
// 1 → country/city
// 2 → group type   (01/06)
// 3 → dates        (02/06)
// 4 → style        (03/06)
// 5 → rhythm       (04/06)
// 6 → budget       (05/06)
// 7 → final q      (06/06) ← POST /trips happens here

function OnboardingFlow() {
  const { update } = useOnboarding()
  const [step, setStep] = useState(1)

  // Local display-only state (not needed in the API body)
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
      onContinue={(level, priority) => {
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

// ── /trip-plan route ───────────────────────────────────────

function TripPlanRoute() {
  const location = useLocation()
  const navigate  = useNavigate()
  const state     = location.state ?? {}

  // Prefer state passed by navigate(); fall back to localStorage
  const display = state.city
    ? state
    : JSON.parse(localStorage.getItem('trip_display_data') ?? '{}')

  return (
    <TripPlanScreen
      city={display.city}
      groupType={display.groupType}
      rhythm={display.rhythm}
      onBack={() => navigate('/dashboard')}
    />
  )
}

// ── App ───────────────────────────────────────────────��────

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"          element={<LoginPage />} />
        <Route path="/register"  element={<RegisterPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/trip"      element={<ActiveTripPage />} />
        <Route path="/onboarding" element={<OnboardingFlow />} />
        <Route path="/trip-plan" element={<TripPlanRoute />} />
        <Route path="*"          element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
