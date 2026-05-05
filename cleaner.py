import re

def clean_html(text):
    def replace_table(match):
        content = match.group(1)
        
        # Sometimes there are two cells in a row (e.g., number and title)
        # Let's just strip all tags safely
        # First, preserve strong/em inside p
        content = re.sub(r'<p>\s*<strong>(.*?)</strong>\s*</p>', r'> **\1**\n>\n', content, flags=re.DOTALL)
        content = re.sub(r'<p>\s*<em>(.*?)</em>\s*</p>', r'> *\1*\n>\n', content, flags=re.DOTALL)
        content = re.sub(r'<p>(.*?)</p>', r'> \1\n>\n', content, flags=re.DOTALL)
        
        # Remove all other HTML tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Clean up excessive newlines/gt
        lines = content.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            if line and line != '>':
                if not line.startswith('>'):
                    line = '> ' + line
                clean_lines.append(line)
                
        return '\n'.join(clean_lines) + '\n\n'

    # Match tables that have <td>...</td>
    # To handle multiple TDs, we just strip the table tags and convert the whole table content
    def replace_full_table(match):
        content = match.group(0)
        # Extract all text inside <p> or <strong> or just raw text
        # Simplest: convert to markdown blockquote
        text_content = re.sub(r'<[^>]+>', ' ', content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        if not text_content:
            return ""
        return f"> {text_content}\n\n"

    # Actually, the tables usually contain instructions. Let's do a more careful regex
    result = re.sub(r'<table>.*?</table>', replace_full_table, text, flags=re.DOTALL)
    return result

with open('structure2.md', 'r', encoding='utf-8') as f:
    text = f.read()

text = clean_html(text)

with open('structure2_clean.md', 'w', encoding='utf-8') as f:
    f.write(text)
