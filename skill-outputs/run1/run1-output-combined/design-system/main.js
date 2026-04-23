(function () {
  'use strict';

  /* ── Theme ─────────────────────────────────────────────────────────── */
  var THEME_KEY = 'prom-ds-theme';
  var root = document.documentElement;
  var themeBtn = document.getElementById('themeToggle');

  function getTheme() {
    var stored = localStorage.getItem(THEME_KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(t) {
    root.setAttribute('data-theme', t);
    if (themeBtn) themeBtn.textContent = t === 'dark' ? '☀' : '🌙';
    localStorage.setItem(THEME_KEY, t);
  }

  applyTheme(getTheme());

  if (themeBtn) {
    themeBtn.addEventListener('click', function () {
      applyTheme(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    });
  }

  /* ── Active nav link ───────────────────────────────────────────────── */
  var currentPath = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.doc-nav-link').forEach(function (a) {
    var href = a.getAttribute('href') || '';
    var target = href.split('/').pop();
    if (target === currentPath) a.classList.add('active');
  });

  /* ── Burger / sidebar ──────────────────────────────────────────────── */
  var burger = document.getElementById('burger');
  var sidebar = document.getElementById('sidebar');
  var overlay = document.getElementById('sidebarOverlay');

  function openSidebar() {
    if (sidebar) sidebar.classList.add('open');
    if (overlay) overlay.classList.add('visible');
    document.body.style.overflow = 'hidden';
  }
  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('visible');
    document.body.style.overflow = '';
  }

  if (burger) burger.addEventListener('click', openSidebar);
  if (overlay) overlay.addEventListener('click', closeSidebar);

  /* ── Sidebar collapse persistence ─────────────────────────────────── */
  var SIDEBAR_KEY = 'prom-ds-sidebar';
  var sidebarCollapsed = localStorage.getItem(SIDEBAR_KEY) === 'collapsed';
  if (sidebarCollapsed && sidebar) sidebar.classList.add('collapsed');

  /* ── Copy buttons on pre blocks ────────────────────────────────────── */
  document.querySelectorAll('pre').forEach(function (pre) {
    var btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.textContent = 'Copy';
    pre.appendChild(btn);

    btn.addEventListener('click', function () {
      var code = pre.querySelector('code');
      var text = code ? code.innerText : pre.innerText.replace(/Copy$/, '').trim();
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = 'Copied!';
        btn.classList.add('copied');
        setTimeout(function () {
          btn.textContent = 'Copy';
          btn.classList.remove('copied');
        }, 2000);
      }).catch(function () {
        btn.textContent = 'Error';
        setTimeout(function () { btn.textContent = 'Copy'; }, 2000);
      });
    });
  });

  /* ── GitHub issue links on action-item cards ───────────────────────── */
  var REPO_URL = 'https://github.com/prometheus/prometheus';
  document.querySelectorAll('[data-issue-title]').forEach(function (card) {
    var title = card.getAttribute('data-issue-title');
    if (title && REPO_URL) {
      var link = document.createElement('a');
      link.href = REPO_URL + '/issues/new?title=' + encodeURIComponent(title) + '&labels=design-system';
      link.textContent = '↗ Open GitHub Issue';
      link.target = '_blank';
      link.style.cssText = 'font-size:12px;margin-top:8px;display:inline-block;';
      card.appendChild(link);
    }
  });

})();
