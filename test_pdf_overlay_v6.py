import fitz

template_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\MSDS_Master_Template.pdf'
merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
out_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\test_stamped_v6.pdf'

doc_template = fitz.open(template_path)
doc_merck = fitz.open(merck_path)
doc_out = fitz.open()

template_page = doc_template[0]
rect = template_page.rect

# Clean template
temp_doc = fitz.open()
temp_page = temp_doc.new_page(width=rect.width, height=rect.height)
temp_page.show_pdf_page(rect, doc_template, 0)
temp_page.draw_rect(fitz.Rect(0, 0, rect.width, 95), color=(1, 1, 1), fill=(1, 1, 1))
temp_page.draw_rect(fitz.Rect(0, 145, rect.width, rect.height), color=(1, 1, 1), fill=(1, 1, 1))

for page_num in range(len(doc_merck)):
    merck_page = doc_merck[page_num]
    
    if page_num == 0:
        # Hide the Millipore logo and top left area safely (y0 to 135)
        # But only from x=0 to x=300 (left side)
        merck_page.draw_rect(fitz.Rect(0, 0, 300, 135), color=(1,1,1), fill=(1,1,1))
        
        # Redact the text on the right side using precision redaction
        strings_to_erase = [
            "SAFETY DATA SHEET",
            "according to Regulation (EC)",
            "No. 1907/2006",
            "Version",
            "Revision Date",
            "Print Date",
            "GENERIC EU MSDS",
            "- NO COUNTRY SPECIFIC DATA - NO OEL DATA"
        ]
        
        for s in strings_to_erase:
            hits = merck_page.search_for(s)
            for hit_rect in hits:
                # Add a little padding to the hit_rect just to fully erase the ink
                # But don't pad if it's near SECTION 1
                if hit_rect.y1 < 165: 
                    merck_page.add_redact_annot(hit_rect, fill=(1,1,1))
                    
        # Apply the redactions - this permanently deletes the text and draws white over it
        merck_page.apply_redactions()
        
        # Since we surgically deleted the text, we can just grab everything from y=125 downward!
        # The black line and "SECTION 1" will be safely nestled in there.
        clip_y0 = 125
        clip_rect = fitz.Rect(0, clip_y0, rect.width, rect.height - 60)
        
        # Shift it down 25 points so the clip (125) lands perfectly at 150 (below Ryze header)
        shift_y = 25
    else:
        clip_y0 = 70
        clip_rect = fitz.Rect(0, clip_y0, rect.width, rect.height - 60)
        shift_y = 20
        
    new_page = doc_out.new_page(width=rect.width, height=rect.height)
    new_page.show_pdf_page(rect, temp_doc, 0)
    
    target_rect = fitz.Rect(
        0, 
        clip_rect.y0 + shift_y, 
        rect.width, 
        clip_rect.y1 + shift_y
    )
    
    new_page.show_pdf_page(target_rect, doc_merck, page_num, clip=clip_rect)

doc_out.save(out_path)
doc_out.close()
doc_template.close()
doc_merck.close()
temp_doc.close()

print(f"Saved test overlay to {out_path}")
