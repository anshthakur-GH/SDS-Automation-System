import fitz

pdf_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Output_SDS_PDF\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5_with_ryze_header.pdf'
doc = fitz.open(pdf_path)
page = doc[0]

# Check for footer text (should be gone)
footer_text = page.get_text("blocks", clip=fitz.Rect(0, 650, 600, 842))
print("Footer text blocks (should be empty or unrelated):")
for b in footer_text:
    print(f"  {repr(b[4].strip())}")

# Check for images (should have the Ryze logo)
images = page.get_images()
print(f"Number of images on page: {len(images)}")
# There should be at least one image in the footer area if it's the logo
# Or we can check if there are images at all and where they are
for img_info in page.get_image_info():
    print(f"Image bbox: {img_info['bbox']}")

doc.close()
