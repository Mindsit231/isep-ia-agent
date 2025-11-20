"""
FastAPI Backend Server
Connects document ingestion pipeline with Streamlit UI
Now with ChromaDB vector search + OpenAI RAG!
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import enhanced pipeline modules
from pipeline_v2 import run_pipeline, answer_question_with_rag, get_collection

app = FastAPI(title="GenAI Document API")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
DATA_RAW = Path(__file__).parent.parent / "data" / "raw"
DATA_PROCESSED = Path(__file__).parent.parent / "data" / "processed"
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)


class QueryRequest(BaseModel):
    """Request model for document queries"""
    question: str
    collection: str = "default"


class QueryResponse(BaseModel):
    """Response model for queries"""
    answer: str
    chunks: List[Dict[str, Any]]


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "GenAI Document API",
        "version": "1.0.0"
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document to the system
    Saves to data/raw/ directory
    """
    try:
        # Save uploaded file
        file_path = DATA_RAW / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Trigger enhanced pipeline to process the new document
        # This will chunk, embed, and store in ChromaDB
        collection = run_pipeline(
            input_dir=str(DATA_RAW),
            output_dir=str(DATA_PROCESSED),
            collection_name="ingested_docs"
        )
        
        return {
            "status": "success",
            "filename": file.filename,
            "message": "Document uploaded, processed, and embedded in vector DB",
            "collection": "ingested_docs"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.post("/query")
async def query_documents(request: QueryRequest) -> QueryResponse:
    """
    Query processed documents using ChromaDB vector search + OpenAI RAG
    Returns AI-generated answers based on relevant chunks
    """
    try:
        # Use enhanced RAG pipeline with vector search + OpenAI
        result = answer_question_with_rag(
            question=request.question,
            collection_name="ingested_docs",
            n_results=5
        )
        
        # Handle string response (error case)
        if isinstance(result, str):
            return QueryResponse(
                answer=result,
                chunks=[]
            )
        
        # Extract answer and sources
        answer = result.get("answer", "No answer generated.")
        sources = result.get("sources", [])
        
        # Convert sources to chunks format for UI compatibility
        chunks = [
            {
                "source_file": src.get("source_file"),
                "chunk_id": src.get("chunk_id")
            }
            for src in sources
        ]
        
        return QueryResponse(
            answer=answer,
            chunks=chunks
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.get("/documents")
async def list_documents():
    """
    List all documents in the system
    Returns raw files and processed chunks info
    """
    try:
        raw_files = [f.name for f in DATA_RAW.glob("*") if f.is_file()]
        processed_files = [f.name for f in DATA_PROCESSED.glob("chunks_*.json")]
        
        # Count total chunks
        total_chunks = 0
        for json_file in DATA_PROCESSED.glob("chunks_*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                total_chunks += len(json.load(f))
        
        return {
            "raw_documents": raw_files,
            "processed_files": processed_files,
            "total_chunks": total_chunks
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """
    Delete a document from the system
    """
    try:
        file_path = DATA_RAW / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_path.unlink()
        
        return {
            "status": "success",
            "message": f"Document {filename} deleted"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
