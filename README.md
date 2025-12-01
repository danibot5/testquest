# TaskQuest Академия

[![CI](https://github.com/danibot5/TaskQuestAcademy/actions/workflows/ci.yml/badge.svg)](https://github.com/danibot5/TaskQuestAcademy/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)

🎮 **Gamified Software Testing Tutor** / **Уеб платформа за обучение по софтуерно тестване чрез игрови мисии**

---

## 📖 Overview / Описание

**English:**
TaskQuest Academy is a gamified web platform teaching students (grades 8–10) core software testing practices: unit testing, integration testing, property-based testing, and mutation testing. The platform uses game mechanics to make learning engaging and fun.

**Български:**
TaskQuest Академия е уеб платформа, която чрез игрови мисии обучава ученици (8–10 клас) на добри практики в софтуерното тестване: unit, интеграционно, property и mutation testing. Целта е да се повиши качеството на ученическите проекти и да се развие аналитично мислене.

---

## ✨ Features / Функционалности

- 📝 **Code Editor** - Write Python code and tests directly in the browser
- 🧪 **Test Execution** - Run pytest in an isolated environment
- 📊 **Coverage Analysis** - Get code coverage reports with visual feedback
- 🎯 **Missions** - Complete gamified missions with increasing difficulty
- 🏆 **Scoring System** - Earn points and rewards for completing missions
- 🌙 **Dark Mode** - Automatic dark mode based on system preferences
- 🇧🇬 **Bulgarian Support** - Full Bulgarian language localization

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | HTML5, CSS3, JavaScript (Vanilla) |
| **Backend** | FastAPI (Python 3.11) |
| **Testing** | pytest, coverage.py, Hypothesis |
| **Container** | Docker, Docker Compose |
| **Web Server** | Nginx (for static files) |
| **CI/CD** | GitHub Actions |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Running with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/danibot5/TaskQuestAcademy.git
cd TaskQuestAcademy

# Start all services
docker compose up --build

# Access the application:
# - Frontend: http://localhost:3000
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Running Locally (Development)

```bash
# Install Python dependencies
cd services/api
pip install -r requirements.txt  # or use pyproject.toml
pip install fastapi uvicorn pydantic pytest coverage hypothesis

# Start the API server
uvicorn main:app --reload --port 8000

# Serve the frontend (in another terminal)
cd web
python -m http.server 3000
```

---

## 📁 Project Structure

```
TaskQuestAcademy/
├── .github/
│   └── workflows/
│       └── ci.yml          # CI pipeline configuration
├── docs/
│   ├── ARCHITECTURE.md     # System architecture documentation
│   └── TESTING.md          # Testing strategy documentation
├── services/
│   └── api/
│       ├── main.py         # FastAPI application
│       ├── Dockerfile      # API container configuration
│       ├── pyproject.toml  # Python project configuration
│       └── tests/
│           └── test_api.py # API unit tests
├── web/
│   ├── index.html          # Main HTML page
│   ├── app.js              # Frontend JavaScript
│   ├── style.css           # Styles with dark mode support
│   └── missions.json       # Mission definitions
├── docker-compose.yml      # Multi-container configuration
├── nginx.conf              # Nginx configuration for frontend
├── Makefile                # Development commands
├── .env.example            # Environment variables template
└── README.md               # This file
```

---

## 🎯 Available Missions

| Mission | Description | Requirements | Points |
|---------|-------------|--------------|--------|
| **Basic Quality** | Introduction to unit testing | 80% coverage, 0 failed tests | 50 |
| **Edge Cases** | Testing boundary conditions | 90% coverage, 3+ passing tests | 75 |
| **Property Testing** | Property-based testing with Hypothesis | Use @given decorator | 100 |
| **Mutation Testing** | Understanding mutation testing | 95% coverage, 5+ passing tests | 150 |

---

## 🧪 Running Tests

```bash
# Using Make
make test

# Or directly with pytest
cd services/api
pytest tests/ -v --cov=. --cov-report=term-missing
```

---

## 🔧 Development

### Useful Commands

```bash
# Start all services
make run

# Start API in development mode
make dev

# Run linting
make lint

# Run tests
make test

# Clean up containers and cache
make clean
```

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000,http://localhost:5173` |
| `LOG_LEVEL` | Logging level | `INFO` |

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Guidelines
- Follow PEP 8 for Python code
- Add tests for new features
- Update documentation as needed
- Keep commits focused and descriptive

---

## 📄 License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE.txt](LICENSE.txt) file for details.

---

## 📞 Contact

- **Category for NOIT:** Софтуерни приложения
- **Repository:** [GitHub](https://github.com/danibot5/TaskQuestAcademy)

---

<p align="center">
Made with ❤️ for Bulgarian students
</p>
