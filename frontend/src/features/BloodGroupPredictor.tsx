import { useMemo, useState } from 'react'
import { apiUrl } from '../api'

type ApiErrorPayload = {
  error?: string
  agents?: { medicalRules?: { issues?: string[] } }
  prediction?: unknown
}

type PredictOk = {
  blocked: boolean
  prediction: {
    label: string
    index: number
    confidence: number
    probs: Record<string, number>
  }
  agents: {
    imageQuality: {
      ok: boolean
      blurScore: number
      brightnessMean: number
      contrastStd: number
      noiseScore: number
      reasons: string[]
    }
    medicalRules: {
      allowResult: boolean
      issues: string[]
      note: string
    }
    confidenceAssessment: { score: number; level: string }
    visionVotes: Array<{ agent: string; label: string; confidence: number }>
    ethicsSafety: { disclaimer: string; privacy: string }
  }
  explainable: { summary: string }
  model: { runtime: string; input_shape: number[]; input_dtype: string }
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
                      ✓ Saved to Atlas
                    </div>
                  )}
                </div>
                <div className="resultMeta">
                  <div>
                    <div className="k">Confidence</div>
                    <div className="v">{(result.prediction.confidence * 100).toFixed(1)}%</div>
                  </div>
                  <div>
                    <div className="k">Quality</div>
                    <div className="v">{result.agents.imageQuality.ok ? 'OK' : 'Needs retake'}</div>
                  </div>
                </div>
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
                  <div className="sectionTitle">Retake guidance</div>
                  <ul>
                    {result.agents.imageQuality.reasons.map((r) => (
                      <li key={r}>{r}</li>
                    ))}
                  </ul>
                </div>
              ) : null}

              <div className="section">
                <div className="sectionTitle">Agent votes</div>
                <div className="voteGrid">
                  {result.agents.visionVotes.map((v) => (
                    <div key={v.agent} className="voteCard">
                      <div className="voteAgent">{v.agent}</div>
                      <div className="votePick">{v.label}</div>
                      <div className="muted">{(v.confidence * 100).toFixed(1)}%</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="hr" />
              <div className="muted small">{result.agents.ethicsSafety.disclaimer}</div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

