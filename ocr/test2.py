

import base64

pdf_path=r"C:\pdfs\zxD20161121193448205\0a3ffdb6926711e9b82e00ac37466cf9.pdf"
with open(pdf_path, "rb") as f:
    pdf_data = base64.b64encode(f.read())
    print( base64.b64decode(pdf_data))



