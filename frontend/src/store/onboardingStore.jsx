import { createContext, useContext, useState } from 'react'

const INITIAL = {
  country_id:        null,
  city_id:           null,
  purpose:           'leisure', // "leisure" | "business" | "education" | "other"
  budget:            'medium',  // "low" | "medium" | "high"
  group_size:        1,
  other_information: [],        // includes trip rhythm: "balanced" | "active" | "relaxed"
  start_date:        null,      // "2026-06-01"
  end_date:          null,
  interests:         [],        // for /generate
  notes:             '',        // final open question — for /generate
}

const OnboardingContext = createContext(null)

export function OnboardingProvider({ children }) {
  const [data, setData] = useState(INITIAL)

  function update(patch) {
    setData(prev => ({ ...prev, ...patch }))
  }

  function reset() {
    setData(INITIAL)
  }

  return (
    <OnboardingContext.Provider value={{ data, update, reset }}>
      {children}
    </OnboardingContext.Provider>
  )
}

export function useOnboarding() {
  const ctx = useContext(OnboardingContext)
  if (!ctx) throw new Error('useOnboarding must be used inside OnboardingProvider')
  return ctx
}
