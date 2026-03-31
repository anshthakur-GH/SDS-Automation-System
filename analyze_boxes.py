import fitz

template_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\MSDS_Master_Template.pdf'
merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
out_txt = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\analyze_boxes.txt'

with open(out_txt, 'w', encoding='utf-8') as f:
    def analyze_pdf(path, name):
        doc = fitz.open(path)
        page = doc[0]
        f.write(f"\n--- Analysis of {name} Page 1 ---\n")
        blocks = page.get_text("blocks")
        # blocks is a list of (x0, y0, x1, y1, "text", block_no, block_type)
        blocks.sort(key=lambda b: b[1]) # sort by y0
        for b in blocks[:20]: # print first 20 blocks
            text = b[4].strip().replace('\n', ' ')
            f.write(f"y0={b[1]:.1f}, y1={b[3]:.1f}: {text[:80]}\n")
        f.write("... bottom blocks ...\n")
        for b in blocks[-5:]:
            text = b[4].strip().replace('\n', ' ')
            f.write(f"y0={b[1]:.1f}, y1={b[3]:.1f}: {text[:80]}\n")
            
    analyze_pdf(template_path, "Template")
    analyze_pdf(merck_path, "Merck SDS")
