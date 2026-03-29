# Power BI DAX Measures Reference

Pre-built DAX measures for the Product Analytics data model.
Copy and paste these into your Power BI Desktop report.

---

## Revenue Measures

```dax
// Total Revenue
Total Revenue =
SUM(daily_product_metrics[total_revenue])

// Revenue MTD (Month-to-Date)
Revenue MTD =
TOTALMTD(SUM(daily_product_metrics[total_revenue]), 'Date'[Date])

// Revenue YTD (Year-to-Date)
Revenue YTD =
TOTALYTD(SUM(daily_product_metrics[total_revenue]), 'Date'[Date])

// Revenue Previous Month
Revenue Prev Month =
CALCULATE(
    SUM(daily_product_metrics[total_revenue]),
    DATEADD('Date'[Date], -1, MONTH)
)

// Revenue MoM Growth %
Revenue MoM Growth =
VAR CurrentMonth = [Total Revenue]
VAR PrevMonth = [Revenue Prev Month]
RETURN
IF(PrevMonth <> 0,
    DIVIDE(CurrentMonth - PrevMonth, PrevMonth) * 100,
    BLANK()
)
```

## Profitability Measures

```dax
// Gross Profit
Gross Profit =
SUM(daily_product_metrics[gross_profit])

// Overall Profit Margin %
Profit Margin % =
DIVIDE([Gross Profit], [Total Revenue]) * 100

// Average Profit Margin
Avg Profit Margin =
AVERAGE(daily_product_metrics[profit_margin])
```

## Order Measures

```dax
// Total Orders
Total Orders =
SUM(daily_product_metrics[total_orders])

// Total Units Sold
Total Units Sold =
SUM(daily_product_metrics[total_units_sold])

// Average Order Value
Avg Order Value =
DIVIDE([Total Revenue], [Total Orders])

// Average Units Per Order
Avg Units Per Order =
DIVIDE([Total Units Sold], [Total Orders])
```

## Product Measures

```dax
// Product Count
Product Count =
DISTINCTCOUNT(products[id])

// Revenue Rank by Product
Product Revenue Rank =
RANKX(
    ALL(products[name]),
    [Total Revenue],
    , DESC, DENSE
)

// Top N Products Revenue
Top 10 Products Revenue =
CALCULATE(
    [Total Revenue],
    TOPN(10, ALL(products[name]), [Total Revenue], DESC)
)

// Product Revenue Share %
Product Revenue Share =
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], ALL(products))
) * 100
```

## Category Measures

```dax
// Category Revenue
Category Revenue =
CALCULATE(
    SUM(daily_product_metrics[total_revenue]),
    ALLEXCEPT(categories, categories[name])
)

// Category Revenue Share %
Category Share % =
DIVIDE(
    [Total Revenue],
    CALCULATE([Total Revenue], ALL(categories))
) * 100
```

## Time Intelligence

```dax
// Rolling 7-Day Average Revenue
Revenue 7D Avg =
AVERAGEX(
    DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -7, DAY),
    [Total Revenue]
)

// Rolling 30-Day Average Revenue
Revenue 30D Avg =
AVERAGEX(
    DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -30, DAY),
    [Total Revenue]
)

// Same Period Last Year
Revenue SPLY =
CALCULATE(
    [Total Revenue],
    SAMEPERIODLASTYEAR('Date'[Date])
)

// YoY Growth %
YoY Growth % =
VAR Current = [Total Revenue]
VAR LastYear = [Revenue SPLY]
RETURN
IF(LastYear <> 0,
    DIVIDE(Current - LastYear, LastYear) * 100,
    BLANK()
)
```

## Discount Measures

```dax
// Average Discount %
Avg Discount % =
AVERAGE(daily_product_metrics[avg_discount_pct])

// Revenue Impact of Discounts
Discount Revenue Impact =
SUMX(
    sales_transactions,
    sales_transactions[unit_price] * sales_transactions[quantity]
    * sales_transactions[discount_pct] / 100
)
```

---

## Date Table (Create in Power BI)

```dax
Date =
ADDCOLUMNS(
    CALENDAR(DATE(2025, 1, 1), DATE(2026, 12, 31)),
    "Year", YEAR([Date]),
    "Month", MONTH([Date]),
    "MonthName", FORMAT([Date], "MMMM"),
    "Quarter", "Q" & FORMAT([Date], "Q"),
    "WeekNum", WEEKNUM([Date]),
    "DayOfWeek", WEEKDAY([Date]),
    "DayName", FORMAT([Date], "dddd"),
    "YearMonth", FORMAT([Date], "YYYY-MM"),
    "IsWeekend", IF(WEEKDAY([Date]) IN {1, 7}, TRUE, FALSE)
)
```
