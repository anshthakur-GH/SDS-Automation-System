import os
from docx2pdf import convert

try:
    docx_path = r'./'
    pdf_path = r'./'

    print(f"Converting {docx_path} to PDF...")
    convert(docx_path, pdf_path)
    print("Successly converted to PDF")
except Exception as e:
    print(f"Failed to convert: {e}")
