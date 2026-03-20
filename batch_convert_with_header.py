import os
from pdf2docx import Converter
from docx import Document
from docxcompose.composer import Composer

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
    base_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\test'
    downloads_path = os.path.join(base_path, 'msds_downloads')
    template_file = os.path.join(base_path, 'MSDS_Master_Template - Copy.docx')
    
    # Get first 2 PDFs
    files = [f for f in os.listdir(downloads_path) if f.endswith('.pdf')]
    files.sort()
    target_files = files[:2]
    
    for filename in target_files:
        pdf_path = os.path.join(downloads_path, filename)
        output_name = filename.replace('.pdf', '_with_header.docx')
        output_path = os.path.join(downloads_path, output_name)
        
        try:
            convert_with_template_header(pdf_path, template_file, output_path)
            print(f"Successfully processed {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    main()
