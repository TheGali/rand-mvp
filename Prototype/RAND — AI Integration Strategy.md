# RAND Building Advisory Group — AI Integration Strategy

*Prepared by Gali Davidi for Eugene Gurevich, PE, AIA*
*February 2026*

---

## Executive Summary

RAND's Physical Condition Survey takes 3-4 months from site visit to delivered report. The engineering judgment happens in hours. The remaining weeks are spent converting what your engineers already know into formatted documents. AI eliminates that conversion step.

A structured field capture method (SPORT) combined with three automated transformations (dictation to prose, photo to titled slide, observations to Excel dashboard) compresses the post-visit work from months to days.

The prototype runs on synthetic data using your sample report as the output template. The key decision for RAND: whether to process everything on a local workstation (simpler, zero privacy risk) or add a controlled cloud pathway for enhanced photo analysis.

---

## 1. Where the Hours Hide

### The Current Workflow

Your PCS workflow follows a predictable pattern:

1. **Pre-visit** (1-2 days): Document review, resident questionnaire distribution, drawing review.
2. **Site visit** (1-2 days): Roof-to-cellar walkthrough, photos, field notes, representative apartment visits.
3. **Report production** (10-14 weeks): Organization, drafting, partner review, QA, final delivery.

The site visit produces the engineering judgment. Report production consumes the calendar. A single PCS report covers 12 building systems, includes 200+ photos, integrates resident questionnaire data from every unit, and delivers budget projections totaling millions of dollars. Your sample report covered $4.9M in recommended work across roof replacement, window programs, heating plant upgrades, electrical modernization, plumbing, and compliance items.

### Five Bottlenecks

**Field notes to draft.** Engineers write narrative descriptions for 12-15 system sections from handwritten or dictated notes. Each section requires condition descriptions, photo cross-references, code citations, and budget language. This is manual, slow, and varies by writer.

**Photo organization.** Hundreds of photos per site visit need sorting, labeling, matching to specific conditions, and inserting into the report. This step alone takes days.

**Partner review queue.** Senior partners review every report across 10-20 active projects. A draft can sit in queue for 1-3 weeks. Revisions re-enter the queue.

**Context switching.** Engineers carry 5-10 projects at different stages. Returning to a half-finished report after weeks on other sites means re-reading field notes and photos to rebuild context.

**Questionnaire integration.** Resident responses need tallying, statistical summary (percentages, patterns by floor and exposure), and weaving into the appropriate system section with representative quotes.

### The Insight

Your engineers know the finding's full anatomy the moment they see a condition: system, location, observation, recommendation, timeframe, estimated cost. That structured knowledge gets flattened into free-form dictation, then someone spends hundreds of hours extracting structure from narrative to build the report and the Excel control board. The reconstruction step is where the time hides.

---

## 2. The Solution

### Structured Capture: SPORT

Each field observation follows five fields:

> **S**ystem. **P**osition. **O**bservation. **R**ecommendation. **T**imeframe.

Example: *"Roofing. Main roof, northeast section. Modified bitumen showing alligatoring at seams, ponding near drain. Thermographic evaluation followed by full replacement. 1 to 3 years."*

Your one-photo-per-slide PowerPoint format becomes the capture unit. Each slide is one observation, one photo, one database row. The same source data renders into three outputs without manual reformatting.

Photo naming follows the same logic: `01-roof-main-NE-001.jpg`. System code, location, sequence. Photos auto-sort into report sections and match to dashboard categories.

### Three Automated Transformations

**1. Field dictation to report prose.** The engineer dictates a SPORT observation. AI expands it into a full paragraph in RAND's voice, with code references, condition context, and budget projection language. The engineer reviews a finished draft, not a blank page. For structured engineering language following known templates, AI output quality is high.

**2. Photo to titled, categorized slide.** AI reads each photo, generates a descriptive title ("Main Roof Level: Ponding Water Near Northeast Drain"), confirms the system category, and suggests a condition rating. 100+ photos get titled in minutes. The engineer confirms or corrects.

**3. Observations to Excel dashboard.** Every structured observation feeds directly into the control board: system, component, condition, action, cost range, timeline. The dashboard populates itself from field data. No one manually transfers items from the report into Excel.

### What Changes for the Team

**Day 3 partner meeting** works from a populated dashboard and draft report sections instead of raw photos and notes. Partners review and approve instead of organizing.

**Associate hours** shift from writing and formatting to reviewing and refining. The value of each hour goes up.

**Consistency** improves. Every engineer's output follows the same structure and prose style. Juniors produce output that reads like a senior's work, because AI applies RAND's template to every observation.

### What AI Does Not Do

AI does not replace engineering judgment. Your engineers make the assessment. AI handles the conversion from structured observation to formatted deliverable. It processes information through functions you define, using your templates and your standards. It does not freestyle or make engineering calls. The judgment stays with your team.

---

## 3. Data Privacy

This is the strategic decision at the center of the project. Everything else follows from it.

### Three Classes of Data

Your pipeline handles three types of content:

**Class 1: Generic.** Code references, boilerplate condition descriptions, material specifications, standard cost ranges. No building identity attached. Safe for any AI system.

**Class 2: Conditionally safe.** Content that becomes safe once identifying details are removed. Photos without visible addresses, anonymized condition notes, aggregated questionnaire statistics. Requires scrubbing before cloud processing.

**Class 3: Must stay on RAND's network.** Building address paired with condition data, owner names, financial projections tied to specific properties, violation records, proprietary assessment methodologies. The combination of building identity plus condition equals potential liability exposure.

### The Sorting Problem

In theory, you send Class 1-2 to cloud AI for the best quality and keep Class 3 local. In practice, someone has to review every photo and every dictation clip to decide which class it falls in. A wide-angle shot might capture a street sign in the corner. A dictation might mention a building name offhand. Miss one, and client-identifiable data hits a cloud API.

That sorting burden eats into the time savings the pipeline is supposed to create. The cost of a single miss is real: client trust, potential liability, and a data handling process that becomes harder to explain to partners and building boards.

### Two Paths Forward

**Path A: All-Local Processing**

Treat everything as Class 3. No sorting, no scrubbing, no risk of accidental leakage. A dedicated AI workstation on RAND's network handles the full pipeline. Everything stays inside your walls.

| Advantage | Detail |
|---|---|
| Zero privacy risk | Nothing leaves the network. Simple to explain to partners and clients. |
| No sorting burden | Engineers focus on engineering, not data classification. |
| Simpler operations | One system, one workflow, no preprocessing step. |
| Windows-native | Fits RAND's existing IT environment. |

| Limitation | Detail |
|---|---|
| Vision quality ceiling | Local models describe and categorize building photos well. They are weaker at catching subtle structural conditions the engineer might miss (the "second set of eyes" feature). |

**Path B: Local Core + Controlled Cloud for Photos**

Process the core pipeline locally. Add a selective cloud pathway for photos that contain no identifying content (close-ups of cracks, generic rooftop surfaces, interior mechanical rooms) to access stronger AI vision for structural analysis.

| Advantage | Detail |
|---|---|
| Better vision quality | Cloud models are stronger at identifying subtle defects: hairline cracks, early-stage spalling, concealed moisture patterns. |
| Structural second opinion | The feature RAND expressed interest in during our first meeting. |

| Limitation | Detail |
|---|---|
| Manual confirmation step | Someone must verify each photo has no identifying content before sending to the cloud. |
| Narrower but still present | A sorting burden exists. Smaller than reviewing everything (only photos, not dictation or data), but still a manual step per photo. |

### Gali's Take

Start with Path A for the pilot. It eliminates an entire category of operational complexity and makes the privacy story unambiguous. If the vision quality gap matters after you've used the system on real projects, add the controlled cloud pathway later. Starting closed and opening up is straightforward. Walking back a cloud dependency is not.

---

## 4. The Vision Question

This deserves separate attention because it was a specific point of interest in our first conversation.

**What local models handle well:** Describing what's in a building photo (system identification, condition naming, location context), generating descriptive titles, confirming system categories, suggesting condition ratings. For the three core transformations in Section 2, local vision is sufficient.

**Where cloud models pull ahead:** Identifying conditions the engineer might not have flagged. A cloud vision model looking at a photo of a rooftop can sometimes spot early-stage membrane degradation, subtle ponding patterns, or hairline cracks that a field engineer moving through 200+ observations in a day might overlook. This is the "structural second opinion" concept.

**The honest assessment:** This capability is real but bounded. AI is not replacing a PE's judgment on structural conditions. It is adding a statistical check: "Did you notice this area?" The value depends on how often it catches something the engineer missed, and that is hard to measure before running it on real project data.

**The practical framing:** The core pipeline (dictation to prose, photo titling, Excel population) delivers the time savings. The structural second opinion is a quality enhancement on top of that. Proving the pipeline works is step one. Evaluating whether the vision quality gap justifies a controlled cloud pathway is step two, best answered with data from the pilot.

---

## 5. Hardware

A dedicated AI workstation sits on RAND's network like any other PC.

| Option | Specification | Cost Range |
|---|---|---|
| **Windows workstation** (recommended) | Dedicated GPU, 64-128GB RAM, SSD storage | $3,000 - $5,000 |
| Mac alternative | Smaller form factor, quieter, less processing headroom | $1,400 - $2,200 |

The Windows workstation is the stronger fit for RAND's environment. It handles the full pipeline: dictation parsing, report prose generation, photo titling, Excel population. Mac works for smaller teams or supplementary processing if preferred.

No ongoing cloud API costs with Path A. The machine is a one-time capital expense.

---

## 6. Prototype and Pilot Plan

### Phase 1: Prototype (no RAND data required)

A working pipeline that takes SPORT-formatted dictation and building photos as input and produces:

1. Draft report sections in RAND's prose style
2. Titled and categorized photo slides
3. A populated Excel control board

**Built with:**
- Your sample PCS report as the output template (received). This gives us section structure, prose style, budget projection format, and questionnaire integration patterns for all 12 building systems.
- Synthetic SPORT dictations (written to match RAND's subject matter).
- Stock building photos (no privacy concern, demonstrates the vision pipeline).
- Frontier AI models for the demo (best output quality for showing what's possible).

**What I need from RAND to build the prototype:**

| Item | Purpose | Priority |
|---|---|---|
| Excel control board column layout | Confirms the exact dashboard structure so auto-population maps correctly. | Required |
| PowerPoint photo-supplement template | Confirms slide layout and captioning format. | Helpful, not blocking |

The original six-item materials request has collapsed. The sample report covers the output format, prose style, and questionnaire structure. The NDA, raw field notes, and real photos are pilot-phase items, not prototype requirements.

### Phase 2: Demo

The next conversation with RAND is a live demonstration, not a slide deck. Input goes in, formatted output comes out.

### Phase 3: Pilot

One real PCS survey processed through the pipeline on RAND's local hardware, reviewed by RAND's engineering team. This is where the NDA, real field data, and local workstation come into play.

---

## 7. Decisions for RAND

| # | Decision | Options | Gali's Take |
|---|---|---|---|
| 1 | **Data processing approach** | (A) All-local: zero risk, simpler ops, no sorting burden. (B) Local + controlled cloud for photos: better vision quality, manual photo review step. | Start with A. Add B later if the vision gap matters after real-world use. |
| 2 | **Hardware platform** | Windows workstation ($3-5K) or Mac ($1.4-2.2K). | Windows. Fits RAND's environment and gives more processing headroom for vision tasks. |
| 3 | **Structural second opinion in pilot scope** | Include cloud vision pathway in the pilot, or defer to post-pilot evaluation. | Defer. Prove the core pipeline first. The second-opinion feature is valuable but not required to demonstrate time savings. |
| 4 | **Excel control board template** | Share current template with Gali, or describe the column structure. | Share the template. This is the one item needed to build the auto-population layer correctly. |

---

## Appendix: What the Sample Report Confirmed

Your redacted sample PCS report validated the following about RAND's output format:

**Section structure.** 12 system sections (Roof, Exterior Walls, Site Exterior, Building Interiors, Mechanical, Electrical, Plumbing, Fire Suppression, Vertical Transportation, Refuse Removal, Laundry, Low Voltage), each following a consistent pattern: system description, questionnaire statistics, resident quotes, RAND assessment, budget projections.

**Budget line format.** Item name, timeframe category (Current Recommendation / Future Allowance with year range), cost calculation (unit count times unit cost, or lump sum).

**Three cost categories.** Current Recommendation, Future Allowance (1-3 years), and longer-term Future Allowances (7-9, 13-15 years).

**Questionnaire integration.** Percentage-based statistics from resident responses, followed by italicized quotes, woven into the corresponding system section.

**Compliance sections.** Local Law references (LL11/FISP, LL97, LL126, LL88/09, LL152) integrated into relevant system sections with penalty calculations and filing deadlines.

**Sub-totals by system.** Each system section ends with an itemized cost summary, feeding into Appendix A's aggregated funding requirements table.

This output structure is the template for the AI pipeline. Every automated transformation maps to a specific section of this format.

---

*Gali Davidi*
*gali@galileo.tools*
