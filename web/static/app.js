(() => {
  const form = document.getElementById("chart-form");
  const loading = document.getElementById("loading");
  const results = document.getElementById("results");
  const placements = document.getElementById("placements");
  const summary = document.getElementById("summary");
  const interpretation = document.getElementById("interpretation");
  const wheelWrap = document.getElementById("wheel-wrap");
  const meta = document.getElementById("meta");
  const aiBtn = document.getElementById("ai-btn");
  const aiOut = document.getElementById("ai-out");
  const aiQ = document.getElementById("ai-question");
  const hint = document.getElementById("form-hint");
  let lastChart = null;

  const apiBase = "";

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hint.textContent = "";
    const fd = new FormData(form);
    const payload = {
      name: fd.get("name") || null,
      date: fd.get("date"),
      time: fd.get("time") || "12:00",
      place: fd.get("place") || null,
      timezone: fd.get("timezone") || null,
      house_system: fd.get("house_system") || "Placidus",
      mode: fd.get("mode") || "Ptolemy",
    };
    const lat = fd.get("lat");
    const lon = fd.get("lon");
    if (lat !== "" && lat != null) payload.lat = Number(lat);
    if (lon !== "" && lon != null) payload.lon = Number(lon);
    if (!payload.place && (payload.lat == null || payload.lon == null)) {
      hint.textContent = "Need place or both latitude and longitude.";
      return;
    }

    loading.classList.remove("hidden");
    results.classList.add("hidden");
    aiBtn.disabled = true;
    aiOut.textContent = "";

    try {
      const res = await fetch(`${apiBase}/api/chart`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!data.ok) {
        hint.textContent = data.error || "Chart failed";
        loading.classList.add("hidden");
        return;
      }
      lastChart = data;
      renderChart(data);
      results.classList.remove("hidden");
      aiBtn.disabled = false;
      results.scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (err) {
      hint.textContent = String(err);
    } finally {
      loading.classList.add("hidden");
    }
  });

  function renderChart(data) {
    const loc = data.input?.location?.display || "";
    meta.textContent = `${data.input?.mode || ""} · ${data.backend || ""} · ${loc}`;
    placements.innerHTML = "";
    (data.planets || []).forEach((p) => {
      const li = document.createElement("li");
      li.innerHTML = `<span>${p.name}</span><span class="sign">${p.sign} ${Number(p.degree_in_sign).toFixed(1)}°</span>`;
      placements.appendChild(li);
    });
    if (data.houses?.ascendant != null) {
      const li = document.createElement("li");
      const asc = data.houses.ascendant;
      const signIdx = Math.floor((asc % 360) / 30);
      const signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"];
      li.innerHTML = `<span>Ascendant</span><span class="sign">${signs[signIdx]} ${(asc % 30).toFixed(1)}°</span>`;
      placements.appendChild(li);
    }
    summary.textContent = data.summary || "";
    interpretation.textContent = data.interpretation || "(No detailed interpreter output for this backend.)";
    wheelWrap.innerHTML = data.wheel_svg || "";
  }

  aiBtn.addEventListener("click", async () => {
    if (!lastChart) return;
    aiBtn.disabled = true;
    aiOut.textContent = "Summoning…";
    try {
      const res = await fetch(`${apiBase}/api/ai/reading`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chart: lastChart, question: aiQ.value || null }),
      });
      const data = await res.json();
      aiOut.textContent = data.reading || data.error || JSON.stringify(data, null, 2);
      if (data.provider) {
        aiOut.textContent += `\n\n— provider: ${data.provider}`;
      }
    } catch (err) {
      aiOut.textContent = String(err);
    } finally {
      aiBtn.disabled = false;
    }
  });
})();
