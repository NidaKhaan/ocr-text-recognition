import easyocr

reader = easyocr.Reader(['en'])
results = reader.readtext('samples/test1.jpg')

# Sort by top-left y-coordinate (line), then x-coordinate (left-to-right within a line)
def sort_key(detection):
    bbox, text, confidence = detection
    top_left = bbox[0]  # (x, y)
    y = top_left[1]
    x = top_left[0]
    return (round(y / 20), x)  # bucket y into ~20px bands to group same-line text

results_sorted = sorted(results, key=sort_key)

for bbox, text, confidence in results_sorted:
    print(f"{confidence:.2f} | {text}")