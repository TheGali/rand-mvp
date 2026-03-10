"""PDF report generator using fpdf2 — secondary deliverable.

Structure:
  1. Cover page (building name, address, date)
  2. Funding summary (expanded view with categories/systems/observations)
  3. Observation pages (photo + prose + recommendation)
  4. Engineer sign-off appendix
"""

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

    # Draft watermark if any observation is unapproved
    observations = job.get("processed_observations", [])
    total = len(observations)
    approved = sum(1 for o in observations if o.get("approved"))
    if total > 0 and approved < total:
        # Large diagonal "DRAFT" watermark (semi-transparent white)
        with pdf.local_context(fill_opacity=0.15):
            pdf.set_font("Helvetica", "B", 80)
            pdf.set_text_color(255, 255, 255)
            with pdf.rotation(angle=-35, x=pdf.w / 2, y=pdf.h / 2):
                pdf.set_xy(0, pdf.h / 2 - 20)
                pdf.cell(pdf.w, 40, "DRAFT", align="C")

        # Approval summary line
        pdf.set_y(160)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(255, 153, 153)
        pdf.cell(0, 10, f"{approved}/{total} observations approved", align="C", new_x="LMARGIN", new_y="NEXT")

    # RAND branding
    pdf.set_y(200)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(136, 153, 170)
    pdf.cell(0, 8, "RAND Engineering & Architecture, DPC", align="C", new_x="LMARGIN", new_y="NEXT")



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


def _priority_to_bucket(priority):
    """Map a priority string to a funding bucket key."""
    p = (priority or "").lower().strip()
    if p in ("immediate", "year 1"):
        return "curr"
    if p in ("year 1-2", "year 1-3", "year 2-3"):
        return "1-3"
    if p in ("year 2-4", "year 3-5", "year 1-5", "year 4-5"):
        return "4-6"
    if p in ("year 6-10", "year 5-10"):
        return "7-9"
    if p in ("year 10+", "year 10-15"):
        return "10-12"
    if p == "capital planning":
        return "13-15"
    return "info"


def _section_to_category(section_name):
    """Map a section/system name to category A, B, or C."""
    s = (section_name or "").lower()
    cat_a = ["roof", "exterior walls", "facade", "windows", "interior finishes",
             "interior", "site", "grounds", "common areas"]
    cat_b = ["hvac", "electrical", "plumbing", "fire protection",
             "elevators", "elevator", "structure", "structural", "foundation"]
    for kw in cat_a:
        if kw in s:
            return "A"
    for kw in cat_b:
        if kw in s:
            return "B"
    return "C"


BUCKET_COLS = ["curr", "1-3", "4-6", "7-9", "10-12", "13-15"]
BUCKET_HEADERS = ["Curr. Rec.", "Yrs 1-3", "Yrs 4-6", "Yrs 7-9", "Yrs 10-12", "Yrs 13-15"]
CATEGORY_LABELS = {
    "A": "A. Building Exterior and Interiors",
    "B": "B. Essential Services",
    "C": "C. Other",
}


def _fmt_cost(amount):
    """Format a cost amount like the web UI."""
    if not amount or amount <= 0:
        return ""
    if amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    if amount >= 1_000:
        return f"${round(amount / 1000)}K"
    return f"${amount:,.0f}"


def _add_funding_summary(pdf, observations):
    """Funding summary — expanded view matching the web UI."""
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "Funding Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Group observations by section number
    section_groups = {}
    for obs in observations:
        parts = (obs.get("obs_number", "") or "").split("-")
        sec_num = parts[0] if parts else "0"
        sec_name = obs.get("section_name") or obs.get("system") or "Unknown"
        key = f"{sec_num}::{sec_name}"
        if key not in section_groups:
            section_groups[key] = {"sec_num": sec_num, "sec_name": sec_name, "obs": []}
        section_groups[key]["obs"].append(obs)

    # Organize into categories
    categories = {"A": [], "B": [], "C": []}
    for key, group in section_groups.items():
        cat = _section_to_category(group["sec_name"])
        categories[cat].append({**group, "section_key": key})

    for cat in ("A", "B", "C"):
        categories[cat].sort(key=lambda g: int(g["sec_num"]) if g["sec_num"].isdigit() else 0)

    # Column widths
    items_w = 62
    est_w = 28
    bucket_w = (pdf.w - 20 - items_w - est_w) / 6

    def _draw_table_header():
        pdf.set_font("Helvetica", "B", 6)
        pdf.set_fill_color(*NAVY)
        pdf.set_text_color(*WHITE)
        pdf.cell(items_w, 8, "Report Items", border=1, fill=True, align="C")
        pdf.cell(est_w, 8, "Est. Qty / Cost", border=1, fill=True, align="C")
        for h in BUCKET_HEADERS:
            pdf.cell(bucket_w, 8, h, border=1, fill=True, align="C")
        pdf.ln()

    _draw_table_header()

    def _check_page_break():
        if pdf.get_y() > 240:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(*NAVY)
            pdf.cell(0, 10, "Funding Summary (continued)", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            _draw_table_header()

    # Grand totals
    grand_buckets = {b: 0 for b in BUCKET_COLS}
    letters = "abcdefghijklmnopqrstuvwxyz"

    for cat in ("A", "B", "C"):
        if not categories[cat]:
            continue

        _check_page_break()

        # Category header row
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_fill_color(220, 228, 237)
        pdf.set_text_color(*NAVY)
        pdf.cell(items_w + est_w + bucket_w * 6, 7, CATEGORY_LABELS[cat], border=1, fill=True)
        pdf.ln()

        for section in categories[cat]:
            _check_page_break()

            # Compute bucket subtotals for this system
            sys_buckets = {b: 0 for b in BUCKET_COLS}
            for obs in section["obs"]:
                b = _priority_to_bucket(obs.get("priority", ""))
                if b != "info" and obs.get("cost_high", 0) > 0:
                    sys_buckets[b] += obs["cost_high"]

            # System subtotal row
            pdf.set_font("Helvetica", "B", 7)
            pdf.set_fill_color(*LIGHT_BG)
            pdf.set_text_color(*DARK)
            label = f"{section['sec_num']}. {section['sec_name']}"
            if len(label) > 38:
                label = label[:38] + "..."
            pdf.cell(items_w, 6, f"  {label} ({len(section['obs'])})", border=1, fill=True)
            pdf.cell(est_w, 6, "", border=1, fill=True)
            for b in BUCKET_COLS:
                pdf.cell(bucket_w, 6, _fmt_cost(sys_buckets[b]), border=1, fill=True, align="R")
            pdf.ln()

            # Individual observation rows
            sorted_obs = sorted(section["obs"], key=lambda o: int((o.get("obs_number", "") or "").split("-")[1]) if len((o.get("obs_number", "") or "").split("-")) > 1 and (o.get("obs_number", "") or "").split("-")[1].isdigit() else 0)

            for i, obs in enumerate(sorted_obs):
                _check_page_break()

                bucket = _priority_to_bucket(obs.get("priority", ""))
                cost = obs.get("cost_high", 0) if obs.get("cost_high", 0) > 0 else 0

                if bucket != "info" and cost > 0:
                    grand_buckets[bucket] += cost

                letter = letters[i] if i < len(letters) else str(i + 1)
                obs_label = (obs.get("funding_label") or obs.get("recommendation") or obs.get("caption") or obs.get("component") or "Observation")
                if len(obs_label) > 50:
                    obs_label = obs_label[:50] + "..."

                pdf.set_font("Helvetica", "", 6)
                pdf.set_fill_color(*WHITE)
                pdf.set_text_color(*DARK)
                pdf.cell(items_w, 5, f"      {letter}. {obs_label}", border=1, fill=True)

                est_info = str(obs.get("estimate_info", "") or "")
                if len(est_info) > 18:
                    est_info = est_info[:18] + "..."
                pdf.set_font("Helvetica", "", 5.5)
                pdf.cell(est_w, 5, est_info, border=1, fill=True, align="C")

                for b in BUCKET_COLS:
                    val = _fmt_cost(cost) if b == bucket and bucket != "info" else ""
                    pdf.cell(bucket_w, 5, val, border=1, fill=True, align="R")
                pdf.ln()

    # Grand total row
    _check_page_break()
    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(*NAVY)
    pdf.set_text_color(*WHITE)
    pdf.cell(items_w, 7, "  TOTAL", border=1, fill=True)
    pdf.cell(est_w, 7, "", border=1, fill=True)
    for b in BUCKET_COLS:
        pdf.cell(bucket_w, 7, _fmt_cost(grand_buckets[b]), border=1, fill=True, align="R")
    pdf.ln()


def _add_signoff_page(pdf, observations):
    """Engineer sign-off appendix page listing all observations with approval status."""
    if not observations:
        return

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "Engineer Sign-Off", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, "Observations marked below have been reviewed and approved by the signing engineer.",
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
    for idx, obs in enumerate(observations):
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

        approved_by = ""
        approved_at = ""
        if obs.get("approved"):
            approved_by = obs.get("approved_by", "")[:35]
            approved_at = obs.get("approved_at", "")
            if approved_at:
                try:
                    approved_at = approved_at[:10]
                except Exception:
                    pass

        values = [
            obs.get("obs_number", ""),
            obs.get("system", "")[:35],
            approved_by,
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

    # 2. Funding summary (expanded view)
    _add_funding_summary(pdf, observations)

    # 3. Observation pages
    _add_observation_pages(pdf, observations, job_dir)

    # 4. Engineer sign-off
    _add_signoff_page(pdf, observations)

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
