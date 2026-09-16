const STORAGE_KEY = "transliteration";

const els = {
  date: document.getElementById("date"),
  cipher: document.getElementById("cipher"),
  form: document.getElementById("guess-form"),
  guess: document.getElementById("guess"),
  primary: document.getElementById("primary"),
  progress: document.getElementById("progress"),
  status: document.getElementById("status"),
  score: document.getElementById("score"),
  revealed: document.getElementById("revealed"),
  rubric: document.getElementById("rubric"),
  rubricList: document.getElementById("rubric-list"),
  lang: document.getElementById("lang"),
  tagline: document.getElementById("tagline"),
};

let mode = "daily";
let daily = null;
let practice = null;
let state = loadState();

function defaultState() {
  return {
    lang: els.lang.value || "ru",
    dailyDate: "",
    slot: 0,
    solved: [false, false, false],
    completed: false,
    history: {},
    practiceIndex: 0,
  };
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY) || "{}";
    const next = { ...defaultState(), ...JSON.parse(raw) };
    if (!next.history || typeof next.history !== "object" || Array.isArray(next.history)) {
      next.history = {};
    }
    return next;
  } catch {
    return defaultState();
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function ordinal(n) {
  const v = n % 100;
  if (v >= 11 && v <= 13) return `${n}TH`;
  const ones = n % 10;
  const suf = ones === 1 ? "ST" : ones === 2 ? "ND" : ones === 3 ? "RD" : "TH";
  return `${n}${suf}`;
}

function formatUtcDate(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  const weekday = dt.toLocaleDateString("en-US", { weekday: "long", timeZone: "UTC" }).toUpperCase();
  const month = dt.toLocaleDateString("en-US", { month: "long", timeZone: "UTC" }).toUpperCase();
  return `${weekday}, ${month} ${ordinal(d)} ${y}`;
}

function shiftDate(iso, days) {
  const [y, m, d] = iso.split("-").map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d + days));
  return dt.toISOString().slice(0, 10);
}

function localIsoDate() {
  return toIso(new Date());
}

function qs() {
  return `lang=${encodeURIComponent(state.lang)}`;
}

async function getJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error("bad response");
  return res.json();
}

function rollDay(today) {
  if (state.dailyDate === today) return;
  state.dailyDate = today;
  state.slot = 0;
  state.solved = [false, false, false];
  state.completed = false;
}

function recordDay(date) {
  state.history[date] = state.solved.filter(Boolean).length;
}

function localDay(y, m, d) {
  return new Date(y, m - 1, d);
}

function parseIso(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return localDay(y, m, d);
}

function pad2(n) {
  return String(n).padStart(2, "0");
}

function toIso(dt) {
  return `${dt.getFullYear()}-${pad2(dt.getMonth() + 1)}-${pad2(dt.getDate())}`;
}

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;");
}

function ytdWeeks() {
  const today = parseIso(localIsoDate());
  const start = localDay(today.getFullYear(), 1, 1);
  const weeks = [];
  let col = [];
  for (let i = 0; i < start.getDay(); i += 1) col.push(null);
  for (let dt = new Date(start); dt <= today; dt.setDate(dt.getDate() + 1)) {
    col.push(new Date(dt));
    if (col.length === 7) {
      weeks.push(col);
      col = [];
    }
  }
  if (col.length) {
    while (col.length < 7) col.push(null);
    weeks.push(col);
  }
  return weeks;
}

function weekdayLabel(row) {
  if (row % 2 === 0) return "";
  return localDay(2026, 1, 4 + row).toLocaleDateString(undefined, { weekday: "short" });
}

function renderRubric(rows) {
  els.rubricList.innerHTML = rows.map((r) => `<li>${r.glyph} = ${r.lat}</li>`).join("");
}

function setRubricOpen(open) {
  els.rubric.classList.toggle("open", open);
  document.body.classList.toggle("rubric-open", open);
}

function currentWord() {
  if (mode === "practice") return practice && practice.word;
  if (!daily || !daily.words) return null;
  const i = state.completed ? daily.words.length - 1 : state.slot;
  return daily.words[i];
}

function renderScore() {
  const weeks = ytdWeeks();
  const months = weeks
    .map((week) => week.find((dt) => dt && dt.getDate() === 1))
    .map((dt) => (dt ? dt.toLocaleDateString(undefined, { month: "short" }) : ""));
  const wdays = [0, 1, 2, 3, 4, 5, 6]
    .map((row) => `<span>${esc(weekdayLabel(row))}</span>`)
    .join("");
  const cells = weeks
    .flat()
    .map((dt) => {
      if (!dt) return `<span class="graph-cell pad"></span>`;
      const iso = toIso(dt);
      const played = Object.hasOwn(state.history, iso);
      const n = played ? state.history[iso] : 0;
      const kind = !played ? "none" : n === 3 ? "ok" : "bad";
      const tip = `${dt.toLocaleDateString()} · ${n}/3`;
      return `<span class="graph-cell ${kind}" data-tip="${esc(tip)}"></span>`;
    })
    .join("");
  els.score.innerHTML = `<div class="graph-scroll"><div class="graph" style="--weeks:${weeks.length}" role="img" aria-label="Year to date scores">
    <div class="graph-months"><span></span>${months.map((m) => `<span>${esc(m)}</span>`).join("")}</div>
    <div class="graph-body">
      <div class="graph-wdays" aria-hidden="true">${wdays}</div>
      <div class="graph-weeks">${cells}</div>
    </div>
  </div></div>`;
}

function renderRevealed() {
  if (!daily || !daily.words) {
    els.revealed.hidden = true;
    els.revealed.innerHTML = "";
    return;
  }
  const n = state.completed ? daily.words.length : state.slot;
  const rows = daily.words.slice(0, n);
  els.revealed.hidden = rows.length === 0;
  els.revealed.innerHTML = rows
    .map((word, i) => {
      const line = `${word.cipher} &rarr; ${word.answer.toUpperCase()}`;
      return `<li>${state.solved[i] ? line : `${line} (wrong)`}</li>`;
    })
    .join("");
}

function isPracticePrompt() {
  const inPractice = mode === "practice";
  const waitingForPractice = Boolean(daily && state.completed && !inPractice);
  const noDaily = Boolean(daily && !daily.words);
  return waitingForPractice || (noDaily && !inPractice);
}

function render() {
  els.lang.value = state.lang;
  els.cipher.lang = state.lang || els.lang.value;

  const src = mode === "practice" ? practice : daily;
  if (src && src.tagline) els.tagline.textContent = src.tagline;

  if (daily) {
    els.date.textContent = formatUtcDate(daily.date);
  }

  const word = currentWord();
  els.cipher.textContent = word ? word.cipher : "";

  const inPractice = mode === "practice";
  const promptPractice = isPracticePrompt();
  const noDaily = Boolean(daily && !daily.words);

  els.primary.textContent = promptPractice ? "Practice" : "Submit";
  els.guess.disabled = promptPractice || !word;

  if (inPractice && practice) {
    els.progress.textContent = `Practice ${practice.index + 1} / ${practice.total}`;
    els.score.hidden = false;
  } else if (noDaily) {
    els.progress.textContent = "No daily puzzle for this date.";
    els.score.hidden = true;
  } else if (daily && daily.words) {
    const n = state.completed ? daily.words.length : state.slot + 1;
    els.progress.textContent = `${n} / ${daily.words.length}`;
    els.score.hidden = !state.completed;
  } else {
    els.progress.textContent = "";
    els.score.hidden = true;
  }
  renderScore();
  renderRevealed();
  setRubricOpen(state.completed || inPractice || noDaily);
}

async function loadDaily() {
  daily = await getJson(`/api/daily?${qs()}&date=${localIsoDate()}`);
  rollDay(daily.date);
  if (state.completed && !Object.hasOwn(state.history, daily.date)) {
    recordDay(daily.date);
  }
  if (daily.rubric) renderRubric(daily.rubric);
  saveState();
}

async function loadPractice() {
  practice = await getJson(`/api/practice?i=${state.practiceIndex}&${qs()}`);
  if (practice.rubric) renderRubric(practice.rubric);
  saveState();
}

async function setPracticeWord(index) {
  state.practiceIndex = index;
  els.status.textContent = "";
  els.guess.value = "";
  saveState();
  await loadPractice();
  render();
  els.guess.focus();
}

async function enterPractice() {
  mode = "practice";
  await setPracticeWord(state.practiceIndex);
}

async function nextPractice() {
  if (!practice) return;
  await setPracticeWord((practice.index + 1) % practice.total);
}

function advanceDaily(correct) {
  els.guess.value = "";
  els.status.textContent = correct ? "Correct." : "";
  if (correct) state.solved[state.slot] = true;
  if (state.slot < daily.words.length - 1) {
    state.slot += 1;
  } else {
    state.completed = true;
    recordDay(daily.date);
  }
  saveState();
  render();
}

async function checkGuess() {
  const word = currentWord();
  if (!word) return;
  const guess = els.guess.value.trim().toLowerCase();
  if (!guess) {
    if (mode === "practice") await nextPractice();
    return;
  }
  const ok = guess === word.answer.toLowerCase();
  if (mode === "daily") {
    advanceDaily(ok);
    return;
  }
  if (ok) {
    await nextPractice();
    return;
  }
  els.status.textContent = "Not quite.";
  els.guess.select();
}

els.form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (isPracticePrompt()) {
    await enterPractice();
    return;
  }
  await checkGuess();
});

els.lang.addEventListener("change", async () => {
  state.lang = els.lang.value;
  saveState();
  await refresh();
});

async function refresh() {
  try {
    if (mode === "practice") await loadPractice();
    else await loadDaily();
    render();
  } catch {
    els.status.textContent = "Could not load puzzle.";
  }
}

function rollIfNewDay() {
  if (localIsoDate() === state.dailyDate) return;
  mode = "daily";
  refresh();
}

function armMidnight() {
  const now = new Date();
  const next = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
  setTimeout(() => {
    rollIfNewDay();
    armMidnight();
  }, Math.max(50, next - now));
}

document.addEventListener("visibilitychange", () => {
  if (document.visibilityState === "visible") rollIfNewDay();
});

refresh();
armMidnight();
