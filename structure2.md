**INDIAN B2B MARKETPLACE**

**Category Wikipedia**

**Universal Structure Guide**

─────────────────────────────────────────────────────

*Complete section-by-section reference for AI agents generating B2B product encyclopedias*

*Covers: what each section is, why it exists, what data to extract, and how to write it*

**How to Read This Guide**

This document is the master reference for any AI agent that needs to generate or update a category Wikipedia on an Indian B2B marketplace. Every section below describes one part of the Wikipedia structure in full detail: what it is, why it matters, what raw data feeds into it, and exactly what the agent should write.

The structure is universal and category-agnostic. It works equally for e-rickshaws, industrial pumps, packaging film, steel rods, industrial chemicals, or textile fabrics. The agent adapts the content of each section to the specific category but never changes the section structure itself.

> GOLDEN RULE Every MAJOR section (1 to 9) must appear in every Wikipedia, in the exact order shown. However, for SUBSECTIONS (e.g. 2.14 Dimensions & Logistics) or specific data points: if the agent finds absolutely no data from the provided sources AND a web search yields no relevant context, the agent must OMIT that subsection entirely rather than guessing, hallucinating, or inserting a "📭 No data found" placeholder. Never invent data.



**Complete Section List**

|        |                                  |                                               |                            |
|--------|----------------------------------|-----------------------------------------------|----------------------------|
| **#** | **Section Name**                 | **Primary Purpose**                           | **Key Output**             |
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
| M      | Wiki Metadata                    | System tracking                               | Metadata table             |

> QF Quick Facts The scannable infobox — always the very first thing in the Wikipedia



**What This Section Is**

Quick Facts is a compact summary table at the very top of every Wikipedia. It gives a buyer or seller an instant snapshot of the category before they read anything else. Think of it like the grey infobox on the right side of a Wikipedia article — it answers "what is this thing" in under 30 seconds.

**Why It Matters**

B2B buyers often land on a category page while comparing multiple categories simultaneously. The Quick Facts box lets them instantly confirm: Is this the right category? Is my price range correct? Is the brand I've heard of listed here? If the answer is yes to all three, they read further. If not, they leave. A well-written Quick Facts section reduces bounce and signals credibility.

**Fields to Populate**

|                                    |                                                                                                                                                                                                                                                                                                  |
|------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Field**                          | What to Write Here                                                                                                                                                                                                                                                                               |
| **Category Path**                  | The parent \> child hierarchy on the marketplace. Example: "Electrical Equipment \> Motors & Drives \> BLDC Motors". Use the marketplace's exact taxonomy.                                                                                                                                       |
| **Common Names & Aliases**         | ALL names this product is known by — brand trade names, regional colloquial names, Hindi/vernacular names, abbreviations. Example: "E-Rickshaw, Toto, Battery Gaadi, रिक्शा, Battery-Operated Rickshaw". Pull every name mentioned in buyer calls and seller catalogs.                            |
| **Key Specifications**             | The 4–5 specifications that define the product and appear in virtually every listing. These become your Primary Specs in Section 3. Example: "Battery Voltage (48V/60V), Motor Power (650W–9.5kW), Battery Type (Lead-Acid/Lithium), Vehicle Category (L3M/L5M), Seating Capacity".              |
| **Price Range**                    | The full ₹ range from the cheapest variant to the most expensive, with unit clarity. Always include both ex-works and on-road if data exists. Example: "₹39,000 (battery-only component) – ₹2,25,000 (fully equipped branded L5M model) per piece". Source from buyer calls and seller catalogs. |
| **Popular Brands**                 | The 5–10 most frequently mentioned brands across all data sources. Include both domestic manufacturers and importers. List in order of frequency of mention, not alphabetical.                                                                                                                   |
| **Key Standards & Certifications** | All applicable certification bodies and standards for this category. Example: "ARAI, iCAT, BIS, ISI, ISO 9001, RoHS, CMVR (L3M/L5M)". These feed into Section 2.12.                                                                                                                              |
| **Primary Use**                    | One sentence describing the main commercial application. Example: "Last-mile passenger transport and goods carriage in urban and semi-urban India." Keep it to one sentence.                                                                                                                     |
| **Typical MOQ**                    | The minimum order quantity for both retail buyers and B2B fleet/dealer buyers. Example: "1 unit (retail / individual operator); 4–12 units (B2B fleet or dealership inquiry)".                                                                                                                   |

> DATA SOURCES FOR QUICK FACTS Buyer call transcripts (for common names, price range, MOQ), Seller catalogs/PDFs (for brand names, certifications, spec ranges), Web search (for regulatory standards, market names). Quick Facts should be populated last — after all other sections — because it summarises the rest of the Wikipedia.



> 1 Category Overview Market context, regulatory framework, and why this category is complex on B2B marketplaces



**What This Section Is**

Category Overview is the opening narrative of the Wikipedia. It answers: What is this product? Who makes it in India? What rules govern it? What is the market doing? Why is it hard to buy and sell on a B2B platform?

This section should read like the opening two paragraphs of a Wikipedia article — authoritative, factual, India-specific, and immediately useful to someone who has some knowledge of the product but needs orientation.

**Subsections to Write**

**1.1 Plain-Language Definition**

What is this product, in simple terms? Define it without jargon. Mention the product family, its basic function, and where it fits in the broader market. A first-time buyer reading this should understand what the product is within one paragraph.

> AGENT INSTRUCTION Write 3–5 sentences. Cover: what the product does, what it is made of or consists of, where it is used, and one sentence on scale of usage in India. Do NOT copy marketing language from seller catalogs. Rewrite in neutral, factual tone.



**1.2 Market Size & Growth**

Provide India-specific market data: TAM (Total Addressable Market), recent CAGR, absolute market size in units or ₹ crore, and 2–3 specific growth drivers. This contextualises why the category exists on the marketplace and signals its commercial importance.

> AGENT INSTRUCTION Extract market figures from web search (IBEF, SIAM, industry reports). If no India-specific data is found, state "market data not found in current sources" and note what type of source is needed. Never invent market figures. Growth drivers can come from buyer call themes — if many buyers cite "fuel cost savings" or "FAME subsidy", that is a real growth driver.



**1.3 Regulatory Framework**

Every B2B product in India operates within a regulatory environment. This subsection documents: which government bodies govern this product, what approvals are mandatory for sale, what standards must be met, and what happens if a product is non-compliant.

For products with no heavy regulation (e.g., basic raw materials), this subsection still documents BIS marks, GST slabs, import duties, and any state-level requirements.

> AGENT INSTRUCTION Pull regulations from: (1) seller catalogs — certifications listed on spec sheets, (2) web search for the applicable Indian regulatory framework (CMVR for vehicles, BIS for electrical, FSSAI for food-grade, etc.), (3) buyer call transcripts — buyers asking "is it ARAI certified?" are flagging a required certification. Always cite the rule name and governing body, not just the certification code.



**1.4 Market Structure**

Describes the supply side: who makes this product, how the market is organised, and what the typical distribution chain looks like in India.

- Organised vs unorganised split (% of market if available)

- Domestic manufacturers vs importers (especially CKD imports from China)

- Typical distribution chain: Manufacturer → Regional Distributor → City Dealer → End Buyer

- Presence of large branded players vs small assemblers

- Geography of manufacturing clusters

**1.5 Key Trends (Current)**

2–4 significant trends shaping this category right now. These come from a combination of web research and patterns observed in buyer call transcripts.

> AGENT INSTRUCTION Trends should be directional and specific, not generic. Bad trend: "Growing demand for electric vehicles." Good trend: "Rapid shift from Lead-Acid to Lithium-Ion batteries driven by 3-year warranty advantage and lower total cost of ownership — visible in 60% of buyer calls mentioning battery type preference." Extract from call patterns AND web context.



**1.6 Why Complex on B2B Marketplaces**

This is the most important subsection for the marketplace team. It explains why this category is hard to transact online, which informs how the platform designs its listing forms, enquiry flows, and matching logic.

Common sources of B2B marketplace complexity:

- Spec ambiguity — same term means different things to different sellers (e.g. "dry battery")

- Price fragmentation — 30–40% price variation for identical products across geographies

- Certification confusion — buyers cannot verify compliance claims in listings

- High customisation — product is made-to-order with no standard SKUs

- Trust deficit — buyer cannot assess seller quality without visiting factory

- Regulatory non-compliance — non-certified products sold alongside certified ones

- Component vs finished goods mixing — some sellers sell parts, others sell assembled units

> 2 Seller-Side Specifications The full spec universe — 15 fixed subsections, always present, category-adapted



**What This Section Is**

This is the largest and most critical section of the Wikipedia. It is a complete, exhaustive map of every specification that sellers offer for this product category. Every spec that could appear in a product listing, seller catalog, brochure, or B2B enquiry belongs here.

Section 2 is the source of truth for the spec creation engine. When the marketplace generates listing spec fields, auto-fills missing data, or validates seller inputs — it all draws from this section.

> STRUCTURAL RULE: 15 FIXED SUBSECTIONS Section 2 always has exactly 15 subsections (2.1 through 2.15), in the same order, with the same names. The agent adapts the content inside each subsection to the specific category. If no data exists for a subsection and web search yields nothing, omit it entirely. Subsections not applicable to a category get a one-line note explaining why (e.g., "2.10 Operator Interface: Not applicable for raw material bulk commodities — no operator interface exists.") Never delete a subsection.



**2.1 Product Types & Model Variants**

> PURPOSE Define the taxonomy of this product — every distinct type, sub-type, and named variant that exists in the market. This is the first thing an agent or buyer needs to know, because the rest of the specs differ across types.



- List every distinct product type (e.g., Passenger, Loader/Cargo, Specialty)

- For each type: list all known named variants from seller catalogs

- For each variant: note its single most defining spec (what makes it THIS variant)

- Include a simple taxonomy tree if product types are hierarchical

> DATA SOURCES Seller catalogs and PDFs are the primary source. Buyer call transcripts reveal how buyers categorise products in their own language (e.g., "seat wala" vs "loader gaadi"). Both sets of names belong here.



**2.2 Performance Specifications**

> PURPOSE All specs that describe what the product DOES — its output, capacity, speed, efficiency, and limits. These are the most buyer-facing specs and almost always become Primary or Secondary tier specs in Section 3.



- Output / throughput / speed — with units and legal/rated maximums where applicable

- Range / capacity / yield — per cycle, per charge, per hour, per batch

- Efficiency rating — %, grade, class, star rating

- Load / stress tolerance — max load, overload rating, safety factor

- Operating envelope — min/max values for all performance specs

> AGENT INSTRUCTION Always extract both the RATED value (manufacturer claim) and the LEGAL maximum (regulatory cap) when they differ. Flag the gap if rated &gt; legal — this is a spec contradiction (Section 6). Example: A motor rated 35 km/h but legally capped at 25 km/h for L3M must be flagged.



**2.3 Power & Energy System**

> PURPOSE All specs related to how the product is powered. For electric products this is battery and charger specs. For fuel-powered products this is engine fuel specs. For pneumatic tools this is air pressure and compressor specs. Adapt to the category.



- Power source type — Electric (AC/DC), Diesel, Petrol, CNG, Pneumatic, Manual, Hybrid

- Rated input — Voltage (V), Current (A), Frequency (Hz), Pressure (bar/psi), Fuel grade

- Energy storage — Battery capacity (Ah, kWh), Fuel tank volume (litres), Reservoir size

- Energy brand — Name of battery/fuel system supplier with warranty

- Charge/refuel method — Type of charger, charging time, rapid charge option, fuel grade

- Energy warranty — Duration, conditions, what voids it

> DATA SOURCES Seller PDFs for rated specs. Buyer call transcripts for real-world performance claims and brand preferences. Web for regulatory input requirements.



**2.4 Prime Mover / Drive System**

> PURPOSE The core mechanism that converts energy into motion or work — motor, engine, actuator, pump, compressor. This is category-specific and highly technical. Get exact rated values.



- Prime mover type — Motor type (BLDC, AC Induction, Servo), Engine type (4-stroke, 2-stroke, diesel), Hydraulic, Pneumatic

- Power rating — Rated watts/kW/HP at stated RPM. Include peak and continuous ratings

- Drive controller/inverter — Amp rating, tube count, frequency, drive type

- Drive mechanism — Direct drive, belt drive, chain drive, gearbox (ratio), CVT

- Operating RPM range — idle, rated, maximum

- Prime mover warranty — months, conditions

**2.5 Structural Body & Frame**

> PURPOSE Physical construction of the product — the structure that holds everything together. Material, dimensions, weight, and finish determine durability, price, and suitability for the application.



- Frame/chassis material — MS (Mild Steel), SS (Stainless Steel), Aluminium, FRP, Cast Iron

- Body/panel material — Same options, specify separately from frame

- Overall dimensions — Length × Width × Height in mm or feet. Both loaded and unloaded if relevant

- Tare weight (unladen) — kg

- Surface finish — Paint type, coating, galvanising, powder coat, anodising

- Corrosion protection — Method and rating

> AGENT INSTRUCTION Material is a price driver. Note price differential where data exists (e.g., "SS body adds ₹5,000 over MS"). Dimensions from seller catalogs. Weight from shipping specs in PDFs.



**2.6 Mechanical Systems**

> PURPOSE All mechanical sub-systems that affect ride quality, handling, braking, and durability. For vehicles: suspension, brakes, steering. For machinery: motion systems, bearings, seals.



- Suspension system — Type (telescopic/leaf spring/coil), stroke, rating, heavy-duty variants

- Braking system — Type (drum/disc/hydraulic), actuation (mechanical/hydraulic/electronic), ABS if present

- Steering — Type, turning radius, power assist if any

- Transmission — Automatic, manual, CVT, gearless, ratio

- Other mechanical — Bearings type, seal spec, lubrication requirement, service interval

**2.7 Working / Contact Surfaces**

> PURPOSE The parts of the product that make contact with the ground, material, or workpiece — tyres, blades, nozzles, dies, pads, liners. These are wear parts with specific replacement cycles.



- Contact element type — Tyre, blade, die, nozzle, pad, roller, liner

- Size specification — Tyre size (e.g., 3.75×12), blade dimensions, nozzle diameter

- Rating — Ply rating, hardness (HRC/HB), pressure rating, temperature rating

- Recommended brands — OEM supplier and acceptable alternatives

- Replacement cycle — km, hours, cycles, or condition-based

- Availability — OEM vs aftermarket, availability in Tier-2/3 cities

**2.8 Payload & Cargo Specifications**

> PURPOSE Specs about how much the product can carry, store, or process. Critical for buyers calculating ROI. For transport: load capacity and cargo dimensions. For machinery: batch size and throughput. For storage: tank/bin volume.



- Rated load capacity — kg, litres, units, MT

- Cargo/working area dimensions — Length × Width × Height of usable space (in feet or mm)

- Load distribution — UDL (Uniformly Distributed Load), point load limits

- Material interface — Coupling type, hook rating, port size, inlet/outlet dimensions

- Special cargo features — Tie-down points, drainage, liner material, temperature control

> AGENT INSTRUCTION For loader vehicles, cargo bed size (dala dimensions) is a Primary Spec. For chemical tanks, inner liner material and corrosion resistance are Primary Specs. Always adapt to what cargo spec is most commercially critical for the category.



**2.9 Operator / User Interface**

> PURPOSE How a human interacts with the product — controls, display, seating, safety systems. Less critical for passive products (raw materials, components) but essential for machinery, vehicles, and tools.



- Controls — Dashboard layout, switches, pedals, levers, HMI touchscreen

- Display/instruments — Speedometer, battery gauge, hour meter, fault indicator

- Seating — Capacity, material, adjustability, certification

- Cabin/enclosure — Open, semi-enclosed, fully enclosed, AC/non-AC

- Safety systems — Emergency stop, interlocks, overload alerts, roll-over protection

> NOT APPLICABLE NOTE For raw materials, basic components, or packaging materials, write: "2.9 Operator Interface: Not applicable — this product has no operator interface. Not relevant for spec creation." Do not delete the subsection.



**2.10 Electrical & Connectivity**

> PURPOSE All electrical input requirements, control interfaces, and connectivity specs. Becomes critical for industrial machinery, automation equipment, and smart products.



- Mains supply — Phase (single/three), voltage (230V/415V), frequency (50Hz), plug type

- Control signal interface — Analogue (4–20mA, 0–10V), Digital (RS485, Modbus, CANbus)

- Telematics/IoT — GPS, SIM slot, OTA update, remote diagnostics, app connectivity

- Electrical protection — MCB rating, IP class, earthing requirement

**2.11 Environmental & Operating Conditions**

> PURPOSE The operating envelope for the product — what conditions it can function in. Critical for buyers in challenging environments (cold storage, outdoor, dusty, humid, high altitude).



- Operating temperature — Min and max °C (both storage and operating)

- IP / Ingress Protection rating — IP54, IP67, NEMA 4X etc.

- Humidity tolerance — % RH

- Altitude limit — Metres above sea level (important for hill-state buyers)

- Dust/water resistance — Additional certifications beyond IP rating

**2.12 Certifications & Compliance**

> PURPOSE Every certification and compliance mark that applies to this product. This subsection has three distinct levels — product-level, component-level, and manufacturing-level. Treat them separately.



**Level 1 — Product / Vehicle Level**

The certification that the ASSEMBLED PRODUCT must hold to be legally sold or operated. Examples: ARAI/iCAT type approval (vehicles), BIS registration (electronics), FSSAI license (food-grade equipment), CE marking (export to EU).

**Level 2 — Component Level**

Certifications on KEY COMPONENTS within the product. Examples: BIS certification on batteries, RoHS compliance on electronics, ISI marking on steel, Hallmark on gold jewelry.

**Level 3 — Manufacturing Level**

Quality management system certifications held by the MANUFACTURER. Examples: ISO 9001:2015 (quality management), ISO 14001 (environmental), IATF 16949 (automotive supply chain).

> AGENT INSTRUCTION Extract all three levels separately. Seller catalogs mention Level 2 and 3. Regulatory web search fills Level 1. Buyer call transcripts reveal which certifications buyers actually check ("Is it iCAT certified?" = Level 1 is commercially critical). For each certification: list the code, the full name, the governing body, and whether it is mandatory or voluntary.



**2.13 Warranty Matrix**

> PURPOSE Complete warranty coverage across every major component. Presented as a structured matrix, not as prose. The matrix is used by the spec creation engine to auto-fill warranty fields in listings and flag listings with suspiciously low warranty claims.



|                              |                                                  |                                  |                                                         |
|------------------------------|--------------------------------------------------|----------------------------------|---------------------------------------------------------|
| **Component**                | **Standard Warranty**                            | **Premium Warranty**             | **What Voids It**                                       |
| Full product / chassis       | \[X months / Y km / Z hours\]                    | \[X months / Y km / Z hours\]    | Overloading, unauthorised modification, accident damage |
| Energy system (battery/tank) | \[X months — lead acid\] / \[Y years — lithium\] | \[Extended option if available\] | Overcharging, wrong fuel grade, physical damage         |
| Prime mover (motor/engine)   | \[X months\]                                     | \[X months\]                     | Operating beyond rated RPM, wrong lubricant             |
| Drive controller / inverter  | \[X months\]                                     | \[X months\]                     | Water ingress, voltage surge                            |
| Consumables (tyres, blades)  | Typically not warranted                          | N/A                              | N/A — replaced based on wear                            |

> DATA SOURCES Seller PDFs are the primary source — warranty terms are usually on the last page of a catalog. Buyer call transcripts reveal which warranty terms matter most to buyers (battery warranty is almost always the #1 concern in battery-powered product categories).



**2.14 Dimensions & Logistics**

> PURPOSE Shipping and packaging specifications — essential for the marketplace to calculate freight costs, container loading, and last-mile delivery feasibility.



- Packed dimensions — L × W × H in cm, gross weight in kg

- Units per 20ft container — FCL count

- Units per 40ft container — FCL count

- Assembly requirement — Fully assembled / SKD (Semi-Knocked Down) / CKD (Completely Knocked Down)

- Special handling — Fragile, hazardous, oversized load, temperature-sensitive

- Stackability — Max stack height, stack weight limit

**2.15 After-Sales & Serviceability**

> PURPOSE How easy is it to get the product serviced after purchase? This is a top concern for B2B buyers who cannot afford downtime. Sellers with strong service networks command premium pricing.



- Authorised service network — Number of service centres, geographic coverage (Tier-1/2/3 cities)

- Service centre location relevance — Are service centres present in buyer's region?

- Spare parts availability — OEM parts: readily available / seasonal / import-dependent

- Common wear part replacement cost — Approximate ₹ for most frequently replaced parts

- MTBF (Mean Time Between Failures) — Manufacturer-stated or field-observed

- Scheduled maintenance interval — Hours/km/months between service visits

- Self-service capability — Can operator do basic maintenance without technician?

> 3 Buyer Specifications What buyers actually ask, what they prioritise, and what they miss



**What This Section Is**

Section 4 maps the buyer's perspective on specifications — not what sellers offer, but what buyers ask for. It is compiled from buyer enquiry call transcripts, enquiry form submissions, and observed purchasing patterns. This section powers the buyer-side matching engine.

**Subsections**

**4.1 Top Buyer Questions (Ranked)**

A numbered list of the most common questions buyers ask, in order of frequency. This comes directly from analysing buyer call transcripts. Example format:

- 1\. "Kitna price hai / on-road price kya hai?" — Price is always asked first

- 2\. "Battery kaisi hai — sukhi ya pani wali?" — Battery type is the second most common question

- 3\. "Mileage kitna milega ek charge mein?" — Range per charge

- 4\. "Kitne saal ki warranty hai battery pe?" — Battery warranty

- 5\. "RTO aur insurance milta hai price mein?" — On-road inclusions

> AGENT INSTRUCTION Extract from buyer call transcripts only. Count frequency. Rank by count. Include the actual language buyers use (Hindi, English, mixed) — this is critical for the agent's enquiry response system to recognise buyer intent.



**4.2 Buyer Priority Matrix**

A table showing which specs each buyer segment prioritises. Uses the buyer personas defined in Section 8 as row headers and the Primary + Secondary specs from Section 3 as columns.

|                      |                             |                             |                                 |
|----------------------|-----------------------------|-----------------------------|---------------------------------|
| **Spec**             | **First-Time Operator**     | **SME Logistics Buyer**     | **Fleet/Dealer Buyer**          |
| \[Primary Spec 1\]   | High — first question       | Medium — secondary concern  | High — affects fleet ROI        |
| \[Primary Spec 2\]   | Medium                      | High — application-critical | High — determines eligibility   |
| \[Primary Spec 3\]   | High — primary price driver | Medium                      | Medium — willing to pay premium |
| \[Secondary Spec 1\] | High — operational concern  | High — downtime risk        | High — fleet uptime             |
| \[Secondary Spec 2\] | Medium                      | Low                         | High — compliance requirement   |

**4.3 Specification Gaps Buyers Miss**

These are specs that are commercially important but that buyers consistently fail to ask about. When they don't ask, they end up with a product that doesn't fit their use case. The agent flags these in enquiry response scripts.

> EXAMPLES OF COMMON GAPS Buyers often do not ask about: (1) Controller amperage — they ask about motor wattage but not controller, which limits real-world performance. (2) Actual vs displayed speed — displayed speed may be set lower to show regulatory compliance. (3) Warranty conditions — buyers ask duration but not what voids it. (4) On-road price inclusions — buyers assume RTO is included when it may not be. These are patterns from call analysis.



**4.4 Enquiry Form vs Call Behaviour Gaps**

Buyers often write one set of specs in their online enquiry form and reveal different or additional requirements during the follow-up call. Documenting this gap helps the platform design better enquiry forms.

- What buyers write in forms: usually price range, quantity, and 1–2 broad specs

- What buyers reveal on calls: specific use case, local terrain/road conditions, financing need, timeline, past bad experiences

- Implication: enquiry forms must prompt for use-case context, not just spec values

**4.5 Total Cost of Ownership (TCO) Framing**

How buyers in this category think about the cost of the product over its lifetime. Some buyers only consider upfront cost (first-time operators). Others think in TCO terms (fleet buyers, large SMEs). Documenting this helps the platform build the right ROI calculators.

- Upfront buyers: focus on ex-showroom price, EMI availability, initial warranty

- TCO buyers: calculate battery replacement cycle, fuel/electricity cost, maintenance cost, resale value

> 4 Most Relevant Spec Combinations Reference configurations from entry to premium — the spec decision tree made into tables



**What This Section Is**

Section 5 documents the STANDARD BUNDLES of specs that actually exist in the market — the configurations that buyers actually buy and sellers actually sell. Rather than treating every spec independently, this section shows how specs cluster together into coherent product tiers.

This section is used by the matching engine to: (1) suggest complete spec bundles to buyers who only specify one or two specs, (2) flag listings whose spec combinations don't match any known market configuration (potentially contradictory or false), and (3) generate "buyers also considered" recommendations.

**5.1 Configuration Tier Table**

A structured table showing the complete spec bundle for each commercial tier, from the most basic/affordable to the most premium/high-performance.

|                      |                 |                                  |                         |                             |                  |
|----------------------|-----------------|----------------------------------|-------------------------|-----------------------------|------------------|
| **Tier**             | **Config Name** | **Primary Spec Values**          | **Key Secondary Specs** | **Typical Price Range (₹)** | **Target Buyer** |
| Entry                | \[Name\]        | \[P1 value, P2 value, P3 value\] | \[S1, S2, S3\]          | ₹\[min\] – ₹\[max\]         | \[Buyer type\]   |
| Mid                  | \[Name\]        | \[P1 value, P2 value, P3 value\] | \[S1, S2, S3\]          | ₹\[min\] – ₹\[max\]         | \[Buyer type\]   |
| Premium              | \[Name\]        | \[P1 value, P2 value, P3 value\] | \[S1, S2, S3\]          | ₹\[min\] – ₹\[max\]         | \[Buyer type\]   |
| Enterprise/High-Perf | \[Name\]        | \[P1 value, P2 value, P3 value\] | \[S1, S2, S3\]          | ₹\[min\] – ₹\[max\]         | \[Buyer type\]   |

> AGENT INSTRUCTION Fill this table with REAL configurations from seller data — use actual products mentioned in catalogs and calls as anchors. If a configuration is hypothetical or inferred, mark it as "[Inferred — no direct source]". Configurations must be internally consistent — no contradictions.



**5.2 Use-Case Configurations**

Some categories have one product sold across many different use cases, each requiring a different spec bundle. This subsection documents those use-case-specific bundles.

- \[Use Case 1\] — Recommended spec bundle: \[Primary specs, Secondary specs, key Tertiary specs\]

- \[Use Case 2\] — Recommended spec bundle: \[different combination\]

- \[Use Case 3\] — Recommended spec bundle: \[different combination\]

**5.3 Upgrade Paths**

Documents the typical upgrade trajectory — what a buyer changes when they step up from one tier to the next, and what performance or price impact that has.

- \[Entry → Mid\]: Change \[Spec X\] from \[value A\] to \[value B\] → Impact: +₹\[amount\], +\[performance benefit\]

- \[Mid → Premium\]: Change \[Spec Y\] from \[value C\] to \[value D\] → Impact: +₹\[amount\], +\[performance benefit\]

**5.4 Anti-Patterns (Common Mis-Configurations)**

Spec combinations that buyers frequently request but that are technically problematic, commercially unavailable, or suboptimal for their stated use case.

> EXAMPLE Buyers in hilly terrain often request high-capacity batteries for range without requesting upgraded suspension or higher motor torque. This creates a mis-match: the vehicle has range but cannot climb hills with full load. The agent should flag this and recommend the complete configuration required for hill-terrain use.



> 5 Spec Contradictions & Flags Hard conflicts, regulatory violations, terminology ambiguity, and buyer red-flag combinations



**What This Section Is**

Section 6 is the quality control layer of the Wikipedia. It documents every known inconsistency, conflict, regulatory violation, and commercial red flag found across all data sources. The spec contradiction detection engine uses this section to automatically flag problematic listings before they go live.

**6.1 Hard Technical Contradictions**

Spec combinations that are physically or technically impossible. These represent either data entry errors, deliberate misrepresentation, or fundamental misunderstanding of the product.

> FORMAT FOR EACH CONTRADICTION State: [Spec A claims X] + [Spec B claims Y] = Impossible because [technical reason]. Resolution: [Which value is correct and why / what test would reveal the truth].



**6.2 Regulatory Violations**

Spec combinations that would make the product non-compliant with Indian regulations. These are high-severity flags — a listing with a regulatory violation cannot go live.

> FORMAT FOR EACH VIOLATION State: [Spec claim] violates [Rule/Act/Standard name, Section X] because [reason]. The legal maximum/minimum is [value]. Source: [regulatory document or governing body website URL].



**6.3 Commercial & Market Contradictions**

Inconsistencies in pricing, warranty, or availability claims that are not technically impossible but are commercially improbable or inconsistent across sources.

- Price contradictions: Same product quoted at X in City A and Y in City B — document the variation and the likely cause

- Warranty contradictions: Seller A claims 3-year warranty, Seller B claims 6 months for identical product — flag and note which is standard vs exceptional

- Availability contradictions: Product claimed to be "in stock" but delivery time is 45–60 days — flag as inconsistency

**6.4 Terminology Ambiguity Flag Table**

A lookup table for terms that mean different things to different sellers or in different contexts. This is one of the most practically useful parts of the Wikipedia for the matching engine.

|                    |                                                  |                            |                  |                                                          |
|--------------------|--------------------------------------------------|----------------------------|------------------|----------------------------------------------------------|
| **Ambiguous Term** | **Meaning A**                                    | **Meaning B**              | **Meaning C**    | **How to Disambiguate**                                  |
| \[Term 1\]         | \[Definition A — which sellers use it this way\] | \[Definition B — context\] | N/A              | \[Ask this clarifying question / check this other spec\] |
| \[Term 2\]         | \[Definition A\]                                 | \[Definition B\]           | \[Definition C\] | \[Disambiguation rule\]                                  |
| \[Term 3\]         | \[Definition A\]                                 | \[Definition B\]           | N/A              | \[Disambiguation rule\]                                  |

> AGENT INSTRUCTION This table is populated from buyer call transcripts where confusion occurs. Whenever a buyer and seller seem to be using the same word to mean different things, extract the term, document both meanings, and add a disambiguation rule. This table is the single most important input for preventing mis-matches on the platform.



**6.5 Buyer Red-Flag Combinations**

Spec combinations in a listing that should trigger a warning to buyers — not technically impossible, but likely to indicate quality issues or misrepresentation.

- \[Red Flag 1\]: \[Spec combination\] — Red flag because \[reason\]. Buyer should ask seller: \[specific question to verify\]

- \[Red Flag 2\]: \[Spec combination\] — Red flag because \[reason\]

- \[Red Flag 3\]: \[Spec combination\] — Red flag because \[reason\]

> 6 Price-Defining Specs & Price Variation What moves the price needle, by how much, and why prices vary across India



**What This Section Is**

Section 7 is the price intelligence layer of the Wikipedia. It answers: which specifications drive the price of this product, how much does each spec upgrade cost, and why does the same product cost different amounts in different parts of India?

This section powers the marketplace's price estimation engine — when a buyer provides a set of specs, the engine can estimate a fair price range.

**7.1 Price Stack Hierarchy**

A ranked list of specifications in descending order of their price impact. The \#1 item is the single biggest determinant of price. This is derived from pricing data across multiple sellers and configurations.

|          |                          |                                                                                 |                                                        |
|----------|--------------------------|---------------------------------------------------------------------------------|--------------------------------------------------------|
| **Rank** | **Spec**                 | **Price Driver Description**                                                    | **Approximate Price Impact**                           |
| 1        | \[Biggest price driver\] | \[Why this spec drives price — e.g., component cost, manufacturing complexity\] | ₹\[X\] – ₹\[Y\] difference between low and high values |
| 2        | \[Second driver\]        | \[Reason\]                                                                      | ₹\[X\] – ₹\[Y\]                                        |
| 3        | \[Third driver\]         | \[Reason\]                                                                      | ₹\[X\] – ₹\[Y\]                                        |
| 4        | \[Fourth driver\]        | \[Reason\]                                                                      | ₹\[X\] – ₹\[Y\]                                        |
| 5        | \[Fifth driver\]         | \[Reason\]                                                                      | ₹\[X\] – ₹\[Y\]                                        |

**7.2 Price Map by Segment**

A table mapping each configuration tier (from Section 5) to its actual price range observed in the market, with what inclusions are standard at that price.

|                 |                     |                     |                                  |
|-----------------|---------------------|---------------------|----------------------------------|
| **Config Tier** | **Ex-Works Price**  | **On-Road Price**   | **What Is Included**             |
| Entry           | ₹\[min\] – ₹\[max\] | ₹\[min\] – ₹\[max\] | List what is and is not included |
| Mid             | ₹\[min\] – ₹\[max\] | ₹\[min\] – ₹\[max\] | List inclusions                  |
| Premium         | ₹\[min\] – ₹\[max\] | ₹\[min\] – ₹\[max\] | List inclusions                  |
| Enterprise      | ₹\[min\] – ₹\[max\] | ₹\[min\] – ₹\[max\] | List inclusions                  |

**7.3 Ex-Works vs On-Road Delta**

Documents exactly what costs are added between the factory price and the price the buyer pays. Important for marketplace price transparency.

- RTO registration: ₹\[amount\] (varies by state — document known state-wise ranges)

- Road tax: ₹\[amount\] or \[X%\] of ex-works price

- Insurance (1st year): ₹\[amount\] range

- Dealer margin: typically \[X%\] – \[Y%\]

- Freight / delivery: ₹\[amount\] per km or flat rate by distance band

- Total on-road premium over ex-works: approximately ₹\[X\] – ₹\[Y\]

**7.4 Geographic Price Disparity**

The same product often costs significantly different amounts in different cities or states. Document known price variations and their causes.

> EXAMPLE FORMAT Product X: ₹1,10,000 in Patna (dealer city) vs ₹1,40,000 in Sitamarhi (end-point town 120km away) — a 27% premium explained by: (1) additional dealer margin in the downstream town, (2) freight cost, (3) lower competition in remote market. Source: [call reference].



**7.5 Component-Only Pricing**

For categories where components are sold separately from assembled units — critical for dealer and assembler buyers.

- \[Component 1 — e.g., battery set\]: ₹\[price range\], \[warranty\]

- \[Component 2 — e.g., motor + controller\]: ₹\[price range\]

- \[Component 3 — e.g., chassis/body only\]: ₹\[price range\]

**7.6 Market Dynamics Affecting Price**

- Government subsidy / scheme impact — e.g., FAME II subsidy reduces price by ₹X for qualifying models

- Input cost sensitivity — e.g., steel price increase of 10% raises product price by ~3%

- Seasonal demand patterns — e.g., higher demand in Q4 (Oct–Dec) before festive season leads to 5–10% premium

- Import duty impact — for categories with significant CKD imports from China

> 7 Buyer Personas Detailed profiles of every distinct buyer type in this category



**What This Section Is**

Section 8 maps the distinct types of buyers who purchase this product on the marketplace. Each persona is a composite profile built from patterns observed across multiple buyer call transcripts. Personas are used to: personalise enquiry response scripts, set correct buyer expectations in listing pages, and tune the matching algorithm's weighting of specs by buyer type.

**Persona Profile Fields (repeat for each persona)**

|                                    |                                                                                                                                                                                |
|------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Field**                          | What to Write                                                                                                                                                                  |
| **Persona Name & Type**            | A descriptive label (e.g., "First-Time Owner-Operator", "SME Logistics Buyer", "Fleet Aggregator"). Not a real name — a type description.                                      |
| **Geography**                      | Which states or city tiers this persona is typically found in. Example: "Tier-2 and Tier-3 cities in Bihar, UP, West Bengal — highest density of this buyer type."             |
| **Business Context**               | What business are they in and why are they buying this product? 2–3 sentences describing their situation.                                                                      |
| **Budget Range**                   | Typical per-unit budget and total order budget. Example: "₹1,00,000 – ₹1,20,000 per unit. Typically buying 1 unit at a time."                                                  |
| **MOQ & Order Pattern**            | How many units, how often, and how they typically order (walk-in, online enquiry, WhatsApp, referral).                                                                         |
| **Primary Specs They Prioritise**  | The 2–3 specs from Section 3 that this persona asks about first. Cross-reference with Section 4.1.                                                                             |
| **Specs They Tend to Miss**        | The gaps from Section 4.3 that apply specifically to this persona.                                                                                                             |
| **Call & Enquiry Behaviour**       | How do they phrase their enquiry? What language do they use? What signals that they are this persona type? 3–4 specific behavioural cues from transcript analysis.             |
| **Financing & Payment Preference** | Cash, bank loan, NBFC loan, government scheme, EMI, trade credit — what is typical for this persona?                                                                           |
| **Decision Timeline**              | How long does it typically take this persona to go from first enquiry to purchase decision?                                                                                    |
| **Red Flags in Their Questions**   | Questions that signal this buyer may not convert or may have unrealistic expectations — e.g., asking for a 1-year warranty on a component that only carries 6 months standard. |

> DATA SOURCES Buyer call transcripts exclusively. Each persona should be grounded in at least 3–5 actual call examples. Do not invent personas — extract them. If fewer than 2 distinct buyer types are observable in the data, document only the observed types and flag that more call data is needed.



> 8 Seller Personas Detailed profiles of every distinct seller type and their risk profile



**What This Section Is**

Section 9 maps the supply side — the distinct types of sellers and manufacturers who operate in this category. Seller personas help buyers understand who they are buying from and what quality/reliability risks that implies. They also help the marketplace design different seller verification requirements by persona type.

**Seller Persona Profile Fields**

|                              |                                                                                                                                                               |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Field**                    | What to Write                                                                                                                                                 |
| **Seller Type & Role**       | Manufacturer, Brand Owner, Regional Distributor, Multi-Tier Dealer, CKD Importer, Trader/Broker. Note if they are also a manufacturer or purely trading.      |
| **Geography**                | Where are they based and what territory do they serve? Example: "Manufacturer based in Noida, serving North and Central India through distributor network."   |
| **Scale**                    | Annual production/sales volume if known. Alternatively: "small" (\<100 units/month), "mid" (100–500), "large" (500+).                                         |
| **Product Range**            | Which product types and variants do they carry? Do they stock all tiers or specialise?                                                                        |
| **Certifications Held**      | Which of the certifications in Section 2.12 do they actually hold? Note any gaps vs what they claim.                                                          |
| **Pricing Model**            | Do they quote ex-works or on-road? Do they offer dealer rates? Is battery price bundled or separate?                                                          |
| **Call & Listing Behaviour** | How do they describe their products? What spec language do they use? What do they emphasise?                                                                  |
| **Strengths**                | What do they do well — quality, price, service network, customisation, speed?                                                                                 |
| **Buyer Risk Factors**       | Key risks for a buyer transacting with this seller type — warranty enforceability, quality consistency, post-sale support, regulatory compliance of products. |

> 9 Listing Spec Tiers Classifying every spec from Section 2 into Primary, Secondary, and Tertiary tiers



**What This Section Is**

Section 3 is a derived section — it takes all the specs catalogued in Section 2 and classifies each one into one of three commercial tiers based on how important it is for listing creation, buyer search, and conversion decisions.

This classification is what the spec creation engine uses when it builds listing forms. Primary specs become mandatory fields that listings cannot go live without. Secondary specs are strongly recommended fields. Tertiary specs are optional advanced fields.

**The Three Tiers**

|                 |                                                                                                                                                                                                                                                                                                                                                                                                     |
|-----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **PRIMARY — P** | Minimum 2, Maximum 3 specs. The specs that appear in EVERY listing for this category and are the first things buyers look at. These go in the main search filter and are used for auto-matching buyer enquiries to seller listings. Without Primary specs, a listing is incomplete. The agent picks the 3 specs from Section 2 that are most frequently mentioned in seller listings and buyer calls combined. |

|                   |                                                                                                                                                                                                                                                                                                                                                                      |
|-------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **SECONDARY — S** | Minimum 2, Maximum 3 specs. Specs that are asked about in more than 60% of buyer enquiry calls or appear in most seller catalogs. These differentiate products within the same Primary spec bucket. Example: two e-rickshaws may both be 48V/1200W (Primary match), but differ on range and warranty (Secondary differentiation). Secondary specs are the real conversion drivers. |

|                  |                                                                                                                                                                                                                                                                                                                              |
|------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **TERTIARY — T** | All remaining specs from Section 2. Used for deep technical filtering, compliance documentation, spec contradiction detection, and comparison tables. Not shown in standard listing view but searchable. A buyer configuring a custom fleet looks at Tertiary specs. An auditor checking compliance looks at Tertiary specs. |

**Tier Assignment Rules**

> HOW THE AGENT ASSIGNS TIERS Step 1: Count how many buyer call transcripts mention each spec type. Any spec mentioned in &gt;80% of calls = Primary candidate. 40–80% = Secondary candidate. &lt;40% = Tertiary. Step 2: Count how many seller catalogs/PDFs prominently feature each spec. Any spec in the headline or first spec table of &gt;70% of catalogs = Primary candidate. Step 3: Cross-check with Section 6 (Spec Contradictions). Any spec that appears in contradiction flags is always Tertiary at minimum — it needs verification before it drives matching. Step 4: Assign exactly 2 or 3 specs as Primary, and 2 or 3 specs as Secondary. If 5 specs all seem equally important, look at which 3 are asked FIRST in buyer calls — those are Primary.



**Example Tier Table (Category-Specific — Fill for Your Category)**

|                                         |                       |           |                                                                             |
|-----------------------------------------|-----------------------|-----------|-----------------------------------------------------------------------------|
| **Spec Name**                           | **Source Subsection** | **Tier**  | **Rationale**                                                               |
| \[Spec 1 — most commercially critical\] | 2.2 / 2.3 / 2.8       | PRIMARY   | Mentioned in \>80% of buyer calls. First question buyers ask.               |
| \[Spec 2 — defines product category\]   | 2.1 / 2.4             | PRIMARY   | Defines the product type. Without it, buyer cannot filter.                  |
| \[Spec 3 — primary price driver\]       | 2.3 / 2.5             | PRIMARY   | Single biggest driver of price variation. Used in price range search.       |
| \[Spec 4 — conversion spec\]            | 2.2 / 2.8             | SECONDARY | Asked in 60–70% of calls. Differentiates models at same price point.        |
| \[Spec 5 — warranty or brand\]          | 2.13                  | SECONDARY | Warranty period drives buyer preference between similar-spec products.      |
| \[Spec 6 — certification\]              | 2.12                  | SECONDARY | Buyers increasingly asking for certifications. Strong trust signal.         |
| \[Spec 7 — technical detail\]           | 2.4 / 2.6             | TERTIARY  | Technical spec asked by fleet buyers and dealers, not first-time buyers.    |
| \[Spec 8 — logistics/dimensions\]       | 2.14                  | TERTIARY  | Required for freight calculation. Not a buying decision factor.             |
| \[All remaining specs\]                 | 2.7 – 2.15            | TERTIARY  | Supporting specs for compliance, deep comparison, and export documentation. |

> AGENT INSTRUCTION Replace bracketed placeholder rows with actual spec names from Section 2 of the Wikipedia being generated. The tier table is category-specific — it will be different for e-rickshaws, steel pipes, textile looms, and chemical drums. Run the tier assignment rules every time a new data source is ingested that might change spec frequency rankings.




> G Glossary Every technical term, abbreviation, regulation, and trade word — defined clearly



**What This Section Is**

The Glossary defines every piece of specialist vocabulary used anywhere in the Wikipedia. It has four buckets: technical terms, regulatory terms, local/trade language, and ambiguous terms (cross-referenced from Section 6.4).

The Glossary is used by the matching engine to normalise vocabulary — to understand that "sukhi battery", "dry battery", and "lithium battery" may all refer to the same product depending on context, and to translate between buyer language and seller language.

**Four Glossary Buckets**

**Bucket 1 — Technical Terms**

Component names, engineering specs, system terms. Written for a non-engineer buyer who encounters the term in a listing.

> FORMAT [Term]: [Plain-English definition in 1–2 sentences, as if explaining to a first-time buyer]. Example: "BLDC Motor: Brushless Direct Current motor. A type of electric motor with no physical brushes, which makes it more efficient, quieter, and longer-lasting than older brushed motors. The standard motor type in modern e-rickshaws."



**Bucket 2 — Regulatory Terms**

Laws, approval bodies, certification codes, regulatory categories. Written with enough detail to help a buyer verify compliance.

> FORMAT [Term]: [Full name]. [What it is and who issues it]. [Why it matters for buyers in this category]. [Where to verify: URL or process]. Example: "iCAT: International Centre for Automotive Technology. A government-authorised testing and certification body for vehicles. iCAT certification means the vehicle design has been type-approved for sale in India. Buyers should ask for the type approval certificate number, which can be verified at the Ministry of Road Transport website."



**Bucket 3 — Local / Trade Language**

Hindi, regional language, and colloquial trade terms that appear in buyer calls and seller conversations but not in formal catalogs. These are critical for the enquiry response engine.

> FORMAT [Local term] ([language/region]): [Formal equivalent]. [Context of use]. Example: "Sukhi battery (Hindi): Dry battery / Lithium-ion battery. Used by buyers and some sellers to refer to lithium batteries (as opposed to 'pani wali' / water-based lead-acid batteries). Context: Buyers asking 'sukhi battery kitne ki hai' are asking for the price of a lithium battery pack."



**Bucket 4 — Ambiguous Terms Lookup**

Terms that have multiple valid meanings in this category. Cross-referenced from Section 6.4. Each entry includes the disambiguation rule that the agent should apply when encountering this term.

> M Wiki Metadata System tracking block — always at the very end of every Wikipedia



**What This Section Is**

The Metadata section is a structured tracking block at the end of every Wikipedia. It serves two purposes: (1) traceability — allows any reader to understand what data went into the Wikipedia and when it was last updated, and (2) quality signalling — the confidence scores tell downstream systems how reliable each section is.

**Metadata Fields**

|                                    |                                                                                                                                                                        |
|------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Field**                          | What to Write                                                                                                                                                          |
| **Category Path**                  | Full path in marketplace taxonomy. Example: "Industrial Equipment \> Electric Vehicles \> E-Rickshaws & E-Carts \> Electric Rickshaw Three Wheeler"                    |
| **Tags**                           | Comma-separated searchable keywords that cover: product names, brand names, spec values, use cases, certification codes, regional terms. These power the search index. |
| **Sources Ingested (Total Count)** | Integer count of all data sources consumed to produce this Wikipedia. Format: "32 (18 buyer call transcripts, 10 seller PDFs/catalogs, 4 web sources)"                 |
| **Data Types**                     | List the types: Buyer Call Transcripts / Seller Catalogs / Web Research / Regulatory Documents / Industry Reports                                                      |
| **Brands Covered**                 | All brand names mentioned anywhere in the Wikipedia — including component brands (battery, tyre, motor), not just vehicle brands.                                      |
| **Standards Referenced**           | All regulatory standards, certifications, and IS codes cited anywhere in the Wikipedia.                                                                                |
| **Market**                         | Always: "Indian B2B (with export-relevant notes where applicable)"                                                                                                     |
| **Last Updated**                   | Date of last Wikipedia update in DD-MMM-YYYY format.                                                                                                                   |

**Section Confidence Scores**

A confidence level for each major section, indicating how well-supported the content is by actual source data. This tells downstream systems which parts of the Wikipedia to trust highly vs. which need more data.

|                           |                      |                                                |
|---------------------------|----------------------|------------------------------------------------|
| **Section**               | **Confidence Level** | **Reason / What Would Improve It**             |
| 1\. Category Overview     | High / Medium / Low  | \[Reason\]                                     |
| 2\. Seller Specifications | High / Medium / Low  | \[Reason — note which subsections are thin\]   |
| 3\. Buyer Specifications  | High / Medium / Low  | \[Reason — note if buyer call data is sparse\] |
| 4\. Spec Combinations     | High / Medium / Low  | \[Reason\]                                     |
| 5\. Contradictions        | High / Medium / Low  | \[Reason\]                                     |
| 6\. Price Intelligence    | High / Medium / Low  | \[Reason — price data is often sparse\]        |
| 7\. Buyer Personas        | High / Medium / Low  | \[Reason\]                                     |
| 8\. Seller Personas       | High / Medium / Low  | \[Reason\]                                     |
| 9\. Listing Spec Tiers    | High / Medium / Low  | \[Reason\]                                     |

> CONFIDENCE LEVEL DEFINITIONS HIGH: 3+ independent sources confirm the content. MEDIUM: 1–2 sources, or data from one source type only (e.g., only seller PDFs, no buyer call data). LOW: Inferred from limited data, or taken from web only with no primary source confirmation. Sections with LOW confidence should include a "📭 More data needed" note specifying the source type required.




