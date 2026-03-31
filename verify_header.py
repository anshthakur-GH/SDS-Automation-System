import os
from docx import Document

docx_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Output_SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5_with_ryze_header.docx'
out_txt = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\verify_output.txt'

doc = Document(docx_path)
with open(out_txt, 'w', encoding='utf-8') as f:
    f.write("Inspecting the first 5 elements in the generated DOCX body...\n")
    for i, element in enumerate(doc.element.body[:5]):
        tag = element.tag.split('}')[-1]
        text = ""
        if tag == 'p':
            from docx.text.paragraph import Paragraph
            p = Paragraph(element, doc)
            text = p.text.strip()
        elif tag == 'tbl':
            from docx.table import Table
            t = Table(element, doc)
            text = " ".join([cell.text.strip().replace('\n', ' ') for row in t.rows for cell in row.cells])
            
        f.write(f"{i}: [{tag}] {repr(text[:300])}\n")
        
    f.write("\nChecking for any Millipore footer artifacts in the entire document:\n")
    footer_found = False
    for element in doc.element.body:
        tag = element.tag.split('}')[-1]
        text = ""
        if tag == 'p':
            from docx.text.paragraph import Paragraph
            p = Paragraph(element, doc)
            text = p.text.strip()
        elif tag == 'tbl':
            from docx.table import Table
            t = Table(element, doc)
            text = " ".join([cell.text.strip().replace('\n', ' ') for row in t.rows for cell in row.cells])
            
        if "MilliporeSigma" in text:
            footer_found = True
            f.write(f"FOUND: {repr(text[:100])}\n")
            
    if not footer_found:
        f.write("No Millipore footers found in the body text!\n")
