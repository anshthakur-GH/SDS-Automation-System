import fitz

merck_path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\Merck SDS\1-Octane_sulphonic_acid_sodium_salt_anhydrous__5324-84-5.pdf'
doc = fitz.open(merck_path)
page = doc[0]

text_dict = page.get_text("dict")
for block in text_dict["blocks"]:
    if "lines" in block:
        for line in block["lines"]:
            for span in line["spans"]:
                if "1.3" in span["text"] or "1.4" in span["text"] or "SUPPLIER" in span["text"].upper() or "EMERGENCY" in span["text"].upper():
                    print(f"[{span['text']}] at {span['bbox']}")

# Also look for any text near 1.3/1.4 that looks like address/phone
# Address might span multiple lines
doc.close()
