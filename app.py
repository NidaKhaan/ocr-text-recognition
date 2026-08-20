import streamlit as st
from PIL import Image
import tempfile
import os
import json

from ocr_engine import extract_text

st.set_page_config(page_title="OCR Text Extractor", layout="centered")

st.title("OCR Text Extractor")
st.caption("Upload an image and extract readable text using EasyOCR.")

LANG_OPTIONS = {"English": "en", "Urdu": "ur"}

min_confidence = st.slider("Minimum confidence", 0.0, 1.0, 0.5, 0.05)
preprocess = st.checkbox("Apply preprocessing (recommended)", value=True)
selected_langs = st.multiselect("Languages", list(LANG_OPTIONS.keys()), default=["English"])
langs = [LANG_OPTIONS[l] for l in selected_langs] or ["en"]

uploaded_files = st.file_uploader(
    "Upload image(s)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)

if uploaded_files:
    all_results = {}

    for uploaded_file in uploaded_files:
        st.subheader(uploaded_file.name)
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

        # extract_text() expects a file path, so save the upload to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name

        with st.spinner("Running OCR..."):
            results = extract_text(tmp_path, preprocess=preprocess, langs=langs)

        os.remove(tmp_path)

        filtered = [r for r in results if r["confidence"] >= min_confidence]
        all_results[uploaded_file.name] = filtered

        if filtered:
            st.table(filtered)
        else:
            st.info("No text detected above this confidence threshold.")

    st.divider()
    st.subheader("Export results")

    json_data = json.dumps(all_results, indent=2, ensure_ascii=False)
    st.download_button(
        "Download as JSON",
        data=json_data,
        file_name="ocr_results.json",
        mime="application/json",
    )

    txt_lines = []
    for name, results in all_results.items():
        txt_lines.append(f"--- {name} ---")
        for r in results:
            txt_lines.append(f"[{r['confidence']:.2f}] {r['text']}")
        txt_lines.append("")
    st.download_button(
        "Download as TXT",
        data="\n".join(txt_lines),
        file_name="ocr_results.txt",
        mime="text/plain",
    )
else:
    st.info("Upload one or more images to get started.")