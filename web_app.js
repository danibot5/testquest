let missions = [];
let currentMission = null;

async function loadMissions() {
  try {
    const resp = await fetch('/missions.json');
    const data = await resp.json();
    missions = data.missions || [];
    // Избираме първата мисия за MVP
    currentMission = missions.find(m => m.id === 'basic_quality') || missions[0];
    renderMission();
  } catch (e) {
    console.warn('Cannot load missions.json', e);
  }
}

function renderMission() {
  const missionBox = document.getElementById('missionBox');
  if (!missionBox) return;
  if (!currentMission) {
    missionBox.innerHTML = '<em>Няма заредена мисия.</em>';
    return;
  }
  missionBox.innerHTML = `
    <h3>${currentMission.title_bg}</h3>
    <p>${currentMission.description_bg}</p>
    <ul style="margin:4px 0 8px;padding-left:16px;">
      ${currentMission.min_coverage !== undefined ? `<li>Минимум покритие: ${currentMission.min_coverage}%</li>` : ''}
      ${currentMission.max_failed !== undefined ? `<li>Макс. провалени тестове: ${currentMission.max_failed}</li>` : ''}
      ${currentMission.min_passed !== undefined ? `<li>Минимум успешни тестове: ${currentMission.min_passed}</li>` : ''}
      ${currentMission.reward_points !== undefined ? `<li>Награда точки: ${currentMission.reward_points}</li>` : ''}
    </ul>
    <div id="missionStatus" style="font-weight:bold;"></div>
  `;
}

const codeEl = document.getElementById('code');
const testsEl = document.getElementById('tests');
const runBtn = document.getElementById('runBtn');
const statusEl = document.getElementById('status');
const passedEl = document.getElementById('passed');
const failedEl = document.getElementById('failed');
const outputEl = document.getElementById('output');

let coverageSpan = document.getElementById('coverage');
let scoreSpan = document.getElementById('score');

runBtn.addEventListener('click', async () => {
  statusEl.textContent = 'Running...';
  runBtn.disabled = true;
  clearResults();

  try {
    const resp = await fetch('http://localhost:8000/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: codeEl.value, tests: testsEl.value })
    });
    const data = await resp.json();
    if (!resp.ok) {
      throw new Error(data.detail || 'HTTP error ' + resp.status);
    }
    updateResults(data);
    evaluateMission(data);
    statusEl.textContent = 'Done';
  } catch (err) {
    statusEl.textContent = 'Error';
    outputEl.textContent = String(err);
    setMissionStatus('Грешка при изпълнение', false);
  } finally {
    runBtn.disabled = false;
  }
});

function clearResults() {
  passedEl.textContent = '0';
  failedEl.textContent = '0';
  coverageSpan.textContent = '0%';
  scoreSpan.textContent = '0';
  outputEl.textContent = '';
  setMissionStatus('', null);
}

function updateResults(data) {
  passedEl.textContent = data.passed;
  failedEl.textContent = data.failed;
  coverageSpan.textContent = data.coverage_percent + '%';
  scoreSpan.textContent = data.score;
  outputEl.textContent = data.output;
}

function evaluateMission(runData) {
  if (!currentMission) return;
  let ok = true;

  if (currentMission.min_coverage !== undefined &&
    runData.coverage_percent < currentMission.min_coverage) ok = false;

  if (currentMission.max_failed !== undefined &&
    runData.failed > currentMission.max_failed) ok = false;

  if (currentMission.min_passed !== undefined &&
    runData.passed < currentMission.min_passed) ok = false;

  if (currentMission.requires_property_keyword) {
    const testsText = testsEl.value;
    
    if (!testsText.includes(currentMission.requires_property_keyword)) {
      ok = false;
    }
  }

  if (ok) {
    setMissionStatus('Мисията изпълнена!', true);
  } else {
    setMissionStatus('Мисията НЕ е изпълнена.', false);
  }
}

function setMissionStatus(text, success) {
  const el = document.getElementById('missionStatus');
  if (!el) return;
  el.textContent = text;
  if (success === null) {
    el.style.color = '';
  } else if (success) {
    el.style.color = '#0a832f';
  } else {
    el.style.color = '#c62828';
  }
}

loadMissions();