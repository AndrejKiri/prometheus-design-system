#!/usr/bin/env python3
"""gen.py — docs site generator for the run2 Prometheus design system."""

import argparse
import html
import json
import shutil
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).parent
OUTPUT_DIR = PROJECT_DIR / "design-system"
SCREENSHOTS_SRC = PROJECT_DIR / "screenshots"
SCREENSHOTS_DEST = OUTPUT_DIR / "screenshots"
TOKENS_PATH = PROJECT_DIR / "tokens.json"
COMPONENTS_PATH = PROJECT_DIR / "components.json"
AUDIT_PATH = PROJECT_DIR / "audit-results.json"
CLAUDE_MD = PROJECT_DIR / "CLAUDE.md"

APP_NAME = "Prometheus Design System"
GITHUB_REPO_URL = "https://github.com/AndrejKiri/prometheus-design-system"


def load(p):
    with open(p) as f:
        return json.load(f)


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  wrote {path.relative_to(PROJECT_DIR)}")


def copy_screenshots():
    if SCREENSHOTS_SRC.exists():
        if SCREENSHOTS_DEST.exists():
            shutil.rmtree(SCREENSHOTS_DEST)
        shutil.copytree(SCREENSHOTS_SRC, SCREENSHOTS_DEST)
        n = sum(1 for _ in SCREENSHOTS_DEST.iterdir())
        print(f"  copied screenshots/ ({n} files)")


# ─── Shell ───────────────────────────────────────────────────────────────────

NAV = [
    ("Foundations", [
        ("index", "Home"),
        ("tokens", "Tokens"),
        ("icons", "Icons"),
    ]),
    ("Components", [
        ("components", "Components"),
        ("patterns", "Patterns"),
        ("action-items", "Action Items"),
    ]),
    ("Audit", [
        ("audit-report", "Audit Report"),
        ("inconsistencies", "Inconsistencies"),
        ("migration", "Migration"),
        ("figma", "Figma Plugin"),
        ("changelog", "Changelog"),
    ]),
]


def sidebar(active, prefix=""):
    sections_html = ""
    for heading, items in NAV:
        lis = ""
        for slug, label in items:
            cls = ' class="doc-nav-link active"' if slug == active else ' class="doc-nav-link"'
            href = f"{prefix}{slug}.html"
            lis += f'        <li><a{cls} href="{href}">{label}</a></li>\n'
        sections_html += (
            f'      <div class="doc-nav-section">\n'
            f'        <div class="doc-nav-label">{heading}</div>\n'
            f'        <ul>\n{lis}        </ul>\n'
            f'      </div>\n'
        )
    return (
        '<aside class="doc-sidebar" id="doc-sidebar">\n'
        '  <nav class="doc-sidebar-nav" aria-label="Docs navigation">\n'
        f'{sections_html}'
        '  </nav>\n'
        '</aside>'
    )


def topbar(prefix=""):
    return f'''<header class="doc-topbar">
  <button class="doc-topbar-burger" id="doc-burger" aria-label="Toggle sidebar">☰</button>
  <a class="doc-topbar-title" href="{prefix}index.html">{APP_NAME}</a>
  <div class="doc-topbar-spacer"></div>
  <button class="doc-topbar-theme" id="doc-theme-toggle" aria-label="Toggle theme">◐</button>
</header>'''


def page(title, active, body, prefix=""):
    css_href = f"{prefix}styles.css"
    js_href = f"{prefix}main.js"
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(title)} — {APP_NAME}</title>
  <link rel="stylesheet" href="{css_href}">
</head>
<body>
  {topbar(prefix)}
  <div class="doc-sidebar-overlay" id="doc-sidebar-overlay"></div>
  {sidebar(active, prefix)}
  <main class="doc-content">
{body}
  </main>
  <script src="{js_href}"></script>
</body>
</html>
'''


# ─── Pages ──────────────────────────────────────────────────────────────────


def gen_index(tokens, components, audit):
    page_count = len(audit.get("pages_audited", []))
    inc_count = len(audit.get("inconsistencies", []))
    comp_count = len(components.get("components", []))
    ai_count = len(components.get("action_items", []))
    token_count = (
        len(tokens["colors"]["brand"]) + len(tokens["colors"]["status"])
        + len(tokens["colors"]["surface"]) + len(tokens["colors"]["text"])
        + len(tokens["spacing"]["scale"]) + len(tokens["typography"]["styles"])
        + len(tokens["border_radius"])
    )
    version = audit.get("audit_date", "2026-04-24")

    cards = [
        ("tokens", "Foundations", "Tokens",
         f"{token_count} tokens covering color, spacing, typography, and elevation."),
        ("components", "Components", "Components",
         f"{comp_count} components with variants, do/don't, and layout specs."),
        ("action-items", "Components", "Action Items",
         f"{ai_count} PR-style tasks grouped by priority and effort."),
        ("audit-report", "Audit", "Audit Report",
         f"{page_count} pages audited, {inc_count} inconsistencies."),
        ("figma", "Audit", "Figma Plugin",
         "Bootstrap variables + text styles in Figma from tokens.json."),
    ]
    card_html = "\n".join(
        f'      <a class="doc-card-link" href="{slug}.html">'
        f'<span class="tag card-tag">{cat}</span>'
        f'<h3>{label}</h3>'
        f'<p>{html.escape(desc)}</p></a>'
        for slug, cat, label, desc in cards
    )

    source_repo = "https://github.com/prometheus/prometheus"
    body = f'''    <h1>{APP_NAME}
      <span class="version-chip">v{version}</span>
    </h1>
    <p class="doc-subtitle">An auto-extracted design system for the Prometheus v3 web UI.</p>

    <aside class="callout callout-wip">
      <strong>Work in progress.</strong> This design system was extracted programmatically from the live application. Some values (breakpoints, motion) are inferred from Mantine defaults rather than measured, and the source-code mapping is best-effort.
    </aside>

    <section class="doc-card-grid">
{card_html}
    </section>

    <section class="acknowledgements">
      <h2>Acknowledgements</h2>
      <p>The audited application is the <a href="{audit.get('app_url','')}">Prometheus v3 web UI</a> — a demo deployment of the <a href="{source_repo}">open-source Prometheus project</a>. It is built on <a href="https://mantine.dev/">Mantine v7</a> with highlight.js for syntax highlighting.</p>
      <p>This docs site was generated by the <code>design-system-extraction-code</code> skill from a visual-audit handoff produced by the <code>design-system-extraction-cowork</code> skill.</p>
    </section>
'''
    write(OUTPUT_DIR / "index.html", page("Home", "index", body))


def gen_tokens_page(tokens):
    def swatch(name, value, usage=""):
        bg = value if value.startswith(("rgb", "#")) else "transparent"
        return (
            f'<div class="swatch"><div class="swatch-color" style="background:{bg}"></div>'
            f'<div class="swatch-info"><div class="swatch-name">{html.escape(name)}</div>'
            f'<div class="swatch-value">{html.escape(value)}</div>'
            + (f'<div class="swatch-usage">{html.escape(usage)}</div>' if usage else '')
            + '</div></div>'
        )

    # Build CSS var mapping
    css_rows = []

    # Brand
    brand_html = ""
    for c in tokens["colors"]["brand"]:
        brand_html += swatch(c["name"], c["value"], c.get("usage", "")) + "\n"
        css_rows.append((f"--doc-{c['name']}", c["value"], c.get("usage", "")))

    # Status
    status_html = ""
    for s in tokens["colors"]["status"]:
        name = s["name"]
        l = s["light"]
        d = s.get("dark", {})
        status_html += (
            f'<div class="status-card">'
            f'<div class="status-title">{html.escape(name)}</div>'
            f'<div class="status-swatches">'
            f'<div class="status-swatch" style="background:{l["bg"]};color:{l["text"]};border:1px solid {l["border"] if l["border"]!="transparent" else "transparent"}">{name} · light</div>'
            + (f'<div class="status-swatch" style="background:{d.get("bg","")};color:{d.get("text","")};border:1px solid {d.get("border","transparent") if d.get("border","transparent")!="transparent" else "transparent"}">{name} · dark</div>' if d else '')
            + '</div></div>\n'
        )
        css_rows.append((f"--doc-status-{name}-bg", l["bg"], "status bg (light)"))
        css_rows.append((f"--doc-status-{name}-text", l["text"], "status text (light)"))

    # Surface
    surface_html = "".join(swatch(s["name"], s["light"], f"dark: {s.get('dark','')}") + "\n" for s in tokens["colors"]["surface"])
    for s in tokens["colors"]["surface"]:
        css_rows.append((f"--doc-surface-{s['name']}", s["light"], "surface (light)"))

    # Text
    text_html = "".join(swatch(t["name"], t["light"], f"dark: {t.get('dark','')}") + "\n" for t in tokens["colors"]["text"])
    for t in tokens["colors"]["text"]:
        css_rows.append((f"--doc-text-{t['name']}", t["light"], "text (light)"))

    # Border
    border_html = "".join(swatch(b["name"], b["light"], f"dark: {b.get('dark','')}") + "\n" for b in tokens["colors"]["border"])
    for b in tokens["colors"]["border"]:
        css_rows.append((f"--doc-border-{b['name']}", b["light"], "border (light)"))

    # Spacing scale
    spacing_html = ""
    for s in tokens["spacing"]["scale"]:
        spacing_html += (
            f'<div class="spacing-row">'
            f'<div class="spacing-preview" style="width:{s["value_px"]}px"></div>'
            f'<div class="spacing-name">{html.escape(s["name"])}</div>'
            f'<div class="spacing-value">{s["value_px"]}px</div>'
            f'</div>\n'
        )
        css_rows.append((f"--doc-spacing-{s['name']}", f"{s['value_px']}px", "spacing scale"))

    # Layout
    layout_rows = ""
    for l in tokens["spacing"].get("layout", []):
        layout_rows += f'<tr><td><code>{html.escape(l["name"])}</code></td><td>{l["value_px"]}px</td></tr>\n'
        css_rows.append((f"--doc-layout-{l['name']}", f"{l['value_px']}px", "layout"))

    # Typography styles
    type_html = ""
    for t in tokens["typography"]["styles"]:
        type_html += (
            f'<div class="type-row">'
            f'<div class="type-preview" style="font-size:{t["size_px"]}px;font-weight:{t["weight"]};line-height:{t["line_height"]}">'
            f'The quick brown fox</div>'
            f'<div class="type-meta">'
            f'<div class="type-name">{html.escape(t["name"])}</div>'
            f'<div class="type-specs">{t["size_px"]}px · {t["weight"]} · lh {t["line_height"]}</div>'
            f'</div></div>\n'
        )

    # Families
    fam_html = ""
    for f in tokens["typography"]["families"]:
        fam_html += f'<div class="family-row"><strong>{html.escape(f["name"])}</strong> — <code>{html.escape(f["family"])}</code><br><span class="family-usage">{html.escape(f["usage"])}</span></div>\n'

    # Radius
    rad_html = ""
    for r in tokens["border_radius"]:
        rad_html += (
            f'<div class="radius-row">'
            f'<div class="radius-preview" style="border-radius:{r["value_px"]}px"></div>'
            f'<div class="radius-name">{html.escape(r["name"])}</div>'
            f'<div class="radius-value">{r["value_px"]}px</div>'
            f'</div>\n'
        )
        css_rows.append((f"--doc-radius-{r['name']}", f"{r['value_px']}px", "border radius"))

    # Elevation
    elev_html = ""
    for e in tokens.get("elevation", []):
        elev_html += (
            f'<div class="elev-row">'
            f'<div class="elev-preview" style="box-shadow:{e["light"]["css"]}"></div>'
            f'<div class="elev-meta"><strong>{html.escape(e["name"])}</strong><br><code>{html.escape(e["light"]["css"])}</code></div>'
            f'</div>\n'
        )
        css_rows.append((f"--doc-shadow-{e['name']}", e["light"]["css"], "elevation"))

    # Breakpoints + motion
    bp_rows = "".join(
        f'<tr><td><code>{html.escape(b["name"])}</code></td><td>{b["value_px"]}px</td></tr>\n'
        for b in tokens.get("breakpoints", [])
    )
    motion = tokens.get("motion", {})
    motion_html = ""
    if motion:
        dur_rows = "".join(
            f'<tr><td><code>{html.escape(d["name"])}</code></td><td>{d["value_ms"]}ms</td></tr>\n'
            for d in motion.get("durations", [])
        )
        ease_rows = "".join(
            f'<tr><td><code>{html.escape(e["name"])}</code></td><td><code>{html.escape(e["value"])}</code></td></tr>\n'
            for e in motion.get("easings", [])
        )
        motion_html = (
            '<h3>Durations</h3><table><thead><tr><th>Token</th><th>Value</th></tr></thead><tbody>'
            f'{dur_rows}</tbody></table>'
            '<h3>Easings</h3><table><thead><tr><th>Token</th><th>Curve</th></tr></thead><tbody>'
            f'{ease_rows}</tbody></table>'
        )

    # CSS variable table
    css_var_rows = "".join(
        f'<tr><td><code>{html.escape(n)}</code></td><td><code>{html.escape(v)}</code></td><td>{html.escape(u)}</td></tr>\n'
        for n, v, u in css_rows
    )

    # Domain lexicon
    lex_rows = "".join(
        f'<tr><td><strong>{html.escape(l["term"])}</strong></td>'
        f'<td>{html.escape(l["definition"])}</td>'
        f'<td><code>{html.escape(l.get("ui_surface",""))}</code></td></tr>\n'
        for l in tokens.get("domain_lexicon", [])
    )

    # Gaps
    gaps = tokens.get("gaps", [])
    gaps_html = ""
    if gaps:
        gap_items = "".join(
            f'<li><strong>{html.escape(g["type"])}</strong>'
            + (f' — <code>{html.escape(g.get("token") or g.get("page") or "")}</code>' if (g.get("token") or g.get("page")) else "")
            + f' — {html.escape(g["reason"])}</li>\n'
            for g in gaps
        )
        gaps_html = f'<h2>Known gaps</h2><ul class="gap-list">{gap_items}</ul>'

    body = f'''    <h1>Tokens</h1>
    <p class="doc-subtitle">All design tokens extracted from the Prometheus v3 web UI.</p>

    <h2 id="brand">Brand</h2>
    <div class="swatch-grid">
{brand_html}
    </div>

    <h2 id="status">Status</h2>
    <div class="status-grid">
{status_html}
    </div>

    <h2 id="surface">Surface</h2>
    <div class="swatch-grid">
{surface_html}
    </div>

    <h2 id="text">Text</h2>
    <div class="swatch-grid">
{text_html}
    </div>

    <h2 id="border">Border</h2>
    <div class="swatch-grid">
{border_html}
    </div>

    <h2 id="spacing">Spacing</h2>
    <div class="spacing-grid">
{spacing_html}
    </div>
    <h3>Layout semantics</h3>
    <table><thead><tr><th>Token</th><th>Value</th></tr></thead><tbody>{layout_rows}</tbody></table>

    <h2 id="typography">Typography</h2>
    <h3>Families</h3>
    {fam_html}
    <h3>Styles</h3>
    <div class="type-grid">
{type_html}
    </div>

    <h2 id="radius">Border radius</h2>
    <div class="radius-grid">
{rad_html}
    </div>

    <h2 id="elevation">Elevation</h2>
    <div class="elev-grid">
{elev_html}
    </div>

    <h2 id="breakpoints">Breakpoints</h2>
    <table><thead><tr><th>Token</th><th>Min width</th></tr></thead><tbody>{bp_rows}</tbody></table>

    <h2 id="motion">Motion</h2>
    {motion_html}

    <h2 id="css-vars">CSS custom properties</h2>
    <p>Copy these into your stylesheet. All tokens are prefixed with <code>--doc-</code>.</p>
    <table class="css-var-table">
      <thead><tr><th>Variable</th><th>Value</th><th>Usage</th></tr></thead>
      <tbody>
{css_var_rows}      </tbody>
    </table>

    <h2 id="lexicon">Domain lexicon</h2>
    <table>
      <thead><tr><th>Term</th><th>Definition</th><th>UI surface</th></tr></thead>
      <tbody>
{lex_rows}      </tbody>
    </table>

    {gaps_html}
'''
    write(OUTPUT_DIR / "tokens.html", page("Tokens", "tokens", body))


def gen_icons_page(tokens):
    icons = tokens.get("icons", {})
    lib = icons.get("library", "Tabler Icons")
    ver = icons.get("default_size_px", 18)
    items = icons.get("icons", [])

    if not items:
        body = f'''    <h1>Icons</h1>
    <p class="doc-subtitle">No icon inventory captured.</p>
    <p>The audit did not enumerate icons separately. See <a href="tokens.html#brand">Tokens</a> for references to the Tabler icons used as Card Title glyphs.</p>
'''
    else:
        groups = {"navigation": [], "status": [], "action": [], "chart": [], "decorative": []}
        classify = {
            "sun": "navigation", "moon": "navigation", "menu": "navigation", "book": "navigation",
            "settings": "navigation", "bell": "status", "bell-off": "status", "circle-info": "status",
            "chevron-up": "action", "chevron-down": "action", "clipboard": "action", "search": "action",
            "database": "decorative", "run": "decorative",
        }
        for ic in items:
            group = classify.get(ic["name"], "decorative")
            groups[group].append(ic)

        grid_html = ""
        for gname, gitems in groups.items():
            if not gitems:
                continue
            grid_html += f'<h3>{gname.title()}</h3><div class="icon-grid">'
            for ic in gitems:
                grid_html += (
                    f'<div class="icon-card">'
                    f'<div class="icon-preview">✦</div>'
                    f'<div class="icon-name"><code>{html.escape(ic["name"])}</code></div>'
                    f'<div class="icon-usage">{html.escape(ic["usage"])}</div>'
                    f'<div class="icon-import"><code>import {{ Icon{"".join(p.title() for p in ic["name"].split("-"))} }} from \'@tabler/icons-react\';</code></div>'
                    f'</div>'
                )
            grid_html += '</div>'

        body = f'''    <h1>Icons</h1>
    <p class="doc-subtitle">{lib} — default size {ver}px.</p>
    <input type="search" class="icon-search" id="icon-search" placeholder="Filter icons…">
{grid_html}
'''
    write(OUTPUT_DIR / "icons.html", page("Icons", "icons", body))


def gen_components_page(components):
    comps = components.get("components", [])
    order = {"complex": 0, "medium": 1, "simple": 2}
    sorted_comps = sorted(comps, key=lambda c: (order.get(c.get("complexity", "simple"), 2), c.get("name", "")))
    categories = {}
    for c in sorted_comps:
        categories.setdefault(c.get("category", "other"), []).append(c)

    sections = ""
    for cat, items in sorted(categories.items()):
        cards = ""
        for c in items:
            cards += (
                f'<a class="doc-card-link" href="components/{c["slug"]}.html">'
                f'<span class="tag tag-{c["complexity"]}">{c["complexity"]}</span>'
                f'<h3>{html.escape(c["name"])}</h3>'
                f'<p>{html.escape(c["description"][:140])}{"…" if len(c["description"]) > 140 else ""}</p>'
                f'</a>\n'
            )
        sections += f'<h2>{cat.title()}</h2><div class="doc-card-grid">{cards}</div>\n'

    body = f'''    <h1>Components</h1>
    <p class="doc-subtitle">{len(comps)} components derived from the Prometheus v3 web UI. Grouped by category; complex components first.</p>
{sections}
'''
    write(OUTPUT_DIR / "components.html", page("Components", "components", body))

    for c in comps:
        gen_component_page(c)


def gen_component_page(c):
    slug = c["slug"]
    name = c["name"]
    desc = c["description"]

    # Do/Don't grid
    dos = [d for d in c.get("dos_and_donts", []) if d["type"] == "do"]
    donts = [d for d in c.get("dos_and_donts", []) if d["type"] == "dont"]

    def dd_html(items, kind):
        out = ""
        for d in items:
            out += (
                f'<div class="{kind}-item">'
                f'<strong>{"DO" if kind == "do" else "DON\'T"}</strong>'
                f'<p>{html.escape(d["text"])}</p>'
                f'</div>'
            )
        return out

    dd_grid = f'<div class="do-dont-grid">{dd_html(dos, "do")}{dd_html(donts, "dont")}</div>'

    # Design (mock variants)
    design_html = ""
    for v in c.get("variants", []):
        design_html += (
            f'<div class="variant-block">'
            f'<h3>{html.escape(v["name"])}</h3>'
            f'<div class="mock-preview">{v.get("mock_html", "")}</div>'
            f'<p class="variant-desc">{html.escape(v["description"])}</p>'
            f'</div>\n'
        )

    # Layout specs
    specs = c.get("layout", {}).get("specs", [])
    spec_rows = ""
    for s in specs:
        tok = f' <code>{html.escape(s["token"])}</code>' if s.get("token") else ""
        spec_rows += f'<tr><td>{html.escape(s["property"])}</td><td><code>{html.escape(s["value"])}</code>{tok}</td></tr>\n'

    # Component Reference (screenshots)
    pages = c.get("pages", [])
    refs = ""
    if pages:
        img_list = ""
        for p in pages:
            # map page url to screenshot filename
            stub = p.strip("/").replace("/", "-") or "index"
            img_list += f'<div class="ref-img"><figcaption>{html.escape(p)}</figcaption><img src="../screenshots/{stub}-light.jpg" alt="{html.escape(p)} light" loading="lazy" onerror="this.style.display=\'none\'"></div>'
        refs = (
            '<details class="ref-details"><summary>Component reference (screenshots)</summary>'
            f'<div class="ref-grid">{img_list}</div>'
            '<p class="ref-note">Placeholder screenshots — the audited app is live at <a href="https://prometheus-e83j.onrender.com" target="_blank">prometheus-e83j.onrender.com</a>.</p>'
            '</details>'
        )

    # Accessibility
    a = c.get("accessibility", {})
    a_rows = ""
    for key, label in [("aria_labels", "ARIA"), ("keyboard", "Keyboard"), ("contrast", "Contrast"), ("screen_reader", "Screen reader")]:
        if a.get(key):
            a_rows += f'<tr><td>{label}</td><td>{html.escape(a[key])}</td></tr>'

    related_incs = c.get("related_inconsistencies", [])
    rel_html = ""
    if related_incs:
        rel_html = (
            '<h2 id="inconsistencies">Related inconsistencies</h2><ul class="rel-inc">'
            + "".join(f'<li><a href="../inconsistencies.html#{i.lower()}">{i}</a></li>' for i in related_incs)
            + '</ul>'
        )

    body = f'''    <h1 id="top">{html.escape(name)}</h1>
    <p class="doc-subtitle">{html.escape(desc)}</p>
    {dd_grid}

    <h2 id="design">Design</h2>
{design_html}

    {refs}

    <h2 id="implementation">Implementation</h2>
    <pre><code>{html.escape(c.get("code_example", "// no example provided"))}</code></pre>

    <h2 id="layout">Layout</h2>
    <table class="spec-table"><thead><tr><th>Property</th><th>Value</th></tr></thead><tbody>
{spec_rows}    </tbody></table>

    <h2 id="accessibility">Accessibility</h2>
    <table class="a11y-table"><tbody>{a_rows}</tbody></table>

    {rel_html}
'''
    write(OUTPUT_DIR / "components" / f"{slug}.html", page(name, "components", body, prefix="../"))


def gen_patterns_page(audit):
    pats = audit.get("patterns", [])
    rows = ""
    for p in pats:
        pages = ", ".join(p.get("pages", []))
        rows += (
            f'<tr>'
            f'<td><strong>{html.escape(p["name"])}</strong></td>'
            f'<td><span class="tag">{html.escape(p.get("category",""))}</span></td>'
            f'<td>{p.get("instance_count",0)}</td>'
            f'<td>{p.get("variation_count",0)}</td>'
            f'<td>{html.escape(p.get("description","")[:160])}{"…" if len(p.get("description",""))>160 else ""}</td>'
            f'<td><code>{html.escape(pages[:80])}{"…" if len(pages)>80 else ""}</code></td>'
            f'</tr>\n'
        )
    body = f'''    <h1>Patterns</h1>
    <p class="doc-subtitle">{len(pats)} UI patterns cataloged during the visual audit.</p>
    <table class="patterns-table">
      <thead><tr><th>Pattern</th><th>Category</th><th>Instances</th><th>Variations</th><th>Description</th><th>Pages</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
'''
    write(OUTPUT_DIR / "patterns.html", page("Patterns", "patterns", body))


def gen_action_items_page(components):
    items = components.get("action_items", [])

    def esc(s):
        return html.escape(s or "")

    cards_by_priority = {"p0-critical": [], "p1-high": [], "p2-medium": [], "p3-low": []}
    for it in items:
        cards_by_priority.setdefault(it["priority"], []).append(it)

    sections = ""
    for pri, label in [("p1-high", "High priority"), ("p2-medium", "Medium priority"), ("p3-low", "Low priority")]:
        bucket = cards_by_priority.get(pri, [])
        if not bucket:
            continue
        cards_html = ""
        for it in bucket:
            labels_html = " ".join(f'<span class="tag">{esc(l)}</span>' for l in it.get("labels", []))
            rel = f'<a class="rel-inc-link" href="inconsistencies.html#{esc(it["related_inconsistency"].lower())}">{esc(it["related_inconsistency"])}</a>' if it.get("related_inconsistency") else ""
            ba = it.get("before_after") or {}
            before = esc(ba.get("before_html", "")) if ba else ""
            after = esc(ba.get("after_html", "")) if ba else ""
            ba_html = ""
            if before or after:
                ba_html = (
                    '<div class="action-card-before-after">'
                    f'<div class="action-card-before"><h4>Before</h4><pre><code>{before}</code></pre></div>'
                    f'<div class="action-card-after"><h4>After</h4><pre><code>{after}</code></pre></div>'
                    '</div>'
                )
            files = it.get("files_changed", [])
            files_html = ""
            if files:
                files_html = (
                    '<details class="files-changed"><summary>Files</summary><ul>'
                    + "".join(f'<li><code>{esc(f)}</code></li>' for f in files)
                    + '</ul></details>'
                )
            issue_title = esc(it.get("github_issue_title") or it["title"])
            issue_link = (
                f'<a class="issue-link" target="_blank" rel="noopener" '
                f'href="{GITHUB_REPO_URL}/issues/new?title={issue_title}&labels={",".join(it.get("labels", []))}">'
                f'Open issue</a>'
            ) if GITHUB_REPO_URL else ""
            cards_html += f'''
<article class="action-card" data-priority="{esc(it["priority"])}" id="{esc(it["id"])}">
  <header class="action-card-header">
    <span class="tag tag-priority {esc(it["priority"].split("-")[0])}">{esc(it["priority"])}</span>
    <span class="tag tag-effort">{esc(it["effort"])}</span>
    <span class="action-card-id">{esc(it["id"])}</span>
    <span class="action-card-title">{esc(it["title"])}</span>
    {labels_html}
    {rel}
    {issue_link}
  </header>
  <div class="action-card-body">
    <p>{esc(it["description"])}</p>
    {ba_html}
    {files_html}
  </div>
</article>
'''
        sections += f'<h2 id="{pri}">{label} <span class="count">{len(bucket)}</span></h2>{cards_html}'

    body = f'''    <h1>Action Items</h1>
    <p class="doc-subtitle">{len(items)} PR-style tasks. Priority and effort are set during extraction; refine as needed when triaging.</p>
{sections}
'''
    write(OUTPUT_DIR / "action-items.html", page("Action Items", "action-items", body))


def gen_audit_report_page(audit):
    pages = audit.get("pages_audited", [])
    row = ""
    for p in pages:
        extra = ""
        if p.get("additional_screenshots"):
            extra = f' <span class="count">+{len(p["additional_screenshots"])}</span>'
        elements = ", ".join(p.get("elements", []))
        row += (
            f'<tr>'
            f'<td><strong>{html.escape(p["name"])}</strong><br><code>{html.escape(p["url"])}</code></td>'
            f'<td>{"yes" if p.get("has_data") else "empty state"}</td>'
            f'<td>{len(p.get("elements", []))}{extra}</td>'
            f'<td>{html.escape(p.get("notes", ""))}</td>'
            f'</tr>\n'
        )

    scope = audit.get("scope", {})
    tech = audit.get("tech_stack", {})
    obs = audit.get("raw_observations", {})

    body = f'''    <h1>Audit Report</h1>
    <p class="doc-subtitle">Full visual audit conducted {audit.get("audit_date","")} via the <code>design-system-extraction-cowork</code> skill.</p>

    <section class="audit-meta">
      <h2>Scope</h2>
      <table>
        <tr><td>App URL</td><td><a href="{html.escape(audit.get("app_url",""))}">{html.escape(audit.get("app_url",""))}</a></td></tr>
        <tr><td>Source repo</td><td><a href="{html.escape(audit.get("source_repo",""))}">{html.escape(audit.get("source_repo",""))}</a></td></tr>
        <tr><td>Tool</td><td><code>{html.escape(audit.get("tool",""))}</code></td></tr>
        <tr><td>Tier</td><td><code>{html.escape(scope.get("tier",""))}</code></td></tr>
        <tr><td>Routes discovered</td><td>{scope.get("total_routes_discovered","?")}</td></tr>
        <tr><td>Routes audited</td><td>{scope.get("routes_audited","?")}</td></tr>
        <tr><td>Dark mode</td><td>{"yes" if obs.get("has_dark_mode") else "no"}</td></tr>
      </table>

      <h2>Tech stack</h2>
      <table>
        <tr><td>Framework</td><td>{html.escape(tech.get("framework",""))}</td></tr>
        <tr><td>UI library</td><td>{html.escape(tech.get("ui_library",""))}</td></tr>
        <tr><td>CSS approach</td><td>{html.escape(tech.get("css_approach",""))}</td></tr>
        <tr><td>Theming</td><td>{html.escape(obs.get("theming_approach",""))}</td></tr>
      </table>
    </section>

    <h2>Pages audited</h2>
    <table class="audit-pages-table">
      <thead><tr><th>Page</th><th>Has data</th><th>Elements</th><th>Notes</th></tr></thead>
      <tbody>
{row}      </tbody>
    </table>

    <h2>Limitations</h2>
    <div class="callout callout-warn">
      <p>{html.escape(obs.get("screenshot_limitations", "none reported"))}</p>
    </div>
'''
    write(OUTPUT_DIR / "audit-report.html", page("Audit Report", "audit-report", body))


def gen_inconsistencies_page(audit):
    incs = audit.get("inconsistencies", [])
    items = ""
    for inc in incs:
        sev = inc.get("severity", "minor")
        variants = inc.get("variants", [])
        variant_rows = "".join(
            f'<tr><td><code>{html.escape(v["page"])}</code></td><td>{html.escape(v.get("implementation",""))}</td></tr>'
            for v in variants
        )
        items += f'''
<article class="inc-item severity-{html.escape(sev)}" id="{html.escape(inc["id"].lower())}">
  <div class="inc-header">
    <span class="inc-id">{html.escape(inc["id"])}</span>
    <span class="tag tag-severity-{html.escape(sev)}">{html.escape(sev)}</span>
    <span class="tag">{html.escape(inc.get("type",""))}</span>
    <h3 class="inc-title">{html.escape(inc["title"])}</h3>
  </div>
  <div class="inc-body">
    <div class="inc-canonical"><strong>Canonical:</strong> {html.escape(inc.get("canonical",""))}</div>
    <p class="inc-reasoning"><strong>Why:</strong> {html.escape(inc.get("reasoning",""))}</p>
    <p class="inc-fix"><strong>Fix:</strong> {html.escape(inc.get("fix",""))}</p>
    <details><summary>Variants across pages</summary>
      <table><thead><tr><th>Page</th><th>Implementation</th></tr></thead><tbody>{variant_rows}</tbody></table>
    </details>
  </div>
</article>
'''
    body = f'''    <h1>Inconsistencies</h1>
    <p class="doc-subtitle">{len(incs)} inconsistencies identified during the visual audit. Each carries a canonical decision and a concrete fix.</p>
{items}
'''
    write(OUTPUT_DIR / "inconsistencies.html", page("Inconsistencies", "inconsistencies", body))


def gen_migration_page(components):
    items = components.get("action_items", [])
    buckets = {
        "Tokenization": [it for it in items if "tokens" in it.get("labels", [])],
        "Component unification": [it for it in items if "component" in it.get("labels", []) and "accessibility" not in it.get("labels", [])],
        "Accessibility": [it for it in items if "accessibility" in it.get("labels", [])],
    }
    sections = ""
    for phase_no, (label, bucket) in enumerate(buckets.items(), start=1):
        if not bucket:
            continue
        li = "".join(
            f'<li><a href="action-items.html#{html.escape(it["id"])}">{html.escape(it["id"])}</a> — {html.escape(it["title"])} <span class="tag tag-effort">{html.escape(it["effort"])}</span></li>'
            for it in bucket
        )
        sections += (
            f'<h2>Phase {phase_no}. {label}</h2>'
            f'<p>{len(bucket)} action item(s). Start here before moving to the next phase.</p>'
            f'<ol class="migration-list">{li}</ol>'
        )

    body = f'''    <h1>Migration Guide</h1>
    <p class="doc-subtitle">A suggested order for rolling these changes into the Prometheus web UI. Each phase is independently shippable.</p>
    <aside class="callout callout-info">Work through phases top-down. Tokenization is the biggest multiplier — once tokens exist in CSS, subsequent component fixes land as one-line changes.</aside>
{sections}
    <h2>After the migration</h2>
    <ul>
      <li>Publish <code>tokens.css</code> alongside the Mantine theme — a downstream consumer can then match your visual identity without reverse-engineering the UI.</li>
      <li>Re-run the <code>design-system-extraction-code</code> skill to regenerate this docs site and confirm the inconsistencies drop off.</li>
    </ul>
'''
    write(OUTPUT_DIR / "migration.html", page("Migration", "migration", body))


def gen_figma_page():
    body = f'''    <h1>Figma Plugin</h1>
    <p class="doc-subtitle">Bootstrap variable collections and text styles in Figma from <code>tokens.json</code>.</p>

    <h2>Installation</h2>
    <ol>
      <li>Download <a href="figma-plugin.zip">figma-plugin.zip</a> and unzip.</li>
      <li>In Figma: <strong>Plugins → Development → Import plugin from manifest…</strong></li>
      <li>Select <code>manifest.json</code> inside the unzipped folder.</li>
      <li>Run <strong>Plugins → Development → {APP_NAME}</strong> in any Figma file.</li>
    </ol>

    <h2>What it creates</h2>
    <ul>
      <li>Variable collections: <strong>Brand</strong>, <strong>Spacing</strong>, <strong>Radius</strong>, <strong>Status Colors</strong>, <strong>Surface</strong>, <strong>Text</strong>.</li>
      <li>Text styles: <code>heading/page</code>, <code>heading/card-title</code>, <code>body/default</code>, <code>code/block</code>, …</li>
      <li>Elevation effect styles from the <code>elevation</code> tokens.</li>
    </ul>

    <h2>Font fallbacks</h2>
    <p>The plugin tries the requested Figma family first, falls back to the same family + Regular weight, then to Inter + the requested weight, then Inter Regular. This survives the common case where only <code>Inter Regular</code> is shipped with Figma.</p>

    <h2>Troubleshooting</h2>
    <ul>
      <li><strong>Crashes on monospace</strong> — replace any <code>Roboto Mono</code> / <code>DejaVu Sans Mono</code> references in <code>code.js</code> with <code>Courier New</code>.</li>
      <li><strong>Nothing visible in Figma</strong> — open <code>Plugins → Development → Open Console</code> and look for <code>[DS]</code> log lines indicating where the plugin stopped.</li>
    </ul>
'''
    write(OUTPUT_DIR / "figma.html", page("Figma Plugin", "figma", body))


def gen_changelog_page(audit):
    body = f'''    <h1>Changelog</h1>
    <p class="doc-subtitle">Generated design-system releases for the Prometheus v3 web UI.</p>

    <section class="changelog-entry">
      <h2>v{audit.get("audit_date","2026-04-24")} — run2</h2>
      <ul>
        <li>Fresh extraction from the same audit corpus as run1.</li>
        <li>Token model expanded: added <code>breakpoints</code>, <code>motion</code>, and a <code>domain_lexicon</code> term list.</li>
        <li>Component catalog grown to {len(audit.get("patterns", []))} patterns with 31 component pages.</li>
        <li>Action items reorganized into high/medium/low priority buckets with before/after snippets.</li>
        <li>Migration guide added grouping actions into a three-phase rollout.</li>
      </ul>
    </section>

    <section class="changelog-entry">
      <h2>v2026-04-22 — run1</h2>
      <ul>
        <li>Initial extraction from the Prometheus v3 web UI.</li>
        <li>18 components, 9 action items, Figma plugin v1.</li>
      </ul>
    </section>
'''
    write(OUTPUT_DIR / "changelog.html", page("Changelog", "changelog", body))


# ─── Styles & JS ────────────────────────────────────────────────────────────


def gen_styles():
    css = CSS
    write(OUTPUT_DIR / "styles.css", css)


def gen_main_js():
    write(OUTPUT_DIR / "main.js", MAIN_JS)


def gen_readme():
    write(OUTPUT_DIR / "README.md", README_MD)


# ─── Orchestration ──────────────────────────────────────────────────────────


def generate():
    print("Generating design system docs site…")
    tokens = load(TOKENS_PATH)
    components = load(COMPONENTS_PATH)
    audit = load(AUDIT_PATH)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    copy_screenshots()
    gen_styles()
    gen_main_js()
    gen_index(tokens, components, audit)
    gen_tokens_page(tokens)
    gen_icons_page(tokens)
    gen_components_page(components)
    gen_patterns_page(audit)
    gen_action_items_page(components)
    gen_audit_report_page(audit)
    gen_inconsistencies_page(audit)
    gen_migration_page(components)
    gen_figma_page()
    gen_changelog_page(audit)
    gen_readme()
    print("Done.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--watch", action="store_true")
    args = parser.parse_args()
    generate()
    if args.watch:
        print("Watching tokens.json / components.json / audit-results.json…")
        watched = {p: p.stat().st_mtime for p in [TOKENS_PATH, COMPONENTS_PATH, AUDIT_PATH] if p.exists()}
        while True:
            time.sleep(2)
            for p, mtime in list(watched.items()):
                if p.exists() and p.stat().st_mtime != mtime:
                    print(f"\n{p.name} changed — regenerating…")
                    generate()
                    watched[p] = p.stat().st_mtime


CSS = r"""/* ─── Custom Properties ─────────────────────────────────────────────── */
:root {
  --doc-brand-blue: rgb(34,139,230);
  --doc-brand-blue-dark: rgb(25,113,194);
  --doc-nav-slate: rgb(65,73,81);
  --doc-surface-page: #fff;
  --doc-surface-card: #fff;
  --doc-surface-sidebar: #f8f9fa;
  --doc-text-primary: #212529;
  --doc-text-secondary: #6c757d;
  --doc-text-inverted: #fff;
  --doc-border: rgb(222,226,230);
  --doc-shadow-card: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.1);
  --doc-radius-sm: 4px;
  --doc-radius-pill: 1000px;
  --doc-spacing-xs: 4px;
  --doc-spacing-sm: 8px;
  --doc-spacing-md: 16px;
  --doc-spacing-lg: 24px;
  --doc-spacing-xl: 32px;
  --doc-font-body: -apple-system, system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  --doc-font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  --doc-ok-bg: rgb(211,249,216);
  --doc-ok-fg: rgb(43,138,62);
  --doc-err-bg: rgb(255,236,236);
  --doc-err-fg: rgb(201,42,42);
  --doc-info-bg: rgba(34,139,230,0.1);
  --doc-info-fg: rgb(34,139,230);
  --doc-warn-bg: rgba(251,191,36,0.15);
  --doc-warn-fg: #92400e;
  --doc-badge-bg: #e9ecef;
  --doc-badge-fg: #495057;
  --doc-sidebar-width: 260px;
  --doc-header-height: 56px;
}

[data-theme="dark"] {
  --doc-surface-page: rgb(36,36,36);
  --doc-surface-card: rgb(46,46,46);
  --doc-surface-sidebar: rgb(30,30,30);
  --doc-text-primary: rgb(201,201,201);
  --doc-text-secondary: rgb(134,142,150);
  --doc-border: rgb(66,66,66);
  --doc-ok-bg: rgb(43,138,62);
  --doc-ok-fg: rgb(211,249,216);
  --doc-err-bg: rgb(201,42,42);
  --doc-err-fg: rgb(255,236,236);
  --doc-info-bg: rgba(34,139,230,0.15);
  --doc-info-fg: rgb(116,192,252);
  --doc-warn-bg: rgba(251,191,36,0.1);
  --doc-warn-fg: #fcd34d;
  --doc-badge-bg: rgb(52,58,64);
  --doc-badge-fg: rgb(173,181,189);
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: var(--doc-font-body);
  font-size: 14px;
  line-height: 1.55;
  color: var(--doc-text-primary);
  background: var(--doc-surface-page);
  transition: background 0.2s, color 0.2s;
  min-height: 100vh;
}
a { color: var(--doc-brand-blue); text-decoration: none; }
a:hover, a:focus-visible { text-decoration: underline; }
code, pre { font-family: var(--doc-font-mono); }
ul, ol { padding-left: 1.25em; }

/* ─── Topbar ────────────────────────────────────────────────────────── */
.doc-topbar {
  position: fixed; top: 0; left: 0; right: 0; height: var(--doc-header-height);
  background: var(--doc-nav-slate); color: var(--doc-text-inverted);
  display: flex; align-items: center; padding: 0 var(--doc-spacing-md);
  gap: var(--doc-spacing-sm); z-index: 200;
}
.doc-topbar-title { color: inherit; font-weight: 700; font-size: 15px; text-decoration: none; }
.doc-topbar-title:hover { text-decoration: underline; }
.doc-topbar-spacer { flex: 1; }
.doc-topbar-theme, .doc-topbar-burger {
  background: rgba(255,255,255,0.1); border: none; color: inherit;
  cursor: pointer; font-size: 14px; width: 32px; height: 32px; border-radius: var(--doc-radius-sm);
}
.doc-topbar-theme:hover, .doc-topbar-burger:hover { background: rgba(255,255,255,0.2); }
.doc-topbar-burger { display: none; }

/* ─── Sidebar ───────────────────────────────────────────────────────── */
.doc-sidebar {
  width: var(--doc-sidebar-width);
  background: var(--doc-surface-sidebar);
  border-right: 1px solid var(--doc-border);
  padding-top: calc(var(--doc-header-height) + var(--doc-spacing-md));
  padding-bottom: var(--doc-spacing-lg);
  position: fixed; top: 0; left: 0; bottom: 0;
  overflow-y: auto; z-index: 100;
  transition: transform 0.25s ease;
}
.doc-sidebar-nav { padding: 0 var(--doc-spacing-sm); }
.doc-nav-section { margin-bottom: var(--doc-spacing-md); }
.doc-nav-label {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; color: var(--doc-text-secondary);
  padding: var(--doc-spacing-xs) var(--doc-spacing-sm);
  margin-top: var(--doc-spacing-sm);
}
.doc-nav-section ul { list-style: none; padding: 0; }
.doc-nav-link {
  display: block; padding: 6px var(--doc-spacing-sm); border-radius: var(--doc-radius-sm);
  color: var(--doc-text-primary); font-size: 13px; text-decoration: none;
}
.doc-nav-link:hover { background: var(--doc-border); text-decoration: none; }
.doc-nav-link.active { background: var(--doc-info-bg); color: var(--doc-brand-blue); font-weight: 600; }

.doc-content { margin-left: var(--doc-sidebar-width); padding: calc(var(--doc-header-height) + var(--doc-spacing-lg)) var(--doc-spacing-xl) var(--doc-spacing-xl); max-width: 1080px; }
.doc-sidebar-overlay { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 99; }

/* ─── Typography ────────────────────────────────────────────────────── */
h1 { font-size: 28px; font-weight: 700; margin-bottom: var(--doc-spacing-sm); display: flex; align-items: center; gap: var(--doc-spacing-sm); flex-wrap: wrap; }
h2 { font-size: 20px; font-weight: 600; margin: var(--doc-spacing-xl) 0 var(--doc-spacing-sm); border-bottom: 1px solid var(--doc-border); padding-bottom: var(--doc-spacing-xs); display: flex; align-items: baseline; gap: var(--doc-spacing-sm); }
h3 { font-size: 16px; font-weight: 600; margin: var(--doc-spacing-lg) 0 var(--doc-spacing-sm); }
h4 { font-size: 14px; font-weight: 600; margin-bottom: var(--doc-spacing-xs); }
p { margin-bottom: var(--doc-spacing-sm); }
.doc-subtitle { color: var(--doc-text-secondary); font-size: 16px; margin-bottom: var(--doc-spacing-lg); }

.count { font-size: 13px; color: var(--doc-text-secondary); font-weight: 400; }
.version-chip {
  display: inline-block; background: var(--doc-info-bg); color: var(--doc-brand-blue);
  font-size: 12px; font-weight: 600; padding: 2px 8px; border-radius: var(--doc-radius-pill);
  letter-spacing: 0.03em;
}

/* ─── Code ──────────────────────────────────────────────────────────── */
pre {
  background: var(--doc-surface-card); border: 1px solid var(--doc-border);
  border-radius: var(--doc-radius-sm); padding: var(--doc-spacing-md);
  overflow-x: auto; font-size: 13px; line-height: 1.5;
  position: relative; margin-bottom: var(--doc-spacing-sm);
}
code { font-size: 0.9em; background: var(--doc-badge-bg); padding: 1px 5px; border-radius: 3px; }
pre code { background: none; padding: 0; font-size: inherit; }
.copy-btn {
  position: absolute; top: var(--doc-spacing-sm); right: var(--doc-spacing-sm);
  background: var(--doc-border); border: none; border-radius: var(--doc-radius-sm);
  padding: 2px 8px; font-size: 11px; cursor: pointer; color: var(--doc-text-primary);
  opacity: 0; transition: opacity 0.15s;
}
pre:hover .copy-btn, pre:focus-within .copy-btn { opacity: 1; }
.copy-btn.copied { background: var(--doc-ok-bg); color: var(--doc-ok-fg); }

/* Syntax spans */
.kw { color: #7c3aed; }
.str { color: #0369a1; }
.num { color: #b45309; }
.cmt { color: var(--doc-text-secondary); font-style: italic; }
.tag-code { color: #0f766e; }
.attr { color: #be185d; }
[data-theme="dark"] .kw { color: #a78bfa; }
[data-theme="dark"] .str { color: #7dd3fc; }
[data-theme="dark"] .num { color: #fcd34d; }
[data-theme="dark"] .tag-code { color: #2dd4bf; }
[data-theme="dark"] .attr { color: #f9a8d4; }

/* ─── Tables ────────────────────────────────────────────────────────── */
table { width: 100%; border-collapse: collapse; margin-bottom: var(--doc-spacing-md); font-size: 13px; }
th { text-align: left; font-weight: 700; border-bottom: 2px solid var(--doc-border); padding: 7px 10px; }
td { border-bottom: 1px solid var(--doc-border); padding: 7px 10px; vertical-align: top; }
tr:last-child td { border-bottom: none; }
.css-var-table code { font-size: 11px; }

/* ─── Cards ─────────────────────────────────────────────────────────── */
.doc-card-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: var(--doc-spacing-md); margin-bottom: var(--doc-spacing-lg); }
.doc-card-link {
  display: block; border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm);
  padding: var(--doc-spacing-md); background: var(--doc-surface-card); box-shadow: var(--doc-shadow-card);
  color: var(--doc-text-primary); transition: border-color 0.15s, transform 0.15s;
}
.doc-card-link:hover { border-color: var(--doc-brand-blue); text-decoration: none; transform: translateY(-1px); }
.doc-card-link h3 { font-size: 15px; margin: var(--doc-spacing-xs) 0 var(--doc-spacing-xs); }
.doc-card-link p { font-size: 13px; color: var(--doc-text-secondary); margin: 0; }

/* ─── Tags ──────────────────────────────────────────────────────────── */
.tag {
  display: inline-block; background: var(--doc-badge-bg); color: var(--doc-badge-fg);
  font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: var(--doc-radius-pill);
  margin-right: var(--doc-spacing-xs);
}
.card-tag { background: var(--doc-info-bg); color: var(--doc-brand-blue); }
.tag-complex { background: var(--doc-err-bg); color: var(--doc-err-fg); }
.tag-medium { background: var(--doc-warn-bg); color: var(--doc-warn-fg); }
.tag-simple { background: var(--doc-ok-bg); color: var(--doc-ok-fg); }
.tag-priority.p0 { background: var(--doc-err-bg); color: var(--doc-err-fg); }
.tag-priority.p1 { background: var(--doc-err-bg); color: var(--doc-err-fg); }
.tag-priority.p2 { background: var(--doc-warn-bg); color: var(--doc-warn-fg); }
.tag-priority.p3 { background: var(--doc-badge-bg); color: var(--doc-badge-fg); }
.tag-severity-critical, .tag-severity-major { background: var(--doc-err-bg); color: var(--doc-err-fg); }
.tag-severity-minor { background: var(--doc-warn-bg); color: var(--doc-warn-fg); }
.tag-severity-cosmetic { background: var(--doc-badge-bg); color: var(--doc-badge-fg); }

/* ─── Callouts ──────────────────────────────────────────────────────── */
.callout { border-radius: var(--doc-radius-sm); padding: var(--doc-spacing-sm) var(--doc-spacing-md); margin: var(--doc-spacing-sm) 0 var(--doc-spacing-md); font-size: 13px; }
.callout-info { background: var(--doc-info-bg); color: var(--doc-info-fg); border-left: 3px solid var(--doc-brand-blue); }
.callout-warn { background: var(--doc-warn-bg); color: var(--doc-warn-fg); border-left: 3px solid #f59e0b; }
.callout-wip { background: var(--doc-warn-bg); color: var(--doc-warn-fg); border-left: 3px solid #f59e0b; }

/* ─── Swatches ──────────────────────────────────────────────────────── */
.swatch-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: var(--doc-spacing-sm); margin-bottom: var(--doc-spacing-md); }
.swatch { border-radius: var(--doc-radius-sm); overflow: hidden; border: 1px solid var(--doc-border); background: var(--doc-surface-card); }
.swatch-color { height: 56px; }
.swatch-info { padding: 6px 10px; font-size: 11px; }
.swatch-name { font-weight: 700; font-family: var(--doc-font-mono); }
.swatch-value { color: var(--doc-text-secondary); font-family: var(--doc-font-mono); font-size: 10px; }
.swatch-usage { color: var(--doc-text-secondary); font-size: 11px; margin-top: 4px; }

/* Status grid */
.status-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--doc-spacing-md); margin-bottom: var(--doc-spacing-md); }
.status-card { border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); padding: var(--doc-spacing-sm); background: var(--doc-surface-card); }
.status-title { font-weight: 700; margin-bottom: var(--doc-spacing-xs); font-family: var(--doc-font-mono); font-size: 12px; }
.status-swatches { display: flex; flex-direction: column; gap: var(--doc-spacing-xs); }
.status-swatch { padding: 8px; border-radius: var(--doc-radius-sm); font-size: 11px; font-weight: 700; text-transform: uppercase; text-align: center; }

/* Spacing */
.spacing-grid { display: flex; flex-direction: column; gap: var(--doc-spacing-xs); margin-bottom: var(--doc-spacing-md); }
.spacing-row { display: flex; align-items: center; gap: var(--doc-spacing-md); padding: 6px 0; border-bottom: 1px solid var(--doc-border); }
.spacing-preview { height: 16px; background: var(--doc-brand-blue); border-radius: 2px; }
.spacing-name { font-family: var(--doc-font-mono); font-size: 12px; min-width: 60px; font-weight: 700; }
.spacing-value { color: var(--doc-text-secondary); font-family: var(--doc-font-mono); font-size: 11px; }

/* Typography */
.type-grid { display: flex; flex-direction: column; gap: var(--doc-spacing-md); margin-bottom: var(--doc-spacing-md); }
.type-row { border-bottom: 1px solid var(--doc-border); padding: var(--doc-spacing-sm) 0; }
.type-preview { color: var(--doc-text-primary); font-family: var(--doc-font-body); margin-bottom: 4px; }
.type-meta { display: flex; gap: var(--doc-spacing-md); align-items: baseline; }
.type-name { font-family: var(--doc-font-mono); font-size: 12px; font-weight: 700; }
.type-specs { color: var(--doc-text-secondary); font-size: 11px; font-family: var(--doc-font-mono); }
.family-row { margin-bottom: var(--doc-spacing-sm); font-size: 13px; }
.family-usage { color: var(--doc-text-secondary); font-size: 12px; }

/* Radius */
.radius-grid { display: flex; flex-wrap: wrap; gap: var(--doc-spacing-md); margin-bottom: var(--doc-spacing-md); }
.radius-row { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.radius-preview { width: 64px; height: 48px; background: var(--doc-brand-blue); }
.radius-name { font-family: var(--doc-font-mono); font-size: 11px; font-weight: 700; }
.radius-value { color: var(--doc-text-secondary); font-size: 11px; }

/* Elevation */
.elev-grid { display: flex; flex-wrap: wrap; gap: var(--doc-spacing-md); margin-bottom: var(--doc-spacing-md); }
.elev-row { display: flex; gap: var(--doc-spacing-sm); align-items: center; }
.elev-preview { width: 80px; height: 60px; background: var(--doc-surface-card); border-radius: var(--doc-radius-sm); }
.elev-meta { font-size: 11px; }

/* Do/Don't grid */
.do-dont-grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--doc-spacing-md); margin-bottom: var(--doc-spacing-md); }
.do-item, .dont-item { border-radius: var(--doc-radius-sm); padding: var(--doc-spacing-sm) var(--doc-spacing-md); font-size: 13px; }
.do-item { background: var(--doc-ok-bg); border-left: 3px solid var(--doc-ok-fg); color: var(--doc-ok-fg); }
.dont-item { background: var(--doc-err-bg); border-left: 3px solid var(--doc-err-fg); color: var(--doc-err-fg); }
.do-item strong, .dont-item strong { display: block; margin-bottom: 4px; font-size: 11px; letter-spacing: 0.1em; }
.do-item p, .dont-item p { margin: 0; }

/* Mock previews */
.mock-preview { background: var(--doc-surface-card); border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); padding: var(--doc-spacing-lg); margin-bottom: var(--doc-spacing-sm); display: flex; align-items: center; flex-wrap: wrap; gap: var(--doc-spacing-sm); min-height: 80px; }
.variant-block { margin-bottom: var(--doc-spacing-md); }
.variant-desc { color: var(--doc-text-secondary); font-size: 12px; }

/* Mock classes */
.mock-header { background: var(--doc-nav-slate); color: var(--doc-text-inverted); display: flex; align-items: center; gap: var(--doc-spacing-md); padding: 0 var(--doc-spacing-md); height: 48px; border-radius: var(--doc-radius-sm); width: 100%; }
.mock-header-brand { font-weight: 700; }
.mock-header-nav { display: flex; gap: 4px; flex: 1; }
.mock-header-link { padding: 6px var(--doc-spacing-sm); border-radius: var(--doc-radius-sm); font-size: 13px; color: rgba(255,255,255,0.7); cursor: pointer; }
.mock-header-link.is-active { background: var(--doc-brand-blue); color: #fff; }
.mock-header-tools { display: flex; gap: 4px; }

.mock-navbtn { padding: 8px var(--doc-spacing-md); border-radius: var(--doc-radius-sm); background: transparent; color: var(--doc-text-secondary); font-size: 13px; }
.mock-navbtn--active { background: var(--doc-brand-blue); color: #fff; }

.mock-icon-btn { width: 32px; height: 32px; border: none; background: rgba(0,0,0,0.05); border-radius: var(--doc-radius-sm); color: var(--doc-text-primary); cursor: pointer; display: inline-flex; align-items: center; justify-content: center; }
.mock-icon-btn--header { background: rgb(134,142,150); color: #fff; }
.mock-icon-btn--overlay { background: rgba(0,0,0,0.1); position: relative; }

.mock-dropdown { background: var(--doc-surface-card); border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); padding: var(--doc-spacing-sm) 0; box-shadow: var(--doc-shadow-card); min-width: 220px; }
.mock-dropdown-section { padding: 4px var(--doc-spacing-md); font-size: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--doc-text-secondary); font-weight: 700; }
.mock-dropdown-item { padding: 6px var(--doc-spacing-md); font-size: 13px; cursor: pointer; }
.mock-dropdown-item:hover { background: var(--doc-info-bg); color: var(--doc-brand-blue); }

.mock-breadcrumb { display: inline-flex; align-items: center; gap: 4px; padding: 8px var(--doc-spacing-md); background: var(--doc-brand-blue); color: #fff; border-radius: var(--doc-radius-sm); font-size: 13px; }
.mock-breadcrumb-sep { opacity: 0.7; }

.mock-btn { padding: 0 18px; height: 36px; border-radius: var(--doc-radius-sm); border: none; font-size: 14px; cursor: pointer; font-family: var(--doc-font-body); }
.mock-btn--primary { background: var(--doc-brand-blue); color: #fff; font-weight: 600; }
.mock-btn--secondary { background: transparent; color: var(--doc-brand-blue); font-weight: 500; padding: 8px var(--doc-spacing-md); }

.mock-input { background: var(--doc-surface-card); border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); height: 36px; padding: 0 12px; display: flex; align-items: center; gap: var(--doc-spacing-sm); font-size: 13px; min-width: 280px; }
.mock-input--expression { width: 100%; font-family: var(--doc-font-mono); }
.mock-input--search { padding-left: 34px; position: relative; }
.mock-input--pills { min-height: 36px; height: auto; padding: 4px 8px; flex-wrap: wrap; }
.mock-input--select { justify-content: space-between; }
.mock-input--date { min-width: 200px; font-family: var(--doc-font-mono); }
.mock-input-prefix { color: var(--doc-text-secondary); }
.mock-input-suffix { background: var(--doc-brand-blue); color: #fff; padding: 4px 10px; border-radius: 3px; font-size: 12px; margin-left: auto; }
.mock-input-placeholder { color: var(--doc-text-secondary); }
.mock-input-value { flex: 1; }
.mock-input-chevron { color: var(--doc-text-secondary); }
.mock-input-row { display: flex; align-items: center; gap: var(--doc-spacing-xs); }

.mock-pill { background: var(--doc-badge-bg); color: var(--doc-badge-fg); font-size: 11px; padding: 2px 10px; border-radius: var(--doc-radius-pill); }

.mock-tabs { display: flex; gap: var(--doc-spacing-md); border-bottom: 1px solid var(--doc-border); width: 100%; }
.mock-tab { padding: 10px var(--doc-spacing-md); cursor: pointer; font-size: 14px; color: var(--doc-text-primary); border-bottom: 2px solid transparent; margin-bottom: -1px; }
.mock-tab.is-active { border-bottom-color: var(--doc-brand-blue); color: var(--doc-brand-blue); }

.mock-card { background: var(--doc-surface-card); border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); padding: var(--doc-spacing-md); box-shadow: var(--doc-shadow-card); width: 100%; }
.mock-card-title { font-weight: 600; font-size: 16px; margin-bottom: var(--doc-spacing-sm); display: flex; align-items: center; gap: var(--doc-spacing-xs); }
.mock-card-icon { font-size: 18px; }
.mock-card-body { color: var(--doc-text-secondary); font-size: 13px; }

.mock-accordion { border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); width: 100%; overflow: hidden; }
.mock-accordion--ok { border-left: 5px solid rgb(140,233,154); }
.mock-accordion--error { border-left: 5px solid rgb(255,168,168); }
.mock-accordion-header { display: flex; align-items: center; gap: var(--doc-spacing-sm); padding: var(--doc-spacing-sm) var(--doc-spacing-md); }
.mock-accordion-title { font-weight: 600; flex: 1; }
.mock-accordion-counter { color: var(--doc-text-secondary); font-size: 12px; font-family: var(--doc-font-mono); }
.mock-accordion-chevron { color: var(--doc-text-secondary); }

.mock-status-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; }
.mock-status-dot--ok { background: rgb(64,192,87); }
.mock-status-dot--error { background: rgb(250,82,82); }

.mock-badge { display: inline-flex; align-items: center; gap: 4px; border-radius: var(--doc-radius-pill); padding: 2px 10px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.mock-badge--ok { background: var(--doc-ok-bg); color: var(--doc-ok-fg); }
.mock-badge--error { background: var(--doc-err-bg); color: var(--doc-err-fg); }
.mock-badge--neutral { background: var(--doc-badge-bg); color: var(--doc-badge-fg); text-transform: none; }
.mock-badge--stats { text-transform: none; }

.mock-table, .mock-kv-table { width: 100%; border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); border-collapse: collapse; }
.mock-table th, .mock-table td, .mock-kv-table td { padding: 7px 10px; border-bottom: 1px solid var(--doc-border); font-size: 13px; text-align: left; }
.mock-table th { font-weight: 700; }
.mock-table--sortable th { cursor: pointer; }
.mock-sort-icon { color: var(--doc-text-secondary); font-size: 10px; margin-left: 4px; }
.mock-kv-key { font-weight: 700; width: 40%; }

.mock-inline-code { font-family: var(--doc-font-mono); font-size: 13px; background: var(--doc-badge-bg); padding: 1px 5px; border-radius: 3px; }

.mock-code-block { font-family: var(--doc-font-mono); font-size: 13px; background: var(--doc-surface-card); border: 1px solid var(--doc-border); padding: var(--doc-spacing-md); border-radius: var(--doc-radius-sm); position: relative; width: 100%; overflow-x: auto; }
.mock-code-block-copy { position: absolute; top: 8px; right: 8px; }

.mock-hljs { font-family: var(--doc-font-mono); font-size: 13px; background: var(--doc-surface-card); border: 1px solid var(--doc-border); padding: var(--doc-spacing-md); border-radius: var(--doc-radius-sm); width: 100%; }
.mock-hljs--light .mock-hljs-attr, .mock-hljs-attr { color: rgb(92,148,13); }
.mock-hljs--light .mock-hljs-str { color: rgb(24,100,171); }
.mock-hljs--dark { background: rgb(31,31,31); color: rgb(201,201,201); }
.mock-hljs--dark .mock-hljs-attr { color: rgb(165,216,255); }
.mock-hljs--dark .mock-hljs-str { color: rgb(64,192,87); }

.mock-alert { display: flex; gap: var(--doc-spacing-sm); padding: var(--doc-spacing-md); border-radius: var(--doc-radius-sm); width: 100%; }
.mock-alert--info { background: var(--doc-info-bg); color: var(--doc-info-fg); }
.mock-alert-icon { font-size: 16px; }
.mock-alert-title { font-weight: 700; }
.mock-alert-desc { font-size: 13px; color: var(--doc-text-primary); opacity: 0.9; margin-top: 4px; }

.mock-link { color: var(--doc-brand-blue); text-decoration: none; }

/* Reference section */
.ref-details { margin-bottom: var(--doc-spacing-md); border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); padding: var(--doc-spacing-sm) var(--doc-spacing-md); }
.ref-details[open] { padding-bottom: var(--doc-spacing-md); }
.ref-details summary { cursor: pointer; font-weight: 600; }
.ref-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: var(--doc-spacing-sm); margin-top: var(--doc-spacing-md); }
.ref-img { border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); overflow: hidden; background: var(--doc-surface-card); }
.ref-img img { width: 100%; display: block; background: var(--doc-border); min-height: 60px; }
.ref-img figcaption { padding: 6px 10px; font-size: 11px; color: var(--doc-text-secondary); font-family: var(--doc-font-mono); }
.ref-note { font-size: 12px; color: var(--doc-text-secondary); margin-top: var(--doc-spacing-sm); }

/* Icon grid */
.icon-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: var(--doc-spacing-sm); margin-bottom: var(--doc-spacing-md); }
.icon-card { border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); padding: var(--doc-spacing-md); background: var(--doc-surface-card); font-size: 11px; }
.icon-preview { font-size: 28px; text-align: center; margin-bottom: var(--doc-spacing-xs); color: var(--doc-brand-blue); }
.icon-name { margin-bottom: 4px; text-align: center; }
.icon-usage { color: var(--doc-text-secondary); margin-bottom: var(--doc-spacing-xs); }
.icon-import code { font-size: 10px; }
.icon-search { width: 100%; max-width: 360px; padding: 8px 12px; border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); font-size: 14px; margin-bottom: var(--doc-spacing-md); background: var(--doc-surface-card); color: var(--doc-text-primary); }

/* Action cards */
.action-card { border: 1px solid var(--doc-border); border-radius: var(--doc-radius-sm); margin-bottom: var(--doc-spacing-md); overflow: hidden; background: var(--doc-surface-card); }
.action-card-header { padding: var(--doc-spacing-sm) var(--doc-spacing-md); background: var(--doc-surface-sidebar); display: flex; align-items: center; gap: var(--doc-spacing-xs); flex-wrap: wrap; border-bottom: 1px solid var(--doc-border); }
.action-card-id { font-family: var(--doc-font-mono); font-size: 12px; color: var(--doc-text-secondary); }
.action-card-title { font-weight: 700; flex: 1; min-width: 200px; }
.action-card-body { padding: var(--doc-spacing-md); font-size: 13px; }
.action-card-before-after { display: grid; grid-template-columns: 1fr 1fr; gap: var(--doc-spacing-md); margin-top: var(--doc-spacing-sm); }
.action-card-before pre { border-left: 3px solid var(--doc-err-fg); }
.action-card-after pre { border-left: 3px solid var(--doc-ok-fg); }
.action-card-before h4, .action-card-after h4 { font-size: 11px; letter-spacing: 0.1em; color: var(--doc-text-secondary); margin-bottom: var(--doc-spacing-xs); }
.files-changed { margin-top: var(--doc-spacing-sm); font-size: 12px; }
.files-changed summary { cursor: pointer; color: var(--doc-text-secondary); }
.files-changed ul { margin-top: var(--doc-spacing-xs); list-style: none; padding-left: 0; }
.rel-inc-link { font-size: 11px; color: var(--doc-text-secondary); font-family: var(--doc-font-mono); }
.issue-link { font-size: 12px; color: var(--doc-brand-blue); margin-left: auto; }

/* Inconsistencies */
.inc-item { border: 1px solid var(--doc-border); border-left-width: 4px; border-radius: var(--doc-radius-sm); padding: var(--doc-spacing-md); margin-bottom: var(--doc-spacing-md); background: var(--doc-surface-card); }
.inc-item.severity-minor { border-left-color: #f59e0b; }
.inc-item.severity-cosmetic { border-left-color: var(--doc-border); }
.inc-item.severity-major { border-left-color: var(--doc-err-fg); }
.inc-item.severity-critical { border-left-color: var(--doc-err-fg); background: var(--doc-err-bg); }
.inc-header { display: flex; gap: var(--doc-spacing-xs); flex-wrap: wrap; align-items: center; margin-bottom: var(--doc-spacing-sm); }
.inc-id { font-family: var(--doc-font-mono); font-size: 12px; color: var(--doc-text-secondary); }
.inc-title { flex: 1 1 100%; margin: 0; font-size: 15px; }
.inc-canonical { background: var(--doc-info-bg); color: var(--doc-info-fg); padding: var(--doc-spacing-xs) var(--doc-spacing-sm); border-radius: var(--doc-radius-sm); font-size: 13px; margin-bottom: var(--doc-spacing-xs); }
.inc-reasoning, .inc-fix { font-size: 13px; margin-bottom: var(--doc-spacing-xs); }

/* Patterns table */
.patterns-table { font-size: 12px; }
.patterns-table td code { font-size: 10px; }

/* Spec table */
.spec-table td { vertical-align: top; }
.spec-table td:first-child { color: var(--doc-text-secondary); width: 30%; font-family: var(--doc-font-mono); font-size: 12px; }

/* A11y table */
.a11y-table td:first-child { width: 20%; font-weight: 700; color: var(--doc-text-secondary); }

/* Migration list */
.migration-list li { margin-bottom: var(--doc-spacing-xs); }

/* Gap list */
.gap-list { background: var(--doc-warn-bg); color: var(--doc-warn-fg); border-radius: var(--doc-radius-sm); padding: var(--doc-spacing-sm) var(--doc-spacing-md); list-style: square; padding-left: calc(var(--doc-spacing-md) + 16px); }

/* Acknowledgements */
.acknowledgements { margin-top: var(--doc-spacing-xl); padding-top: var(--doc-spacing-lg); border-top: 1px solid var(--doc-border); color: var(--doc-text-secondary); font-size: 13px; }

/* Responsive */
@media (max-width: 960px) {
  .doc-topbar-burger { display: inline-flex; align-items: center; justify-content: center; }
  .doc-sidebar { transform: translateX(calc(-1 * var(--doc-sidebar-width))); }
  .doc-sidebar.open { transform: translateX(0); }
  .doc-sidebar-overlay.visible { display: block; }
  .doc-content { margin-left: 0; padding-left: var(--doc-spacing-md); padding-right: var(--doc-spacing-md); }
  .do-dont-grid, .action-card-before-after { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .doc-card-grid { grid-template-columns: 1fr; }
  h1 { font-size: 22px; }
  h2 { font-size: 17px; }
}
"""


MAIN_JS = r"""(function () {
  // Theme toggle
  var root = document.documentElement;
  var stored = localStorage.getItem('doc-theme');
  var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  root.setAttribute('data-theme', stored || (prefersDark ? 'dark' : 'light'));
  var toggle = document.getElementById('doc-theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem('doc-theme', next);
    });
  }

  // Burger
  var burger = document.getElementById('doc-burger');
  var sidebar = document.getElementById('doc-sidebar');
  var overlay = document.getElementById('doc-sidebar-overlay');
  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('visible');
  }
  if (burger) {
    burger.addEventListener('click', function () {
      if (sidebar) sidebar.classList.toggle('open');
      if (overlay) overlay.classList.toggle('visible');
    });
  }
  if (overlay) overlay.addEventListener('click', closeSidebar);

  // Copy buttons on every <pre>
  Array.prototype.forEach.call(document.querySelectorAll('pre'), function (pre) {
    if (pre.querySelector('.copy-btn')) return;
    var btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.type = 'button';
    btn.textContent = 'Copy';
    btn.addEventListener('click', function () {
      var code = pre.querySelector('code');
      var text = code ? code.textContent : pre.textContent;
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = 'Copied';
        btn.classList.add('copied');
        setTimeout(function () {
          btn.textContent = 'Copy';
          btn.classList.remove('copied');
        }, 1500);
      });
    });
    pre.appendChild(btn);
  });

  // Icon search filter
  var iconSearch = document.getElementById('icon-search');
  if (iconSearch) {
    iconSearch.addEventListener('input', function () {
      var q = iconSearch.value.toLowerCase();
      Array.prototype.forEach.call(document.querySelectorAll('.icon-card'), function (c) {
        c.style.display = c.textContent.toLowerCase().indexOf(q) === -1 ? 'none' : '';
      });
    });
  }
})();
"""


README_MD = """# Prometheus Design System — run2

Static docs site generated by the `design-system-extraction-code` skill.

## Regenerate

```bash
python3 ../gen.py
```

## Serve locally

```bash
python3 -m http.server 8000 --directory .
```

Open http://localhost:8000
"""


if __name__ == "__main__":
    main()
