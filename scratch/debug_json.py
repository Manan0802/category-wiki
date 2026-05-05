import json
from pathlib import Path

p = Path(r'c:\Users\Imart\Desktop\Category_wiki\data\inputs\input_2047\call 1.json')
try:
    content = p.read_text(encoding='utf-8')
    print(f"Read with utf-8: First 5 chars: {repr(content[:5])}")
    json.loads(content)
    print("Parsed successfully with utf-8")
except Exception as e:
    print(f"Failed with utf-8: {e}")

try:
    content = p.read_text(encoding='utf-8-sig')
    print(f"Read with utf-8-sig: First 5 chars: {repr(content[:5])}")
    json.loads(content)
    print("Parsed successfully with utf-8-sig")
except Exception as e:
    print(f"Failed with utf-8-sig: {e}")
