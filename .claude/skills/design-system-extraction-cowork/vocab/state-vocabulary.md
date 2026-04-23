---
title: State Vocabulary
description: Controlled vocabulary for additional_screenshots[].state keys in audit-results.json
---

# State Vocabulary

Use these state keys in `additional_screenshots[].state`. The validator enforces prefix matching.

## Theme States

- `light-theme` — default light color scheme
- `dark-theme` — dark color scheme

## Modal States

- `modal-open-<name>` — a named modal is open (e.g. `modal-open-settings`, `modal-open-delete-confirm`)

## Tab States

- `tab-<name>` — a specific tab is active (e.g. `tab-graph`, `tab-table`, `tab-labels`)

## Hover States

- `hover-<selector>` — element matching selector is hovered (e.g. `hover-target-row`, `hover-nav-item`)

## Expanded States

- `expanded-<group>` — a named accordion or collapsible group is expanded (e.g. `expanded-node_exporter`, `expanded-advanced-options`)

## Error States

- `error-<code>` — an error state is shown (e.g. `error-503`, `error-no-data`, `error-auth`)

## Loading / Empty States

- `empty-state` — page or component shows empty/no-data state
- `loading-state` — page or component shows loading/skeleton state
