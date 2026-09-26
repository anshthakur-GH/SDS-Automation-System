import docx
import sys
import io

# utf-8 safe printing to a file
with io.open("table1_clean2.txt", "w", encoding="utf-8") as f:
    doc = docx.Document('MSDS_ACETIC ACID_COMPANY.docx')
    for table in doc.tables[:1]:
        for row in table.rows[30:50]:
            f.write(" | ".join([cell.text.strip().replace('\n', ' ') for cell in row.cells]) + "\n")
