#!/usr/bin/env python3
"""Generate all docs-site HTML from tokens.json and components.json."""
import json, os, pathlib, html as htmllib

BASE = pathlib.Path(__file__).parent
DATA = BASE.parent

tokens = json.loads((DATA / "tokens.json").read_text())
comps = json.loads((DATA / "components.json").read_text())
audit = json.loads((DATA / "audit-results.json").read_text())

components = comps["components"]
action_items = comps.get("action_items", [])
inconsistencies = audit["inconsistencies"]

SLUGS = [(c["slug"], c["name"]) for c in components]

# ─── Nav helpers ──────────────────────────────────────────────────────────────

def sidebar_nav(prefix=""):
    comp_links = "\n".join(
        f'      <a href="{prefix}components/{slug}.html" class="doc-nav-link doc-nav-sub">{htmllib.escape(name)}</a>'
        for slug, name in SLUGS
    )
    return f"""<aside class="doc-sidebar" id="sidebar">
  <nav class="doc-sidebar-nav">
    <div class="doc-nav-section">
      <div class="doc-nav-label">Overview</div>
      <a href="{prefix}index.html" class="doc-nav-link">Home</a>
      <a href="{prefix}tokens.html" class="doc-nav-link">Tokens</a>
      <a href="{prefix}icons.html" class="doc-nav-link">Icons</a>
      <a href="{prefix}patterns.html" class="doc-nav-link">Patterns</a>
    </div>
    <div class="doc-nav-section">
      <div class="doc-nav-label">Components</div>
      <a href="{prefix}components.html" class="doc-nav-link">All Components</a>
{comp_links}
    </div>
    <div class="doc-nav-section">
      <div class="doc-nav-label">Reference</div>
      <a href="{prefix}action-items.html" class="doc-nav-link">Action Items</a>
      <a href="{prefix}inconsistencies.html" class="doc-nav-link">Inconsistencies</a>
      <a href="{prefix}audit-report.html" class="doc-nav-link">Audit Report</a>
      <a href="{prefix}figma.html" class="doc-nav-link">Figma Plugin</a>
      <a href="{prefix}changelog.html" class="doc-nav-link">Changelog</a>
    </div>
  </nav>
</aside>"""

def topbar(prefix=""):
    return f"""<header class="doc-topbar">
  <button class="doc-topbar-burger" id="burger" aria-label="Open menu">☰</button>
  <span class="doc-topbar-title">🔥 Prometheus Design System</span>
  <span class="doc-topbar-spacer"></span>
  <button class="doc-topbar-theme" id="themeToggle" aria-label="Toggle theme">🌙</button>
</header>
<div class="doc-sidebar-overlay" id="sidebarOverlay"></div>"""

def page(title, body, prefix="", extra_head=""):
    css = f"{prefix}styles.css"
    js = f"{prefix}main.js"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{htmllib.escape(title)} — Prometheus Design System</title>
<link rel="stylesheet" href="{css}">
{extra_head}
</head>
<body>
{topbar(prefix)}
{sidebar_nav(prefix)}
<div class="doc-content">
<main class="doc-main">
{body}
</main>
</div>
<script src="{js}"></script>
</body>
</html>"""

def write(path, content):
    path = BASE / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"  wrote {path.relative_to(BASE)}")

# ─── Helpers ──────────────────────────────────────────────────────────────────

def badge(text, cls="gray"):
    return f'<span class="doc-badge doc-badge-{cls}">{htmllib.escape(text)}</span>'

def priority_badge(p):
    cls = {"p0-critical": "red", "p1-high": "red", "p2-medium": "blue", "p3-low": "gray"}.get(p, "gray")
    label = p.split("-", 1)[1].upper() if "-" in p else p
    return f'<span class="doc-badge doc-badge-{cls}">{label}</span>'

def effort_badge(e):
    cls = {"easy": "green", "medium": "blue", "hard": "red"}.get(e, "gray")
    return f'<span class="doc-badge doc-badge-{cls}">{e.upper()}</span>'

def esc(s):
    return htmllib.escape(str(s)) if s else ""

def code_block(code):
    return f"<pre><code>{esc(code)}</code></pre>"

# ─── index.html ───────────────────────────────────────────────────────────────

def gen_index():
    cards = [
        ("🎨", "Tokens", "tokens.html", "Colors, spacing, typography, radius, elevation"),
        ("🔣", "Icons", "icons.html", "12 Tabler icons catalogued from the app"),
        ("🧩", "Components", "components.html", "18 extracted UI components with docs"),
        ("🔗", "Patterns", "patterns.html", "Composition patterns and page-level layouts"),
        ("🛠", "Action Items", "action-items.html", "9 PR-ready fix cards for inconsistencies"),
        ("🔍", "Audit Report", "audit-report.html", "Full Phase 1 visual audit findings"),
        ("⚠️", "Inconsistencies", "inconsistencies.html", "INC-001 through INC-009 with resolution notes"),
        ("🔌", "Figma Plugin", "figma.html", "Bootstrap Figma variables from tokens.json"),
        ("📋", "Changelog", "changelog.html", "Version history of the design system"),
    ]
    grid = "\n".join(
        f'<a href="{href}" class="doc-card-link"><div class="doc-card-icon">{icon}</div>'
        f'<h3>{label}</h3><p>{desc}</p></a>'
        for icon, label, href, desc in cards
    )
    body = f"""<h1>Prometheus Design System</h1>
<p class="doc-subtitle">Extracted from <a href="https://prometheus-e83j.onrender.com" target="_blank">prometheus-e83j.onrender.com</a> via visual audit · {audit['audit_date']} · Mantine v7+</p>
<div class="callout callout-info">10 pages audited · 18 patterns catalogued · 9 inconsistencies identified · light + dark themes</div>
<div class="doc-card-grid" style="margin-top:24px">{grid}</div>
<h2 id="stats">At a glance</h2>
<table>
<thead><tr><th>Metric</th><th>Value</th></tr></thead>
<tbody>
<tr><td>Pages audited</td><td>10</td></tr>
<tr><td>UI patterns</td><td>18</td></tr>
<tr><td>Inconsistencies</td><td>9</td></tr>
<tr><td>Framework</td><td>Mantine v7+</td></tr>
<tr><td>Themes</td><td>Light + Dark</td></tr>
<tr><td>Brand color (light)</td><td><code>rgb(34,139,230)</code> Mantine blue</td></tr>
<tr><td>Nav background</td><td><code>rgb(65,73,81)</code> slate (theme-invariant)</td></tr>
</tbody>
</table>"""
    write("index.html", page("Home", body))

# ─── tokens.html ──────────────────────────────────────────────────────────────

def color_swatch(name, light_val, dark_val=None):
    return f"""<div class="swatch">
  <div class="swatch-color" style="background:{light_val}"></div>
  <div class="swatch-info">
    <div class="swatch-name">{esc(name)}</div>
    <div class="swatch-value">{esc(light_val)}</div>
    {f'<div class="swatch-value">dark: {esc(dark_val)}</div>' if dark_val else ''}
  </div>
</div>"""

def gen_tokens():
    tok = tokens
    # Brand swatches
    brand_swatches = "\n".join(
        color_swatch(c["name"], c["value"])
        for c in tok["colors"]["brand"]
    )
    # Status swatches
    status_rows = ""
    for s in tok["colors"]["status"]:
        l = s["light"]; d = s.get("dark", {})
        status_rows += f"<tr><td><b>{esc(s['name'])}</b></td>"
        status_rows += f"<td><span style='background:{esc(l['bg'])};color:{esc(l['text'])};padding:2px 10px;border-radius:1000px;font-size:12px'>{esc(s['name'])}</span></td>"
        if d:
            status_rows += f"<td><span style='background:{esc(d['bg'])};color:{esc(d['text'])};padding:2px 10px;border-radius:1000px;font-size:12px'>{esc(s['name'])}</span></td>"
        status_rows += "</tr>"
    # Surface
    surface_swatches = "\n".join(
        color_swatch(c["name"], c["light"], c.get("dark"))
        for c in tok["colors"]["surface"]
    )
    # Text
    text_rows = "\n".join(
        f'<tr><td><b>{esc(c["name"])}</b></td><td><code>{esc(c["light"])}</code></td><td><code>{esc(c.get("dark","—"))}</code></td></tr>'
        for c in tok["colors"]["text"]
    )
    # Border
    border_rows = "\n".join(
        f'<tr><td><b>{esc(c["name"])}</b></td><td><code>{esc(c["light"])}</code></td><td><code>{esc(c.get("dark","—"))}</code></td></tr>'
        for c in tok["colors"]["border"]
    )
    # Spacing
    spacing_rows = "\n".join(
        f'<tr><td><code>{esc(s["name"])}</code></td><td>{s["value_px"]}px</td>'
        f'<td>{s.get("value_rem","—")}rem</td>'
        f'<td><div style="height:8px;background:var(--doc-brand-blue);border-radius:2px;width:{min(s["value_px"]*4,200)}px"></div></td></tr>'
        for s in tok["spacing"]["scale"]
    )
    layout_rows = "\n".join(
        f'<tr><td><code>{esc(s["name"])}</code></td><td>{s["value_px"]}px</td><td>—</td><td>—</td></tr>'
        for s in tok["spacing"].get("layout", [])
    )
    # Typography families
    fam_rows = "\n".join(
        f'<tr><td><b>{esc(f["name"])}</b></td><td><code style="font-family:{esc(f["family"])}">{esc(f["family"][:40])}{"…" if len(f["family"])>40 else ""}</code></td>'
        f'<td>{esc(f.get("figma_family","—"))}</td><td style="font-size:12px">{esc(f["usage"])}</td></tr>'
        for f in tok["typography"]["families"]
    )
    # Typography styles
    style_rows = "\n".join(
        f'<tr><td><code>{esc(s["name"])}</code></td><td>{esc(s["category"])}</td><td>{s["size_px"]}px</td><td>{s["weight"]}</td><td>{s["line_height"]}</td></tr>'
        for s in tok["typography"]["styles"]
    )
    # Radius
    radius_rows = "\n".join(
        f'<tr><td><code>{esc(r["name"])}</code></td><td>{r["value_px"]}px</td>'
        f'<td><div style="width:32px;height:32px;background:var(--doc-brand-blue);border-radius:{min(r["value_px"],16)}px"></div></td></tr>'
        for r in tok["border_radius"]
    )
    # Elevation
    elev_rows = ""
    for e in tok.get("elevation", []):
        css = e["light"]["css"]
        elev_rows += f'<tr><td><code>{esc(e["name"])}</code></td><td><code>{esc(css)}</code></td>'
        elev_rows += f'<td><div style="width:48px;height:32px;background:var(--doc-surface-card);box-shadow:{esc(css)};border-radius:4px;border:1px solid var(--doc-border)"></div></td></tr>'

    body = f"""<h1>Design Tokens</h1>
<p class="doc-subtitle">All values extracted from live DOM inspection of <a href="https://prometheus-e83j.onrender.com" target="_blank">prometheus-e83j.onrender.com</a></p>

<h2 id="brand">Brand Colors</h2>
<div class="swatch-grid">{brand_swatches}</div>

<h2 id="status">Status Colors</h2>
<table>
<thead><tr><th>Name</th><th>Light</th><th>Dark</th></tr></thead>
<tbody>{status_rows}</tbody>
</table>

<h2 id="surface">Surface Colors</h2>
<div class="swatch-grid">{surface_swatches}</div>

<h2 id="text">Text Colors</h2>
<table>
<thead><tr><th>Name</th><th>Light</th><th>Dark</th></tr></thead>
<tbody>{text_rows}</tbody>
</table>

<h2 id="border">Border Colors</h2>
<table>
<thead><tr><th>Name</th><th>Light</th><th>Dark</th></tr></thead>
<tbody>{border_rows}</tbody>
</table>

<h2 id="spacing">Spacing</h2>
<table>
<thead><tr><th>Name</th><th>px</th><th>rem</th><th>Visual</th></tr></thead>
<tbody>{spacing_rows}{layout_rows}</tbody>
</table>

<h2 id="typography">Typography — Families</h2>
<table>
<thead><tr><th>Name</th><th>Family</th><th>Figma</th><th>Usage</th></tr></thead>
<tbody>{fam_rows}</tbody>
</table>

<h2 id="type-styles">Typography — Styles</h2>
<table>
<thead><tr><th>Name</th><th>Category</th><th>Size</th><th>Weight</th><th>Line height</th></tr></thead>
<tbody>{style_rows}</tbody>
</table>

<h2 id="radius">Border Radius</h2>
<table>
<thead><tr><th>Name</th><th>Value</th><th>Preview</th></tr></thead>
<tbody>{radius_rows}</tbody>
</table>

<h2 id="elevation">Elevation / Shadows</h2>
<table>
<thead><tr><th>Name</th><th>CSS</th><th>Preview</th></tr></thead>
<tbody>{elev_rows}</tbody>
</table>"""
    write("tokens.html", page("Tokens", body))

# ─── icons.html ───────────────────────────────────────────────────────────────

def gen_icons():
    icons_data = tokens.get("icons", {})
    icon_list = icons_data.get("icons", [])
    rows = "\n".join(
        f'<tr><td><code>{esc(i["name"])}</code></td><td>{esc(i["usage"])}</td></tr>'
        for i in icon_list
    )
    body = f"""<h1>Icon Inventory</h1>
<p class="doc-subtitle">Library: {esc(icons_data.get("library","—"))} · {len(icon_list)} icons · default size {icons_data.get("default_size_px","—")}px</p>
<div class="callout callout-info">SVG paths were not captured in the visual audit. Icons are listed by name as observed in the Tabler Icons library used by Mantine.</div>
<table>
<thead><tr><th>Icon name</th><th>Usage in app</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<h2 id="usage">Icon usage rules</h2>
<div class="do-dont-grid">
  <div class="do-item"><strong>Do</strong>Use Tabler Icons exclusively — the app imports from @tabler/icons-react.</div>
  <div class="do-item"><strong>Do</strong>Set aria-hidden="true" on decorative icons; provide aria-label on interactive ones.</div>
  <div class="dont-item"><strong>Don't</strong>Mix icon libraries — do not add Heroicons, Material Icons, or others.</div>
  <div class="dont-item"><strong>Don't</strong>Use icons as the sole indicator for status — pair with text or color.</div>
</div>"""
    write("icons.html", page("Icons", body))

# ─── components.html ──────────────────────────────────────────────────────────

def gen_components_index():
    by_cat = {}
    for c in components:
        cat = c["category"]
        by_cat.setdefault(cat, []).append(c)

    sections = ""
    for cat, comps_in_cat in sorted(by_cat.items()):
        cards = "\n".join(
            f'<a href="components/{c["slug"]}.html" class="doc-card-link">'
            f'<h3>{esc(c["name"])}</h3>'
            f'<p>{esc(c.get("subtitle",""))}</p>'
            f'<p style="margin-top:8px">{badge(c["complexity"])}&nbsp;{badge(cat,"gray")}</p></a>'
            for c in comps_in_cat
        )
        sections += f'<h2 id="{cat}">{cat.replace("-"," ").title()}</h2><div class="doc-card-grid">{cards}</div>'

    body = f"""<h1>Components</h1>
<p class="doc-subtitle">18 components extracted from the Prometheus web UI · all match patterns in <a href="audit-report.html">audit-results.json</a></p>
{sections}"""
    write("components.html", page("Components", body))

# ─── Individual component pages ───────────────────────────────────────────────

def gen_component_page(comp):
    slug = comp["slug"]
    name = comp["name"]
    prefix = "../"

    # Do / don't
    dos = [d for d in comp.get("dos_and_donts", []) if d["type"] == "do"]
    donts = [d for d in comp.get("dos_and_donts", []) if d["type"] == "dont"]
    dd_items = []
    for i in range(max(len(dos), len(donts))):
        do_html = f'<div class="do-item"><strong>✓ Do</strong>{esc(dos[i]["text"])}</div>' if i < len(dos) else '<div></div>'
        dont_html = f'<div class="dont-item"><strong>✗ Don\'t</strong>{esc(donts[i]["text"])}</div>' if i < len(donts) else '<div></div>'
        dd_items.append(do_html + dont_html)
    dd_grid = f'<div class="do-dont-grid">{"".join(dd_items)}</div>' if dd_items else ""

    # Variants preview
    variant_previews = ""
    for v in comp.get("variants", []):
        mock_html = v.get("mock_html") or ""
        toks = ", ".join(v.get("tokens_used", []))
        variant_previews += f"""<h3>{esc(v["name"])}</h3>
<p style="font-size:13px;color:var(--doc-text-secondary)">{esc(v.get("description",""))}</p>
<div class="mock-preview">{mock_html}</div>
{"<p style='font-size:11px;color:var(--doc-text-secondary)'>Tokens: <code>" + esc(toks) + "</code></p>" if toks else ""}"""

    # Layout specs
    spec_rows = "\n".join(
        f'<tr><td>{esc(s["property"])}</td><td><code>{esc(s["value"])}</code>'
        f'{"<br><small>token: <code>" + esc(s["token"]) + "</code></small>" if s.get("token") else ""}</td></tr>'
        for s in comp.get("layout", {}).get("specs", [])
    )
    spec_table = f'<table class="spec-table"><tbody>{spec_rows}</tbody></table>' if spec_rows else ""

    # Accessibility
    a11y = comp.get("accessibility", {})
    a11y_items = ""
    for key, label in [("aria_labels","ARIA"), ("keyboard","Keyboard"), ("contrast","Contrast"), ("screen_reader","Screen reader")]:
        val = a11y.get(key)
        if val:
            a11y_items += f'<tr><td><b>{label}</b></td><td>{esc(val)}</td></tr>'
    a11y_table = f'<table><tbody>{a11y_items}</tbody></table>' if a11y_items else "<p>No specific accessibility requirements noted.</p>"

    # Code example
    code_ex = comp.get("code_example") or ""
    code_section = f"<h2 id='implementation'>Implementation</h2>{code_block(code_ex)}" if code_ex else ""

    # Related inconsistencies
    incs = comp.get("related_inconsistencies", [])
    inc_links = ""
    if incs:
        inc_links = "<p style='font-size:13px'>Related inconsistencies: " + " ".join(
            f'<a href="../inconsistencies.html#{i.lower()}">{i}</a>' for i in incs
        ) + "</p>"

    # Screenshots
    pages_list = comp.get("pages", [])
    screenshot_items = ""
    for pg_url in pages_list[:3]:
        pg_slug = pg_url.strip("/").replace("/", "-") or "index"
        light_path = f"../screenshots/{pg_slug}-light.jpg"
        dark_path = f"../screenshots/{pg_slug}-dark.jpg"
        screenshot_items += f"""<div>
  <p style="font-size:12px;color:var(--doc-text-secondary)">{esc(pg_url)} — <a href="https://prometheus-e83j.onrender.com{esc(pg_url)}" target="_blank">Live ↗</a></p>
  <div style="display:flex;gap:8px">
    <img src="{light_path}" alt="Light screenshot" style="max-width:48%;border:1px solid var(--doc-border);border-radius:4px" onerror="this.style.display='none'">
    <img src="{dark_path}" alt="Dark screenshot" style="max-width:48%;border:1px solid var(--doc-border);border-radius:4px" onerror="this.style.display='none'">
  </div>
</div>"""

    body = f"""<h1>{esc(name)}</h1>
<p class="doc-subtitle">{esc(comp.get("subtitle",""))}</p>

{dd_grid}

<h2 id="description">Description</h2>
<p>{esc(comp.get("description",""))}</p>
<p>{badge(comp["complexity"])}&nbsp;{badge(comp["category"],"gray")}&nbsp;{'&nbsp;'.join(badge(pg,"gray") for pg in pages_list)}</p>
{inc_links}

<h2 id="design">Design variants</h2>
{variant_previews}

{f'''<details>
<summary>Component Reference — screenshots &amp; live links</summary>
<div class="details-body">{screenshot_items}</div>
</details>''' if screenshot_items else ""}

{code_section}

<h2 id="layout">Layout specifications</h2>
{spec_table}

<h2 id="accessibility">Accessibility</h2>
{a11y_table}"""

    write(f"components/{slug}.html", page(name, body, prefix=prefix))

# ─── action-items.html ─────────────────────────────────────────────────────────

def gen_action_items():
    cards = ""
    for ai in action_items:
        labels_html = " ".join(badge(l, "gray") for l in ai.get("labels", []))
        before = ai.get("before_after", {}) or {}
        diff_html = ""
        if before.get("diff"):
            diff_html = f"<h4>Diff</h4>{code_block(before['diff'])}"
        elif before.get("before_html") and before.get("after_html"):
            diff_html = f"""<div class="action-card-before-after">
  <div class="action-card-before"><h4>Before</h4>{code_block(before['before_html'])}</div>
  <div class="action-card-after"><h4>After</h4>{code_block(before['after_html'])}</div>
</div>"""

        rel_inc = ai.get("related_inconsistency")
        inc_link = f'<a href="inconsistencies.html#{rel_inc.lower()}" style="font-size:12px">{rel_inc}</a>&nbsp;' if rel_inc else ""

        files = ai.get("files_changed") or []
        files_html = ""
        if files:
            files_html = "<p style='font-size:12px;color:var(--doc-text-secondary)'>Files: " + " ".join(f"<code>{esc(f)}</code>" for f in files) + "</p>"

        issue_title = esc(ai.get("github_issue_title") or "")

        cards += f"""<div class="action-card" data-issue-title="{issue_title}">
  <div class="action-card-header">
    <span class="action-card-id">{esc(ai["id"])}</span>
    {inc_link}
    {priority_badge(ai["priority"])}
    {effort_badge(ai["effort"])}
    {labels_html}
    <span class="action-card-title">{esc(ai["title"])}</span>
  </div>
  <div class="action-card-body">
    <p>{esc(ai["description"])}</p>
    {files_html}
    {diff_html}
  </div>
</div>"""

    body = f"""<h1>Action Items</h1>
<p class="doc-subtitle">9 PR-ready fix cards derived from inconsistency analysis · click "↗ Open GitHub Issue" to file in <a href="https://github.com/prometheus/prometheus" target="_blank">prometheus/prometheus</a></p>
{cards}"""
    write("action-items.html", page("Action Items", body))

# ─── inconsistencies.html ─────────────────────────────────────────────────────

def gen_inconsistencies():
    items = ""
    for inc in inconsistencies:
        severity = inc.get("severity", "minor")
        variants_html = "".join(
            f'<li style="font-size:13px"><b>{esc(v["page"])}</b> — {esc(v["implementation"])}</li>'
            for v in inc.get("variants", [])
        )
        items += f"""<div class="inc-item severity-{esc(severity)}" id="{esc(inc['id'].lower())}">
  <div class="inc-id">{esc(inc['id'])} · {esc(severity)} · {esc(inc.get('type',''))}</div>
  <div class="inc-title">{esc(inc['title'])}</div>
  <div class="inc-canonical">{esc(inc['canonical'])}</div>
  <div class="inc-reasoning">{esc(inc['reasoning'])}</div>
  <ul style="margin:8px 0 0 16px">{variants_html}</ul>
  <p style="margin-top:8px;font-size:12px">Pages: {', '.join(f'<code>{esc(p)}</code>' for p in inc.get('pages',[]))}</p>
</div>"""

    body = f"""<h1>Inconsistencies</h1>
<p class="doc-subtitle">9 inconsistencies identified during Phase 1 visual audit — INC-001 through INC-009</p>
<div class="callout callout-info">Each entry includes the observed variation, canonical resolution, and a link to the corresponding action item.</div>
{items}"""
    write("inconsistencies.html", page("Inconsistencies", body))

# ─── audit-report.html ────────────────────────────────────────────────────────

def gen_audit_report():
    pages_rows = "\n".join(
        f'<tr><td><code>{esc(p["url"])}</code></td><td>{esc(p["name"])}</td>'
        f'<td>{", ".join(esc(e) for e in p.get("elements",[]))}</td></tr>'
        for p in audit["pages_audited"]
    )
    pattern_rows = "\n".join(
        f'<tr><td>{esc(pat["name"])}</td><td>{badge(pat["category"],"gray")}</td>'
        f'<td>{pat["instance_count"]}</td><td>{pat["variation_count"]}</td>'
        f'<td style="font-size:12px">{", ".join(esc(pg) for pg in pat.get("pages",[]))}</td></tr>'
        for pat in audit["patterns"]
    )
    obs = audit.get("raw_observations", {})
    lp = obs.get("light_palette", {})
    dp = obs.get("dark_palette", {})
    palette_rows = "\n".join(
        f'<tr><td><code>{esc(k)}</code></td>'
        f'<td><span style="background:{esc(lp.get(k,""))}; display:inline-block; width:16px; height:16px; border:1px solid var(--doc-border); border-radius:2px; vertical-align:middle"></span> <code>{esc(lp.get(k,"—"))}</code></td>'
        f'<td><span style="background:{esc(dp.get(k,""))}; display:inline-block; width:16px; height:16px; border:1px solid var(--doc-border); border-radius:2px; vertical-align:middle"></span> <code>{esc(dp.get(k,"—"))}</code></td></tr>'
        for k in set(list(lp.keys()) + list(dp.keys()))
    )
    body = f"""<h1>Audit Report</h1>
<p class="doc-subtitle">Phase 1 visual audit · {audit['audit_date']} · tool: {audit['tool']} · <a href="{esc(audit['app_url'])}" target="_blank">{esc(audit['app_url'])}</a></p>

<h2 id="scope">Scope</h2>
<p>{esc(audit['scope']['description'])}</p>
<table>
<thead><tr><th>URL</th><th>Name</th><th>Elements audited</th></tr></thead>
<tbody>{pages_rows}</tbody>
</table>

<h2 id="patterns">All 18 Patterns</h2>
<table>
<thead><tr><th>Name</th><th>Category</th><th>Instances</th><th>Variations</th><th>Pages</th></tr></thead>
<tbody>{pattern_rows}</tbody>
</table>

<h2 id="palette">Raw Palette</h2>
<div class="callout callout-warn">Error badge exact values not captured — estimated from Mantine red palette. Re-capture with a Playwright script if pixel-exact values are required.</div>
<table>
<thead><tr><th>Token</th><th>Light</th><th>Dark</th></tr></thead>
<tbody>{palette_rows}</tbody>
</table>

<h2 id="framework">Framework Notes</h2>
<p>{esc(audit.get('framework_notes',''))}</p>

<h2 id="screenshots">Screenshot Limitation</h2>
<p class="callout callout-warn">{esc(obs.get('screenshot_limitations',''))}</p>"""
    write("audit-report.html", page("Audit Report", body))

# ─── patterns.html ────────────────────────────────────────────────────────────

def gen_patterns():
    body = """<h1>Composition Patterns</h1>
<p class="doc-subtitle">How components are combined at the page level</p>

<h2 id="list-page">List page pattern</h2>
<p>Used on /alerts, /rules, /targets, /service-discovery. Combines: Filter Input (Pills) at the top, then either an Accordion (targets) or a flat list of Cards with inline content.</p>
<pre><code>FilterInput (Pills)
  └── [Mantine Accordion | Card list]
       └── Table rows | Label Badges | Health Status Badges</code></pre>

<h2 id="status-page">Status / metadata page pattern</h2>
<p>Used on /status, /tsdb-status. Stacked Cards, each with a Card Title (with or without icon) over a Key-Value Table.</p>
<pre><code>Card (Card Title with Icon)
  └── Key-Value Table
Card (Card Title without Icon)
  └── Key-Value Table</code></pre>

<h2 id="config-page">Config / code page pattern</h2>
<p>Used on /config. A single Card containing a YAML Code Block with a Copy Button in the top-right corner.</p>
<pre><code>Card
  └── Copy Button (top-right)
  └── YAML Code Block</code></pre>

<h2 id="empty-state">Empty state pattern</h2>
<p>Shared across /alerts, /rules, /alertmanager-discovery. When a list has no data, replace the list with a Mantine Alert Info Callout.</p>
<pre><code>if (items.length === 0):
  Mantine Alert Info Callout
else:
  [list content]</code></pre>

<h2 id="label-comparison">Label comparison pattern</h2>
<p>Unique to /service-discovery. The Discovered/Target Labels Layout places two groups of Label Badges side-by-side so users can see before/after relabeling.</p>
<pre><code>Grid (2 cols)
  ├── Discovered Labels column: Label Badge[]
  └── Target Labels column:    Label Badge[]</code></pre>

<h2 id="query-toolbar">Query toolbar pattern</h2>
<p>Unique to /query. The most complex surface — a dense toolbar with nine distinct button variants followed by a result panel.</p>
<pre><code>Group (horizontal)
  ├── Primary Button (Execute)
  ├── Button (subtle) × 2
  ├── SegmentedControl
  └── ActionIcon × n
Result panel (Graph | Table | Explain)</code></pre>"""
    write("patterns.html", page("Patterns", body))

# ─── figma.html ───────────────────────────────────────────────────────────────

def gen_figma():
    body = f"""<h1>Figma Plugin</h1>
<p class="doc-subtitle">Bootstrap Figma variables from the extracted token set</p>

<div class="callout callout-info">The plugin bootstraps color variables, text styles, and effects from <code>tokens.json</code>. Import via Figma → Plugins → Development → Import plugin from manifest.</div>

<h2 id="install">Installation</h2>
<ol>
<li>Download <code>figma-plugin.zip</code> from the project folder.</li>
<li>Unzip to a local directory.</li>
<li>In Figma: Plugins → Development → Import plugin from manifest → select <code>manifest.json</code>.</li>
<li>Run the plugin from Plugins → Development → Prometheus Design System.</li>
</ol>

<h2 id="what-it-creates">What the plugin creates</h2>
<table>
<thead><tr><th>Figma artefact</th><th>Source</th></tr></thead>
<tbody>
<tr><td>Color variables (brand, status, surface, text, border)</td><td><code>tokens.json → colors</code></td></tr>
<tr><td>Text styles (heading, body, label, code)</td><td><code>tokens.json → typography.styles</code></td></tr>
<tr><td>Drop shadow effects</td><td><code>tokens.json → elevation</code></td></tr>
</tbody>
</table>

<h2 id="font-notes">Font notes</h2>
<ul style="font-size:13px;margin-left:16px">
<li>Body font maps to <b>Inter</b> — always bundled in Figma.</li>
<li>Mono font maps to <b>Courier New</b> — bundled; DejaVu Sans Mono and Roboto Mono are not available.</li>
<li>Font weights are wrapped in try/catch — families that only ship "Regular" will gracefully fall back.</li>
<li>Use "Semi Bold" (with space) not "SemiBold" for Figma font weight strings.</li>
</ul>

<h2 id="tokens-used">Token preview</h2>
<table>
<thead><tr><th>Variable name</th><th>Value</th></tr></thead>
<tbody>
{''.join(f'<tr><td><code>{esc(c["name"])}</code></td><td><span style="background:{esc(c["value"])};display:inline-block;width:14px;height:14px;border-radius:2px;border:1px solid var(--doc-border);vertical-align:middle"></span> <code>{esc(c["value"])}</code></td></tr>' for c in tokens["colors"]["brand"])}
</tbody>
</table>"""
    write("figma.html", page("Figma Plugin", body))

# ─── changelog.html ───────────────────────────────────────────────────────────

def gen_changelog():
    body = f"""<h1>Changelog</h1>
<p class="doc-subtitle">Version history of the Prometheus Design System</p>

<h2 id="v1-0-0">v1.0.0 — 2026-04-22</h2>
<p>Initial extraction from <a href="https://prometheus-e83j.onrender.com" target="_blank">prometheus-e83j.onrender.com</a>.</p>
<ul style="margin-left:16px;font-size:13px">
<li>Phase 1 visual audit: 10 pages, 18 patterns, 9 inconsistencies (claude-cowork)</li>
<li>Phase 2: token extraction — colors, spacing, typography, radius, elevation, icons</li>
<li>Phase 3: component extraction — 18 components with variants, specs, a11y, code examples</li>
<li>Phase 4: docs site — static HTML/CSS/JS, light + dark theme, mobile-responsive</li>
<li>Phase 5: Figma plugin — bootstraps color variables and text styles</li>
</ul>"""
    write("changelog.html", page("Changelog", body))

# ─── README.md ────────────────────────────────────────────────────────────────

def gen_readme():
    content = """# Prometheus Design System

Generated from a visual audit of https://prometheus-e83j.onrender.com

## Structure

- `index.html` — home page
- `tokens.html` — design token docs
- `icons.html` — icon inventory
- `components.html` — component overview
- `components/<slug>.html` — individual component pages (18)
- `patterns.html` — composition patterns
- `action-items.html` — PR-style fix cards
- `inconsistencies.html` — INC-001 through INC-009
- `audit-report.html` — full audit findings
- `figma.html` — Figma plugin docs
- `changelog.html` — version history
- `figma-plugin/` — Figma plugin source
- `styles.css` — single global stylesheet
- `main.js` — theme toggle, copy buttons, nav

## Run locally

```
npx serve . -l 3000
```
"""
    write("README.md", content)

# ─── Main ─────────────────────────────────────────────────────────────────────

print("Generating docs site...")
gen_index()
gen_tokens()
gen_icons()
gen_components_index()
for comp in components:
    gen_component_page(comp)
gen_action_items()
gen_inconsistencies()
gen_audit_report()
gen_patterns()
gen_figma()
gen_changelog()
gen_readme()
print(f"Done — {len(list(BASE.rglob('*.html')))} HTML files generated.")
