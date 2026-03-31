import fitz

merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
out_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\test_extract.pdf'

doc_merck = fitz.open(merck_path)
doc_out = fitz.open()

# Test Extract 1: Just clip from 115 Downwards
merck_page = doc_merck[0]
rect = merck_page.rect

new_page = doc_out.new_page(width=rect.width, height=rect.height)
clip_rect = fitz.Rect(0, 115, rect.width, rect.height)
new_page.show_pdf_page(rect, doc_merck, 0, clip=clip_rect)

doc_out.save(out_path)
doc_out.close()
doc_merck.close()

print(f"Saved exact clip to {out_path}")
