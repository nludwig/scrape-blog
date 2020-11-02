from docx import Document

def format_paragraphs_to_docx(paras, doc=None):
    if doc is None:
        doc = Document()

    for para in paras:
        doc.add_paragraph(para)

    doc.add_page_break()

    return doc
