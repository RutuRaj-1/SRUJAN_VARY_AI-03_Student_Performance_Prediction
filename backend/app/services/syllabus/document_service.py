import os
import uuid
import fitz  # PyMuPDF
from typing import Dict, Any, Tuple
from fastapi import UploadFile, HTTPException, status
from app.core.logging import logger

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../uploads/syllabus"))
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


class DocumentProcessingService:
    def __init__(self):
        os.makedirs(UPLOAD_DIR, exist_ok=True)

    def validate_file(self, file: UploadFile) -> str:
        ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file extension '{ext}'. Allowed formats: PDF, DOCX, TXT.",
            )
        return ext

    async def save_file(self, file: UploadFile, institution_id: uuid.UUID) -> Tuple[str, int]:
        ext = self.validate_file(file)
        inst_dir = os.path.join(UPLOAD_DIR, str(institution_id))
        os.makedirs(inst_dir, exist_ok=True)

        unique_filename = f"{uuid.uuid4()}{ext}"
        target_path = os.path.join(inst_dir, unique_filename)

        content = await file.read()
        file_size = len(content)

        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of 25MB (Received {file_size / (1024 * 1024):.2f}MB).",
            )

        with open(target_path, "wb") as f:
            f.write(content)

        # Reset pointer in case file object is reused
        await file.seek(0)
        return target_path, file_size

    def extract_text(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        ext = os.path.splitext(file_path)[1].lower()
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at path: {file_path}")

        if ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext == ".docx":
            return self._extract_docx(file_path)
        elif ext == ".txt":
            return self._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported format: {ext}")

    def _extract_pdf(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        doc = fitz.open(file_path)
        pages_text = []
        total_pages = len(doc)

        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text("text")
            if text:
                pages_text.append(text)

        doc.close()
        full_text = "\n\n".join(pages_text).strip()
        metadata = {
            "extractor": "PyMuPDF",
            "page_count": total_pages,
            "char_count": len(full_text),
            "word_count": len(full_text.split()),
        }
        return full_text, metadata

    def _extract_docx(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        try:
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = "\n\n".join(paragraphs).strip()
            metadata = {
                "extractor": "python-docx",
                "paragraph_count": len(paragraphs),
                "char_count": len(full_text),
                "word_count": len(full_text.split()),
            }
            return full_text, metadata
        except Exception as e:
            logger.error("Error reading docx: %s", e)
            raise

    def _extract_txt(self, file_path: str) -> Tuple[str, Dict[str, Any]]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            full_text = f.read().strip()
        metadata = {
            "extractor": "plain-text-decoder",
            "line_count": len(full_text.splitlines()),
            "char_count": len(full_text),
            "word_count": len(full_text.split()),
        }
        return full_text, metadata


document_service = DocumentProcessingService()
