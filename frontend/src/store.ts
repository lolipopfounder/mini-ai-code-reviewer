import { create } from 'zustand'
import { lint } from './api'
import type { Issue, Language } from './types'

interface ReviewState {
  language: Language
  code: string
  isLoading: boolean
  error: string
  issues: Issue[]
  cached: boolean
  reviewed: boolean
  activeIssue: number | null

  setLanguage: (language: Language) => void
  setCode: (code: string) => void
  setActiveIssue: (index: number | null) => void
  submit: () => Promise<void>
}

export const useReviewStore = create<ReviewState>((set, get) => ({
  language: 'python',
  code: '',
  isLoading: false,
  error: '',
  issues: [],
  cached: false,
  reviewed: false,
  activeIssue: null,

  setLanguage: (language) => {
    set({ language: language, issues: [], error: '', cached: false, reviewed: false, activeIssue: null })
  },

  setCode: (code) => {
    set({ code: code, issues: [], error: '', cached: false, reviewed: false, activeIssue: null })
  },

  setActiveIssue: (index) => {
    set({ activeIssue: index })
  },

  submit: async () => {
    set({ isLoading: true, error: '', activeIssue: null })

    const language = get().language
    const code = get().code

    try {
      const result = await lint(language, code)
      set({ issues: result.issues, cached: result.cache, reviewed: true })
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Something went wrong'
      set({ error: message, issues: [], cached: false, reviewed: false })
    }

    set({ isLoading: false })
  },
}))
