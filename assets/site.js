/* AI-901 Grand Prix · shared behaviour: theme, nav, progress, copy buttons,
   image zoom, completion tracking, quiz reveal scoring, tabs, pit board. */
(function () {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const KEY = 'ai901-gp';
  const store = { get(k, d) { try { return JSON.parse(localStorage.getItem(KEY + ':' + k)) ?? d; } catch { return d; } }, set(k, v) { try { localStorage.setItem(KEY + ':' + k, JSON.stringify(v)); } catch {} } };

  /* theme */
  const root = document.documentElement;
  const applyTheme = t => { if (t) root.setAttribute('data-theme', t); else root.removeAttribute('data-theme'); };
  applyTheme(store.get('theme', null) || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : null));
  $('#theme')?.addEventListener('click', () => { const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark'; applyTheme(next); store.set('theme', next); });

  /* mobile nav */
  const menu = $('.menu-btn'), nav = $('.nav');
  menu?.addEventListener('click', () => { const open = nav.classList.toggle('open'); menu.setAttribute('aria-expanded', open); });

  /* reading progress */
  const bar = $('#readbar');
  const onScroll = () => { if (!bar) return; const h = document.documentElement; const max = h.scrollHeight - h.clientHeight; bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%'; };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  /* pit board: student number -> every <span class="v" data-v="student"> and derived names */
  const pit = $('#student');
  const applyStudent = s => {
    s = (s || 's07').toLowerCase().replace(/[^a-z0-9]/g, '');
    if (!/^s\d{2}$/.test(s)) s = 's' + (s.replace(/\D/g, '') || '7').padStart(2, '0').slice(-2);
    $$('.v[data-v="student"]').forEach(e => e.textContent = s);
    $$('.v[data-v="rg"]').forEach(e => e.textContent = 'rg-ai901-' + s);
    $$('.v[data-v="name"]').forEach(e => e.textContent = 'ai901-' + s + '-' + (store.get('word', 'pitcrew')));
    $$('.v[data-v="proj"]').forEach(e => e.textContent = 'proj-ai901-' + s);
    if (pit && pit.value !== s) pit.value = s;
    store.set('student', s);
  };
  applyStudent(store.get('student', 's07'));
  pit?.addEventListener('change', () => applyStudent(pit.value));
  pit?.addEventListener('keyup', e => { if (e.key === 'Enter') applyStudent(pit.value); });

  /* copy buttons on code blocks */
  $$('pre').forEach(pre => {
    const b = document.createElement('button'); b.className = 'copy'; b.type = 'button'; b.textContent = 'Copy';
    b.addEventListener('click', async () => {
      const clone = pre.cloneNode(true); clone.querySelector('.copy')?.remove(); clone.querySelectorAll('.out').forEach(o => o.remove());
      try { await navigator.clipboard.writeText(clone.innerText.replace(/\n+$/, '')); b.textContent = 'Copied'; b.classList.add('ok'); setTimeout(() => { b.textContent = 'Copy'; b.classList.remove('ok'); }, 1400); } catch { b.textContent = 'Select & copy'; }
    });
    pre.appendChild(b);
  });

  /* screenshots: click to zoom */
  $$('img.shot').forEach(img => {
    img.addEventListener('click', () => {
      if (img.classList.contains('zoomed')) { img.classList.remove('zoomed'); $('.dim')?.remove(); return; }
      const dim = document.createElement('div'); dim.className = 'dim'; dim.addEventListener('click', () => { img.classList.remove('zoomed'); dim.remove(); });
      document.body.appendChild(dim); img.classList.add('zoomed');
    });
  });
  addEventListener('keydown', e => { if (e.key === 'Escape') { $$('img.shot.zoomed').forEach(i => i.classList.remove('zoomed')); $('.dim')?.remove(); } });

  /* tabs (Portal / Cloud Shell / Python) */
  $$('.tabs').forEach(t => {
    const tabs = $$('[role="tab"]', t), panels = $$('[role="tabpanel"]', t);
    const pick = i => { tabs.forEach((x, k) => x.setAttribute('aria-selected', k === i)); panels.forEach((p, k) => p.hidden = k !== i); };
    tabs.forEach((x, i) => x.addEventListener('click', () => { pick(i); store.set('tab', x.textContent.trim()); }));
    const pref = store.get('tab', null); const idx = tabs.findIndex(x => x.textContent.trim() === pref); pick(idx >= 0 ? idx : 0);
  });

  /* completion tracking */
  const page = document.body.dataset.page;
  const done = store.get('done', {});
  const paintDone = () => { $$('.nav a[data-lab]').forEach(a => a.classList.toggle('is-done', !!done[a.dataset.lab])); $$('.lapcard li[data-lab]').forEach(li => li.classList.toggle('done', !!done[li.dataset.lab])); };
  paintDone();
  if (page && /^lab/.test(page)) {
    const target = $$('h2').find(h => /what you learned|pit wall debrief/i.test(h.textContent));
    if (target && 'IntersectionObserver' in window) {
      new IntersectionObserver((es, io) => { if (es.some(e => e.isIntersecting)) { done[page] = Date.now(); store.set('done', done); paintDone(); io.disconnect(); } }, { threshold: .2 }).observe(target);
    }
  }

  /* quiz reveal scoring (details.reveal.quiz) */
  const quiz = $$('details.reveal.quiz');
  if (quiz.length) {
    const sc = document.createElement('p'); sc.className = 'quiz-score';
    quiz[0].parentNode.insertBefore(sc, quiz[0]);
    const paint = () => { const n = quiz.filter(q => q.open).length; sc.textContent = n ? `${n} of ${quiz.length} answers revealed` : `${quiz.length} questions · answer in your head first, then reveal`; };
    quiz.forEach(q => q.addEventListener('toggle', paint)); paint();
  }

  /* masthead speed-lines animation */
  const cv = $('canvas.mast-fx');
  if (cv && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const ctx = cv.getContext('2d'); let w, h, ps = [];
    const size = () => { w = cv.width = cv.offsetWidth * devicePixelRatio; h = cv.height = cv.offsetHeight * devicePixelRatio; };
    const spawn = () => ({ x: -40, y: h * (0.1 + Math.random() * 0.85), v: (1.5 + Math.random() * 3) * devicePixelRatio, len: (40 + Math.random() * 160) * devicePixelRatio, c: ['#E10600', '#FACC15', '#38BDF8', '#ffffff'][Math.floor(Math.random() * 4)], a: 0.08 + Math.random() * 0.3 });
    size(); addEventListener('resize', size);
    for (let i = 0; i < 34; i++) { const p = spawn(); p.x = Math.random() * w; ps.push(p); }
    const frame = () => {
      ctx.clearRect(0, 0, w, h);
      ps.forEach(p => { p.x += p.v; if (p.x > w + p.len) Object.assign(p, spawn()); ctx.globalAlpha = p.a; ctx.strokeStyle = p.c; ctx.lineWidth = 1.2 * devicePixelRatio; ctx.beginPath(); ctx.moveTo(p.x - p.len, p.y); ctx.lineTo(p.x, p.y); ctx.stroke(); });
      requestAnimationFrame(frame);
    };
    frame();
  }
})();
