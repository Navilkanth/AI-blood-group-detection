import { useMemo, useState } from 'react'
import { apiUrl } from '../api'

type ApiErrorPayload = { error?: string }

type CellsResult = {
  rbcCountEstimate: number
  wbcCountEstimate: number
  overlayPngBase64?: string
  notes: string[]
}

export function CellsAnalyzer() {
  const [file, setFile] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<CellsResult | null>(null)

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file])

  async function onAnalyze() {
    setError(null)
    setResult(null)
    if (!file) {
      setError('Please choose an image.')
      return
    }
    setBusy(true)
    try {
      const form = new FormData()
      form.append('image', file)
      const res = await fetch(apiUrl('/api/analyze/cells'), { method: 'POST', body: form })
      const data: unknown = await res.json()
      const payload = data as ApiErrorPayload
      if (!res.ok) {
        setError(payload?.error ?? 'Request failed')
        return
      }
      setResult(data as CellsResult)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Network error')
    } finally {
      setBusy(false)
    }
  }

  const overlayUrl = useMemo(() => {
    if (!result?.overlayPngBase64) return null
    return `data:image/png;base64,${result.overlayPngBase64}`
  }, [result])

  return (
    <div className="panel">
      <div className="panelHeader">
        <div>
          <h2 className="h2">RBC / WBC (image heuristic)</h2>
          <p className="muted">
            Upload a microscope image. This is a basic OpenCV estimate for demo purposes (not calibrated).
          </p>
        </div>
      </div>

      <div className="grid2">
        <div className="card">
          <div className="field">
            <label className="label">Microscope image</label>
            <input type="file" accept="image/*" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
          </div>
          {previewUrl ? (
            <div className="previewWrap">
              <img className="preview" src={previewUrl} alt="preview" />
            </div>
          ) : (
            <div className="previewEmpty">No image selected</div>
          )}
          <button className="primary" onClick={onAnalyze} disabled={busy || !file} type="button">
            {busy ? 'Analyzing…' : 'Analyze'}
          </button>
          {error ? <div className="errorBox">{error}</div> : null}
        </div>

        <div className="card">
          {!result ? (
            <div className="muted">Output will appear here.</div>
          ) : (
            <>
              <div className="resultTop">
                <div className="resultMeta">
                  <div>
                    <div className="k">RBC estimate</div>
                    <div className="v">{result.rbcCountEstimate}</div>
                  </div>
                  <div>
                    <div className="k">WBC estimate</div>
                    <div className="v">{result.wbcCountEstimate}</div>
                  </div>
                </div>
              </div>
              <div className="hr" />
              {overlayUrl ? (
                <div className="previewWrap">
                  <img className="preview" src={overlayUrl} alt="overlay" />
                </div>
              ) : null}
              <ul className="muted small">
                {result.notes.map((n) => (
                  <li key={n}>{n}</li>
                ))}
              </ul>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

