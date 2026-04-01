import fitz
import os

ARIAL = r'C:\Windows\Fonts\arial.ttf'
ARIAL_BOLD = r'C:\Windows\Fonts\arialbd.ttf'

def generate_ryze_page1(data, template_path, output_path):
    # Create a fresh, purely blank page to construct the Ryze Section 1 
    # This prevents any residual/duplicate text bleeding from the original template
    doc_out = fitz.open()
    page = doc_out.new_page(width=595.28, height=841.89) # Standard A4
    rect = page.rect
    
    # Insert the logo on the far right
    logo_path = os.path.join(os.path.dirname(template_path), 'extracted_logo_0.png')
    if os.path.exists(logo_path):
        logo_w, logo_h = 200, 66
        logo_rect = fitz.Rect(rect.width - 45 - logo_w, 25, rect.width - 45, 25 + logo_h)
        page.insert_image(logo_rect, filename=logo_path)
    
    # Insert the heading on the left side, split into two lines to match the reference image
    page.insert_text(fitz.Point(45, 55), "MATERIAL SAFETY DATA SHEET", fontfile=ARIAL_BOLD, fontsize=16, color=(0,0,0))
    page.insert_text(fitz.Point(45, 78), "(MSDS)", fontfile=ARIAL_BOLD, fontsize=16, color=(0,0,0))

    # Section 1 Heading - Shifted Up
    RYZE_NAVY = (15/255, 45/255, 87/255)
    page.draw_rect(fitz.Rect(35, 105, 560, 125), color=RYZE_NAVY, fill=RYZE_NAVY)
    page.insert_text(fitz.Point(40, 119), "SECTION 1: Identification of the substance/mixture and of the company/undertaking", fontfile=ARIAL_BOLD, fontsize=10, color=(1,1,1))
    
    # DRAW TABLE FRAME/BORDER - Reduced Height
    table_rect = fitz.Rect(35, 130, 560, 420)
    page.draw_rect(table_rect, color=(0.8, 0.8, 0.8), fill=None, width=0.5)

    curr_y = 145
    line_h = 14
    colon_x = 240 # Adjust the colon position
    
    # 1.1 Product identifier
    page.insert_text(fitz.Point(45, curr_y), "1.1. Product identifier", fontfile=ARIAL_BOLD, fontsize=10)
    curr_y += line_h
    
    def add_row(key, val, y):
        page.insert_text(fitz.Point(45, y), key, fontfile=ARIAL_BOLD, fontsize=10)
        if isinstance(val, list):
            page.insert_text(fitz.Point(colon_x, y), ":", fontfile=ARIAL, fontsize=10)
            for i, v in enumerate(val):
                page.insert_text(fitz.Point(colon_x + 10, y + (i*11)), str(v), fontfile=ARIAL, fontsize=10)
            return y + (max(1, len(val))*11) + 4
        else:
            page.insert_text(fitz.Point(colon_x, y), f":  {str(val)}" if str(val) else ":", fontfile=ARIAL, fontsize=10)
            return y + line_h

    curr_y = add_row("Product form", data.get("product_form", "Substance"), curr_y)
    curr_y = add_row("Product name", data.get("product_name", ""), curr_y)
    curr_y = add_row("Type of product", data.get("type_of_product", "Chemical"), curr_y)
    curr_y = add_row("Product Grades (Applicable)", data.get("product_grades", "AR/ACS, LR, HPLC,CERTIFIED DRY"), curr_y)
    curr_y = add_row("Product Code", data.get("product_codes", []), curr_y)
    curr_y = add_row("CAS No", data.get("cas_no", ""), curr_y)
    curr_y = add_row("Molecular Formula", data.get("formula", ""), curr_y)
    curr_y = add_row("Molecular Weight (g/mol)", data.get("molecular_weight", ""), curr_y)
    
    curr_y += 5
    
    # 1.2 Identified uses
    page.insert_text(fitz.Point(45, curr_y), "1.2. Relevant identified uses of the substance or mixture and uses advised against", fontfile=ARIAL_BOLD, fontsize=10)
    curr_y += line_h
    uses_val = data.get("identified_uses", "Industrial; For professional use only: Laboratory chemicals")
    page.insert_text(fitz.Point(45, curr_y), "1.2.1. Relevant identified uses", fontfile=ARIAL_BOLD, fontsize=10)
    page.insert_textbox(fitz.Rect(colon_x, curr_y - 10, 550, curr_y + 20), f":  {uses_val}", fontfile=ARIAL, fontsize=10)
    curr_y += 20
    
    page.insert_text(fitz.Point(45, curr_y), "1.2.2. Uses advised against", fontfile=ARIAL_BOLD, fontsize=10)
    page.insert_textbox(fitz.Rect(colon_x, curr_y - 10, 550, curr_y + 20), ":  No additional information available", fontfile=ARIAL, fontsize=10)
    curr_y += 16
    
    # 1.3 Supplier
    page.insert_text(fitz.Point(45, curr_y), "1.3. Details of the supplier of the safety data sheet", fontfile=ARIAL_BOLD, fontsize=10)
    curr_y += line_h
    
    # Text Address
    address_lines = [
        "RYZE CHEMIE",
        "Office No.13, Plot No.C-39 A",
        "Gami Industrial Park, TTC Industrial Area,",
        "Thane, Maharashtra-400705"
    ]
    for line in address_lines:
        page.insert_text(fitz.Point(45, curr_y), line, fontfile=ARIAL, fontsize=10, color=(0,0,0))
        curr_y += 12
        
    # Blue URL with underline
    url_text = "www.ryzechemie.com"
    url_color = (0.2, 0.4, 0.8)
    page.insert_text(fitz.Point(45, curr_y), url_text, fontfile=ARIAL, fontsize=10, color=url_color)
    page.draw_line(fitz.Point(45, curr_y + 2), fitz.Point(150, curr_y + 2), color=url_color, width=0.8)
    curr_y += 18
    
    # 1.4 Emergency
    page.insert_text(fitz.Point(45, curr_y), "1.4. Emergency Telephone Number", fontfile=ARIAL_BOLD, fontsize=10)
    page.insert_text(fitz.Point(colon_x, curr_y), ":  +91- 99-3006-02-02", fontfile=ARIAL_BOLD, fontsize=10)

    doc_out.save(output_path)
    doc_out.close()

if __name__ == "__main__":
    from extract_sds_data import extract_sds_data
    base_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1'
    test_pdf = os.path.join(base_path, 'Merck SDS', '14-Dioxane__123-91-1.pdf')
    template_pdf = os.path.join(base_path, 'MSDS_Master_Template.pdf')
    output_p1 = os.path.join(base_path, 'test_new_page1.pdf')
    
    data = extract_sds_data(test_pdf)
    generate_ryze_page1(data, template_pdf, output_p1)
