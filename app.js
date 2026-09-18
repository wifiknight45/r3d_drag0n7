(() => {
  const form = document.getElementById('chartForm');
  const out = document.getElementById('out');
  const API = localStorage.getItem('r3d_api') || 'http://127.0.0.1:7860';
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    out.hidden = false;
    out.textContent = 'casting…';
    try {
      const res = await fetch(`${API}/api/chart`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(body.detail || body.error || res.statusText);
      out.textContent = JSON.stringify(body, null, 2);
    } catch (err) {
      out.textContent = `offline / no API at ${API}\n${JSON.stringify(data, null, 2)}\n\n${err.message}`;
    }
  });
})();
