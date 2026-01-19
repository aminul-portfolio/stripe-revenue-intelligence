const MD_PATH = "../30k_master_checklist.md";
const STORAGE_KEY = "masterChecklistProgress_v1";

function nowStamp() {
  const d = new Date();
  // ISO date + time (local)
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

// Simple deterministic hash for stable IDs (no external libs)
function hashString(str) {
  let h = 2166136261;
  for (let i = 0; i < str.length; i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0).toString(16);
}

function loadState() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
  } catch {
    return {};
  }
}

function saveState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state, null, 2));
}

function download(filename, text) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type: "application/json" }));
  a.download = filename;
  a.click();
  URL.revokeObjectURL(a.href);
}

function parseChecklist(md) {
  const lines = md.split("\n");
  const sections = [];
  let current = { title: "General", tasks: [], raw: [] };

  const pushCurrent = () => {
    if (current.tasks.length || current.raw.length) sections.push(current);
  };

  for (const line of lines) {
    const heading = line.match(/^#{1,3}\s+(.*)/);
    if (heading) {
      pushCurrent();
      current = { title: heading[1].trim(), tasks: [], raw: [] };
      continue;
    }

    const task = line.match(/^\s*[-*]\s+\[( |x|X)\]\s+(.*)$/);
    if (task) {
      const label = task[2].trim();
      const id = hashString(current.title + "::" + label);
      current.tasks.push({ id, label });
      continue;
    }

    // keep non-task lines as supporting context (optional display)
    if (line.trim()) current.raw.push(line);
  }

  pushCurrent();
  return sections;
}

function render(sections, state) {
  const content = document.getElementById("content");
  content.innerHTML = "";

  sections.forEach((sec) => {
    const secEl = document.createElement("div");
    secEl.className = "section";

    const doneCount = sec.tasks.filter(t => state[t.id]?.checked).length;
    const badgeText = sec.tasks.length ? `${doneCount}/${sec.tasks.length} done` : "notes";

    const head = document.createElement("div");
    head.className = "section-head";
    head.innerHTML = `
      <div class="left">
        <div class="line">${sec.title}</div>
        <span class="badge">${badgeText}</span>
      </div>
      <div class="muted">click to open</div>
    `;
    head.addEventListener("click", () => secEl.classList.toggle("open"));

    const body = document.createElement("div");
    body.className = "section-body";

    // Optional: show non-task context as rendered markdown
    if (sec.raw.length) {
      const notes = document.createElement("div");
      notes.className = "muted";
      notes.style.marginBottom = "10px";
      notes.innerHTML = marked.parse(sec.raw.join("\n"));
      body.appendChild(notes);
    }

    sec.tasks.forEach((t) => {
      const row = document.createElement("div");
      row.className = "task";

      const st = state[t.id] || { checked: false, ts: "" };

      row.innerHTML = `
        <div class="meta">
          <div class="line">${t.label}</div>
        </div>
        <div class="right">
          <span class="timestamp">${st.ts || "—"}</span>
          <input class="checkbox" type="checkbox" ${st.checked ? "checked" : ""} />
        </div>
      `;

      const cb = row.querySelector(".checkbox");
      cb.addEventListener("change", () => {
        const next = loadState();
        next[t.id] = {
          checked: cb.checked,
          ts: cb.checked ? nowStamp() : ""
        };
        saveState(next);
        // Update timestamp UI
        row.querySelector(".timestamp").textContent = next[t.id].ts || "—";
        // Update section badge
        // simplest: re-render whole UI for accurate counts
        render(sections, next);
      });

      body.appendChild(row);
    });

    secEl.appendChild(head);
    secEl.appendChild(body);
    content.appendChild(secEl);
  });
}

async function init() {
  const res = await fetch(MD_PATH, { cache: "no-store" });
  if (!res.ok) {
    document.getElementById("content").innerHTML =
      `<div class="muted">Could not load ${MD_PATH}. Make sure the file exists and paths are correct.</div>`;
    return;
  }

  const md = await res.text();
  const sections = parseChecklist(md);
  const state = loadState();

  render(sections, state);

  // Search
  const search = document.getElementById("search");
  search.addEventListener("input", () => {
    const q = search.value.trim().toLowerCase();
    const filtered = sections.map(s => ({
      ...s,
      tasks: s.tasks.filter(t => t.label.toLowerCase().includes(q) || s.title.toLowerCase().includes(q))
    })).filter(s => s.tasks.length || !q);

    render(filtered, loadState());
    // Expand all when searching
    if (q) document.querySelectorAll(".section").forEach(el => el.classList.add("open"));
  });

  // Expand / collapse
  document.getElementById("btnExpandAll").addEventListener("click", () => {
    document.querySelectorAll(".section").forEach(el => el.classList.add("open"));
  });
  document.getElementById("btnCollapseAll").addEventListener("click", () => {
    document.querySelectorAll(".section").forEach(el => el.classList.remove("open"));
  });

  // Export / import
  document.getElementById("btnExport").addEventListener("click", () => {
    const payload = {
      exported_at: nowStamp(),
      storage_key: STORAGE_KEY,
      state: loadState()
    };
    download(`checklist_progress_${new Date().toISOString().slice(0,10)}.json`, JSON.stringify(payload, null, 2));
  });

  const fileImport = document.getElementById("fileImport");
  document.getElementById("btnImport").addEventListener("click", () => fileImport.click());
  fileImport.addEventListener("change", async () => {
    const f = fileImport.files?.[0];
    if (!f) return;
    const text = await f.text();
    const payload = JSON.parse(text);
    if (!payload.state) return;
    saveState(payload.state);
    render(sections, loadState());
  });

  document.getElementById("btnClear").addEventListener("click", () => {
    localStorage.removeItem(STORAGE_KEY);
    render(sections, {});
  });
}

init();
