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

# Blank out the placeholder body text in the template (from y0=145 down to y1=bottom)
temp_page.draw_rect(fitz.Rect(0, 145, rect.width, rect.height), color=(1, 1, 1), fill=(1, 1, 1))

for page_num in range(len(doc_merck)):
    merck_page = doc_merck[page_num]
    
    if page_num == 0:
        # Erase the top Millipore logo and main text safely
        merck_page.draw_rect(fitz.Rect(0, 0, rect.width, 115), color=(1,1,1), fill=(1,1,1))
        
        # Selectively erase the deeply extending "GENERIC EU MSDS" and "Print Date" blocks
        blocks = merck_page.get_text("blocks")
        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            if y1 < 162 and ("GENERIC" in text or "Print Date" in text or "SAFETY" in text or "Version" in text):
                merck_page.draw_rect(fitz.Rect(x0, y0, x1, y1), color=(1,1,1), fill=(1,1,1))
                
        # Now clip from 115 downward (to ensure any vector commands for SECTION 1 are captured)
        clip_y0 = 115
        clip_rect = fitz.Rect(0, clip_y0, rect.width, merck_page.rect.height - 60)
        
        # Shift down by 35 points: 115 clip becomes 150 on the output
        # COMPANY header is at ~143.5, meaning we have a 6.5 margin
        shift_y = 35 
    else:
        # Page 2+: Small header ends around y=70
        clip_y0 = 70
        clip_rect = fitz.Rect(0, clip_y0, rect.width, merck_page.rect.height - 60)
        
        # Shift slightly up to position text beautifully
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
