# TaskQuest Academy - Testing Guide

## Overview

This document describes the testing strategy and instructions for running tests locally.

## Testing Pyramid

```
        ╱╲
       ╱  ╲
      ╱ E2E ╲         End-to-end tests (future)
     ╱────────╲
    ╱Integration╲     API integration tests
   ╱──────────────╲
  ╱   Unit Tests    ╲  Function-level tests
 ╱────────────────────╲
```

## Test Categories

### Unit Tests

Located in `services/api/tests/test_api.py`:

- **Health Endpoint Tests** - Verify `/health` returns correct status
- **Run Endpoint Tests** - Test code execution with various inputs
- **Mission Endpoint Tests** - Verify mission loading and validation
- **Parsing Function Tests** - Test result parsing helpers

### Integration Tests (via TestClient)

The FastAPI TestClient allows testing the full API stack:

```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
response = client.post("/run", json={...})
```

## Running Tests Locally

### Prerequisites

```bash
# Install dependencies
cd services/api
pip install fastapi uvicorn pydantic pytest coverage hypothesis httpx pytest-cov
```

### Running All Tests

```bash
# Using Make
make test

# Using pytest directly
cd services/api
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Running Specific Tests

```bash
# Run a specific test file
pytest tests/test_api.py -v

# Run a specific test class
pytest tests/test_api.py::TestHealthEndpoint -v

# Run a specific test
pytest tests/test_api.py::TestParsingFunctions::test_parse_pass_fail_basic -v
```

### Running with Coverage

```bash
# Generate coverage report
pytest tests/ --cov=. --cov-report=term-missing

# Generate HTML coverage report
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

## Test Output Examples

### Successful Test Run

```
$ pytest tests/ -v
======================== test session starts ========================
tests/test_api.py::TestHealthEndpoint::test_health_returns_ok PASSED
tests/test_api.py::TestRunEndpoint::test_run_valid_code PASSED
tests/test_api.py::TestParsingFunctions::test_parse_pass_fail_basic PASSED
========================= 10 passed in 2.5s =========================
```

### Coverage Report

```
Name       Stmts   Miss  Cover   Missing
-----------------------------------------
main.py      120     15    88%   45-48, 92-95
-----------------------------------------
TOTAL        120     15    88%
```

## Linting

The project uses Ruff for linting and mypy for type checking:

```bash
# Run linting
make lint

# Or individually:
ruff check services/api/
mypy services/api/main.py --ignore-missing-imports
```

## CI Pipeline

Tests are automatically run on every push and pull request via GitHub Actions:

1. **Lint Job** - Runs Ruff and mypy
2. **Test Job** - Runs pytest with coverage (after lint passes)
3. **Coverage Upload** - Reports coverage to Codecov

## Writing New Tests

### Test Structure

```python
class TestNewFeature:
    """Tests for new feature."""
    
    def test_feature_works(self, client):
        """Feature should work correctly."""
        response = client.get("/new-endpoint")
        assert response.status_code == 200
        assert "expected_key" in response.json()
```

### Best Practices

1. **Descriptive Names** - Use clear test and class names
2. **Docstrings** - Document what each test verifies
3. **Isolation** - Tests should not depend on each other
4. **Fixtures** - Use pytest fixtures for common setup
5. **Assertions** - Be specific about what you're testing

## Property-Based Testing (Future)

The platform uses Hypothesis for property-based testing in missions:

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_add_commutative(a, b):
    assert add(a, b) == add(b, a)
```

## Mutation Testing (Future)

For advanced testing, mutmut will be integrated:

```bash
# Run mutation testing
mutmut run --paths-to-mutate=main.py

# View results
mutmut results
```
