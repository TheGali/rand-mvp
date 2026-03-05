"""Main CLI entry point for the RAND report pipeline.

Usage:
    python run.py --input mock/output/test_survey.pptx --output results/
"""

import os
from pathlib import Path

import click
from dotenv import load_dotenv

from src.parser import parse_pptx
from src.processor import process_report
from src.pptx_writer import write_results_to_pptx
from src.excel_writer import write_command_center, write_funding_summary


def write_flags_report(report, output_path):
    """Write a plain text report of all flags across observations."""
    lines = []
    lines.append("RAND Report Pipeline — Flags Report")
    lines.append("=" * 50)
    lines.append("")

    flag_count = 0
    for po in report.processed_observations:
        if po.flags:
            lines.append(f"Observation {po.obs_number} ({po.section_name}):")
            for flag in po.flags:
                lines.append(f"  [{flag.get('type', 'unknown')}] {flag.get('message', '')}")
                flag_count += 1
            lines.append("")

    if flag_count == 0:
        lines.append("No flags raised.")
    else:
        lines.append(f"Total flags: {flag_count}")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"  Written: {output_path}")


@click.command()
@click.option("--input", "input_path", required=True, help="Path to input .pptx file")
@click.option("--output", "output_dir", required=True, help="Output directory for results")
def main(input_path, output_dir):
    """RAND AI Report Pipeline — process a survey PowerPoint into structured output."""
    load_dotenv(override=True)

    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stem = input_path.stem

    print(f"RAND AI Report Pipeline")
    print(f"{'=' * 50}")
    print(f"Input: {input_path}")
    print(f"Output: {output_dir}")

    # Step 1: Parse PowerPoint
    print(f"\n[1/4] Parsing PowerPoint...")
    report = parse_pptx(str(input_path))
    print(f"  Found {len(report.observations)} observations")
    if report.building_name:
        print(f"  Building: {report.building_name}")

    # Step 2: Process through Claude
    print(f"\n[2/4] Processing observations through Claude API...")
    report = process_report(report)

    # Step 3: Write outputs
    print(f"\n[3/4] Writing output files...")

    pptx_out = output_dir / f"{stem}_processed.pptx"
    write_results_to_pptx(report, str(input_path), str(pptx_out))

    cc_out = output_dir / "command_center.xlsx"
    write_command_center(report, str(cc_out))

    fs_out = output_dir / "funding_summary.xlsx"
    write_funding_summary(report, str(fs_out))

    flags_out = output_dir / "flags_report.txt"
    write_flags_report(report, str(flags_out))

    # Step 4: Summary
    print(f"\n[4/4] Summary")
    print(f"{'=' * 50}")
    print(f"  Observations processed: {len(report.processed_observations)}")

    flagged = sum(1 for po in report.processed_observations if po.flags)
    print(f"  Observations with flags: {flagged}")

    total_cost = sum(po.cost_high for po in report.processed_observations)
    print(f"  Total estimated cost (high): ${total_cost:,.0f}")

    systems = set(po.system for po in report.processed_observations if po.system)
    print(f"  Systems covered: {len(systems)}")

    print(f"\n  Output files:")
    print(f"    {pptx_out}")
    print(f"    {cc_out}")
    print(f"    {fs_out}")
    print(f"    {flags_out}")
    print(f"\nDone.")


if __name__ == "__main__":
    main()
