# BreatheSmart AI — Architectural Specification

## 1. System Overview & Component Topology

BreatheSmart AI is a production-grade, full-stack, GenAI-powered urban air quality decision companion designed to help families navigate severe winter smog and urban air pollution.

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

---

## 2. Layered Software Architecture

### A. Presentation Layer (`frontend/`)
- **React 19 & TypeScript**: Strict type safety without `any`.
- **TanStack Query v5**: Server-state caching, optimistic updates, and background revalidation.
- **Tailwind CSS & Lucide Icons**: Modern environmental tech aesthetic (emerald/teal accents, high-contrast readable typography).
- **Recharts Data Visualization**: Hourly pollutant trends with accessible HTML table alternatives.
- **Accessibility Layer (WCAG 2.1 AA)**: Semantic HTML5, keyboard navigation, focus rings, and color-blind safe risk indicators.

### B. API & Routing Layer (`backend/app/api/v1/`)
- **Location Endpoints**: City search, reverse geocoding, and user-saved coordinates.
- **Air Quality Endpoints**: Real-time pollutant readings (PM2.5, PM10, NO2, SO2, O3, CO), AQI standard tags, and 5-day forecasts.
- **Recommendation Endpoints**: 4-part segmented daily action plans (Morning, Afternoon, Evening, Night).
- **Conversational Assistant**: Contextually grounded chat interface with prompt-injection defenses.
- **Profile & Feedback**: Session-scoped preference management and recommendation rating storage.

### C. Business Logic & Domain Services (`backend/app/services/`)
- **Recommendation Service**: Integrates live forecast windows with user daily routine.
- **Indoor Air Quality Service**: Balances outdoor smog infiltration against indoor CO2 accumulation to calculate optimal window ventilation windows.
- **Sustainability Service**: Calculates commute emission savings (DEFRA/EPA emission factors) while strictly distinguishing personal particulate exposure from CO2e emissions.

### D. Data Provider Abstraction (`backend/app/providers/`)
- **`BaseAirQualityProvider`**: Abstract interface decoupling the application from specific vendors.
- **Open-Meteo Integration**: HTTPX async client with exponential backoff, jitter, and 15-minute TTL caching. Clearly tags every reading as `measured`, `modeled`, or `forecast`.

### E. Database Layer (`backend/app/db/` & `backend/app/models/`)
- **Neon Serverless PostgreSQL**:
  - `DATABASE_URL`: Pooled connection (PgBouncer) for async runtime operations.
  - `DATABASE_URL_UNPOOLED`: Direct connection for Alembic migrations.
- **Relational Models**:
  - `UserSession`: Opaque tokens hashed with SHA-256.
  - `UserProfile`: Session-bound preferences using PostgreSQL JSONB.
  - `SavedLocation`: Coordinate mappings.
  - `AirQualitySnapshot`: Cached environmental metrics.
  - `RecommendationPlan`: Persisted AI plans and fallbacks.
  - `UserFeedback`: Community quality feedback.

---

## 3. Generative AI Architecture & Guardrails

- **Provider**: Groq (`https://api.groq.com/openai/v1`).
- **Model**: `openai/gpt-oss-120b`.
- **Architectural Principle**: **The LLM is NOT the source of truth.**
  - The backend calculates and validates environmental context and passes trusted data.
  - The LLM synthesizes, contextualizes, and personalizes advice.
  - Strict Pydantic response models validate the JSON structure.
  - If Groq encounters downtime or rate limits, the deterministic fallback engine activates seamlessly.

---

## 4. Security Architecture

1. **Session Management**: Opaque session tokens stored as SHA-256 hashes. Raw tokens never enter the database.
2. **Cookies**: `HttpOnly`, `SameSite=Lax`, and `Secure` in production.
3. **CSRF Protection**: Double-submit cookie pattern for state-changing requests.
4. **Injection Prevention**: Parameterized SQLAlchemy ORM queries and Pydantic v2 input schemas.
5. **Zero Client Secrets**: All external API keys and database credentials reside exclusively in the backend.