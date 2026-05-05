import re

# Read structure2.md
with open('structure2.md', 'r', encoding='utf-8') as f:
    structure_content = f.read()

# Update wiki_builder.md
with open(r'skills\wiki_builder.md', 'r', encoding='utf-8') as f:
    builder_content = f.read()

# Find where to replace in wiki_builder
# Replace from "## Required Article Structure" down to "## Strict Rules — Non-Negotiable"
new_builder = re.sub(
    r'## Required Article Structure.*?## Strict Rules — Non-Negotiable',
    '## Required Article Structure\n\n' + structure_content + '\n\n## Strict Rules — Non-Negotiable',
    builder_content,
    flags=re.DOTALL
)

with open(r'skills\wiki_builder.md', 'w', encoding='utf-8') as f:
    f.write(new_builder)

# Update enricher.md
with open(r'skills\enricher.md', 'r', encoding='utf-8') as f:
    enricher_content = f.read()

# In enricher.md, replace the structural list block under "### 5. Structural Polish — STRICT SECTION ENFORCEMENT"
new_list = '''> ```
> # [Category Name]
> ## Quick Facts
> ## 1. Category Overview
> ## 2. Seller-Side Specifications
> ## 3. Buyer Specifications
> ## 4. Most Relevant Spec Combinations
> ## 5. Spec Contradictions & Flags
> ## 6. Price-Defining Specs & Variation
> ## 7. Buyer Personas
> ## 8. Seller Personas
> ## 9. Listing Spec Tiers
> ## Glossary
> ## Wiki Metadata
> ```'''

enricher_content = re.sub(
    r'> ```\n> # \[Category Name\].*?> ```',
    new_list,
    enricher_content,
    flags=re.DOTALL
)

# Also fix the Market Intelligence task to point to the correct sections or remove it since it's an old section name
enricher_content = re.sub(
    r'### 3. Market Intelligence Summary — Add or Enhance.*?### 4. Conflict Resolution',
    '### 3. Category Overview & Personas — Enhance\nEnhance sections 1, 7, and 8 with deep market intelligence.\n\n### 4. Conflict Resolution',
    enricher_content,
    flags=re.DOTALL
)

# Update the "NEVER remove a mandatory heading" line to match the new OMIT rule
enricher_content = re.sub(
    r'- \*\*NEVER remove a mandatory heading\.\*\* If there is no data, write `> 📭 No data found` under the heading — do NOT delete the heading\.',
    '- **NEVER remove a major heading (1-9).** However, for granular SUBSECTIONS (e.g. 2.14 Dimensions), if there is absolutely no data from sources or web search, OMIT the subsection entirely rather than writing "No data found".',
    enricher_content
)

with open(r'skills\enricher.md', 'w', encoding='utf-8') as f:
    f.write(enricher_content)
