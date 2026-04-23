#!/usr/bin/env node
// Created by design-system-apply-feedback from run1 feedback
// Captures interactive states (modals, expanded accordions, hovers) via Playwright.
// Reads interaction-recipes.json from the project folder for state → action sequences.
//
// Usage: node capture-interactive.mjs <project-folder>
// One-time setup: npm install playwright && npx playwright install chromium

import { chromium } from "playwright";
import { readFileSync, existsSync, mkdirSync } from "fs";
import { resolve, join } from "path";

const projectDir = resolve(process.argv[2] || ".");
const auditPath = join(projectDir, "audit-results.json");
const recipesPath = join(projectDir, "interaction-recipes.json");

if (!existsSync(auditPath)) {
  console.error(`audit-results.json not found in ${projectDir}`);
  process.exit(1);
}
if (!existsSync(recipesPath)) {
  console.log(`interaction-recipes.json not found — copying template to ${recipesPath}`);
  const templatePath = new URL("interaction-recipes.json", import.meta.url).pathname;
  if (existsSync(templatePath)) {
    const { copyFileSync } = await import("fs");
    copyFileSync(templatePath, recipesPath);
    console.log("Edit interaction-recipes.json to define state → action sequences, then re-run.");
  } else {
    console.error("Template not found. Create interaction-recipes.json manually.");
  }
  process.exit(0);
}

const audit = JSON.parse(readFileSync(auditPath, "utf8"));
const recipes = JSON.parse(readFileSync(recipesPath, "utf8"));
const screenshotsDir = join(projectDir, "screenshots");
mkdirSync(screenshotsDir, { recursive: true });

async function runRecipe(page, actions) {
  for (const action of actions) {
    if (action.click) await page.click(action.click);
    if (action.hover) await page.hover(action.hover);
    if (action.wait) await page.waitForTimeout(action.wait);
    if (action.waitForSelector) await page.waitForSelector(action.waitForSelector, { timeout: 5000 });
  }
}

async function captureInteractive() {
  const browser = await chromium.launch();
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 } });

  for (const audPage of audit.pages_audited) {
    if (!audPage.additional_screenshots) continue;

    for (const ss of audPage.additional_screenshots) {
      const recipe = recipes[ss.state];
      if (!recipe) {
        console.log(`  no recipe for state "${ss.state}" — skipping ${ss.path}`);
        continue;
      }

      const browserPage = await context.newPage();
      await browserPage.goto(audPage.url, { waitUntil: "networkidle", timeout: 30000 });
      await browserPage.waitForTimeout(500);

      if (recipe.theme) {
        await browserPage.evaluate((t) => {
          document.documentElement.setAttribute("data-mantine-color-scheme", t);
          try { localStorage.setItem("mantine-color-scheme-value", t); } catch (_) {}
        }, recipe.theme);
        await browserPage.waitForTimeout(300);
      }

      await runRecipe(browserPage, recipe.actions || []);

      const outPath = ss.path.startsWith("screenshots/")
        ? join(projectDir, ss.path)
        : join(screenshotsDir, ss.path);
      await browserPage.screenshot({ path: outPath, type: "jpeg", quality: 80 });
      console.log(`  captured: ${ss.path} (state: ${ss.state})`);
      await browserPage.close();
    }
  }

  await browser.close();
  console.log("\nInteractive capture complete.");
}

captureInteractive().catch((e) => { console.error(e); process.exit(1); });
