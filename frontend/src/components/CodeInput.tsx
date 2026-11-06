import CodeMirror from '@uiw/react-codemirror'
import { useReviewStore } from '../store'

function CodeInput() {
  const code = useReviewStore((state) => state.code)
  const setCode = useReviewStore((state) => state.setCode)
  const submit = useReviewStore((state) => state.submit)
  const isLoading = useReviewStore((state) => state.isLoading)

  return (
    <div>
      <p>Paste your code here:</p>

      <CodeMirror
        value={code}
        height="300px"
        onChange={(value) => setCode(value)}
      />

      <button onClick={submit} disabled={isLoading || code.trim() === ''}>
        {isLoading ? 'Reviewing...' : 'Review Code'}
      </button>
    </div>
  )
}

export default CodeInput
