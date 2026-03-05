# PRD: RAND AI Report Pipeline

## Product Overview

A single-document pipeline that transforms raw field observations into finished Physical Condition Survey reports. One PowerPoint file lives from skeleton to deliverable. Engineers populate it on their phones in the field. AI processes it at the office. Partners review a finished draft instead of assembling one from scratch.

The product replaces 2-3 days of manual report assembly with 30 minutes of AI processing and partner review.

## The Problem

RAND engineers survey buildings, take hundreds of photos, and dictate observations. Back at the office, junior staff spend days assembling these into a formatted report: writing prose, organizing by system, building cost tables, creating the summary command center page. Partners then review the assembled draft on Day 3.

The assembly step is mechanical. It follows templates, uses standard language, and maps to known categories. It's the exact work AI handles well: structured input, formatted output, domain-specific voice.

## Core Principle: One Document

There is no separate input and output. The PowerPoint starts as a skeleton and matures through stages. Every stakeholder (engineer, AI, partner) works inside the same file. The document is the product's interface.

---

## Document Lifecycle

### Stage 1: Skeleton Generation (Before Field Visit)

The system generates a PowerPoint template based on building type and scope.

**Pre-populated:**
- Cover slide (building name, address, survey date, prepared by)
- Command center front page (empty table with system rows, column headers for condition/recommendation/priority/cost)
- Section dividers for each building system (1. Roof, 2. Facade, 3. Windows, etc.)
- Empty cell slides under each section (photo placeholder + text box)
- Summary tables (empty structure, formulas/links ready)

**What the engineer receives:** A document that looks like the final report with nothing filled in. Every slide has a purpose. The engineer just needs to fill in the blanks.

**System categories (RAND standard, ~15):**
1. Roof
2. Facade
3. Windows
4. Entrance/Doors
5. Interiors
6. Mechanical
7. Electrical
8. Plumbing
9. Fire Protection
10. Elevators
11. Site
12. Compliance
13. Laundry
14. Low Voltage
15. Refuse

Each section starts with 5-10 empty cell slots. Engineers can add more if needed.

### Stage 2: Field Capture (Mobile-Optimized)

Engineers work inside the document on their phones using the PowerPoint mobile app (iOS/Android).

**For each observation, the engineer:**
1. Swipes to the next empty cell slide in the relevant section
2. Taps the photo placeholder to insert a photo from their camera roll (or takes one directly)
3. Taps the text box below the photo and dictates or types a SPORT note

**SPORT format (5 fields, easy to remember):**
- **S**ystem: Roof, Facade, Plumbing, etc.
- **P**osition: Where on the building
- **O**bservation: What they see
- **R**ecommendation: What to do about it
- **T**imeframe: When (Immediate, 1-3 Years, 3-5 Years, etc.)

**Example dictation:** "Roofing. Main roof, northeast section. Modified bitumen showing alligatoring at seams, ponding near drain. Full replacement with tapered insulation. One to three years."

**What the engineer does NOT do:**
- Write formal prose
- Estimate costs
- Format anything
- Fill in the command center
- Generate summaries

The document at this stage is ugly but complete. Every observation has a photo and a note in the right section.

### Stage 3: AI Processing (Office Workstation)

The populated document is fed to the AI pipeline on RAND's local workstation. No data leaves the network.

**Per-cell processing (for each observation slide):**

| Step | Input | Output |
|---|---|---|
| 1. Caption generation | Photo | Descriptive photo caption in RAND format ("Photo 4-1. Stair A, 1st floor: Polyethylene zip wall in place at stair entrance for dust mitigation.") |
| 2. System classification | Photo + SPORT note | Verified system category, component type |
| 3. Prose expansion | SPORT dictation + photo | Full RAND-style paragraph (code references, budget language, condition context, template-matched voice) |
| 4. Data extraction | SPORT dictation | Structured fields: condition rating, recommendation, priority tier, estimated cost range |
| 5. Completeness check | All fields | Flag: missing photo, vague observation, no recommendation, system mismatch |

**Cross-document processing (after all cells):**

| Step | Input | Output |
|---|---|---|
| 6. Command center | All cell data | Front page table: one row per observation, columns for system/location/component/condition/recommendation/priority/cost, hyperlinked to cell slides |
| 7. Summary by system | All cell data | Funding requirements table grouped by system and timeframe |
| 8. 20-year timeline | Cost + timeframe data | Capital planning spreadsheet with costs distributed across years |
| 9. Section transitions | System groupings | Transition slides between system sections |
| 10. Numbering + ordering | Full document | Sequential photo numbering, section numbering, consistent ordering |

**Output:** The same PowerPoint, now fully populated. Every cell has a photo, caption, and prose paragraph. The command center links to every cell. Summary tables are filled. Ready for partner review.

**Processing time target:** Under 10 minutes for a 90-observation report.

### Stage 4: Partner Review

Partners open the AI-processed document on Day 3.

**Review workflow:**
1. Open the command center front page. Scan all observations at a glance.
2. Click any row to jump to its cell slide. Read the AI-generated prose alongside the photo.
3. Mark each observation: Approved, Deferred, Needs Discussion.
4. Add partner notes inline (a text box or comment on the slide).
5. After review, re-run a lightweight AI pass to regenerate summary tables reflecting partner decisions.

**What partners are doing:** Reviewing and approving engineering content. Not assembling a report, not formatting, not calculating.

### Stage 5: Export

One-click export into three formats from the approved document:
- **Electronic PDF:** Hyperlinked command center, clickable navigation
- **Bound hardcopy:** Print-ready, paginated for physical binding
- **Board presentation:** Formatted for projection/screen sharing with clients

---

## Mobile-First Field Design

The field capture experience is the critical UX. If engineers won't use it on their phones, the product fails. Every design decision serves one goal: zero friction on a 6-inch screen.

### Template Slide Design (Cell)

Each cell slide is portrait orientation (8.5" x 11") with two zones:

```
+-------------------------+
|                         |
|                         |
|    PHOTO PLACEHOLDER    |
|    (tap to add)         |
|                         |
|    60% of slide height  |
|                         |
|                         |
+-------------------------+
|                         |
|  Photo X-X. [caption]   |  < AI fills this later
|                         |
+-------------------------+
|                         |
|  SPORT NOTE             |
|  (tap to dictate/type)  |
|                         |
|  35% of slide height    |
|                         |
|                         |
+-------------------------+
```

**Design rules for mobile editing:**
- Two tap targets per slide: photo area, text area. Nothing else.
- Photo placeholder covers the top 60%. Large enough to tap easily on a phone. Tapping opens the camera or photo picker.
- Text box covers the bottom 35%. Large font (16pt minimum). Room for 3-5 lines of dictated text.
- Caption line between them is gray/placeholder text. Engineer ignores it. AI fills it in Stage 3.
- No small buttons, no dropdowns, no form fields. Just a photo slot and a text slot.
- Section header (e.g., "4. BUILDING INTERIORS") is visible at the top but not editable. The engineer knows which section they're in.

### Navigation on Mobile

**The problem:** A 90-observation document has 100+ slides. Scrolling through all of them on a phone is painful.

**Solutions:**
- **Section divider slides** are visually distinct (bold system name, different background color). Engineers swipe past them to orient.
- **Empty cells are obviously empty.** The photo placeholder shows a camera icon and "Tap to add photo." The text box shows "Dictate observation here." Full cells look full. Partially filled cells (photo but no note, or note but no photo) show a warning color.
- **PowerPoint mobile's slide sorter view** shows thumbnails. Empty slides are visually distinct from filled ones. Engineer can tap any empty cell to jump to it.
- **Engineers work section by section.** They're on the roof, so they swipe to the Roof section and fill cells. They go to the basement, swipe to Mechanical. The document's section structure matches the physical survey flow.

### Voice Dictation

Phone keyboards have built-in voice dictation (iOS Dictation, Android Voice Typing). The engineer taps the text box, taps the microphone icon, and speaks their SPORT observation. No custom speech-to-text needed.

**SPORT helps dictation quality.** A structured format (System, Position, Observation, Recommendation, Timeframe) gives the engineer a mental template. They speak in order, pause between fields. The AI can parse even if the dictation has minor transcription errors, because it knows the expected structure.

### Adding Extra Cells

If a section needs more observations than the skeleton provided:
- **v1 (simple):** Engineer duplicates an empty cell slide within the section. PowerPoint mobile supports slide duplication.
- **v2 (better):** A "+" slide at the end of each section. Tapping it (or duplicating it) adds a new empty cell.

### File Sync

The PowerPoint lives in RAND's shared drive (OneDrive, SharePoint, or similar). Engineers open it on their phones via the Office mobile app. Changes sync when they have connectivity.

**Offline behavior:** PowerPoint mobile supports offline editing. Changes sync when the phone reconnects. No custom sync logic needed. If multiple engineers are working on different sections simultaneously, PowerPoint's co-authoring handles conflicts (each engineer works in their own section, so conflicts are rare).

---

## Optional: Field AI Suggestions (v2)

Not in the pilot. Documented here for roadmap.

**Concept:** After the engineer drops a photo into a cell, a lightweight cloud API call analyzes the image and returns a suggestion:

> "Possible membrane deterioration visible at the seam. Consider noting the extent of delamination and proximity to the nearest drain."

**Implementation:**
- Trigger: photo inserted into a cell slide
- API: Cloud vision model (Claude, GPT-4V, or Gemini Pro Vision) with a RAND-specific prompt
- Response: 1-2 sentence suggestion displayed as a slide comment or notification
- Connectivity: requires signal. If offline, the request queues and fires when connectivity returns. The suggestion appears later as a comment on the slide.
- Non-blocking: the engineer continues working regardless. The suggestion is advisory.

**Why defer to v2:**
- The core product value is in Stage 3 (office processing), not field assistance
- Connectivity in cellars and mechanical rooms is unreliable
- On-device vision models (Gemma 3n, MiniCPM-V) can run offline on phones but are not accurate enough for engineering-grade observations
- Adding field AI increases complexity without increasing the core value proposition
- Prove the office pipeline first, then layer on field intelligence

---

## AI Processing Pipeline (Technical Detail)

### Input Parsing

The pipeline reads the populated PowerPoint and extracts:
- Slide structure (which section each slide belongs to, based on position relative to section dividers)
- Photo images (extracted as image files)
- Text content (the SPORT dictation from each cell's text box)
- Metadata (slide order, section assignment)

### Model Requirements

**For the pilot (local workstation):**
- Vision + language model that can run on a Windows workstation with a consumer GPU
- Must handle: photo understanding, text generation in a specific voice, structured data extraction
- Candidates: Llama 3.2 Vision (11B or 90B), Qwen2.5-VL, CogVLM2
- The 90B-class models will need a workstation with 48GB+ VRAM (e.g., RTX 4090 or dual RTX 4070 Ti)
- For the pilot, a cloud API on synthetic data is acceptable (no real client data)

**Prompt architecture (per cell):**

Each cell goes through a single multimodal prompt that receives:
1. The photo
2. The SPORT dictation
3. A RAND style guide (few-shot examples of finished paragraphs from existing reports)
4. The system category context

And returns a structured JSON:
```json
{
  "caption": "Photo 1-1. Main roof, NE section: Modified bitumen membrane showing alligatoring at seams with ponding near drain.",
  "system": "Roof",
  "component": "Membrane",
  "location": "Main Roof - NE Section",
  "condition": "Poor",
  "prose": "Modified bitumen roofing membrane on the northeast section of the main roof exhibits widespread alligatoring at seams, indicating advanced UV degradation and loss of flexibility. Ponding water was observed near the northeast roof drain, suggesting inadequate drainage slope or partially obstructed drain assembly. The condition is consistent with a membrane approaching or past its serviceable life. Reference: NYC Building Code Section 1504, Roof Drainage...",
  "recommendation": "Full roof replacement with tapered insulation system. NDL 20-year warranty.",
  "priority": "1-3 Years",
  "cost_estimate": 615000,
  "flags": []
}
```

### Template Matching

The AI doesn't improvise RAND's voice. It matches it.

**Input to the AI:** 3-5 example paragraphs from existing RAND reports for the same system category. These serve as style templates. The AI learns RAND's sentence structure, vocabulary, level of technical detail, and citation habits.

**This is critical.** The output must be indistinguishable from a paragraph written by a RAND engineer. Partners are reviewing drafts, not editing AI-generated text. If the prose reads like AI, the product fails.

### Cost Estimation

Cost estimates come from a reference table maintained by RAND, not from the AI model. The AI identifies the component type and scope, then looks up the cost range from RAND's internal data.

**v1:** A static cost reference table (JSON or CSV) loaded into the pipeline. Columns: system, component, typical scope, cost range per unit, units. The AI maps each observation to a row in this table.

**v2:** The cost table learns from past reports. As RAND approves more reports, the estimates calibrate to their actual project costs.

### Command Center Generation

After all cells are processed, the pipeline:
1. Collects all structured JSON outputs
2. Sorts by system category and observation number
3. Generates the command center table (one row per observation)
4. Inserts hyperlinks from each row to its cell slide
5. Generates the summary-by-system table (costs aggregated by system and timeframe)
6. Generates the 20-year capital timeline (costs distributed across years)
7. Writes all tables back into the PowerPoint template slides

---

## Infrastructure

### Local Workstation (Production)

- Windows PC on RAND's network
- GPU: NVIDIA RTX 4090 (24GB VRAM) minimum, ideally 48GB+ for the 90B-class models
- RAM: 64GB
- Storage: 1TB SSD (models + working files)
- Software: Python runtime, Ollama or vLLM for local inference, the processing pipeline
- Estimated cost: $3,000-5,000

### Cloud (Pilot Only)

- For the prototype built on synthetic data and stock photos
- API: Claude Vision or Gemini Pro Vision
- No RAND client data touches cloud during pilot
- Allows rapid iteration without hardware procurement

### Transition Path

1. Build and prove the pipeline on cloud APIs with synthetic data
2. Validate output quality with Eugene using fake reports
3. Procure workstation, install local models
4. Test with a real scrubbed report (or synthetic data matching a real building)
5. Deploy for production use

---

## CTO Recommendation (Deliverable for Eugene)

Eugene needs a document to get CTO sign-off on the local infrastructure approach. This should be a separate one-page memo covering:

- **What:** AI-assisted report generation running on a dedicated Windows workstation on RAND's network
- **Why local:** Zero data leaves the network. No cloud dependency. No ongoing API costs. Compliant with client confidentiality requirements by default.
- **What it does:** Converts engineer field observations (photos + structured notes) into formatted report drafts. Does not make engineering decisions. Does not replace engineer judgment. Generates prose and data tables from structured input using RAND's own templates and standards.
- **What it costs:** One-time $3-5K for hardware. No recurring fees. Electricity only.
- **IT burden:** Minimal. The workstation runs a self-contained pipeline. No integration with existing systems required. RAND's IT team would need to: (1) set it up on the network, (2) maintain standard Windows updates. The pipeline itself is maintained by Galileo.
- **Security posture:** All processing local. No external API calls. No data exfiltration vector. The workstation is air-gappable if needed.
- **Risk:** If the workstation fails, RAND reverts to manual report assembly (status quo). No operational dependency.

---

## Pilot Scope

### What to build first
1. PowerPoint skeleton template (mobile-optimized cell layout)
2. Processing script that reads a populated PPT and runs each cell through the AI pipeline
3. Output: the same PPT with prose, captions, and command center populated

### What to test
- Give Eugene a skeleton, have him (or an engineer) fill it with stock building photos and rough SPORT notes on a phone
- Process it through the pipeline
- Compare output quality to a real RAND report

### What success looks like
- Partners can review the AI-generated draft with minimal edits
- Prose matches RAND's voice (not generic AI writing)
- Command center is accurate and hyperlinked
- Cost estimates are in the right ballpark
- Total processing time under 10 minutes for a full report

### What to defer
- Field AI suggestions (v2)
- Automated cost table learning (v2)
- Multi-engineer co-authoring workflows (v2)
- Client-facing Vortex dashboard (v2, connects to Eugene's broader vision)
- Local workstation deployment (build on cloud first, migrate after pilot validates)

---

## Open Questions for Eugene

1. **Template flexibility:** How many distinct cell templates does RAND need per system? His PPT shows "template-level content which will need to be flexible depending on the element." Need to understand the range: is it 3 variants or 30?
2. **Cost reference data:** Does RAND have an internal cost table, or do engineers estimate from experience? This determines whether the AI can auto-populate costs or should leave them for partner review.
3. **SPORT adoption:** Will engineers accept a structured dictation format, or will they resist? If resistance is likely, the AI needs to handle fully unstructured notes (harder but doable).
4. **Existing slide decks:** Does RAND already produce slide decks in the field that we can study for current input patterns?
5. **Partner review behavior:** How do partners currently mark up drafts? Track changes? Printed red-pen? This shapes the review UX in the document.
