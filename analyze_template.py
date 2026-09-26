import fitz

template_path = r'./'
doc = fitz.open(template_path)
page = doc[0]

text_dict = page.get_text("dict")
for block in text_dict["blocks"]:
    if "lines" in block:
        for line in block["lines"]:
            for span in line["spans"]:
                if "MATERIAL" in span["text"].upper():
                    print(f"Title: '{span['text']}' at {span['bbox']}, size {span['size']}, font {span['font']}")

doc.close()
