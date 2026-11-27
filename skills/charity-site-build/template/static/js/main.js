/* charity-sites progressive enhancement. No dependencies, no tracking.
   The site works without JavaScript; this file adds the mobile menu, dropdowns,
   copy buttons, inline validation and the hand-off to the payment provider.
   Card details are NEVER collected here: donations continue on the provider's page. */
(function () {
  'use strict';

  // ---- Mobile drawer
  var toggle = document.querySelector('.menu-toggle');
  var drawer = document.getElementById('drawer');
  function setDrawer(open) {
    drawer.classList.toggle('is-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', toggle.getAttribute(open ? 'data-label-close' : 'data-label-open'));
    toggle.querySelector('.icon-open').hidden = open;
    toggle.querySelector('.icon-close').hidden = !open;
  }
  if (toggle && drawer) {
    toggle.addEventListener('click', function () { setDrawer(!drawer.classList.contains('is-open')); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && drawer.classList.contains('is-open')) { setDrawer(false); toggle.focus(); }
    });
  }

  // ---- Desktop dropdowns: click/keyboard operated, never hover-only
  document.querySelectorAll('.nav button[aria-haspopup]').forEach(function (btn) {
    var li = btn.parentElement;
    function close() { li.classList.remove('is-open'); btn.setAttribute('aria-expanded', 'false'); }
    btn.addEventListener('click', function () {
      var open = !li.classList.contains('is-open');
      document.querySelectorAll('.nav li.is-open').forEach(function (o) { o.classList.remove('is-open'); o.querySelector('button').setAttribute('aria-expanded', 'false'); });
      li.classList.toggle('is-open', open);
      btn.setAttribute('aria-expanded', String(open));
    });
    li.addEventListener('keydown', function (e) { if (e.key === 'Escape') { close(); btn.focus(); } });
    li.addEventListener('focusout', function (e) { if (!li.contains(e.relatedTarget)) close(); });
  });

  // ---- Copy buttons (bank details)
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var value = btn.getAttribute('data-copy');
      var label = btn.querySelector('.label');
      var original = label.textContent;
      function done() {
        btn.classList.add('is-copied');
        label.textContent = btn.getAttribute('data-done');
        var status = btn.closest('.bank-block').querySelector('[role="status"]');
        if (status) status.textContent = btn.getAttribute('data-status');
        setTimeout(function () { btn.classList.remove('is-copied'); label.textContent = original; }, 3000);
      }
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(value).then(done);
      } else {
        var ta = document.createElement('textarea');
        ta.value = value; ta.setAttribute('readonly', ''); ta.style.position = 'absolute'; ta.style.opacity = '0';
        document.body.appendChild(ta); ta.select();
        try { document.execCommand('copy'); done(); } finally { ta.remove(); }
      }
    });
  });

  // ---- Sticky donate bar: hide while a text field has focus so it never covers it
  var sticky = document.querySelector('.sticky-donate');
  if (sticky) {
    document.addEventListener('focusin', function (e) { if (e.target.matches('input, textarea, select')) sticky.classList.add('is-hidden'); });
    document.addEventListener('focusout', function (e) { if (e.target.matches('input, textarea, select')) sticky.classList.remove('is-hidden'); });
  }

  // ---- Validation shared by forms
  var EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
  function validateFields(form) {
    var firstBad = null;
    form.querySelectorAll('.field').forEach(function (f) {
      var input = f.querySelector('input, select, textarea');
      var err = f.querySelector('.error');
      if (!input || !err || input.name === 'custom-amount') return;
      var v = input.value.trim();
      var empty = input.required && !v;
      var invalid = !empty && input.type === 'email' && v && !EMAIL.test(v);
      var bad = empty || invalid;
      f.classList.toggle('is-error', bad);
      err.hidden = !bad;
      if (bad) err.querySelector('.msg').textContent = err.getAttribute(invalid ? 'data-msg-invalid' : 'data-msg-empty');
      input.setAttribute('aria-invalid', bad ? 'true' : 'false');
      if (bad && !firstBad) firstBad = input;
    });
    var summary = form.querySelector('.error-summary');
    if (summary) summary.hidden = !firstBad;
    if (firstBad) { (summary || firstBad).focus(); }
    return !firstBad;
  }
  function showDemoNotice(form) {
    var note = form.querySelector('.form-preview-note');
    if (note) { note.hidden = false; }
  }

  // ---- Contact form
  var contact = document.getElementById('contact-form');
  if (contact) {
    contact.addEventListener('submit', function (e) {
      if (!validateFields(contact)) { e.preventDefault(); return; }
      if (contact.dataset.demo === 'true') { e.preventDefault(); showDemoNotice(contact); return; }
      // A form service (Formspree, Web3Forms, Netlify Forms, a Cloudflare Worker…) receives the POST.
    });
  }

  // ---- Newsletter
  document.querySelectorAll('[data-newsletter]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      var input = form.querySelector('input[type="email"]');
      var status = form.querySelector('.newsletter-status');
      if (!EMAIL.test(input.value.trim())) { e.preventDefault(); input.setAttribute('aria-invalid', 'true'); input.focus(); return; }
      input.removeAttribute('aria-invalid');
      if (form.dataset.demo === 'true') { e.preventDefault(); status.textContent = document.querySelector('.form-preview-note') ? document.querySelector('.form-preview-note').textContent : ''; }
    });
  });

  // ---- Donation: choose amount here, pay on the provider's hosted page
  var don = document.getElementById('donation-form');
  if (don) {
    var custom = don.querySelector('#custom-amount');
    var totals = document.querySelectorAll('[data-total]');
    var freqLabel = document.querySelector('[data-frequency-label]');
    var err = don.querySelector('#amount-error');
    var sym = don.dataset.currencySymbol || '';
    var pos = don.dataset.currencyPosition || 'after';
    var sep = don.dataset.thousands || ',';
    function fmt(n) {
      var s = String(n).replace(/\B(?=(\d{3})+(?!\d))/g, sep);
      return pos === 'before' ? sym + s : s + ' ' + sym;
    }
    function amount() {
      var c = custom && custom.value.replace(/[^\d]/g, '');
      if (c) return parseInt(c, 10);
      var r = don.querySelector('input[name="preset"]:checked');
      return r ? parseInt(r.value, 10) : 0;
    }
    function frequency() {
      var f = don.querySelector('input[name="frequency"]:checked');
      return f ? f.value : 'once';
    }
    function refresh() {
      var n = amount();
      totals.forEach(function (t) { t.textContent = n ? fmt(n) : '–'; });
      if (freqLabel) freqLabel.textContent = freqLabel.getAttribute(frequency() === 'monthly' ? 'data-monthly' : 'data-once');
    }
    don.addEventListener('input', refresh);
    don.querySelectorAll('input[name="preset"]').forEach(function (r) {
      r.addEventListener('change', function () { if (custom) custom.value = ''; refresh(); });
    });
    if (custom) custom.addEventListener('input', function () {
      if (custom.value) don.querySelectorAll('input[name="preset"]').forEach(function (r) { r.checked = false; });
    });
    refresh();

    don.addEventListener('submit', function (e) {
      e.preventDefault();
      var n = amount();
      var min = parseInt(don.dataset.min || '1', 10);
      if (!n || n < min) {
        err.hidden = false;
        err.querySelector('.msg').textContent = err.getAttribute(n ? 'data-msg-min' : 'data-msg-choose');
        (custom || err).focus();
        return;
      }
      err.hidden = true;
      var url = frequency() === 'monthly' && don.dataset.monthlyUrl ? don.dataset.monthlyUrl : don.dataset.url;
      var map = don.dataset.links ? JSON.parse(don.dataset.links) : null;
      if (map) url = map[String(n)];
      if (!url || don.dataset.demo === 'true') { showDemoNotice(don); return; }
      var param = map ? '' : don.dataset.amountParam;
      if (param) {
        var value = don.dataset.amountUnit === 'minor' ? n * 100 : n;
        url += (url.indexOf('?') === -1 ? '?' : '&') + encodeURIComponent(param) + '=' + encodeURIComponent(value);
      }
      var submit = don.querySelector('button[type="submit"]');
      submit.classList.add('is-loading');
      submit.setAttribute('aria-busy', 'true');
      window.location.assign(url);
    });
  }
})();
