import logging

from docx import Document

def format_paragraphs_to_docx(title, paras, doc=None):
    if doc is None:
        doc = Document()

    doc.add_heading(title)

    for para in paras:
        if isinstance(para, dict):
            logging.info('Got image of width %s', para.get('width'))
            doc.add_picture(para['img'], width=para.get('width'))
            para['img'].close()
        else:
            doc.add_paragraph(para)

    doc.add_page_break()

    return doc
