export type Language = 'python' | 'javascript' | 'typescript'
export type Severity = 'high' | 'medium' | 'low'

export interface Issue {
  line_start: number
  line_end: number
  severity: Severity
  explanation: string
  fix: string
}

export interface LintResponse {
  issues: Issue[]
  cache: boolean
}
