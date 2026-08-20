import argparse
import os
import json
import logging
from ocr_engine import extract_text

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png")


def process_image(image_path: str, min_confidence: float, preprocess: bool) -> list[dict]:
    """Run OCR on one image and filter by confidence threshold."""
    results = extract_text(image_path, preprocess=preprocess)
    return [r for r in results if r["confidence"] >= min_confidence]


def collect_image_paths(input_path: str) -> list[str]:
    """Return a list of image file paths from a single file or a directory."""
    if os.path.isfile(input_path):
        return [input_path]
    if os.path.isdir(input_path):
        return [
            os.path.join(input_path, f)
            for f in sorted(os.listdir(input_path))
            if f.lower().endswith(SUPPORTED_EXTENSIONS)
        ]
    return []


def save_results(all_results: dict, output_path: str):
    """Save results as .txt or .json depending on file extension."""
    if output_path.endswith(".json"):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            for path, results in all_results.items():
                f.write(f"--- {path} ---\n")
                for r in results:
                    f.write(f"[{r['confidence']:.2f}] {r['text']}\n")
                f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Extract text from image(s) using OCR.")
    parser.add_argument("--input", required=True, help="Path to an image file or a folder of images")
    parser.add_argument("--min-confidence", type=float, default=0.0, help="Drop results below this confidence (0.0-1.0)")
    parser.add_argument("--output", help="Path to save results as .txt or .json (optional)")
    parser.add_argument("--no-preprocess", action="store_true", help="Disable image preprocessing")
    args = parser.parse_args()

    image_paths = collect_image_paths(args.input)

    if not image_paths:
        logger.info(f"Error: no valid image(s) found at {args.input}")
        return

    preprocess = not args.no_preprocess

    all_results = {}
    for path in image_paths:
        logger.info(f"Processing {path}...")
        all_results[path] = process_image(path, args.min_confidence, preprocess)

    for path, results in all_results.items():
        logger.info(f"\n--- {path} ({len(results)} line(s)) ---")
        for r in results:
            logger.info(f"[{r['confidence']:.2f}] {r['text']}")

    if args.output:
        save_results(all_results, args.output)
        logger.info(f"\nSaved results to {args.output}")


if __name__ == "__main__":
    main()