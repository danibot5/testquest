# TaskQuest Academy - Architecture

## System Overview

TaskQuest Academy is a web-based educational platform that teaches software testing concepts through gamified missions. The architecture follows a simple client-server model with containerized deployment.

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                         │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     Nginx (Port 3000)                       │
│                    Static File Server                       │
│              - index.html, app.js, style.css               │
└─────────────────────────────┬───────────────────────────────┘
                              │ /api/* proxy
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Port 8000)                │
│                                                             │
│  Endpoints:                                                 │
│  - GET  /health          Health check                       │
│  - GET  /missions        List available missions            │
│  - POST /run             Execute code with tests            │
│  - POST /validate-mission Validate mission completion       │
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Isolated Test Execution                    │
│            (Temporary directories with timeout)             │
│                                                             │
│  - pytest for test execution                                │
│  - coverage.py for code coverage                            │
│  - Resource limits and timeouts                             │
└─────────────────────────────────────────────────────────────┘
```

## Key Components

### Frontend (web/)

The frontend is a vanilla JavaScript application with no framework dependencies:

- **index.html** - Main HTML structure with mission selector and code editors
- **app.js** - JavaScript logic for mission loading, test execution, and result display
- **style.css** - Responsive styles with CSS variables for dark mode support
- **missions.json** - Static mission definitions with Bulgarian translations

### Backend (services/api/)

The backend is built with FastAPI and provides:

- **main.py** - Core API application with all endpoints
- **Dockerfile** - Container configuration for the API
- **pyproject.toml** - Python project metadata and dependencies
- **tests/** - API unit tests

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check for monitoring |
| `/missions` | GET | Returns list of available missions |
| `/run` | POST | Executes code with tests and returns results |
| `/validate-mission` | POST | Validates if results meet mission requirements |

### Test Execution Flow

1. User submits code and tests via the frontend
2. API creates a temporary directory
3. Code and tests are written to files
4. `coverage run -m pytest` executes the tests
5. `coverage report` generates coverage data
6. Results are parsed and returned to the frontend
7. Temporary directory is cleaned up

## Security Considerations

- **Isolated Execution** - Each test run uses a fresh temporary directory
- **Timeouts** - Test execution has a 15-second timeout
- **No Network** - Future: sandbox containers without network access
- **Resource Limits** - Future: CPU/memory limits per execution

## Data Model (Future)

```
users(id, username, email, role, created_at)
missions(id, title, description_md, language, difficulty)
mission_attempts(id, user_id, mission_id, status, mutation_score, coverage_percent)
code_submissions(id, attempt_id, passed_tests, failed_tests, runtime_seconds)
```

## Deployment

### Docker Compose

The application is deployed using Docker Compose with two services:

1. **api** - FastAPI backend with hot reload
2. **web** - Nginx serving static files

### CI/CD Pipeline

GitHub Actions workflow includes:
- Code linting with Ruff
- Type checking with mypy
- Test execution with pytest
- Coverage reporting

## Future Enhancements

- [ ] Database integration (PostgreSQL)
- [ ] User authentication and progress tracking
- [ ] Redis queue for async mutation testing
- [ ] Docker sandboxes for enhanced security
- [ ] Monaco Editor for better code editing
- [ ] Mutation testing with mutmut
