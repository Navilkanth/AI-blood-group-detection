# Model analysis (from `blood_group_model.tflite` + `labels (2).json`)

## Runtime versions

- **TensorFlow (serving env)**: `2.20.0`
- **Inference runtime used by backend**: **TFLite** (via `tensorflow.lite.Interpreter`)

## Labels (class order)

From `labels (2).json`:

- `0 -> A`
- `1 -> AB`
- `2 -> B`
- `3 -> O`

## TFLite input / output

- **Input tensor**
  - **name**: `serving_default_input_1:0`
  - **shape**: `[1, 224, 224, 3]` (NHWC)
  - **dtype**: `float32`
- **Output tensor**
  - **name**: `StatefulPartitionedCall:0`
  - **shape**: `[1, 4]`
  - **dtype**: `float32`

## Preprocessing used by this project

The Flask backend does:

- Read image bytes → **EXIF-corrected RGB**
- Resize to **224×224**
- Convert to float32 and scale to **[0, 1]** via `x = x / 255.0`

## Output interpretation

The backend treats the output as a **probability vector** over 4 classes.  
If the output does not look like probabilities (values outside [0,1] or sum not close to 1), it applies a **softmax**.

## `.keras` compatibility note

Your `.keras` file failed to load in this environment due to a **Keras serialization mismatch** (`keras.src.engine.functional` import error).

Practical recommendation:

- Use the **`.tflite`** model for serving (this project already does).
- If you must load the `.keras` model, recreate the training/export environment to match the original Keras/TensorFlow version, then re-export to `.tflite` (or re-save the `.keras` in the newer format).

