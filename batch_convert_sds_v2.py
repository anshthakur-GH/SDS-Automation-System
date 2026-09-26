import os
import fitz
import re
from extract_sds_data import extract_sds_data
from generate_COMPANY_page1 import generate_COMPANY_page1

# Global Settings
ARIAL = r'C:\Windows\Fonts\arial.ttf'
ARIAL_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
COMPANY_NAVY = (15/255, 45/255, 87/255)

def apply_branding_to_body(merck_doc, template_path):
    """
    Apply Navy headers and footer cleanup to all pages of the document.
    """
    doc_template = fitz.open(template_path)
    rect = doc_template[0].rect
    
    # 1. Prepare Footer Template (Page 2+)
    # We want a footer-only template for consistency
    temp_doc_footer = fitz.open()
    tp_footer = temp_doc_footer.new_page(width=rect.width, height=rect.height)
    tp_footer.show_pdf_page(rect, doc_template, 0)
    # Erase everything except footer
    tp_footer.draw_rect(fitz.Rect(0, 0, rect.width, rect.height - 80), color=(1, 1, 1), fill=(1, 1, 1))

    footer_strings = [
        "Millipore-", "Page", "The life science business of Merck", 
        "MilliporeSigma", "the US and Canada"
    ]

    for page_num in range(len(merck_doc)):
        page = merck_doc[page_num]
        all_blocks = page.get_text("dict")["blocks"]

        # === FOOTER CLEANUP ===
        for s in footer_strings:
            hits = page.search_for(s)
            for hit_rect in hits:
                if hit_rect.y0 > 650:
                    page.add_redact_annot(hit_rect, fill=(1,1,1))
        page.draw_rect(fitz.Rect(0, 670, rect.width, rect.height), color=(1,1,1), fill=(1,1,1))
        
        # === RECOLOR SECTION HEADERS ===
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if re.match(r"^SECTION \d+:", text.upper()) and span["bbox"][0] < 60:
                            bar_rect = fitz.Rect(45, span["bbox"][1]-2, 576, span["bbox"][3]+2)
                            page.draw_rect(bar_rect, color=COMPANY_NAVY, fill=COMPANY_NAVY)
                            page.add_redact_annot(span["bbox"], fill=COMPANY_NAVY)
                            
        page.apply_redactions()
        
        # Overlay the white text back
        for block in all_blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if re.match(r"^SECTION \d+:", text.upper()) and span["bbox"][0] < 60:
                             page.insert_text(span["origin"], text, fontfile=ARIAL_BOLD, fontsize=11, color=(1, 1, 1))
        
        # Overlay COMPANY Footer Template (for logo/decor)
        page.show_pdf_page(rect, temp_doc_footer, 0)

    temp_doc_footer.close()
    doc_template.close()

def process_sds_v2(pdf_path, template_path, output_path):
    print(f"Processing {os.path.basename(pdf_path)}...")
    
    # 1. Extract Data
    data = extract_sds_data(pdf_path)
    
    # 2. Generate New Page 1
    temp_p1_path = "temp_p1.pdf"
    generate_COMPANY_page1(data, template_path, temp_p1_path)
    
    # 3. Open Original and Apply Branding to Body (including Page 1 content if needed, but we replace it anyway)
    # Actually, we should apply branding to all pages and then just drop the first page and replace it.
    merck_doc = fitz.open(pdf_path)
    apply_branding_to_body(merck_doc, template_path)
    
    # 4. Assemble Final Document
    doc_final = fitz.open()
    
    # Add our new Page 1
    p1_doc = fitz.open(temp_p1_path)
    doc_final.insert_pdf(p1_doc)
    p1_doc.close()
    
    # Append the rest of the original (Pages 2 onwards)
    if len(merck_doc) > 1:
        doc_final.insert_pdf(merck_doc, from_page=1, to_page=len(merck_doc)-1)
    
    doc_final.save(output_path)
    doc_final.close()
    merck_doc.close()
    
    if os.path.exists(temp_p1_path):
        os.remove(temp_p1_path)

def main():
    base_path = r'./'
    downloads_path = os.path.join(base_path, 'Merck SDS')
    template_file = os.path.join(base_path, 'MSDS_Master_Template.pdf')
    output_path_dir = os.path.join(base_path, 'Output_SDS_PDF_V2')
    
    if not os.path.exists(output_path_dir):
        os.makedirs(output_path_dir)
        
    for filename in os.listdir(downloads_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(downloads_path, filename)
            output_name = filename.replace('.pdf', '_Final_v2.pdf')
            output_path = os.path.join(output_path_dir, output_name)
            
            try:
                process_sds_v2(pdf_path, template_file, output_path)
                print(f"Finalized v2: {filename}")
            except Exception as e:
                print(f"Error v2 {filename}: {e}")

if __name__ == "__main__":
    main()
