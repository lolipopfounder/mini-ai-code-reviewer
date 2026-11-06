import type { Language, LintResponse } from './types'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function getErrorMessage(res: Response) {
  try {
    const data = await res.json()
    if (data.error) {
      return data.error
    }
    if (data.detail && data.detail.length > 0) {
      return data.detail[0].msg
    }
  } catch (err) {
    console.log('could not read error json', err)
  }
  return 'Something went wrong (status ' + res.status + ')'
}

export async function lint(language: Language, code: string) {
  let res
  try {
    res = await fetch(API_URL + '/lint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ language: language, code: code }),
    })
  } catch (err) {
    console.log(err)
    throw new Error('Cannot reach the server', { cause: err })
  }

  if (!res.ok) {
    const message = await getErrorMessage(res)
    throw new Error(message)
  }

  const data: LintResponse = await res.json()
  return data
}

export async function getLanguages() {
  let res
  try {
    res = await fetch(API_URL + '/languages')
  } catch (err) {
    console.log(err)
    throw new Error('Cannot reach the server', { cause: err })
  }

  if (!res.ok) {
    const message = await getErrorMessage(res)
    throw new Error(message)
  }

  const data = await res.json()
  const languages: Language[] = data.languages
  return languages
}
