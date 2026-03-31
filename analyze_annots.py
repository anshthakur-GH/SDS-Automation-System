import fitz

merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
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
