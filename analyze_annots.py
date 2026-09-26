import fitz

merck_path = r'./'
doc = fitz.open(merck_path)
page = doc[0]

# List all annotations
annots = page.annots()
if not annots:
    print("No annotations found.")
else:
    for i, annot in enumerate(annots):
        print(f"Annot {i}: type={annot.type}, rect={annot.rect}, colors={annot.colors}")

doc.close()
