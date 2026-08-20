import streamlit as st
from PIL import Image
import tempfile
import os
import json

from ocr_engine import extract_text

st.set_page_config(page_title="OCR Text Extractor", layout="centered")

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0F1115;
    color: #E8E9ED;
}

h1, h2, h3 {
    font-family: 'Sora', sans-serif !important;
    color: #E8E9ED !important;
}

.app-title {
    font-family: 'Sora', sans-serif;
    font-weight: 700;
    font-size: 2rem;
    color: #E8E9ED;
    margin-bottom: 0.2rem;
}

.app-caption {
    color: #8B90A0;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}

[data-testid="stFileUploader"] {
    background-color: #1A1D24;
    border: 1px dashed #2A2E38;
    border-radius: 10px;
    padding: 1rem;
}

.result-card {
    background-color: #1A1D24;
    border: 1px solid #2A2E38;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}

.result-header {
    font-family: 'Sora', sans-serif;
    font-weight: 600;
    color: #E8E9ED;
    margin-bottom: 0.8rem;
    font-size: 1.1rem;
}

.line-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.35rem 0;
    border-bottom: 1px solid #21242C;
}

.line-row:last-child {
    border-bottom: none;
}

.line-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.88rem;
    color: #E8E9ED;
    flex: 1;
}

.conf-bar-track {
    width: 70px;
    height: 6px;
    background-color: #2A2E38;
    border-radius: 3px;
    overflow: hidden;
    flex-shrink: 0;
}

.conf-bar-fill {
    height: 100%;
    border-radius: 3px;
}

.conf-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.78rem;
    color: #8B90A0;
    width: 38px;
    flex-shrink: 0;
    text-align: right;
}

.empty-state {
    color: #8B90A0;
    font-size: 0.9rem;
    padding: 0.5rem 0;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown('<div class="app-title">OCR Text Extractor</div>', unsafe_allow_html=True)
st.markdown('<div class="app-caption">Upload an image and extract readable text, with confidence-scored results.</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    min_confidence = st.slider("Minimum confidence", 0.0, 1.0, 0.5, 0.05)
with col2:
    preprocess = st.checkbox("Apply preprocessing", value=True)

uploaded_files = st.file_uploader(
    "Upload image(s)",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
)


def confidence_color(confidence: float) -> str:
    if confidence >= 0.75:
        return "#34D399"  # emerald
    if confidence >= 0.4:
        return "#F59E0B"  # amber
    return "#EF4444"      # red


def render_results_card(filename: str, results: list[dict]):
    st.markdown(f'<div class="result-card"><div class="result-header">{filename}</div>', unsafe_allow_html=True)

    if not results:
        st.markdown('<div class="empty-state">No text detected above this confidence threshold.</div></div>', unsafe_allow_html=True)
        return

    rows_html = ""
    for r in results:
        color = confidence_color(r["confidence"])
        pct = int(r["confidence"] * 100)
        text = r["text"].replace("<", "&lt;").replace(">", "&gt;")
        rows_html += f"""
        <div class="line-row">
            <div class="line-text">{text}</div>
            <div class="conf-bar-track"><div class="conf-bar-fill" style="width:{pct}%; background-color:{color};"></div></div>
            <div class="conf-label">{r['confidence']:.2f}</div>
        </div>
        """
    st.markdown(rows_html + "</div>", unsafe_allow_html=True)


if uploaded_files:
    all_results = {}

    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
            image.save(tmp.name)
            tmp_path = tmp.name

        with st.spinner("Running OCR..."):
            results = extract_text(tmp_path, preprocess=preprocess)

        os.remove(tmp_path)

        filtered = [r for r in results if r["confidence"] >= min_confidence]
        all_results[uploaded_file.name] = filtered

        render_results_card(uploaded_file.name, filtered)

    st.divider()
    st.subheader("Export results")

    json_data = json.dumps(all_results, indent=2)
    st.download_button("Download as JSON", data=json_data, file_name="ocr_results.json", mime="application/json")

    txt_lines = []
    for name, results in all_results.items():
        txt_lines.append(f"--- {name} ---")
        for r in results:
            txt_lines.append(f"[{r['confidence']:.2f}] {r['text']}")
        txt_lines.append("")
    st.download_button("Download as TXT", data="\n".join(txt_lines), file_name="ocr_results.txt", mime="text/plain")
else:
    st.info("Upload one or more images to get started.")