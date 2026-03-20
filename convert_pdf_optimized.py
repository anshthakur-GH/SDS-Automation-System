from pdf2docx import Converter
import os

def convert_pdf_optimized(pdf_path, docx_path):
    abs_pdf_path = os.path.abspath(pdf_path)
    abs_docx_path = os.path.abspath(docx_path)
    
    print(f"Converting {abs_pdf_path} (Optimized)...")
    
    # Settings to improve layout and image retention
    settings = {
        'image_extraction': True,
        'image_threshold': 0.1,  # More sensitive to images
        'curve_threshold': 1.0,  # More sensitive to curves
        'line_overlap_threshold': 0.9,
        'line_break_free_space_ratio': 0.1,
        'table_threshold': 0.1,  # More sensitive to tables
    }
    
    cv = Converter(abs_pdf_path)
    
    try:
        # Pass settings directly to the convert method
        cv.convert(abs_docx_path, start=0, end=None, **settings)
        cv.close()
        print("Conversion complete.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    pdf_file = r'd:\UNFAZED\Projects\RYZE CHEMIE\test\msds_downloads\msds_00004.pdf'
    docx_file = r'd:\UNFAZED\Projects\RYZE CHEMIE\test\msds_downloads\msds_00004_optimized.docx'
    
    convert_pdf_optimized(pdf_file, docx_file)
