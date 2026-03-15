import io
from enum import StrEnum

from docx import Document as DocxDocument
from pypdf import PdfReader


class ContentType(StrEnum):
    PDF = "application/pdf"
    TEXT = "text/plain"
    MARKDOWN = "text/markdown"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


SUPPORTED_CONTENT_TYPES = {ct.value for ct in ContentType}


def parse_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_text(data: bytes) -> str:
    return data.decode("utf-8")


def parse_docx(data: bytes) -> str:
    doc = DocxDocument(io.BytesIO(data))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs if paragraph.text)


_PARSERS = {
    ContentType.PDF: parse_pdf,
    ContentType.TEXT: parse_text,
    ContentType.MARKDOWN: parse_text,
    ContentType.DOCX: parse_docx,
}


def extract_text(data: bytes, content_type: str) -> str:
    parser = _PARSERS.get(ContentType(content_type))
    if parser is None:
        raise ValueError(f"Unsupported content type: {content_type}")
    return parser(data)
