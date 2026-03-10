import PyPDF2
import pdfplumber
import io
import re
from typing import Optional, List
import pytesseract
from PIL import Image
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from PDF using multiple methods for maximum accuracy
    """
    all_text = ""
    
    # Method 1: Try PyMuPDF first (best for most PDFs)
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text:
                all_text += text + "\n"
        doc.close()
    except Exception as e:
        print(f"PyMuPDF failed: {e}")
    
    # Method 2: Try pdfplumber (good for complex layouts)
    if len(all_text.split()) < 100:  # If we didn't get enough text
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        all_text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}")
    
    # Method 3: Fallback to PyPDF2
    if len(all_text.split()) < 100:
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        all_text += page_text + "\n"
        except Exception as e:
            print(f"PyPDF2 failed: {e}")
    
    # Clean and normalize the text
    cleaned_text = clean_extracted_text(all_text)
    
    # Debug: Show word count
    word_count = len(cleaned_text.split())
    print(f"Extracted {word_count} words from PDF")
    
    return cleaned_text

def clean_extracted_text(text: str) -> str:
    """
    Clean and normalize extracted text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace and normalize line breaks
    lines = []
    for line in text.split('\n'):
        line = line.strip()
        if line and len(line) > 1:  # Filter very short lines
            lines.append(line)
    
    # Join with appropriate spacing
    cleaned_text = '\n'.join(lines)
    
    # Fix common OCR/parsing issues
    replacements = [
        (r'\s+', ' '),  # Multiple spaces to single space
        (r'\t', ' '),   # Tabs to spaces
        (r'•\s*', '• '),  # Ensure space after bullet
        (r'-\s*', '- '),  # Ensure space after hyphen
        (r'\.\s+\.', '.'),  # Remove double periods
        (r',\s+,', ','),   # Remove double commas
    ]
    
    for pattern, replacement in replacements:
        cleaned_text = re.sub(pattern, replacement, cleaned_text)
    
    # Preserve important section headers
    cleaned_text = re.sub(r'([A-Z][A-Z\s]+)(?=\n)', r'\1\n', cleaned_text)
    
    return cleaned_text.strip()

def extract_text_with_ocr(pdf_path: str) -> str:
    """
    Extract text using OCR (for image-based PDFs)
    """
    try:
        import pytesseract
        from pdf2image import convert_from_path
        
        images = convert_from_path(pdf_path)
        text = ""
        
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            text += f"--- Page {i+1} ---\n" + page_text + "\n"
        
        return clean_extracted_text(text)
    except Exception as e:
        print(f"OCR failed: {e}")
        return ""

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes
    """
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
        tmp_file.write(pdf_bytes)
        tmp_file.flush()
        
        try:
            text = extract_text_from_pdf(tmp_file.name)
            
            # If text extraction is poor, try OCR
            if len(text.split()) < 100:
                print("Text extraction poor, trying OCR...")
                ocr_text = extract_text_with_ocr(tmp_file.name)
                if len(ocr_text.split()) > len(text.split()):
                    text = ocr_text
        
        finally:
            os.unlink(tmp_file.name)
        
        return text