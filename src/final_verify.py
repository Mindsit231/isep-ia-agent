"""Verify the latest JSON output"""
import json
from pathlib import Path

print("\n" + "="*70)
print("📊 STEP 7: VERIFYING FINAL OUTPUT")
print("="*70)

# Find the latest JSON file
output_dir = Path('../data/processed')
json_files = list(output_dir.glob('*.json'))

if not json_files:
    print("❌ No output files found!")
    exit(1)

# Get the most recent file
latest_file = max(json_files, key=lambda p: p.stat().st_mtime)

print(f"\n✓ Found output file: {latest_file.name}")
print(f"  File size: {latest_file.stat().st_size} bytes")

# Load the JSON
with open(latest_file, 'r', encoding='utf-8') as f:
    chunks = json.load(f)

print(f"\n✓ Successfully loaded JSON")
print(f"  Total chunks: {len(chunks)}")

# Show breakdown by source
print(f"\n📄 Chunks per document:")
sources = {}
for chunk in chunks:
    source = chunk['source_file']
    sources[source] = sources.get(source, 0) + 1

for i, (source, count) in enumerate(sources.items(), 1):
    print(f"  {i}. {source}: {count} chunk(s)")

# Show chunk details
print(f"\n📝 All chunks overview:")
print(f"  {'#':<5} {'Source':<25} {'Chars':<8} {'Preview':<30}")
print(f"  {'-'*5} {'-'*25} {'-'*8} {'-'*30}")
for chunk in chunks:
    preview = chunk['text'][:30].replace('\n', ' ')
    print(f"  {chunk['chunk_id']:<5} {chunk['source_file']:<25} {chunk['char_count']:<8} {preview}...")

print("\n" + "="*70)
print("✅ OUTPUT VERIFIED - Ready for Member 2!")
print("="*70 + "\n")
