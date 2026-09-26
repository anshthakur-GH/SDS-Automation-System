import os
from docx import Document

docx_path = r'./'
out_txt = r'./'

doc = Document(docx_path)
with open(out_txt, 'w', encoding='utf-8') as f:
    f.write("Inspecting the first 30 elements in the DOCX body...\n")
    for i, element in enumerate(doc.element.body[:30]):
        tag = element.tag.split('}')[-1]
        text = ""
        has_image = False
        if tag == 'p':
            from docx.text.paragraph import Paragraph
            p = Paragraph(element, doc)
            text = p.text.strip()
            has_image = 'graphic' in element.xml or 'pic' in element.xml
        elif tag == 'tbl':
            from docx.table import Table
            t = Table(element, doc)
            text = " | ".join([cell.text.strip().replace('\n', ' ') for row in t.rows for cell in row.cells])
        else:
            text = f"<{tag}>"
            
        f.write(f"{i}: [{tag}] (Img: {has_image}) {repr(text[:300])}\n")
