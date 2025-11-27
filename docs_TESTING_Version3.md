Testing strategy:
- Unit: mission scoring, result aggregation, API handlers
- Integration: end-to-end run (submit code+tests -> results)
- Property-based: AST transforms and result aggregations maintain invariants
- Mutation: measure mutation score on core modules
- Performance smoke: N runs < threshold time
- Security: sandbox isolation tests (no net, file limits)