/* File: monitoring/static/js/health.js */
(() => {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);

  function safeJsonStringify(obj) {
    try {
      return JSON.stringify(obj, null, 2);
    } catch {
      return "{}";
    }
  }

  function setPill(pillEl, ok, text) {
    if (!pillEl) return;
    pillEl.classList.remove("issues__pill--open", "issues__pill--resolved");
    pillEl.classList.add(ok ? "issues__pill--resolved" : "issues__pill--open");
    pillEl.textContent = text;
  }

  async function fetchJson(url, timeoutMs = 5000) {
    const ctl = new AbortController();
    const t = window.setTimeout(() => ctl.abort(), timeoutMs);

    try {
      const r = await fetch(url, {
        method: "GET",
        credentials: "same-origin",
        headers: { "Accept": "application/json" },
        signal: ctl.signal,
      });
      const data = await r.json().catch(() => ({}));
      return { ok: r.ok, status: r.status, data };
    } finally {
      window.clearTimeout(t);
    }
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch {
      return false;
    }
  }

  function renderChecks(tbody, payload) {
    if (!tbody) return;
    const checks = (payload && payload.checks) || {};
    const timings = (payload && payload.timings_ms) || {};
    const errors = (payload && payload.errors) || {};

    const rows = Object.keys(checks).length ? Object.keys(checks) : ["db"];

    tbody.innerHTML = "";
    rows.forEach((k) => {
      const ok = !!checks[k];
      const ms = timings[k];
      const err = errors[k];

      const tr = document.createElement("tr");
      tr.className = "issues__tr";

      const td1 = document.createElement("td");
      td1.className = "issues__td";
      td1.textContent = k;

      const td2 = document.createElement("td");
      td2.className = "issues__td";
      const pill = document.createElement("span");
      pill.className = `issues__pill ${ok ? "issues__pill--resolved" : "issues__pill--open"}`;
      pill.textContent = ok ? "OK" : "Fail";
      td2.appendChild(pill);

      const td3 = document.createElement("td");
      td3.className = "issues__td issues__td--mono";
      td3.textContent = Number.isFinite(ms) ? `${ms} ms` : "—";

      const td4 = document.createElement("td");
      td4.className = "issues__td issues__td--muted";
      td4.textContent = err ? String(err) : "—";

      tr.append(td1, td2, td3, td4);
      tbody.appendChild(tr);
    });
  }

  async function refresh() {
    const pill = $("[data-health-pill]");
    const serviceEl = $("[data-health-service]");
    const envEl = $("[data-health-env]");
    const versionEl = $("[data-health-version]");
    const timeEl = $("[data-health-time]");
    const tbody = $("[data-health-checks]");
    const jsonEl = $("[data-health-json]");
    const noteEl = $("[data-health-note]");

    setPill(pill, false, "Checking…");
    if (noteEl) noteEl.textContent = "";

    // Prefer root /healthz/ (what your load balancer would hit)
    const { ok, status, data } = await fetchJson("/healthz/");

    // Render
    if (serviceEl) serviceEl.textContent = data.service || "—";
    if (envEl) envEl.textContent = data.env || "—";
    if (versionEl) versionEl.textContent = data.version || "—";
    if (timeEl) timeEl.textContent = data.time || "—";
    if (jsonEl) jsonEl.textContent = safeJsonStringify(data);

    renderChecks(tbody, data);

    if (ok) {
      setPill(pill, true, "Healthy");
      if (noteEl) noteEl.textContent = "All checks passed.";
      noteEl?.classList.remove("is-error");
    } else {
      setPill(pill, false, `Not Ready (${status})`);
      if (noteEl) noteEl.textContent = "One or more checks failed. See errors/timings.";
      noteEl?.classList.add("is-error");
    }
  }

  function init() {
    const page = $("[data-health-page]");
    if (!page) return;

    const refreshBtn = $("[data-health-refresh]");
    const copyBtn = $("[data-health-copy]");
    const copyBtn2 = $("[data-health-copy-2]");
    const jsonEl = $("[data-health-json]");

    const doCopy = async () => {
      const text = jsonEl ? jsonEl.textContent : "{}";
      await copyText(text);
    };

    refreshBtn?.addEventListener("click", refresh);
    copyBtn?.addEventListener("click", doCopy);
    copyBtn2?.addEventListener("click", doCopy);

    refresh();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
