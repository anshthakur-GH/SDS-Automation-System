import fitz

merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
doc = fitz.open(merck_path)
page = doc[0]

# Analyze DRAWINGS
drawings = page.get_drawings()
print(f"Found {len(drawings)} drawing items on page 1.")

for i, d in enumerate(drawings):
    # We're looking for filled rectangles (highlight boxes)
    if d['type'] == 'f' or (d['fill'] is not None):
        rect = d['rect']
        fill_color = d['fill']
        # If it's light blue, it will have a high B value and high R/G
        # E.g., (0.89, 0.92, 0.96)
        if fill_color:
            print(f"Item {i}: Rect={rect}, Fill={fill_color}")

# Also check for text segments with background?
# Sometimes they are just text segments with a bbox.
text_dict = page.get_text("dict")
for block in text_dict["blocks"]:
    if "lines" in block:
        for line in block["lines"]:
            for span in line["spans"]:
                if span["text"].strip() and "SECTION" in span["text"].upper():
                    print(f"Text Span: {span['text']}, Bbox: {span['bbox']}, Color: {span['color']}")

doc.close()
