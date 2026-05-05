
## Category: `{CATEGORY_NAME}`

---

### 1. Quick Facts

> A scannable snapshot of the category. Fill this with the category name, a one-line definition, 3–7 typical product examples, the industries that buy from this category, typical order scale and frequency, and any mandatory certifications or regulatory requirements a seller must comply with.

```
Category Name        :
One-Line Definition  :
Typical Products     :
Industry Verticals   :
Trade Scale          :     :
```

---

### 2. Category Overview

> Cover what the category includes and explicitly excludes, where it sits in a buyer's supply chain (raw material / component / consumable / capital equipment), how it is typically sourced and distributed, which adjacent categories it borders and what distinguishes them, and any demand seasonality or macro drivers.

---

### 3. Seller-Side Specifications

> The complete set of technical attributes a seller uses to describe a product in this category. For each spec, provide its canonical name, common aliases sellers use, data type (numeric / categorical / boolean / free-text), unit of measurement with all unit variants in use, allowed values or plausible numeric range, whether it is mandatory or optional, and any phrases or patterns where it commonly appears in unstructured seller text.

---

### 4. Buyer Specifications

> The attributes a buyer uses when writing an RFQ or purchase requirement. List the must-have specs a buyer always specifies, the nice-to-have specs they include when they have a preference, cases where buyers use different terminology than sellers for the same attribute, how buyers typically express quantity, and how they signal quality requirements (by brand, standard, certification, or descriptive grade).

---

### 5. Most Relevant Spec Combinations

> The 2–4 specs that together define a meaningfully distinct product variant — i.e., the "clustering key" of the category. List the primary variant axes, common named product profiles that are actively traded in the market, any spec dependency rules where one spec constrains another, and any combinations that are over-specified or physically redundant.

---

### 6. Spec Contradictions & Flags

> Known data quality issues and listing errors in this category. For each flag, note the impossible or suspicious combination, why it is wrong, and the severity: `auto-reject`, `manual-review`, or `soft-warning`. Also cover common unit errors, out-of-range numeric values, ambiguous terms with no standard definition, and patterns that suggest a listing was copy-pasted from another category.

---

### 7. Price-Defining Specs & Variation

> Which specs most strongly drive price differences within the category, in ranked order. Include indicative price ranges for common product profiles, known price multiplier factors when a spec changes (e.g., stainless vs mild steel = 2.5–3x), price points that are implausibly low and suggest fraud or miscategorization, and typical volume discount break-points.

---

### 8. Buyer Personas

> 3–5 archetypes of who buys in this category. For each persona, describe what drives their purchase, how they typically write RFQ requirements (spec-heavy, use-case based, brand-first, or open-ended), which specs they commonly omit that sellers need to clarify, and their typical buying timeline (spot / planned / capex cycle).

---

### 9. Seller Personas

> 3–5 archetypes of who sells in this category. For each persona, describe the typical completeness and accuracy of their listing data, how they structure their listings, what trust signals confirm their identity and claims, and how difficult it is to extract clean specs from their listings (High / Medium / Low) with a reason.

---

### 10. Listing Spec Tiers

It takes all the specs catalogued in Section 2 and classifies each one into one of three commercial tiers based on how important it is for listing creation, buyer search, and conversion decisions.

This classification is what the spec creation engine uses when it builds listing forms. Primary specs become mandatory fields that listings cannot go live without. Secondary specs are strongly recommended fields. Tertiary specs are optional advanced fields.
I’ve reviewed the markdown you uploaded. 

**PRIMARY**
2–3 must-have specs that appear in every listing and are first in search filters. Examples: `Voltage`, `Power`, `Capacity`.

**SECONDARY**
2–3 differentiating specs that matter for buyer decision-making. Examples: `Range`, `Warranty`, `Material`.

**TERTIARY**
All remaining specs for deep filtering, compliance checks, and detailed comparison. Not shown in the main listing view but searchable.

---

### 11. Glossary

> Definitions of domain-specific terms, abbreviations, standards, and jargon used in this category. Focus on terms that are category-specific, ambiguous across contexts, or frequently misused by sellers. For each term, include a plain-language definition, a note on how it is used specifically in this category, related terms, and the formal standard it maps to if one exists.

---

### 12. Wiki Metadata

> System fields for versioning, pipeline integration, and quality tracking. Not shown to buyers or sellers. Populate after all other sections are complete.

```
Category     :
Wiki Version        : 1.0.0
Generated By        : {model_name} / Prompt v{X}
Completeness Score  : (auto-computed)
Last Updated        : {YYYY-MM-DD}
Data Sources Used   :
```

---


