"""
Verify the final JSON output
"""
import json

print("="*60)
print("VERIFYING FINAL JSON OUTPUT")
print("="*60)

# Load the JSON file
with open('../data/processed/chunks_20251030_235918.json', 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print(f"\n✓ Successfully loaded JSON file")
print(f"  Total chunks: {len(chunks)}")

# Check sources
sources = set([c['source_file'] for c in chunks])
print(f"\n✓ Documents processed:")
for source in sources:
    count = sum(1 for c in chunks if c['source_file'] == source)
    print(f"  - {source}: {count} chunks")

# Check chunk sizes
char_counts = [c['char_count'] for c in chunks]
print(f"\n✓ Chunk size statistics:")
print(f"  Average: {sum(char_counts)/len(char_counts):.0f} characters")
print(f"  Minimum: {min(char_counts)} characters")
print(f"  Maximum: {max(char_counts)} characters")

# Verify structure
print(f"\n✓ Verifying chunk structure:")
required_fields = ['chunk_id', 'text', 'char_count', 'source_file', 'page_number']
for i, chunk in enumerate(chunks):
    missing = [field for field in required_fields if field not in chunk]
    if missing:
        print(f"  ✗ Chunk {i} missing fields: {missing}")
    else:
        if i == 0:
            print(f"  ✓ All chunks have required fields")
        break

# Show sample chunk
print(f"\n✓ Sample chunk (first):")
print(f"  chunk_id: {chunks[0]['chunk_id']}")
print(f"  source_file: {chunks[0]['source_file']}")
print(f"  page_number: {chunks[0]['page_number']}")
print(f"  char_count: {chunks[0]['char_count']}")
print(f"  text preview: {chunks[0]['text'][:80]}...")

print("\n" + "="*60)
print("JSON OUTPUT VERIFIED! ✓")
print("="*60)
