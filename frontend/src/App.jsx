import { useState } from 'react'
import OnboardingStep1 from './pages/OnboardingStep1'
import OnboardingStep2 from './pages/OnboardingStep2'
import OnboardingStep3 from './pages/OnboardingStep3'
import OnboardingStep4 from './pages/OnboardingStep4'
import TripPlanScreen from './pages/TripPlanScreen'

function App() {
  const [step, setStep] = useState(1)
  const [city, setCity] = useState(null)
  const [groupType, setGroupType] = useState(null)
  const [rhythm, setRhythm] = useState(null)

  if (step === 5) {
    return (
      <TripPlanScreen
        city={city}
        groupType={groupType}
        rhythm={rhythm}
        onBack={() => setStep(1)}
      />
    )
  }

  if (step === 4) {
    return (
      <OnboardingStep4
        city={city}
        groupType={groupType}
        rhythm={rhythm}
        onComplete={() => setStep(5)}
      />
    )
  }

  if (step === 3) {
    return (
      <OnboardingStep3
        city={city}
        groupType={groupType}
        onBack={() => setStep(2)}
        onContinue={(r) => {
          setRhythm(r)
          setStep(4)
        }}
      />
    )
  }

  if (step === 2) {
    return (
      <OnboardingStep2
        city={city}
        onBack={() => setStep(1)}
        onContinue={(group, notes) => {
          setGroupType(group)
          setStep(3)
        }}
      />
    )
  }

  return (
    <OnboardingStep1
      onContinue={(selectedCity) => {
        setCity(selectedCity)
        setStep(2)
      }}
    />
  )
}

export default App