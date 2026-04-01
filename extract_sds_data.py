import fitz
import re
import os

def extract_sds_data(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    text = page.get_text("text")
    blocks = page.get_text("blocks")
    
    data = {
        "product_name": "",
        "cas_no": "",
        "product_codes": [],
        "formula": "",
        "molecular_weight": "",
        "identified_uses": "",
        "product_form": "Substance",
        "type_of_product": "Chemical",
        "product_grades": "AR/ACS, LR, HPLC, CERTIFIED DRY",
    }
    
    # Identify Section 1 header
    section1_y = 1000
    for b in blocks:
        if "SECTION 1" in b[4].upper():
            section1_y = b[1]
            break
            
    # 1. Product Name (find the largest emboldened block or just before identifiers)
    # Merck usually puts it right at the top area (y between 100 and 150)
    for b in blocks:
        if 100 < b[1] < section1_y and b[4].strip():
            candidate = b[4].strip().split("\n")[0].strip()
            # Filter out boilerplate
            if not any(x in candidate for x in ["SAFETY DATA SHEET", "Millipore-", "Page", "Index-No", "CAS-No", "EC-No"]):
                if len(candidate) > 2:
                    data["product_name"] = candidate
                    break

    # 2. CAS No
    cas_match = re.search(r"(?:CAS-No|CAS No|CAS)\s*[:.]?\s*([\d-]+)", text, re.IGNORECASE)
    if not cas_match:
        cas_match = re.search(r"(\d{2,7}-\d{2}-\d)", text)
    if cas_match:
        data["cas_no"] = cas_match.group(1).strip()
        
    # 3. Product Codes (Merck uses 'Product Number' or just puts it next to 'Millipore-')
    codes = re.findall(r"Product Number\s*:\s*([\d\w/.]+)", text)
    if not codes:
        # Fallback: Millipore- X.XXXXX
        codes = re.findall(r"Millipore-\s*([\d\w/.]+)", text)
    if codes:
        data["product_codes"] = [c.strip() for c in codes]
        
    # 4. Formula & Molecular weight
    formula_match = re.search(r"Formula\s*:\s*(.*?)(?:\n|$)", text, re.IGNORECASE)
    if formula_match:
        data["formula"] = formula_match.group(1).strip()
        
    weight_match = re.search(r"Molecular weight\s*:\s*([\d\.]+)\s*g/mol", text, re.IGNORECASE)
    if weight_match:
        data["molecular_weight"] = weight_match.group(1).strip()
        
    # 5. Identified Uses (Section 1.2)
    uses_search = re.search(r"1\.2\.\s*Relevant identified uses.*?(?:1\.3\.|$)", text, re.DOTALL | re.IGNORECASE)
    if uses_search:
        uses_block = uses_search.group(0)
        lines = uses_block.split("\n")[1:] # skip header
        cleaned_uses = [line.strip() for line in lines if not any(x in line for x in ["1.3.", "1.2.1", "1.2.2", "Relevant identified"])]
        data["identified_uses"] = " ".join(cleaned_uses).strip()
        
    doc.close()
    return data

if __name__ == "__main__":
    base_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1'
    test_pdf = os.path.join(base_path, 'Merck SDS', '14-Dioxane__123-91-1.pdf')
    res = extract_sds_data(test_pdf)
    print("--- Extracted Data (14-Dioxane) ---")
    for k, v in res.items():
        print(f"  {k}: {v}")
