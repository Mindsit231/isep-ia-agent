"""
Document Parser
Extracts text from different document types (PDF, DOCX, TXT)
"""

from pathlib import Path
from pypdf import PdfReader
import docx

def parse_pdf(file_path: Path) -> dict:
    """
    Extract text from PDF files
    Returns dict with text per page
    """
    reader = PdfReader(str(file_path))
    
    # Extract text from each page
    pages = []
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text.strip():  # Only add non-empty pages
            pages.append({
                'page_number': page_num,
                'text': text
            })
    
    return {
        'source_file': file_path.name,
        'total_pages': len(reader.pages),
        'pages': pages
    }

def parse_docx(file_path: Path) -> dict:
    """
    Extract text from DOCX files
    """
    doc = docx.Document(str(file_path))
    
    # Combine all paragraphs
    text = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
    
    return {
        'source_file': file_path.name,
        'total_pages': 1,  # DOCX doesn't have pages
        'pages': [{
            'page_number': 1,
            'text': text
        }]
    }

def parse_txt(file_path: Path) -> dict:
    """
    Extract text from TXT files
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    return {
        'source_file': file_path.name,
        'total_pages': 1,
        'pages': [{
            'page_number': 1,
            'text': text
        }]
    }

def parse_document(file_path: Path) -> dict:
    """
    Main function to parse any supported document
    Routes to appropriate parser based on file type
    """
    extension = file_path.suffix.lower()
    
    try:
        if extension == '.pdf':
            return parse_pdf(file_path)
        elif extension == '.docx':
            return parse_docx(file_path)
        elif extension == '.txt':
            return parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
    except Exception as e:
        print(f"Error parsing {file_path.name}: {str(e)}")
        return None
