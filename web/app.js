let missions = [];
let currentMission = null;

async function loadMissions() {
  try {
    const resp = await fetch('missions.json');
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}`);
    }
    const data = await resp.json();
    missions = data.missions || [];
    populateMissionSelector();
    // Select the first mission by default
    if (missions.length > 0) {
      currentMission = missions[0];
      document.getElementById('missionSelect').value = currentMission.id;
      renderMission();
    }
  } catch (e) {
    console.warn('Cannot load missions.json', e);
    const missionBox = document.getElementById('missionBox');
    if (missionBox) {
      missionBox.innerHTML = '<em>Грешка при зареждане на мисии.</em>';
    }
  }
}

function populateMissionSelector() {
  const select = document.getElementById('missionSelect');
  if (!select) return;
  
  select.innerHTML = '';
  missions.forEach(m => {
    const option = document.createElement('option');
    option.value = m.id;
    option.textContent = m.title_bg;
    select.appendChild(option);
  });
  
  select.addEventListener('change', (e) => {
    currentMission = missions.find(m => m.id === e.target.value);
    renderMission();
    clearResults();
  });
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
    <ul class="mission-requirements">
      ${currentMission.min_coverage !== undefined ? `<li>Минимум покритие: ${currentMission.min_coverage}%</li>` : ''}
      ${currentMission.max_failed !== undefined ? `<li>Макс. провалени тестове: ${currentMission.max_failed}</li>` : ''}
      ${currentMission.min_passed !== undefined ? `<li>Минимум успешни тестове: ${currentMission.min_passed}</li>` : ''}
      ${currentMission.requires_property_keyword ? `<li>Изисква ключова дума: <code>${currentMission.requires_property_keyword}</code></li>` : ''}
      ${currentMission.reward_points !== undefined ? `<li>Награда: ${currentMission.reward_points} точки</li>` : ''}
    </ul>
    <div id="missionStatus"></div>
  `;
}

const codeEl = document.getElementById('code');
const testsEl = document.getElementById('tests');
const runBtn = document.getElementById('runBtn');
const statusEl = document.getElementById('status');
const passedEl = document.getElementById('passed');
const failedEl = document.getElementById('failed');
const outputEl = document.getElementById('output');
const coverageSpan = document.getElementById('coverage');
const scoreSpan = document.getElementById('score');

runBtn.addEventListener('click', async () => {
  statusEl.textContent = 'Running...';
  statusEl.className = 'status-running';
  runBtn.disabled = true;
  clearResults();

  try {
    // Use relative URL with /api prefix when served through nginx,
    // fallback to direct API URL for development
    const apiBaseUrl = window.location.port === '3000' ? '/api' : 'http://localhost:8000';
    const resp = await fetch(`${apiBaseUrl}/run`, {
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
    statusEl.className = 'status-done';
  } catch (err) {
    statusEl.textContent = 'Error';
    statusEl.className = 'status-error';
    outputEl.textContent = String(err);
    setMissionStatus('Грешка при изпълнение', false);
  } finally {
    runBtn.disabled = false;
  }
});

function clearResults() {
  passedEl.textContent = '0';
  failedEl.textContent = '0';
  if (coverageSpan) coverageSpan.textContent = '0%';
  if (scoreSpan) scoreSpan.textContent = '0';
  outputEl.textContent = '';
  setMissionStatus('', null);
}

function updateResults(data) {
  passedEl.textContent = data.passed;
  failedEl.textContent = data.failed;
  if (coverageSpan) coverageSpan.textContent = data.coverage_percent + '%';
  if (scoreSpan) scoreSpan.textContent = data.score;
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
    setMissionStatus('Мисията изпълнена! 🎉', true);
  } else {
    setMissionStatus('Мисията НЕ е изпълнена.', false);
  }
}

function setMissionStatus(text, success) {
  const el = document.getElementById('missionStatus');
  if (!el) return;
  el.textContent = text;
  el.className = '';
  if (success === null) {
    el.className = '';
  } else if (success) {
    el.className = 'mission-success';
  } else {
    el.className = 'mission-failed';
  }
}

loadMissions();
