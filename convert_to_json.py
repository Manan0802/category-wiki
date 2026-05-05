import re
import json
import ast

def fix_python_literal(text):
    # This is a bit hacky but should work for this specific file
    # We want to find cases where a string is broken across lines
    # e.g., 'Electric Rickshaw (Half dala) [\n                4-battery\n            ]'
    
    # Regex to find single quoted strings spanning multiple lines
    # We'll replace the newlines inside them with spaces
    def replace_newlines(match):
        return match.group(0).replace('\n', ' ')
    
    # This regex looks for ' followed by anything including newlines until '
    # But it must be careful not to match across different strings.
    # However, in this file, the strings are mostly on one line or broken in specific places.
    
    # Let's try a different approach: join the lines if they don't look like they end a field
    lines = text.splitlines()
    fixed_lines = []
    current_line = ""
    
    for line in lines:
        stripped = line.strip()
        current_line += " " + stripped
        # Check if the current line has balanced quotes
        # (This is a simplified check, assuming no escaped quotes)
        if current_line.count("'") % 2 == 0:
            fixed_lines.append(current_line.strip())
            current_line = ""
            
    return "\n".join(fixed_lines)

try:
    with open('try.json', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the newlines in strings
    cleaned_content = fix_python_literal(content)
    
    # Now try to parse
    data = ast.literal_eval(cleaned_content)
    
    with open('try.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    
    print("Successfully converted try.json to valid JSON.")
except Exception as e:
    print(f"Error: {e}")
    # Fallback: let's try a simpler regex to just fix the specific known issues
    try:
        content = re.sub(r"'Electric Rickshaw \(Half dala\) \[\s+", "'Electric Rickshaw (Half dala) [ ", content)
        content = re.sub(r"\s+battery\s+\]'", " battery ]'", content)
        data = ast.literal_eval(content)
        with open('try.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print("Successfully converted try.json using fallback regex.")
    except Exception as e2:
        print(f"Fallback error: {e2}")
