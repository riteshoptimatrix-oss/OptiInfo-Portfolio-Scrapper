# 🚀 OptiInfo Portfolio Scraper & Analysis

A production-ready full-stack monorepo that scrapes portfolio cards from [OptiInfo Our Works](https://www.optiinfo.com/our-works/) using **Python Playwright**, stores them in **SQLite**, and deep-analyzes each website's tech stack (backend, frontend, hosting, CMS, CDN, security, SSL, DNS, HTTP headers) via a **FastAPI** backend that powers a **Next.js** dashboard.

---

## ✨ Features

- **🗂️ Portfolio Scraping** – Direct DOM scraping of OptiInfo portfolio cards using Python Playwright (100% first-party, no third-party scraping APIs).
- **🔍 Website Analysis Engine** – Fingerprints each scraped website:
  - Tech stack detection: CMS, frontend frameworks, backend, database, server
  - Infrastructure: hosting, CDN, deployment, e-commerce platforms, integrations, analytics
  - Security: SSL/TLS, headers, HTTP security hardening
  - DNS & HTTP layer inspection
  - Confidence scoring + automatic classification
- **⚡ Async Job Management** – Bulk analysis queued and processed asynchronously with stop/cancel support.
- **📊 Dashboard** – Next.js + TypeScript + Tailwind dashboard with search, category filters, pagination, live scrape progress, and per-website analysis results.
- **📤 Export** – CSV/Excel export of scraped data.
- **🛡️ Hardened API** – Structured logging, global exception handlers (no stack traces leaked), CORS config, and SQLAlchemy-backed persistence.

---

## 🔒 Compliance Rules

- ❌ NO third-party scraping APIs (Apify, Firecrawl, RapidAPI, SerpAPI, etc.)
- ❌ NO OpenAI / AI extraction APIs
- ❌ NO external data services
- ✅ **100% Direct DOM inspection via Python Playwright**
- ✅ **FastAPI as custom backend API**
- ✅ **SQLite local database**
- ✅ **Next.js + TypeScript + Tailwind CSS dashboard**

---

## 📁 Project Structure

```text
Scrapper & Analysis/
├── .gitignore
├── README.md
├── backend/
│   ├── .env.example
│   ├── requirements.txt
│   ├── tests/
│   │   └── test_analyzer_rules.py
│   └── app/
│       ├── main.py                      # FastAPI entry, CORS, global exception handlers
│       ├── core/
│       │   ├── config.py                # Pydantic settings (env-driven)
│       │   ├── database.py              # SQLAlchemy engine & sessions
│       │   ├── logging_config.py        # Structured logging setup
│       │   └── async_utils.py
│       ├── models/
│       │   ├── portfolio.py             # PortfolioItem / Website models
│       │   └── analysis.py              # Analysis result models
│       ├── schemas/
│       │   ├── portfolio.py
│       │   ├── analysis.py
│       │   └── scraper.py
│       ├── routes/
│       │   ├── health.py                # GET /api/health
│       │   ├── scraper.py               # POST /start, GET /status
│       │   ├── portfolio.py             # GET /portfolios, /categories, /stats
│       │   ├── analyzer.py              # analyze, bulk-analyze, status, stats
│       │   └── export.py                # CSV/Excel export
│       ├── scraper/
│       │   ├── browser.py               # Playwright browser manager
│       │   ├── parser.py                # DOM card parser
│       │   ├── portfolio_scraper.py
│       │   ├── cli.py
│       │   └── utils.py
│       ├── analyzer/
│       │   ├── analyzer_service.py
│       │   ├── browser_analyzer.py
│       │   ├── classifier.py
│       │   ├── confidence.py
│       │   ├── dns_analyzer.py
│       │   ├── fingerprint_engine.py
│       │   ├── http_analyzer.py
│       │   ├── security.py
│       │   ├── ssl_analyzer.py
│       │   └── detectors/               # cms, cdn, hosting, backend, frontend,
│       │       └── ...                  # ecommerce, analytics, integrations, etc.
│       └── services/
│           ├── analyzer_job_manager.py  # async analysis job queue
│           ├── playwright_scraper.py
│           ├── portfolio_service.py
│           └── scraper_service.py
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── next.config.ts
    ├── .env.example
    ├── app/
    │   ├── layout.tsx
    │   ├── globals.css
    │   └── page.tsx                     # Dashboard homepage
    ├── components/
    │   ├── layout/                      # Header / Navbar
    │   ├── dashboard/                   # Cards, table, filters, pagination, scrape progress
    │   └── analysis/                    # Analysis modal & tab
    └── lib/
        ├── api.ts                       # Centralized API client
        ├── constants.ts
        └── types.ts                     # TypeScript interfaces
```

---

## ⚙️ Prerequisites

- **Python 3.12+**
- **Node.js 20+** (npm)
- **Playwright** supported browser (Chromium)

---

## 🛠️ Installation

### 1. Backend

```bash
cd backend

# Create & activate virtual environment
python -m venv myenv
# Windows PowerShell:
.\myenv\Scripts\Activate.ps1
# Linux/macOS:
source myenv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright Chromium browser
playwright install chromium

# Configure environment
cp .env.example .env
```

### 2. Frontend

```bash
cd frontend

# Configure environment
cp .env.example .env.local

# Install Node dependencies
npm install
```

---

## 🏃 Running the Application

### Backend API

```bash
cd backend
.\myenv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **API Base URL:** `http://localhost:8000`
- **Swagger Docs:** `http://localhost:8000/api/docs`
- **ReDoc:** `http://localhost:8000/api/redoc`
- **Health Check:** `http://localhost:8000/api/health`

### Frontend Dashboard

```bash
cd frontend
npm run dev
```

- **Dashboard:** `http://localhost:3000`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health status (API, DB, Playwright) |
| `POST` | `/api/scraper/start` | Start a scrape job |
| `GET` | `/api/scraper/status` | Scrape job progress |
| `GET` | `/api/portfolios` | Paginated portfolio list (search/filter) |
| `GET` | `/api/portfolios/{id}` | Single portfolio detail |
| `DELETE` | `/api/portfolios/{id}` | Delete a portfolio item |
| `GET` | `/api/categories` | Available categories |
| `GET` | `/api/stats` | Dashboard stats |
| `POST` | `/api/websites/{id}/analyze` | Analyze a single website |
| `POST` | `/api/websites/analyze-bulk` | Bulk-analyze websites (async job) |
| `POST` | `/api/websites/analyze-stop` | Stop running analysis jobs |
| `GET` | `/api/websites/{id}/analysis` | Analysis result of a website |
| `GET` | `/api/websites/{id}/analysis/status` | Analysis job status |
| `GET` | `/api/analyses` | All analyses |
| `GET` | `/api/analysis/stats` | Analysis statistics |
| `GET` | `/api/export` | Export portfolios (CSV/Excel) |

All endpoints are also available under `/api/v1/...` for backward compatibility.

---

## 🔧 Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Bind host |
| `PORT` | `8000` | Bind port |
| `DATABASE_URL` | `sqlite:///./portfolio_scraper.db` | SQLAlchemy DB URL |
| `PLAYWRIGHT_HEADLESS` | `true` | Headless browser mode |
| `CORS_ORIGINS` | JSON array | Allowed CORS origins |

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Backend API base URL |

---

## 🧪 Tests

```bash
cd backend
.\myenv\Scripts\Activate.ps1
pytest
```

Additional verification/diagnostic scripts live in `backend/tests/`.

---

## ⚠️ Notes

- `backend/.env`, `frontend/.env.local`, SQLite databases (`*.db`), local virtual environments, and `node_modules` are git-ignored — never commit secrets.
- The scraper targets `https://www.optiinfo.com/our-works/` (configurable via `TARGET_URL` in backend settings).