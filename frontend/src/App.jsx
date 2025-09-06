import React, { useState } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setResult(null)
    if (!file) {
      setError('Please choose a PDF file first.')
      return
    }
    const form = new FormData()
    form.append('pdf', file)
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/summarize`, {
        method: 'POST',
        body: form
      })
      if (!res.ok) {
        const data = await res.json().catch(() => ({}))
        throw new Error(data.detail || `Request failed with ${res.status}`)
      }
      const data = await res.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Something went wrong.')
    } finally {
      setLoading(false)
    }
  }

  const onCopy = async () => {
    if (!result) return
    const toCopy = `# ${result.title}\n\n${result.summary}\n\nTags: ${result.tags.join(', ')}`
    try {
      await navigator.clipboard.writeText(toCopy)
      alert('Copied to clipboard!')
    } catch {
      alert('Copy failed.')
    }
  }

  const onDownload = () => {
    if (!result) return
    const blob = new Blob(
      [
        `Title: ${result.title}\n\nSummary:\n${result.summary}\n\nTags: ${result.tags.join(', ')}`
      ],
      { type: 'text/plain' }
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = (result.title || 'summary').replace(/[^a-z0-9\-]+/gi, '_') + '.txt'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="container">
      <h1>Legal PDF Summarizer</h1>
      <form onSubmit={handleSubmit} className="card">
        <label className="file-label">
          <span>Choose PDF</span>
          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
        </label>
        <button type="submit" disabled={loading}>
          {loading ? 'Summarizing…' : 'Summarize PDF'}
        </button>
        {loading && <div className="spinner" aria-label="Loading"></div>}
      </form>

      {error && <div className="error">{error}</div>}

      {result && (
        <div className="result card">
          <h2>{result.title}</h2>
          <p className="muted">Tags: {result.tags.join(', ')}</p>
          <pre className="summary">{result.summary}</pre>
          <div className="actions">
            <button onClick={onCopy}>Copy</button>
            <button onClick={onDownload}>Download</button>
          </div>
        </div>
      )}

      <footer>
        <p>Point the app to your API by setting <code>VITE_API_BASE</code> in <code>.env</code>.</p>
      </footer>
    </div>
  )
}
