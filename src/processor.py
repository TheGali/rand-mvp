"""AI processing module — sends observations to Claude for structured output.

Uses tool_use for reliable JSON extraction. Retries on API errors.
Processes observations concurrently for speed. Tracks estimated API cost.
"""

import base64
import io
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import anthropic
from PIL import Image

from src.models import ProcessedObservation
from src.prompts import (
    SYSTEM_PROMPT,
    OBSERVATION_TOOL_SCHEMA,
    FEW_SHOT_EXAMPLES,
    build_observation_prompt,
)


# Pricing per 1M tokens (USD) — update as Anthropic adjusts pricing
_MODEL_PRICING = {
    "sonnet": {"input": 3.00, "output": 15.00},
    "haiku":  {"input": 0.80, "output": 4.00},
    "opus":   {"input": 15.00, "output": 75.00},
}
_DEFAULT_PRICING = {"input": 3.00, "output": 15.00}


def _get_pricing(model_name):
    """Get per-1M-token pricing for a model name."""
    lower = model_name.lower()
    for key, pricing in _MODEL_PRICING.items():
        if key in lower:
            return pricing
    return _DEFAULT_PRICING


def _resize_image(image_bytes, max_dim=1024):
    """Resize image so longest side is at most max_dim pixels."""
    img = Image.open(io.BytesIO(image_bytes))
    w, h = img.size
    if max(w, h) <= max_dim:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    ratio = max_dim / max(w, h)
    new_size = (int(w * ratio), int(h * ratio))
    img = img.resize(new_size, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _process_single_observation(client, obs, model_name, max_dim, max_retries):
    """Process a single observation through Claude API.

    Returns (ProcessedObservation, usage_dict).
    """
    # Build message content
    content = []

    # Add image if present
    if obs.image_bytes:
        resized = _resize_image(obs.image_bytes, max_dim)
        b64_image = base64.b64encode(resized).decode("utf-8")
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": b64_image,
            }
        })

    # Add text prompt
    prompt_text = build_observation_prompt(
        obs,
        section_name=obs.section_name,
        examples=FEW_SHOT_EXAMPLES,
    )
    content.append({"type": "text", "text": prompt_text})

    # Retry loop
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model_name,
                max_tokens=2000,
                system=SYSTEM_PROMPT,
                tools=[OBSERVATION_TOOL_SCHEMA],
                tool_choice={"type": "tool", "name": "record_observation"},
                messages=[{"role": "user", "content": content}],
            )

            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            }

            # Extract tool use result
            for block in response.content:
                if block.type == "tool_use":
                    data = block.input
                    return ProcessedObservation(
                        slide_index=obs.slide_index,
                        obs_number=obs.obs_number,
                        section_name=obs.section_name,
                        raw_text=obs.raw_text,
                        image_bytes=obs.image_bytes,
                        image_path=obs.image_path,
                        caption=data.get("caption", ""),
                        system=data.get("system", obs.section_name),
                        component=data.get("component", ""),
                        location=data.get("location", ""),
                        condition=data.get("condition", ""),
                        prose=data.get("prose", ""),
                        recommendation=data.get("recommendation", ""),
                        funding_label=data.get("funding_label", ""),
                        priority=data.get("priority", ""),
                        cost_low=float(data.get("cost_low", 0)),
                        cost_high=float(data.get("cost_high", 0)),
                        flags=data.get("flags", []),
                    ), usage

            # No tool_use block found
            last_error = "No tool_use block in response"

        except anthropic.APIError as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"    API error (attempt {attempt + 1}): {e}. Retrying in {wait}s...")
                time.sleep(wait)

    # All retries exhausted — return placeholder with error flag
    print(f"    FAILED after {max_retries} attempts: {last_error}")
    return ProcessedObservation(
        slide_index=obs.slide_index,
        obs_number=obs.obs_number,
        section_name=obs.section_name,
        raw_text=obs.raw_text,
        image_bytes=obs.image_bytes,
        image_path=obs.image_path,
        caption=f"Photo {obs.obs_number}: [Processing failed]",
        system=obs.section_name,
        prose="[This observation could not be processed. Please review manually.]",
        flags=[{"type": "processing_error", "message": str(last_error)}],
    ), {"input_tokens": 0, "output_tokens": 0}


def process_report(report, progress_callback=None):
    """Process all observations concurrently through Claude API.

    Args:
        report: Report with populated observations list
        progress_callback: Optional callable(current, total, obs_number, status,
            obs_data=None, cost_usd=0.0) for real-time progress reporting.

    Returns:
        Report with populated processed_observations list
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    model_name = os.getenv("MODEL_NAME", "claude-sonnet-4-20250514")
    max_dim = int(os.getenv("MAX_IMAGE_DIMENSION", "1024"))
    max_retries = int(os.getenv("MAX_RETRIES", "3"))
    concurrency = int(os.getenv("CONCURRENCY", "5"))

    client = anthropic.Anthropic(api_key=api_key)
    pricing = _get_pricing(model_name)

    total = len(report.observations)
    print(f"\nProcessing {total} observations through Claude API...")
    print(f"  Model: {model_name}")
    print(f"  Concurrency: {concurrency}")
    print(f"  Max image dimension: {max_dim}px")
    print()

    start_time = time.time()
    cumulative_cost = 0.0
    completed_count = 0
    results = {}

    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        future_to_idx = {}
        for i, obs in enumerate(report.observations):
            future = pool.submit(
                _process_single_observation, client, obs, model_name, max_dim, max_retries
            )
            future_to_idx[future] = (i, obs)

        for future in as_completed(future_to_idx):
            i, obs = future_to_idx[future]
            processed, usage = future.result()
            results[i] = processed
            completed_count += 1

            # Calculate cost for this observation
            obs_cost = (
                usage["input_tokens"] * pricing["input"]
                + usage["output_tokens"] * pricing["output"]
            ) / 1_000_000
            cumulative_cost += obs_cost

            status = "OK" if not any(f["type"] == "processing_error" for f in processed.flags) else "FAILED"
            print(f"  [{completed_count}/{total}] Obs {processed.obs_number} ({processed.section_name})... {status} (${obs_cost:.4f})")

            if progress_callback:
                obs_data = {
                    "slide_index": processed.slide_index,
                    "obs_number": processed.obs_number,
                    "section_name": processed.section_name,
                    "raw_text": processed.raw_text,
                    "caption": processed.caption,
                    "system": processed.system,
                    "component": processed.component,
                    "location": processed.location,
                    "condition": processed.condition,
                    "prose": processed.prose,
                    "recommendation": processed.recommendation,
                    "priority": processed.priority,
                    "cost_low": processed.cost_low,
                    "cost_high": processed.cost_high,
                    "flags": processed.flags,
                }
                progress_callback(
                    current=completed_count,
                    total=total,
                    obs_number=processed.obs_number,
                    status=status,
                    obs_data=obs_data,
                    cost_usd=cumulative_cost,
                )

    # Reconstruct ordered list
    for i in range(total):
        report.processed_observations.append(results[i])

    total_time = time.time() - start_time
    print(f"\nProcessing complete: {total} observations in {total_time:.1f}s")
    print(f"  Estimated API cost: ${cumulative_cost:.4f}")

    return report
