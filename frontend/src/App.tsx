import LanguageSelector from './components/LanguageSelector'
import CodeInput from './components/CodeInput'
import Result from './components/Result'

function App() {
  return (
    <div>
      <h1>Mini-AI Code Reviewer</h1>
      <LanguageSelector />
      <CodeInput />
      <Result />
    </div>
  )
}

export default App
