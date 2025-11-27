from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import subprocess
import os
import shutil

app = FastAPI(title="TaskQuest API")

# Allow the frontend to call the backend in browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RunRequest(BaseModel):
    code: str
    tests: str

class TestResult(BaseModel):
    passed: int
    failed: int
    output: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run", response_model=TestResult)
def run_tests(req: RunRequest):
    temp_dir = tempfile.mkdtemp(prefix="taskquest_")
    try:
        code_path = os.path.join(temp_dir, "main.py")
        tests_path = os.path.join(temp_dir, "test_main.py")

        with open(code_path, "w", encoding="utf-8") as f:
            f.write(req.code)
        with open(tests_path, "w", encoding="utf-8") as f:
            f.write(req.tests)

        cmd = ["pytest", "-q", "--disable-warnings", "--maxfail=1"]
        proc = subprocess.run(
            cmd, cwd=temp_dir, capture_output=True, text=True, timeout=10
        )
        output = (proc.stdout or "") + "\n" + (proc.stderr or "")

        passed = 0
        failed = 0
        for line in output.splitlines():
            if "passed" in line or "failed" in line:
                parts = line.replace(",", "").split()
                for i, p in enumerate(parts):
                    if p == "passed":
                        try: passed = int(parts[i-1])
                        except: pass
                    if p == "failed":
                        try: failed = int(parts[i-1])
                        except: pass

        return TestResult(passed=passed, failed=failed, output=output)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Test run timeout")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error running tests: {e}")
    finally:
        try: shutil.rmtree(temp_dir)
        except: pass