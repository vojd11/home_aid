# Home Aid Kit Manager — Technical Plan (Multi‑User, Python Backend)

## 0) Objectives

* Build a responsive web app (desktop + mobile) for home aid kit management.
* Core features:

  1. Add medications (name, quantity).
  2. One‑tap decrement (−1) quantity.
  3. Tags: add/remove per medication, filter by tags.
  4. Search within your inventory.
  5. External links: resolve and store links to

     * **Tabletki (tabletki.ua)**: product search results using URL format https://tabletki.ua/uk/search/MEDICATION_NAME
* Multi‑user with households (shared cabinets) and role‑based access.

---

## 1) Non‑Functional Requirements

* **Availability:** 99.5%+ target.
* **Performance:** Local inventory search < \~100ms for 10k items/household.
* **Security:** JWT auth, TLS (HTTPS), per‑route RBAC.
* **Legal/Compliance:** Only store *links* + minimal metadata from external sites; respect robots.txt/ToS; rate‑limit & cache lookups.
* **Observability:** Structured logging, traces, metrics, audit log for inventory changes.
* **Internationalization:** UA/EN UI copy via i18n.

---

## 2) System Architecture

* **Frontend (SPA/PWA):** React + Tailwind + React Query; optional Next.js for SSR.
* **Backend:** Python **FastAPI** (async), **SQLAlchemy** + **Alembic**.
* **DB:** **PostgreSQL** (primary), optional **pg\_trgm** for fuzzy search.
* **Cache/Queue:** **Redis** (rate limits, dedupe, Celery broker/result).
* **Background Jobs:** **Celery** workers for external site lookups, re‑crawls.
* **Object Storage (optional):** S3‑compatible for exports/backups.
* **Auth:** JWT (access + refresh), optional OAuth (Google/Apple) later.
* **Deployment:** Docker + Compose for dev; prod on Fly.io/Render/Hetzner.

```
[React PWA] ⇄ [FastAPI] ⇄ [PostgreSQL]
                 │
                 ├──[Redis: cache + rate limit]
                 └──[Celery workers: Tabletki resolver]
```

---

## 3) Data Model (ERD)

### Core

* **users** (id, email, password\_hash, locale, created\_at, last\_login)
* **households** (id, name, created\_at)
* **household\_members** (id, household\_id, user\_id, role: owner|editor|viewer, invited\_at)
* **medications** (
  id, household\_id, name\_raw, name\_norm, quantity INT NOT NULL DEFAULT 0,
  tabletki\_link,
  notes, created\_by, created\_at, updated\_at
  )
* **tags** (id, household\_id, name\_norm UNIQUE (household\_id, name\_norm))
* **medication\_tags** (medication\_id, tag\_id, UNIQUE (medication\_id, tag\_id))

### History/Audit

* **inventory\_events** (id, medication\_id, user\_id, delta INT, reason ENUM('add','decrement','set','import'), created\_at)
* **activity\_log** (id, household\_id, user\_id, action, entity\_type, entity\_id, created\_at, meta JSONB)

### Integrations

* **external\_resolutions** (id, medication\_id, source ENUM('TABLETKI'),
  query TEXT, result\_title TEXT NULL, page\_url TEXT,
  status ENUM('SUCCESS','NO\_MATCH','ERROR'), fetched\_at, http\_status, hash)

**Indexes**

* medications: (household\_id, name\_norm), gin\_trgm\_ops on name\_norm, gin on tags via materialized view (optional)

**Normalization rules**

* `name_norm` = uppercased, stripped punctuation/extra spaces; store both raw and norm for display + search.

---

## 4) External Link Resolution (DRLZ & Tabletki)

### Strategy

* **On create/edit** of a medication, enqueue a background job:

  * Build query string from `name_norm`.
  * **DRLZ**: Use the public search endpoint; parse first relevant hit (title + href). If an “instruction” (leaflet) link is present on the product page, store it.
  * **Tabletki**: Store the *search URL* (always valid); optionally, if permitted, parse first result and store a canonical product URL.
* **Caching**: (Redis) key by `(source, query_hash)` for 7 days. Avoid hammering external sites.
* **Rate limiting**: e.g., 1 req/sec/site/app‑wide, 10/min per household.
* **Resilience**: retry with exponential backoff, degrade gracefully (only save search URL if parsing fails).
* **Compliance note**: do not store scraped content; only store URLs + result title.

### URL builders

* DRLZ search: `http://www.drlz.com.ua/ibp/ddsite.nsf/all/shlist?opendocument&query=<urlencoded>`
* Tabletki search: `https://tabletki.ua/uk/search/<urlencoded>`

---

## 5) API Design (FastAPI)

**Auth**

* `POST /auth/register` (email, password)
* `POST /auth/login` → {access, refresh}
* `POST /auth/refresh`

**Households**

* `GET /households`
* `POST /households` (name)
* `POST /households/{id}/members` (invite email, role)
* `PATCH /households/{id}/members/{userId}` (role)

**Medications**

* `POST /households/{hid}/medications` (name, quantity)
* `GET /households/{hid}/medications?search=&tag=&limit=&cursor=`
* `GET /households/{hid}/medications/{mid}`
* `PATCH /households/{hid}/medications/{mid}` (name?, quantity?)
* `POST /households/{hid}/medications/{mid}/decrement` (amount=1 default)
* `DELETE /households/{hid}/medications/{mid}`

**Tags**

* `POST /households/{hid}/tags` (name)
* `DELETE /households/{hid}/tags/{tid}`
* `POST /households/{hid}/medications/{mid}/tags/{tid}`
* `DELETE /households/{hid}/medications/{mid}/tags/{tid}`

**Integrations**

* `POST /households/{hid}/medications/{mid}/resolve-links` (force re‑resolve)
* `GET /households/{hid}/medications/{mid}/links` → {tabletki\_link}

**Exports**

* `GET /households/{hid}/export.csv`

**Observability**

* `GET /households/{hid}/activity` (paginated)

---

## 6) Backend Implementation Notes

* **FastAPI**: async routes, pydantic models, OpenAPI docs.
* **DB layer**: SQLAlchemy 2.0 (async), Alembic for migrations.
* **Search**: ILIKE on name\_norm; enable `pg_trgm` for fuzzy (`%` similarity) optional.
* **Concurrency**: Use `httpx.AsyncClient` for outbound resolver calls.
* **Background jobs**: Celery (`redis://`) with tasks: `resolve_tabletki(query)`; idempotent by `hash=(source+query_norm)`.
* **Security**: Passlist CORS (frontend origin), rate limits via Redis (sliding window), input validation, audit logs on inventory change.
* **Testing**: pytest + httpx test client; VCR.py to record resolver fixtures.

---

## 7) Frontend Implementation Notes

* **Framework**: React (Vite or Next.js). Tailwind for styling; shadcn/ui for components.
* **State & Data**: React Query (server cache), Zod schemas mirroring Pydantic for client‑side validation.
* **PWA**: manifest.json, service worker for offline read + queued writes (background sync) optional.
* **Responsive layout**

  * **Mobile**: sticky search at top; list with quantity pill + −1 button; FAB (+) to add.
  * **Desktop**: 2‑column layout — left: tag filters; right: list/table.
* **Key components**

  * `MedicationList` (virtualized)
  * `MedicationCard` (name, qty, tags, links, −1 button)
  * `TagChips` (add/remove)
  * `SearchBar` (debounced)
  * `AddMedicationDialog`
  * `LinkBadges` (Tabletki)

---

## 8) UX Flows

1. **Add med**: user types *"Ібупрофен"* → create with qty → optimistic card shows → background job generates Tabletki search link → link badge appears.
2. **Decrement**: tap `−1` → optimistic update → event logged.
3. **Tagging**: typeahead create new tag (Enter), chip appears; click × to remove.
4. **Search**: typeahead across name + tags; optional fuzzy.

---

## 9) Tabletki Resolver Pseudocode (Python)

```py
async def search_tabletki(query: str) -> str:
    # Simply return search URL - no HTTP request needed
    return f"https://tabletki.ua/uk/search/{quote(query)}"
```

---

## 10) Roles & Permissions

* **owner**: manage members, delete household, full edit.
* **editor**: CRUD meds/tags, export.
* **viewer**: read‑only.
* **Rate limiting** per user+household.

---

## 11) Validation & Edge Cases

* Normalize names; prevent duplicates per household (merge prompt if near‑duplicate by trigram similarity > 0.9).
* Quantities are non‑negative; guard underflow on decrement; allow configurable minimum.
* Unicode search (UA/RU/EN); handle diacritics.
* External resolver fallbacks when offline/timeouts.

---

## 12) Monitoring & Telemetry

* **Logs**: JSON logs (uvicorn), request IDs, user IDs, latency.
* **Metrics**: Prometheus counters/histograms: resolver success/fail, queue depth, API latencies.
* **Alerts**: on 5xx rate spikes, resolver errors > threshold.

---

## 13) DevOps & Environments

* **Dev**: Docker Compose: postgres, redis, api, worker, frontend.
* **CI**: GitHub Actions: lint (ruff), test, build, migrations check.
* **CD**: Tag → build → deploy → Alembic upgrade.
* **Secrets**: 12‑factor via env vars.

---

## 14) Project Timeline (Sprints)

* **Sprint 1 (Backend core)**: Auth, households, meds CRUD, decrement + audit; DB migrations.
* **Sprint 2 (Frontend MVP)**: List, search, tags, decrement, add flow.
* **Sprint 3 (Integrations)**: Celery, Redis, Tabletki resolver, link badges.
* **Sprint 4 (Production hardening)**: rate limits, caching, monitoring, i18n, PWA.

---

## 15) Acceptance Criteria (MVP)

* Create household, invite second user.
* Add “Ібупрофен 200 мг”, set qty=20; see item in list.
* Click −1 → qty decremented, cannot go below 0.
* Add tags “біль”, “грип”. Filter by tag shows only tagged meds.
* Search “ібупр” finds item.
* Item shows Tabletki search link.

---

## 16) Nice‑to‑Haves (Post‑MVP)

* Expiry dates + reminders.
* Bar‑code scan on mobile to prefill names.
* Bulk import/export CSV.
* Multi‑language synonyms (ibuprofen/ібупрофен/ибупрофен).
* Per‑item min stock + low‑stock notifications (email/Telegram).

---

## 17) Example FastAPI Schemas (abridged)

```py
class MedicationIn(BaseModel):
    name: constr(min_length=1)
    quantity: conint(ge=0) = 0

class MedicationOut(BaseModel):
    id: int
    name: str
    quantity: int
    tags: list[str]
    tabletki_link: HttpUrl | None
```

---

## 18) Security & Legal Notes

* Present clear **disclaimer**: links lead to third‑party info; always read official instructions and consult a professional.
* Respect robots.txt; throttle resolvers; avoid storing third‑party content.
* User data: store hashed passwords (argon2/bcrypt), rotate JWT secrets on breach, implement refresh token revocation.

---

## 19) Sample DB Migration (SQL, sketch)

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  locale TEXT DEFAULT 'uk-UA',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE households (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE household_members (
  id BIGSERIAL PRIMARY KEY,
  household_id BIGINT REFERENCES households(id) ON DELETE CASCADE,
  user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
  role TEXT CHECK (role IN ('owner','editor','viewer')) NOT NULL,
  UNIQUE (household_id, user_id)
);

CREATE TABLE medications (
  id BIGSERIAL PRIMARY KEY,
  household_id BIGINT REFERENCES households(id) ON DELETE CASCADE,
  name_raw TEXT NOT NULL,
  name_norm TEXT NOT NULL,
  quantity INT NOT NULL DEFAULT 0,
  tabletki_link TEXT,
  notes TEXT,
  created_by BIGINT REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX meds_name_norm_idx ON medications USING gin (name_norm gin_trgm_ops);

CREATE TABLE tags (
  id BIGSERIAL PRIMARY KEY,
  household_id BIGINT REFERENCES households(id) ON DELETE CASCADE,
  name_norm TEXT NOT NULL,
  UNIQUE (household_id, name_norm)
);

CREATE TABLE medication_tags (
  medication_id BIGINT REFERENCES medications(id) ON DELETE CASCADE,
  tag_id BIGINT REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (medication_id, tag_id)
);

CREATE TABLE inventory_events (
  id BIGSERIAL PRIMARY KEY,
  medication_id BIGINT REFERENCES medications(id) ON DELETE CASCADE,
  user_id BIGINT REFERENCES users(id),
  delta INT NOT NULL,
  reason TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE external_resolutions (
  id BIGSERIAL PRIMARY KEY,
  medication_id BIGINT REFERENCES medications(id) ON DELETE CASCADE,
  source TEXT NOT NULL,
  query TEXT NOT NULL,
  result_title TEXT,
  page_url TEXT,
  instruction_url TEXT,
  status TEXT NOT NULL,
  http_status INT,
  fetched_at TIMESTAMPTZ DEFAULT now(),
  hash TEXT
);
```

---

## 20) Implementation Checklist

* [ ] Repo scaffolding (frontend, api, worker, infra)
* [ ] DB & migrations
* [ ] Auth & households
* [ ] Meds CRUD + decrement + audit
* [ ] Tags CRUD + filter
* [ ] Search (name + tags)
* [ ] Celery + Redis + resolvers
* [ ] Rate limit + cache
* [ ] PWA polish
* [ ] Telemetry + alerts
* [ ] CI/CD

---

## 21) Next Step — Choose Frontend Baseline

* **Option A:** Vite + React + Router (simpler, pure SPA)
* **Option B:** Next.js (SSR/ISR for SEO; nice DX).
  For an authenticated app, **Option A** is perfectly fine and fast.
