"""Tests for TaskQuest API."""

import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app, parse_pass_fail, parse_coverage


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for /health endpoint."""
    
    def test_health_returns_ok(self, client):
        """Health endpoint should return status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestRunEndpoint:
    """Tests for /run endpoint."""
    
    def test_run_valid_code(self, client):
        """Run endpoint should execute valid code and tests."""
        response = client.post("/run", json={
            "code": "def add(a, b):\n    return a + b",
            "tests": "from main import add\n\ndef test_add():\n    assert add(2, 3) == 5"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["passed"] >= 1
        assert data["failed"] == 0
        assert "coverage_percent" in data
        assert "score" in data
        assert "output" in data
    
    def test_run_syntax_error_in_code(self, client):
        """Run endpoint should handle syntax errors in code."""
        response = client.post("/run", json={
            "code": "def add(a, b)\n    return a + b",  # Missing colon
            "tests": "from main import add\n\ndef test_add():\n    assert add(2, 3) == 5"
        })
        # The test should run but fail due to syntax error
        assert response.status_code == 200
        data = response.json()
        # Tests will fail to import due to syntax error
        assert "output" in data
    
    def test_run_empty_code(self, client):
        """Run endpoint should reject empty code."""
        response = client.post("/run", json={
            "code": "",
            "tests": "def test_something(): pass"
        })
        assert response.status_code == 422  # Validation error
    
    def test_run_empty_tests(self, client):
        """Run endpoint should reject empty tests."""
        response = client.post("/run", json={
            "code": "def add(a, b): return a + b",
            "tests": ""
        })
        assert response.status_code == 422  # Validation error
    
    def test_run_failing_test(self, client):
        """Run endpoint should report failing tests."""
        response = client.post("/run", json={
            "code": "def add(a, b):\n    return a - b",  # Wrong implementation
            "tests": "from main import add\n\ndef test_add():\n    assert add(2, 3) == 5"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["failed"] >= 1


class TestMissionsEndpoint:
    """Tests for /missions endpoint."""
    
    def test_get_missions(self, client):
        """Missions endpoint should return list of missions."""
        response = client.get("/missions")
        assert response.status_code == 200
        data = response.json()
        assert "missions" in data
        assert isinstance(data["missions"], list)
    
    def test_missions_have_required_fields(self, client):
        """Each mission should have required fields."""
        response = client.get("/missions")
        assert response.status_code == 200
        missions = response.json()["missions"]
        
        if missions:  # Only test if missions exist
            mission = missions[0]
            assert "id" in mission
            assert "title" in mission
            assert "title_bg" in mission
            assert "description" in mission
            assert "description_bg" in mission
            assert "reward_points" in mission


class TestValidateMissionEndpoint:
    """Tests for /validate-mission endpoint."""
    
    def test_validate_passing_mission(self, client):
        """Validate endpoint should approve passing results."""
        # First get a mission
        missions_response = client.get("/missions")
        if missions_response.status_code == 200 and missions_response.json()["missions"]:
            mission_id = missions_response.json()["missions"][0]["id"]
            
            response = client.post("/validate-mission", json={
                "mission_id": mission_id,
                "passed": 5,
                "failed": 0,
                "coverage_percent": 95
            })
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert "message" in data
    
    def test_validate_nonexistent_mission(self, client):
        """Validate endpoint should reject unknown mission."""
        response = client.post("/validate-mission", json={
            "mission_id": "nonexistent_mission_xyz",
            "passed": 5,
            "failed": 0,
            "coverage_percent": 95
        })
        assert response.status_code == 404


class TestParsingFunctions:
    """Tests for parsing helper functions."""
    
    def test_parse_pass_fail_basic(self):
        """Parse pass/fail from standard pytest output."""
        output = "1 passed in 0.05s"
        passed, failed = parse_pass_fail(output)
        assert passed == 1
        assert failed == 0
    
    def test_parse_pass_fail_mixed(self):
        """Parse pass/fail with mixed results."""
        output = "3 passed, 2 failed in 0.10s"
        passed, failed = parse_pass_fail(output)
        assert passed == 3
        assert failed == 2
    
    def test_parse_pass_fail_only_failed(self):
        """Parse pass/fail with only failures."""
        output = "5 failed in 0.15s"
        passed, failed = parse_pass_fail(output)
        assert passed == 0
        assert failed == 5
    
    def test_parse_pass_fail_empty(self):
        """Parse pass/fail from empty output."""
        output = ""
        passed, failed = parse_pass_fail(output)
        assert passed == 0
        assert failed == 0
    
    def test_parse_coverage_basic(self):
        """Parse coverage percentage from report."""
        output = "Name    Stmts   Miss  Cover\n" \
                 "main.py     10      2    80%\n" \
                 "TOTAL       10      2    80%"
        coverage = parse_coverage(output)
        assert coverage == 80
    
    def test_parse_coverage_full(self):
        """Parse 100% coverage."""
        output = "TOTAL       50      0   100%"
        coverage = parse_coverage(output)
        assert coverage == 100
    
    def test_parse_coverage_empty(self):
        """Parse coverage from empty output."""
        output = ""
        coverage = parse_coverage(output)
        assert coverage == 0
