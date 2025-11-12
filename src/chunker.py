"""
Text Chunker
Splits document text into smaller chunks for better processing
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

def create_chunks(parsed_doc: dict, chunk_size: int = 1000, chunk_overlap: int = 200) -> list:
    """
    Split document text into chunks
    
    Args:
        parsed_doc: Output from parser.py
        chunk_size: Target size for each chunk (characters)
        chunk_overlap: Number of characters to overlap between chunks
    
    Returns:
        List of chunk dictionaries with metadata
    """
    if not parsed_doc or not parsed_doc.get('pages'):
        return []
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Try to split at natural boundaries
    )
    
    chunks = []
    chunk_id = 0
    
    # Process each page
    for page in parsed_doc['pages']:
        page_text = page['text']
        page_number = page['page_number']
        
        # Split page text into chunks
        page_chunks = text_splitter.split_text(page_text)
        
        # Create chunk metadata
        for chunk_text in page_chunks:
            chunks.append({
                'chunk_id': chunk_id,
                'text': chunk_text,
                'char_count': len(chunk_text),
                'source_file': parsed_doc['source_file'],
                'page_number': page_number
            })
            chunk_id += 1
    
    return chunks

def get_chunking_stats(chunks: list) -> dict:
    """
    Get statistics about the chunking process
    """
    if not chunks:
        return {'total_chunks': 0}
    
    char_counts = [c['char_count'] for c in chunks]
    
    return {
        'total_chunks': len(chunks),
        'avg_chunk_size': sum(char_counts) / len(char_counts),
        'min_chunk_size': min(char_counts),
        'max_chunk_size': max(char_counts)
    }
