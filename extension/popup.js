const inventory = () => [...document.querySelectorAll(
    'a,button,input,select,textarea,label,h1,h2,[role],[data-testid]')]
  .filter(e => e.offsetParent !== null).slice(0, 150)
  .map(e => ({ tag: e.tagName.toLowerCase(), id: e.id || null,
    testid: e.dataset.testid || null, role: e.getAttribute('role'),
    type: e.getAttribute('type'), name: e.getAttribute('name'),
    aria: e.getAttribute('aria-label'), placeholder: e.getAttribute('placeholder'),
    text: (e.innerText || e.value || '').trim().slice(0, 60) }));

document.getElementById('go').onclick = async () => {
  const out = document.getElementById('out');
  out.textContent = 'Analyse de la page…';
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const [{ result: elements }] = await chrome.scripting.executeScript(
    { target: { tabId: tab.id }, func: inventory });
  out.textContent = 'L\'agent écrit et exécute le test (1 à 3 min)…';
  const isEdge = navigator.userAgent.includes('Edg/');
  const res = await fetch('http://localhost:8000/run', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: tab.url, title: tab.title, elements,
      request: document.getElementById('req').value,
      channel: isEdge ? 'msedge' : 'chrome' })
  });
  const r = await res.json();
  out.innerHTML = `${r.passed ? '✅ Test réussi' : r.probable_bug ? '🐞 Anomalie probable' : '⚠️ Test à revoir'}
    (${r.attempts} tentative(s)) — <a href="${r.report_url}" target="_blank">ouvrir le rapport</a>`;
};