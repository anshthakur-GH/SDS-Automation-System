import fitz

template_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\MSDS_Master_Template.pdf'
merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
out_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\test_stamped_v2.pdf'

doc_template = fitz.open(template_path)
doc_merck = fitz.open(merck_path)
doc_out = fitz.open()

template_page = doc_template[0]
rect = template_page.rect

# We will create a clean "stamp" of the template first
# We do this by creating a temporary PDF, copying template page 1, and blanking out unwanted areas
temp_doc = fitz.open()
temp_page = temp_doc.new_page(width=rect.width, height=rect.height)
temp_page.show_pdf_page(rect, doc_template, 0)

# Blank out the top-right auto-date/page number from the template (y0=0 to y0=95)
top_right_hide = fitz.Rect(0, 0, rect.width, 95)
temp_page.draw_rect(top_right_hide, color=(1, 1, 1), fill=(1, 1, 1))

# Blank out the placeholder body text in the template (from y0=150 down to y1=bottom-80)
body_hide = fitz.Rect(0, 150, rect.width, rect.height - 80)
temp_page.draw_rect(body_hide, color=(1, 1, 1), fill=(1, 1, 1))

# Now, iterate over all pages in the Merck SDS
for page_num in range(len(doc_merck)):
    merck_page = doc_merck[page_num]
    
    # Create the final page
    new_page = doc_out.new_page(width=rect.width, height=rect.height)
    
    # Draw our cleaned-up Template onto the new page
    new_page.show_pdf_page(rect, temp_doc, 0)
    
    if page_num == 0:
        # Page 1: Skip the huge Millipore header (top 160 points) and bottom footer (bottom 60 points)
        clip_rect = fitz.Rect(0, 160, rect.width, rect.height - 60)
        # Shift it down by 30 points to give the Ryze header breathing room
        shift_y = 30
    else:
        # Page 2+: Skip the smaller header (top 70 points) and bottom footer (bottom 60 points)
        clip_rect = fitz.Rect(0, 70, rect.width, rect.height - 60)
        # Just a small shift or no shift
        shift_y = 80 # Shift down so it aligns with the Ryze header nicely
        
    # Calculate the bounding box where we paste the clip
    # We maintain the same width, but move the top-left corner
    target_rect = fitz.Rect(
        0, 
        clip_rect.y0 + shift_y, 
        rect.width, 
        clip_rect.y1 + shift_y
    )
    
    new_page.show_pdf_page(target_rect, doc_merck, page_num, clip=clip_rect)

doc_out.save(out_path)
doc_out.close()
doc_template.close()
doc_merck.close()
temp_doc.close()

print(f"Saved test overlay to {out_path}")
