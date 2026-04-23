# Prometheus Design System — Audit Report

**Reference:** https://andrejkiri.github.io/prometheus-design-system/
**Skill output:** https://andrejkiri.github.io/prometheus-design-system/skill-output/

Focus: visual design + structure & features. Format: bullet list. Screenshots: embedded layout diagrams (see note below).

---

## Overall verdict

The two sites are clearly the same *kind* of thing — a Prometheus design-system documentation site with a dark header, left-sidebar navigation, and a main content area. Colors, nav dark-slate background (`rgb(65,73,81)`) and Mantine-blue accent (`rgb(34,139,230)` / `#228be6`) match. Tokens pages describe the same families (colors, typography, spacing, radius, elevation). Patterns pages cover roughly the same six patterns. Both generate Figma plugin artefacts.

Where they diverge is in **taxonomy, depth, and framing**: the reference is a code-author's view of the system (React component names, detailed CSS variable table, per-component pages, 18 before/after action-item cards, migration guide), while the skill-output is a DOM-audit's view (design-descriptive component names, shorter token list, INC-/AI- coded findings, extra Audit Report + Inconsistencies + Changelog reference pages). Same system, different lens.

---

## Homepage layout — side-by-side mock

![Reference homepage layout](images/layout-reference.png)

![Skill-output homepage layout](images/layout-skill.png)

> These are simplified layout diagrams rendered from the actual content I captured, not pixel screenshots of the live sites. My sandbox's outbound network policy blocks `andrejkiri.github.io`, so I could fetch the rendered HTML/text via the tool-bridged `web_fetch` but could not drive Playwright against the live URLs. The companion file **`live-comparison.html`** opens both sites side-by-side in iframes for pixel-accurate visual diffing in your browser.

---

## Header / top bar

- Both use a dark slate header (`rgb(65,73,81)`), white text, burger menu on the left, `🌙` theme toggle on the right — same silhouette.
- **Wordmark differs:** reference reads `Prometheus Design System`; skill output prefixes it with a flame emoji → `🔥 Prometheus Design System`.
- **Version chip:** reference shows a `v0.1.0 — WIP` pill next to the wordmark that links to the changelog. Skill output has no version chip in the header.
- Skill output exposes the changelog in the sidebar ("Reference → Changelog") instead of the header.

## Left sidebar / primary navigation

- Reference groups nav as a flat list (`Home`, `Design Tokens`, `Icon Inventory`) followed by a single `Components` header with 20 links below it (Overview + 19 components), then `UI Patterns` and `Action Items` at the bottom.
- Skill output uses **three explicit section headers** — `Overview`, `Components`, `Reference` — each with labels above a grouped list.
- `Overview` in skill-output flattens `Home / Tokens / Icons / Patterns` together, whereas the reference keeps Patterns at the bottom alongside Action Items.
- `Reference` section is **skill-only**: `Action Items`, `Inconsistencies`, `Audit Report`, `Figma Plugin`, `Changelog`. Reference has none of these as dedicated sidebar entries except Action Items.
- **Component list length:** reference lists 19 components (PascalCase React names); skill lists 18 components (human-readable names, see Components section).
- Active-state styling looks visually similar — both highlight the current item with the Mantine blue `primary-color-filled`.

## Homepage content

- **Page H1:** both "Prometheus Design System" — match.
- **Tagline/subtitle:**
  - Reference: "A design system proposal for the Prometheus monitoring UI."
  - Skill: "Extracted from prometheus-e83j.onrender.com via visual audit · 2026-04-21 · Mantine v7+"
- Reference has a **"Work in Progress — Early Draft" yellow callout** with a paragraph about feedback — missing from skill output.
- Reference has a **provenance paragraph** ("Every token, component, and pattern here was derived from the actual Prometheus codebase…") — skill replaces this with a one-liner stat line "10 pages audited · 18 patterns catalogued · 9 inconsistencies identified · light + dark themes".
- **Explore card grid:**
  - Reference has **5 cards** (Design Tokens, Icon Inventory, Components, UI Patterns, Action Items) each with a category tag (`FOUNDATIONS`, `COMPONENTS`, `PATTERNS`, `ROADMAP`).
  - Skill has **9 cards** with leading emoji on each (🎨 Tokens, 🔣 Icons, 🧩 Components, 🔗 Patterns, 🛠 Action Items, 🔍 Audit Report, ⚠️ Inconsistencies, 🔌 Figma Plugin, 📋 Changelog). Cards have no category tag.
- Skill adds an **"At a glance" table** (Pages audited / UI patterns / Inconsistencies / Framework / Themes / Brand color / Nav background) — not present in reference.
- Reference has an **"Acknowledgements"** section (Julius Volz, nicholasgasior, contributors) — not present in skill output.

## Design Tokens page

- Both document: brand / surface colors, status colors, typography (families + sizes + weights), spacing, border radius, elevation, borders. Core structure overlaps.
- **Reference is considerably deeper.** It adds:
  - A full **five-state Health badge matrix** (ok / err / warn / info / unknown) with light- and dark-mode swatches and panel-border variants, plus live rendered badge examples.
  - **PromQL syntax colors** table (keyword, labelName, string, number/duration × light/dark).
  - **Semantic spacing tokens** (`headerLogoNavGap`, `mainPadding`, `cardPadding`, `infoPageMaxWidth`, `healthPanelBorderWidth`, `actionIconSize`, etc.).
  - **Motion / Transitions** table (`hoverReveal`, `accordionChevron`, `backgroundTransition`, `interactiveHover`, `dataTransition`).
  - **Breakpoints** table with Mantine breakpoint values and "Responsive Patterns" (navbar collapse, logo text visibility thresholds).
  - A full **`--prom-*` CSS custom-property reference** (~40 variables).
  - Text-style naming convention ready for Figma (e.g. `heading/page`, `body/default`, `code/metric`).
- **Skill is lighter**: brand / status / surface / text / border color tables, a short spacing list, typography families + 7 styles, radius (only 3 tokens: `sm`, `pill`, `pill-max`), and elevation (only `card`). It omits motion, breakpoints, PromQL syntax colors, semantic spacing, and the `--prom-*` variable catalogue.
- **Color values are consistent** where both mention the same token: nav `rgb(65,73,81)`, Mantine blue `rgb(34,139,230)` / `#228be6`, gray-1 `#f1f3f5`, etc.
- Skill references the source app URL (`prometheus-e83j.onrender.com`) as where values were "extracted from" — reference says values were "derived from the codebase."
- Skill exposes INC-numbered callouts in-line (e.g. "…see INC-009"); reference does not.

## Icon Inventory page

- Both name Tabler Icons as the library, both note `stroke-width: 2`, both list default size 18px.
- **Reference catalogues ~21 icons** organized into four groups — Navigation, Status & Health, Data & Content, Action — each row with a rendered icon, Tabler name, React import symbol (`IconMenu2`, `IconChevronDown`…) and usage description. Includes **Do / Don't guidelines** and a Figma implementation note.
- **Skill catalogues 12 icons** in a single flat table with name + usage only, and explicitly notes "SVG paths were not captured in the visual audit." Icons are listed as names rather than rendered glyphs. It has a short "Do / Don't" block but no import-symbol column.
- Only the skill mentions icons like `database`, `run`, `bell-off`, `book`; only the reference covers `menu-2`, `arrows-minimize`, `circle-check`, `circle-x`, `alert-triangle`, `info-circle`, `circle-minus`, `file-description`, `server`, `settings`, `activity`, `table`, `cpu`, `file-check`, `flag`, `send`. Overlap: `sun`, `moon`, `search`, `clipboard`, `chevron-down`, `bell`.

## Components overview page

- **Component count:** reference 19, skill 18.
- **Component naming style:** reference uses PascalCase React-component names (`AppShell`, `DataTable`, `StatusBadge`, `ThemeToggle`, `SettingsPanel`); skill uses design-descriptive labels (`Header/Navbar`, `Sortable Table`, `Health Status Badge`, `Primary Button`, `Button Variants Group`, `Mantine Card`, `Mantine Accordion`, `Mantine Alert Info Callout`, `YAML Code Block`, `Copy Button`, etc.). Several skill names embed "Mantine" directly.
- **Grouping:** skill groups components under explicit H2 category sections (`Data Display`, `Feedback`, `Input`, `Layout`, `Navigation`); reference shows a flat list of cards with per-card category tags.
- **Overlap (same underlying UI):**
  - `LabelBadge` ⇔ `Label Badge`
  - `KeyValueTable` ⇔ `Key-Value Table`
  - `StatusBadge` / `HealthPanel` ⇔ `Health Status Badge`
  - `DataTable` ⇔ `Sortable Table`
  - `PoolAccordion` ⇔ `Mantine Accordion`
  - `CodeBlock` ⇔ `YAML Code Block`
  - `FilterToolbar` ⇔ `Filter Input (Pills)` / `Filter Input (Single Field)` (split in two in skill)
  - `NavButton` / `AppShell` ⇔ `Header/Navbar`
  - `ErrorAlert` ⇔ `Mantine Alert Info Callout` (loose)
  - `EmptyState` ⇔ (none in skill, or folded into the Alert callout)
- **Reference-only components:** `AppShell` (as separate page), `EmptyState`, `EndpointLink`, `ErrorAlert`, `InfoCard`, `InfoPageLayout`, `NavButton`, `SeriesName`, `SettingsPanel`, `StateMultiSelect`, `ThemeToggle`. Also per-component detail pages for each (`/components/*.html`).
- **Skill-only components:** `Card Title with Icon`, `Card Title without Icon`, `Primary Button`, `Button Variants Group`, `Discovered/Target Labels Layout`, `Stats Badge` (split out), `Copy Button`, `YAML Code Block` as a first-class component.
- Reference announces a **Figma plugin download** (`figma-plugin.zip — 11 KB`) directly on the Components overview; skill links to a dedicated Figma Plugin reference page.

## UI Patterns page

- Both pages cover six patterns with the same broad coverage (list pages, status/info pages, query toolbar, empty states, config/code, accordion + filter composition).
- **Reference patterns:** Info Page Pattern, Accordion List Pattern, Query Panel Pattern, Filter Bar Pattern, Suspense + ErrorBoundary Composition, URL-Persistent State. Each includes a code block showing the composition and tables of variations (per-page state options, URL params).
- **Skill patterns:** List page, Status/metadata page, Config/code page, Empty state, Label comparison, Query toolbar. Each includes an ASCII tree showing component composition.
- Reference patterns are implementation-deep (`<Suspense>` + `<ErrorBoundary>` wrapping, `useSuspenseAPIQuery` semantics, URL query-param table tied to `use-query-params`). Skill patterns are composition-level (which components stack inside which).
- **Label comparison pattern** is explicit in skill (Discovered/Target Labels Layout for `/service-discovery`) but not named as a separate pattern in the reference.

## Action Items page

- Reference lists **18 items** (10 Compliance Tasks PR#1–#10 + 8 Polish Proposals PR#11–#18), plus a **Migration Guide** section with Phase 1–4 adoption guidance and a component-mapping + CSS-variable migration table at the end.
- Skill lists **9 items** (AI-001 through AI-009), each tied to a matching `INC-xxx` on the Inconsistencies page (skill-only).
- Reference items come with **Before / After visual mockups** (rendered badge, border, empty-state examples) and decision cards showing alternative approaches ("Recommended", "Alt"). Skill items are mostly diff + rationale, no visual before/after.
- **Topic overlap** is real but not 1:1. Both address:
  - hardcoded `rgb(65, 73, 81)` header colors → design tokens (Ref PR#1; Skill has no direct match — the nav being theme-invariant slate is documented as intentional in skill's tokens).
  - Unify health status badges (Ref PR#2; Skill AI-007 is narrower — uppercase rendering concern).
  - Unify panel borders (Ref PR#3; not in skill).
  - Extract shared `FilterToolbar` (Ref PR#4; Skill AI-004 proposes migrating `/flags` to PillsInput).
  - localStorage key collision (Ref PR#5; not in skill).
  - SeriesName dark-mode hover (Ref PR#6; not in skill).
  - Logo text visibility gap between `sm`/`md` breakpoints (Ref PR#7; not in skill).
  - Hardcoded spacing values → Mantine tokens (Ref PR#8; not in skill).
  - Logo `fz={20}` → rem token (Ref PR#9; not in skill).
  - Shared icon-style constant (Ref PR#10; not in skill).
- **Skill-only issues:** card-title icon consistency (AI-001), monospace for code-like identifiers (AI-002), Label Badge / Stats Badge casing rules (AI-003), key-value table sort affordance (AI-005), Configuration Reload health badge (AI-006), highlight.js token color swap between themes (AI-008), explicit monospace font stack (AI-009).
- **Polish proposals** (border-bottom on header, EmptyState on Alerts, row hover on Flags, etc.) are reference-only.

## Pages / routes present

- **Both:** `index.html`, `tokens.html`, `icons.html`, `components.html`, `patterns.html`, `action-items.html`.
- **Reference-only:** `changelog.html` (linked from header), 19 per-component pages under `/components/*.html`.
- **Skill-only:** `inconsistencies.html`, `audit-report.html`, `figma.html`, `changelog.html`, and 18 per-component pages under `/components/*.html` (with different slugs — e.g. `header-navbar.html`, `mantine-card.html`, `filter-input-pills.html`).

## Visual / styling feel (inferred from content + tokens declared)

- Both intend the same palette: white surfaces in light, dark slate `rgb(65,73,81)` header always dark, Mantine blue `#228be6` as primary accent, gray-1 `#f1f3f5` for subtle backgrounds.
- Cards in the Explore grid are visually similar (bordered white cards on a light surface) but skill uses a **large leading emoji** as the card's "icon", whereas reference uses no leading icon — the category tag is the visual hook.
- Typography tokens align broadly (system-UI sans body, monospace for code, 14px base body), though exact weight/size tables differ (reference 5 sizes xs–xl 12–20px; skill 7 named styles).
- Reference sub-pages (tokens / icons / patterns / action-items) consistently expose an **"On this page" anchor TOC** at the bottom of the content rail. Skill-output sub-pages I fetched did not render that TOC list.

## Content/tone

- Reference: first-person documentation authored as a proposal ("This is a very early version…", "Feedback is welcome"), with a human acknowledgements section.
- Skill: report-like tone ("Extracted from… via visual audit", "10 pages audited"), uses structured identifiers (INC-001, AI-001, "Phase 1 visual audit"). Reads as machine-generated artefact.

## Things that are the same (so the skill did hit the mark on)

- Overall three-pane layout (header / left sidebar / main + right-rail TOC).
- Dark slate header color, white header text, `🌙` theme toggle, burger menu on mobile.
- Mantine-blue primary accent, neutral card surface.
- Set of main pages (home / tokens / icons / components / patterns / action items) present in both.
- Tokens page families covered (color, typography, spacing, radius, elevation, borders).
- Same Tabler-Icons library declaration with 18px default size and 2-stroke.
- Patterns coverage — both identify list-page, status-info-page, query toolbar, empty-state, and config/code patterns.
- Both ship a Figma plugin / Figma integration story.

## Biggest structural gaps if you want the skill output closer to the reference

1. Add version chip + "Work in Progress" callout to the home header/hero.
2. Add an **Acknowledgements** section on home.
3. Rename components to PascalCase engineering names and add per-component detail pages matching reference's 19-page set.
4. Expand the Tokens page to include: breakpoints, motion, PromQL colors, semantic spacing, `--prom-*` variable reference, and the full health-badge matrix (5 states × light/dark × badge/panel-border).
5. Expand the Icons page to ~23 icons grouped into Navigation / Status & Health / Data & Content / Action with rendered glyphs and import symbols.
6. Bulk up Action Items to ~18 entries with before/after visual mockups and a Migration Guide (Phases 1–4) at the end.
7. Drop the Reference section (or keep but consolidate) — the reference site doesn't expose Audit Report / Inconsistencies / Changelog as top-level sidebar pages.
8. Swap the 9 emoji-cards grid for the reference's 5 category-tagged cards (Foundations / Components / Patterns / Roadmap).

---

## How to verify visually

Open **`live-comparison.html`** in a browser (double-click the file). It loads both sites side-by-side in iframes with a page selector, so you can flip between Home / Tokens / Icons / Components / Patterns / Action Items and eyeball each pane. Both frames are the actual live sites — nothing about them is cached or modified here.

---

*Generated 2026-04-23 from `web_fetch` of each site's HTML. Reference pages fetched: home, tokens, icons, components, patterns, action-items. Skill-output pages fetched: home, tokens, icons, components, patterns, action-items.*
