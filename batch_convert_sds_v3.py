import os
import fitz
import re
from extract_sds_data import extract_sds_data
from generate_COMPANY_page1 import generate_COMPANY_page1

# Paths to branding assets
ARIAL_BOLD = r'C:\Windows\Fonts\arialbd.ttf'

def apply_minimal_branding(doc_merck, template_path):
    """
    Surgical branding: Logo in footer, minimal redacts, no other changes.
    """
    doc_template = fitz.open(template_path)
    logo_path = os.path.join(os.path.dirname(template_path), 'extracted_logo_0.png')
    
    # Identify footer branding area from template
    rect = doc_template[0].rect
    
    # We'll insert the logo manually at bottom center
    logo_w, logo_h = 240, 80
    center_x = rect.width / 2
    logo_rect = fitz.Rect(
        center_x - logo_w / 2,
        rect.height - 90,
        center_x + logo_w / 2,
        rect.height - 90 + logo_h
    )

    footer_strings = [
        "The life science business of Merck", 
        "MilliporeSigma in the US and Canada",
        "Millipore-"
    ]

    for page_num in range(len(doc_merck)):
        page = doc_merck[page_num]
        
        # 1. Surgical Footer Cleanup (ONLY specific Merck copyright strings)
        for s in footer_strings:
            hits = page.search_for(s)
            for hit_rect in hits:
                if hit_rect.y0 > 750: # Only target bottom edge
                    page.add_redact_annot(hit_rect, fill=(1,1,1))
        
        # Blank only the very bottom right strip where Millipore graphics might be
        page.draw_rect(fitz.Rect(450, rect.height - 80, rect.width, rect.height), color=(1,1,1), fill=(1,1,1))
        page.apply_redactions()
        
        # 2. Insert COMPANY Logo in the middle of footer
        if os.path.exists(logo_path):
            page.insert_image(logo_rect, filename=logo_path)

    doc_template.close()

def process_sds_v3(pdf_path, template_path, output_path):
    print(f"Processing v3: {os.path.basename(pdf_path)}...")
    
    # 1. Extract Data
    data = extract_sds_data(pdf_path)
    
    # 2. Generate new COMPANY Page 1 Content
    temp_p1_path = "temp_p1_v3.pdf"
    # To keep it non-destructive, we'll use a headless version if needed, 
    # but for now we'll use the existing generator and just clip the top.
    generate_COMPANY_page1(data, template_path, temp_p1_path)
    
    # 3. Open Original and Patch Page 1
    doc_merck = fitz.open(pdf_path)
    p1 = doc_merck[0]
    
    # Locate Section 2 to avoid cutting it
    section2_y = -1
    for b in p1.get_text("blocks"):
        if "SECTION 2" in b[4].upper():
            section2_y = b[1]
            break
            
    # If no SECTION 2 found, assume default cutoff at y=460
    cutoff_y = section2_y - 5 if section2_y > 0 else 460
    
    # Blank out the original Section 1 area (top to SECTION 2)
    p1.draw_rect(fitz.Rect(0, 0, p1.rect.width, cutoff_y), color=(1,1,1), fill=(1,1,1))
    
    # Patch with our COMPANY Section 1
    # We clip the top of our generated page (usually top to y=420 covers Section 1 and COMPANY header)
    doc_COMPANY_p1 = fitz.open(temp_p1_path)
    # The COMPANY Page 1 contains the header (60 shift) + Section 1 table.
    # Its Section 1 ends around y=400.
    COMPANY_clip = fitz.Rect(0, 0, p1.rect.width, 420)
    p1.show_pdf_page(COMPANY_clip, doc_COMPANY_p1, 0, clip=COMPANY_clip)
    doc_COMPANY_p1.close()
    
    # 4. Apply Minimal Branding to ALL pages (Logo in footer)
    apply_minimal_branding(doc_merck, template_path)
    
    # 5. Save
    doc_merck.save(output_path)
    doc_merck.close()
    
    if os.path.exists(temp_p1_path):
        os.remove(temp_p1_path)

if __name__ == "__main__":
    base_path = r'./'
    downloads_path = os.path.join(base_path, 'Merck SDS')
    template_file = os.path.join(base_path, 'MSDS_Master_Template.pdf')
    output_path_dir = os.path.join(base_path, 'Output_SDS_PDF_V3_Restoration')
    
    if not os.path.exists(output_path_dir):
        os.makedirs(output_path_dir)
        
    for filename in os.listdir(downloads_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(downloads_path, filename)
            output_name = filename.replace('.pdf', '_Final_v3.pdf')
            output_path = os.path.join(output_path_dir, output_name)
            process_sds_v3(pdf_path, template_file, output_path)
            print(f"Finalized v3: {filename}")
