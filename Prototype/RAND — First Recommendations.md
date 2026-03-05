# RAND Building Advisory Group — Initial Recommendations

*Prepared by Gali Davidi for Eugene Gurevich, PE, AIA*
*Following our meeting on February 17, 2026*

---

## The Insight That Makes Two Weeks Possible

Your pilot structure (Day 1 document review, Day 2 site work, Day 3 team meeting, Weeks 1-2 assembly and QA) compresses the calendar. That's necessary but not sufficient. The real compression comes from eliminating an entire category of work: re-structuring information that was already structured in your engineer's head the moment they looked at the building.

A PCS finding has a fixed anatomy: system, location, condition, recommendation, timeframe, estimated cost. Your engineers know all six the second they see a condition. That structured knowledge gets flattened into free-form dictation, then someone spends hours extracting structure from narrative to build the Excel control board and organize the report. That reconstruction step is where the hundreds of hours hide.

Your instinct to front-load into finished documents is the right one. The refinement: front-load *structured observations*, not just dictation. Three things happen at once when field data comes in structured:

1. The Excel control board populates itself (structured data maps directly to rows)
2. Report sections generate themselves (AI expands structured observations into RAND's prose style)
3. The Day 3 partner meeting works from a populated dashboard instead of a stack of photos

That third point changes the meeting itself. Partners aren't organizing; they're reviewing. They see every finding, sorted by system, with cost projections already attached. Their job becomes approval and prioritization, not assembly.

---

## One Slide = One Observation = One Database Row

Your one-photo-per-slide format is smarter than it looks at first. Each slide is a natural unit of work. The entire PCS becomes a data set that renders into different views (the photo supplement, the narrative report, the Excel dashboard) when every slide follows a consistent structure. Same source, multiple outputs.

Each slide's dictation should hit five fields. SPORT makes them easy to remember:

> **S**ystem. **P**osition. **O**bservation. **R**ecommendation. **T**imeframe.

Example: *"Roofing. Main roof, northeast section. Modified bitumen showing alligatoring at seams, ponding near drain. Thermographic evaluation followed by full replacement. 1 to 3 years."*

A good AI model can parse free-form dictation and figure out what your engineer meant. The structure solves a different problem: completeness. Engineers dictating off the cuff occasionally skip a field (no timeframe, no system label, no clear recommendation). A consistent pattern means nothing gets left out. At 200+ observations per survey, that compounds.

Photo naming follows the same logic: `01-roof-main-NE-001.jpg`. System code, location, sequence. Photos auto-sort into report sections and match to control board categories without manual tagging.

---

## What AI Does (and Doesn't Do)

AI doesn't replace engineering judgment. Your engineers make the assessment. AI handles the three transformations that eat associate-level hours:

**Field observation to report prose.** The engineer dictates "Roofing. Main roof NE. Alligatoring at seams, ponding near drain. Full replacement. 1-3 years." AI expands that into a full paragraph in RAND's voice, with code references, condition context, and budget projection language. The engineer reviews a draft, not a blank page.

**Photo to titled, categorized slide.** AI reads each photo, generates a descriptive title ("Main Roof Level: Ponding Water Near Northeast Drain"), confirms the system category, and suggests a condition rating. The engineer confirms or corrects. 100+ photos get titled in minutes, not hours.

**Observations to dashboard.** Every structured observation feeds directly into the Excel control board: system, component, condition, action, cost range, timeline. The dashboard builds itself from field data. No one manually transfers items from the report into Excel.

The critical design principle: AI processes information through functions you define, using your templates and your standards. It doesn't freestyle or make engineering calls. It transforms structured input into formatted output. The engineering judgment stays with your team.

---

## Keeping Data on Your Network

Three classes of data run through this pipeline: generic content with no building identity (code references, boilerplate, condition descriptions), content that becomes safe once scrubbed (photos without visible addresses, anonymized notes), and content that must never leave RAND's network (building address paired with condition data, owner names, financial projections, violation records tied to properties). In theory, you send the first two classes to cloud AI and keep the third local. In practice, someone has to review every photo and every dictation clip to decide which class it falls in. A wide-angle shot might capture a street sign in the corner. A dictation might mention a building name offhand. Miss one, and client-identifiable data hits a cloud API. That sorting burden eats into the time savings, and the cost of a single miss is real.

The simpler path: treat everything as local. No sorting, no scrubbing pipeline, no risk of accidental leakage. A dedicated AI workstation ($3-5K range) sits on RAND's network and handles the full pipeline: dictation to prose, photo titling, Excel population. Fits a Windows environment like any other PC. For structured engineering language following known templates, local output quality is comparable to cloud.

The one area where cloud models pull ahead is vision: catching subtle structural conditions the engineer might miss (a "second set of eyes" on building photos). RAND expressed interest in that capability. All-local means simpler operations and zero privacy risk, but limited structural second-opinion compared to cloud. A controlled cloud pathway for non-identifying photos (close-ups of cracks, generic rooftop surfaces, interior mechanical rooms) would deliver better vision quality for that feature, but requires someone to confirm each photo carries no identifying content before sending. That's a narrower sorting problem than reviewing everything, but it's still a manual step. Your call on whether that trade-off is worth it for the pilot.

Starting all-local doesn't close the cloud door. Local models improve fast. If the vision quality gap matters after you've used the system, you can add a controlled cloud pathway later. Easier to start closed and open up than to walk back a cloud dependency.

---

## What I Need to Build the Prototype

1. **Signed NDA** (both sides) so we can work with real project data
2. **A completed PCS report** (any past project, redacted if needed) to study the output format, section structure, and prose style your clients expect
3. **The PowerPoint photo-supplement template** you're building
4. **The Excel control board template** you're building
5. **A sample resident questionnaire** (the standard template RAND sends to buildings pre-visit)
6. **One past set of raw field notes and photos** from a real survey (to prototype the AI processing pipeline against actual input)

With these, I build a working pipeline against real RAND data. The next conversation is a demo, not a deck.

---

*Gali Davidi*
*gali@galileo.tools*
