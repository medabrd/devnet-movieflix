"""Build a self-contained HTML slide deck from slides.md (no external deps).

Usage: python build-slides.py
Outputs: slides.html (open in browser)
"""
from pathlib import Path
import html
import re

HERE = Path(__file__).parent
SRC = HERE / "slides.md"
OUT = HERE / "slides.html"

raw = SRC.read_text(encoding="utf-8")

# Strip Marp frontmatter
if raw.startswith("---"):
    end = raw.find("---", 3)
    raw = raw[end + 3:].lstrip()

# Split slides on --- separator (Marp convention)
slides_md = [s.strip() for s in raw.split("\n---\n") if s.strip()]


def md_to_html(text: str) -> str:
    """Tiny markdown subset: h1-h3, code blocks, inline code, bold, italic, lists, tables, pipes."""
    out_lines = []
    in_code = False
    in_table = False
    in_list = False
    code_buf = []
    table_buf = []

    for line in text.split("\n"):
        # Code fences
        if line.strip().startswith("```"):
            if in_code:
                escaped = html.escape("\n".join(code_buf))
                out_lines.append(f'<pre><code>{escaped}</code></pre>')
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append(line)
            continue

        # Tables (very basic)
        if "|" in line and line.strip().startswith("|"):
            table_buf.append(line)
            in_table = True
            continue
        if in_table and not line.strip().startswith("|"):
            out_lines.append(render_table(table_buf))
            table_buf = []
            in_table = False

        # Headings
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            level = len(m.group(1))
            content = inline(m.group(2))
            out_lines.append(f"<h{level}>{content}</h{level}>")
            continue

        # Lists
        if re.match(r"^\s*[-*]\s+", line):
            if not in_list:
                out_lines.append("<ul>")
                in_list = True
            content = inline(re.sub(r"^\s*[-*]\s+", "", line))
            out_lines.append(f"<li>{content}</li>")
            continue
        else:
            if in_list:
                out_lines.append("</ul>")
                in_list = False

        # Paragraphs / blank lines
        if line.strip() == "":
            out_lines.append("")
        else:
            out_lines.append(f"<p>{inline(line)}</p>")

    if in_list:
        out_lines.append("</ul>")
    if in_table and table_buf:
        out_lines.append(render_table(table_buf))

    return "\n".join(out_lines)


def render_table(rows: list[str]) -> str:
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    if len(cells) < 2:
        return ""
    # second row is separator (|---|---|)
    header = cells[0]
    body = cells[2:] if len(cells) > 2 else []
    th = "".join(f"<th>{inline(h)}</th>" for h in header)
    rows_html = ""
    for row in body:
        tds = "".join(f"<td>{inline(c)}</td>" for c in row)
        rows_html += f"<tr>{tds}</tr>"
    return f"<table><thead><tr>{th}</tr></thead><tbody>{rows_html}</tbody></table>"


def inline(text: str) -> str:
    # inline code
    text = re.sub(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>", text)
    # bold then italic
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


slides_html = "\n".join(
    f'<section class="slide"><div class="slide-inner">{md_to_html(s)}</div><div class="slide-num">{i+1} / {len(slides_md)}</div></section>'
    for i, s in enumerate(slides_md)
)

PAGE = """<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><title>MovieFlix — Slides de soutenance</title>
<style>
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #0f1115; color: #e6e6e6; font-family: -apple-system, "Segoe UI", Roboto, sans-serif; }
.deck { max-width: 1100px; margin: 0 auto; padding: 2rem 1rem; }
.slide { background: #1a1d24; border-radius: 12px; padding: 3rem; margin-bottom: 2rem; min-height: 70vh; position: relative; box-shadow: 0 6px 20px rgba(0,0,0,0.4); page-break-after: always; }
.slide-inner h1 { color: #e50914; font-size: 2.4rem; margin-top: 0; }
.slide-inner h2 { color: #e50914; font-size: 1.8rem; border-bottom: 2px solid #2a2d34; padding-bottom: 0.4rem; }
.slide-inner h3 { color: #ffd166; }
.slide-inner p { font-size: 1.05rem; line-height: 1.6; }
.slide-inner ul { line-height: 1.8; }
.slide-inner code { background: #0f1115; padding: 2px 6px; border-radius: 3px; color: #ffd166; font-size: 0.9em; }
.slide-inner pre { background: #0f1115; padding: 1rem; border-radius: 6px; overflow-x: auto; border-left: 3px solid #e50914; }
.slide-inner pre code { background: transparent; color: #e6e6e6; padding: 0; }
.slide-inner table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
.slide-inner th, .slide-inner td { padding: 0.5rem 0.8rem; border-bottom: 1px solid #2a2d34; text-align: left; }
.slide-inner th { background: #0f1115; color: #ffd166; }
.slide-inner strong { color: #ffffff; }
.slide-num { position: absolute; bottom: 1rem; right: 1.5rem; color: #555; font-size: 0.85rem; }
.toolbar { position: sticky; top: 0; background: #0f1115; padding: 0.8rem 1rem; border-bottom: 1px solid #2a2d34; z-index: 10; text-align: center; }
.toolbar button { background: #e50914; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; font-size: 0.95rem; margin: 0 4px; }
.toolbar button:hover { background: #b00710; }
@media print { .toolbar { display: none; } .slide { box-shadow: none; min-height: 95vh; } body { background: white; color: black; } .slide { background: white; color: black; } .slide-inner h2 { color: #b00710; border-color: #ccc; } .slide-inner pre { background: #f5f5f5; } }
</style></head><body>
<div class="toolbar">
<button onclick="window.print()">Imprimer / PDF</button>
<button onclick="document.documentElement.requestFullscreen()">Plein écran</button>
<span style="color:#888; margin-left:1rem;">Soutenance MovieFlix — Med Abroud &amp; Tesnime Chriaa</span>
</div>
<div class="deck">
__SLIDES__
</div>
</body></html>
""".replace("__SLIDES__", slides_html)

OUT.write_text(PAGE, encoding="utf-8")
print(f"OK: generated {OUT} ({len(slides_md)} slides, {OUT.stat().st_size} bytes)")
