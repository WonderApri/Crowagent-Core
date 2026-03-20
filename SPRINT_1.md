# Sprint 1 — Core Features Alignment

## Repository: Crowagent-Core
## Sprint Period: March 2026

### Objective
Stabilise the CrowAgent Platform MVP — physics-informed campus thermal
intelligence for university estate managers.

### Sprint 1 Deliverables

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1 | Beta password gate on Streamlit app | Eng | Done |
| 2 | Enterprise-grade header/footer redesign | Design | Done |
| 3 | UI theme alignment with crowagent.ai website | Design | Done |
| 4 | PINN thermal model validation — accuracy benchmarks | AI/Eng | Planned |
| 5 | Multi-building portfolio comparison view | Eng | Planned |
| 6 | Compliance Hub — MEES, EPC, SECR, Part L, Future Homes | Eng | Planned |
| 7 | PDF report export via fpdf2 | Eng | Planned |
| 8 | Live weather integration — Open-Meteo + Met Office | Eng | Planned |
| 9 | Security hardening per SECURITY_GUIDE.md | Security | Planned |

### Key Metrics
- **Target users**: 5 university estate teams in pilot
- **Model accuracy**: PINN thermal predictions within ±5% of metered data
- **Uptime**: 99.5% on Railway hosting

### Dependencies
- `platform-sdk` — optional auth layer for hosted version
- `crowagent-infra` — `crowagent-platform-ci.yml` for Vercel + Railway deploy
- Open-Meteo API (no key), Met Office DataPoint (free tier)

### Acceptance Criteria
- Streamlit app loads with beta gate
- Dashboard shows energy, carbon, and financial KPIs
- AI Advisor returns physics-informed recommendations
- All pytest tests pass (`pytest tests/`)
