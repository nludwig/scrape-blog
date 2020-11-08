from docx import Document

def format_paragraphs_to_docx(title, paras, doc=None):
    if doc is None:
        doc = Document()

    doc.add_heading(title)

    for para in paras:
        doc.add_paragraph(para)

    doc.add_page_break()

    return doc
