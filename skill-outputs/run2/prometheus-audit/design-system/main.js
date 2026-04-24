(function () {
  // Theme toggle
  var root = document.documentElement;
  var stored = localStorage.getItem('doc-theme');
  var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  root.setAttribute('data-theme', stored || (prefersDark ? 'dark' : 'light'));
  var toggle = document.getElementById('doc-theme-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      localStorage.setItem('doc-theme', next);
    });
  }

  // Burger
  var burger = document.getElementById('doc-burger');
  var sidebar = document.getElementById('doc-sidebar');
  var overlay = document.getElementById('doc-sidebar-overlay');
  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('visible');
  }
  if (burger) {
    burger.addEventListener('click', function () {
      if (sidebar) sidebar.classList.toggle('open');
      if (overlay) overlay.classList.toggle('visible');
    });
  }
  if (overlay) overlay.addEventListener('click', closeSidebar);

  // Copy buttons on every <pre>
  Array.prototype.forEach.call(document.querySelectorAll('pre'), function (pre) {
    if (pre.querySelector('.copy-btn')) return;
    var btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.type = 'button';
    btn.textContent = 'Copy';
    btn.addEventListener('click', function () {
      var code = pre.querySelector('code');
      var text = code ? code.textContent : pre.textContent;
      navigator.clipboard.writeText(text).then(function () {
        btn.textContent = 'Copied';
        btn.classList.add('copied');
        setTimeout(function () {
          btn.textContent = 'Copy';
          btn.classList.remove('copied');
        }, 1500);
      });
    });
    pre.appendChild(btn);
  });

  // Icon search filter
  var iconSearch = document.getElementById('icon-search');
  if (iconSearch) {
    iconSearch.addEventListener('input', function () {
      var q = iconSearch.value.toLowerCase();
      Array.prototype.forEach.call(document.querySelectorAll('.icon-card'), function (c) {
        c.style.display = c.textContent.toLowerCase().indexOf(q) === -1 ? 'none' : '';
      });
    });
  }
})();
