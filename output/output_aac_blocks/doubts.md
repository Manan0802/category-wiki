# 🤔 Agent Doubt Log — AAC Blocks

> **🚀 Run:** 2026-04-22 12:13:06 UTC

> **MCAT ID:** 68865
> **Category:** Building Materials > Masonry Blocks
> **Total Doubts Raised This Run:** 8
> **Unresolved:** 6 🔴
> **Self-Resolved:** 2 ✅

---

## 🔴 Unresolved Doubts

### 🟡 DOUBT-501: Technical Specifications → Carpet Area Increase

- **Type:** `conflicting_data`
- **Severity:** medium
- **Raised at:** Step 5 (UPDATE)
- **Question:** The CONECC source document provides conflicting values for the increase in carpet area. A benefits table states a 2% increase in floor space, while a comparison table on the same page states a 3-5% contribution to carpet area. Which value is more accurate or what is the context for the difference?

**Evidence:**
```
Source A: "Page 5 comparison table states 3-5% contribution to carpet area"
Source B: "the benefits table on the same page states a 2% increase in floor space area"
```

**Action Taken by Agent:** I have included both values in the wiki and noted the conflict directly in the text, attributing it to the single source document.

**Suggested Resolution:** Clarify with the manufacturer (CONECC) which figure is correct or under what specific conditions each figure applies. The 3-5% range is more common in industry marketing, but the 2% might be a more conservative, verifiable figure.

---

### 🟡 DOUBT-701: Technical Specifications → Dimensional Tolerance

- **Type:** `conflicting_data`
- **Severity:** medium
- **Raised at:** Step 7 (UPDATE)
- **Question:** The MEPCRETE source document provides two different values for dimensional tolerance. Which one is correct?

**Evidence:**
```
Source A: (MEPCRETE catalog, Page 5) specifies variation in dimensions as +/- 1 mm.
Source B: (MEPCRETE catalog, Page 9) specifies variation in dimensions as +/- 1.5 mm.
```

**Action Taken by Agent:** I have noted the conflict within the dimensional tolerance specification in the main table, stating both values and attributing them as conflicting claims from the same source. The existing range in the table has been updated to reflect this new data.

**Suggested Resolution:** Review the full MEPCRETE product datasheet or contact the manufacturer to confirm the official tolerance. It's possible one value is for a premium product line.

---

### 🔴 DOUBT-702: Technical Specifications → Compressive Strength

- **Type:** `conflicting_data`
- **Severity:** high
- **Raised at:** Step 7 (UPDATE)
- **Question:** The MEPCRETE source document provides two drastically different and conflicting values for compressive strength, with one appearing to have a unit error. What is the correct value?

**Evidence:**
```
Source A: (MEPCRETE catalog, Page 5) specifies 40-50 kg/cm², which converts to a standard 3.92-4.9 N/mm².
Source B: (MEPCRETE catalog, Page 9) specifies 3.5-4 N/m², which is an extremely low value and likely a typo for N/mm².
```

**Action Taken by Agent:** I have flagged the conflict in the article. I have added the reasonable value (3.92-4.9 N/mm²) from the conversion of 40-50 kg/cm² to the main text and noted the conflict with the anomalous N/m² value, which I've identified as a probable typo for N/mm².

**Suggested Resolution:** Confirm with the manufacturer (MEPCRETE) if the "N/m²" value was a typo and should have been "N/mm²".

---

### 🟢 DOUBT-703: Technical Specifications → Fire Resistance

- **Type:** `conflicting_data`
- **Severity:** low
- **Raised at:** Step 7 (UPDATE)
- **Question:** The MEPCRETE source document provides two different values for fire resistance. Are these for different conditions or a direct conflict?

**Evidence:**
```
Source A: (MEPCRETE catalog, Page 5) specifies a general fire resistance of 4 hours.
Source B: (MEPCRETE catalog, Page 9) specifies "up to 6 hours for an 8 inch wall."
```

**Action Taken by Agent:** I treated this as conditional data rather than a direct conflict. I updated the main fire resistance specification to reflect the broader range and added a note specifying that the 6-hour rating is for a thicker (200mm/8-inch) wall, as this is a common dependency.

**Suggested Resolution:** No immediate action is needed, as the data appears conditional. The context provided (wall thickness) is sufficient for a buyer's understanding.

---

### 🔴 DOUBT-901: Technical Specifications → Thermal Conductivity (k)

- **Type:** `unusual_value`
- **Severity:** high
- **Raised at:** Step 9 (UPDATE)
- **Question:** The new source lists thermal conductivity as `0.16 kw-m/C`. The unit `kw-m/C` is highly unusual and, if interpreted literally (kilowatt-meter/Celsius), would equate to 160 W/m.K, which is orders of magnitude higher than any standard value for AAC blocks and would make it a conductor, not an insulator. Is this a typo for `0.16 W/m.K`?

**Evidence:**
```
Source A: acc-block pdf 8.json states `thermal_conductivity.value: 0.16`, `unit: kw-m/C`.
Source B: Existing wiki data from multiple sources (CONECC, JK SMARTBLOX, FLOAT AAC, FIXOLITE) all list values between 0.10 and 0.24, with the unit consistently being `W/m.K`. A value of 0.16 W/m.K fits perfectly within this established range.
```

**Action Taken by Agent:** Treated the value as a typo. I have recorded the thermal conductivity as `0.16 W/m.K` in the specifications table, consistent with other manufacturers' data. The original unusual unit is noted in the thought process but omitted from the main text to avoid confusion for the end-user.

**Suggested Resolution:** Confirm with the source provider or a domain expert if `kw-m/C` is a valid (though rare) unit or if it's a definite typo for `W/m.K`.

---

### 🔴 DOUBT-1001: Technical Specifications → Overall Density Range

- **Type:** `unusual_value`
- **Severity:** high
- **Raised at:** Step 10 (UPDATE)
- **Question:** The new source (ECOMATE catalog) lists a density range of 50-650 kg/m³. A density of 50 kg/m³ is physically improbable for a structural concrete block, being significantly lighter than water and below the lowest IS 2185 standard class (451 kg/m³). Is this a known ultra-lightweight variant or, as the source extraction notes suggest, a typo in the original document (e.g., for 550)?

**Evidence:**
```
Source A: acc-block pdf 9.json states `products.[0].common_specifications.density.value: 50-650` and notes "50 may be a typo in the source".
Source B: Existing wiki data shows the common commercial range is 551-700 kg/m³ and IS 2185 starts at 451 kg/m³.
```

**Action Taken by Agent:** I have added the ECOMATE range (50-650 kg/m³) to the notes of the density specification in the main table, explicitly mentioning the potential typo. I did not alter the primary range in the Quick Facts table as this value is a significant outlier.

**Suggested Resolution:** Clarify with the manufacturer (SRIKAR ENTERPRISES) if '50 kg/m³' is a valid density for any of their products or if it is a typo for '550 kg/m³'.

---

## ✅ Self-Resolved Doubts

### DOUBT-101: Technical Specifications → Density *(Resolved)*

- **Originally raised at:** Step 1
- **Question:** The source document provides conflicting information regarding the overall density range of AAC blocks.
- **Resolved at:** Step 2 (UPDATE)
- **Resolution:** The new source (FIXOLITE catalog) provides a density of 600-700 kg/m³, which is similar to one of ModCrete's specified ranges (551-650 kg/m³). This confirms that while the IS 2185 standard permits a wide theoretical range (451-1000 kg/m³), commercially available blocks are typically concentrated in the 550-750 kg/m³ range for general use. The conflict is resolved by clarifying the difference between the broad standard and common market offerings in the main table.

---

### DOUBT-102: Technical Specifications → Compressive Strength *(Resolved)*

- **Originally raised at:** Step 1
- **Question:** The source document provides conflicting information regarding the overall compressive strength of AAC blocks.
- **Resolved at:** Step 2 (UPDATE)
- **Resolution:** The new source (FIXOLITE catalog) specifies a compressive strength of 30-40 kg/sqcm (approx. 2.94 - 3.92 N/mm²). This aligns with the general 3-5 N/mm² value mentioned by the first source and falls within a specific grade (likely Class II) of the detailed IS standard table. This confirms that the detailed table is the correct reference, while manufacturers often advertise a specific, common strength grade. The conflict is resolved by framing the different values as representing different levels of detail (general marketing vs. specific grade), which is now reflected in the technical specifications table.

---

