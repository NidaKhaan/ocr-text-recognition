import easyocr
from preprocessing import preprocess_image

_reader = None


def get_reader():
    """Load the EasyOCR English model once and reuse it across calls."""
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'])
    return _reader


def extract_text(image_path: str, preprocess: bool = True) -> list[dict]:
    """
    Run OCR on an image and return results in reading order.

    If preprocess=True (default), applies grayscale, upscale, deskew,
    conditional denoise/sharpen, and contrast enhancement before OCR.

    Returns a list of dicts: {"text": str, "confidence": float}
    """
    reader = get_reader()
    image_input = preprocess_image(image_path) if preprocess else image_path
    results = reader.readtext(image_input)

    def sort_key(detection):
        bbox, text, confidence = detection
        top_left = bbox[0]
        return (round(top_left[1] / 20), top_left[0])

    results_sorted = sorted(results, key=sort_key)

    return [
        {"text": text, "confidence": round(confidence, 2)}
        for bbox, text, confidence in results_sorted
    ]