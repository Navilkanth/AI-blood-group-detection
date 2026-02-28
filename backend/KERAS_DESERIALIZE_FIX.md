# Fixing `.keras` deserialization (legacy → Keras 3 compatible)

## Why it fails

Your file `blood_group_model (1).keras` was saved with **legacy Keras v2 serialization** that references modules like:

- `keras.src.engine.functional`

In **TensorFlow 2.20 (Keras 3)** these legacy module paths are no longer importable, so `load_model()` fails.

## The fix (safe + recommended)

Convert the legacy `.keras` once using **Python 3.10 + TensorFlow 2.15**, export to **SavedModel**, then wrap to a **Keras 3 `.keras`**.

After this you’ll have a new file that loads in TF 2.20 without errors:

- `backend/converted/model_keras3.keras`

## Step-by-step (Windows)

From repo root:

### 1) Create a Python 3.10 conversion environment

```bash
cd backend
py -3.10 -m venv .venv310
.\.venv310\Scripts\python -m pip install --upgrade pip
.\.venv310\Scripts\pip install "tensorflow==2.15.1"
```

### 2) Export SavedModel from the legacy `.keras`

```bash
.\.venv310\Scripts\python tools\export_savedmodel_from_legacy_keras.py ^
  --in-keras "C:\Users\navin\Downloads\blood_group_model (1).keras" ^
  --out-savedmodel ".\converted\saved_model"
```

### 3) Wrap SavedModel into a Keras 3 `.keras` (current backend env)

```bash
.\.venv\Scripts\python tools\wrap_savedmodel_to_keras3.py ^
  --in-savedmodel ".\converted\saved_model" ^
  --out-keras ".\converted\model_keras3.keras"
```

### 4) Verify it loads (TF 2.20)

```bash
.\.venv\Scripts\python -c "import tensorflow as tf; m=tf.keras.models.load_model(r'backend\\converted\\model_keras3.keras', compile=False); print('loaded', [t.shape for t in m.inputs], [t.shape for t in m.outputs])"
```

## Important note

For production serving, **TFLite** is still the simplest/fastest path (and the Flask API already uses `blood_group_model.tflite`).

