import docx

def read_docx(path):
    doc = docx.Document(path)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

if __name__ == "__main__":
    path = r'd:\UNFAZED\Projects\RYZE CHEMIE\Test 1\MSDS_ACETIC ACID_Ryze.docx'
    print(read_docx(path))
