import fitz

template_path = r'./'
merck_path = r'./'
out_path = r'./'

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
temp_page.draw_rect(fitz.Rect(0, 0, rect.width, 95), color=(1, 1, 1), fill=(1, 1, 1))

# Blank out the placeholder body text in the template (from y0=145 down to y1=bottom-80)
temp_page.draw_rect(fitz.Rect(0, 145, rect.width, rect.height - 80), color=(1, 1, 1), fill=(1, 1, 1))

for page_num in range(len(doc_merck)):
    merck_page = doc_merck[page_num]
    
    if page_num == 0:
        # Erase the top Millipore logo and main text safely
        merck_page.draw_rect(fitz.Rect(0, 0, rect.width, 135), color=(1,1,1), fill=(1,1,1))
        
        # Selectively erase the deeply extending "GENERIC EU MSDS" and "Print Date" blocks
        blocks = merck_page.get_text("blocks")
        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            if y1 < 162 and ("GENERIC" in text or "Print Date" in text or "SAFETY" in text):
                merck_page.draw_rect(fitz.Rect(x0, y0, x1, y1), color=(1,1,1), fill=(1,1,1))
                
        # Now clip from 140 downward (which safely includes the black lines and SECTION 1)
        clip_y0 = 140
        clip_rect = fitz.Rect(0, clip_y0, rect.width, rect.height - 60)
        target_y0 = 140  # No shift, natural position gives ~16pt gap from COMPANY header!
        shift_y = 0
    else:
        clip_y0 = 70
        clip_rect = fitz.Rect(0, clip_y0, rect.width, rect.height - 60)
        # Shift slightly up to align with COMPANY header on subsequent pages if needed
        # We'll just leave them roughly in place for now
        shift_y = 0
        target_y0 = clip_y0
        
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
