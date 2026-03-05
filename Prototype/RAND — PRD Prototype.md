# PRD: RAND AI Report Pipeline — Prototype

*Prepared by Gali Davidi*
*March 2026*

---

## Purpose

This document specifies the prototype for RAND Engineering's AI-powered Physical Condition Survey (PCS) report pipeline. The prototype proves one thing: structured field observations (photo + dictated note) go in, formatted report content comes out.

This PRD is written to be self-contained. When fed to an AI coding assistant alongside the example files listed at the end, it should contain everything needed to build a working prototype.

**This prototype will be built in its own repository, not inside the Obsidian vault.**

---

## What the Prototype Does

Takes a populated PowerPoint file (photos + SPORT-format notes on each slide) and produces:

1. **Report prose** for each observation, written in RAND's engineering voice
2. **Photo captions** in RAND's naming convention
3. **A command center table** (Excel) summarizing all observations with structured data
4. **A funding requirements summary** grouped by system and timeframe

The prototype runs on cloud APIs (Claude or GPT-4o) using synthetic data. No real client data. Local model deployment is a later phase.

---

## What the Prototype Does NOT Do

- Field capture (engineers use PowerPoint Mobile, that already works)
- Partner review workflow (humans review the output manually)
- Local model inference (cloud APIs only for now)
- Cost estimation from RAND's internal tables (uses placeholder ranges)
- Export to PDF, hardcopy, or presentation formats
- PowerPoint template generation (the skeleton is built manually for the prototype)

---

## Architecture

```
┌────────────────────────────────────────────────────┐
│                  INPUT                              │
│  Populated PowerPoint (.pptx)                       │
│  - Section divider slides (system headers)          │
│  - Observation slides (photo + SPORT note each)     │
└────────────────┬───────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│              PARSER                                 │
│  python-pptx reads the PowerPoint:                  │
│  - Identifies section dividers vs observation slides │
│  - Extracts photo (as image file) from each slide   │
│  - Extracts text (SPORT note) from each slide       │
│  - Maps each slide to its parent system section     │
│  - Assigns sequential observation numbers           │
└────────────────┬───────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│         AI PROCESSING (per observation)             │
│  For each slide, send to Claude/GPT-4o:             │
│  - The photo                                        │
│  - The SPORT note text                              │
│  - The system category (from section divider)       │
│  - 2-3 example paragraphs from RAND's style guide   │
│                                                     │
│  Model returns structured JSON:                     │
│  {                                                  │
│    "caption": "Photo 1-1. Main roof, NE...",        │
│    "system": "Roof",                                │
│    "component": "Membrane",                         │
│    "location": "Main Roof - NE Section",            │
│    "condition": "Poor",                             │
│    "prose": "Modified bitumen roofing membrane...",  │
│    "recommendation": "Full roof replacement...",     │
│    "priority": "1-3 Years",                         │
│    "cost_low": 500000,                              │
│    "cost_high": 700000,                             │
│    "flags": []                                      │
│  }                                                  │
└────────────────┬───────────────────────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────┐
│              OUTPUT GENERATION                      │
│                                                     │
│  1. Write prose + caption back into each PPT slide  │
│  2. Generate command_center.xlsx:                    │
│     - One row per observation                       │
│     - Columns: #, System, Component, Location,      │
│       Condition, Recommendation, Priority, Cost     │
│  3. Generate funding_summary.xlsx:                  │
│     - Rows grouped by system                        │
│     - Columns by timeframe bucket                   │
│     - Totals per system and grand total             │
└────────────────────────────────────────────────────┘
```

---

## SPORT Format (Input)

Each observation slide contains a dictated note following this structure:

> **S**ystem. **P**osition. **O**bservation. **R**ecommendation. **T**imeframe.

### Examples

**Roofing:**
"Roofing. Main roof, northeast section. Modified bitumen showing alligatoring at seams, ponding near drain. Full replacement with tapered insulation. One to three years."

**Mechanical:**
"Mechanical. Boiler room, basement level. Cast iron sectional boiler showing corrosion at base sections, flame impingement damage on fire side. Boiler replacement with high-efficiency condensing unit. Three to five years."

**Electrical:**
"Electrical. Main electrical room, basement. Original 1960s switchgear, bus bar connections showing heat discoloration. Full switchgear replacement. One to three years."

**Building Interiors:**
"Interiors. Stair A, first floor. Polyethylene zip wall in place at stair entrance for dust mitigation during ongoing renovation. Monitor and remove upon project completion. Immediate."

The AI must handle:
- Notes that don't perfectly follow SPORT order
- Missing fields (flag them, don't hallucinate)
- Dictation artifacts (minor transcription errors, filler words)
- Abbreviated system names ("Mech" for Mechanical, "Elec" for Electrical)

---

## RAND Report Voice (Style Guide)

The AI-generated prose must match RAND's engineering report style. Key characteristics:

- **Third person, passive voice preferred.** "The roofing membrane was observed to exhibit..." not "We saw the roof..."
- **Code references inline.** "Per NYC Building Code Section 1504..." or "In accordance with Local Law 11/FISP requirements..."
- **Condition-recommendation-cost structure.** Each paragraph describes what was observed, what should be done, and what it will cost.
- **Budget projection language.** "An allowance of $X is recommended for..." or "A current recommendation of $X is provided for..."
- **Timeframe categories.** Current Recommendation, Future Allowance (1-3 Years), Future Allowance (3-5 Years), Future Allowance (7-10 Years).
- **Questionnaire integration.** When survey data exists: "X% of respondents reported [condition]. Representative comment: '[italicized quote].'"
- **No hedging or uncertainty markers.** No "it appears" or "it seems." Direct observations stated as facts.
- **Technical specificity.** Name the material, the failure mode, the code section. Not "the roof looks bad" but "the modified bitumen membrane exhibits alligatoring at seams consistent with UV degradation beyond serviceable life."

**The example files include excerpts from a real RAND report. These are the ground truth for voice matching. The AI prompt should include 2-3 of these excerpts as few-shot examples for every observation it processes.**

---

## Building Systems (RAND Standard Categories)

The prototype should recognize and categorize observations into these 15 systems:

| # | System | Common Components |
|---|--------|-------------------|
| 1 | Roof | Membrane, flashing, drains, bulkhead waterproofing, parapets |
| 2 | Exterior Walls / Facade | Brick, lintels, sills, caulking, fire escapes, pointing |
| 3 | Windows | Frames, glazing, hardware, weatherstripping |
| 4 | Entrance / Doors | Entry doors, vestibule, canopy, lobby finishes |
| 5 | Building Interiors | Hallways, stairwells, flooring, wall finishes, handrails |
| 6 | Mechanical / HVAC | Boilers, burners, distribution piping, controls, breeching |
| 7 | Electrical | Switchgear, panels, feeders, common-area lighting |
| 8 | Plumbing | Risers, branch lines, water main, domestic hot water |
| 9 | Fire Protection | Standpipe, sprinkler, fire alarm, smoke detectors |
| 10 | Elevators / Vertical Transportation | Cab, controller, machine, rails, pit equipment |
| 11 | Site / Exterior | Sidewalk, areaway, retaining walls, parking, landscaping |
| 12 | Compliance | LL11/FISP, LL97, LL126, LL88/09, LL152 items |
| 13 | Laundry | Machines, venting, drainage, room finishes |
| 14 | Low Voltage | Intercom, security cameras, access control, fire alarm panels |
| 15 | Refuse | Compactors, chute, recycling, storage room |

---

## Output: Command Center (Excel)

One row per observation. Columns:

| Column | Source | Example |
|--------|--------|---------|
| Obs # | Sequential within system (e.g., 1-1, 1-2 for Roof) | 1-1 |
| System | From section divider or SPORT note | Roof |
| Component | AI-extracted | Membrane |
| Location | AI-extracted from SPORT Position field | Main Roof - NE Section |
| Condition | AI-assigned (Good / Fair / Poor / Critical) | Poor |
| Observation Summary | AI-generated one-liner | Alligatoring at seams with ponding |
| Recommendation | AI-extracted from SPORT | Full replacement with tapered insulation |
| Priority | AI-mapped timeframe | 1-3 Years |
| Cost Low | AI-estimated or placeholder | $500,000 |
| Cost High | AI-estimated or placeholder | $700,000 |
| Photo Ref | Auto-generated | Photo 1-1 |

---

## Output: Funding Summary (Excel)

Aggregated view for capital planning:

| System | Current Recommendation | 1-3 Years | 3-5 Years | 7-10 Years | Total |
|--------|----------------------|-----------|-----------|------------|-------|
| Roof | $0 | $615,000 | $0 | $0 | $615,000 |
| Electrical | $0 | $425,000 | $0 | $0 | $425,000 |
| ... | ... | ... | ... | ... | ... |
| **Grand Total** | | | | | **$X,XXX,XXX** |

---

## Mock Data Requirements

Since real PCS reports may not be available yet, the prototype needs mock data to test against.

### Mock Data Generator

Build a script (`generate_mock_data.py`) that creates a test PowerPoint file:

1. **Building profile:** A fictional 12-story, 80-unit co-op in Manhattan. Built 1962. Common systems in varying condition.

2. **15-25 observations** spread across at least 8 of the 15 system categories. Mix of:
   - Critical items (immediate action needed)
   - Near-term items (1-3 years)
   - Long-term items (3-5+ years)
   - At least one item per condition rating (Good, Fair, Poor, Critical)

3. **Stock photos.** Use freely licensed building/infrastructure photos. The AI vision component will describe what it sees, even if the photos don't perfectly match the SPORT notes. That's fine for testing the pipeline. Each observation slide gets a photo.

4. **SPORT notes.** Written to vary in quality:
   - Some perfectly structured ("Roofing. Main roof NE. Alligatoring at seams...")
   - Some abbreviated ("Roof. NE corner. Membrane failing. Replace. 1-3 yrs")
   - Some slightly messy (as if dictated: "This is the um mechanical room, basement level, the boiler has corrosion at the base...")
   - One or two missing a field (no timeframe, or no recommendation) to test the flagging system

5. **Section dividers.** Bold system name slides between observation groups.

### PowerPoint Structure

```
Slide 1:  Cover (Building name, address, date, prepared by)
Slide 2:  Command Center placeholder (empty table)
Slide 3:  Section divider — "1. ROOF"
Slide 4:  Observation (photo + SPORT note)
Slide 5:  Observation (photo + SPORT note)
Slide 6:  Section divider — "2. EXTERIOR WALLS"
Slide 7:  Observation (photo + SPORT note)
...
Slide N:  Section divider — "15. REFUSE"
Slide N+1: Observation (photo + SPORT note)
```

---

## Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11+ | Standard for AI pipelines, rich library ecosystem |
| PowerPoint parsing | `python-pptx` | Read/write .pptx files programmatically |
| Excel generation | `openpyxl` | Write .xlsx with formatting |
| AI model (primary) | Claude API (claude-sonnet-4-20250514 or claude-opus-4-20250514) | Best vision + structured output for prototype quality |
| AI model (fallback) | OpenAI GPT-4o | Alternative if Claude rate-limited |
| Image handling | `Pillow` | Resize/compress photos before API calls |
| Config | `.env` file | API keys, model selection, output paths |
| CLI | `argparse` or `click` | Simple command-line interface |

### Project Structure

```
rand-report-pipeline/
├── README.md
├── requirements.txt
├── .env.example
├── src/
│   ├── __init__.py
│   ├── parser.py          # PowerPoint parsing logic
│   ├── processor.py       # AI processing per observation
│   ├── prompts.py         # Prompt templates and style guide
│   ├── excel_writer.py    # Command center + funding summary
│   ├── pptx_writer.py     # Write results back to PowerPoint
│   └── models.py          # Data classes for Observation, Report, etc.
├── mock/
│   ├── generate_mock_data.py
│   ├── photos/            # Stock building photos for testing
│   └── output/            # Generated test PowerPoint files
├── style_guide/
│   ├── rand_examples.md   # RAND prose examples (few-shot)
│   └── system_categories.json
├── tests/
│   └── test_parser.py
└── run.py                 # Main entry point
```

### Entry Point

```bash
# Generate mock data
python mock/generate_mock_data.py

# Process a populated PowerPoint
python run.py --input mock/output/test_survey.pptx --output results/

# Output:
#   results/test_survey_processed.pptx   (prose + captions written back)
#   results/command_center.xlsx          (observation table)
#   results/funding_summary.xlsx         (cost summary by system)
```

---

## AI Prompt Architecture

### Per-Observation Prompt

Each observation slide gets one multimodal API call. The prompt includes:

1. **System prompt:** Role as a RAND Engineering report writer. Instructions for structured JSON output. Voice rules from the style guide section above.

2. **Few-shot examples:** 2-3 complete input/output pairs showing:
   - A SPORT note + what the finished prose paragraph looks like
   - A photo + what the caption looks like
   - The structured JSON output format

3. **The observation:** The photo (as image) + the SPORT note text + the system category from the section divider.

4. **Output schema:** Enforce JSON output matching the schema in the Architecture section above. Use Claude's tool_use or GPT's function_calling to guarantee structure.

### Prompt Template (Pseudocode)

```
SYSTEM:
You are a report writer for RAND Engineering & Architecture, DPC.
You transform field observations into formal Physical Condition Survey
report content. Your output must match RAND's established voice exactly.

Rules:
- Third person, passive voice
- Include relevant NYC building code references
- Use RAND's cost projection language
- Never hedge (no "appears to" or "seems to")
- Flag missing SPORT fields in the "flags" array
- If the photo doesn't match the note, flag it

OUTPUT FORMAT:
Return a JSON object with these fields: [schema]

EXAMPLES:
[2-3 few-shot examples from style_guide/rand_examples.md]

USER:
System Category: {section_name}
Observation #{obs_number}
SPORT Note: {extracted_text}
[attached: photo image]

Generate the report content for this observation.
```

---

## Completeness Checks

The pipeline flags these issues per observation:

| Flag | Trigger | Severity |
|------|---------|----------|
| `missing_photo` | Slide has text but no image | Error |
| `missing_note` | Slide has photo but no text | Error |
| `missing_system` | SPORT note doesn't specify a system | Warning |
| `missing_recommendation` | No recommendation in SPORT note | Warning |
| `missing_timeframe` | No timeframe specified | Warning |
| `system_mismatch` | SPORT system doesn't match section divider | Warning |
| `photo_text_mismatch` | Photo content doesn't align with note | Info |
| `vague_observation` | Observation too generic to expand | Warning |

Flags are:
- Included in the JSON output per observation
- Collected into a `flags_report.txt` summary file
- Printed to console during processing

---

## Success Criteria (Prototype)

| Criterion | Target |
|-----------|--------|
| Processes a 20-observation mock survey end to end | Pass/fail |
| Prose reads like RAND's voice (human review) | Qualitative |
| Command center Excel has correct data for all observations | 100% |
| Funding summary totals match command center | 100% |
| Flags correctly identify missing/incomplete observations | 90%+ |
| Processing time for 20 observations | Under 5 minutes |
| Written back to PowerPoint without corrupting the file | Pass/fail |

---

## Known Limitations (Prototype)

1. **Cost estimates are rough.** Without RAND's internal cost tables, the AI will estimate from general knowledge. Expect directionally correct but not precise numbers. This is clearly marked as placeholder data.

2. **Photo-note alignment is trust-based.** If a stock photo shows a roof but the SPORT note says "Electrical," the AI will flag the mismatch but process both. Real data won't have this problem.

3. **No questionnaire integration.** The prototype doesn't handle resident survey data. That's a later feature when real questionnaire responses are available.

4. **No hyperlinks in the command center.** The Excel doesn't link back to specific PowerPoint slides. That's a v2 feature.

5. **Single-file processing.** One PowerPoint in, outputs out. No batch processing, no queue, no web interface.

---

## Example Files to Attach

When feeding this PRD to another AI to build the prototype, attach these files from the RAND Engineering folder. Each file's purpose is noted so the AI knows what to use it for.

### Required

| # | File | Purpose |
|---|------|---------|
| 1 | **This PRD** (`RAND — PRD Prototype.md`) | The build specification. The AI reads this to know what to build. |
| 2 | **`RAND — Building Condition Survey Process.md`** | Domain knowledge. Explains the full PCS workflow, resident questionnaires, capital plan structure, and NYC compliance context (LL11, LL97, LL126). The AI needs this to generate realistic mock data and understand what a PCS report contains. |
| 3 | **`RAND — AI Integration Strategy.md`** | Contains the SPORT format definition, the three automated transformations, the data privacy tiers, hardware specs, and the pilot plan. Sections 1-2 are essential for understanding the input/output contract. |

### Recommended (for better output quality)

| # | File | Purpose |
|---|------|---------|
| 4 | **`RAND — PRD AI Report Pipeline.md`** | The full product vision (not just prototype). Gives context for what the prototype is building toward: the document lifecycle, mobile field design, command center generation, and partner review workflow. Helps the AI make design decisions that align with the eventual product. |
| 5 | **`RAND — Meeting 1 Notes (2026-02-17).md`** | Eugene's actual words about the workflow, the "ludicrous degree" front-loading philosophy, the PowerPoint Mobile decision, and the vortex model. Gives the AI context for why decisions were made. |
| 6 | **`RAND — First Recommendations.md`** | The original pitch document. Contains the "one slide = one observation = one database row" framing and the initial SPORT examples. |

### If Available (attach if you have them)

| # | File | Purpose |
|---|------|---------|
| 7 | **A sample RAND PCS report** (redacted PDF or Word doc) | Ground truth for output voice and format. The AI uses this to write few-shot examples in `style_guide/rand_examples.md`. Without this, the AI generates prose from the style guide description above, which is good but not as precisely matched. |
| 8 | **Eugene's PowerPoint photo-supplement template** | If Eugene has shared the PPT template he's building, attach it so the parser knows the exact slide layout (photo placeholder size/position, text box position, section divider format). Without this, the prototype uses a reasonable default layout. |
| 9 | **Eugene's Excel control board template** | If available, attach so the Excel writer matches RAND's exact column structure and formatting. Without this, the prototype uses the column structure defined in this PRD. |

### Note on Real PCS Data

We may not have real PCS reports or field photos ready for the prototype. That's expected. The mock data generator creates synthetic observations and uses stock photos. The pipeline is designed so that swapping in real data later requires zero code changes: just replace the input PowerPoint.

If RAND does provide a redacted sample report before the prototype is built, it goes into `style_guide/` as few-shot reference material. The pipeline improves with better examples but works without them.

---

## Build Sequence

For the AI building this prototype, here's the recommended order:

1. **`src/models.py`** — Data classes first. `Observation`, `ProcessedObservation`, `Report`, `Flag`.
2. **`style_guide/system_categories.json`** — The 15 system categories with aliases and common components.
3. **`src/prompts.py`** — Prompt templates. Hardest to get right, benefits from iteration.
4. **`src/parser.py`** — PowerPoint parsing. Extract slides, photos, text, section assignments.
5. **`mock/generate_mock_data.py`** — Create test data. Needed before you can test anything.
6. **`src/processor.py`** — AI processing loop. Calls the model for each observation.
7. **`src/pptx_writer.py`** — Write results back into the PowerPoint.
8. **`src/excel_writer.py`** — Generate both Excel outputs.
9. **`run.py`** — Wire it all together.
10. **`tests/test_parser.py`** — Validate parsing logic against mock data.

---

*This prototype proves the core value proposition: structured field observations in, formatted report content out. Everything else (local models, partner review, field AI, questionnaire integration) layers on top of this foundation.*
