/* AI-901 Grand Prix · practice exam engine (vanilla JS, no dependencies) */
(function () {
  const Q = window.AI901_QUESTIONS || [];
  const $ = (s, r = document) => r.querySelector(s);
  const KEY = 'ai901-gp:quiz';
  const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch { return {}; } };
  const save = s => { try { localStorage.setItem(KEY, JSON.stringify(s)); } catch {} };
  let state = load();                      // { [id]: { picked: [idx...], correct: bool } }
  const root = $('#quiz'); if (!root || !Q.length) return;
  const board = { n: $('#sb-n'), pct: $('#sb-pct'), bar: $('#sb-bar-i'), live: $('#sb-live') };
  const DOMAINS = [...new Set(Q.map(q => q.domain))];

  // deterministic per-session option shuffle (seeded by question id), remembering original indexes
  const shuffle = (arr, seed) => { const a = arr.map((v, i) => ({ v, i })); let s = seed; for (let k = a.length - 1; k > 0; k--) { s = (s * 9301 + 49297) % 233280; const j = Math.floor((s / 233280) * (k + 1)); [a[k], a[j]] = [a[j], a[k]]; } return a; };
  const seedOf = id => [...id].reduce((h, c) => (h * 31 + c.charCodeAt(0)) % 100000, 7);

  function render() {
    root.innerHTML = '';
    Q.forEach((q, n) => {
      const card = document.createElement('section'); card.className = 'q'; card.id = 'q-' + q.id;
      const opts = shuffle(q.options, seedOf(q.id));
      const type = q.multi ? 'checkbox' : 'radio';
      card.innerHTML = `<div class="qn"><span>Question ${n + 1} of ${Q.length}${q.multi ? ' · choose all that apply' : ''}</span><span class="dom">${q.domain}</span></div>
        <h3>${q.q}</h3>
        <div class="opts">${opts.map(o => `<label><input type="${type}" name="${q.id}" value="${o.i}"><span>${o.v}</span></label>`).join('')}</div>
        ${q.multi ? '<p style="margin:10px 0 0"><button type="button" class="btn" style="padding:8px 14px;font-size:14px" data-check>Check answer</button></p>' : ''}
        <div class="why"><b>Explanation.</b> ${q.why} <a href="${q.lap}.html" style="margin-left:6px">Revisit ${q.lap.replace('lab', 'Lap ')} →</a></div>`;
      root.appendChild(card);
      if (q.multi) card.querySelector('[data-check]')?.addEventListener('click', () => { const picked = [...card.querySelectorAll('input:checked')].map(i => +i.value); if (picked.length) answer(card, q, picked); });
      else card.querySelectorAll('input').forEach(i => i.addEventListener('change', () => answer(card, q, [+i.value])));
      const st = state[q.id];
      if (st) paint(card, q, st.picked);       // after wiring: paint() removes the Check button
    });
    score();
  }
  function answer(card, q, picked) {
    if (state[q.id]) return;
    const correct = picked.length === q.answer.length && picked.every(p => q.answer.includes(p));
    state[q.id] = { picked, correct }; save(state); paint(card, q, picked); score();
    const next = card.nextElementSibling; if (next && next.classList.contains('q')) setTimeout(() => next.scrollIntoView({ behavior: 'smooth', block: 'start' }), 350);
  }
  function paint(card, q, picked) {
    card.classList.add('answered');
    card.querySelectorAll('label').forEach(l => { const v = +l.querySelector('input').value; l.querySelector('input').disabled = true; l.querySelector('input').checked = picked.includes(v); if (q.answer.includes(v)) l.classList.add('correct'); else if (picked.includes(v)) l.classList.add('wrong'); });
    const b = card.querySelector('[data-check]'); if (b) b.remove();
  }
  function score() {
    const done = Object.keys(state).length, right = Object.values(state).filter(s => s.correct).length;
    const pct = done ? Math.round((right / done) * 100) : 0;
    board.n.textContent = `${done} / ${Q.length}`; board.pct.textContent = done ? `${right} right · ${pct}%` : 'no answers yet';
    board.bar.style.width = (done / Q.length * 100) + '%';
    if (board.live) board.live.textContent = `${done} of ${Q.length} answered, ${right} correct`;
    const res = $('#result'); if (!res) return;
    if (done < Q.length) { res.classList.remove('show'); return; }
    const scaled = Math.round(right / Q.length * 1000);
    const verdict = pct >= 85 ? '🏆 Pole position. You would pass comfortably; book the exam.' : pct >= 70 ? '🥉 Podium. That is a pass (700+). Revisit the weak domains below and you are safe.' : pct >= 55 ? '🏎️ Midfield. Close. Reread the laps for the domains under 70% and retake tomorrow.' : '🔧 Back to the pit lane. Not yet. Work through the laps again, slowly, with the quizzes.';
    const rows = DOMAINS.map(d => { const qs = Q.filter(q => q.domain === d); const r = qs.filter(q => state[q.id]?.correct).length; const p = Math.round(r / qs.length * 100); const lap = qs[0].lap; return `<tr><td>${d}</td><td>${r} / ${qs.length}</td><td><b style="color:${p >= 70 ? 'var(--green-ink)' : 'var(--red-ink)'}">${p}%</b></td><td><a href="${lap}.html">${lap.replace('lab', 'Lap ')}</a></td></tr>`; }).join('');
    res.innerHTML = `<h3 style="margin-top:0">Result · ${right} of ${Q.length} · scaled ≈ ${scaled} / 1000</h3><p style="font-size:18px">${verdict}</p><table><thead><tr><th>Domain</th><th>Right</th><th>Score</th><th>Revisit</th></tr></thead><tbody>${rows}</tbody></table><p class="small muted">The scaled number is a rough guide only: the real exam weights domains and uses several question types. 700 is the pass mark.</p>`;
    res.classList.add('show');
    licence(right, scaled);
  }
  /* the pit-crew licence: a printable card for the student who finished the day */
  function licence(right, scaled) {
    const box = $('#licence'); if (!box) return;
    const g = k => { try { return JSON.parse(localStorage.getItem('ai901-gp:' + k)); } catch { return null; } };
    const student = g('student') || 's07', done = g('done') || {};
    const LAPS = [['lab0', '#94A3B8'], ['lab1', '#EF4444'], ['lab2', '#22C55E'], ['lab3', '#F59E0B'], ['lab4', '#38BDF8'], ['lab5', '#A78BFA'], ['lab6', '#14B8A6'], ['lab7', '#FACC15']];
    const n = LAPS.filter(([l]) => done[l]).length;
    const date = new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' });
    const grade = scaled >= 850 ? 'Pole position' : scaled >= 700 ? 'Podium' : scaled >= 550 ? 'Midfield' : 'Pit lane';
    box.innerHTML = `<div class="licence-card"><div class="lc-top"><div><div class="lc-eyebrow">Velocity Motors · AI pit crew licence</div><h3>Driver ${student.toUpperCase()}</h3><div style="color:#94A3B8;font-size:14px">AI-901 Grand Prix · ${date}</div></div><div class="lc-num">${student}</div></div>
      <div class="lc-grid"><div><small>Practice exam</small><b>${right} / ${Q.length}</b></div><div><small>Scaled score</small><b>≈ ${scaled}</b></div><div><small>Verdict</small><b>${grade}</b></div><div><small>Laps completed</small><b>${n} of 8</b><div class="lc-laps">${LAPS.map(([l, c]) => `<i style="--d:${c}" class="${done[l] ? 'on' : ''}"></i>`).join('')}</div></div></div>
      <div class="lc-foot"><span>Built a Foundry resource, a prompt, an agent, speech, vision, image generation and Content Understanding in one day. Not a Microsoft credential: book AI-901 for that.</span><button type="button" onclick="window.print()">Print</button></div></div>`;
    box.classList.add('show');
  }
  $('#sb-reset')?.addEventListener('click', () => { if (confirm('Clear all answers and start again?')) { state = {}; save(state); $('#licence')?.classList.remove('show'); render(); window.scrollTo({ top: root.offsetTop - 120, behavior: 'smooth' }); } });
  $('#sb-reveal')?.addEventListener('click', () => { root.querySelectorAll('.q').forEach(c => c.classList.add('answered')); });
  render();
})();
