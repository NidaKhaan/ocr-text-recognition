import cv2
import numpy as np


def preprocess_image(image_path: str, upscale_min_width: int = 1000) -> np.ndarray:
    """
    Preprocess an image to improve OCR accuracy:
    - Convert to grayscale
    - Upscale if narrower than upscale_min_width (helps detect small text)
    - Apply CLAHE contrast enhancement

    Returns a processed image as a numpy array, ready to pass into EasyOCR.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    if width < upscale_min_width:
        scale = upscale_min_width / width
        new_size = (int(width * scale), int(height * scale))
        gray = cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    return enhanced