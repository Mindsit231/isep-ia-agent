# Document Ingestion Pipeline

Member 1 Component - GenAI Document Repository Project

## Overview
This pipeline loads documents (PDF, DOCX, TXT), extracts text, chunks it, and outputs JSON for embedding.

## Structure
```
src/
├── loader.py    - Loads files from data/raw/
├── parser.py    - Extracts text from documents
├── chunker.py   - Splits text into chunks
└── pipeline.py  - Main orchestration script
```

## Setup

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Add documents**
Place your PDF/DOCX/TXT files in `data/raw/`

3. **Run pipeline**
```bash
cd src
python pipeline.py
```

## Output
Generates `data/processed/chunks_TIMESTAMP.json` with:
- chunk_id
- text
- char_count
- source_file
- page_number

## Configuration
Edit `pipeline.py` to change:
- Chunk size (default: 1000 characters)
- Chunk overlap (default: 200 characters)
- Input/output directories

## Requirements
- Python 3.8+
- See requirements.txt

## Next Steps
Output JSON is ready for Member 2 (Embedding + Vector DB)
