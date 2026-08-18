import easyocr

_reader = None

def get_reader():
    """Load the EasyOCR model once and reuse it (avoids reloading on every call)."""
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'])
    return _reader

def extract_text(image_path: str) -> list[dict]:
    """
    Run OCR on an image and return results in reading order.

    Returns a list of dicts: {"text": str, "confidence": float}
    """
    reader = get_reader()
    results = reader.readtext(image_path)

    def sort_key(detection):
        bbox, text, confidence = detection
        top_left = bbox[0]
        return (round(top_left[1] / 20), top_left[0])

    results_sorted = sorted(results, key=sort_key)

    return [
        {"text": text, "confidence": round(confidence, 2)}
        for bbox, text, confidence in results_sorted
    ]