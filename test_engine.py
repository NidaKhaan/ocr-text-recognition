from ocr_engine import extract_text

results = extract_text('samples/test1.jpg')
for r in results:
    print(f"{r['confidence']:.2f} | {r['text']}")