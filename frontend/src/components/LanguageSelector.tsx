import { useEffect, useState } from 'react'
import { getLanguages } from '../api'
import { useReviewStore } from '../store'
import type { Language } from '../types'

function LanguageSelector() {
  const language = useReviewStore((state) => state.language)
  const setLanguage = useReviewStore((state) => state.setLanguage)

  const [languages, setLanguages] = useState<Language[]>([])
  const [loadError, setLoadError] = useState('')

  useEffect(() => {
    getLanguages()
      .then((list) => setLanguages(list))
      .catch((err) => setLoadError(err.message))
  }, [])

  if (loadError) {
    return <p>Could not load languages: {loadError}</p>
  }

  return (
    <div>
      <span>Language:</span>
      {languages.map((lang) => (
        <button
          key={lang}
          onClick={() => setLanguage(lang)}
          disabled={lang === language}
        >
          {lang}
        </button>
      ))}
    </div>
  )
}

export default LanguageSelector
