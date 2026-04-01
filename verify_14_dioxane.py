import fitz
import os

pdf_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Output_SDS_PDF\14-Dioxane__123-91-1_Final.pdf'

if not os.path.exists(pdf_path):
    print(f"Error: File not found at {pdf_path}")
    exit(1)

doc = fitz.open(pdf_path)
print(f"Verifying {os.path.basename(pdf_path)} with {len(doc)} pages.")

for i in range(len(doc)):
    page = doc[i]
    print(f"\n--- Page {i+1} ---")
    
    # Check for Ryze logo (should be in the footer)
    images = page.get_image_info()
    found_logo = False
    for img in images:
        bbox = img['bbox']
        # Footer area: y > 700
        if bbox[1] > 700:
            print(f"Found image in footer at bbox: {bbox}")
            found_logo = True
    
    if not found_logo:
        print("Warning: No image found in footer area.")
    
    # Check for "SECTION 1:" or similar (should have Navy Bar)
    # We can't easily check 'color' of rectangles without get_drawings(), 
    # but we can check if the text is present.
    text = page.get_text("text")
    if "SECTION 1:" in text.upper():
        print("Found SECTION 1 text.")
    
    # Check if Millipore/Merck text is gone from footer
    footer_text = page.get_text("text", clip=fitz.Rect(0, 750, 600, 842))
    if "Millipore" in footer_text or "Merck" in footer_text:
        print(f"Warning: Found old branding in footer: {repr(footer_text.strip())}")
    else:
        print("Footer branding seems cleared.")

doc.close()
