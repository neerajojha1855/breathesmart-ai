# BreatheSmart AI — Architectural Specification

## 1. System Overview & Component Topology

BreatheSmart AI is a production-grade, full-stack, GenAI-powered urban air quality decision companion designed to help families navigate severe winter smog and urban air pollution.

```
                     ┌──────────────────────────────────────────────┐
                     │          Client (React 19 / Vite)            │
                     │   TanStack Query • Tailwind • Recharts       │
                     └──────────────────────┬───────────────────────┘
                                            │ HTTPS / REST + CSRF
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │          FastAPI Application Core            │
                     │  Security Middleware • CORS • Rate Limiting  │
                     └───────┬──────────────┬──────────────┬────────┘
                             │              │              │
             ┌───────────────┘              │              └────────────────┐
             ▼                              ▼                               ▼
 ┌──────────────────────┐      ┌──────────────────────────┐      ┌──────────────────────┐
 │   Groq GenAI Engine  │      │ Neon Serverless Postgres │      │ External Providers   │
 │   gpt-oss-120b       │      │ SQLAlchemy 2.0 (Async)   │      │ Open-Meteo AQI & Wx  │
 │ Pydantic Validation  │      │ JSONB Snapshots & Plans  │      │ Geocoding API        │
 │ Deterministic Fallb. │      │ PgBouncer Connection Pool│      │ In-Memory TTL Cache  │
 └──────────────────────┘      └──────────────────────────┘      └──────────────────────┘
```

---

## 2. Layered Software Architecture

### A. Presentation Layer (`frontend/`)

- **React 19 & TypeScript**: Strict type safety without `any`.
- **TanStack Query v5**: Server-state caching, optimistic updates, and background revalidation.
- **Tailwind CSS & Lucide Icons**: High-contrast, WCAG 2.1 AA accessible theme (emerald/teal accents, distinct state borders).
- **Recharts Data Visualization**: Diurnal pollutant curves with accessible, semantic HTML table alternatives for screen readers.
- **Route Code Splitting**: All major pages (`DashboardPage`, `PlannerPage`, `IndoorAdvisorPage`, `SustainabilityPage`, `ProfilePage`, `AssistantPage`) lazily loaded via `React.lazy()` with skeleton fallbacks.

### B. API & Routing Layer (`backend/app/api/v1/`)

- **Location Endpoints (`/locations`)**: Multi-city search, reverse geocoding, and session-scoped coordinate persistence.
- **Air Quality Endpoints (`/air-quality`)**: Current multi-pollutant readings (PM2.5, PM10, NO2, SO2, O3, CO) and 5-day hourly forecasts tagged with data provenance (`measured`, `modeled`, `forecast`).
- **Recommendation Endpoints (`/recommendations`)**: Time-segmented diurnal action plans and scientific indoor ventilation reports.
- **Sustainability Endpoints (`/sustainability`)**: Comparative commute impact modeling with DEFRA/EPA factors.
- **Conversational Assistant (`/assistant`)**: Natural language chat interface with prompt-injection defenses.
- **Profile & Feedback Endpoints (`/profile`, `/feedback`)**: User preferences, sensitive-group consent toggles, and recommendation ratings.

### C. Business Logic & Domain Services (`backend/app/services/`)

- **`RecommendationService`**: Integrates 5-day forecast dips with user profile preferences to generate morning, afternoon, evening, and night plans.
- **`IndoorAirService`**: Evaluates window ventilation feasibility against acute outdoor PM2.5 and indoor CO2 accumulation hazards; calculates HEPA air purifier CADR and air changes per hour (ACH).
- **`SustainabilityService`**: Computes modal shift emissions savings while strictly distinguishing personal particulate inhalation avoidance from direct greenhouse gas (CO2e) reduction.

### D. Data Provider Abstraction (`backend/app/providers/`)

- **`BaseAirQualityProvider`**: Abstract interface decoupling the application from specific vendors.
- **`OpenMeteoAirQualityProvider`**: HTTPX async client with exponential backoff, jitter, and 15-minute in-memory TTL caching.
- **`OpenMeteoGeocodingProvider`**: Global city search and reverse geocoding client.

### E. Database Layer (`backend/app/db/` & `backend/app/models/`)

- **Neon Serverless PostgreSQL**:
  - `DATABASE_URL`: Pooled connection (PgBouncer) for async runtime operations (`asyncpg`).
  - `DATABASE_URL_UNPOOLED`: Direct connection for transactional DDL migrations via Alembic.
- **Relational Models**:
  - `UserSession`: Opaque tokens hashed with SHA-256.
  - `UserProfile`: Session-bound preferences using PostgreSQL JSONB.
  - `SavedLocation`: Coordinate mappings and primary city selection.
  - `AirQualitySnapshot`: Cached environmental metrics.
  - `RecommendationPlan`: Persisted AI plans and fallbacks.
  - `UserFeedback`: 1-5 star ratings and community qualitative feedback.

---

## 3. Generative AI Architecture & Guardrails

- **Provider**: Groq Cloud API (`https://api.groq.com/openai/v1`).
- **Model**: `openai/gpt-oss-120b`.
- **Zero-Hallucination Policy**: **The LLM is NEVER the source of truth for atmospheric data.**
  1. The backend fetches, validates, and normalizes environmental metrics.
  2. Grounded metrics and user context are embedded into strict system and user prompts.
  3. The model returns structured JSON validated against Pydantic schemas (`BreatheSmartActionPlanResponse`, `AIChatResponse`).
  4. If the model fails validation after retries or encounters network failure, the `DeterministicFallbackGenerator` synthesizes validated, evidence-based recommendations instantly.

---

## 4. Security & Privacy Architecture

1. **Session Management**: Cryptographically secure 32-byte opaque session tokens. The database stores only salted SHA-256 hashes (`hashed_token`). Raw tokens are never persisted or logged.
2. **Double-Submit CSRF Defense**: State-changing requests (`POST`, `PUT`, `DELETE`) require a valid `breathe_smart_csrf` cookie matched against an `X-CSRF-Token` header.
3. **Sensitive Group Consent**: Medical and household vulnerability indicators (children, elderly, asthma) are gated behind explicit user opt-in (`sensitive_group_consent: true`).
4. **Credential Redaction**: A centralized `CredentialMaskingFilter` masks sensitive tokens and connection strings in application logs.
5. **Dependency Audit Compliance**: Maintained zero known vulnerabilities across Python packages (`pip-audit`) and Node modules (`npm audit`).
