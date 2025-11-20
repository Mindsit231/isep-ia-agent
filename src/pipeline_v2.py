"""
Document Ingestion Pipeline + Vector Store Integration (Enhanced)
Combines Anurag's ingestion + Gael's ChromaDB + OpenAI RAG
"""

import json
from pathlib import Path
from datetime import datetime
import chromadb
import os
from dotenv import load_dotenv
from openai import OpenAI

from loader import load_documents
from parser import parse_document
from chunker import create_chunks, get_chunking_stats

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ChromaDB persistent storage path
CHROMA_DB_PATH = Path(__file__).parent.parent / "chroma_db"


def run_pipeline(input_dir: str = '../data/raw', output_dir: str = '../data/processed', collection_name: str = "ingested_docs"):
    """
    Processes documents -> chunks -> embeds -> stores in ChromaDB
    """
    print("="*60)
    print("🚀 Starting Document Ingestion + Embedding Pipeline")
    print("="*60)

    # STEP 1: Load files
    print("\n[1/5] Loading documents...")
    documents = load_documents(input_dir)
    if not documents:
        print("❌ No documents found.")
        return None

    # STEP 2: Parse & chunk
    print("\n[2/5] Parsing & chunking documents...")
    all_chunks = []
    for doc in documents:
        parsed = parse_document(doc)
        if not parsed:
            continue
        chunks = create_chunks(parsed)
        all_chunks.extend(chunks)
        print(f"  ✓ {doc.name}: {len(chunks)} chunks")

    stats = get_chunking_stats(all_chunks)
    print(f"\nChunking complete → {stats['total_chunks']} chunks total")

    # STEP 3: Save as JSON
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_path / f"chunks_{timestamp}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved chunks to {output_file}")

    # STEP 4: Create Chroma collection with persistence
    print("\n[4/5] Creating ChromaDB collection...")
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    
    # Delete existing collection if it exists (for fresh ingestion)
    try:
        chroma_client.delete_collection(collection_name)
        print(f"  ✓ Cleared existing collection: {collection_name}")
    except:
        pass
    
    collection = chroma_client.create_collection(collection_name)
    print(f"✓ Using collection: {collection_name}")

    # STEP 5: Embed & store chunks
    print("\n[5/5] Embedding and storing chunks...")
    texts = [chunk['text'] for chunk in all_chunks]
    ids = [f"{chunk['source_file']}_chunk_{chunk['chunk_id']}" for chunk in all_chunks]
    metadatas = [
        {
            'source_file': chunk['source_file'],
            'chunk_id': chunk['chunk_id'],
            'page_number': chunk['page_number']
        }
        for chunk in all_chunks
    ]

    # Store in Chroma with metadata
    collection.add(
        documents=texts,
        ids=ids,
        metadatas=metadatas
    )

    print(f"✅ Stored {len(texts)} chunks in Chroma collection: '{collection_name}'")
    print(f"✅ ChromaDB persisted at: {CHROMA_DB_PATH}")
    print("="*60)
    print("Pipeline complete! Ready for querying.")
    print("="*60)

    return collection


def get_collection(collection_name: str = "ingested_docs"):
    """
    Get existing ChromaDB collection
    """
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    try:
        return chroma_client.get_collection(collection_name)
    except:
        return None


def query_collection(collection, query: str, n_results: int = 3):
    """
    Query the Chroma collection for relevant chunks
    """
    results = collection.query(query_texts=[query], n_results=n_results)
    return results


def answer_question_with_rag(question: str, collection_name: str = "ingested_docs", n_results: int = 3):
    """
    Runs a RAG query: retrieve → send to OpenAI → get final answer
    """
    # Get collection
    collection = get_collection(collection_name)
    if not collection:
        return "No documents have been indexed yet. Please run the ingestion pipeline first."
    
    # Retrieve relevant chunks
    results = collection.query(query_texts=[question], n_results=n_results)
    
    if not results["documents"] or not results["documents"][0]:
        return "No relevant information found for your query."
    
    retrieved_chunks = results["documents"][0]
    metadatas = results["metadatas"][0] if results.get("metadatas") else []

    # Build context
    context = "\n\n---\n\n".join(retrieved_chunks)

    # Create prompt
    prompt = f"""You are an assistant that answers questions based on retrieved document context.

Context from documents:
{context}

Question: {question}

Instructions:
- Answer ONLY based on the context provided above
- Be concise and direct
- If the context doesn't contain enough information, say so
- Cite specific details from the context when relevant
"""

    # Get GPT answer
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        # Return answer with metadata
        return {
            "answer": answer,
            "sources": [
                {
                    "source_file": meta.get("source_file"),
                    "chunk_id": meta.get("chunk_id")
                }
                for meta in metadatas
            ]
        }
    except Exception as e:
        return f"Error generating answer: {str(e)}"


if __name__ == "__main__":
    # Run pipeline
    collection = run_pipeline()
    
    if collection:
        # Example query
        print("\n" + "="*60)
        print("Testing RAG Query...")
        print("="*60)
        
        result = answer_question_with_rag(
            "What is the refund policy?",
            n_results=3
        )
        
        if isinstance(result, dict):
            print("\n--- FINAL ANSWER ---")
            print(result["answer"])
            print("\n--- SOURCES ---")
            for source in result["sources"]:
                print(f"  - {source['source_file']} (chunk {source['chunk_id']})")
        else:
            print(result)
