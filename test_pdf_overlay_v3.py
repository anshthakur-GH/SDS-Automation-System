import fitz

template_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\MSDS_Master_Template.pdf'
merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
out_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\test_stamped_v3.pdf'

doc_template = fitz.open(template_path)
doc_merck = fitz.open(merck_path)
doc_out = fitz.open()

template_page = doc_template[0]
rect = template_page.rect

# Create a clean "stamp" of the template
temp_doc = fitz.open()
temp_page = temp_doc.new_page(width=rect.width, height=rect.height)
temp_page.show_pdf_page(rect, doc_template, 0)

# Blank out the top-right auto-date/page number from the template (y0=0 to y0=95)
top_right_hide = fitz.Rect(0, 0, rect.width, 95)
temp_page.draw_rect(top_right_hide, color=(1, 1, 1), fill=(1, 1, 1))

# Blank out the placeholder body text in the template (from y0=145 down to y1=bottom-80)
body_hide = fitz.Rect(0, 145, rect.width, rect.height - 80)
temp_page.draw_rect(body_hide, color=(1, 1, 1), fill=(1, 1, 1))

for page_num in range(len(doc_merck)):
    new_page = doc_out.new_page(width=rect.width, height=rect.height)
    new_page.show_pdf_page(rect, temp_doc, 0)
    
    if page_num == 0:
        # Page 1: 
        # The Merck header ends with "GENERIC EU MSDS" at y1=157.7
        # We start clipping exactly at y=158 to catch "SECTION 1" which is just below it.
        clip_y0 = 158
        clip_rect = fitz.Rect(0, clip_y0, rect.width, rect.height - 60)
        
        # The Ryze header ends around y=143.5
        # We target pasting at y=148, which leaves a very small 4.5pt gap
        target_y0 = 148
        shift_y = target_y0 - clip_y0
    else:
        # Page 2+: 
        # Smaller header ends around y=70
        clip_y0 = 70
        clip_rect = fitz.Rect(0, clip_y0, rect.width, rect.height - 60)
        
        # Paste below the Ryze header 
        target_y0 = 148
        shift_y = target_y0 - clip_y0
        
    target_rect = fitz.Rect(
        0, 
        clip_rect.y0 + shift_y, 
        rect.width, 
        clip_rect.y1 + shift_y
    )
    
    # Optional: draw a white rectangle on the new_page where we paste just to ensure opacity
    new_page.draw_rect(target_rect, color=(1, 1, 1), fill=(1, 1, 1))
    
    new_page.show_pdf_page(target_rect, doc_merck, page_num, clip=clip_rect)

doc_out.save(out_path)
doc_out.close()
doc_template.close()
doc_merck.close()
temp_doc.close()

print(f"Saved test overlay to {out_path}")
