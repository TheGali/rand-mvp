# RAND Engineering — Meeting 1 Notes

**Date:** 2026-02-17, 1:00 PM
**Attendees:** Gali Davidi + Eugene Gurevich, PE, AIA (RAND partner, Building Advisory Group director)
**Format:** Video call, ~40 min. Eugene screen-shared an Apple Freeform diagram of the pilot workflow.

---

## Strategic Context

Eugene directs RAND's new Building Advisory Group, which he publicly declared to his partners as the "first AI-supported team" at the firm.

**The "vortex" model.** RAND's engineering teams (structural, MEP, facade/roofing, architecture, BDG) currently operate in silos. Eugene's advisory group sits at the center, pulling all disciplines into a unified building-level perspective. Junior engineers rotate through the advisory team to develop full-building intuition.

**Account-based, not project-based.** Eugene's vision: 20-year capital plans per building, updated live, instead of competing for one-off projects. This creates a long-term advisory relationship with each building.

**Developer conflict strategy.** Sponsors hire RAND preemptively so the buyer's side can't retain them. Defensive positioning that locks in the relationship early.

**Long-term vision.** Live-updating building health dashboards, eventually 24/7 monitoring.

---

## Flagship Product: Physical Condition Survey (PCS)

The PCS is a "roof to cellar" survey covering roof, exterior walls, interiors, site, mechanical, electrical, plumbing, fire suppression, vertical transportation, refuse, laundry, and low-voltage systems. RAND currently delivers these as 200-300 page Word documents. Timeline: 3-4 months.

**Core bottleneck.** Not enough gets captured during fieldwork. Engineers take photos, go home, then write up observations from memory. Context switching (pick up, put down the project) balloons hours into the hundreds.

**Eugene's philosophy: front-load to a "ludicrous degree."** Work inside finished documents from the start. Eliminate the Word document entirely.

---

## New Deliverable Format

Eugene has redesigned how the PCS gets built:

- **PowerPoint photo supplement.** One photo per slide. Caption + report section text below each photo. This replaces the traditional Word doc.
- **PowerPoint Mobile as the field tool.** Engineers dictate captions and report text directly from their phone while on site, under each photo. Eugene calls this "a revelation." One photo per slide means easy rearranging, no layout headaches on mobile.
- **Excel control board.** All building systems listed on the left, items broken down, mapped to a year-by-year timeline (10-20 year capital plan). Includes cost projections by system.

Gali suggested a custom RAND app; Eugene pushed back. PowerPoint Mobile is the capture tool. No new software.

---

## Pilot Workflow (from Freeform diagram)

Eugene drew this in Apple Freeform during the call:

- **Day 1:** Review available documents (drawings, offering plan, resident questionnaire)
- **Day 2:** Site work (roof to cellar, various units). Small team of 2-3 engineers. Photos + content capture directly in PowerPoint.
- **Day 3:** Project team meeting. Senior staff help prioritize, get report framework finalized.
- **Week 1:** Report assembly + review
- **Week 2:** QA layer + report issued

Target: compress the current 3-4 month cycle into this structure.

---

## Where AI Fits

ChatGPT usage planned at the report-drafting stage (visible on Freeform diagram):

1. **Dictated field notes to report prose.** Engineers dictate observations on site ("This is an inverted roof. Probably needs replacement in five years."). AI expands shorthand into RAND's formal report language.
2. **Photo titles and descriptions.** AI describes what's in each photo, suggests system category and condition rating.

Gali's contribution: explained deterministic vs. non-deterministic AI use. Build deterministic processing functions (structured inputs, predictable outputs), don't let AI freestyle the final product.

Gali flagged that Eugene's 20 years of experience lets him "see the matrix" when looking at building conditions, but junior staff won't have that intuition. The AI processing layer needs to be structured enough for juniors to use reliably.

---

## Privacy and Data Handling

**Concerns raised by RAND:**
- Proprietary information
- PII (resident names, unit numbers)
- Financial projections tied to specific buildings
- Individual names

**RAND is on Microsoft 365.** Open to purchasing dedicated hardware (Mac Mini or PC with GPU) for running a local model on sensitive data.

---

## Tool Discussion

Eugene is committed to PowerPoint Mobile as the capture interface. Gali sees a processing-layer opportunity (backend that takes the PowerPoint output and structures it) but deferred. No new tools pitched in this meeting.

---

## Pre-existing Assets

- RAND has a standard resident questionnaire template (sent to buildings before the site visit)
- PowerPoint photo-supplement template (Eugene is building this)
- Excel control board template (Eugene is building this)

---

## Action Items

| Owner | Item |
|-------|------|
| Gali | Email signed NDA to Eugene |
| Eugene | Email Gali the PowerPoint photo-supplement template |
| Eugene | Email Gali the Excel control board template |
| Gali | Send recommendations brief |

---

## Source Notes

Combined from two sources:
- **Fathom transcript:** ~38 of 40 minutes captured. Some sections garbled; screen-shared Freeform content not captured in text. Covers the Building Advisory Group vision, PCS workflow, front-loading philosophy, PowerPoint/Excel format, pilot timeline, and deterministic AI discussion.
- **Brain dump / Freeform diagram:** Fills in privacy concerns, M365 detail, local model conversation, ChatGPT usage stages, team size, pre-visit document flow, and the tail end of the call. Confirmed accurate by Gali.

The transcript captured roughly half the content of the call (much of the Freeform visual walkthrough was invisible to the transcriber).
