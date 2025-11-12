"""
Document Loader
Loads files from the data/raw directory
"""

from pathlib import Path
from typing import List

def load_documents(directory: str) -> List[Path]:
    """
    Load all document files from a directory
    Supports: PDF, DOCX, TXT
    """
    # Convert to Path object
    doc_dir = Path(directory)
    
    # Check if directory exists
    if not doc_dir.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")
    
    # Supported file types
    supported_extensions = ['.pdf', '.docx', '.txt']
    
    # Get all files with supported extensions
    documents = []
    for ext in supported_extensions:
        documents.extend(doc_dir.glob(f'*{ext}'))
    
    print(f"Found {len(documents)} documents in {directory}")
    
    return documents

def get_file_info(file_path: Path) -> dict:
    """
    Get basic information about a file
    """
    return {
        'name': file_path.name,
        'path': str(file_path),
        'extension': file_path.suffix,
        'size_bytes': file_path.stat().st_size
    }
