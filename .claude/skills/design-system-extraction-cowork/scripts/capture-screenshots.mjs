#!/usr/bin/env node
// Created by design-system-apply-feedback from run1 feedback
// Backfills real screenshots after Cowork handoff (Phase 1.5).
// Reads pages_audited from audit-results.json and captures each page
// in light and dark themes via Playwright Chromium.
//
// Usage: node capture-screenshots.mjs <project-folder>
// One-time setup: npm install playwright && npx playwright install chromium

import { chromium } from "playwright";
import { readFileSync, mkdirSync, existsSync } from "fs";
import { resolve, dirname, join } from "path";

const projectDir = resolve(process.argv[2] || ".");
const auditPath = join(projectDir, "audit-results.json");

if (!existsSync(auditPath)) {
  console.error(`audit-results.json not found in ${projectDir}`);
  process.exit(1);
}

const audit = JSON.parse(readFileSync(auditPath, "utf8"));
const hasDarkMode = audit.raw_observations?.has_dark_mode ?? false;
const screenshotsDir = join(projectDir, "screenshots");
mkdirSync(screenshotsDir, { exist_ok: true, recursive: true });

async function setTheme(page, theme) {
  await page.evaluate((t) => {
    document.documentElement.setAttribute("data-mantine-color-scheme", t);
    try { localStorage.setItem("mantine-color-scheme-value", t); } catch (_) {}
  }, theme);
  await page.waitForTimeout(300);
}

async function captureAll() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });

  for (const page of audit.pages_audited) {
    const browserPage = await context.newPage();
    await browserPage.goto(page.url, { waitUntil: "networkidle", timeout: 30000 });
    await browserPage.waitForTimeout(500);

    const themes = hasDarkMode ? ["light", "dark"] : ["light"];
    for (const theme of themes) {
      if (hasDarkMode) await setTheme(browserPage, theme);

      // Primary screenshot
      const ssPath = page.screenshot.replace(/^screenshots\//, "");
      const outPath = join(screenshotsDir, ssPath.replace("-light", "").replace("-dark", "")
        .replace(/\.jpg$/, `-${theme}.jpg`).replace(/\.png$/, `-${theme}.png`));
      const finalPath = page.screenshot.startsWith("screenshots/")
        ? join(projectDir, page.screenshot)
        : join(screenshotsDir, page.screenshot);
      await browserPage.screenshot({ path: finalPath, type: "jpeg", quality: 80, fullPage: true });
      console.log(`  captured: ${page.screenshot} (${theme})`);

      // Additional screenshots
      if (page.additional_screenshots) {
        for (const ss of page.additional_screenshots) {
          // These require interactive state — skip here, handled by capture-interactive.mjs
          console.log(`  skipped interactive: ${ss.path} (state: ${ss.state}) — run capture-interactive.mjs`);
        }
      }
    }

    await browserPage.close();
  }

  await browser.close();
  console.log("\nDone. Run capture-interactive.mjs for modal/hover states.");
}

captureAll().catch((e) => { console.error(e); process.exit(1); });
