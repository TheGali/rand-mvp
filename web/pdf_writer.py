"""PDF report generator using fpdf2 — secondary deliverable.

Structure:
  1. Cover page (building name, address, date)
  2. Command center table
  3. Observation pages (photo + prose + recommendation)
  4. Funding summary appendix
"""

from collections import defaultdict
from pathlib import Path

from fpdf import FPDF


def _safe_text(text):
    """Replace unicode characters that fpdf2 core fonts can't handle."""
    return (
        str(text)
        .replace("\u2014", " - ")   # em dash
        .replace("\u2013", " - ")   # en dash
        .replace("\u2018", "'")     # left single quote
        .replace("\u2019", "'")     # right single quote
        .replace("\u201c", '"')     # left double quote
        .replace("\u201d", '"')     # right double quote
        .replace("\u2026", "...")   # ellipsis
        .replace("\u00b0", " deg")  # degree sign
        .replace("\u00ae", "(R)")   # registered
        .replace("\u2122", "(TM)")  # trademark
        .encode("latin-1", errors="replace").decode("latin-1")
    )


# RAND brand colors (RGB tuples)
NAVY = (30, 58, 95)
BLUE = (37, 99, 235)
WHITE = (255, 255, 255)
DARK = (31, 42, 55)
GRAY = (107, 114, 128)
LIGHT_BG = (240, 244, 248)

# Condition badge colors
COND_COLORS = {
    "critical": (127, 29, 29),
    "poor": (153, 27, 27),
    "fair": (146, 64, 14),
    "good": (6, 95, 70),
    "satisfactory": (30, 64, 175),
}


class RANDReport(FPDF):
    """Custom PDF with RAND header/footer."""

    def __init__(self, job):
        super().__init__(orientation="P", unit="mm", format="letter")
        self.job = job
        self.set_auto_page_break(auto=True, margin=20)

    def cell(self, *args, **kwargs):
        if args and len(args) >= 3 and isinstance(args[2], str):
            args = list(args)
            args[2] = _safe_text(args[2])
        if "text" in kwargs and isinstance(kwargs["text"], str):
            kwargs["text"] = _safe_text(kwargs["text"])
        # Also handle the 'txt' kwarg
        if "txt" in kwargs and isinstance(kwargs["txt"], str):
            kwargs["txt"] = _safe_text(kwargs["txt"])
        return super().cell(*args, **kwargs)

    def multi_cell(self, *args, **kwargs):
        if args and len(args) >= 3 and isinstance(args[2], str):
            args = list(args)
            args[2] = _safe_text(args[2])
        if "text" in kwargs and isinstance(kwargs["text"], str):
            kwargs["text"] = _safe_text(kwargs["text"])
        if "txt" in kwargs and isinstance(kwargs["txt"], str):
            kwargs["txt"] = _safe_text(kwargs["txt"])
        return super().multi_cell(*args, **kwargs)

    def header(self):
        if self.page_no() == 1:
            return  # No header on cover
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*NAVY)
        self.cell(0, 5, "RAND Engineering & Architecture, DPC", align="L")
        self.cell(0, 5, self.job.get("building_name", ""), align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*NAVY)
        line_y = self.get_y() + 1
        self.line(10, line_y, self.w - 10, line_y)
        self.ln(4)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*GRAY)
        self.cell(0, 5, f"Physical Condition Survey — Page {self.page_no()}", align="C")


def _add_cover(pdf, job):
    """Cover page."""
    pdf.add_page()
    pdf.set_fill_color(*NAVY)
    pdf.rect(0, 0, pdf.w, pdf.h, "F")

    # Building name
    pdf.set_y(80)
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*WHITE)
    pdf.multi_cell(0, 15, job.get("building_name", "Building Survey"), align="C", new_x="LMARGIN", new_y="NEXT")

    # Address
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(187, 204, 221)
    pdf.cell(0, 10, job.get("address", ""), align="C", new_x="LMARGIN", new_y="NEXT")

    # Report type
    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 14)
    pdf.set_text_color(153, 170, 187)
    pdf.cell(0, 10, "Physical Condition Survey", align="C", new_x="LMARGIN", new_y="NEXT")

    # RAND branding
    pdf.set_y(200)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(136, 153, 170)
    pdf.cell(0, 8, "RAND Engineering & Architecture, DPC", align="C", new_x="LMARGIN", new_y="NEXT")


def _add_command_center(pdf, observations):
    """Command center table page(s)."""
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "Command Center", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Table header
    col_widths = [14, 35, 30, 22, 22, 55, 18]
    headers = ["Obs #", "System", "Component", "Cond.", "Priority", "Summary", "Cost"]

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)

    for i, (header, w) in enumerate(zip(headers, col_widths)):
        pdf.cell(w, 7, header, border=1, fill=True, align="C")
    pdf.ln()

    # Data rows
    pdf.set_font("Helvetica", "", 7)
    for idx, obs in enumerate(observations):
        # Check if we need a new page
        if pdf.get_y() > 245:
            pdf.add_page()
            # Re-draw header
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(*NAVY)
            pdf.cell(0, 10, "Command Center (continued)", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_fill_color(*NAVY)
            pdf.set_text_color(*WHITE)
            for header, w in zip(headers, col_widths):
                pdf.cell(w, 7, header, border=1, fill=True, align="C")
            pdf.ln()
            pdf.set_font("Helvetica", "", 7)

        # Alternating row color
        if idx % 2 == 0:
            pdf.set_fill_color(*LIGHT_BG)
            fill = True
        else:
            pdf.set_fill_color(*WHITE)
            fill = True

        pdf.set_text_color(*DARK)

        cost_high = obs.get("cost_high", 0)
        cost_str = f"${cost_high:,.0f}" if cost_high > 0 else ""

        prose_summary = obs.get("prose", "")
        if len(prose_summary) > 45:
            prose_summary = prose_summary[:45] + "..."

        values = [
            obs.get("obs_number", ""),
            obs.get("system", "")[:22],
            obs.get("component", "")[:20],
            obs.get("condition", ""),
            obs.get("priority", "")[:12],
            prose_summary,
            cost_str,
        ]

        for val, w in zip(values, col_widths):
            pdf.cell(w, 6, str(val), border=1, fill=fill)
        pdf.ln()


def _add_observation_pages(pdf, observations, job_dir):
    """One page per observation with photo, prose, and details."""
    for obs in observations:
        pdf.add_page()

        obs_number = obs.get("obs_number", "")
        system = obs.get("system", "")

        # Observation header
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 8, f"Observation {obs_number} — {system}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        # Photo
        image_path = Path(job_dir) / "images" / f"obs_{obs_number}.png"
        if image_path.exists():
            try:
                pdf.image(str(image_path), x=10, w=90)
                pdf.ln(3)
            except Exception:
                pass

        # Caption
        caption = obs.get("caption", "")
        if caption:
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(*GRAY)
            pdf.multi_cell(0, 4, caption)
            pdf.ln(3)

        # Info box
        info_items = [
            ("System", obs.get("system", "")),
            ("Component", obs.get("component", "")),
            ("Location", obs.get("location", "")),
            ("Condition", obs.get("condition", "")),
            ("Priority", obs.get("priority", "")),
        ]
        if obs.get("cost_high", 0) > 0:
            info_items.append(("Cost Range", f"${obs.get('cost_low', 0):,.0f} — ${obs.get('cost_high', 0):,.0f}"))

        pdf.set_fill_color(*LIGHT_BG)
        y_start = pdf.get_y()
        pdf.rect(10, y_start, pdf.w - 20, len(info_items) * 5 + 4, "F")
        pdf.set_y(y_start + 2)

        for label, value in info_items:
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*GRAY)
            pdf.cell(30, 5, f"{label}:")
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*DARK)
            pdf.cell(0, 5, value, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        # Prose
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*NAVY)
        pdf.cell(0, 6, "Observation", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*DARK)
        pdf.multi_cell(0, 5, obs.get("prose", ""))
        pdf.ln(3)

        # Recommendation
        rec = obs.get("recommendation", "")
        if rec:
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*NAVY)
            pdf.cell(0, 6, "Recommendation", new_x="LMARGIN", new_y="NEXT")

            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*DARK)
            pdf.multi_cell(0, 5, rec)

        # Flags
        flags = obs.get("flags", [])
        if flags:
            pdf.ln(3)
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(146, 64, 14)
            for flag in flags:
                pdf.cell(0, 4, f"  {flag.get('type', '')}: {flag.get('message', '')}", new_x="LMARGIN", new_y="NEXT")


def _add_funding_summary(pdf, observations):
    """Funding summary appendix page."""
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "Funding Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Group costs
    system_priority_costs = defaultdict(lambda: defaultdict(float))
    all_priorities = set()

    for obs in observations:
        system = obs.get("system", "Other")
        priority = obs.get("priority", "Unclassified")
        cost_high = obs.get("cost_high", 0)
        all_priorities.add(priority)
        if cost_high > 0:
            system_priority_costs[system][priority] += cost_high

    def priority_sort_key(p):
        pl = p.lower()
        if "immediate" in pl or "1-2" in pl:
            return 0
        if "1-3" in pl or "short" in pl:
            return 1
        if "3-5" in pl or "medium" in pl:
            return 2
        if "6-10" in pl or "long" in pl:
            return 3
        if "10" in pl or "capital" in pl:
            return 4
        return 5

    sorted_priorities = sorted(all_priorities, key=priority_sort_key)
    sorted_systems = sorted(system_priority_costs.keys())

    if not sorted_systems:
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*GRAY)
        pdf.cell(0, 8, "No cost data available.")
        return

    # Table
    cols = ["System"] + sorted_priorities + ["Total"]
    num_cols = len(cols)
    system_w = 40
    data_w = (pdf.w - 20 - system_w) / (num_cols - 1)

    # Header
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    pdf.cell(system_w, 7, "System", border=1, fill=True, align="C")
    for col in cols[1:]:
        col_display = col[:12] if len(col) > 12 else col
        pdf.cell(data_w, 7, col_display, border=1, fill=True, align="C")
    pdf.ln()

    # Data
    pdf.set_font("Helvetica", "", 7)
    for i, system in enumerate(sorted_systems):
        if i % 2 == 0:
            pdf.set_fill_color(*LIGHT_BG)
        else:
            pdf.set_fill_color(*WHITE)

        pdf.set_text_color(*DARK)
        sys_display = system[:25] if len(system) > 25 else system
        pdf.cell(system_w, 6, sys_display, border=1, fill=True)

        row_total = 0
        for pri in sorted_priorities:
            cost = system_priority_costs[system].get(pri, 0)
            pdf.cell(data_w, 6, f"${cost:,.0f}" if cost > 0 else "—", border=1, fill=True, align="R")
            row_total += cost

        pdf.set_font("Helvetica", "B", 7)
        pdf.cell(data_w, 6, f"${row_total:,.0f}" if row_total > 0 else "—", border=1, fill=True, align="R")
        pdf.set_font("Helvetica", "", 7)
        pdf.ln()

    # Grand total
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(*LIGHT_BG)
    pdf.cell(system_w, 7, "TOTAL", border=1, fill=True)

    for pri in sorted_priorities:
        col_total = sum(system_priority_costs[sys].get(pri, 0) for sys in sorted_systems)
        pdf.cell(data_w, 7, f"${col_total:,.0f}" if col_total > 0 else "—", border=1, fill=True, align="R")

    grand_total = sum(cost for sys_costs in system_priority_costs.values() for cost in sys_costs.values())
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(data_w, 7, f"${grand_total:,.0f}", border=1, fill=True, align="R")


def _add_signoff_page(pdf, observations):
    """Engineer sign-off appendix page listing all approved observations."""
    approved = [o for o in observations if o.get("approved")]
    if not approved:
        return

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "Engineer Sign-Off", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, "Each observation below has been reviewed and approved by the signing engineer.",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    col_widths = [18, 55, 55, 68]
    headers = ["Obs #", "System", "Approved By", "Date"]

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    for header, w in zip(headers, col_widths):
        pdf.cell(w, 7, header, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_font("Helvetica", "", 7)
    for idx, obs in enumerate(approved):
        if pdf.get_y() > 245:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(*NAVY)
            pdf.cell(0, 10, "Engineer Sign-Off (continued)", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_fill_color(*NAVY)
            pdf.set_text_color(*WHITE)
            for header, w in zip(headers, col_widths):
                pdf.cell(w, 7, header, border=1, fill=True, align="C")
            pdf.ln()
            pdf.set_font("Helvetica", "", 7)

        if idx % 2 == 0:
            pdf.set_fill_color(*LIGHT_BG)
        else:
            pdf.set_fill_color(*WHITE)

        pdf.set_text_color(*DARK)

        approved_at = obs.get("approved_at", "")
        if approved_at:
            try:
                approved_at = approved_at[:10]
            except Exception:
                pass

        values = [
            obs.get("obs_number", ""),
            obs.get("system", "")[:35],
            obs.get("approved_by", "")[:35],
            approved_at,
        ]

        for val, w in zip(values, col_widths):
            pdf.cell(w, 6, str(val), border=1, fill=True)
        pdf.ln()


def generate_pdf_report(job, job_dir, output_path):
    """Generate the polished PDF report.

    Args:
        job: Job dict from job.json
        job_dir: Path to the job directory (for images)
        output_path: Path for output .pdf file
    """
    observations = job.get("processed_observations", [])

    pdf = RANDReport(job)

    # 1. Cover
    _add_cover(pdf, job)

    # 2. Command center
    _add_command_center(pdf, observations)

    # 3. Observation pages
    _add_observation_pages(pdf, observations, job_dir)

    # 4. Funding summary
    _add_funding_summary(pdf, observations)

    # 5. Engineer sign-off
    _add_signoff_page(pdf, observations)

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
