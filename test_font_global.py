import fitz
import os
import re

# Font Paths
ARIAL = r'C:\Windows\Fonts\arial.ttf'
ARIAL_BOLD = r'C:\Windows\Fonts\arialbd.ttf'

def test_font_change(input_pdf, output_pdf):
    doc = fitz.open(input_pdf)
    page = doc[0] # Test on Page 1
    
    # Get all text spans
    text_dict = page.get_text("dict")
    
    # WIPE the page (draw a big white rectangle over the body)
    # Keeping the Ryze header area (top 85pts) if it exists, or just wipe all.
    # For a fair test, we wipe the whole page.
    page.draw_rect(page.rect, color=(1,1,1), fill=(1,1,1))
    
    for block in text_dict["blocks"]:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    if not text: continue
                    
                    # Decide if Heading (11) or Content (10)
                    # Simple heuristic for this test: "SECTION" or All-Caps or Bold
                    is_heading = "SECTION" in text.upper() or span["font"].lower().endswith("bold")
                    
                    font_size = 11 if is_heading else 10
                    font_path = ARIAL_BOLD if is_heading else ARIAL
                    
                    # Insert the text back at the original position (plus a small offset if size changed)
                    # Note: this will NOT wrap the text, so if size 10 is wider, it will overflow.
                    try:
                        page.insert_text(
                            span["origin"], 
                            text, 
                            fontfile=font_path, 
                            fontsize=font_size, 
                            color=(0,0,0)
                        )
                    except Exception as e:
                        print(f"Error inserting '{text[:20]}': {e}")
                        
    doc.save(output_pdf)
    doc.close()
    print(f"Test PDF saved to: {output_pdf}")

if __name__ == "__main__":
    base_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1'
    merck_sample = os.path.join(base_path, 'Merck SDS', '1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf')
    output_sample = os.path.join(base_path, 'test_font_global_output.pdf')
    
    test_font_change(merck_sample, output_sample)
