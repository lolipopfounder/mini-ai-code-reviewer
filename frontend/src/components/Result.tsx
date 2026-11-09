import { useReviewStore } from '../store'

function Code({ text, start }: { text: string; start: number }) {
  return (
    <pre>
      {text.split('\n').map((line, i) => (
        <div key={i}>
          <span className="num">{start + i}</span>
          {line}
        </div>
      ))}
    </pre>
  )
}

function Result() {
  const code = useReviewStore((state) => state.code)
  const issues = useReviewStore((state) => state.issues)
  const cached = useReviewStore((state) => state.cached)
  const error = useReviewStore((state) => state.error)
  const isLoading = useReviewStore((state) => state.isLoading)
  const reviewed = useReviewStore((state) => state.reviewed)

  if (isLoading) return <p>Loading...</p>
  if (error) return <p>Error: {error}</p>
  if (!reviewed) return null
  const cacheText = <p>result from cache: {cached ? 'True' : 'False'}</p>

  if (issues.length === 0) {
    return (
      <div>
        <p>No issues found</p>
        {cacheText}
      </div>
    )
  }

  const lines = code.split('\n')

  return (
    <div>
      <h2>Result</h2>
      {cacheText}
      {issues.map((issue, i) => (
        <div key={i} className="issue">
          <h3>Severity: {issue.severity}</h3>
          <p>
            Line(s): {issue.line_start === issue.line_end
              ? issue.line_start
              : issue.line_start + ' - ' + issue.line_end}
          </p>
          <p>{issue.explanation}</p>
          <div className="compare">
            <div className="old-code">
              <p>Your code</p>
              <Code
                text={lines.slice(issue.line_start - 1, issue.line_end).join('\n')}
                start={issue.line_start}
              />
            </div>
            <div className="new-code">
              <p>Suggested fix</p>
              <Code text={issue.fix} start={issue.line_start} />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default Result
