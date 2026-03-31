import os
from docx2pdf import convert

try:
    docx_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\MSDS_Master_Template.docx'
    pdf_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\MSDS_Master_Template.pdf'

    print(f"Converting {docx_path} to PDF...")
    convert(docx_path, pdf_path)
    print("Successly converted to PDF")
except Exception as e:
    print(f"Failed to convert: {e}")
