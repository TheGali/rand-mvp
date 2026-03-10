"""AI Chat Assistant — system prompt, tool schemas, and context builder.

Provides the building advisor chat feature for the dashboard.
Claude uses tool_use to return structured UI blocks (charts, tables, etc.)
alongside conversational text. The frontend renders these as rich components.
"""

import json
import os
from collections import defaultdict

import anthropic


CHAT_SYSTEM_PROMPT = """You are RAND AI, a senior building advisor built into RAND Engineering & Architecture's Physical Condition Survey (PCS) platform.

Your user is a co-op or condo board member — typically the board president, treasurer, or facilities chair. They are NOT engineers. They manage budgets, present to shareholders, and make decisions about when to spend money. They just received a professional Physical Condition Survey of their building and need help understanding it.

## How to Think

You have been given two things:
1. A PRE-COMPUTED EXECUTIVE SUMMARY with totals by system, by priority, and key metrics. Use these numbers directly — do not re-derive them from raw observations.
2. The RAW OBSERVATIONS for detail when the user asks about a specific system or item.

When the user asks a high-level question ("what's urgent?", "show me the capital plan"), lean on the executive summary. When they ask about a specific system or observation, dive into the raw data.

## Communication Style

- **Direct and decisive.** Board members want clarity, not hedging. Say "Your roof needs $X within 3 years" not "It appears the roof may potentially require..."
- **Lead with the answer, then explain.** State the conclusion first, then support it.
- **Frame everything in terms of money and time.** That's what boards care about.
- **Use round numbers.** Say "$870K" not "$867,400" in conversation. The exact figures are in the report.
- **Reference observation numbers** (e.g., "Obs 3-2") so they can cross-reference the full report.
- **Keep it concise.** 2-4 sentences of text per point. Don't write paragraphs when a bullet will do.

## Visualization Guidelines

Use tools to show data, but be smart about it:

### Capital Charts (show_capital_chart)
- **Categories MUST be top-level SYSTEMS: Roof, Exterior Walls, Elevators, HVAC, Plumbing, Electrical, etc.**
- **NEVER use individual components or observations as categories.** Wrong: "Roof Membrane Replacement", "Parapet Wall Repairs", "Sump Pump System". Right: "Roof" (combining all roof items into one number).
- Copy the aggregated system totals directly from the CHART DATA TABLE provided in the survey context. Do NOT disaggregate them into components.
- Use these time buckets (matching the Funding Summary): Curr. Rec., Yrs 1-3, Yrs 4-6, Yrs 7-9, Yrs 10-12, Yrs 13-15
- Max 6-8 system categories. Combine small systems into "Other".
- Example of CORRECT chart data:
  ```
  periods: [
    { label: "Curr. Rec.", categories: [{ name: "Electrical", amount: 12500 }] },
    { label: "Yrs 1-3", categories: [{ name: "Roof", amount: 629000 }, { name: "Facade", amount: 236000 }, ...] },
  ]
  ```
  Notice: "Roof" is ONE category with the total, not split into "Membrane", "Parapet", "Coping".

### Comparison Charts (show_comparison_chart) — USE FOR ALL "WHAT IF" SCENARIOS
- **Whenever you compare two scenarios (original vs revised, current plan vs deferred, etc.), you MUST use show_comparison_chart, NOT show_capital_chart.**
- Each time period gets side-by-side grouped bars — one per scenario. This is the only chart type that makes comparisons readable.
- Use the same time buckets as the Funding Summary: Curr. Rec., Yrs 1-3, Yrs 4-6, Yrs 7-9, Yrs 10-12, Yrs 13-15
- Each scenario has a name (e.g., "Original Plan", "Revised Plan") and a total for each period.
- Include only periods where at least one scenario has spending > 0.
- Example:
  ```
  scenarios: [
    { name: "Original Plan", values: [12500, 850000, 1015000, 230000, 0, 0] },
    { name: "Revised Plan",  values: [12500, 260000, 450000, 350000, 280000, 0] }
  ]
  ```

### Cost Summaries (show_cost_summary)
- Group by system or priority bucket — whichever is more relevant to the question.
- Always include percentages so the user can see relative weight.
- 4-8 categories max. Group small items.

### Observation Lists (show_observations)
- Only show 3-8 most relevant observations, not exhaustive lists. The full list is in the report already.
- Write a clear 1-sentence summary for each — don't just repeat the prose from the report.

### Action Items (show_action_items)
- Focus on 3-6 actionable next steps, not a dump of everything.
- Each item should be a specific action the board can take, not a description of a condition.
- Include cost and timeframe for every item.

## "What If" Scenarios

When the user asks about moving projects or changing timing:
1. Give a brief summary (3-5 bullet points MAX) of what can move, what can't, and key trade-offs.
2. Then IMMEDIATELY call show_comparison_chart to visualize Original vs Revised side-by-side.
3. After the chart, add 2-3 sentences on risks if relevant.
4. Do NOT write a long explanation and THEN try to show a chart — the chart IS the answer. Text is supporting context.
5. Don't moralize — present the trade-offs and let the board decide.

## Boundaries
- Use ONLY data from the survey. Do not invent observations, costs, or conditions.
- Do not provide legal advice.
- Do not contradict the engineer's assessments — you can explain them, but not override them.
- If asked about something not in the survey, say so clearly.
- When quoting costs, note they are engineer's estimates from the survey date."""


CHAT_TOOL_SCHEMAS = [
    {
        "name": "show_capital_chart",
        "description": "Display a stacked bar chart of capital expenditures. Categories MUST be top-level building SYSTEMS (e.g., 'Roof', 'Elevators', 'Plumbing') — NEVER individual observations or components. Pull system totals from the SYSTEM × PRIORITY MATRIX. Max 6-8 system categories; combine small ones into 'Other'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Chart title"},
                "periods": {
                    "type": "array",
                    "description": "Time periods on x-axis (use standard priority buckets)",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string", "description": "e.g. 'Curr. Rec.', 'Yrs 1-3', 'Yrs 4-6', 'Yrs 7-9', 'Yrs 10-12', 'Yrs 13-15'"},
                            "categories": {
                                "type": "array",
                                "description": "Building systems with costs. MUST be system-level (e.g. 'Roof', 'Plumbing'). Max 8.",
                                "maxItems": 8,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string", "description": "System name, e.g. 'Roof', 'Plumbing'"},
                                        "amount": {"type": "number", "description": "Total cost in USD for this system in this period"},
                                    },
                                    "required": ["name", "amount"],
                                },
                            },
                        },
                        "required": ["label", "categories"],
                    },
                },
            },
            "required": ["title", "periods"],
        },
    },
    {
        "name": "show_comparison_chart",
        "description": "Display a GROUPED bar chart comparing two scenarios side-by-side. REQUIRED for any 'what if' or before/after comparison. Each time period shows bars for each scenario next to each other (NOT stacked). Use standard Funding Summary periods: Curr. Rec., Yrs 1-3, Yrs 4-6, Yrs 7-9, Yrs 10-12, Yrs 13-15.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Chart title, e.g. 'Original vs Revised Capital Plan'"},
                "periods": {
                    "type": "array",
                    "description": "Time period labels on x-axis (use Funding Summary buckets)",
                    "items": {"type": "string"},
                },
                "scenarios": {
                    "type": "array",
                    "description": "Two or more scenarios to compare side-by-side",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Scenario label, e.g. 'Original Plan', 'Revised Plan'"},
                            "values": {
                                "type": "array",
                                "description": "Total spend per period (same order as periods array)",
                                "items": {"type": "number"},
                            },
                        },
                        "required": ["name", "values"],
                    },
                },
            },
            "required": ["title", "periods", "scenarios"],
        },
    },
    {
        "name": "show_cost_summary",
        "description": "Display a cost summary card with total and category breakdowns shown as progress bars. Use for system-level or priority-level cost overviews. 4-8 categories max.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "total": {"type": "number", "description": "Total cost in USD"},
                "categories": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "amount": {"type": "number"},
                            "percentage": {"type": "number", "description": "Percentage of total (0-100)"},
                        },
                        "required": ["name", "amount"],
                    },
                },
            },
            "required": ["title", "total", "categories"],
        },
    },
    {
        "name": "show_observations",
        "description": "Display a compact list of observation cards. Use to highlight 3-8 specific findings (e.g., the most urgent items, items in a specific system). Write a fresh 1-sentence summary — don't just copy the prose.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "observations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "obs_number": {"type": "string"},
                            "system": {"type": "string"},
                            "component": {"type": "string"},
                            "condition": {"type": "string"},
                            "priority": {"type": "string"},
                            "cost_high": {"type": "number"},
                            "summary": {"type": "string", "description": "Fresh 1-sentence plain-English summary of this finding"},
                        },
                        "required": ["obs_number", "summary"],
                    },
                },
            },
            "required": ["title", "observations"],
        },
    },
    {
        "name": "show_action_items",
        "description": "Display a prioritized checklist of 3-6 recommended next steps. Each item should be a specific ACTION the board can take (e.g., 'Get 3 bids for roof replacement'), not a description of a condition.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "description": "Specific action the board should take"},
                            "timeframe": {"type": "string", "description": "When to do it"},
                            "estimated_cost": {"type": "string", "description": "Formatted cost, e.g. '$450K'"},
                            "urgency": {"type": "string", "enum": ["critical", "high", "medium", "low"]},
                            "related_obs": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Related observation numbers",
                            },
                        },
                        "required": ["action", "timeframe"],
                    },
                },
            },
            "required": ["title", "items"],
        },
    },
]


# ── Priority bucket mapping (mirrors the funding summary logic) ──

def _priority_bucket(priority):
    """Map a priority string to a standard time bucket.

    Mirrors the Funding Summary tab's priorityToBucket() exactly.
    """
    p = (priority or "").lower().strip()
    if p in ("immediate", "year 1"):
        return "Curr. Rec."
    if p in ("year 1-2", "year 1-3", "year 2-3"):
        return "Yrs 1-3"
    if p in ("year 2-4", "year 3-5", "year 1-5", "year 4-5"):
        return "Yrs 4-6"
    if p in ("year 6-10", "year 5-10"):
        return "Yrs 7-9"
    if p in ("year 10+", "year 10-15"):
        return "Yrs 10-12"
    if p in ("capital planning",):
        return "Yrs 13-15"
    return "Other"


def build_chat_context(job_data):
    """Build a structured context with pre-computed aggregates.

    Returns a string containing:
    1. Building metadata
    2. Executive summary (totals by system, by priority)
    3. Key metrics (most expensive system, most urgent items, etc.)
    4. Raw observations (for detail questions)
    """
    building = job_data.get("building_name", "Unknown Building")
    address = job_data.get("address", "")
    obs_list = job_data.get("processed_observations", [])

    # ── Pre-compute aggregates ──

    # By system
    by_system = defaultdict(lambda: {"cost_high": 0, "cost_low": 0, "count": 0,
                                      "conditions": [], "priorities": []})
    # By priority bucket
    by_priority = defaultdict(lambda: {"cost_high": 0, "count": 0, "systems": set()})
    # Totals
    total_high = 0
    total_low = 0
    immediate_items = []
    worst_conditions = []  # Poor/Critical

    for obs in obs_list:
        system = obs.get("system", "Unknown")
        cost_h = obs.get("cost_high", 0) or 0
        cost_l = obs.get("cost_low", 0) or 0
        condition = obs.get("condition", "")
        priority = obs.get("priority", "")
        bucket = _priority_bucket(priority)

        by_system[system]["cost_high"] += cost_h
        by_system[system]["cost_low"] += cost_l
        by_system[system]["count"] += 1
        if condition:
            by_system[system]["conditions"].append(condition)
        if priority:
            by_system[system]["priorities"].append(priority)

        by_priority[bucket]["cost_high"] += cost_h
        by_priority[bucket]["count"] += 1
        by_priority[bucket]["systems"].add(system)

        total_high += cost_h
        total_low += cost_l

        if bucket == "Curr. Rec.":
            immediate_items.append(obs)
        if condition and condition.lower() in ("poor", "critical"):
            worst_conditions.append(obs)

    # ── Build context string ──

    lines = [
        "=" * 60,
        "BUILDING SURVEY DATA",
        "=" * 60,
        f"Building: {building}",
        f"Address: {address}",
        f"Total observations: {len(obs_list)}",
        f"Total estimated cost (high): ${total_high:,.0f}",
        f"Total estimated cost (low): ${total_low:,.0f}",
        "",
    ]

    # Executive summary: costs by system
    lines.append("── COST BY SYSTEM (sorted high to low) ──")
    sorted_systems = sorted(by_system.items(), key=lambda x: x[1]["cost_high"], reverse=True)
    for system, data in sorted_systems:
        pct = (data["cost_high"] / total_high * 100) if total_high > 0 else 0
        worst = "N/A"
        if data["conditions"]:
            cond_order = {"critical": 5, "poor": 4, "fair": 3, "good": 2, "satisfactory": 1}
            worst = max(data["conditions"], key=lambda c: cond_order.get(c.lower(), 0))
        lines.append(
            f"  {system}: ${data['cost_high']:,.0f} ({pct:.0f}%) — "
            f"{data['count']} observations, worst condition: {worst}"
        )
    lines.append("")

    # Executive summary: costs by priority bucket
    lines.append("── COST BY PRIORITY BUCKET ──")
    bucket_order = ["Curr. Rec.", "Yrs 1-3", "Yrs 4-6", "Yrs 7-9", "Yrs 10-12", "Yrs 13-15", "Other"]
    for bucket in bucket_order:
        if bucket in by_priority:
            data = by_priority[bucket]
            pct = (data["cost_high"] / total_high * 100) if total_high > 0 else 0
            systems_str = ", ".join(sorted(data["systems"]))
            lines.append(
                f"  {bucket}: ${data['cost_high']:,.0f} ({pct:.0f}%) — "
                f"{data['count']} items — Systems: {systems_str}"
            )
    lines.append("")

    # Immediate / critical items
    if immediate_items:
        lines.append(f"── IMMEDIATE ATTENTION ({len(immediate_items)} items) ──")
        for obs in immediate_items:
            lines.append(
                f"  [{obs.get('obs_number')}] {obs.get('system')} — {obs.get('component', '')} — "
                f"${obs.get('cost_high', 0):,.0f} — {obs.get('recommendation', '')[:120]}"
            )
        lines.append("")

    # Worst conditions
    if worst_conditions:
        lines.append(f"── POOR/CRITICAL CONDITION ({len(worst_conditions)} items) ──")
        for obs in worst_conditions:
            lines.append(
                f"  [{obs.get('obs_number')}] {obs.get('system')} — {obs.get('component', '')} — "
                f"Condition: {obs.get('condition')} — ${obs.get('cost_high', 0):,.0f}"
            )
        lines.append("")

    # Pre-aggregated chart data — JSON-like for easy tool use
    lines.append("── CHART-READY DATA (use directly for show_capital_chart categories) ──")
    lines.append("Each object below is one chart category. Copy these system names and amounts as-is.")
    lines.append("")

    # Build per-system-per-bucket lookup
    sys_bucket_costs = defaultdict(lambda: defaultdict(float))
    for obs in obs_list:
        system = obs.get("system", "Unknown")
        bucket = _priority_bucket(obs.get("priority", ""))
        sys_bucket_costs[system][bucket] += obs.get("cost_high", 0) or 0

    for bucket in bucket_order[:6]:
        items = []
        for system, _ in sorted_systems:
            amt = sys_bucket_costs[system].get(bucket, 0)
            if amt > 0:
                items.append(f'    {{ name: "{system}", amount: {int(amt)} }}')
        if items:
            lines.append(f'  Period "{bucket}":')
            lines.append(",\n".join(items))
            lines.append("")
    lines.append("")

    # Observations grouped by system
    lines.append("=" * 60)
    lines.append("OBSERVATIONS BY SYSTEM")
    lines.append("=" * 60)

    obs_by_system = defaultdict(list)
    for obs in obs_list:
        obs_by_system[obs.get("system", "Unknown")].append(obs)

    for system, _ in sorted_systems:
        sys_obs = obs_by_system.get(system, [])
        sys_data = by_system[system]
        lines.append("")
        lines.append(f"── {system.upper()} ({sys_data['count']} obs, total: ${sys_data['cost_high']:,.0f}) ──")
        for obs in sys_obs:
            cost_h = obs.get("cost_high", 0) or 0
            cost_str = f"${cost_h:,.0f}" if cost_h > 0 else "$0"
            flags = obs.get("flags", [])
            flag_str = " [FLAG]" if flags else ""
            lines.append(
                f"  [{obs.get('obs_number', '?')}] {obs.get('component', '?')} — "
                f"{obs.get('location', '?')} — {obs.get('condition', '?')} — "
                f"{obs.get('priority', '?')} — {cost_str}{flag_str}"
            )
            prose = (obs.get("prose", "") or "")[:150]
            rec = (obs.get("recommendation", "") or "")[:120]
            if prose:
                lines.append(f"    {prose}")
            if rec:
                lines.append(f"    Rec: {rec}")

    return "\n".join(lines)


def _aggregate_chart_categories(tool_input, job_data):
    """Post-process show_capital_chart output to merge individual items into systems.

    When the model returns granular categories like "Roof Membrane Replacement"
    and "Parapet Wall Repairs", this merges them into "Roof" by matching against
    known system names from the survey data.
    """
    obs_list = job_data.get("processed_observations", [])

    # Build lookup: component/observation name fragments → system
    system_keywords = defaultdict(set)
    for obs in obs_list:
        system = obs.get("system", "")
        if not system:
            continue
        # Add the system name itself
        system_keywords[system.lower()].add(system)
        # Add component and location as keywords
        for field in ("component", "location", "funding_label"):
            val = (obs.get(field, "") or "").lower().strip()
            if val:
                system_keywords[val].add(system)

    # Also build a direct amount→system lookup from observations
    known_systems = set()
    for obs in obs_list:
        s = obs.get("system", "")
        if s:
            known_systems.add(s)

    def match_system(category_name):
        """Try to match a category name to a known system."""
        name_lower = category_name.lower()

        # Direct match
        for sys in known_systems:
            if sys.lower() == name_lower:
                return sys

        # Check if the system name is contained in the category name
        # Sort by length (longest first) to prefer more specific matches
        for sys in sorted(known_systems, key=len, reverse=True):
            if sys.lower() in name_lower:
                return sys

        # Check if category name contains key system words
        system_word_map = {
            "roof": "Roof",
            "membrane": "Roof",
            "parapet": "Roof",
            "coping": "Roof",
            "facade": "Exterior Walls / Facade",
            "brick": "Exterior Walls / Facade",
            "masonry": "Exterior Walls / Facade",
            "plexiglass": "Exterior Walls / Facade",
            "wind screen": "Exterior Walls / Facade",
            "fisp": "Exterior Walls / Facade",
            "sealant": "Exterior Walls / Facade",
            "window": "Exterior Walls / Facade",
            "elevator": "Elevators",
            "hvac": "HVAC",
            "boiler": "HVAC",
            "cooling": "HVAC",
            "steam": "HVAC",
            "humidifier": "HVAC",
            "heating": "HVAC",
            "plumbing": "Plumbing",
            "pump": "Plumbing",
            "sump": "Plumbing",
            "backflow": "Plumbing",
            "water": "Plumbing",
            "drain": "Plumbing",
            "electrical": "Electrical",
            "junction": "Electrical",
            "arc flash": "Electrical",
            "switchgear": "Electrical",
            "fire": "Fire Protection",
            "sprinkler": "Fire Protection",
            "alarm": "Fire Protection",
            "interior": "Interior Finishes",
            "corridor": "Interior Finishes",
            "lobby": "Interior Finishes",
            "ceiling": "Interior Finishes",
            "foundation": "Structural / Building Envelope",
            "structural": "Structural / Building Envelope",
            "energy": "Energy Systems / Building Envelope",
            "ll97": "Energy Systems / Building Envelope",
            "law 97": "Energy Systems / Building Envelope",
            "compactor": "Common Areas",
            "trash": "Common Areas",
            "site": "Site / Grounds",
            "sidewalk": "Site / Grounds",
            "landscape": "Site / Grounds",
        }

        for keyword, sys in system_word_map.items():
            if keyword in name_lower:
                # Only use if this system actually exists in the building data
                if sys in known_systems:
                    return sys
                # Fuzzy: check if a similar system exists
                for ks in known_systems:
                    if keyword in ks.lower():
                        return ks

        return None

    # Process each period
    periods = tool_input.get("periods", [])
    new_periods = []

    for period in periods:
        merged = defaultdict(float)
        for cat in period.get("categories", []):
            system = match_system(cat["name"])
            if system:
                merged[system] += cat.get("amount", 0)
            else:
                merged[cat["name"]] += cat.get("amount", 0)

        # Sort by amount descending
        sorted_cats = sorted(merged.items(), key=lambda x: x[1], reverse=True)

        # Combine small items into "Other" if > 8 categories
        if len(sorted_cats) > 8:
            top = sorted_cats[:7]
            other_total = sum(amt for _, amt in sorted_cats[7:])
            top.append(("Other", other_total))
            sorted_cats = top

        new_periods.append({
            "label": period["label"],
            "categories": [{"name": name, "amount": int(amt)} for name, amt in sorted_cats if amt > 0],
        })

    tool_input["periods"] = new_periods
    return tool_input


def stream_chat_response(job_data, message, history):
    """Generator that yields SSE event dicts from Claude's streaming response.

    Yields dicts with keys:
        type: "text_delta" | "tool_use_complete" | "complete" | "error"
        + type-specific fields
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        yield {"type": "error", "message": "API key not configured"}
        return

    model_name = os.getenv("CHAT_MODEL_NAME", os.getenv("MODEL_NAME", "claude-sonnet-4-20250514"))
    client = anthropic.Anthropic(api_key=api_key)

    # Build context
    context = build_chat_context(job_data)

    # Build messages: context as first user message, then history, then new message
    messages = [
        {
            "role": "user",
            "content": (
                "Here is the full Physical Condition Survey data for this building. "
                "The executive summary at the top has pre-computed totals — use those "
                "directly for charts and summaries rather than re-counting from raw "
                "observations.\n\n" + context
            ),
        },
        {
            "role": "assistant",
            "content": (
                "I've reviewed the complete Physical Condition Survey. I have the "
                "system-level cost totals and the priority timeline matrix ready — "
                "I'll use those for any charts or summaries. I also have the full "
                "observation details for when you want to drill into a specific system. "
                "What would you like to know about your building?"
            ),
        },
    ]

    for msg in (history or []):
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": message})

    try:
        with client.messages.stream(
            model=model_name,
            max_tokens=16000,
            system=CHAT_SYSTEM_PROMPT,
            tools=CHAT_TOOL_SCHEMAS,
            messages=messages,
        ) as stream:
            current_tool_name = None
            current_tool_id = None
            tool_input_json = ""

            for event in stream:
                if event.type == "content_block_start":
                    if event.content_block.type == "tool_use":
                        current_tool_id = event.content_block.id
                        current_tool_name = event.content_block.name
                        tool_input_json = ""

                elif event.type == "content_block_delta":
                    if hasattr(event.delta, "text"):
                        yield {"type": "text_delta", "text": event.delta.text}
                    elif hasattr(event.delta, "partial_json"):
                        tool_input_json += event.delta.partial_json

                elif event.type == "content_block_stop":
                    if current_tool_name:
                        try:
                            tool_input = json.loads(tool_input_json) if tool_input_json else {}
                        except json.JSONDecodeError:
                            tool_input = {}

                        yield {
                            "type": "tool_use_complete",
                            "id": current_tool_id,
                            "tool": current_tool_name,
                            "input": tool_input,
                        }
                        current_tool_name = None
                        current_tool_id = None
                        tool_input_json = ""

            # Get final usage for cost tracking
            final = stream.get_final_message()
            input_tokens = final.usage.input_tokens
            output_tokens = final.usage.output_tokens

            # Detect truncation
            if final.stop_reason == "max_tokens":
                yield {"type": "text_delta", "text": "\n\n*(Response was cut short — try a more specific question or ask me to continue.)*"}

            # Estimate cost
            lower = model_name.lower()
            if "haiku" in lower:
                cost = (input_tokens * 0.80 + output_tokens * 4.00) / 1_000_000
            elif "opus" in lower:
                cost = (input_tokens * 15.00 + output_tokens * 75.00) / 1_000_000
            else:
                cost = (input_tokens * 3.00 + output_tokens * 15.00) / 1_000_000

            yield {"type": "complete", "cost_usd": round(cost, 4)}

    except anthropic.APIError as e:
        yield {"type": "error", "message": f"API error: {str(e)}"}
    except Exception as e:
        yield {"type": "error", "message": f"Unexpected error: {str(e)}"}
