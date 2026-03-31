import fitz

merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
doc = fitz.open(merck_path)
page = doc[0]

# Find "SECTION" locations
section_rects = page.search_for("SECTION")
print(f"Found {len(section_rects)} 'SECTION' instances.")

# Check for drawings that overlap these areas
drawings = page.get_drawings()
print(f"Total drawings: {len(drawings)}")

for i, s_rect in enumerate(section_rects):
    print(f"SECTION {i} bbox: {s_rect}")
    for j, d in enumerate(drawings):
        d_rect = d['rect']
        # If the drawing rect overlaps the SECTION rect significantly
        if d_rect.intersects(s_rect):
            print(f"  Overlapping Drawing {j}: rect={d_rect}, type={d['type']}, fill={d.get('fill')}, color={d.get('color')}, width={d.get('width')}")

doc.close()
