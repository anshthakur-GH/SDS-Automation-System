import os
import fitz
import re
from extract_sds_data import extract_sds_data
from generate_COMPANY_page1 import generate_COMPANY_page1

ARIAL_BOLD = r'C:\Windows\Fonts\arialbd.ttf'
COMPANY_NAVY = (15/255, 45/255, 87/255)

def apply_minimal_branding(doc_merck, template_path):
    doc_template = fitz.open(template_path)
    logo_path = os.path.join(os.path.dirname(template_path), 'extracted_logo_0.png')
    rect = doc_template[0].rect
    # We no longer need to define logo_req out here since we define it inside the loop
    center_x = rect.width / 2
    for page_num in range(len(doc_merck)):
        page = doc_merck[page_num]
        
        # We do not blindly wipe the top header for page 2 onwards, 
        # as Merck documents do not have a standard repeating header and SDS text flows to the top margin.
            
        # Selective Footer Erasure for all pages:
        # Instead of painting a large 180px white box, we specifically target the text blocks
        # and images that make up the Merck footer to avoid cutting off genuine SDS data.
        footer_patterns = [
            "life science business of Merck",
            "MilliporeSigma",
            "Millipore-",
            "Page ",
            "Version",
            "Revision Date"
        ]
        
        # 1. Format all section headers globally with the Navy Blue background.
        # We use strictly defined Line geometries rather than Blocks to prevent multi-line merging issues.
        for block_dict in page.get_text("dict").get("blocks", []):
            if "lines" in block_dict:
                for line in block_dict["lines"]:
                    line_text = "".join([span["text"] for span in line["spans"]]).strip()
                    
                    if line_text.startswith("SECTION ") and not line_text.startswith("SECTION 1:") and ":" in line_text and len(line_text) < 150:
                        bbox = line["bbox"]  # Precise tight geometric box of JUST the text line: (x0, y0, x1, y1)
                        
                        # 1. Total Eradication: WIPE the original line exclusively with a white box.
                        page.draw_rect(fitz.Rect(30, bbox[1] - 5, 570, bbox[3] + 5), color=(1,1,1), fill=(1,1,1))
                        
                        # 2. Draw perfectly calibrated 20px Navy box securely anchored to the line's top coordinate (y0)
                        bg_rect = fitz.Rect(35, bbox[1] - 4, 560, bbox[1] + 16)
                        page.draw_rect(bg_rect, color=COMPANY_NAVY, fill=COMPANY_NAVY)
                        
                        # 3. Insert pristine white text effortlessly inside the calibrated box
                        text_rect = fitz.Rect(40, bbox[1] - 1, 550, bbox[1] + 16)
                        page.insert_textbox(text_rect, line_text, fontfile=ARIAL_BOLD, fontsize=10, color=(1,1,1))
        
        # 2. Selective Footer Erasure
        for b in page.get_text("blocks"):
            text = b[4].strip()
            
            if b[1] > 650:
                if any(p in b[4] for p in footer_patterns):
                    page.draw_rect(fitz.Rect(b[0], b[1], b[2], b[3]), color=(1,1,1), fill=(1,1,1))
                    
        # Cover the large 'M' graphic on the bottom right if present
        for img in page.get_images(full=True):
            for r in page.get_image_rects(img[0]):
                if r.y0 > 650 and r.x0 > 300:
                    page.draw_rect(r, color=(1,1,1), fill=(1,1,1))
        
        # We will use a reasonably sized logo for the footer
        logo_w, logo_h = 200, 66
        logo_rect = fitz.Rect(center_x - logo_w / 2, rect.height - 120, center_x + logo_w / 2, rect.height - 120 + logo_h)
        
        # Insert centered logo on all pages in the footer
        if os.path.exists(logo_path):
            page.insert_image(logo_rect, filename=logo_path)
            
    doc_template.close()

def process_sds_v3_1(pdf_path, template_path, output_path):
    print(f"Processing v3.1: {os.path.basename(pdf_path)}...")
    data = extract_sds_data(pdf_path)
    temp_p1_path = "temp_p1_v3_1.pdf"
    generate_COMPANY_page1(data, template_path, temp_p1_path)
    
    doc_merck = fitz.open(pdf_path)
    p1 = doc_merck[0]
    section2_y = -1
    for b in p1.get_text("blocks"):
        if "SECTION 2" in b[4].upper():
            section2_y = b[1]
            break
            
    cutoff_y = section2_y - 5 if section2_y > 0 else 500
    p1.draw_rect(fitz.Rect(0, 0, p1.rect.width, cutoff_y), color=(1,1,1), fill=(1,1,1))
    
    doc_COMPANY_p1 = fitz.open(temp_p1_path)
    # Give the clip enough height to copy over all of Section 1 text, which takes up around 490 units.
    COMPANY_clip = fitz.Rect(0, 0, p1.rect.width, cutoff_y)
    p1.show_pdf_page(COMPANY_clip, doc_COMPANY_p1, 0, clip=COMPANY_clip)
    doc_COMPANY_p1.close()
    
    apply_minimal_branding(doc_merck, template_path)
    doc_merck.save(output_path)
    doc_merck.close()
    if os.path.exists(temp_p1_path):
        os.remove(temp_p1_path)

if __name__ == "__main__":
    base_path = r'./'
    downloads_path = os.path.join(base_path, 'Merck SDS')
    template_file = os.path.join(base_path, 'MSDS_Master_Template.pdf')
    output_path_dir = os.path.join(base_path, 'Output_SDS_PDF_V3_1_Fix')
    
    if not os.path.exists(output_path_dir):
        os.makedirs(output_path_dir)
        
    for filename in os.listdir(downloads_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(downloads_path, filename)
            output_name = filename.replace('.pdf', '_Final_v3_1.pdf')
            output_path = os.path.join(output_path_dir, output_name)
            try:
                process_sds_v3_1(pdf_path, template_file, output_path)
                print(f"Finalized v3_1: {filename}")
            except Exception as e:
                print(f"Error v3_1 {filename}: {e}")
