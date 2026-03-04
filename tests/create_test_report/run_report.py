"""
run_report.py — run the full test suite and produce an HTML report
               generated from a Markdown intermediate.

Usage (from the project root):
    python tests/create_test_report/run_report.py
    python tests/create_test_report/run_report.py --out reports/sprint1.html
    python tests/create_test_report/run_report.py --md   # also save the .md file
    python tests/create_test_report/run_report.py --open # open in browser when done

Pipeline
--------
  .env.test loaded via python-dotenv (before pytest starts, not via CLI flag)
      pytest (in-process)
          ReportPlugin        collects one record dict per test
          build_markdown      renders records into a Markdown string
          markdown lib        converts Markdown to an HTML fragment
          HTML shell          wraps fragment in a styled page and writes to file
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import webbrowser
from pathlib import Path

# ── Resolve paths (before any local imports) ──────────────────────────────────

HERE         = Path(__file__).parent                  # tests/create_test_report/
TESTS_DIR    = HERE.parent                            # tests/
PROJECT_ROOT = TESTS_DIR.parent                       # project root
RESULTS_DIR  = TESTS_DIR / "results"                  # tests/results/

for p in (str(PROJECT_ROOT), str(TESTS_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

# ── Load .env.test before Settings is imported anywhere ───────────────────────
# Done here manually so pytest never sees --envfile, which is a pytest-dotenv
# CLI flag that is not registered when the plugin is absent.
from dotenv import load_dotenv  # noqa: E402

_env_file = PROJECT_ROOT / ".env.test"
if _env_file.exists():
    load_dotenv(_env_file, override=True)
else:
    print(f"Warning: .env.test not found at {_env_file} — using environment as-is.")

# ── Local imports (safe now that env vars are set) ────────────────────────────
import markdown as md_lib  # noqa: E402

from create_test_report.report_plugin   import ReportPlugin    # noqa: E402
from create_test_report.markdown_report import build_markdown  # noqa: E402


# ── HTML shell ────────────────────────────────────────────────────────────────

_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: #f0f2f5;
  color: #1a1a2e;
  padding: 2.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

h1 { font-size: 1.8rem; font-weight: 800; margin-bottom: 1.5rem; }
h2 { font-size: 1.2rem; font-weight: 700; margin: 2rem 0 .75rem;
     padding-bottom: .35rem; border-bottom: 2px solid #e5e7eb; }
h3 { font-size: .95rem; font-weight: 600; margin: 1.5rem 0 .5rem; color: #555; }
p  { line-height: 1.6; margin-bottom: .75rem; }
hr { border: none; border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }

table {
  border-collapse: collapse;
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,.07);
  font-size: .85rem;
  width: 100%;
  margin-bottom: 1rem;
}
th {
  background: #f8fafc;
  padding: .55rem .9rem;
  text-align: left;
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .06em;
  color: #888;
  border-bottom: 1px solid #e5e7eb;
}
td {
  padding: .6rem .9rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: top;
  line-height: 1.5;
  word-break: break-word;
}
tr:last-child td { border-bottom: none; }
tr:hover td { background: #fafafa; }

code {
  font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
  font-size: .82em;
  background: #f1f5f9;
  padding: .1em .35em;
  border-radius: 4px;
  color: #0f172a;
}

.filter-bar {
  display: flex;
  gap: .5rem;
  margin: 1rem 0 1.5rem;
  flex-wrap: wrap;
}
.filter-btn {
  padding: .35rem .85rem;
  border-radius: 6px;
  border: 1.5px solid #d1d5db;
  background: #fff;
  cursor: pointer;
  font-size: .8rem;
  font-weight: 500;
  color: #555;
  transition: all .15s;
}
.filter-btn:hover { border-color: #2563eb; color: #2563eb; }
.filter-btn.active { background: #2563eb; border-color: #2563eb; color: #fff; }

tr.hidden-row { display: none; }
"""

_JS = """
function filterRows(status) {
  document.querySelectorAll('.filter-btn').forEach(b => {
    b.classList.toggle('active', b.dataset.filter === status);
  });
  document.querySelectorAll('tr[data-status]').forEach(row => {
    row.classList.toggle('hidden-row', status !== 'ALL' && row.dataset.status !== status);
  });
}
"""


def _wrap_html(body_html, *, total, passed, failed, skipped):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Test Report</title>
  <style>{_CSS}</style>
</head>
<body>

<div class="filter-bar">
  <button class="filter-btn active" data-filter="ALL"
          onclick="filterRows('ALL')">All ({total})</button>
  <button class="filter-btn" data-filter="PASSED"
          onclick="filterRows('PASSED')">Passed ({passed})</button>
  <button class="filter-btn" data-filter="FAILED"
          onclick="filterRows('FAILED')">Failed ({failed})</button>
  <button class="filter-btn" data-filter="SKIPPED"
          onclick="filterRows('SKIPPED')">Skipped ({skipped})</button>
</div>

{body_html}

<script>{_JS}</script>
</body>
</html>"""


# ── Markdown to annotated HTML ────────────────────────────────────────────────

def _md_to_html(md_text):
    """
    Convert Markdown to an HTML fragment, then tag every data row with
    data-status so the JS filter can show/hide rows by result.
    """
    fragment = md_lib.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br"],
    )

    def _tag_row(m):
        row_html = m.group(0)
        if "PASSED" in row_html:
            return row_html.replace("<tr>", '<tr data-status="PASSED">', 1)
        if "FAILED" in row_html:
            return row_html.replace("<tr>", '<tr data-status="FAILED">', 1)
        if "SKIPPED" in row_html:
            return row_html.replace("<tr>", '<tr data-status="SKIPPED">', 1)
        return row_html

    return re.sub(r"<tr>.*?</tr>", _tag_row, fragment, flags=re.S)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Run tests and generate an HTML report via Markdown."
    )
    parser.add_argument(
        "--out",
        default=str(RESULTS_DIR / "test_report.html"),
        help="Output HTML file path (default: tests/results/test_report.html).",
    )
    parser.add_argument(
        "--md", action="store_true",
        help="Also save the intermediate Markdown file alongside the HTML.",
    )
    parser.add_argument(
        "--open", action="store_true",
        help="Open the HTML report in the default browser when done.",
    )
    args = parser.parse_args()

    import pytest

    plugin  = ReportPlugin()
    started = time.perf_counter()

    exit_code = pytest.main(
        [
            str(TESTS_DIR),
            "--tb=short",
            "-q",
            "--no-header",
            # No --envfile flag here — .env.test is already loaded above
        ],
        plugins=[plugin],
    )

    total_duration_ms = round((time.perf_counter() - started) * 1000)

    # Build Markdown
    md_text = build_markdown(plugin.records, total_duration_ms=total_duration_ms)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.md:
        md_path = out_path.with_suffix(".md")
        md_path.write_text(md_text, encoding="utf-8")
        print(f"Markdown saved to:      {md_path.resolve()}")

    # Convert to HTML
    body_fragment = _md_to_html(md_text)

    records = plugin.records
    total   = len(records)
    passed  = sum(1 for r in records if r["status"] == "PASSED")
    failed  = sum(1 for r in records if r["status"] == "FAILED")
    skipped = sum(1 for r in records if r["status"] == "SKIPPED")

    full_html = _wrap_html(
        body_fragment,
        total=total, passed=passed, failed=failed, skipped=skipped,
    )

    out_path.write_text(full_html, encoding="utf-8")
    print(f"HTML report written to: {out_path.resolve()}")

    if args.open:
        webbrowser.open(out_path.resolve().as_uri())

    sys.exit(0 if exit_code == 0 else 1)


if __name__ == "__main__":
    main()