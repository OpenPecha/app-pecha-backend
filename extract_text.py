#!/usr/bin/env python3
"""
Extract a specific text_id from bo_segments_production.json
"""
import json

# Configuration
input_file = "bo_segments_production.json"
output_file = "choejuk.json"
target_text_id = "4495c84a-309b-403a-9865-934175d69e65"

print(f"Loading {input_file}...")
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total texts in file: {len(data)}")

# Extract the specific text
if target_text_id in data:
    extracted_data = {
        target_text_id: data[target_text_id]
    }
    
    # Save to new file
    print(f"Extracting text_id: {target_text_id}")
    print(f"Number of segments: {len(data[target_text_id])}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(extracted_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Successfully saved to {output_file}")
else:
    print(f"✗ Error: text_id '{target_text_id}' not found in the data")
    print(f"Available text_ids (first 10):")
    for i, tid in enumerate(list(data.keys())[:10]):
        print(f"  {i+1}. {tid}")
