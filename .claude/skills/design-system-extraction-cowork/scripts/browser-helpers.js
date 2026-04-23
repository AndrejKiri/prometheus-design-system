// browser-helpers.js — inject this file's contents via javascript_tool at the start of a page survey.
// Created by design-system-apply-feedback from run1 feedback.
//
// Usage: paste the contents of this file as the javascript_tool text, then call the helpers
// in subsequent javascript_tool calls.

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
