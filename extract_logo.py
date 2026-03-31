import fitz

template_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\MSDS_Master_Template.pdf'
doc = fitz.open(template_path)
page = doc[0]

images = page.get_images(full=True)
print(f"Found {len(images)} images on template page 1:")
for i, img in enumerate(images):
    xref = img[0]
    pix = fitz.Pixmap(doc, xref)
    print(f"  Image {i}: xref={xref}, size={pix.width}x{pix.height}")
    out_path = f'd:\\UNFAZED\\Projects\\RYZE CHEMIE\\Test 1\\extracted_logo_{i}.png'
    if pix.n < 5:  # GRAY or RGB
        pix.save(out_path)
    else:  # CMYK: convert first
        pix2 = fitz.Pixmap(fitz.csRGB, pix)
        pix2.save(out_path)
    print(f"  Saved to {out_path}")

doc.close()
