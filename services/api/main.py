"""TaskQuest API - Backend for the gamified testing platform."""

import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TaskQuest API",
    description="Backend API for TaskQuest Academy - Gamified Software Testing Platform",
    version="0.1.0"
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunRequest(BaseModel):
    """Request model for running tests."""
    code: str = Field(..., description="Python source code to test", min_length=1)
    tests: str = Field(..., description="Pytest test code", min_length=1)


class TestResult(BaseModel):
    """Response model for test results."""
    passed: int
    failed: int
    coverage_percent: int
    score: int
    output: str


class Mission(BaseModel):
    """Mission model."""
    id: str
    title: str
    title_bg: str
    description: str
    description_bg: str
    min_coverage: int | None = None
    max_failed: int | None = None
    min_passed: int | None = None
    requires_property_keyword: str | None = None
    reward_points: int


class MissionsResponse(BaseModel):
    """Response model for missions list."""
    missions: list[Mission]


class ValidateMissionRequest(BaseModel):
    """Request model for mission validation."""
    mission_id: str = Field(..., description="ID of the mission to validate")
    passed: int = Field(..., ge=0, description="Number of passed tests")
    failed: int = Field(..., ge=0, description="Number of failed tests")
    coverage_percent: int = Field(..., ge=0, le=100, description="Coverage percentage")
    tests_content: str | None = Field(None, description="Test code content for keyword validation")


class ValidationResult(BaseModel):
    """Response model for mission validation."""
    success: bool
    message: str
    reward_points: int | None = None


def load_missions() -> list[dict[str, Any]]:
    """Load missions from the missions.json file."""
    missions_path = Path(__file__).parent.parent.parent / "web" / "missions.json"
    
    if not missions_path.exists():
        logger.warning(f"Missions file not found at {missions_path}")
        return []
    
    try:
        with open(missions_path, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("missions", [])
    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Failed to load missions: {e}")
        return []


@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/missions", response_model=MissionsResponse)
def get_missions() -> MissionsResponse:
    """Get available missions."""
    missions = load_missions()
    return MissionsResponse(missions=[Mission(**m) for m in missions])


@app.post("/validate-mission", response_model=ValidationResult)
def validate_mission(req: ValidateMissionRequest) -> ValidationResult:
    """Validate if test results meet mission requirements."""
    missions = load_missions()
    mission = next((m for m in missions if m["id"] == req.mission_id), None)
    
    if not mission:
        raise HTTPException(status_code=404, detail=f"Mission '{req.mission_id}' not found")
    
    # Check requirements
    failures: list[str] = []
    
    if mission.get("min_coverage") is not None:
        if req.coverage_percent < mission["min_coverage"]:
            failures.append(f"Coverage {req.coverage_percent}% < required {mission['min_coverage']}%")
    
    if mission.get("max_failed") is not None:
        if req.failed > mission["max_failed"]:
            failures.append(f"Failed tests {req.failed} > max allowed {mission['max_failed']}")
    
    if mission.get("min_passed") is not None:
        if req.passed < mission["min_passed"]:
            failures.append(f"Passed tests {req.passed} < required {mission['min_passed']}")
    
    if mission.get("requires_property_keyword"):
        keyword = mission["requires_property_keyword"]
        if req.tests_content and keyword not in req.tests_content:
            failures.append(f"Missing required keyword: '{keyword}'")
    
    if failures:
        return ValidationResult(
            success=False,
            message="Mission requirements not met: " + "; ".join(failures)
        )
    
    return ValidationResult(
        success=True,
        message="Mission completed successfully!",
        reward_points=mission.get("reward_points", 0)
    )


def parse_pass_fail(output: str) -> tuple[int, int]:
    """Parse pytest output to extract passed/failed counts."""
    passed = 0
    failed = 0
    for line in output.splitlines():
        if ("passed" in line or "failed" in line) and "in" in line:
            # Example: "1 passed, 1 failed in 0.05s"
            cleaned = line.replace(",", "")
            parts = cleaned.split()
            for i, p in enumerate(parts):
                if p == "passed" and i > 0:
                    try:
                        passed = int(parts[i - 1])
                    except ValueError:
                        pass
                if p == "failed" and i > 0:
                    try:
                        failed = int(parts[i - 1])
                    except ValueError:
                        pass
    return passed, failed


def parse_coverage(report_output: str) -> int:
    """Parse coverage report to extract coverage percentage."""
    # Coverage report last line example: "TOTAL    5      0   100%"
    coverage_percent = 0
    for line in report_output.splitlines():
        if line.startswith("TOTAL"):
            m = re.search(r"(\d+)%", line)
            if m:
                coverage_percent = int(m.group(1))
    return coverage_percent


@app.post("/run", response_model=TestResult)
def run_tests(req: RunRequest) -> TestResult:
    """Run tests with coverage and return results."""
    # Note: Empty string validation is handled by Pydantic's min_length=1
    # This provides additional protection for whitespace-only inputs
    if not req.code.strip():
        raise HTTPException(status_code=422, detail="Code cannot contain only whitespace")
    if not req.tests.strip():
        raise HTTPException(status_code=422, detail="Tests cannot contain only whitespace")
    
    temp_dir = tempfile.mkdtemp(prefix="taskquest_")
    logger.info(f"Created temp directory: {temp_dir}")
    
    try:
        code_path = os.path.join(temp_dir, "main.py")
        tests_path = os.path.join(temp_dir, "test_main.py")

        with open(code_path, "w", encoding="utf-8") as f:
            f.write(req.code)
        with open(tests_path, "w", encoding="utf-8") as f:
            f.write(req.tests)

        # 1) Run pytest with coverage
        test_cmd = [
            "coverage", "run", "-m", "pytest",
            "-q", "--disable-warnings", "--maxfail=5"
        ]
        test_proc = subprocess.run(
            test_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=15
        )
        test_output = (test_proc.stdout or "") + "\n" + (test_proc.stderr or "")

        passed, failed = parse_pass_fail(test_output)

        # 2) Generate coverage report
        cov_cmd = ["coverage", "report", "--omit", "*/site-packages/*", "--precision", "0"]
        cov_proc = subprocess.run(
            cov_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=10
        )
        coverage_output = (cov_proc.stdout or "") + "\n" + (cov_proc.stderr or "")
        coverage_percent = parse_coverage(coverage_output)

        # Calculate score
        score = passed * 10 - failed * 5 + coverage_percent

        combined_output = test_output + "\n---- COVERAGE REPORT ----\n" + coverage_output

        logger.info(f"Test run complete: passed={passed}, failed={failed}, coverage={coverage_percent}%")
        
        return TestResult(
            passed=passed,
            failed=failed,
            coverage_percent=coverage_percent,
            score=score,
            output=combined_output
        )
    except subprocess.TimeoutExpired:
        logger.error("Test run timeout")
        raise HTTPException(status_code=408, detail="Test run timeout (15s limit exceeded)")
    except Exception as e:
        logger.error(f"Error running tests: {e}")
        raise HTTPException(status_code=400, detail=f"Error running tests: {str(e)}")
    finally:
        try:
            shutil.rmtree(temp_dir)
            logger.debug(f"Cleaned up temp directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")
