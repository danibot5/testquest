# TaskQuest Академия (Gamified Software Testing Tutor)

Кратко описание:
Уеб платформа, която чрез игрови мисии обучава ученици (8–10 клас) на добри практики в софтуерното тестване: unit, интеграционно, property и mutation testing. Целта е да се повиши качеството на ученическите проекти и да се развие аналитично мислене.

Category for NOIT: Софтуерни приложения

Demo goals:
- Редактор на код + изпълнение на тестове в изолирана среда
- Покритие на тестове и mutation score
- Мисии с точки, значки и табло

Tech stack:
- Frontend: React + TypeScript + Monaco Editor
- Backend: FastAPI (Python)
- DB: PostgreSQL
- Queue: Redis (по-късно)
- Testing: pytest, coverage.py, Hypothesis, mutmut
- DevOps: Docker Compose, GitHub Actions

## English Summary
TaskQuest Academy is a gamified web platform teaching students (grades 8–10) core software testing practices: unit, integration, property-based and mutation testing. Goal: raise quality of student projects and strengthen analytical thinking.

## Quick Start (dev)
- Requirements: Docker + Docker Compose
- Commands:
  - `docker compose up --build`
  - Backend: http://localhost:8000
  - Frontend: http://localhost:5173

## Project Structure
- web/ - HTML, CSS, JS
- services/api/ - FastAPI backend
- docs/ - Architecture, testing plan, security notes
- .github/workflows/ — CI pipelines

## License
GPL-3.0-only
