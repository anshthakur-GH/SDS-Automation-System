import fitz

merck_path = r'./'
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
logo_doc = fitz.open(r'./')
# Actually let's just use a professional dark blue (COMPANY Navy)
# COMPANY Navy: (0.1, 0.23, 0.4) roughly

doc.close()
