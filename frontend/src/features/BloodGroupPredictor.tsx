import { useMemo, useState } from 'react'
import { apiUrl } from '../api'

type ApiErrorPayload = {
  error?: string
  agents?: { medicalRules?: { issues?: string[] } }
  prediction?: unknown
}

type PredictOk = {
  prediction_id: string
  consensus_met: boolean
  reasoning: string
  blocked: boolean
  prediction: {
    label: string
    index: number
    confidence: number
    probs: Record<string, number>
  }
  haemoglobin?: {
    hb_g_dl: number
    status: string
    referenceRange: { low: number; high: number }
  }
  agents: {
    imageQuality: {
      ok: boolean
      blurScore: number
      reasons: string[]
    }
    medicalRules: {
      allowResult: boolean
      issues: string[]
    }
    confidenceAssessment: { score: number; level: string }
    visionVotes: Array<{ agent: string; label: string; confidence: number }>
    ethicsSafety: { disclaimer: string }
  }
  explainable: { summary: string }
  db_id?: string
}

export function BloodGroupPredictor() {
  const [file, setFile] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<PredictOk | null>(null)

  const previewUrl = useMemo(() => (file ? URL.createObjectURL(file) : null), [file])

  async function onSubmit() {
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
      const res = await fetch(apiUrl('/api/predict/blood-group'), {
        method: 'POST',
        body: form,
      })
      const data: unknown = await res.json()
      const payload = data as ApiErrorPayload
      if (!res.ok) {
        setError(payload?.error ?? payload?.agents?.medicalRules?.issues?.join('; ') ?? 'Request failed')
        if (payload?.prediction) setResult(data as PredictOk)
        return
      }
      setResult(data as PredictOk)
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Network error')
    } finally {
      setBusy(false)
    }
  }

  const probsSorted = useMemo(() => {
    if (!result) return []
    return Object.entries(result.prediction.probs).sort((a, b) => b[1] - a[1])
  }, [result])

  return (
    <div className="panel">
      <div className="panelHeader">
        <div>
          <h2 className="h2">Blood Group Prediction (ABO)</h2>
          <p className="muted">
            Upload a blood sample image. The system runs multi-step checks + consensus voting and returns a tentative ABO
            label with confidence.
          </p>
        </div>
      </div>

      <div className="grid2">
        <div className="card">
          <div className="field">
            <label className="label">Blood sample image</label>
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </div>
          {previewUrl ? (
            <div className="previewWrap">
              <img className="preview" src={previewUrl} alt="preview" />
            </div>
          ) : (
            <div className="previewEmpty">No image selected</div>
          )}

          <div className="row">
            <button className="primary" onClick={onSubmit} disabled={busy || !file} type="button">
              {busy ? 'Running…' : 'Predict'}
            </button>
            <a className="link" href={apiUrl('/api/model')} target="_blank" rel="noreferrer">
              Model status
            </a>
          </div>
          {error ? <div className="errorBox">{error}</div> : null}
        </div>

        <div className="card">
          {!result ? (
            <div className="muted">Prediction output will appear here.</div>
          ) : (
            <>
              <div className="resultTop">
                <div className="resultLabel">
                  <div className="pill">Predicted</div>
                  <div className="big">{result.prediction.label}</div>
                  {result.db_id && (
                    <div style={{ marginTop: '8px', fontSize: '0.7rem', color: '#22863a', fontWeight: 'bold' }}>
                      ✓ Saved to History
                    </div>
                  )}
                </div>
                <div className="resultMeta">
                  <div>
                    <div className="k">Confidence</div>
                    <div className="v">{(result.prediction.confidence * 100).toFixed(1)}%</div>
                  </div>
                  <div>
                    <div className="k">Consensus</div>
                    <div className={`v ${result.consensus_met ? 'text-success' : 'text-danger'}`}>
                      {result.consensus_met ? '5/5 VERIFIED' : 'CONFLICT'}
                    </div>
                  </div>
                </div>
              </div>

              {result.haemoglobin && (
                <div className="infoBox hbBox" style={{ marginTop: '1rem', background: '#f6f8fa', border: '1px solid #d0d7de', borderRadius: '8px', padding: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div className="k" style={{ fontSize: '0.75rem', color: '#666', textTransform: 'uppercase' }}>Estimated Haemoglobin</div>
                    <div className="tag" style={{
                      background: result.haemoglobin.status === 'normal' ? '#dafbe1' : '#ffeef0',
                      color: result.haemoglobin.status === 'normal' ? '#1a7f37' : '#cf222e',
                      fontSize: '0.7rem',
                      fontWeight: 'bold',
                      padding: '2px 6px',
                      borderRadius: '4px'
                    }}>{result.haemoglobin.status.toUpperCase()}</div>
                  </div>
                  <div className="v" style={{ fontSize: '1.2rem', fontWeight: 'bold', margin: '4px 0' }}>{result.haemoglobin.hb_g_dl.toFixed(1)} g/dL</div>
                  <div className="muted" style={{ fontSize: '0.75rem' }}>Ref: {result.haemoglobin.referenceRange.low}-{result.haemoglobin.referenceRange.high} g/dL</div>
                </div>
              )}

              <div className="status-banner" style={{
                padding: '12px',
                borderRadius: '8px',
                background: result.consensus_met ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                border: `1px solid ${result.consensus_met ? '#22c55e' : '#ef4444'}`,
                margin: '1rem 0',
                fontSize: '0.85rem'
              }}>
                <strong>ID:</strong> {result.prediction_id} | <strong>Status:</strong> {result.consensus_met ? 'Accepted' : 'Manual Review Required'}
              </div>

              <div className="hr" />

              <div className="section">
                <div className="sectionTitle">Explainable summary</div>
                <div className="muted">{result.explainable.summary}</div>
              </div>

              <div className="section">
                <div className="sectionTitle">Class probabilities</div>
                <div className="probs">
                  {probsSorted.map(([label, p]) => (
                    <div key={label} className="probRow">
                      <div className="probLabel">{label}</div>
                      <div className="probBar">
                        <div className="probFill" style={{ width: `${Math.max(0, Math.min(1, p)) * 100}%` }} />
                      </div>
                      <div className="probVal">{(p * 100).toFixed(1)}%</div>
                    </div>
                  ))}
                </div>
              </div>

              {!result.agents.imageQuality.ok ? (
                <div className="warnBox">
                  <div className="sectionTitle">Quality Guidance</div>
                  <ul>
                    {result.agents.imageQuality.reasons.map((r) => (
                      <li key={r}>{r}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              <div className="hr" />
              <div className="muted small">{result.agents.ethicsSafety.disclaimer}</div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
