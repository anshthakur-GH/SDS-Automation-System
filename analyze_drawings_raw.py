import fitz

merck_path = r'./'
doc = fitz.open(merck_path)
page = doc[0]

# Dump ALL drawings
drawings = page.get_drawings()
print(f"Total drawings on page 1: {len(drawings)}")

for i, d in enumerate(drawings):
    print(f"Drawing {i}:")
    for key, value in d.items():
        if key == 'items':
            print(f"  {key}: [{len(value)} sub-items]")
        else:
            print(f"  {key}: {value}")

doc.close()
# Also check other pages (maybe page 2 is different?)
doc = fitz.open(merck_path)
if len(doc) > 1:
    page2 = doc[1]
    drawings2 = page2.get_drawings()
    print(f"\nTotal drawings on page 2: {len(drawings2)}")
    for i, d in enumerate(drawings2[:5]): # only first 5
        print(f"  P2 Drawing {i}: {d['rect']}, fill={d.get('fill')}")
doc.close()
