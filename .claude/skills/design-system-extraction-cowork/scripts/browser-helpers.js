// browser-helpers.js — concat this file's contents into EVERY javascript_tool call.
// Originally created by design-system-apply-feedback from run1 feedback.
// Updated for run2 (SPA helper-lifecycle fix).
//
// Why inline-every-call: SPAs (Mantine/React/Vue/Next/etc.) and the Chrome MCP
// `navigate` tool both perform full document replaces that wipe `window.*`
// state. "Inject once, call many" fails on the second tool call with
// `ReferenceError: __waitForStable is not defined`.
//
// Correct usage pattern — every javascript_tool payload:
//   1. Cat the contents of this file as the prelude.
//   2. Append the specific observation/action code.
//   3. Send as a single javascript_tool call.
//
// The `window.*` assignments below still work because they execute in the same
// tool call as the consumer. They are NOT a durable installation.

// Wait for one of the given CSS selectors to appear and the DOM to go quiet.
window.__waitForStable = async (selectors, quietMs = 500, timeoutMs = 8000) => {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    const found = selectors.some(s => document.querySelector(s));
    if (found) {
      await new Promise(resolve => {
        let timer;
        const mo = new MutationObserver(() => {
          clearTimeout(timer);
          timer = setTimeout(() => { mo.disconnect(); resolve(); }, quietMs);
        });
        mo.observe(document.body, { childList: true, subtree: true });
        timer = setTimeout(() => { mo.disconnect(); resolve(); }, quietMs);
      });
      return true;
    }
    await new Promise(r => setTimeout(r, 100));
  }
  return false; // timed out — proceed anyway
};

// Wrap async code in an IIFE (top-level await not supported in classic scripts).
window.__runAsync = fn => (async () => fn())();

// Set Mantine color scheme directly (more reliable than clicking the theme toggle button).
window.__setTheme = (theme) => {
  document.documentElement.setAttribute('data-mantine-color-scheme', theme);
  try { localStorage.setItem('mantine-color-scheme-value', theme); } catch (_) {}
};

// Get current Mantine theme from the DOM.
window.__getTheme = () =>
  document.documentElement.getAttribute('data-mantine-color-scheme') || 'light';

// Cache reference background colors for light/dark ground-truth checks.
window.__themeRef = {
  light: null,
  dark: null,
  calibrate: () => {
    window.__setTheme('light');
    window.__themeRef.light = getComputedStyle(document.body).backgroundColor;
    window.__setTheme('dark');
    window.__themeRef.dark = getComputedStyle(document.body).backgroundColor;
  },
  currentTheme: () => {
    const bg = getComputedStyle(document.body).backgroundColor;
    if (bg === window.__themeRef.dark) return 'dark';
    if (bg === window.__themeRef.light) return 'light';
    return 'unknown';
  }
};

'browser-helpers loaded';
