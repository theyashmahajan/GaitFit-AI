from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


def build_report_pdf(payload: dict[str, Any], out_dir: Path) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 2.0 * cm
    c.setFont("Helvetica-Bold", 18)
    c.drawString(2 * cm, y, "GaitFit AI Report")
    y -= 0.7 * cm
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.grey)
    c.drawString(2 * cm, y, f"Job ID: {payload.get('job_id', '-')}")
    c.setFillColor(colors.black)
    y -= 1.0 * cm

    profile = payload.get("gait_profile", {})
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2 * cm, y, "Gait Profile")
    y -= 0.6 * cm
    c.setFont("Helvetica", 11)
    _line(c, 2, y, f"Pronation: {profile.get('pronation_type', '-')}")
    y -= 0.5 * cm
    _line(c, 2, y, f"Strike Pattern: {profile.get('strike_pattern', '-')}")
    y -= 0.5 * cm
    _line(c, 2, y, f"Knee Alignment: {profile.get('knee_alignment', '-')}")
    y -= 0.5 * cm
    _line(c, 2, y, f"Cadence: {profile.get('cadence_spm', '-')}")
    y -= 0.7 * cm

    summary = payload.get("summary", "")
    c.setFont("Helvetica-Bold", 13)
    c.drawString(2 * cm, y, "Summary")
    y -= 0.6 * cm
    c.setFont("Helvetica", 11)
    y = _multiline(c, 2 * cm, y, summary, width - 4 * cm, 14)
    y -= 0.4 * cm

    size_est = payload.get("shoe_size_estimate", {})
    if size_est:
        c.setFont("Helvetica-Bold", 13)
        c.drawString(2 * cm, y, "Estimated Shoe Size")
        y -= 0.6 * cm
        c.setFont("Helvetica", 11)
        if size_est.get("estimated"):
            _line(c, 2, y, f"Foot Length (estimated): {size_est.get('foot_length_cm', '-')} cm")
            y -= 0.5 * cm
            _line(c, 2, y, f"UK: {size_est.get('uk_size', '-')}")
            y -= 0.5 * cm
            _line(c, 2, y, f"US (Men): {size_est.get('us_men_size', '-')}")
            y -= 0.5 * cm
            _line(c, 2, y, f"US (Women): {size_est.get('us_women_size', '-')}")
            y -= 0.5 * cm
            _line(c, 2, y, f"EU: {size_est.get('eu_size', '-')}")
            y -= 0.5 * cm
            _line(c, 2, y, f"Confidence: {size_est.get('confidence', '-')}")
            y -= 0.5 * cm
            y = _multiline(c, 2 * cm, y, str(size_est.get("disclaimer", "")), width - 4 * cm, 12)
            y -= 0.3 * cm
        else:
            y = _multiline(c, 2 * cm, y, str(size_est.get("message", "")), width - 4 * cm, 12)
            y -= 0.3 * cm

    c.setFont("Helvetica-Bold", 13)
    c.drawString(2 * cm, y, "Top Recommendations")
    y -= 0.6 * cm
    c.setFont("Helvetica", 11)
    for idx, rec in enumerate(payload.get("recommendations", [])[:3], start=1):
        _line(c, 2, y, f"{idx}. {rec.get('shoe_type', '-')}: {int((rec.get('match_score', 0) or 0) * 100)}%")
        y -= 0.5 * cm
        y = _multiline(c, 2.4 * cm, y, rec.get("why_this_fits", ""), width - 4.4 * cm, 13)
        y -= 0.3 * cm

    evidence = payload.get("evidence", {})
    evidence_url = evidence.get("image_url", "")
    if evidence_url:
        local_name = evidence_url.replace("/assets/", "")
        local_path = out_dir / local_name
        if local_path.exists():
            y -= 0.2 * cm
            c.setFont("Helvetica-Bold", 13)
            c.drawString(2 * cm, y, "Visual Evidence")
            y -= 0.6 * cm
            img_w = width - 4 * cm
            img_h = min(8 * cm, y - 1.2 * cm)
            if img_h > 2 * cm:
                c.drawImage(str(local_path), 2 * cm, y - img_h, img_w, img_h, preserveAspectRatio=True, anchor="n")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()


def _line(c: canvas.Canvas, x_cm: float, y: float, text: str) -> None:
    c.drawString(x_cm * cm, y, text)


def _multiline(c: canvas.Canvas, x: float, y: float, text: str, max_width: float, line_height: int) -> float:
    words = text.split()
    line = ""
    for word in words:
        test = (line + " " + word).strip()
        if c.stringWidth(test, "Helvetica", 11) <= max_width:
            line = test
            continue
        c.drawString(x, y, line)
        y -= line_height
        line = word
    if line:
        c.drawString(x, y, line)
        y -= line_height
    return y
