import { useEffect, useState } from 'react'
import { apiUrl } from '../api'

type HistoryRecord = {
    _id: string
    prediction_id: string
    timestamp: string
    feature: string
    prediction?: {
        label: string
        confidence: number
    }
    haemoglobin?: {
        hb_g_dl: number
        status: string
    }
    analysis?: {
        rbcCount: number
        wbcCount: number
        totalCells: number
    }
    agents?: {
        medicalRules: {
            allowResult: boolean
            issues: string[]
        }
    }
}

export function History() {
    const [records, setRecords] = useState<HistoryRecord[]>([])
    const [dbStatus, setDbStatus] = useState<{ connected: boolean; type?: string; database?: string; collection?: string } | null>(null)
    const [busy, setBusy] = useState(false)
    const [error, setError] = useState<string | null>(null)

    async function checkDbStatus() {
        try {
            const res = await fetch(apiUrl('/api/db-status'))
            if (res.ok) {
                const data = await res.json()
                setDbStatus(data)
            }
        } catch (e) {
            console.error('Failed to check DB status', e)
        }
    }

    async function fetchHistory() {
        setBusy(true)
        setError(null)
        checkDbStatus()
        try {
            const res = await fetch(apiUrl('/api/history'))
            if (!res.ok) throw new Error('Failed to fetch history')
            const data = await res.json()
            setRecords(data.records || [])
        } catch (e: any) {
            setError(e.message)
        } finally {
            setBusy(false)
        }
    }

    useEffect(() => {
        fetchHistory()
    }, [])

    function renderFeatureValue(r: HistoryRecord) {
        if (r.feature === 'blood_group' || r.feature === 'malaria' || r.feature === 'cancer') {
            return (
                <div>
                    <span className="result-label">{r.prediction?.label}</span>
                    {r.prediction?.confidence && (
                        <div className="small muted">{(r.prediction.confidence * 100).toFixed(1)}% confidence</div>
                    )}
                </div>
            )
        }
        if (r.feature === 'hemoglobin') {
            return (
                <div>
                    <span className="result-label">{r.haemoglobin?.hb_g_dl} g/dL</span>
                    <div className={`small ${r.haemoglobin?.status === 'normal' ? 'text-success' : 'text-danger'}`}>
                        {r.haemoglobin?.status.toUpperCase()}
                    </div>
                </div>
            )
        }
        if (r.feature === 'cells') {
            return (
                <div>
                    <span className="result-label">{r.analysis?.totalCells} Cells</span>
                    <div className="small muted">RBC: {r.analysis?.rbcCount} | WBC: {r.analysis?.wbcCount}</div>
                </div>
            )
        }
        return <span className="muted">N/A</span>
    }

    function renderStatus(r: HistoryRecord) {
        if (r.feature === 'blood_group' && r.agents?.medicalRules) {
            return r.agents.medicalRules.allowResult ? (
                <span className="tag success">Screened</span>
            ) : (
                <span className="tag warn" title={r.agents.medicalRules.issues?.join(', ')}>
                    Blocked
                </span>
            )
        }
        return <span className="tag info">Completed</span>
    }

    return (
        <div className="panel">
            <div className="panelHeader">
                <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <h2 className="h2" style={{ margin: 0 }}>Patient Diagnostics History</h2>
                        {dbStatus && (
                            <div className={`db-indicator ${dbStatus.connected ? 'online' : 'offline'}`}>
                                {dbStatus.connected ? `● ${dbStatus.type || 'Connected'}` : '● Offline'}
                            </div>
                        )}
                    </div>
                    <p className="muted" style={{ marginTop: '4px' }}>
                        Full diagnostic records for all integrated features.
                    </p>
                </div>
                <button className="primary small" onClick={fetchHistory} disabled={busy}>
                    {busy ? 'Refreshing...' : 'Refresh'}
                </button>
            </div>

            {error && <div className="errorBox">{error}</div>}

            <div className="card">
                {records.length === 0 && !busy ? (
                    <div className="muted emptyState">No records found. Perform analysis to save history.</div>
                ) : (
                    <div className="tableWrap">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Timestamp</th>
                                    <th>Feature</th>
                                    <th>Analysis Result</th>
                                    <th>Status</th>
                                    <th>ID</th>
                                </tr>
                            </thead>
                            <tbody>
                                {records.map((r) => (
                                    <tr key={r._id || r.prediction_id}>
                                        <td>{new Date(r.timestamp).toLocaleString()}</td>
                                        <td>
                                            <span className="feature-pill">
                                                {(r.feature || 'unknown').replace('_', ' ').toUpperCase()}
                                            </span>
                                        </td>
                                        <td>{renderFeatureValue(r)}</td>
                                        <td>{renderStatus(r)}</td>
                                        <td className="small muted font-mono">{(r.prediction_id || r._id).slice(-8)}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>

            <style>{`
        .tableWrap { overflow-x: auto; margin-top: 1rem; }
        .table { width: 100%; border-collapse: collapse; text-align: left; }
        .table th, .table td { padding: 16px 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }
        .table th { color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 800; }
        .emptyState { padding: 3rem; text-align: center; }
        .tag { padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; }
        .tag.success { background: rgba(34, 197, 94, 0.1); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.2); }
        .tag.warn { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
        .tag.info { background: rgba(99, 102, 241, 0.1); color: #6366f1; border: 1px solid rgba(99, 102, 241, 0.2); }
        .db-indicator { padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; }
        .db-indicator.online { background: rgba(34, 197, 94, 0.1); color: #22c55e; border: 1px solid rgba(34, 197, 94, 0.2); }
        .db-indicator.offline { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); }
        .feature-pill { font-size: 0.65rem; background: rgba(255,255,255,0.05); padding: 2px 6px; border-radius: 4px; color: var(--text-muted); font-weight: 600; }
        .result-label { font-weight: 700; font-size: 1.1rem; color: var(--text-main); }
        .font-mono { font-family: monospace; }
      `}</style>
        </div>
    )
}
