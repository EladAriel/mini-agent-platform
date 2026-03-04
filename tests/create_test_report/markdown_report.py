"""
markdown_report.py — converts collected test records into a Markdown string.

The Markdown is structured as:

  # Test Report
  ## Summary          ← stat table + progress bar (HTML inside MD)
  ## Results          ← one H3 per file, one table per file
"""

from __future__ import annotations

from collections import defaultdict


# ── Escaping ──────────────────────────────────────────────────────────────────

def _md(text: str) -> str:
    """Escape pipe characters so they don't break Markdown tables."""
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


# ── Public API ────────────────────────────────────────────────────────────────

def build_markdown(records: list[dict], *, total_duration_ms: int) -> str:
    passed  = sum(1 for r in records if r["status"] == "PASSED")
    failed  = sum(1 for r in records if r["status"] == "FAILED")
    skipped = sum(1 for r in records if r["status"] == "SKIPPED")
    total   = len(records)
    pct     = round(passed / total * 100) if total else 0

    lines: list[str] = []

    # ── Title ─────────────────────────────────────────────────────────────────
    lines += [
        "# 🧪 Test Report",
        "",
    ]

    # ── Summary table ─────────────────────────────────────────────────────────
    lines += [
        "## Summary",
        "",
        "| | |",
        "|---|---|",
        f"| **Score** | `{passed} / {total}` |",
        f"| **Passed** | {passed} ✅ |",
        f"| **Failed** | {failed} {'❌' if failed else '—'} |",
        f"| **Skipped** | {skipped} {'⚠️' if skipped else '—'} |",
        f"| **Duration** | {total_duration_ms:,} ms |",
        f"| **Pass rate** | {pct}% |",
        "",
    ]

    # ── Per-file results ──────────────────────────────────────────────────────
    lines += ["## Results", ""]

    by_file: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_file[r["file"]].append(r)

    for fname, recs in sorted(by_file.items()):
        f_passed = sum(1 for r in recs if r["status"] == "PASSED")
        f_total  = len(recs)

        lines += [
            f"### 📁 `{fname}`  —  {f_passed}/{f_total} passed",
            "",
            "| Functionality | Test name | Score | Input | Expected output | Actual output | Time |",
            "|---|---|:---:|---|---|---|---:|",
        ]

        for r in recs:
            score     = _score_cell(r["status"])
            inp       = _md(r["input"])       or "—"
            expected  = _md(r["expected_output"]) or "—"
            actual    = _md(r["actual_output"])
            func      = _md(r["functionality"])
            tname     = _md(r["test_name"])
            duration  = f"{r['duration_ms']} ms"

            lines.append(
                f"| {func} | {tname} | {score} | {inp} | {expected} | {actual} | {duration} |"
            )

        lines += ["", "---", ""]

    return "\n".join(lines)


def _score_cell(status: str) -> str:
    if status == "PASSED":
        return "✅ 1/1"
    if status == "FAILED":
        return "❌ 0/1"
    return "⚠️ —/1"