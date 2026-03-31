import fitz

merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
doc = fitz.open(merck_path)
page = doc[0]

# List ALL drawings with a fill
drawings = page.get_drawings()
print(f"Total drawings: {len(drawings)}")

for i, d in enumerate(drawings):
    fill = d.get("fill")
    if fill:
        # Check if it's light blue: R, G, B all > 0.8 and B is the highest
        is_light_blue = all(c > 0.7 for c in fill) and fill[2] > fill[0]
        print(f"Drawing {i}: rect={d['rect']}, fill={fill}, is_light_blue={is_light_blue}")

# Also analyze the logo color (already extracted in previous turn)
logo_doc = fitz.open(r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\extracted_logo_0.png')
# Actually let's just use a professional dark blue (Ryze Navy)
# Ryze Navy: (0.1, 0.23, 0.4) roughly

doc.close()
