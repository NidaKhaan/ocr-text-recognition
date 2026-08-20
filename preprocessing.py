import cv2
import numpy as np


def estimate_blur(gray: np.ndarray) -> float:
    """
    Return the variance of the Laplacian of the image — a standard blur metric.
    Lower values indicate a blurrier image (less high-frequency detail/edges).
    """
    return cv2.Laplacian(gray, cv2.CV_64F).var()


def deskew(gray: np.ndarray) -> np.ndarray:
    """
    Detect and correct small rotational skew using the minimum-area bounding
    rectangle of thresholded foreground (text) pixels.
    """
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thresh > 0))

    if coords.shape[0] < 20:
        return gray  # not enough foreground pixels to estimate skew reliably

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 0.5 or abs(angle) > 15:
        return gray  # ignore negligible skew or implausible detection

    (h, w) = gray.shape
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        gray, matrix, (w, h),
        flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )


def preprocess_image(
    image_path: str,
    upscale_min_width: int = 1000,
    blur_threshold: float = 100.0,
    enable_deskew: bool = False,
    enable_sharpen: bool = False,
) -> np.ndarray:
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not read image: {image_path}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    height, width = gray.shape
    if width < upscale_min_width:
        scale = upscale_min_width / width
        new_size = (int(width * scale), int(height * scale))
        gray = cv2.resize(gray, new_size, interpolation=cv2.INTER_CUBIC)

    if enable_deskew:
        gray = deskew(gray)

    if enable_sharpen and estimate_blur(gray) < blur_threshold:
        gray = cv2.fastNlMeansDenoising(gray, h=10)
        sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        gray = cv2.filter2D(gray, -1, sharpen_kernel)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    return enhanced