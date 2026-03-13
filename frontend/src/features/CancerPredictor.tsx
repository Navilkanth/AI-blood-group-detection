import { useMemo, useState } from 'react'
import { apiUrl } from '../api'

type CancerResult = {
    success: boolean
    prediction_id: string
    timestamp: string
    prediction: {
        label: string
        confidence: number
        raw_scores: number[]
    }
}

export function CancerPredictor() {
    const [file, setFile] = useState<File | null>(null)
    const [busy, setBusy] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [result, setResult] = useState<CancerResult | null>(null)

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
            const res = await fetch(apiUrl('/api/predict-cancer'), {
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
                    <h2 className="h2">Blood Cancer Detection (CNN)</h2>
                    <p className="muted">
                        Deep Learning analysis of blood cell morphology to detect indications of leukemia or other blood cancers.
                    </p>
                </div>
            </div>

            <div className="grid2">
                <div className="card">
                    <div className="sectionTitle">Cell Sample</div>
                    <div className="uploadControl">
                        <input
                            type="file"
                            accept="image/*"
                            onChange={(e) => setFile(e.target.files?.[0] || null)}
                            className="fileInput"
                            id="cancer-upload"
                        />
                        <label htmlFor="cancer-upload" className="fileLabel">
                            {file ? 'Change Image' : 'Select Cell Image'}
                        </label>
                    </div>

                    {previewUrl && (
                        <div className="previewFrame">
                            <img src={previewUrl} alt="Preview" className="imgPreview" />
                        </div>
                    )}

                    <button className="primary full" onClick={onSubmit} disabled={busy || !file}>
                        {busy ? 'Analyzing...' : 'Run Analysis'}
                    </button>

                    {error && <div className="errorBox">{error}</div>}
                </div>

                <div className="card">
                    <div className="sectionTitle">Diagnostic Summary</div>
                    {!result && !busy && (
                        <div className="emptyState">Upload high-resolution cell imagery for analysis.</div>
                    )}
                    {busy && <div className="loadingState">Deep CNN analysis in progress...</div>}

                    {result && (
                        <div className="resultContent">
                            <div className="resultMain">
                                <div className="label">Classification:</div>
                                <div className={`value big ${result.prediction.label === 'Cancer' ? 'danger' : 'success'}`}>
                                    {result.prediction.label}
                                </div>
                            </div>

                            <div className="resultMain">
                                <div className="label">Confidence:</div>
                                <div className="value">{(result.prediction.confidence * 100).toFixed(1)}%</div>
                            </div>

                            <div className="hr" />

                            <div className="section">
                                <div className="sectionTitle">Metadata</div>
                                <div className="muted">Tracking ID: {result.prediction_id}</div>
                                <div className="muted">Analysis Time: {new Date(result.timestamp).toLocaleString()}</div>
                            </div>

                            <div className="hr" />

                            <div className="warnBox">
                                <strong>Important:</strong> This tool is for educational and research purposes. A definitive diagnosis requires a bone marrow biopsy and professional clinical evaluation.
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
