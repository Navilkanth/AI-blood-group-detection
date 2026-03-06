import { useEffect, useState } from 'react'
import { apiUrl } from '../api'

type HistoryRecord = {
    _id: string
    timestamp: string
    prediction: {
        label: string
        confidence: number
    }
    agents: {
        imageQuality: {
            ok: boolean
        }
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

    return (
        <div className="panel">
            <div className="panelHeader">
                <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <h2 className="h2" style={{ margin: 0 }}>Patient Records ({dbStatus?.type || 'DB'})</h2>
                        {dbStatus && (
                            <div className={`db-indicator ${dbStatus.connected ? 'online' : 'offline'}`}>
                                {dbStatus.connected ? `● ${dbStatus.type || 'Connected'}` : '● Offline'}
                            </div>
                        )}
                    </div>
                    <p className="muted" style={{ marginTop: '4px' }}>
                        {dbStatus?.connected
                            ? `Storage: ${dbStatus.database} > ${dbStatus.collection}`
                            : 'Database connection missing'}
                    </p>
                </div>
                <button className="primary small" onClick={fetchHistory} disabled={busy}>
                    {busy ? 'Refreshing...' : 'Refresh'}
                </button>
            </div>

            {error && <div className="errorBox">{error}</div>}

            <div className="card">
                {records.length === 0 && !busy ? (
                    <div className="muted emptyState">No records found. Perform a prediction to save it to the database.</div>
                ) : (
                    <div className="tableWrap">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>ID</th>
                                    <th>Blood Group</th>
                                    <th>Confidence</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {records.map((r) => (
                                    <tr key={r._id}>
                                        <td>{new Date(r.timestamp).toLocaleString()}</td>
                                        <td className="small muted">{r._id.slice(-8)}</td>
                                        <td>
                                            <span className="big">{r.prediction.label}</span>
                                        </td>
                                        <td>{(r.prediction.confidence * 100).toFixed(1)}%</td>
                                        <td>
                                            {r.agents.medicalRules.allowResult ? (
                                                <span className="tag success">Result Allowed</span>
                                            ) : (
                                                <span className="tag warn" title={r.agents.medicalRules.issues.join(', ')}>
                                                    Blocked
                                                </span>
                                            )}
                                        </td>
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
        .table th, .table td { padding: 12px; border-bottom: 1px solid #eee; }
        .table th { color: #666; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
        .emptyState { padding: 3rem; text-align: center; }
        .tag { padding: 4px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }
        .tag.success { background: #e6ffed; color: #22863a; }
        .tag.warn { background: #fff5f5; color: #cb2431; }
        .db-indicator { padding: 4px 10px; border-radius: 20px; font-size: 0.7rem; font-weight: bold; text-transform: uppercase; }
        .db-indicator.online { background: #dcffe4; color: #1a7f37; border: 1px solid #2da44e; }
        .db-indicator.offline { background: #ffeef0; color: #cf222e; border: 1px solid #d73a49; }
      `}</style>
        </div>
    )
}
