# Product Analytics — End-to-End Data Analysis Platform

Enterprise-grade analytics system for product performance monitoring, integrating backend data sources with interactive dashboards, automated ETL pipelines, and Docker-based deployment.

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791)
![Power BI](https://img.shields.io/badge/Power%20BI-Ready-F2C811)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  Docker Compose Orchestration                │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ PostgreSQL │──│  FastAPI   │──│   Plotly   │            │
│  │  Database  │  │  REST API  │  │   Dash     │            │
│  │  :5432     │  │  :8000     │  │  Dashboard │            │
│  └────────────┘  └────────────┘  │  :8050     │            │
│        │                │        └────────────┘            │
│        │         ┌──────┘                                   │
│  ┌─────┴──────┐  │                                         │
│  │    ETL     │──┘        ┌─────────────┐                  │
│  │  Pipeline  │           │  Power BI   │ (External)       │
│  │ APScheduler│           │  Desktop    │                  │
│  └────────────┘           └─────────────┘                  │
└──────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Database** | PostgreSQL 15 | Analytical data store |
| **REST API** | FastAPI + SQLAlchemy | Backend data access layer |
| **ETL Pipeline** | Python + Pandas + APScheduler | Data transformation & scheduling |
| **Web Dashboard** | Plotly Dash | Interactive visualizations |
| **BI Integration** | Power BI Desktop | Further Enterprise reporting |
| **Containerization** | Docker Compose | Service orchestration |
| **CI/CD** | GitHub Actions | Automated build & deploy |

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Git

### Launch

```bash
# Clone the repository
git clone <repository-url>
cd product-analytics

# Start all services
docker-compose up -d --build

# Wait ~60 seconds for database initialization and ETL first run
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | [http://localhost:8050](http://localhost:8050) | Interactive analytics dashboard |
| **API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Swagger UI for REST API |
| **API Health** | [http://localhost:8000/health](http://localhost:8000/health) | Health check endpoint |
| **Database** | `localhost:5432` | PostgreSQL (user: `analytics_user`) |

---

## Project Structure

```
product-analytics/
├── docker-compose.yml          # Service orchestration
├── .env                        # Environment configuration
├── database/
│   ├── Dockerfile
│   └── init.sql                # Schema + 12K+ seed transactions
├── api/
│   ├── Dockerfile
│   ├── main.py                 # FastAPI application
│   ├── database.py             # SQLAlchemy connection
│   ├── models.py               # ORM models
│   ├── schemas.py              # Pydantic schemas
│   └── routers/
│       ├── products.py         # Product CRUD endpoints
│       ├── sales.py            # Sales data & aggregation
│       └── analytics.py        # KPI & analytics endpoints
├── etl/
│   ├── Dockerfile
│   ├── pipeline.py             # ETL orchestrator
│   ├── extractors.py           # Data extraction
│   ├── transformers.py         # Cleaning & normalization
│   ├── loaders.py              # Database loading (upsert)
│   └── scheduler.py            # APScheduler cron jobs
├── dashboard/
│   ├── Dockerfile
│   ├── app.py                  # Dash application
│   ├── callbacks.py            # Interactive chart callbacks
│   ├── layouts/
│   │   ├── overview.py         # Executive overview page
│   │   ├── product_detail.py   # Product drill-down page
│   │   └── kpi_cards.py        # Reusable KPI components
│   └── assets/
│       └── styles.css          # Dark theme styling
├── powerbi/
│   ├── connection_guide.md     # Power BI setup instructions
│   └── measures.md             # DAX measures library
└── .github/workflows/
    └── ci-cd.yml               # GitHub Actions pipeline
```

---

## Features

### Data Layer
- **56 products** across 8 categories and 5 regions
- **~12,000 sales transactions** with realistic distribution
- Pre-computed daily metrics and monthly KPIs
- Analytical views for fast querying

### REST API (15+ Endpoints)
- Product listing with filtering (category, price, search)
- Sales aggregation (daily, weekly, monthly)
- Analytics: overview KPIs, revenue trends, top products
- Category and regional performance breakdowns
- Full Swagger/OpenAPI documentation

### ETL Pipeline
- **Hourly incremental** processing (last 2 days)
- **Daily full refresh** at midnight
- Data cleaning: deduplication, null handling, outlier removal
- Normalization: category/channel standardization
- KPI computation: revenue, growth %, margins, AOV

### Dashboard
- Premium dark theme with glassmorphism effects
- 6 KPI cards with trend indicators
- 10+ interactive charts (trends, bars, scatter, pie, heatmap)
- Product drill-down with category/product filters
- Channel analysis and discount impact views
- Auto-refresh every 60 seconds


## API Examples

```bash
# Health check
curl http://localhost:8000/health

# List products
curl "http://localhost:8000/api/v1/products?category=Electronics&limit=10"

# Monthly sales aggregation
curl "http://localhost:8000/api/v1/sales/aggregate?group_by=monthly"

# Executive KPI overview
curl http://localhost:8000/api/v1/analytics/overview

# Top 10 products by revenue
curl "http://localhost:8000/api/v1/analytics/top-products?limit=10&sort_by=revenue"

# Category performance
curl http://localhost:8000/api/v1/analytics/category-performance
```

---

## Docker Commands

```bash
# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# View ETL logs
docker-compose logs etl

# Stop all services
docker-compose down

# Stop and remove volumes (reset database)
docker-compose down -v
```

---

## Development

```bash
# Rebuild a specific service
docker-compose build api
docker-compose up -d api

# Run ETL manually
docker-compose exec etl python pipeline.py

# Access PostgreSQL CLI
docker-compose exec database psql -U analytics_user -d product_analytics
```

---

## License

This project is for educational and demonstration purposes.
