from pdf2docx import Converter
import os

pdf_file = r'd:\UNFAZED\Projects\RYZE CHEMIE\test\msds_downloads\msds_00004.pdf'
docx_file = r'd:\UNFAZED\Projects\RYZE CHEMIE\test\msds_downloads\msds_00004.docx'

if os.path.exists(pdf_file):
    print(f"Converting {pdf_file} to {docx_file}...")
    cv = Converter(pdf_file)
    cv.convert(docx_file, start=0, end=None)
    cv.close()
    print("Conversion complete.")
else:
    print(f"Error: {pdf_file} does not exist.")
