# Prometheus Design System

A design system proposal for the [Prometheus](https://prometheus.io/) monitoring UI. Built on **Mantine 8 + React 19 + TypeScript** — the same stack already used in the Prometheus web interface.

> **Work in Progress — Early Draft**
> This is a very early version of a design system proposal for the Prometheus UI. It is actively being worked on and not yet ready for review. Feedback is welcome, but nobody is expected to give feedback at this stage.

## What this solves

The Prometheus UI has grown organically, resulting in fragmented patterns across pages. This design system extracts, normalizes, and documents 19 components and a shared token layer to fix concrete problems found during a [deep codebase audit](audit-report.html):

- **Fragmented health badge system** → unified `StatusBadge` component
- **Dual border inconsistency** (AlertsPage vs RulesPage) → `HealthPanel`
- **4 different filter bar implementations** → `FilterToolbar`
- **Hardcoded colors/spacing** → design tokens with `light-dark()` theming

## Components

| Component | Description |
|---|---|
| StatusBadge | Unified health/state badge across all pages |
| HealthPanel | Bordered panel with consistent header styling |
| LabelBadge | Label key-value pair display |
| FilterToolbar | Shared filter bar with search, state select, collapse |
| InfoCard | Metric/info card for status pages |
| InfoPageLayout | Two-column layout for info pages |
| DataTable | Sortable, filterable data table |
| KeyValueTable | Key-value pair table (flags, config) |
| CodeBlock | Syntax-highlighted code with copy button |
| SeriesName | Metric series name with formatted labels |
| EndpointLink | Clickable endpoint URL with scrape metadata |
| EmptyState | Empty/no-results state placeholder |
| ErrorAlert | Error banner with retry action |
| PoolAccordion | Collapsible pool/group container |
| NavButton | Top navigation tab button |
| StateMultiSelect | Multi-select dropdown for state filtering |
| SettingsPanel | Settings/preferences panel |
| ThemeToggle | Light/dark mode toggle |
| PrometheusAppShell | Top-level app shell with nav and layout |

## Documentation site

The docs site is a static HTML/CSS/JS bundle — no build step required.

### Run locally

```bash
npx serve . -l 3000
```

Then open [http://localhost:3000](http://localhost:3000).

### Site structure

```
├── index.html                  # Introduction
├── principles.html             # Design principles
├── tokens.html                 # Design tokens
├── accessibility.html          # Accessibility guidelines
├── architecture-decisions.html # ADRs
├── components.html             # Component overview
├── components/                 # 19 component pages
├── patterns.html               # UI patterns
├── figma.html                  # Figma structure guide
├── icons.html                  # Icon inventory
├── changelog.html              # Changelog
├── next-steps.html             # Roadmap + migration guide
├── contributing.html           # Contributing guidelines
├── inconsistencies.html        # Inconsistency log
├── audit-report.html           # Full codebase audit
├── screenshots/                # Prometheus UI reference screenshots
├── figma-plugin/               # Figma bootstrap plugin
├── styles.css
└── main.js
```

## Roadmap

| Version | Milestone |
|---|---|
| **v0.1.0** (current) | 19 components extracted, 9 inconsistencies resolved, documentation site |
| **v0.2.0** | Prometheus 3.x components (native histograms, UTF-8 label display), npm publish |
| **v0.3.0** | Upstream PRs merged, Storybook integration, Figma component library |
| **v1.0.0** | Stable API, full test coverage, adopted in `prometheus/prometheus` |

## License

This project is intended to be contributed upstream to the [Prometheus](https://github.com/prometheus/prometheus) project under the Apache 2.0 License.
