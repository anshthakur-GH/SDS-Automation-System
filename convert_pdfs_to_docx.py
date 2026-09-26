import os
from pdf2docx import Converter

def convert_pdf_to_docx(pdf_folder, docx_folder):
    if not os.path.exists(docx_folder):
        os.makedirs(docx_folder)
        
    for filename in os.listdir(pdf_folder):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(pdf_folder, filename)
            docx_path = os.path.join(docx_folder, filename.replace('.pdf', '.docx'))
            
            print(f"Converting {filename} to DOCX...")
            try:
                cv = Converter(pdf_path)
                cv.convert(docx_path, start=0, end=None)
                cv.close()
                print(f"Successfully converted to {docx_path}")
            except Exception as e:
                print(f"Error converting {filename}: {e}")

if __name__ == "__main__":
    base_path = r'./'
    pdf_output_dir = os.path.join(base_path, 'Output_SDS_PDF')
    docx_output_dir = os.path.join(base_path, 'Output_SDS_DOCX')
    
    convert_pdf_to_docx(pdf_output_dir, docx_output_dir)
