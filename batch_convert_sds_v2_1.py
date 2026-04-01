import os
import fitz
import re
from extract_sds_data import extract_sds_data
from generate_ryze_page1 import generate_ryze_page1

# Global Settings
ARIAL_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
RYZE_NAVY = (15/255, 45/255, 87/255)

def apply_branding_to_body(doc_merck, template_path):
    """
    Apply branding (Navy bars, footer cleanup) to Pages 2+ of the document.
    """
    doc_template = fitz.open(template_path)
    rect = doc_template[0].rect
    
    # Iterate through all pages from Page 2 onwards (index 1+)
    # Actually, we apply it to everything, then we handle the Page 1 special logic.
    footer_strings = [
        "Millipore-", "Page", "The life science business of Merck", 
        "MilliporeSigma", "the US and Canada"
    ]

    for page_num in range(len(doc_merck)):
        page = doc_merck[page_num]
        all_blocks = page.get_text("dict")["blocks"]

        # 1. FOOTER CLEANUP
        for s in footer_strings:
            hits = page.search_for(s)
            for hit_rect in hits:
                if hit_rect.y0 > 650:
                    page.add_redact_annot(hit_rect, fill=(1,1,1))
        page.draw_rect(fitz.Rect(0, 670, rect.width, rect.height), color=(1,1,1), fill=(1,1,1))
        
        # 2. RECOLOR SECTION HEADERS
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if re.match(r"^SECTION \d+:", text.upper()) and span["bbox"][0] < 60:
                            bar_rect = fitz.Rect(45, span["bbox"][1]-2, 576, span["bbox"][3]+2)
                            page.draw_rect(bar_rect, color=RYZE_NAVY, fill=RYZE_NAVY)
                            page.add_redact_annot(span["bbox"], fill=RYZE_NAVY)
                            
        page.apply_redactions()
        
        # 3. RE-RENDER WHITE SECTION TEXT
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if re.match(r"^SECTION \d+:", text.upper()) and span["bbox"][0] < 60:
                             page.insert_text(span["origin"], text, fontfile=ARIAL_BOLD, fontsize=11, color=(1, 1, 1))
        
        # 4. OVERLAY RYZE LOGO FROM TEMPLATE (TRANS-PARENT)
        # Instead of showing the entire template page (which might have white), 
        # we only overlay the footer part from template, but we MUST be careful not to have white.
        # Actually, draw_rect(1,1,1) is what made it white.
        # Let's just overlay the bottom 80 pts of the template page.
        footer_clip = fitz.Rect(0, rect.height - 80, rect.width, rect.height)
        page.show_pdf_page(footer_clip, doc_template, 0, clip=footer_clip)

    doc_template.close()

def process_sds_v2_1(pdf_path, template_path, output_path):
    print(f"Processing v2.1: {os.path.basename(pdf_path)}...")
    
    # 1. Extract Data
    data = extract_sds_data(pdf_path)
    
    # 2. Generate Ryze Page 1 (Section 1 only)
    temp_p1_path = "temp_p1.pdf"
    generate_ryze_page1(data, template_path, temp_p1_path)
    
    # 3. Open Original and Prep Pages 2+
    merck_doc = fitz.open(pdf_path)
    # Identify Section 2 start on Page 1
    p1_blocks = merck_doc[0].get_text("blocks")
    section2_y = -1
    for b in p1_blocks:
        if "SECTION 2" in b[4].upper():
            section2_y = b[1]
            break
            
    # Apply branding to all pages (cleaning footers and recoloring)
    apply_branding_to_body(merck_doc, template_path)
    
    # 4. Assemble Final Doc
    doc_final = fitz.open()
    
    # Reconstruct Page 1
    # a. Take our new Ryze Head
    ryze_p1_doc = fitz.open(temp_p1_path)
    final_p1 = doc_final.new_page(width=merck_doc[0].rect.width, height=merck_doc[0].rect.height)
    final_p1.show_pdf_page(final_p1.rect, ryze_p1_doc, 0) # Base Ryze S1
    ryze_p1_doc.close()
    
    # b. Append original Section 2 if found on Page 1
    if section2_y > 0:
        # Clip from section2_y down to just before the original footer
        # Subtract some margin if needed. Original footer starts around 650.
        clip_rect = fitz.Rect(0, section2_y - 5, merck_doc[0].rect.width, 670)
        # Shift it down to where our Ryze Section 1 ends (estimated y ~ 420)
        target_y0 = 420
        target_rect = fitz.Rect(0, target_y0, merck_doc[0].rect.width, target_y0 + clip_rect.height)
        final_p1.show_pdf_page(target_rect, merck_doc, 0, clip=clip_rect)
    
    # Append Pages 2+
    if len(merck_doc) > 1:
        doc_final.insert_pdf(merck_doc, from_page=1, to_page=len(merck_doc)-1)
    
    doc_final.save(output_path)
    doc_final.close()
    merck_doc.close()
    
    if os.path.exists(temp_p1_path):
        os.remove(temp_p1_path)

if __name__ == "__main__":
    base_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1'
    downloads_path = os.path.join(base_path, 'Merck SDS')
    template_file = os.path.join(base_path, 'MSDS_Master_Template.pdf')
    output_path_dir = os.path.join(base_path, 'Output_SDS_PDF_V2_1')
    
    if not os.path.exists(output_path_dir):
        os.makedirs(output_path_dir)
        
    for filename in os.listdir(downloads_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(downloads_path, filename)
            output_name = filename.replace('.pdf', '_Final_v2_1.pdf')
            output_path = os.path.join(output_path_dir, output_name)
            process_sds_v2_1(pdf_path, template_file, output_path)
            print(f"Finalized v2.1: {filename}")
