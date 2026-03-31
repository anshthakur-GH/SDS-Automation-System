import fitz

template_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\MSDS_Master_Template.pdf'
merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
out_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\test_stamped.pdf'

# Open both PDFs
doc_template = fitz.open(template_path)
doc_merck = fitz.open(merck_path)

# Create a new output PDF
doc_out = fitz.open()

# We only test the first page
template_page = doc_template[0]
merck_page = doc_merck[0]

# Get dimensions of template
rect = template_page.rect
print(f"Template rect: {rect}")
merck_rect = merck_page.rect
print(f"Merck rect: {merck_rect}")

# We will copy the template page structure to output
new_page = doc_out.new_page(width=rect.width, height=rect.height)
new_page.show_pdf_page(rect, doc_template, 0) # Stamp the template background (header/footer)

# Now define the clipping area for the Merck SDS (e.g. skip top 130 and bottom 60)
# We need to find the exact coordinates. Let's try:
# top margin: 150 points
# bottom margin: 50 points
clip_rect = fitz.Rect(0, 150, merck_rect.width, merck_rect.height - 50)

# Stamp the clipped Merck SDS over the new page
new_page.show_pdf_page(clip_rect, doc_merck, 0, clip=clip_rect)

doc_out.save(out_path)
doc_out.close()
doc_template.close()
doc_merck.close()

print(f"Saved test overlay to {out_path}")
