import { useMemo, useState } from 'react'
import { apiUrl } from '../api'

type MalariaResult = {
    success: boolean
    prediction_id: string
    timestamp: string
    prediction: {
        label: string
        confidence: number
        raw_scores: number[]
    }
}

export function MalariaPredictor() {
    const [file, setFile] = useState<File | null>(null)
    const [busy, setBusy] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [result, setResult] = useState<MalariaResult | null>(null)

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
            const res = await fetch(apiUrl('/api/predict-malaria'), {
                method: 'POST',
                body: form,
            })
            const data = await res.json()
            if (!res.ok) {
                setError(data.error || 'Request failed')
                return
            }
            setResult(data)
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
                    <h2 className="h2">Malaria Parasite Detection</h2>
                    <p className="muted">
                        Analyzes thin blood smear images to detect Malaria parasites (Plasmodium species).
                    </p>
                </div>
            </div>

            <div className="grid2">
                <div className="card">
                    <div className="sectionTitle">Sample Image</div>
                    <div className="uploadControl">
                        <input
                            type="file"
                            accept="image/*"
                            onChange={(e) => setFile(e.target.files?.[0] || null)}
                            className="fileInput"
                            id="malaria-upload"
                        />
                        <label htmlFor="malaria-upload" className="fileLabel">
                            {file ? 'Change Image' : 'Select Blood Smear'}
                        </label>
                    </div>

                    {previewUrl && (
                        <div className="previewFrame">
                            <img src={previewUrl} alt="Preview" className="imgPreview" />
                        </div>
                    )}

                    <button className="primary full" onClick={onSubmit} disabled={busy || !file}>
                        {busy ? 'Analyzing...' : 'Run Detection'}
                    </button>

                    {error && <div className="errorBox">{error}</div>}
                </div>

                <div className="card">
                    <div className="sectionTitle">Detection Results</div>
                    {!result && !busy && (
                        <div className="emptyState">Upload an image and run detection to see results.</div>
                    )}
                    {busy && <div className="loadingState">Processing image...</div>}

                    {result && (
                        <div className="resultContent">
                            <div className="resultMain">
                                <div className="label">Status:</div>
                                <div className={`value big ${result.prediction.label === 'Parasitized' ? 'danger' : 'success'}`}>
                                    {result.prediction.label}
                                </div>
                            </div>

                            <div className="resultMain">
                                <div className="label">Confidence:</div>
                                <div className="value">{(result.prediction.confidence * 100).toFixed(1)}%</div>
                            </div>

                            <div className="hr" />

                            <div className="section">
                                <div className="sectionTitle">Report Details</div>
                                <div className="muted">ID: {result.prediction_id}</div>
                                <div className="muted">Date: {new Date(result.timestamp).toLocaleString()}</div>
                            </div>

                            <div className="hr" />

                            <div className="infoBox">
                                <strong>Medical Note:</strong> This is an AI-assisted screening tool. Results should be verified by a qualified pathologist via microscopy.
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
