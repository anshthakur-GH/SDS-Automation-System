import fitz

merck_path = r'./'
doc = fitz.open(merck_path)
page = doc[0]

text_dict = page.get_text("dict")
for block in text_dict["blocks"]:
    if "lines" in block:
        for line in block["lines"]:
            for span in line["spans"]:
                print(f"{repr(span['text'])} at {span['bbox']}")

doc.close()
