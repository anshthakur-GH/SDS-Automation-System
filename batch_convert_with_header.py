import os
from pdf2docx import Converter
from docx import Document
from docxcompose.composer import Composer

def clean_converted_docx(docx_path):
    print(f"Cleaning up old headers/footers in {docx_path}...")
    doc = Document(docx_path)
    
    # 1. Find where the actual SDS content starts
    section_1_index = -1
    elements = doc.element.body[:]
    
    for i, element in enumerate(elements):
        tag = element.tag.split('}')[-1]
        text = ""
        if tag == 'p':
            from docx.text.paragraph import Paragraph
            p = Paragraph(element, doc)
            text = p.text.strip()
        elif tag == 'tbl':
            from docx.table import Table
            t = Table(element, doc)
            text = " ".join([cell.text.strip() for row in t.rows for cell in row.cells])
            
        if "SECTION 1" in text.upper():
            section_1_index = i
            break
            
    # 2. Delete everything before SECTION 1 (the old header/logo)
    if section_1_index > 0:
        for i in range(section_1_index):
            element = elements[i]
            if element.getparent() is not None:
                element.getparent().remove(element)
                
    # 3. Clean up the old footers across the rest of the document
    footer_keywords = [
        "The life science business of Merck operates as MilliporeSigma",
        "MilliporeSigma in the US and Canada"
    ]
    
    for element in elements[max(0, section_1_index):]:
        tag = element.tag.split('}')[-1]
        text = ""
        if tag == 'p':
            from docx.text.paragraph import Paragraph
            p = Paragraph(element, doc)
            text = p.text.strip()
        elif tag == 'tbl':
            from docx.table import Table
            t = Table(element, doc)
            text = " ".join([cell.text.strip() for row in t.rows for cell in row.cells])
            
        # Check for footer signatures
        is_footer = any(keyword in text for keyword in footer_keywords)
        if is_footer and element.getparent() is not None:
            element.getparent().remove(element)
            
    doc.save(docx_path)

def convert_with_template_header(pdf_path, template_path, output_path):
    temp_docx = "temp_converted.docx"
    
    # 1. Convert PDF to temp DOCX
    print(f"Converting {pdf_path} to temp DOCX...")
    settings = {
        'image_extraction': True,
        'image_threshold': 0.1,
        'curve_threshold': 1.0,
        'table_threshold': 0.1,
    }
    cv = Converter(pdf_path)
    cv.convert(temp_docx, start=0, end=None, **settings)
    cv.close()
    
    # 1.5 Clean up the converted file (remove old header/footer content)
    clean_converted_docx(temp_docx)
    
    # 2. Open template and converted docx
    print(f"Applying template header from {template_path}...")
    master = Document(template_path)
    
    # Clear master body but keep header/footer
    # Note: We keep the first section and just clear its content paragraphs/tables
    for p in master.paragraphs:
        p.text = "" # Clearing text might not be enough if there are tables
    
    # A better way is to delete all paragraphs and tables
    # But Clearing is safer for simple templates
    # Actually, let's use Composer to merge them
    
    # Creating a new document from template to preserve headers/footers
    base_doc = Document(template_path)
    # Remove all content from the body of base_doc
    # (Leaving it empty but with headers)
    for element in base_doc.element.body:
        base_doc.element.body.remove(element)
    
    # Re-add an empty paragraph if needed (python-docx sometimes complains if body is totally empty)
    # base_doc.add_paragraph()
    
    # Use Composer to append the converted document
    sub_doc = Document(temp_docx)
    composer = Composer(base_doc)
    composer.append(sub_doc)
    
    # Save final
    print(f"Saving final to {output_path}...")
    composer.save(output_path)
    
    # Cleanup
    if os.path.exists(temp_docx):
        os.remove(temp_docx)

def main():
    base_path = r'./'
    downloads_path = os.path.join(base_path, 'Merck SDS')
    template_file = os.path.join(base_path, 'MSDS_Master_Template.docx')
    output_path_dir = os.path.join(base_path, 'Output_SDS')
    
    if not os.path.exists(output_path_dir):
        os.makedirs(output_path_dir)
    
    # Get PDFs
    files = [f for f in os.listdir(downloads_path) if f.endswith('.pdf')]
    files.sort()
    target_files = files[:2]  # Test with first 2
    
    if not target_files:
        print("No PDFs found in", downloads_path)
        return
        
    for filename in target_files:
        pdf_path = os.path.join(downloads_path, filename)
        output_name = filename.replace('.pdf', '_with_COMPANY_header.docx')
        output_path = os.path.join(output_path_dir, output_name)
        
        try:
            convert_with_template_header(pdf_path, template_file, output_path)
            print(f"Successfully processed {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
