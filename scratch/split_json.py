import os
import re

input_file = r'c:\Users\Imart\Desktop\Category_wiki\data\inputs\input_68865\acc-block pdf.json'
output_dir = os.path.dirname(input_file)

with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find segments. 
# It looks for ///// pdf X ////// followed by a JSON block starting with { and ending with }
# We need to be careful as there might be multiple { } blocks if not handled correctly.
# However, the user says there are 10 pdfs.

# Alternative: split by the comment lines.
parts = re.split(r'//+\s*pdf\s*\d+\s*//+', content)
# The first part might be empty or metadata before the first pdf comment.
# Following parts are the JSON content (possibly with leading/trailing whitespace).

pdf_count = 0
for part in parts:
    stripped_part = part.strip()
    if stripped_part:
        pdf_count += 1
        output_filename = f'acc-block pdf {pdf_count}.json'
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write(stripped_part)
        print(f"Created {output_path}")

print(f"Total PDF files created: {pdf_count}")
