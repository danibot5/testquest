System overview:
- Frontend (React + TS): mission UI, editor, progress, charts
- Backend (FastAPI): auth, mission logic, execution API, analytics
- Sandbox (Docker): per-run isolated containers with resource limits
- DB (PostgreSQL): users, missions, attempts, results
- Queue (Redis, later): async mutation runs

Key components:
- Execution API: accepts source + tests, runs pytest, returns coverage + results
- Mutation Engine: uses mutmut to generate and run mutants; aggregates kill map
- Property Testing: Hypothesis to generate counterexamples; UI shows minimized failing cases

Security:
- No network inside sandbox containers
- CPU/memory limits; timeouts to prevent infinite loops
- Sanitized I/O; restricted filesystem

Data model (initial):
- users(id, username, email, role, created_at)
- missions(id, title, description_md, language, difficulty)
- mission_attempts(id, user_id, mission_id, status, mutation_score, coverage_percent, started_at, finished_at)
- code_submissions(id, attempt_id, created_at, passed_tests, failed_tests, runtime_seconds)
- mutation_runs(id, attempt_id, total, killed, survived, timeouted, details_json, created_at)