import json
import os

input_file = r'c:\Users\Imart\Desktop\Category_wiki\data\inputs\input_68865\buyer_call.json'
output_dir = os.path.dirname(input_file)

with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

calls = data.get('calls', [])

for i, call in enumerate(calls, 1):
    output_filename = f'buyer_call {i}.json'
    output_path = os.path.join(output_dir, output_filename)
    with open(output_path, 'w', encoding='utf-8') as out_f:
        json.dump(call, out_f, indent=2)
    print(f"Created {output_path}")

print(f"Total Call files created: {len(calls)}")
