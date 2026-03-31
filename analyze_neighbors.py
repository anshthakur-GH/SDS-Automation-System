import fitz

merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
doc = fitz.open(merck_path)
page = doc[0]

# High precision search
text_blocks = page.get_text("dict")["blocks"]

target_y_1_3 = None
target_y_1_4 = None

for block in text_blocks:
    if "lines" in block:
        for line in block["lines"]:
            for span in line["spans"]:
                txt = span["text"]
                if "1.3" in txt:
                    print(f"Found 1.3 label at {span['bbox']}")
                    target_y_1_3 = span["bbox"][1]
                if "1.4" in txt:
                    print(f"Found 1.4 label at {span['bbox']}")
                    target_y_1_4 = span["bbox"][1]

# Now print anything slightly below these Y values
if target_y_1_3:
    print("\nBlocks near 1.3:")
    for block in text_blocks:
        if "lines" in block:
            b = block["bbox"]
            if b[1] > target_y_1_3 and b[1] < target_y_1_3 + 80:
                print(f"  {b}: {block['lines'][0]['spans'][0]['text'][:50]}...")
                
if target_y_1_4:
    print("\nBlocks near 1.4:")
    for block in text_blocks:
        if "lines" in block:
            b = block["bbox"]
            if b[1] > target_y_1_4 and b[1] < target_y_1_4 + 50:
                print(f"  {b}: {block['lines'][0]['spans'][0]['text'][:50]}...")

doc.close()
