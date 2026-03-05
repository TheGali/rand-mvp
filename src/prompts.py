"""Prompt templates and tool schemas for Claude API calls.

Loads few-shot examples from style_guide/rand_examples.md at module level.
"""

import os
from pathlib import Path

# Load few-shot examples
_STYLE_GUIDE_DIR = Path(__file__).resolve().parent.parent / "style_guide"
_EXAMPLES_PATH = _STYLE_GUIDE_DIR / "rand_examples.md"

try:
    FEW_SHOT_EXAMPLES = _EXAMPLES_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    FEW_SHOT_EXAMPLES = ""

SYSTEM_PROMPT = """\
You are a senior engineer at RAND Engineering & Architecture, writing Physical Condition Survey (PCS) reports for New York City cooperative and condominium buildings.

## Voice and Style
- Write in passive voice and third person ("was observed to be", "it is recommended that")
- Use formal, technical engineering language — no hedging, no qualifiers like "seems" or "appears to"
- Spell out numbers under ten; use numerals for measurements and quantities
- Reference building codes and standards where relevant (NYC Building Code, ASTM, etc.)
- Be specific: name materials, dimensions, locations, quantities
- Each prose paragraph should be 3-6 sentences covering situation, problem, observation details, and recommendation
- Do NOT use bullet points in prose — write flowing paragraphs

## Photo Caption Convention
Format: "Photo [obs_number]: [Location] — [brief description of what's shown]"
Keep captions to one line, descriptive but concise.

## Cost Estimates
- Only populate cost_low and cost_high if the field notes explicitly state a dollar amount
- Never invent or estimate costs — the AI must not fabricate pricing
- If no cost is mentioned in the field notes, use 0 for both cost_low and cost_high
- When a cost range is stated (e.g., "$150,000-$200,000"), extract the numbers directly

## Handling Incomplete Input
- Field notes may be abbreviated, messy dictation, or missing SPORT fields
- Work with whatever text is provided — extract what you can, infer the rest from context and any photo
- If a photo is provided with no text, describe what you observe in the photo
- If text is provided with no photo, work from the text alone
- Flag observations where critical information is missing (use the flags field)

## Output
Use the provided tool to return structured data. Every field should be populated with your best assessment.
"""


def build_observation_prompt(obs, section_name="", examples=""):
    """Build the user prompt for a single observation.

    Args:
        obs: Observation dataclass instance
        section_name: Current building system section (from divider slide)
        examples: Few-shot examples text
    """
    parts = []

    if examples:
        parts.append("## Reference Examples\n")
        parts.append(examples)
        parts.append("\n---\n")

    parts.append("## Current Observation\n")

    if section_name:
        parts.append(f"**Building System Section:** {section_name}\n")

    parts.append(f"**Observation Number:** {obs.obs_number}\n")

    if obs.raw_text and obs.raw_text.strip():
        parts.append(f"**Field Notes:**\n```\n{obs.raw_text.strip()}\n```\n")
    else:
        parts.append("**Field Notes:** (none provided — describe based on the photo)\n")

    parts.append(
        "\nAnalyze this observation and provide structured output using the tool. "
        "Write report prose in RAND's engineering voice. "
        "Generate a photo caption following the naming convention. "
        "Only include costs if the field notes explicitly state dollar amounts — otherwise use 0."
    )

    return "".join(parts)


OBSERVATION_TOOL_SCHEMA = {
    "name": "record_observation",
    "description": (
        "Record a processed building observation with report prose, "
        "caption, classification, and cost estimate."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "caption": {
                "type": "string",
                "description": "Photo caption in RAND format: 'Photo [obs_number]: [Location] — [description]'"
            },
            "system": {
                "type": "string",
                "description": "Building system category (e.g., Roof, Exterior Walls / Facade, Plumbing)"
            },
            "component": {
                "type": "string",
                "description": "Specific component within the system (e.g., EPDM membrane, galvanized risers)"
            },
            "location": {
                "type": "string",
                "description": "Location within the building (e.g., main roof level, east facade floors 8-10)"
            },
            "condition": {
                "type": "string",
                "description": "Condition rating (e.g., Poor, Fair, Good, Satisfactory, Critical)"
            },
            "prose": {
                "type": "string",
                "description": "Full report prose paragraph in RAND engineering voice (3-6 sentences, passive voice, no bullets)"
            },
            "recommendation": {
                "type": "string",
                "description": "Summary of recommended action"
            },
            "priority": {
                "type": "string",
                "description": "Priority timeframe (e.g., Year 1-2, Year 3-5, Year 6-10, Immediate, Short Term)"
            },
            "cost_low": {
                "type": "number",
                "description": "Extract from field notes only — use 0 if no cost is stated by the engineer"
            },
            "cost_high": {
                "type": "number",
                "description": "Extract from field notes only — use 0 if no cost is stated by the engineer"
            },
            "flags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "Flag type (e.g., missing_info, system_mismatch, unclear_scope)"
                        },
                        "message": {
                            "type": "string",
                            "description": "Description of the issue"
                        }
                    },
                    "required": ["type", "message"]
                },
                "description": "Flags for issues with this observation (missing info, ambiguity, etc.)"
            }
        },
        "required": [
            "caption", "system", "component", "location", "condition",
            "prose", "recommendation", "priority", "cost_low", "cost_high", "flags"
        ]
    }
}
