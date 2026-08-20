# OCR Text Extractor

A confidence-scored OCR utility for extracting text from images — built as a real tool, not a demo. Supports single images and batch folders, exports to JSON/TXT, and ships with a web UI for interactive use.

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
[![Streamlit](https://img.shields.io/badge/streamlit-deployed-FF4B4B?logo=streamlit&logoColor=white)](https://ocr-text-recognition-fzmkfhjbgfikwfbbqhde5m.streamlit.app/)
![EasyOCR](https://img.shields.io/badge/OCR-EasyOCR-6366F1)
![License(https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)

**[Live demo](https://ocr-text-recognition-fzmkfhjbgfikwfbbqhde5m.streamlit.app/)**


---

## What it does

Given an image (or a folder of images), this tool extracts readable text along with a per-line confidence score, in correct top-to-bottom reading order. It's built around a core insight validated during development: **confidence score is a reliable signal for filtering unreliable extractions** — low-confidence lines are consistently garbage, high-confidence lines are consistently correct. The `--min-confidence` threshold (CLI and UI) makes this actionable instead of just informational.

## Features

- **Batch processing** — point at a single image or a folder
- **Confidence filtering** — drop low-quality detections below a configurable threshold
- **Exportable output** — `.txt` or `.json`
- **Image preprocessing** — grayscale, upscaling, CLAHE contrast enhancement (proven to improve accuracy — see Evaluation below)
- **Web UI** — drag-and-drop upload, adjustable confidence slider, visual confidence bars per line, downloadable results
- **CLI** — scriptable, for batch/automated use

## Screenshot


## Architecture

```
Input image(s) (file or folder)
        │
        ▼
preprocessing.py   → grayscale, upscale, CLAHE contrast enhancement
        │
        ▼
ocr_engine.py       → EasyOCR inference (cached model), reading-order sort
        │
        ├──► ocr.py   (CLI: batch processing, confidence filter, export)
        │
        └──► app.py   (Streamlit: upload, visualize, export)
```

`ocr_engine.py` is the single shared core — both the CLI and the web app call the same `extract_text()` function, so OCR logic is implemented and tested once, not duplicated per interface.

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| OCR engine | [EasyOCR](https://github.com/JaidedAI/EasyOCR) | Pure-pip install (no system binary dependency, unlike Tesseract), stronger accuracy on varied real-world fonts and backgrounds |
| Preprocessing | OpenCV (headless) | Industry-standard image processing; `-headless` build avoids GUI dependencies that break on cloud deployment |
| Web UI | Streamlit | Fast to build, deploys directly to Streamlit Community Cloud |
| Runtime | CPU only | Inference on single images is fast enough on CPU; no GPU/Colab dependency for a tool of this scope |

## Setup

```bash
git clone https://github.com/NidaKhaan/ocr-text-recognition
cd ocr-text-recognition
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
```

First run downloads EasyOCR's model weights (~100MB, one-time) and caches them locally — subsequent runs load instantly from cache.

## Usage

### CLI

```bash
# Single image
python ocr.py --input samples/receipt.jpg

# Batch folder, with confidence filter and export
python ocr.py --input samples/ --min-confidence 0.5 --output results.json

# Disable preprocessing (for comparison/debugging)
python ocr.py --input samples/receipt.jpg --no-preprocess
```

| Flag | Description |
|---|---|
| `--input` | Path to an image file or a folder of images (required) |
| `--min-confidence` | Drop results below this confidence, 0.0–1.0 (default: 0.0) |
| `--output` | Export path, `.json` or `.txt` (optional) |
| `--no-preprocess` | Skip preprocessing step (default: preprocessing on) |

### Web app

```bash
streamlit run app.py
```

Upload one or more images, adjust the confidence slider, and download results as JSON or TXT.

## Evaluation

Tested against three varied real-world samples — not just a single clean case — to get an honest picture of where the tool performs well and where it doesn't.

| Sample | Type | Result at 0.5 confidence threshold |
|---|---|---|
| Book page scan | Clean, single-column, serif print | 13/14 lines correct; near-perfect after preprocessing |
| Restaurant receipt | Photo, mixed print quality, numeric fields | Item names and totals mostly correct (0.9+ confidence); a few numeric fields garbled at lower confidence, correctly flagged by the threshold |
| Web page screenshot | Small sans-serif font, 3-column grid layout | Improved from 3/5 to 5/5 correct lines after preprocessing (CLAHE contrast enhancement) |

**Preprocessing impact (measured, not assumed):** on the hardest sample (web screenshot), preprocessing improved accuracy from 3/5 to 5/5 correct lines at the same confidence threshold, and additionally recovered one previously-undetected line. Verified via `--no-preprocess` A/B comparison — not a subjective judgment call.

## Known limitations

- **Multi-column layout ordering.** Text is sorted top-to-bottom by vertical position, which works well for single-column documents but does not reconstruct true reading order across multi-column layouts (e.g., side-by-side grid sections). This is a document layout analysis problem, deliberately out of scope for this tool's current version.
- **Font/ligature misreads.** Certain letter combinations (e.g., "fl", "ti") are occasionally misread on some fonts, particularly in low-contrast source images.
- **Multilingual support was evaluated and descoped.** EasyOCR's Urdu recognition was tested and found unreliable on Nastaliq-style script (confidence consistently below 0.3, vs. 0.7+ typical for English), confirmed via preprocessing on/off comparison to rule out pipeline bugs. This is a documented limitation of the underlying model's non-Latin script support, not specific to this tool. English-only was chosen deliberately to keep quality high rather than ship a broken multilingual feature.
- **CPU inference only.** No GPU acceleration; each image takes a few seconds to process. Acceptable for this tool's scope (single images / small batches), not intended for high-throughput production use.

## Project structure

```
ocr-text-recognition/
├── ocr_engine.py       # Core OCR logic (shared by CLI and web app)
├── preprocessing.py    # Image preprocessing pipeline
├── ocr.py              # CLI entry point
├── app.py              # Streamlit web app
├── requirements.txt
├── samples/             # Test images used for evaluation
└── README.md
```

## Future improvements

- Document layout analysis for proper multi-column reading order
- Configurable preprocessing (deskew, denoise) validated against real blurry/tilted samples
- PDF input support
- Batch export as a single combined report

## Author

Nida Sheraz