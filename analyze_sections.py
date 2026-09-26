import fitz

pdf_path = r'./'
doc = fitz.open(pdf_path)
page = doc[0]

text_dict = page.get_text("dict")

for block in text_dict["blocks"]:
    if "lines" in block:
        for line in block["lines"]:
            for span in line["spans"]:
                if "SECTION" in span["text"].upper():
                    print(f"Span: '{span['text'][:30]}' - Font: {span['font']}, Size: {span['size']}")

doc.close()
