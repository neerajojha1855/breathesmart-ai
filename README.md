# BreatheSmart AI — Your Intelligent Urban Air Quality Companion

### Production-Grade Full-Stack GenAI Application for Winter Smog & Urban Environmental Resilience

*PromptWars Challenge 6 Submission*

---

## 1. Overview and Problem Statement

Severe winter smog and urban air pollution episodes pose acute health hazards to urban populations. During peak stagnation events, thermal inversions trap toxic concentrations of fine particulate matter (PM2.5, PM10) alongside nitrogen dioxide (NO2), ozone (O3), sulfur dioxide (SO2), and carbon monoxide (CO). Urban residents routinely face:

- **Severe Health Risks**: Microscopic PM2.5 penetrates deep into lung tissue and the bloodstream, exacerbating cardiovascular and respiratory illnesses.
- **Ventilation Dilemma**: Inhabitants either permanently seal homes—causing hazardous indoor CO2 accumulation, volatile organic compound (VOC) buildup, and stale air—or open windows during peak smog spikes.
- **Commuting Vulnerabilities**: Commuters inadvertently increase acute particulate exposure by active travel along congested corridors during morning temperature inversions.
- **Generic, Impersonal Advice**: Public air quality indexes report city-wide averages without time-segmented actionability or personalization for vulnerable groups (children, elderly, respiratory conditions).

**BreatheSmart AI** is a scientifically grounded, full-stack decision-support companion engineered to guide families through acute pollution episodes with actionable intelligence:

1. **Low-Emission Time-Segmented Daily Planner**: Recommends morning, afternoon, evening, and night routines based on forecast diurnal smog dips.
2. **Indoor Air Quality Intelligence**: Evaluates window ventilation suitability against indoor CO2 buildup, schedules HEPA filtration, and specifies kitchen and combustion safety measures.
3. **Sustainable Commute Impact Calculator**: Models modal shifts using UK DEFRA / US EPA emissions conversion factors, strictly distinguishing personal particulate inhalation avoidance from direct greenhouse gas (CO2e) reduction.
4. **Contextually Grounded Conversational AI**: Powered by Groq (`openai/gpt-oss-120b`) with zero-hallucination guardrails and deterministic fallback.

---

## 2. Technical Stack & Architectural Decisions

| Layer | Technologies & Libraries | Architectural Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 19, TypeScript (Strict), Vite, Tailwind CSS, TanStack Query v5, Recharts, Lucide React, Vitest | Zero-`any` type safety, sub-2s production builds, route-level code splitting, accessible charts with semantic table fallbacks. |
| **Backend API** | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), HTTPX, Alembic | Async non-blocking endpoints, strict JSON validation, clean domain layer separation. |
| **Database & Storage**| Neon Serverless PostgreSQL, asyncpg, PgBouncer | Dual-connection architecture: pooled runtime access via PgBouncer and direct unpooled access for Alembic DDL migrations. |
| **Generative AI** | Groq SDK (`openai/gpt-oss-120b`), Pydantic Schema Enforcement | Ultra-fast inference (<1.5s), strict JSON schema prompts, defensive schema normalizer, and zero-hallucination guardrails. |
| **Air Quality & Geocoding** | Open-Meteo Air Quality & Geocoding APIs | Multi-pollutant forecasts with explicit data provenance (`measured`, `modeled`, `forecast`) and in-memory TTL caching. |
| **Code Quality & Testing** | pytest, pytest-asyncio, pytest-cov, Ruff, MyPy, Vitest, Testing Library | 88% backend test coverage, 100% passing frontend suites, zero lint or type errors. |

---

## 3. Security, Resilience & Privacy Guardrails

- **Zero-Trust Session Architecture**: Anonymous, privacy-preserving session tokens generated via `secrets.token_urlsafe(32)`. Only salted SHA-256 hashes are persisted in Neon Postgres; raw tokens are never logged or stored.
- **Double-Submit CSRF Defense**: State-changing operations (`POST`, `PUT`, `DELETE`) require a cryptographically secure `breathe_smart_csrf` token delivered via cookie and validated via the `X-CSRF-Token` header.
- **Sensitive Data & Privacy Consent**: Household vulnerabilities (children, elderly, respiratory sensitivities) require explicit user consent via `sensitive_group_consent`.
- **Zero-Hallucination Policy**: The LLM is **never** the source of truth for atmospheric data. The backend computes verified pollutant metrics and passes them as grounding context.
- **Deterministic Fallback Engine**: If the Groq GenAI service experiences latency, rate limiting, or network interruption, `DeterministicFallbackGenerator` synthesizes validated action plans instantaneously.
- **Credential Redaction in Logs**: Centralized logging filter strips tokens, passwords, and API keys before writing to log streams.

---

## 4. Local Development & Verification

### Prerequisites

- Python 3.12+
- Node.js v20+ / npm v10+
- Neon PostgreSQL Account (or standard PostgreSQL instance)
- Groq API Key

### Backend Setup

```bash
# 1. Navigate to backend and activate virtualenv
cd backend
# Windows:
.\.venv\Scripts\Activate.ps1
# Unix:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Populate DATABASE_URL, DATABASE_URL_UNPOOLED, and GROQ_API_KEY in backend/.env

# 4. Run database migrations
alembic upgrade head

# 5. Start FastAPI application
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev
```

### Reproducible Quality & Verification Commands

```bash
# --- Backend Suite ---
cd backend
python -m pytest -c pytest.ini tests/ --cov=app --cov-report=term-missing
# Result: 30 passed in ~160s, 88% coverage

python -m ruff check app
# Result: All checks passed!

python -m mypy -p app --explicit-package-bases
# Result: Success: no issues found in 51 source files

# --- Frontend Suite ---
cd frontend
npm run lint
# Result: 0 errors

npx tsc -b
# Result: 0 errors

npm test -- --run
# Result: 15 passed across 5 test suites

npm run build
# Result: Production build successfully transformed 2800 modules in 1.52s
```

---

## 5. PromptWars Challenge 6 Submission Matrix

| Challenge Criteria | Implementation Evidence | Test & Verification Reference |
| :--- | :--- | :--- |
| **1. Low-Emission Daily Routine Planner** | `backend/app/services/recommendation_service.py`<br>`frontend/src/pages/PlannerPage.tsx` | Time-segmented recommendations (morning, afternoon, evening, night). Verified in `tests/api/test_endpoints.py` and `src/pages/__tests__/PlannerPage.test.tsx`. |
| **2. Indoor Air Quality & Ventilation Advisor** | `backend/app/services/indoor_air_service.py`<br>`frontend/src/pages/IndoorAdvisorPage.tsx` | Window opening schedule balancing outdoor smog vs. indoor CO2 accumulation; HEPA purifier sizing. Verified in `tests/unit/test_domain_services.py`. |
| **3. Sustainable Commute Impact Calculator** | `backend/app/services/sustainability_service.py`<br>`frontend/src/pages/SustainabilityPage.tsx` | Strict scientific separation of acute personal particulate avoidance from DEFRA/EPA CO2e emission savings. Verified in `tests/unit/test_domain_services.py` and `src/pages/__tests__/SustainabilityPage.test.tsx`. |
| **4. Grounded GenAI Decision Companion** | `backend/app/ai/groq_client.py`<br>`frontend/src/pages/AssistantPage.tsx` | Groq `openai/gpt-oss-120b` grounded exclusively on real-time AQI data; zero-hallucination fallback engine. Verified in `tests/unit/test_ai_service.py` and `tests/unit/test_logging_and_resilience.py`. |
| **5. Neon Postgres & Async Architecture** | `backend/app/db/session.py`<br>`backend/alembic/versions/001_initial_schema.py` | Pooled and unpooled connections, asyncpg, JSONB preference storage, indexed foreign keys. Verified in `tests/api/test_crud_endpoints.py`. |
| **6. Production Security & Code Quality** | `backend/app/core/security.py`<br>`backend/app/api/deps.py` | Double-submit CSRF, token hashing, pip-audit 0 vulnerabilities, npm audit 0 vulnerabilities, MyPy 100% clean, Ruff 100% clean. |
