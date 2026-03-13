# AI-Driven Blood Group Detection (Flask + React)

This project serves your trained model (`.tflite` / `.keras`) behind a **Flask API** and provides a **React** UI to:

- Predict **ABO blood group** from a blood sample image (AI-assisted screening)
- Provide **multi-agent style cross-verification** (image quality + multiple augmented votes + consensus + confidence + safety rules)
- Run additional **Hemoglobin (Hb)** checks (rule-based)
- Provide **RBC/WBC** rough estimates from microscope images (simple OpenCV heuristics; demo only)
- **Malaria Detection**: High-accuracy analysis for Plasmodium parasites in blood smear images.
- **Blood Cancer Detection**: Deep CNN analysis of cell morphology to detect indications of malignancy.

## Tech stack

- **Backend**: Python, Flask, OpenCV, NumPy, TensorFlow (for TFLite inference)
- **Frontend**: React (Vite + TypeScript)

## 1) Backend setup

From the repo root:

```bash
cd backend
rmdir /s /q .venv
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt  or  pip install -r locked_requirements.txt
python app.py
```

Backend will run at `http://localhost:5000`.

### Model paths

Edit `backend/.env` if your files are not at:

- `MODEL_TFLITE_PATH=C:\\Users\\navin\\Downloads\\blood_group_model.tflite`
- `LABELS_PATH=C:\\Users\\navin\\Downloads\\labels (2).json`

You can verify the model loads:

- `GET http://localhost:5000/api/model`

## 2) Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at `http://localhost:5173` and call the backend at `http://localhost:5000`.

## 3) Model analysis report

After installing backend dependencies:

```bash
cd backend
.venv\\Scripts\\python tools\\analyze_model.py
```

This writes `backend/model_report.json` with:
- TensorFlow version used
- TFLite tensor shapes/dtypes
- Keras input/output + parameter count (if the `.keras` path is available)

## Safety note

This system is designed as an **AI-assisted preliminary screening tool**. It does **not** replace certified laboratory testing.

