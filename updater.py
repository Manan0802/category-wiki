import re

with open('structure2_clean.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update GOLDEN RULE
text = re.sub(
    r'> GOLDEN RULE Every section listed here must appear in every Wikipedia.*?Sections are never skipped, merged, or reordered.',
    '> GOLDEN RULE Every MAJOR section (1 to 9) must appear in every Wikipedia, in the exact order shown. However, for SUBSECTIONS (e.g. 2.14 Dimensions & Logistics) or specific data points: if the agent finds absolutely no data from the provided sources AND a web search yields no relevant context, the agent must OMIT that subsection entirely rather than guessing, hallucinating, or inserting a "📭 No data found" placeholder. Never invent data.',
    text,
    flags=re.DOTALL
)

# 2. Update the Complete Section List
new_table = '''| **#** | **Section Name**                 | **Primary Purpose**                           | **Key Output**             |
|--------|----------------------------------|-----------------------------------------------|----------------------------|
| QF     | Quick Facts                      | Scannable infobox at top                      | Summary table              |
| 1      | Category Overview                | Market + regulatory context                   | Narrative paragraphs       |
| 2      | Seller-Side Specifications       | Full spec universe                            | 15 numbered subsections    |
| 3      | Buyer Specifications             | What buyers ask + miss                        | Priority matrix + gap list |
| 4      | Most Relevant Spec Combinations  | Reference configurations                      | Config tier table          |
| 5      | Spec Contradictions & Flags      | Conflicts, violations, red flags              | Warning blocks             |
| 6      | Price-Defining Specs & Variation | Price intelligence                            | Price stack + map          |
| 7      | Buyer Personas                   | Who buys + how they behave                    | Persona profiles           |
| 8      | Seller Personas                  | Who sells + supplier risk                     | Persona profiles           |
| 9      | Listing Spec Tiers               | Primary / Secondary / Tertiary classification | Tier tables                |
| G      | Glossary                         | Every term defined                            | Definition table           |
| M      | Wiki Metadata                    | System tracking                               | Metadata table             |'''

text = re.sub(r'\| \*\*\\#\*\* \| \*\*Section Name\*\*.*?\| M      \| Wiki Metadata.*?\| Metadata table             \|', new_table, text, flags=re.DOTALL)

# 3. Remove 'Open Doubt Log' and 'Quick Reference' from Wiki Metadata
text = re.sub(r'\*\*Open Doubt Log\*\*.*?(?=\*\*Quick Reference\*\*|$)', '', text, flags=re.DOTALL)
text = re.sub(r'\*\*Quick Reference\*\*.*?(?=\*End of Universal)', '', text, flags=re.DOTALL)
text = re.sub(r'\*\*Open Doubt Log\*\*.*', '', text, flags=re.DOTALL)

# 4. Extract Section 3 (Listing Spec Tiers)
match = re.search(r'(> 3 Listing Spec Tiers.*?)(?=> 4 Buyer Specifications)', text, flags=re.DOTALL)
if match:
    section_3 = match.group(1)
    text = text.replace(section_3, '')
    
    # Update Section numbers in the extracted text
    section_3 = section_3.replace('> 3 Listing Spec Tiers', '> 9 Listing Spec Tiers')
    
    # Update tier constraints
    section_3 = section_3.replace('3 specs maximum. The specs that appear', 'Minimum 2, Maximum 3 specs. The specs that appear')
    section_3 = section_3.replace('3 to 5 specs. Specs that are asked', 'Minimum 2, Maximum 3 specs. Specs that are asked')
    section_3 = section_3.replace('Never assign more than 3 specs as Primary.', 'Assign exactly 2 or 3 specs as Primary, and 2 or 3 specs as Secondary.')
    
    # Insert it before Glossary
    text = text.replace('> G Glossary', section_3 + '\n> G Glossary')

# 5. Shift other section numbers
text = text.replace('> 4 Buyer Specifications', '> 3 Buyer Specifications')
text = text.replace('> 5 Most Relevant Spec Combinations', '> 4 Most Relevant Spec Combinations')
text = text.replace('> 6 Spec Contradictions &amp; Flags', '> 5 Spec Contradictions & Flags')
text = text.replace('> 6 Spec Contradictions & Flags', '> 5 Spec Contradictions & Flags')
text = text.replace('> 7 Price-Defining Specs &amp; Price Variation', '> 6 Price-Defining Specs & Price Variation')
text = text.replace('> 7 Price-Defining Specs & Price Variation', '> 6 Price-Defining Specs & Price Variation')
text = text.replace('> 8 Buyer Personas', '> 7 Buyer Personas')
text = text.replace('> 9 Seller Personas', '> 8 Seller Personas')

# Also fix the STRUCTURAL RULE: 15 FIXED SUBSECTIONS text
text = text.replace('Subsections marked "always present" must never be empty — if no data exists, explicitly state what data is needed.', 'If no data exists for a subsection and web search yields nothing, omit it entirely.')

with open('structure2.md', 'w', encoding='utf-8') as f:
    f.write(text)
