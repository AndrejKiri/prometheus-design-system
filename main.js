/* ═══════════════════════════════════════════════════════════════════════════
   Prometheus Design System — Documentation Site JS
   ═══════════════════════════════════════════════════════════════════════════ */

(function () {
  "use strict";

  // ─── Theme Toggle ──────────────────────────────────────────────────────
  var _currentTheme = null;

  function getPreferredTheme() {
    if (_currentTheme) return _currentTheme;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function setTheme(theme) {
    _currentTheme = theme;
    document.documentElement.setAttribute("data-theme", theme);
    var btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = theme === "dark" ? "☀️" : "🌙";
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "light";
    setTheme(current === "dark" ? "light" : "dark");
  }

  // ─── Active Nav Highlight ──────────────────────────────────────────────
  function highlightActiveNav() {
    const path = window.location.pathname;
    const page = path.split("/").pop() || "index.html";
    document.querySelectorAll(".doc-nav-link").forEach(function (link) {
      const href = link.getAttribute("href");
      if (!href) return;
      const linkPage = href.split("/").pop() || "index.html";
      if (page === linkPage || (page === "" && linkPage === "index.html")) {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });
  }

  // ─── Mobile Sidebar ───────────────────────────────────────────────────
  function setupMobileSidebar() {
    const burger = document.getElementById("sidebar-burger");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("sidebar-overlay");

    if (!burger || !sidebar) return;

    burger.addEventListener("click", function () {
      sidebar.classList.toggle("open");
      if (overlay) overlay.classList.toggle("open");
    });

    if (overlay) {
      overlay.addEventListener("click", function () {
        sidebar.classList.remove("open");
        overlay.classList.remove("open");
      });
    }

    // Close on nav click (mobile)
    sidebar.querySelectorAll(".doc-nav-link").forEach(function (link) {
      link.addEventListener("click", function () {
        if (window.innerWidth <= 768) {
          sidebar.classList.remove("open");
          if (overlay) overlay.classList.remove("open");
        }
      });
    });
  }

  // ─── Copy to Clipboard ────────────────────────────────────────────────
  function setupCopyButtons() {
    document.querySelectorAll("pre").forEach(function (pre) {
      if (pre.querySelector(".code-copy-btn")) return;
      var btn = document.createElement("button");
      btn.className = "code-copy-btn";
      btn.textContent = "Copy";
      btn.addEventListener("click", function () {
        var code = pre.querySelector("code");
        var text = code ? code.textContent : pre.textContent;
        try {
          navigator.clipboard.writeText(text).then(function () {
            btn.textContent = "Copied!";
            setTimeout(function () { btn.textContent = "Copy"; }, 1500);
          }).catch(function() { btn.textContent = "Copy"; });
        } catch(e) {}
      });
      pre.style.position = "relative";
      pre.appendChild(btn);
    });
  }

  // ─── Collapsible Sidebar ───────────────────────────────────────────────
  function setupCollapsibleSidebar() {
    var sidebar = document.getElementById("sidebar");
    if (!sidebar) return;

    // Create toggle button (fixed position, appended to body)
    var btn = document.createElement("button");
    btn.className = "sidebar-collapse-btn";
    btn.setAttribute("aria-label", "Toggle sidebar");
    btn.innerHTML = "‹";
    document.body.appendChild(btn);

    // Restore state
    var collapsed = localStorage.getItem("sidebar-collapsed") === "true";
    if (collapsed) document.body.classList.add("sidebar-collapsed");

    btn.addEventListener("click", function () {
      document.body.classList.toggle("sidebar-collapsed");
      var isCollapsed = document.body.classList.contains("sidebar-collapsed");
      localStorage.setItem("sidebar-collapsed", isCollapsed);
    });
  }

  // ─── Collapsible TOC ─────────────────────────────────────────────────
  function setupCollapsibleToc() {
    var toc = document.querySelector(".doc-toc-sidebar");
    if (!toc) return;

    // Create toggle button (fixed position on body)
    var btn = document.createElement("button");
    btn.className = "toc-collapse-btn";
    btn.setAttribute("aria-label", "Toggle table of contents");
    var arrow = document.createElement("span");
    arrow.className = "toc-arrow";
    arrow.textContent = "›";
    btn.appendChild(arrow);
    document.body.appendChild(btn);

    // Restore state
    var collapsed = localStorage.getItem("toc-collapsed") === "true";
    if (collapsed) {
      document.body.classList.add("toc-collapsed");
    }

    btn.addEventListener("click", function () {
      document.body.classList.toggle("toc-collapsed");
      var isCollapsed = document.body.classList.contains("toc-collapsed");
      localStorage.setItem("toc-collapsed", isCollapsed);
    });
  }

  // ─── GitHub Issue Links for Action Items ───────────────────────────────
  var GITHUB_REPO = "prometheus/prometheus";
  var GITHUB_ICON_SVG = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>';

  function buildIssueUrl(title, body) {
    return "https://github.com/" + GITHUB_REPO + "/issues/new?title=" +
      encodeURIComponent(title) + "&body=" + encodeURIComponent(body);
  }

  function makeGithubLink(href, text) {
    var a = document.createElement("a");
    a.className = "pr-github-link";
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.innerHTML = GITHUB_ICON_SVG + " " + text;
    return a;
  }

  function getCardItemUrl(card) {
    return window.location.origin + window.location.pathname + "#" + card.id;
  }

  function setupGithubIssueLinks() {
    var cards = document.querySelectorAll(".pr-card");
    if (!cards.length) return;

    cards.forEach(function (card) {
      var number = card.querySelector(".pr-card-number");
      var titleEl = card.querySelector(".pr-card-title");
      var body = card.querySelector(".pr-card-body");
      if (!titleEl || !body) return;

      var title = titleEl.textContent.trim();
      var numText = number ? number.textContent.trim() : "";
      var itemUrl = getCardItemUrl(card);

      // Extract problem description (first <p> in card body)
      var problemP = body.querySelector(":scope > p");
      var problemText = problemP ? problemP.textContent.trim() : "";

      // Detect if this is a bug-like item
      var isBug = !!card.querySelector(".pr-label-fix");

      // --- "Open Issue" link after problem paragraph ---
      var issueBody;
      if (isBug) {
        issueBody = "## What did you do?\n" +
          problemText + "\n\n" +
          "## What did you expect to see?\n" +
          "Consistent, correct behavior as described in the design system.\n\n" +
          "## What did you see instead? Under which circumstances?\n" +
          "See details in the design system audit.\n\n" +
          "---\n_From [Prometheus Design System \u2014 Action Item " + numText + "](" + itemUrl + ")_";
      } else {
        issueBody = "## Proposal\n" +
          problemText + "\n\n" +
          "---\n_From [Prometheus Design System \u2014 Action Item " + numText + "](" + itemUrl + ")_";
      }

      var issueLink = makeGithubLink(buildIssueUrl(title, issueBody), "Open Issue");
      issueLink.classList.add("pr-issue-link");
      if (problemP) {
        problemP.insertAdjacentElement("afterend", issueLink);
      }

    });
  }

  // ─── Init ─────────────────────────────────────────────────────────────
  document.addEventListener("DOMContentLoaded", function () {
    setTheme(getPreferredTheme());
    highlightActiveNav();
    setupMobileSidebar();
    setupCopyButtons();
    setupCollapsibleSidebar();
    setupCollapsibleToc();
    setupGithubIssueLinks();

    var toggle = document.getElementById("theme-toggle");
    if (toggle) toggle.addEventListener("click", toggleTheme);
  });
})();
