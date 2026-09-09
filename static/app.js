const STORAGE_KEY = "transliterillic";

const els = {
  date: document.getElementById("date"),
  cipher: document.getElementById("cipher"),
  form: document.getElementById("guess-form"),
  guess: document.getElementById("guess"),
  primary: document.getElementById("primary"),
  progress: document.getElementById("progress"),
  status: document.getElementById("status"),
  score: document.getElementById("score"),
  rubric: document.getElementById("rubric"),
  rubricList: document.getElementById("rubric-list"),
  lang: document.getElementById("lang"),
};

let mode = "daily";
let daily = null;
let practice = null;
let state = loadState();

function defaultState() {
  return {
    lang: "ru",
    dailyDate: "",
    slot: 0,
    solved: [false, false, false],
    completed: false,
    lastWinDate: "",
    currentStreak: 0,
    maxStreak: 0,
    daysWon: 0,
    practiceIndex: 0,
  };
}

function loadState() {
  try {
    return { ...defaultState(), ...JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}") };
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
  const yesterday = shiftDate(today, -1);
  if (state.lastWinDate !== today && state.lastWinDate !== yesterday) {
    state.currentStreak = 0;
  }
  state.dailyDate = today;
  state.slot = 0;
  state.solved = [false, false, false];
  state.completed = false;
}

function markWin(today) {
  if (state.lastWinDate === today) return;
  const yesterday = shiftDate(today, -1);
  state.currentStreak = state.lastWinDate === yesterday ? state.currentStreak + 1 : 1;
  state.maxStreak = Math.max(state.maxStreak, state.currentStreak);
  state.daysWon += 1;
  state.lastWinDate = today;
}

function renderRubric(rows) {
  els.rubricList.innerHTML = rows.map((r) => `<li>${r.cyr} = ${r.lat}</li>`).join("");
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
  els.score.innerHTML = `<dfn title="Consecutive days played">Streak</dfn>: ${state.currentStreak} &bull; <dfn title="Total perfect scores">Won</dfn>: ${state.daysWon}`;
}

function isPracticePrompt() {
  const inPractice = mode === "practice";
  const waitingForPractice = Boolean(daily && state.completed && !inPractice);
  const noDaily = Boolean(daily && !daily.words);
  return waitingForPractice || (noDaily && !inPractice);
}

function render() {
  els.lang.value = state.lang;
  els.cipher.lang = state.lang || "ru";

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
  setRubricOpen(state.completed || inPractice || noDaily);
}

async function loadDaily() {
  daily = await getJson(`/api/daily?${qs()}`);
  rollDay(daily.date);
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

async function checkGuess() {
  const word = currentWord();
  if (!word) return;
  const guess = els.guess.value.trim().toLowerCase();
  if (!guess) {
    if (mode === "practice") await nextPractice();
    return;
  }
  if (guess === word.answer.toLowerCase()) {
    els.guess.value = "";
    if (mode === "daily") {
      els.status.textContent = "Correct.";
      state.solved[state.slot] = true;
      if (state.slot < daily.words.length - 1) {
        state.slot += 1;
      } else {
        state.completed = true;
        markWin(daily.date);
      }
      saveState();
      render();
    } else {
      await nextPractice();
    }
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

refresh();
