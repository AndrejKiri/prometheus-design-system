#!/usr/bin/env python3
"""
Handoff Schema Validator
========================
Validates audit-results.json, tokens.json, and components.json for:
- Required fields and correct types
- Cross-reference integrity (INC IDs, token names, pattern names, slugs)
- Enum value correctness
- File existence (screenshots)

Usage:
    python validate-handoff.py <project-directory>

    The project directory should contain:
    - audit-results.json
    - tokens.json (optional — skips token cross-checks if missing)
    - components.json (optional — skips component cross-checks if missing)
    - screenshots/ (optional — skips screenshot file checks if missing)

Exit codes:
    0 = all checks passed
    1 = one or more checks failed
    2 = missing required files or invalid JSON
"""

import json
import os
import sys
import re
from pathlib import Path

# ─── Enums ───────────────────────────────────────────────────────────────────

SCOPE_TIERS = {"core", "core-plus-data", "full", "custom"}
TOOLS = {"perplexity-computer", "claude-code", "claude-cowork", "manual"}
PATTERN_CATEGORIES = {"navigation", "data-display", "input", "feedback", "layout", "overlay", "media", "utility"}
SEVERITY_LEVELS = {"critical", "major", "minor", "cosmetic"}
INCONSISTENCY_TYPES = {"implementation-drift", "hardcoded-values", "missing-normalization", "style-drift", "duplicated-logic", "accessibility", "responsive"}
AUTH_METHODS = {"username-password", "sso", "api-token", "oauth", "none", None}
TOKEN_SOURCES = {"visual-audit", "source-code", "both"}
COMPLEXITY_LEVELS = {"simple", "medium", "complex"}
DO_DONT_TYPES = {"do", "dont"}
PRIORITY_LEVELS = {"p0-critical", "p1-high", "p2-medium", "p3-low"}
EFFORT_LEVELS = {"easy", "medium", "hard"}
ACTION_LABELS = {"inconsistency", "tokens", "component", "accessibility", "responsive", "documentation", "refactor"}
TYPOGRAPHY_CATEGORIES = {"heading", "body", "label", "code", "display"}
FONT_WEIGHTS = {100, 200, 300, 400, 500, 600, 700, 800, 900}
SLUG_PATTERN = re.compile(r'^[a-z0-9-]+$')

# ─── Reporter ────────────────────────────────────────────────────────────────

class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passes = []
        self.current_file = ""

    def set_file(self, name):
        self.current_file = name

    def error(self, msg):
        self.errors.append(f"[FAIL] {self.current_file}: {msg}")

    def warn(self, msg):
        self.warnings.append(f"[WARN] {self.current_file}: {msg}")

    def ok(self, msg):
        self.passes.append(f"[PASS] {self.current_file}: {msg}")

    def print_report(self):
        print("\n" + "=" * 70)
        print("HANDOFF SCHEMA VALIDATION REPORT")
        print("=" * 70)

        if self.passes:
            print(f"\n--- Passed ({len(self.passes)}) ---")
            for p in self.passes:
                print(f"  {p}")

        if self.warnings:
            print(f"\n--- Warnings ({len(self.warnings)}) ---")
            for w in self.warnings:
                print(f"  {w}")

        if self.errors:
            print(f"\n--- Errors ({len(self.errors)}) ---")
            for e in self.errors:
                print(f"  {e}")

        print("\n" + "-" * 70)
        total = len(self.passes) + len(self.warnings) + len(self.errors)
        print(f"Total checks: {total}")
        print(f"Passed: {len(self.passes)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Errors: {len(self.errors)}")

        if self.errors:
            print("\nRESULT: FAIL")
        elif self.warnings:
            print("\nRESULT: PASS (with warnings)")
        else:
            print("\nRESULT: PASS")

        print("=" * 70)
        return len(self.errors) == 0

# ─── Helpers ─────────────────────────────────────────────────────────────────

def load_json(path, report):
    """Load and parse a JSON file. Returns None on failure."""
    if not path.exists():
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        report.set_file(path.name)
        report.error(f"Invalid JSON: {e}")
        return None

def check_required_field(data, field, expected_type, report, context=""):
    """Check that a required field exists and has the correct type."""
    prefix = f"{context}." if context else ""
    if field not in data:
        report.error(f"Missing required field '{prefix}{field}'")
        return False
    if not isinstance(data[field], expected_type):
        report.error(f"'{prefix}{field}' should be {expected_type.__name__}, got {type(data[field]).__name__}")
        return False
    return True

def check_enum(value, allowed, report, field_name):
    """Check that a value is in the allowed set."""
    if value not in allowed:
        report.error(f"'{field_name}' has invalid value '{value}'. Allowed: {sorted(str(v) for v in allowed if v is not None)}")
        return False
    return True

def check_non_empty_array(data, field, report, context=""):
    """Check that a field is a non-empty array."""
    prefix = f"{context}." if context else ""
    if field not in data:
        report.error(f"Missing required array '{prefix}{field}'")
        return False
    if not isinstance(data[field], list):
        report.error(f"'{prefix}{field}' should be array, got {type(data[field]).__name__}")
        return False
    if len(data[field]) == 0:
        report.error(f"'{prefix}{field}' must not be empty")
        return False
    return True

# ─── audit-results.json ─────────────────────────────────────────────────────

def validate_audit(data, project_dir, report):
    report.set_file("audit-results.json")

    # Top-level required fields
    for field, ftype in [("app_url", str), ("audit_date", str), ("tool", str)]:
        check_required_field(data, field, ftype, report)

    # Tool enum
    if "tool" in data:
        if check_enum(data["tool"], TOOLS, report, "tool"):
            report.ok(f"tool = '{data['tool']}' is valid")

    # Scope object
    if check_required_field(data, "scope", dict, report):
        scope = data["scope"]
        if check_required_field(scope, "tier", str, report, "scope"):
            if check_enum(scope["tier"], SCOPE_TIERS, report, "scope.tier"):
                report.ok(f"scope.tier = '{scope['tier']}' is valid")
        check_required_field(scope, "description", str, report, "scope")
        check_required_field(scope, "total_routes_discovered", int, report, "scope")
        check_required_field(scope, "routes_audited", int, report, "scope")

    # Auth (optional but validate if present)
    if "auth" in data and isinstance(data["auth"], dict):
        auth = data["auth"]
        if "method" in auth:
            check_enum(auth["method"], AUTH_METHODS, report, "auth.method")

    # Pages audited
    page_urls = set()
    page_elements = set()
    screenshot_paths = []

    if check_non_empty_array(data, "pages_audited", report):
        for i, page in enumerate(data["pages_audited"]):
            ctx = f"pages_audited[{i}]"
            check_required_field(page, "url", str, report, ctx)
            check_required_field(page, "name", str, report, ctx)
            check_required_field(page, "screenshot", str, report, ctx)
            check_required_field(page, "elements", list, report, ctx)

            if "url" in page:
                page_urls.add(page["url"])
            if "elements" in page and isinstance(page["elements"], list):
                page_elements.update(page["elements"])
            if "screenshot" in page:
                screenshot_paths.append(page["screenshot"])

            # Additional screenshots
            if "additional_screenshots" in page and isinstance(page["additional_screenshots"], list):
                for j, ss in enumerate(page["additional_screenshots"]):
                    check_required_field(ss, "path", str, report, f"{ctx}.additional_screenshots[{j}]")
                    check_required_field(ss, "state", str, report, f"{ctx}.additional_screenshots[{j}]")
                    if "path" in ss:
                        screenshot_paths.append(ss["path"])

        report.ok(f"pages_audited has {len(data['pages_audited'])} entries")

    # Patterns
    pattern_names = set()
    if check_non_empty_array(data, "patterns", report):
        for i, pat in enumerate(data["patterns"]):
            ctx = f"patterns[{i}]"
            check_required_field(pat, "name", str, report, ctx)
            check_required_field(pat, "pages", list, report, ctx)
            check_required_field(pat, "instance_count", int, report, ctx)
            check_required_field(pat, "variation_count", int, report, ctx)
            check_required_field(pat, "description", str, report, ctx)

            if check_required_field(pat, "category", str, report, ctx):
                check_enum(pat["category"], PATTERN_CATEGORIES, report, f"{ctx}.category")

            if "name" in pat:
                pattern_names.add(pat["name"])

        report.ok(f"patterns has {len(data['patterns'])} entries")

    # Cross-check: every element in pages must have a matching pattern
    orphan_elements = page_elements - pattern_names
    if orphan_elements:
        for elem in sorted(orphan_elements):
            report.error(f"Element '{elem}' appears in pages_audited but has no matching entry in patterns[]")
    else:
        report.ok(f"All {len(page_elements)} element names in pages match pattern entries")

    # Unused patterns (warning only)
    unused_patterns = pattern_names - page_elements
    if unused_patterns:
        for pat in sorted(unused_patterns):
            report.warn(f"Pattern '{pat}' defined but not referenced in any page's elements[]")

    # Inconsistencies
    inconsistency_ids = set()
    if "inconsistencies" in data and isinstance(data["inconsistencies"], list):
        for i, inc in enumerate(data["inconsistencies"]):
            ctx = f"inconsistencies[{i}]"

            if check_required_field(inc, "id", str, report, ctx):
                inc_id = inc["id"]
                if inc_id in inconsistency_ids:
                    report.error(f"{ctx}: Duplicate inconsistency ID '{inc_id}'")
                inconsistency_ids.add(inc_id)

            check_required_field(inc, "title", str, report, ctx)
            check_required_field(inc, "canonical", str, report, ctx)
            check_required_field(inc, "reasoning", str, report, ctx)

            if check_required_field(inc, "severity", str, report, ctx):
                check_enum(inc["severity"], SEVERITY_LEVELS, report, f"{ctx}.severity")

            if check_required_field(inc, "type", str, report, ctx):
                check_enum(inc["type"], INCONSISTENCY_TYPES, report, f"{ctx}.type")

            if check_required_field(inc, "pages", list, report, ctx):
                for page_ref in inc["pages"]:
                    if page_ref not in page_urls:
                        report.error(f"{ctx}: References page '{page_ref}' not found in pages_audited")

            if check_required_field(inc, "variants", list, report, ctx):
                if len(inc["variants"]) < 2:
                    report.error(f"{ctx}: variants must have at least 2 entries (found {len(inc['variants'])})")
                for j, var in enumerate(inc["variants"]):
                    check_required_field(var, "page", str, report, f"{ctx}.variants[{j}]")
                    check_required_field(var, "implementation", str, report, f"{ctx}.variants[{j}]")

        if data["inconsistencies"]:
            report.ok(f"inconsistencies has {len(data['inconsistencies'])} entries with unique IDs")
    else:
        check_required_field(data, "inconsistencies", list, report)

    # Raw observations
    if check_required_field(data, "raw_observations", dict, report):
        obs = data["raw_observations"]
        if "has_dark_mode" not in obs:
            report.warn("raw_observations.has_dark_mode not set")
        else:
            report.ok(f"has_dark_mode = {obs['has_dark_mode']}")

    # Screenshot file existence
    screenshots_dir = project_dir / "screenshots"
    if screenshots_dir.exists():
        missing_screenshots = []
        for ss_path in screenshot_paths:
            full_path = project_dir / ss_path
            if not full_path.exists():
                missing_screenshots.append(ss_path)
        if missing_screenshots:
            for ss in missing_screenshots:
                report.error(f"Screenshot file not found: {ss}")
        else:
            report.ok(f"All {len(screenshot_paths)} screenshot files exist")
    elif screenshot_paths:
        report.warn(f"screenshots/ directory not found — cannot verify {len(screenshot_paths)} screenshot paths")

    return pattern_names, inconsistency_ids, page_urls, data.get("raw_observations", {}).get("has_dark_mode", False)


# ─── tokens.json ─────────────────────────────────────────────────────────────

def validate_tokens(data, audit_url, has_dark_mode, report):
    report.set_file("tokens.json")

    # Top-level required fields
    check_required_field(data, "app_url", str, report)
    check_required_field(data, "extraction_date", str, report)

    # URL match
    if "app_url" in data and audit_url:
        if data["app_url"] != audit_url:
            report.error(f"app_url '{data['app_url']}' does not match audit-results.json '{audit_url}'")
        else:
            report.ok("app_url matches audit-results.json")

    # Source enum
    if check_required_field(data, "source", str, report):
        if check_enum(data["source"], TOKEN_SOURCES, report, "source"):
            report.ok(f"source = '{data['source']}' is valid")

    # Colors
    token_names = set()

    if check_required_field(data, "colors", dict, report):
        colors = data["colors"]
        for subcategory in ["brand", "status", "surface", "text", "border"]:
            if check_non_empty_array(colors, subcategory, report, "colors") if subcategory in ["brand", "status", "surface", "text"] else True:
                if subcategory in colors and isinstance(colors[subcategory], list):
                    for i, entry in enumerate(colors[subcategory]):
                        ctx = f"colors.{subcategory}[{i}]"
                        check_required_field(entry, "name", str, report, ctx)
                        if "name" in entry:
                            token_names.add(entry["name"])

                        # Status colors need light.bg/text/border
                        if subcategory == "status":
                            if check_required_field(entry, "light", dict, report, ctx):
                                light = entry["light"]
                                for prop in ["bg", "text", "border"]:
                                    check_required_field(light, prop, str, report, f"{ctx}.light")
                            if has_dark_mode and "dark" not in entry:
                                report.error(f"{ctx}: App has dark mode but no 'dark' object provided")

                        # Surface/text need light, dark if dark mode
                        if subcategory in ["surface", "text", "border"]:
                            check_required_field(entry, "light", str, report, ctx)
                            if has_dark_mode and "dark" not in entry:
                                report.warn(f"{ctx}: App has dark mode but no 'dark' value")

                        # Figma RGB validation for brand colors
                        if subcategory == "brand" and "figma_rgb" in entry:
                            rgb = entry["figma_rgb"]
                            for ch in ["r", "g", "b"]:
                                if ch in rgb:
                                    if not (0 <= rgb[ch] <= 1):
                                        report.error(f"{ctx}.figma_rgb.{ch} = {rgb[ch]} is out of range [0, 1]")
                            report.ok(f"{ctx} has valid figma_rgb") if all(0 <= rgb.get(ch, 0) <= 1 for ch in ["r", "g", "b"]) else None

            elif subcategory == "border":
                # Border is not strictly required but should exist
                if subcategory not in colors:
                    report.warn("colors.border not present")

        report.ok(f"colors has all required subcategories")

    # Spacing
    if check_required_field(data, "spacing", dict, report):
        if check_non_empty_array(data["spacing"], "scale", report, "spacing"):
            for i, entry in enumerate(data["spacing"]["scale"]):
                ctx = f"spacing.scale[{i}]"
                check_required_field(entry, "name", str, report, ctx)
                check_required_field(entry, "value_px", (int, float), report, ctx)
                if "name" in entry:
                    token_names.add(entry["name"])
            report.ok(f"spacing.scale has {len(data['spacing']['scale'])} entries")

    # Typography
    font_family_names = set()
    if check_required_field(data, "typography", dict, report):
        typo = data["typography"]

        if check_non_empty_array(typo, "families", report, "typography"):
            for i, entry in enumerate(typo["families"]):
                ctx = f"typography.families[{i}]"
                check_required_field(entry, "name", str, report, ctx)
                check_required_field(entry, "family", str, report, ctx)
                check_required_field(entry, "usage", str, report, ctx)
                if "name" in entry:
                    font_family_names.add(entry["name"])
                    token_names.add(entry["name"])

        if check_non_empty_array(typo, "styles", report, "typography"):
            categories_found = set()
            for i, entry in enumerate(typo["styles"]):
                ctx = f"typography.styles[{i}]"
                check_required_field(entry, "name", str, report, ctx)

                if check_required_field(entry, "category", str, report, ctx):
                    check_enum(entry["category"], TYPOGRAPHY_CATEGORIES, report, f"{ctx}.category")
                    categories_found.add(entry["category"])

                check_required_field(entry, "font_family", str, report, ctx)
                if "font_family" in entry and entry["font_family"] not in font_family_names:
                    report.error(f"{ctx}.font_family '{entry['font_family']}' not found in typography.families")

                check_required_field(entry, "size_px", (int, float), report, ctx)

                if check_required_field(entry, "weight", int, report, ctx):
                    check_enum(entry["weight"], FONT_WEIGHTS, report, f"{ctx}.weight")

                check_required_field(entry, "line_height", (int, float), report, ctx)

                if "name" in entry:
                    token_names.add(entry["name"])

            # Check minimum coverage
            for required_cat in ["heading", "body", "code"]:
                if required_cat not in categories_found:
                    report.error(f"typography.styles missing category '{required_cat}' — need at least one heading, body, and code style")
                else:
                    report.ok(f"typography.styles has '{required_cat}' category")

    # Border radius
    if check_non_empty_array(data, "border_radius", report):
        for i, entry in enumerate(data["border_radius"]):
            ctx = f"border_radius[{i}]"
            check_required_field(entry, "name", str, report, ctx)
            check_required_field(entry, "value_px", (int, float), report, ctx)
            if "name" in entry:
                token_names.add(entry["name"])
        report.ok(f"border_radius has {len(data['border_radius'])} entries")

    # Elevation (optional)
    if "elevation" in data and isinstance(data["elevation"], list):
        for i, entry in enumerate(data["elevation"]):
            ctx = f"elevation[{i}]"
            check_required_field(entry, "name", str, report, ctx)
            if check_required_field(entry, "light", dict, report, ctx):
                check_required_field(entry["light"], "css", str, report, f"{ctx}.light")
            if "name" in entry:
                token_names.add(entry["name"])
        report.ok(f"elevation has {len(data['elevation'])} entries")

    return token_names


# ─── components.json ─────────────────────────────────────────────────────────

def validate_components(data, audit_url, pattern_names, inconsistency_ids, token_names, report):
    report.set_file("components.json")

    # Top-level
    check_required_field(data, "app_url", str, report)
    check_required_field(data, "extraction_date", str, report)

    # URL match
    if "app_url" in data and audit_url:
        if data["app_url"] != audit_url:
            report.error(f"app_url '{data['app_url']}' does not match audit-results.json '{audit_url}'")
        else:
            report.ok("app_url matches audit-results.json")

    # Components
    slugs = set()
    component_names = set()

    if check_non_empty_array(data, "components", report):
        for i, comp in enumerate(data["components"]):
            ctx = f"components[{i}]"

            # Name
            if check_required_field(comp, "name", str, report, ctx):
                name = comp["name"]
                component_names.add(name)
                if pattern_names and name not in pattern_names:
                    report.error(f"{ctx}: name '{name}' not found in audit-results.json patterns")

            # Slug
            if check_required_field(comp, "slug", str, report, ctx):
                slug = comp["slug"]
                if not SLUG_PATTERN.match(slug):
                    report.error(f"{ctx}: slug '{slug}' does not match pattern ^[a-z0-9-]+$")
                if slug in slugs:
                    report.error(f"{ctx}: duplicate slug '{slug}'")
                slugs.add(slug)

            check_required_field(comp, "description", str, report, ctx)

            # Complexity enum
            if check_required_field(comp, "complexity", str, report, ctx):
                check_enum(comp["complexity"], COMPLEXITY_LEVELS, report, f"{ctx}.complexity")

            # Category enum
            if check_required_field(comp, "category", str, report, ctx):
                check_enum(comp["category"], PATTERN_CATEGORIES, report, f"{ctx}.category")

            check_required_field(comp, "pages", list, report, ctx)

            # Variants
            if check_non_empty_array(comp, "variants", report, ctx):
                for j, var in enumerate(comp["variants"]):
                    vctx = f"{ctx}.variants[{j}]"
                    check_required_field(var, "name", str, report, vctx)
                    check_required_field(var, "description", str, report, vctx)

                    # Token cross-reference
                    if "tokens_used" in var and isinstance(var["tokens_used"], list) and token_names:
                        for tok in var["tokens_used"]:
                            if tok not in token_names:
                                report.error(f"{vctx}: tokens_used references '{tok}' not found in tokens.json")

            # Layout
            if check_required_field(comp, "layout", dict, report, ctx):
                if check_non_empty_array(comp["layout"], "specs", report, f"{ctx}.layout"):
                    for j, spec in enumerate(comp["layout"]["specs"]):
                        sctx = f"{ctx}.layout.specs[{j}]"
                        check_required_field(spec, "property", str, report, sctx)
                        check_required_field(spec, "value", str, report, sctx)

            # Do/Don't
            if check_non_empty_array(comp, "dos_and_donts", report, ctx):
                for j, dd in enumerate(comp["dos_and_donts"]):
                    dctx = f"{ctx}.dos_and_donts[{j}]"
                    if check_required_field(dd, "type", str, report, dctx):
                        check_enum(dd["type"], DO_DONT_TYPES, report, f"{dctx}.type")
                    check_required_field(dd, "text", str, report, dctx)

            # Related inconsistencies cross-reference
            if "related_inconsistencies" in comp and isinstance(comp["related_inconsistencies"], list) and inconsistency_ids:
                for inc_ref in comp["related_inconsistencies"]:
                    if inc_ref not in inconsistency_ids:
                        report.error(f"{ctx}: related_inconsistencies references '{inc_ref}' not found in audit-results.json")

        report.ok(f"components has {len(data['components'])} entries")

        # Check all pattern names are covered
        if pattern_names:
            uncovered = pattern_names - component_names
            if uncovered:
                for pat in sorted(uncovered):
                    report.warn(f"Pattern '{pat}' from audit-results.json has no matching component")
            else:
                report.ok(f"All {len(pattern_names)} patterns from audit have matching components")

        # Slug uniqueness summary
        report.ok(f"All {len(slugs)} slugs are unique")

    # Action items
    if "action_items" in data and isinstance(data["action_items"], list):
        action_ids = set()
        for i, ai in enumerate(data["action_items"]):
            ctx = f"action_items[{i}]"

            if check_required_field(ai, "id", str, report, ctx):
                if ai["id"] in action_ids:
                    report.error(f"{ctx}: duplicate action item ID '{ai['id']}'")
                action_ids.add(ai["id"])

            check_required_field(ai, "title", str, report, ctx)
            check_required_field(ai, "description", str, report, ctx)

            if check_required_field(ai, "priority", str, report, ctx):
                check_enum(ai["priority"], PRIORITY_LEVELS, report, f"{ctx}.priority")

            if check_required_field(ai, "effort", str, report, ctx):
                check_enum(ai["effort"], EFFORT_LEVELS, report, f"{ctx}.effort")

            if check_required_field(ai, "labels", list, report, ctx):
                for label in ai["labels"]:
                    check_enum(label, ACTION_LABELS, report, f"{ctx}.labels")

            # Cross-reference inconsistency
            if "related_inconsistency" in ai and ai["related_inconsistency"] and inconsistency_ids:
                if ai["related_inconsistency"] not in inconsistency_ids:
                    report.error(f"{ctx}: related_inconsistency '{ai['related_inconsistency']}' not found in audit-results.json")

        report.ok(f"action_items has {len(data['action_items'])} entries with unique IDs")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate-handoff.py <project-directory>")
        print("       The directory should contain audit-results.json, tokens.json, components.json")
        sys.exit(2)

    project_dir = Path(sys.argv[1]).resolve()
    if not project_dir.is_dir():
        print(f"Error: '{project_dir}' is not a directory")
        sys.exit(2)

    report = Report()

    # ── Load files ──

    audit_path = project_dir / "audit-results.json"
    tokens_path = project_dir / "tokens.json"
    components_path = project_dir / "components.json"

    audit_data = load_json(audit_path, report)
    tokens_data = load_json(tokens_path, report)
    components_data = load_json(components_path, report)

    if audit_data is None:
        report.set_file("audit-results.json")
        report.error("File not found or invalid JSON — this file is required")
        report.print_report()
        sys.exit(2)

    # ── Validate audit-results.json ──

    pattern_names, inconsistency_ids, page_urls, has_dark_mode = validate_audit(
        audit_data, project_dir, report
    )
    audit_url = audit_data.get("app_url")

    # ── Validate tokens.json ──

    token_names = set()
    if tokens_data is not None:
        token_names = validate_tokens(tokens_data, audit_url, has_dark_mode, report)
    else:
        report.set_file("tokens.json")
        report.warn("File not found — skipping token validation and token cross-reference checks")

    # ── Validate components.json ──

    if components_data is not None:
        validate_components(
            components_data, audit_url, pattern_names, inconsistency_ids, token_names, report
        )
    else:
        report.set_file("components.json")
        report.warn("File not found — skipping component validation")

    # ── Print report ──

    passed = report.print_report()
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
