import { useState } from 'react'
import { apiUrl } from '../api'

type ApiErrorPayload = { error?: string }

type HbResult = {
  hb_g_dl: number
  sex: 'male' | 'female' | 'other'
  referenceRange: { low: number; high: number }
  status: 'low' | 'normal' | 'high'
  note: string
}

export function HemoglobinCheck() {
  const [hb, setHb] = useState('13.5')
  const [sex, setSex] = useState<'male' | 'female' | 'other'>('other')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<HbResult | null>(null)

  async function onCheck() {
    setError(null)
    setResult(null)
    setBusy(true)
    try {
      const res = await fetch(apiUrl('/api/check/hemoglobin'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ hb_g_dl: hb, sex }),
      })
      const data: unknown = await res.json()
      const payload = data as ApiErrorPayload
      if (!res.ok) {
        setError(payload?.error ?? 'Request failed')
        return
      }
      setResult(data as HbResult)
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
          <h2 className="h2">Hemoglobin (Hb) check</h2>
          <p className="muted">Rule-based reference range check (not a diagnosis).</p>
        </div>
      </div>

      <div className="grid2">
        <div className="card">
          <div className="field">
            <label className="label">Hemoglobin (g/dL)</label>
            <input value={hb} onChange={(e) => setHb(e.target.value)} inputMode="decimal" />
          </div>
          <div className="field">
            <label className="label">Sex (for reference range)</label>
            <select
              value={sex}
              onChange={(e) => setSex(e.target.value as 'male' | 'female' | 'other')}
            >
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other / Prefer not to say</option>
            </select>
          </div>
          <button className="primary" onClick={onCheck} disabled={busy} type="button">
            {busy ? 'Checking…' : 'Check'}
          </button>
          {error ? <div className="errorBox">{error}</div> : null}
        </div>

        <div className="card">
          {!result ? (
            <div className="muted">Result will appear here.</div>
          ) : (
            <>
              <div className="resultTop">
                <div className="resultLabel">
                  <div className="pill">Status</div>
                  <div className="big">{result.status.toUpperCase()}</div>
                </div>
                <div className="resultMeta">
                  <div>
                    <div className="k">Hb</div>
                    <div className="v">{result.hb_g_dl.toFixed(2)} g/dL</div>
                  </div>
                  <div>
                    <div className="k">Ref range</div>
                    <div className="v">
                      {result.referenceRange.low}–{result.referenceRange.high} g/dL
                    </div>
                  </div>
                </div>
              </div>
              <div className="hr" />
              <div className="muted small">{result.note}</div>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

