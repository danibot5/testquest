from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import tempfile
import subprocess
import os
import shutil
from typing import List

app = FastAPI(title="TaskQuest API")

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
    # Create isolated temp directory
    temp_dir = tempfile.mkdtemp(prefix="taskquest_")
    try:
        # Write code and tests to files
        code_path = os.path.join(temp_dir, "main.py")
        tests_path = os.path.join(temp_dir, "test_main.py")

        with open(code_path, "w", encoding="utf-8") as f:
            f.write(req.code)
        with open(tests_path, "w", encoding="utf-8") as f:
            f.write(req.tests)

        # Run pytest with a timeout and no network-related plugins
        # Note: For full isolation use containers (planned). This is minimal for local demo.
        cmd = ["pytest", "-q", "--disable-warnings", "--maxfail=1"]
        proc = subprocess.run(
            cmd,
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=10  # seconds
        )
        output = proc.stdout + "\n" + proc.stderr

        # Parse a simple pass/fail from output
        # Pytest summary lines often look like: "1 passed, 1 failed in 0.05s"
        passed = 0
        failed = 0
        for line in output.splitlines():
            if "passed" in line or "failed" in line:
                # naive parse
                parts = line.replace(",", "").split()
                for i, p in enumerate(parts):
                    if p == "passed":
                        try:
                            passed = int(parts[i-1])
                        except Exception:
                            pass
                    if p == "failed":
                        try:
                            failed = int(parts[i-1])
                        except Exception:
                            pass

        return TestResult(passed=passed, failed=failed, output=output)
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Test run timeout")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error running tests: {e}")
    finally:
        # Clean up temp dir
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass