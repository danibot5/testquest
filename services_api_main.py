from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import subprocess
import os
import shutil
import re

app = FastAPI(title="TaskQuest API")

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
    coverage_percent: int
    score: int
    output: str

@app.get("/health")
def health():
    return {"status": "ok"}

def parse_pass_fail(output: str):
    passed = 0
    failed = 0
    for line in output.splitlines():
        if ("passed" in line or "failed" in line) and "in" in line:
            # пример: "1 passed, 1 failed in 0.05s"
            cleaned = line.replace(",", "")
            parts = cleaned.split()
            for i, p in enumerate(parts):
                if p == "passed":
                    try: passed = int(parts[i-1])
                    except: pass
                if p == "failed":
                    try: failed = int(parts[i-1])
                    except: pass
    return passed, failed

def parse_coverage(report_output: str):
    # coverage report последна линия може да изглежда:
    # "TOTAL    5      0   100%"
    coverage_percent = 0
    for line in report_output.splitlines():
        if line.startswith("TOTAL"):
            # Извличаме последното число с %.
            m = re.search(r"(\d+)%", line)
            if m:
                coverage_percent = int(m.group(1))
    return coverage_percent

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

        # 1) coverage run pytest
        test_cmd = [
            "coverage", "run", "-m", "pytest",
            "-q", "--disable-warnings", "--maxfail=1"
        ]
        test_proc = subprocess.run(
            test_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=15
        )
        test_output = (test_proc.stdout or "") + "\n" + (test_proc.stderr or "")

        passed, failed = parse_pass_fail(test_output)

        # 2) coverage report
        cov_cmd = ["coverage", "report", "--omit", "*/site-packages/*", "--precision", "0"]
        cov_proc = subprocess.run(
            cov_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=10
        )
        coverage_output = (cov_proc.stdout or "") + "\n" + (cov_proc.stderr or "")
        coverage_percent = parse_coverage(coverage_output)

        # Score формула (можеш да я промениш):
        score = passed * 10 - failed * 5 + coverage_percent

        combined_output = test_output + "\n---- COVERAGE REPORT ----\n" + coverage_output

        return TestResult(
            passed=passed,
            failed=failed,
            coverage_percent=coverage_percent,
            score=score,
            output=combined_output
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Test run timeout")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error running tests: {e}")
    finally:
        try: shutil.rmtree(temp_dir)
        except: pass