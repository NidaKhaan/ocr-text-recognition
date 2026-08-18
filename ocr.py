import argparse
import os
from ocr_engine import extract_text

def main():
    parser = argparse.ArgumentParser(description="Extract text from an image using OCR.")
    parser.add_argument("--image", required=True, help="Path to the image file")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: file not found: {args.image}")
        return

    results = extract_text(args.image)

    if not results:
        print("No text detected in image.")
        return

    print(f"\nExtracted {len(results)} line(s):\n")
    for r in results:
        print(f"[{r['confidence']:.2f}] {r['text']}")

if __name__ == "__main__":
    main()