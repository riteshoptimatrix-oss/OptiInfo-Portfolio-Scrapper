<div align="center">

# 🕷️ OptiInfo Portfolio Scraper & Analysis

**A production-ready full-stack monorepo that scrapes, stores, and deep-analyzes portfolio websites — zero third-party scraping APIs, 100% custom-built.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Playwright](https://img.shields.io/badge/Playwright-Chromium-45ba4b?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev)
[![SQLite](https://img.shields.io/badge/SQLite-Local_DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)

</div>

---

## 📌 What Is This?

This monorepo scrapes portfolio cards from [OptiInfo Our Works](https://www.optiinfo.com/our-works/) using **Python Playwright**, stores them in **SQLite**, and deep-analyzes each website's full tech stack via a **FastAPI** backend — all powered by a live **Next.js** dashboard.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🗂️ **Portfolio Scraping** | Direct DOM scraping via Python Playwright — no third-party APIs |
| 🔍 **Website Analysis Engine** | Fingerprints CMS, frontend, backend, hosting, CDN, e-commerce, SSL/TLS, DNS, HTTP headers |
| 🔐 **Security Audit** | SSL certificate check, HTTP security header hardening analysis |
| ⚡ **Async Job Management** | Bulk analysis queued asynchronously with stop/cancel support |
| 📊 **Live Dashboard** | Next.js + TypeScript + Tailwind, search, filters, pagination, live scrape progress |
| 📤 **Export** | CSV/Excel export of all scraped & analyzed data |
| 🛡️ **Hardened API** | Structured logging, global exception handlers (no stack traces leaked), CORS config |

---

## 🔒 Compliance Rules

> This project was built under strict constraints:

- ❌ NO third-party scraping APIs (Apify, Firecrawl, RapidAPI, SerpAPI, etc.)
- ❌ NO OpenAI / AI extraction APIs
- ❌ NO external data services
- ✅ **100% Direct DOM inspection via Python Playwright**
- ✅ **FastAPI as custom backend API**
- ✅ **SQLite local database**
- ✅ **Next.js + TypeScript + Tailwind CSS dashboard**

---

## 🛠️ Tech Stack

### Backend
| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Web Framework | FastAPI + Uvicorn |
| Browser Automation | Playwright (Chromium) |
| ORM | SQLAlchemy |
| Database | SQLite |
| Data Export | Pandas + OpenPyXL |
| Config | Pydantic Settings + python-dotenv |
| HTTP Client | HTTPX |

### Frontend
| Layer | Technology |
|---|---|
| Framework | Next.js 16 (App Router) |
| Language | TypeScript 5 |
| Styling | Tailwind CSS 4 |
| Runtime | Node.js 20+ |

---

## 📁 Project Structure

```text
Scrapper & Analysis/
├── .gitignore
├── README.md
├── backend/
│   ├── .env.example              ← copy to .env
│   ├── requirements.txt
│   ├── tests/
│   │   └── test_analyzer_rules.py
│   └── app/
│       ├── main.py               # FastAPI entry, CORS, global exception handlers
│       ├── core/
│       │   ├── config.py         # Pydantic settings (env-driven)
│       │   ├── database.py       # SQLAlchemy engine & sessions
│       │   ├── logging_config.py # Structured logging setup
│       │   └── async_utils.py
│       ├── models/
│       │   ├── portfolio.py      # PortfolioItem / Website models
│       │   └── analysis.py       # Analysis result models
│       ├── schemas/
│       │   ├── portfolio.py
│       │   ├── analysis.py
│       │   └── scraper.py
│       ├── routes/
│       │   ├── health.py         # GET /api/health
│       │   ├── scraper.py        # POST /start, GET /status
│       │   ├── portfolio.py      # GET /portfolios, /categories, /stats
│       │   ├── analyzer.py       # analyze, bulk-analyze, status, stats
│       │   └── export.py         # CSV/Excel export
│       ├── scraper/
│       │   ├── browser.py        # Playwright browser manager
│       │   ├── parser.py         # DOM card parser
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
│       │   └── detectors/        # cms, cdn, hosting, backend, frontend,
│       │       └── ...           # ecommerce, analytics, integrations, etc.
│       └── services/
│           ├── analyzer_job_manager.py  # async analysis job queue
│           ├── playwright_scraper.py
│           ├── portfolio_service.py
│           └── scraper_service.py
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── next.config.ts
    ├── .env.example              ← copy to .env.local
    ├── app/
    │   ├── layout.tsx
    │   ├── globals.css
    │   └── page.tsx              # Dashboard homepage
    ├── components/
    │   ├── layout/               # Header / Navbar
    │   ├── dashboard/            # Cards, table, filters, pagination, scrape progress
    │   └── analysis/             # Analysis modal & tab
    └── lib/
        ├── api.ts                # Centralized API client
        ├── constants.ts
        └── types.ts              # TypeScript interfaces
```

---

## ⚙️ Prerequisites

- **Python 3.12+**
- **Node.js 20+** (npm)
- **Playwright** supported browser (Chromium)

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd "Scrapper & Analysis"
```

### 2. Backend Setup

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
# Edit .env with your settings
```

### 3. Frontend Setup

```bash
cd frontend

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API base URL

# Install Node dependencies
npm install
```

---

## ▶️ Running the Application

### Start the Backend API

```bash
cd backend
.\myenv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

| URL | Description |
|---|---|
| `http://localhost:8000` | API Base URL |
| `http://localhost:8000/api/docs` | Swagger UI |
| `http://localhost:8000/api/redoc` | ReDoc |
| `http://localhost:8000/api/health` | Health Check |

### Start the Frontend Dashboard

```bash
cd frontend
npm run dev
```

- **Dashboard:** `http://localhost:3000`

---

## 🔌 API Reference

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

> All endpoints are also available under `/api/v1/...` for backward compatibility.

---

## 🔧 Environment Variables

### Backend — `backend/.env`

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Bind host |
| `PORT` | `8000` | Bind port |
| `DATABASE_URL` | `sqlite:///./portfolio_scraper.db` | SQLAlchemy DB URL |
| `PLAYWRIGHT_HEADLESS` | `true` | Headless browser mode |
| `CORS_ORIGINS` | JSON array | Allowed CORS origins |

### Frontend — `frontend/.env.local`

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` | Backend API base URL |

> ⚠️ **Never commit `.env` files.** Use `.env.example` as the template only.

---

## 🧪 Tests

```bash
cd backend
.\myenv\Scripts\Activate.ps1
pytest
```

Additional verification/diagnostic scripts live in `backend/tests/`.

---

## 🗺️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Next.js Dashboard                     │
│          (Search · Filters · Live Progress · Export)     │
└─────────────────────┬───────────────────────────────────┘
                      │  HTTP / REST
┌─────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                        │
│   ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│   │   Scraper   │  │   Analyzer   │  │   Exporter   │   │
│   │  (Playwright│  │  (DNS, SSL,  │  │  (CSV/Excel) │   │
│   │   DOM parse)│  │  HTTP, CMS..)│  │              │   │
│   └──────┬──────┘  └──────┬───────┘  └──────────────┘   │
│          │                │                              │
│   ┌──────▼────────────────▼────────────────────────┐    │
│   │              SQLite Database                    │    │
│   │         (portfolios + analysis results)         │    │
│   └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
          │
          ▼
   https://www.optiinfo.com/our-works/
   (Scraped via headless Chromium)
```

---

## ⚠️ Important Notes

- `backend/.env`, `frontend/.env.local`, SQLite databases (`*.db`), local virtual environments (`myenv/`), and `node_modules/` are **git-ignored** — never commit secrets.
- The scraper targets `https://www.optiinfo.com/our-works/` (configurable via `TARGET_URL` in backend settings).
- The analyzer performs **direct HTTP/DNS inspection** — no proxy or third-party fingerprinting services.

---

## 📄 License

This project is proprietary. All rights reserved.

---

<div align="center">

**Built with ❤️ by Ritesh Gajjar**

</div>