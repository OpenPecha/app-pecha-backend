
import json
import re
import argparse
import sys
from typing import Dict, List, Tuple


def find_shad_patterns(text: str) -> List[Tuple[int, int, str]]:

    patterns = [
        r'།།',       
        r'། །',       
        r'ག །',       
        r'ཤ །',
        r'གི །',       
    ]
    
    matches = []
    
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            # Check if this is part of the excluded pattern །། །།
            # Look around the match to see if it's part of this pattern
            start = match.start()
            end = match.end()
            match_text = match.group()
            
            # Check for །། །། pattern
            # If current match is །།, check if followed by space and another །།
            if match_text == '།།':
                # Check if followed by ' །།'
                if text[end:end+3] == ' །།':
                    continue  # Skip this match, it's part of །། །།
                # Check if preceded by '།། '
                if start >= 3 and text[start-3:start] == '།། ':
                    continue  # Skip this match, it's part of །། །།
            
            matches.append((start, end, match_text))
    
    # Sort by position
    matches.sort(key=lambda x: x[0])
    
    return matches


def apply_br_to_segment(segment: str) -> str:

    # Find all matching patterns
    matches = find_shad_patterns(segment)
    
    if not matches:
        return segment
    
    # Remove the last match (don't apply <br/> to the end of segment)
    if len(matches) > 0:
        matches = matches[:-1]
    
    # If no matches left after removing the last one, return original
    if not matches:
        return segment
    
    # Apply <br/> tags by building the new string
    # Work backwards to avoid position shifts
    result = segment
    for start, end, pattern in reversed(matches):
        # Insert <br/> after the pattern
        result = result[:end] + '<br/>' + result[end:]
    
    return result


def process_texts(data: Dict, text_ids: List[str] = None, process_all: bool = False) -> Dict:

    result = {}
    
    # Determine which texts to process
    if process_all:
        texts_to_process = list(data.keys())
    elif text_ids:
        texts_to_process = [tid for tid in text_ids if tid in data]
        # Warn about missing text IDs
        missing = set(text_ids) - set(texts_to_process)
        if missing:
            print(f"Warning: Text IDs not found in input: {missing}")
    else:
        print("Error: Must specify either --text-id(s) or --all")
        return {}
    
    print(f"Processing {len(texts_to_process)} text(s)...")
    
    for text_id in texts_to_process:
        segments = data[text_id]
        processed_segments = {}
        
        total_segments = len(segments)
        br_count = 0
        
        for segment_id, segment_content in segments.items():
            processed_content = apply_br_to_segment(segment_content)
            processed_segments[segment_id] = processed_content
            
            # Count how many <br/> tags were added
            br_count += processed_content.count('<br/>')
        
        result[text_id] = processed_segments
        print(f"  Text {text_id}: {total_segments} segments, {br_count} <br/> tags added")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Apply <br/> tags to Tibetan text segments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single text
  python apply_br.py --input choejuk.json --output choejuk_br.json --text-id 4495c84a-309b-403a-9865-934175d69e65
  
  # Process multiple specific texts
  python apply_br.py --input bo_segments_production.json --text-ids <id1> <id2> <id3>
  
  # Process all texts
  python apply_br.py --input bo_segments_production.json --output bo_segments_production_br.json --all
        """
    )
    
    parser.add_argument('--input', '-i', required=True, help='Input JSON file')
    parser.add_argument('--output', '-o', help='Output JSON file (default: <input>_br.json)')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text-id', help='Single text ID to process')
    group.add_argument('--text-ids', nargs='+', help='Multiple text IDs to process')
    group.add_argument('--all', action='store_true', help='Process all texts')
    
    args = parser.parse_args()
    
    # Set default output filename if not specified
    if not args.output:
        input_base = args.input.rsplit('.json', 1)[0]
        args.output = f"{input_base}_br.json"
    
    # Load input file
    print(f"Loading {args.input}...")
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.input}': {e}")
        sys.exit(1)
    
    print(f"Loaded {len(data)} text(s) from input file")
    
    # Determine text IDs to process
    text_ids = None
    if args.text_id:
        text_ids = [args.text_id]
    elif args.text_ids:
        text_ids = args.text_ids
    
    # Process the texts
    result = process_texts(data, text_ids=text_ids, process_all=args.all)
    
    if not result:
        print("No texts processed. Exiting.")
        sys.exit(1)
    
    # Save output file
    print(f"\nSaving to {args.output}...")
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Successfully saved to {args.output}")


if __name__ == "__main__":
    main()
