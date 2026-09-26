import os
import fitz
import re

def process_sds(pdf_path, template_path, output_path):
    print(f"Processing {os.path.basename(pdf_path)}...")
    doc_template = fitz.open(template_path)
    doc_merck = fitz.open(pdf_path)
    doc_out = fitz.open()

    template_page = doc_template[0]
    rect = template_page.rect

    # --- Prepare Template Page 1 (Header + Footer) ---
    ARIAL_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
    
    # Shift the template upward by 60pts so the header sits closer to the top
    header_shift = 60
    temp_doc1 = fitz.open()
    tp1 = temp_doc1.new_page(width=rect.width, height=rect.height)
    shifted_rect = fitz.Rect(0, -header_shift, rect.width, rect.height - header_shift)
    tp1.show_pdf_page(shifted_rect, doc_template, 0)
    # Erase the auto-date/page text (originally at y=8-95, now shifted up by 60)
    tp1.draw_rect(fitz.Rect(0, 0, rect.width, 35), color=(1, 1, 1), fill=(1, 1, 1))
    
    # Redact the original large MSDS title (at y~20-40 after shift) and overwrite with Arial 11
    tp1.draw_rect(fitz.Rect(30, 15, 560, 45), color=(1, 1, 1), fill=(1, 1, 1))
    tp1.insert_text(fitz.Point(35.7, 35), "MATERIAL SAFETY DATA SHEET (MSDS)", fontfile=ARIAL_BOLD, fontsize=11, color=(0,0,0))

    # Erase placeholder body text (header ends ~85 after shift, blank from 90 down)
    tp1.draw_rect(fitz.Rect(0, 90, rect.width, rect.height), color=(1, 1, 1), fill=(1, 1, 1))

    # --- Prepare Template Page 2+ (Footer only) ---
    temp_doc2 = fitz.open()
    tp2 = temp_doc2.new_page(width=rect.width, height=rect.height)
    tp2.show_pdf_page(rect, doc_template, 0)
    # Erase everything EXCEPT the bottom footer (y>height-80)
    tp2.draw_rect(fitz.Rect(0, 0, rect.width, rect.height - 80), color=(1, 1, 1), fill=(1, 1, 1))

    strings_to_erase = [
        "SAFETY DATA SHEET",
        "according to Regulation (EC)",
        "No. 1907/2006",
        "Version",
        "Revision Date",
        "Print Date",
        "GENERIC EU MSDS",
        "- NO COUNTRY SPECIFIC DATA - NO OEL DATA",
        "www.sigmaaldrich.com",
    ]

    footer_strings = [
        "Millipore-",
        "Page",
        "The life science business of Merck",
        "MilliporeSigma",
        "the US and Canada",
    ]
    
    COMPANY_NAVY = (15/255, 45/255, 87/255) # Dark Navy Blue

    for page_num in range(len(doc_merck)):
        merck_page = doc_merck[page_num]
        all_blocks = merck_page.get_text("dict")["blocks"]
        
        # === FOOTER CLEANUP (ALL PAGES) ===
        for s in footer_strings:
            hits = merck_page.search_for(s)
            for hit_rect in hits:
                if hit_rect.y0 > 650:
                    merck_page.add_redact_annot(hit_rect, fill=(1,1,1))
        
        # Blank the entire bottom strip
        merck_page.draw_rect(fitz.Rect(0, 670, rect.width, rect.height), color=(1,1,1), fill=(1,1,1))
        
        # === RECOLOR SECTION HEADERS (ALL PAGES) ===
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if re.match(r"^SECTION \d+:", text.upper()) and span["bbox"][0] < 60:
                            bar_rect = fitz.Rect(45, span["bbox"][1]-2, 576, span["bbox"][3]+2)
                            merck_page.draw_rect(bar_rect, color=COMPANY_NAVY, fill=COMPANY_NAVY)
                            merck_page.add_redact_annot(span["bbox"], fill=COMPANY_NAVY)
                            
        merck_page.apply_redactions()
        
        # === PAGE-SPECIFIC LOGIC ===
        new_page = doc_out.new_page(width=rect.width, height=rect.height)
        
        if page_num == 0:
            # Draw Template Page 1
            new_page.show_pdf_page(rect, temp_doc1, 0) # Use prepared doc
            
            # Hide the Millipore logo and header strip across full width
            merck_page.draw_rect(fitz.Rect(0, 0, rect.width, 78), color=(1,1,1), fill=(1,1,1))
            
            for s in strings_to_erase:
                hits = merck_page.search_for(s)
                for hit_rect in hits:
                     if hit_rect.y1 < 165: 
                         merck_page.add_redact_annot(hit_rect, fill=(1,1,1))
            
            blocks = merck_page.get_text("blocks")
            for b in blocks:
                x0, y0, x1, y1, text, block_no, block_type = b
                if y1 < 135 and block_type == 0:
                    merck_page.add_redact_annot(fitz.Rect(x0, y0, x1, y1), fill=(1,1,1))
            
            merck_page.apply_redactions()
            
            clip_rect = fitz.Rect(0, 78, rect.width, rect.height)
            shift_y = 12
            
            target_rect = fitz.Rect(0, clip_rect.y0 + shift_y, rect.width, clip_rect.y1 + shift_y)
            new_page.show_pdf_page(target_rect, doc_merck, page_num, clip=clip_rect)
        else:
            # Pages 2+ : Copy the page as-is, BUT first overlay the footer-only template
            new_page.show_pdf_page(rect, temp_doc2, 0) # Use prepared doc
            new_page.show_pdf_page(rect, doc_merck, page_num)
        
        # === RE-RENDER WHITE SECTION TEXT (ALL PAGES) ===
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if re.match(r"^SECTION \d+:", text.upper()) and span["bbox"][0] < 60:
                             actual_y_offset = (12 if page_num == 0 and span["bbox"][1] > 78 else 0)
                             p_orig = fitz.Point(span["origin"][0], span["origin"][1] + actual_y_offset)
                             new_page.insert_text(p_orig, text, fontfile=ARIAL_BOLD, fontsize=11, color=(1, 1, 1))
        
        # === ADD COMPANY LOGO TO FOOTER (ALL PAGES) ===
        logo_path = os.path.join(os.path.dirname(template_path), 'extracted_logo_0.png')
        if os.path.exists(logo_path):
            logo_width = 240
            logo_height = 80
            center_x = rect.width / 2
            logo_rect = fitz.Rect(
                center_x - logo_width / 2,
                rect.height - 90,
                center_x + logo_width / 2,
                rect.height - 90 + logo_height
            )
            new_page.insert_image(logo_rect, filename=logo_path)

    doc_out.save(output_path)
    doc_out.close()
    doc_template.close()
    doc_merck.close()
    temp_doc1.close()
    temp_doc2.close()

if __name__ == "__main__":
    base_path = r'./'
    merck_pdf = os.path.join(base_path, 'Merck SDS', '14-Dioxane__123-91-1.pdf')
    template_pdf = os.path.join(base_path, 'MSDS_Master_Template.pdf')
    output_pdf = os.path.join(base_path, 'Output_SDS_PDF', '14-Dioxane__123-91-1_Final.pdf')
    
    if not os.path.exists(os.path.dirname(output_pdf)):
        os.makedirs(os.path.dirname(output_pdf))
        
    process_sds(merck_pdf, template_pdf, output_pdf)
    print(f"Final PDF saved to: {output_pdf}")
