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
    # Original bbox from analyze_template: (35.7, 81.0, 480, 96.9)
    # After shift of 60: y0 ~ 21, y1 ~ 37
    tp1.draw_rect(fitz.Rect(30, 15, 560, 45), color=(1, 1, 1), fill=(1, 1, 1))
    tp1.insert_text(fitz.Point(35.7, 35), "MATERIAL SAFETY DATA SHEET (MSDS)", fontfile=ARIAL_BOLD, fontsize=11, color=(0,0,0))

    # Erase placeholder body text (header ends ~85 after shift, blank from 90 down)
    tp1.draw_rect(fitz.Rect(0, 90, rect.width, rect.height), color=(1, 1, 1), fill=(1, 1, 1))

    # --- Prepare Template Page 2+ (Footer only, no top COMPANY header) ---
    temp_doc2 = fitz.open()
    tp2 = temp_doc2.new_page(width=rect.width, height=rect.height)
    tp2.show_pdf_page(rect, doc_template, 0)
    # Erase the entire COMPANY header (y0=0 to 145) and the body (y0=145 down to bottom-80 roughly)
    # We basically erase everything EXCEPT the bottom footer (y>height-80)
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
        
        # Capture all text blocks BEFORE redaction/drawing for re-rendering white text later
        all_blocks = merck_page.get_text("dict")["blocks"]

        # Search for sub-point labels (optional cleanup, can just remove this loop)
        # ... no longer needed for internal edits ...
        
        # === FOOTER CLEANUP (ALL PAGES) ===
        # Redact known footer text strings at the bottom of the page
        for s in footer_strings:
            hits = merck_page.search_for(s)
            for hit_rect in hits:
                if hit_rect.y0 > 650:  # only target the bottom footer area
                    merck_page.add_redact_annot(hit_rect, fill=(1,1,1))
        
        # Blank the entire bottom strip to wipe the Millipore logo graphic on the right
        merck_page.draw_rect(fitz.Rect(0, 670, rect.width, rect.height), color=(1,1,1), fill=(1,1,1))
        
        # === RECOLOR SECTION HEADERS (ALL PAGES) ===
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        # Strictly match "SECTION X:" at the start of a span
                        # and ensure it's on the left side (x < 60) to avoid in-text cites
                        if re.match(r"^SECTION \d+:", text.upper()) and span["bbox"][0] < 60:
                            # Draw Navy Bar across the width
                            bar_rect = fitz.Rect(45, span["bbox"][1]-2, 576, span["bbox"][3]+2)
                            merck_page.draw_rect(bar_rect, color=COMPANY_NAVY, fill=COMPANY_NAVY)
                            # Redact original text
                            merck_page.add_redact_annot(span["bbox"], fill=COMPANY_NAVY)
                            
        merck_page.apply_redactions()
        
        # === PAGE-SPECIFIC LOGIC ===
        new_page = doc_out.new_page(width=rect.width, height=rect.height)
        
        if page_num == 0:
            # Draw Template Page 1
            new_page.show_pdf_page(rect, temp_doc1, 0)
            
            # Hide the Millipore logo and header strip across full width
            merck_page.draw_rect(fitz.Rect(0, 0, rect.width, 78), color=(1,1,1), fill=(1,1,1))
            
            # --- NO MORE 1.3 & 1.4 REDACTION ---
            
            # Redact specific text strings that may extend below y=135
            for s in strings_to_erase:
                hits = merck_page.search_for(s)
                for hit_rect in hits:
                     if hit_rect.y1 < 165: 
                         merck_page.add_redact_annot(hit_rect, fill=(1,1,1))
            
            # Catch-all: redact remaining text blocks ONLY in the logo zone (y1 < 135)
            blocks = merck_page.get_text("blocks")
            for b in blocks:
                x0, y0, x1, y1, text, block_no, block_type = b
                if y1 < 135 and block_type == 0:
                    merck_page.add_redact_annot(fitz.Rect(x0, y0, x1, y1), fill=(1,1,1))
            
            merck_page.apply_redactions()
            
            # Clip from y=78 to capture everything including SECTION 1 heading
            clip_rect = fitz.Rect(0, 78, rect.width, rect.height)
            shift_y = 12
            
            target_rect = fitz.Rect(
                0, 
                clip_rect.y0 + shift_y, 
                rect.width, 
                clip_rect.y1 + shift_y
            )
            new_page.show_pdf_page(target_rect, doc_merck, page_num, clip=clip_rect)
        else:
            # Pages 2+ : Copy the page as-is (footer/headers already modified above)
            new_page.show_pdf_page(rect, doc_merck, page_num)
        
        # === RE-RENDER WHITE SECTION TEXT (ALL PAGES) ===
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if re.match(r"^SECTION \d+:", text.upper()) and span["bbox"][0] < 60:
                             # On Page 1, any text below 78 was shifted by 12 points
                             # On Page 2+, offset is 0
                             actual_y_offset = (12 if page_num == 0 and span["bbox"][1] > 78 else 0)
                             p_orig = fitz.Point(span["origin"][0], span["origin"][1] + actual_y_offset)
                             # Re-render in Arial Bold 11
                             new_page.insert_text(p_orig, text, fontfile=ARIAL_BOLD, fontsize=11, color=(1, 1, 1))
        
        # === NO MORE 1.3 & 1.4 INSERTION ===

        # === ADD COMPANY LOGO TO FOOTER (ALL PAGES) ===
        logo_path = os.path.join(os.path.dirname(template_path), 'extracted_logo_0.png')
        logo_width = 240  # 120 * 2 = 240 points
        logo_height = 80  # 40 * 2 = 80 points
        center_x = rect.width / 2
        logo_rect = fitz.Rect(
            center_x - logo_width / 2,
            rect.height - 90,  # Adjusted to sit comfortably
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

def main():
    base_path = r'./'
    downloads_path = os.path.join(base_path, 'Merck SDS')
    template_file = os.path.join(base_path, 'MSDS_Master_Template.pdf')
    output_path_dir = os.path.join(base_path, 'Output_SDS_PDF')
    
    if not os.path.exists(output_path_dir):
        os.makedirs(output_path_dir)
        
    files = [f for f in os.listdir(downloads_path) if f.endswith('.pdf')]
    files.sort()
    
    # Process all PDFs
    for filename in files:
        pdf_path = os.path.join(downloads_path, filename)
        output_name = filename.replace('.pdf', '_with_COMPANY_header.pdf')
        output_path = os.path.join(output_path_dir, output_name)
        
        try:
            process_sds(pdf_path, template_file, output_path)
            print(f"Successfully finalized {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
