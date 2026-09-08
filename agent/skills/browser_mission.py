"""Browser research mission: browse, synthesize locally, and create a PDF report."""
from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path

from core.ollama import OllamaClient
from config import DATA_DIR
from skills.browser_agent import BrowserAgent
from skills.browser_operator import _BROWSER
from skills.audit_log import record

REPORT_DIR = DATA_DIR / "research"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "jarvis-research"


def _pdf(title: str, body: str, path: Path):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, Paragraph
        from reportlab.lib.enums import TA_LEFT
        from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph as P, PageBreak
    except ImportError as exc:
        raise RuntimeError("reportlab is required for PDF reports. Run: pip install -r requirements.txt") from exc
    styles = getSampleStyleSheet()
    styles["Title"].alignment = TA_LEFT
    story = [P(title, styles["Title"]), Spacer(1, 10)]
    for para in re.split(r"\n\s*\n", body.strip()):
        clean = para.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(P(clean.replace("\n", "<br/>"), styles["BodyText"]))
        story.append(Spacer(1, 8))
    SimpleDocTemplate(str(path), pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40).build(story)


def research_mission(goal: str, max_steps: int = 12) -> dict:
    if not goal.strip():
        return {"ok": False, "error": "Research mission is empty."}
    agent = BrowserAgent(OllamaClient(), max_steps=max_steps)
    result = agent.run(goal)
    if not result.get("ok"):
        return result
    snapshot = _BROWSER.snapshot(18000)
    synthesis_prompt = f"""Create a factual research report for this goal: {goal}
Use only the browser evidence below. Clearly separate facts from uncertainty. Include:
1. Executive summary
2. Key findings
3. Practical recommendations
4. Risks/limitations
5. Sources or URLs visible in the evidence

BROWSER EVIDENCE:
{snapshot}"""
    summary = OllamaClient().chat([{"role": "system", "content": "You are JARVIS Research Analyst. Be accurate, concise and transparent."}, {"role": "user", "content": synthesis_prompt}], temperature=0.2)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    pdf_path = REPORT_DIR / f"{_slug(goal)}-{stamp}.pdf"
    md_path = REPORT_DIR / f"{_slug(goal)}-{stamp}.md"
    md_body = f"# JARVIS Research Mission\n\nGoal: {goal}\nGenerated: {datetime.now().isoformat(timespec='minutes')}\n\n{summary}\n\n## Browser evidence\n\n{snapshot}\n"
    md_path.write_text(md_body, encoding="utf-8")
    _pdf(f"JARVIS Research Report — {goal}", summary + "\n\nSources / browser evidence:\n" + snapshot, pdf_path)
    try:
        subprocess.Popen(["cmd", "/c", "start", "", str(pdf_path)], shell=False)
    except Exception:
        pass
    record("research_mission", "completed", f"{goal[:300]} | {pdf_path}")
    return {"ok": True, "pdf": str(pdf_path), "markdown": str(md_path), "sources": re.findall(r"https?://[^\s]+", snapshot)[:30], "summary": summary, "history": result.get("history", [])}
