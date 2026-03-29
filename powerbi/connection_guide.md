# Power BI Connection Guide

This guide explains how to connect **Power BI Desktop** to the Product Analytics backend for interactive reporting and dashboard creation.

---

## Prerequisites

- [Power BI Desktop](https://powerbi.microsoft.com/desktop/) installed
- Docker services running (`docker-compose up -d`)
- API accessible at `http://localhost:8000`
- PostgreSQL accessible at `localhost:5432`

---

## Option 1: Connect via PostgreSQL (Recommended)

Direct database connection provides the best performance for large datasets.

### Steps

1. Open **Power BI Desktop**
2. Click **Get Data** → **Database** → **PostgreSQL database**
3. Enter connection details:
   - **Server**: `localhost`
   - **Database**: `product_analytics`
   - **Username**: `analytics_user`
   - **Password**: `analytics_pass_2026`
4. Click **OK** and select **DirectQuery** or **Import** mode

### Recommended Tables to Import

| Table | Purpose |
|-------|---------|
| `products` | Product master data (SKU, name, price, cost) |
| `categories` | Product category reference |
| `regions` | Regional reference data |
| `sales_transactions` | Raw transactional data |
| `daily_product_metrics` | Pre-aggregated daily metrics |
| `kpi_summary` | Pre-computed KPIs by period |

### Recommended Views

| View | Purpose |
|------|---------|
| `v_product_performance` | Lifetime product performance summary |
| `v_regional_performance` | Regional revenue and profit summary |
| `v_monthly_trends` | Month-over-month trend analysis |

---

## Option 2: Connect via REST API (Web Data Source)

Use this when direct database access is restricted.

### Steps

1. Click **Get Data** → **Web**
2. Enter the API URL:
   ```
   http://localhost:8000/api/v1/analytics/top-products?limit=50
   ```
3. Power BI will detect JSON format — click **Transform Data**
4. Expand the JSON records into a table

### Available API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/v1/products` | All products with category info |
| `/api/v1/sales/aggregate?group_by=monthly` | Monthly sales aggregation |
| `/api/v1/analytics/overview` | Executive KPI summary |
| `/api/v1/analytics/revenue-trends?period=monthly` | Revenue trend data |
| `/api/v1/analytics/top-products?limit=20` | Top performing products |
| `/api/v1/analytics/category-performance` | Category breakdown |
| `/api/v1/analytics/regional-performance` | Regional breakdown |
| `/api/v1/analytics/kpis` | Pre-computed KPI summary |

---

## Data Model in Power BI

### Recommended Relationships

```
categories (1) ──→ (M) products
products   (1) ──→ (M) sales_transactions
regions    (1) ──→ (M) sales_transactions
products   (1) ──→ (M) daily_product_metrics
regions    (1) ──→ (M) daily_product_metrics
```

### Star Schema Design

- **Fact Table**: `sales_transactions` or `daily_product_metrics`
- **Dimension Tables**: `products`, `categories`, `regions`
- **Summary Table**: `kpi_summary`

---

## Suggested Reports

### 1. Executive Overview
- KPI cards: Total Revenue, Orders, Units, Profit Margin
- Revenue trend line chart (monthly)
- Top 10 products bar chart
- Regional performance map

### 2. Product Deep Dive
- Product performance matrix
- Category comparison
- Price vs. volume scatter plot
- Discount impact analysis

### 3. Regional Analysis
- Revenue by region
- Growth comparison across regions
- Channel mix by region

---

## Scheduled Refresh

### Power BI Service (Online)

1. Publish report to Power BI Service
2. Go to **Dataset Settings** → **Scheduled Refresh**
3. Configure the **On-premises data gateway** pointing to `localhost:5432`
4. Set refresh schedule (recommended: every 1 hour)

### Using Power BI REST API

```powershell
# Trigger dataset refresh via Power BI REST API
Invoke-RestMethod -Method POST `
  -Uri "https://api.powerbi.com/v1.0/myorg/datasets/{datasetId}/refreshes" `
  -Headers @{ Authorization = "Bearer $token" }
```

---

## Tips

- Use **DirectQuery** for real-time data; **Import** for faster report interactions
- Create a **Date table** in Power BI for time intelligence functions
- Use the `daily_product_metrics` table for most visualizations (pre-aggregated = faster)
- Reference the [DAX Measures](measures.md) document for ready-to-use calculations
