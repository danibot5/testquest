const codeEl = document.getElementById('code');
const testsEl = document.getElementById('tests');
const runBtn = document.getElementById('runBtn');
const statusEl = document.getElementById('status');
const passedEl = document.getElementById('passed');
const failedEl = document.getElementById('failed');
const outputEl = document.getElementById('output');

runBtn.addEventListener('click', async () => {
  statusEl.textContent = 'Running...';
  runBtn.disabled = true;
  passedEl.textContent = '0';
  failedEl.textContent = '0';
  outputEl.textContent = '';

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
    passedEl.textContent = data.passed;
    failedEl.textContent = data.failed;
    outputEl.textContent = data.output;
    statusEl.textContent = 'Done';
  } catch (err) {
    statusEl.textContent = 'Error';
    outputEl.textContent = String(err);
  } finally {
    runBtn.disabled = false;
  }
});