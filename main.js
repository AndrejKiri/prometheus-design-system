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

    // Create toggle button
    var btn = document.createElement("button");
    btn.className = "sidebar-collapse-btn";
    btn.setAttribute("aria-label", "Toggle sidebar");
    btn.innerHTML = "‹";
    sidebar.appendChild(btn);

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

    // Create toggle button
    var btn = document.createElement("button");
    btn.className = "toc-collapse-btn";
    btn.setAttribute("aria-label", "Toggle table of contents");
    btn.innerHTML = "›";
    toc.appendChild(btn);

    // Create dot indicators
    var tocInline = toc.querySelector(".toc-inline");
    if (tocInline) {
      var dots = document.createElement("div");
      dots.className = "toc-dots";
      var links = tocInline.querySelectorAll("a");
      links.forEach(function (link) {
        var dot = document.createElement("a");
        dot.className = "toc-dot";
        dot.href = link.href;
        dot.title = link.textContent;
        dots.appendChild(dot);
      });
      toc.appendChild(dots);
    }

    // Restore state
    var collapsed = localStorage.getItem("toc-collapsed") === "true";
    if (collapsed) toc.classList.add("toc-collapsed");

    btn.addEventListener("click", function () {
      toc.classList.toggle("toc-collapsed");
      var isCollapsed = toc.classList.contains("toc-collapsed");
      localStorage.setItem("toc-collapsed", isCollapsed);
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

    var toggle = document.getElementById("theme-toggle");
    if (toggle) toggle.addEventListener("click", toggleTheme);
  });
})();
