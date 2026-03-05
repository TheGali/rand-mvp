# Building Condition Survey / Capital Reserve Study Process

Internal reference for understanding the Physical Condition Survey (PCS) and Capital Reserve Study (CRS) workflow at NYC engineering firms, with RAND Engineering as the primary context.

---

## 1. Industry-Standard PCS Workflow

### Pre-Visit

- Board and managing agent provide existing documentation: architectural drawings, offering plan, prior survey reports, DOB violation history, recent capital improvement records.
- The engineer reviews known problem areas and repair history with the board before the visit.
- A resident questionnaire is distributed to all shareholders/unit owners (typically by the managing agent) to surface conditions inside individual apartments that the engineer cannot observe during common-area walkthroughs.

### Site Visit

- Roof-to-cellar walkthrough covering all major building systems: roof and bulkhead, facades, windows, entrance doors, terraces/balconies, hallways, stairwells, elevators, heating/HVAC, plumbing/drainage, electrical, fire protection, intercom/security, laundry, parking, and site exterior.
- Larger buildings (7+ stories, 40+ units, multiple elevators) require a team with multiple specialties: exterior/waterproofing, mechanical/HVAC, electrical, plumbing, structural. Smaller buildings can be handled by a single engineer.
- Engineers take photos and field notes throughout. They may ride scaffolding to inspect facades up close, conduct investigative probes on exterior walls, or use moisture meters on interior walls.
- Discussions with the building superintendent, resident contacts, and any active contractors on site.
- Representative apartment visits (typically 6-8 units, roughly 5-10% of total units). These are selected based on questionnaire responses, focusing on apartments that reported symptoms of potential systemic issues (leaks, cracks, pressure problems).

### Post-Visit

- Field notes and photos are organized and mapped to building systems.
- Draft report is assembled: narrative descriptions of each system's condition, captioned photographs, and a prioritized list of recommended repair and replacement items with associated budget projections and timetables.
- Partner-level review. Comments and revisions cycle back to the writing engineer.
- QA pass for consistency, accuracy of cost estimates, and compliance references.
- Final delivery to the board and managing agent (PDF report plus Excel capital plan).

---

## 2. Where the 3-4 Month Timeline Breaks Down

The site visit itself takes 1-2 days. The remaining 10-14 weeks are consumed by report production. Common bottlenecks:

- **Field notes to draft:** Engineers write narrative descriptions for each building system based on handwritten or typed field notes. This is manual, slow, and varies by writer. A single report can include 15-20 system sections, each with condition descriptions, photo references, and recommendations.
- **Photo organization:** Hundreds of photos per site visit need to be sorted, labeled, matched to specific conditions, and inserted into the report. This step alone can take days.
- **Partner review cycles:** Senior partners review every report before delivery. They juggle reviews across 10-20 active projects. A report can sit in the review queue for 1-3 weeks. Comments require revisions, which re-enter the queue.
- **Context switching:** Engineers carry 5-10 projects at different stages simultaneously. Returning to a half-written report after weeks on other sites means re-reading field notes and photos to regain context.
- **Cost estimate updates:** Budget projections need current pricing. Engineers reference internal databases and vendor quotes that may require follow-up.
- **Client follow-up:** Missing documents, unanswered questionnaires, or access issues cause delays that push the project back.

---

## 3. Resident Questionnaire

### Format

The questionnaire is a 1-2 page form (paper or digital) distributed to all units. It covers:

- **Windows:** Condition, air/water infiltration, operability, condensation.
- **Plumbing:** Water pressure, discolored water, drain speed, fixture condition.
- **Heating/cooling:** Temperature adequacy, radiator/unit condition, thermostat function.
- **Leaks/moisture:** Ceiling stains, wall stains, bathroom/kitchen leaks, mold.
- **Walls/floors/ceilings:** Cracks, shifting, bulging, sagging, peeling paint.
- **Electrical:** Non-functional outlets/switches, flickering lights, tripped breakers.
- **General:** Pest issues, odors, noise complaints, elevator reliability.

Most questions are multiple choice or yes/no. Some include free-text fields for elaboration.

### How Responses Feed Into Findings

- Responses are tallied and quantified (e.g., "72% of respondents reported window air infiltration," "34% reported low water pressure above the 10th floor").
- Patterns flag systemic issues. Clustered leak complaints on one facade exposure indicate waterproofing failure. Widespread pressure complaints above a certain floor indicate riser or pump issues.
- Quantified results appear in the corresponding system section of the report, lending statistical weight to the engineer's visual observations.
- Questionnaire data also guides apartment selection for the representative unit visits.

---

## 4. Capital Plan / Reserve Study Structure

The capital plan is delivered as an Excel workbook (or appendix table) with the following structure:

### Component Inventory

Each row represents a major building component or sub-component, organized by system:

| System Category | Example Components |
|---|---|
| Roof | Membrane, flashing, drains, bulkhead waterproofing |
| Facade | Brick repointing, lintels, sills, caulking, fire escapes |
| Windows | Window replacement or restoration, by exposure |
| Entrance/Lobby | Doors, vestibule, canopy, lobby finishes |
| Hallways/Stairs | Floor finishes, wall finishes, stair treads, handrails |
| Elevators | Cab renovation, controller modernization, machine replacement |
| Heating/HVAC | Boiler, burner, breeching, distribution piping, controls |
| Plumbing | Risers, branch lines, water main, domestic hot water |
| Electrical | Switchgear, panels, feeders, common-area lighting |
| Fire Protection | Standpipe, sprinkler, fire alarm, smoke detectors |
| Site/Exterior | Sidewalk, areaway, retaining walls, parking, landscaping |

### Columns per Component

- **Description:** What the component is and where it is located.
- **Observed Condition:** Rating (Good / Fair / Poor) or descriptive assessment.
- **Estimated Useful Life:** Standard expected lifespan for the component.
- **Adjusted Remaining Useful Life:** Years remaining based on observed condition and age.
- **Current Recommendation:** Work needed now or within 1-2 years, with estimated cost.
- **Future Allowance:** Projected costs broken into timeframes (e.g., Years 3-5, 6-10, 11-15, 16-20).

### Summary of Anticipated Funding Requirements

A summary appendix aggregates all component costs into a single table showing total capital needs by timeframe. This is the document boards use for financial planning, assessment decisions, and loan applications. Fannie Mae and Freddie Mac lending guidelines require either a 10% reserve line item in the operating budget or a reserve study with a corresponding prescribed reserve contribution.

---

## 5. NYC Compliance Context

These local laws create both demand for PCS/CRS work and specific compliance sections within the reports.

### Local Law 11 / FISP (Facade Inspection Safety Program)

- All buildings taller than 6 stories must have facades inspected every 5 years by a Qualified Exterior Wall Inspector (QEWI).
- Each inspection cycle is divided into three sub-cycles based on the last digit of the building's tax block number (e.g., Cycle 10A: blocks ending in 4, 5, 6, 9; Cycle 10B: blocks ending in 0, 7, 8; Cycle 10C: blocks ending in 1, 2, 3).
- Facades are classified as Safe, Safe With a Repair and Maintenance Program (SWARMP), or Unsafe.
- Unsafe conditions require immediate protective measures (sidewalk shed, netting) and corrective work.
- **Late fees:** $1,000/month for late initial report filing. $5,000/year failure-to-file penalty on top of that. These increased significantly in Cycle 9 (previously $250/month and $1,000/year).

### Local Law 97 (Climate Mobilization Act, 2019)

- Sets greenhouse gas emissions limits for buildings over 25,000 square feet.
- First compliance period: 2024-2029. Stricter limits begin 2030.
- Emissions are calculated per square foot using carbon coefficients for each fuel type.
- Penalties: $268 per metric ton of CO2e over the cap, assessed annually.
- Goal: 40% emissions reduction by 2030, net zero by 2050.
- PCS reports increasingly include energy system assessments and LL97 exposure analysis.

### Local Law 126 (Gas Piping Inspections)

- All buildings (except 1-2 family homes) must have gas piping inspected by a Licensed Master Plumber every 4 years.
- Applies to all gas piping from the point of entry to individual appliance connections.

### Local Law 126 (Parapet Wall Inspections, effective January 2024)

- All buildings with parapets facing a public right-of-way must have annual parapet inspections by December 31 of each year.
- The inspection checks for misalignment, cracks (horizontal and diagonal), missing or loose bricks/coping stones, and mortar deterioration.
- Observation reports must be kept on file for at least 6 years.

### Local Laws 92/94 (Sustainable Roof Requirements)

- Buildings undergoing major roof renovations or new construction must install solar panels, green roofs, or a combination covering 100% of the sustainable roofing zone.
- Exceptions for fire code setbacks, access requirements, and roofs with slopes greater than 17%.
- Effective November 2019 as part of the Climate Mobilization Act.
- (Often referenced informally as "Local Law 37" requirements, though LL92/94 are the operative laws.)

### DOB Violations and Permit Tracking

- Active DOB violations and open permits are reviewed during the pre-visit phase.
- The PCS report flags unresolved violations and recommends corrective action.
- Boards use the report to prioritize violation resolution alongside capital work.

---

## Key Takeaway for AI Optimization

The highest-value automation targets in this workflow are: (1) field notes to draft narrative generation, (2) photo sorting, labeling, and matching to conditions, (3) questionnaire response aggregation and statistical summary, (4) capital plan cost table population from templates and historical data, and (5) compliance deadline tracking across multiple local laws. The partner review bottleneck is a process issue, not a content issue, but faster draft production shortens the overall cycle by reducing the number of items in the review queue at any given time.
