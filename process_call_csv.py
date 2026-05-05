import os
import csv
import ast
import json
import argparse
import re

def fix_python_literal(text):
    # Join lines to prevent single quotes from breaking across newlines
    lines = text.splitlines()
    fixed_lines = []
    current_line = ""
    
    for line in lines:
        stripped = line.strip()
        current_line += " " + stripped
        # Check if the current line has balanced quotes
        if current_line.count("'") % 2 == 0:
            fixed_lines.append(current_line.strip())
            current_line = ""
            
    # In case the last line didn't finish
    if current_line:
        fixed_lines.append(current_line.strip())
        
    return "\n".join(fixed_lines)

def process_csv(csv_path, mcat_id):
    output_dir = os.path.join("call", f"call_{mcat_id}")
    os.makedirs(output_dir, exist_ok=True)
    
    existing_urls = set()
    max_count = 0
    
    # Check existing files to avoid duplicates and find the highest file counter
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            if filename.endswith(".json") and filename.startswith("call "):
                filepath = os.path.join(output_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as jf:
                        jdata = json.load(jf)
                        if 'metadata' in jdata and 'source_url' in jdata['metadata']:
                            existing_urls.add(jdata['metadata']['source_url'])
                    
                    # Update max count
                    num_part = filename.replace("call ", "").replace(".json", "")
                    if num_part.isdigit():
                        max_count = max(max_count, int(num_part))
                except Exception as e:
                    print(f"Error reading existing file {filepath}: {e}")
                    
    print(f"Found {len(existing_urls)} existing calls. Will only add new ones.")
    count = max_count + 1
    new_files_saved = 0
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                row_mcat_id = str(row.get('category_mcat_id', '')).strip()
                
                # Check if this row belongs to the target mcat_id
                if row_mcat_id == str(mcat_id) or row_mcat_id.startswith(f"{mcat_id}."):
                    raw_text = row.get('llm_extracted_json', '')
                    file_url = row.get('file_url', '')
                    
                    if not raw_text:
                        continue
                        
                    # Skip if we already processed this URL
                    if file_url and file_url in existing_urls:
                        continue
                        
                    # Fix formatting
                    cleaned_text = fix_python_literal(raw_text)
                    
                    # Convert to dictionary
                    try:
                        data = ast.literal_eval(cleaned_text)
                    except SyntaxError:
                        # Fallback simple fixes if needed
                        fallback_text = re.sub(r"\[\s+", "[", cleaned_text)
                        fallback_text = re.sub(r"\s+\]", "]", fallback_text)
                        data = ast.literal_eval(fallback_text)
                        
                    # Inject the file URL for citations
                    if isinstance(data, dict):
                        if 'metadata' not in data:
                            data['metadata'] = {}
                        data['metadata']['source_url'] = file_url
                    
                    # Save to JSON file
                    out_filename = os.path.join(output_dir, f"call {count}.json")
                    with open(out_filename, 'w', encoding='utf-8') as out_f:
                        json.dump(data, out_f, indent=4)
                        
                    print(f"Saved NEW call: {out_filename}")
                    existing_urls.add(file_url) # Add to set to prevent duplicates in the same CSV
                    count += 1
                    new_files_saved += 1
                    
        print(f"\nProcess complete. Added {new_files_saved} new JSON files to {output_dir}")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process call CSV into JSON files incrementally.")
    parser.add_argument("--csv", required=True, help="Path to the CSV file")
    parser.add_argument("--mcat_id", required=True, help="Target MCAT ID to process")
    args = parser.parse_args()
    
    process_csv(args.csv, args.mcat_id)
