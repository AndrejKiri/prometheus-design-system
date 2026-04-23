# Prometheus Design System

A design system proposal for the [Prometheus](https://prometheus.io/) monitoring UI. Built on **Mantine 8 + React 19 + TypeScript** — the same stack already used in the Prometheus web interface.

> **Work in Progress — Early Draft**
> This is a very early version of a design system proposal for the Prometheus UI. It is actively being worked on and not yet ready for review. Feedback is welcome, but nobody is expected to give feedback at this stage.

## Live preview

The latest skill-output run is published at:
**[https://andrejkiri.github.io/prometheus-design-system/skill-output/](https://andrejkiri.github.io/prometheus-design-system/skill-output/)**

> Deployed automatically from `skill-outputs/` on push to `main`. Source for all runs is preserved in [skill-outputs/](skill-outputs/).

## Documentation site

The docs site is a static HTML/CSS/JS bundle — no build step required.

```bash
npx serve . -l 3000
```

Then open [http://localhost:3000](http://localhost:3000).

### Main pages (in site nav)

- [Home](index.html) — overview and links
- [Design Tokens](tokens.html) — colors, typography, spacing, elevation
- [Icon Inventory](icons.html) — Tabler icons used in the UI
- [Components](components.html) — 19 components with Figma plugin
- [UI Patterns](patterns.html) — recurring layout and interaction patterns
- [Action Items](action-items.html) — concrete tasks and PRs

### Reference pages (not in nav)

- [Figma Structure](figma.html) — Figma library setup guide
- [Audit Report](audit-report.html) — full codebase audit findings
- [Inconsistency Log](inconsistencies.html) — 9 resolved inconsistencies
- [Migration Guide](migration.html) — incremental adoption phases
- [Changelog](changelog.html) — version history

## License

This project is intended to be contributed upstream to the [Prometheus](https://github.com/prometheus/prometheus) project under the Apache 2.0 License.
