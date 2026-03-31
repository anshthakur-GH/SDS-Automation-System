import fitz

merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
doc = fitz.open(merck_path)
page = doc[0]

# List all images
images = page.get_images(full=True)
print(f"Total images on page: {len(images)}")

for i, img in enumerate(images):
    xref = img[0]
    pix = fitz.Pixmap(doc, xref)
    print(f"Image {i}: xref {xref}, size {pix.width}x{pix.height}, colorspace {pix.colorspace.name}")
    # Inspect corners for color
    # (Checking a few points to see if it's light blue)
    if pix.width > 10 and pix.height > 10:
        c = pix.pixel(1, 1) # First pixel
        print(f"  Top-left pixel: {c}")

doc.close()
