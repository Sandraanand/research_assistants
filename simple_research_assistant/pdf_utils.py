"""
PDF Utilities for extracting text from uploaded PDFs
"""
import pdfplumber
from PyPDF2 import PdfReader
from io import BytesIO


def extract_text_from_pdf(pdf_file) -> str:
    """
    Extract text from PDF file
    
    Args:
        pdf_file: File-like object or bytes
        
    Returns:
        Extracted text as string
    """
    try:
        # Try pdfplumber first (better text extraction)
        text = extract_with_pdfplumber(pdf_file)
        if text.strip():
            return text
        
        # Fallback to PyPDF2
        text = extract_with_pypdf2(pdf_file)
        return text
    
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def extract_with_pdfplumber(pdf_file) -> str:
    """Extract text using pdfplumber"""
    try:
        if isinstance(pdf_file, bytes):
            pdf_file = BytesIO(pdf_file)
        
        text_parts = []
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return "\n\n".join(text_parts)
    
    except Exception as e:
        print(f"pdfplumber extraction failed: {e}")
        return ""


def extract_with_pypdf2(pdf_file) -> str:
    """Extract text using PyPDF2 as fallback"""
    try:
        if isinstance(pdf_file, bytes):
            pdf_file = BytesIO(pdf_file)
        elif hasattr(pdf_file, 'seek'):
            pdf_file.seek(0)  # Reset file pointer
        
        reader = PdfReader(pdf_file)
        text_parts = []
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        
        return "\n\n".join(text_parts)
    
    except Exception as e:
        print(f"PyPDF2 extraction failed: {e}")
        return ""


def extract_pdf_metadata(pdf_file) -> dict:
    """
    Extract metadata from PDF
    
    Args:
        pdf_file: File-like object or bytes
        
    Returns:
        Dictionary with metadata
    """
    try:
        if isinstance(pdf_file, bytes):
            pdf_file = BytesIO(pdf_file)
        elif hasattr(pdf_file, 'seek'):
            pdf_file.seek(0)
        
        reader = PdfReader(pdf_file)
        metadata = reader.metadata
        
        return {
            "title": metadata.get("/Title", ""),
            "author": metadata.get("/Author", ""),
            "pages": len(reader.pages),
            "creator": metadata.get("/Creator", ""),
            "producer": metadata.get("/Producer", ""),
        }
    
    except Exception as e:
        print(f"Metadata extraction failed: {e}")
        return {"pages": 0}
