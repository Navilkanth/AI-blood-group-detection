import { useState, useMemo } from 'react'
import { apiUrl } from '../api'


type HbResult = {
  hb_g_dl: number
  status: 'low' | 'normal' | 'high'
  referenceRange: { low: number; high: number }
  note: string
}

export function HemoglobinCheck() {
  const [file, setFile] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<HbResult | null>(null)

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file])

  async function onAnalyze() {
    setError(null)
    setResult(null)
    if (!file) {
      setError('Please choose a blood sample image.')
      return
    }
    setBusy(true)
    try {
      const form = new FormData()
      form.append('image', file)
      const res = await fetch(apiUrl('/api/check/hemoglobin'), { method: 'POST', body: form })
      const data: any = await res.json()
      if (!res.ok) {
        setError(data?.error ?? 'Analysis failed')
        return
      }
      if (data.haemoglobin) {
        setResult(data.haemoglobin as HbResult)
      } else {
        setResult(data as HbResult)
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Network error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="panel">
      <div className="panelHeader">
        <div>
          <h2 className="h2">Automated Hemoglobin (Hb) Analysis</h2>
          <p className="muted">
            Upload a blood sample image. The system will estimate Hb levels based on colorimetric analysis.
          </p>
        </div>
      </div>

      <div className="grid2">
        <div className="card">
          <div className="field">
            <label className="label">Sample image</label>
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
            {busy ? 'Analyzing…' : 'Estimate Hb'}
          </button>
          {error ? <div className="errorBox">{error}</div> : null}
        </div>

        <div className="card">
          {!result ? (
            <div className="muted">Output will appear here after analysis.</div>
          ) : (
            <>
              <div className="resultTop">
                <div className="resultLabel">
                  <div className="pill">Current Level</div>
                  <div className="big">{result.hb_g_dl.toFixed(1)} g/dL</div>
                </div>
                <div className="resultMeta">
                  <div>
                    <div className="k">Status</div>
                    <div className="v" style={{ fontWeight: 'bold', color: result.status === 'normal' ? '#22863a' : '#cb2431' }}>
                      {result.status.toUpperCase()}
                    </div>
                  </div>
                  <div>
                    <div className="k">Ref range</div>
                    <div className="v">{result.referenceRange.low}–{result.referenceRange.high}</div>
                  </div>
                </div>
              </div>
              <div className="hr" />
              <p className="small muted">{result.note}</p>
              <div className="infoBox small">
                <span>ℹ️</span> This is an AI-driven colorimetric estimate. Always cross-verify with clinical lab reports.
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
