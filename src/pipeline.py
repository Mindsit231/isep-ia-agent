"""
Document Ingestion Pipeline
Orchestrates the entire process: Load -> Parse -> Chunk -> Save
"""

import json
from pathlib import Path
from datetime import datetime

from loader import load_documents
from parser import parse_document
from chunker import create_chunks, get_chunking_stats

def run_pipeline(input_dir: str = '../data/raw', output_dir: str = '../data/processed'):
    """
    Main pipeline function
    Processes all documents and saves chunks as JSON
    """
    print("="*50)
    print("Starting Document Ingestion Pipeline")
    print("="*50)
    
    # Load documents
    print("\n[1/4] Loading documents...")
    documents = load_documents(input_dir)
    
    if not documents:
        print("No documents found. Exiting.")
        return
    
    # Process each document
    all_chunks = []
    
    print(f"\n[2/4] Parsing documents...")
    for doc in documents:
        print(f"  - Processing: {doc.name}")
        
        # Parse
        parsed = parse_document(doc)
        if not parsed:
            continue
        
        # Chunk
        chunks = create_chunks(parsed)
        all_chunks.extend(chunks)
        
        print(f"    Generated {len(chunks)} chunks")
    
    # Statistics
    print(f"\n[3/4] Chunking complete")
    stats = get_chunking_stats(all_chunks)
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Avg chunk size: {stats['avg_chunk_size']:.0f} characters")
    
    # Save output
    print(f"\n[4/4] Saving output...")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_path / f"chunks_{timestamp}.json"
    
    # Save as JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"  Saved to: {output_file}")
    print("\n" + "="*50)
    print("Pipeline Complete!")
    print("="*50)
    
    return output_file

if __name__ == "__main__":
    # Run the pipeline
    run_pipeline()
