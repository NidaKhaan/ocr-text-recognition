import easyocr
from preprocessing import preprocess_image

_reader = None
_reader_langs = None


def get_reader(langs: list[str] = None):
    """
    Load the EasyOCR model for the given language list, reusing it if the
    language selection hasn't changed since the last call.
    """
    global _reader, _reader_langs
    if langs is None:
        langs = ['en']

    if _reader is None or _reader_langs != langs:
        _reader = easyocr.Reader(langs)
        _reader_langs = langs

    return _reader


def extract_text(image_path: str, preprocess: bool = True, langs: list[str] = None) -> list[dict]:
    """
    Run OCR on an image and return results in reading order.

    langs: list of EasyOCR language codes, e.g. ['en'], ['en', 'ur'].
           Defaults to English only if not specified.

    If preprocess=True (default), applies grayscale + upscale + contrast
    enhancement before running OCR, which improves accuracy on small,
    low-contrast, or compressed images.

    Returns a list of dicts: {"text": str, "confidence": float}
    """
    reader = get_reader(langs)
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