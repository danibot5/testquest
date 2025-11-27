import React, { useState } from 'react';

export default function App() {
  const [code, setCode] = useState<string>(`def add(a, b):
    return a + b
`);
  const [tests, setTests] = useState<string>(`from main import add

def test_add_simple():
    assert add(2, 3) == 5
`);
  const [result, setResult] = useState<{passed:number; failed:number; output:string} | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const resp = await fetch('http://localhost:8000/run', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ code, tests })
      });
      if (!resp.ok) {
        const d = await resp.json().catch(()=>({detail:'Unknown error'}));
        throw new Error(d.detail || `HTTP ${resp.status}`);
      }
      const data = await resp.json();
      setResult(data);
    } catch (e:any) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{padding: 16, display: 'grid', gap: 16}}>
      <h1>TaskQuest Академия</h1>
      <p>Минимален демо интерфейс: въведи код и тестове, натисни Run.</p>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:16}}>
        <div>
          <h3>Код (main.py)</h3>
          <textarea
            value={code}
            onChange={(e)=>setCode(e.target.value)}
            style={{width:'100%', height:300, fontFamily:'monospace'}}
          />
        </div>
        <div>
          <h3>Тестове (test_main.py)</h3>
          <textarea
            value={tests}
            onChange={(e)=>setTests(e.target.value)}
            style={{width:'100%', height:300, fontFamily:'monospace'}}
          />
        </div>
      </div>

      <button onClick={run} disabled={loading} style={{padding:'8px 16px'}}>
        {loading ? 'Running...' : 'Run'}
      </button>

      {error && <div style={{color:'red'}}>Error: {error}</div>}
      {result && (
        <div>
          <h3>Резултат</h3>
          <p>Passed: {result.passed} | Failed: {result.failed}</p>
          <pre style={{background:'#f5f5f5', padding:12, overflow:'auto'}}>{result.output}</pre>
        </div>
      )}
    </div>
  );
}