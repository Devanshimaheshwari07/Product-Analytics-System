"""
Callbacks — Dash interactive callbacks for all dashboard charts and filters.
Fetches data from the FastAPI REST API and renders Plotly charts.
"""
import os
import requests
import plotly.graph_objects as go
import plotly.express as px
from dash import Input, Output, callback, html
from layouts.kpi_cards import create_kpi_card, format_currency, format_number

API_BASE = os.getenv("API_BASE_URL", "http://api:8000")

# ─── Color Palette ────────────────────────────────────────────
COLORS = {
    "blue": "#3b82f6",
    "purple": "#8b5cf6",
    "cyan": "#06b6d4",
    "green": "#10b981",
    "orange": "#f59e0b",
    "pink": "#ec4899",
    "red": "#ef4444",
    "indigo": "#6366f1",
}

CATEGORY_COLORS = [
    "#3b82f6", "#8b5cf6", "#06b6d4", "#10b981",
    "#f59e0b", "#ec4899", "#ef4444", "#6366f1",
]

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", color="#94a3b8", size=12),
    margin=dict(l=40, r=20, t=10, b=40),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", zerolinecolor="rgba(255,255,255,0.06)"),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8", size=11),
    ),
    hoverlabel=dict(
        bgcolor="#1e293b",
        font_size=13,
        font_family="Inter, system-ui, sans-serif",
        bordercolor="rgba(255,255,255,0.1)",
    ),
)


def api_get(endpoint):
    """Fetch data from the API with error handling."""
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"API error ({endpoint}): {e}")
        return None


# ═══════════════════════════════════════════════════════════════
# OVERVIEW PAGE CALLBACKS
# ═══════════════════════════════════════════════════════════════

@callback(
    Output("overview-kpi-cards", "children"),
    Input("overview-refresh-interval", "n_intervals"),
)
def update_overview_kpis(_):
    data = api_get("/api/v1/analytics/overview")
    if not data:
        return [html.Div("Loading...", style={"color": "#94a3b8"})]

    return [
        create_kpi_card("Total Revenue", format_currency(data["total_revenue"]), color="blue", icon="💰"),
        create_kpi_card("Total Orders", format_number(data["total_orders"]), color="green", icon="📦"),
        create_kpi_card("Units Sold", format_number(data["total_units_sold"]), color="purple", icon="🏷️"),
        create_kpi_card("Avg Order Value", f"${data['avg_order_value']:,.2f}", color="orange", icon="💵"),
        create_kpi_card("Gross Profit", format_currency(data["gross_profit"]), color="green", icon="📈"),
        create_kpi_card("Profit Margin", f"{data['avg_profit_margin']:.1f}%", color="purple", icon="🎯"),
    ]


@callback(
    Output("revenue-trend-chart", "figure"),
    Input("overview-refresh-interval", "n_intervals"),
)
def update_revenue_trend(_):
    data = api_get("/api/v1/analytics/revenue-trends?period=monthly")
    fig = go.Figure()

    if data:
        periods = [d["period"][:10] for d in data]
        revenues = [float(d["revenue"]) for d in data]
        profits = [float(d["gross_profit"]) for d in data]

        fig.add_trace(go.Scatter(
            x=periods, y=revenues, name="Revenue",
            line=dict(color=COLORS["blue"], width=3),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.1)",
            mode="lines+markers",
            marker=dict(size=6),
        ))
        fig.add_trace(go.Scatter(
            x=periods, y=profits, name="Gross Profit",
            line=dict(color=COLORS["green"], width=2, dash="dot"),
            mode="lines+markers",
            marker=dict(size=5),
        ))

    fig.update_layout(**CHART_LAYOUT)
    return fig


@callback(
    Output("category-revenue-chart", "figure"),
    Input("overview-refresh-interval", "n_intervals"),
)
def update_category_revenue(_):
    data = api_get("/api/v1/analytics/category-performance")
    fig = go.Figure()

    if data:
        categories = [d["category"] for d in data]
        revenues = [float(d["total_revenue"]) for d in data]

        fig.add_trace(go.Bar(
            x=revenues, y=categories, orientation="h",
            marker=dict(
                color=CATEGORY_COLORS[:len(categories)],
                cornerradius=6,
            ),
            text=[format_currency(r) for r in revenues],
            textposition="auto",
            textfont=dict(color="#f1f5f9", size=11),
        ))

    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig


@callback(
    Output("top-products-chart", "figure"),
    Input("overview-refresh-interval", "n_intervals"),
)
def update_top_products(_):
    data = api_get("/api/v1/analytics/top-products?limit=10&sort_by=revenue")
    fig = go.Figure()

    if data:
        names = [d["product_name"][:30] for d in data]
        revenues = [float(d["lifetime_revenue"]) for d in data]

        fig.add_trace(go.Bar(
            x=revenues, y=names, orientation="h",
            marker=dict(
                color=[f"rgba(59,130,246,{0.4 + 0.06*i})" for i in range(len(names))],
                cornerradius=6,
            ),
            text=[format_currency(r) for r in revenues],
            textposition="auto",
            textfont=dict(color="#f1f5f9", size=11),
        ))

    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    return fig


@callback(
    Output("regional-performance-chart", "figure"),
    Input("overview-refresh-interval", "n_intervals"),
)
def update_regional_performance(_):
    data = api_get("/api/v1/analytics/regional-performance")
    fig = go.Figure()

    if data:
        regions = [d["region_name"] for d in data]
        revenues = [float(d["total_revenue"]) for d in data]
        profits = [float(d["gross_profit"]) for d in data]

        fig.add_trace(go.Bar(
            x=regions, y=revenues, name="Revenue",
            marker=dict(color=COLORS["blue"], cornerradius=6),
        ))
        fig.add_trace(go.Bar(
            x=regions, y=profits, name="Profit",
            marker=dict(color=COLORS["green"], cornerradius=6),
        ))

    fig.update_layout(**CHART_LAYOUT, barmode="group")
    return fig


@callback(
    Output("profit-margin-chart", "figure"),
    Input("overview-refresh-interval", "n_intervals"),
)
def update_profit_margin(_):
    data = api_get("/api/v1/analytics/category-performance")
    fig = go.Figure()

    if data:
        categories = [d["category"] for d in data]
        revenues = [float(d["total_revenue"]) for d in data]
        profits = [float(d["gross_profit"]) for d in data]
        margins = [
            round(p / r * 100, 1) if r > 0 else 0
            for r, p in zip(revenues, profits)
        ]

        fig.add_trace(go.Bar(
            x=categories, y=margins,
            marker=dict(
                color=[COLORS["green"] if m > 50 else COLORS["orange"] if m > 30 else COLORS["red"] for m in margins],
                cornerradius=6,
            ),
            text=[f"{m:.1f}%" for m in margins],
            textposition="auto",
            textfont=dict(color="#f1f5f9", size=11),
        ))

    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(yaxis=dict(title="Profit Margin %"))
    return fig


@callback(
    Output("orders-trend-chart", "figure"),
    Input("overview-refresh-interval", "n_intervals"),
)
def update_orders_trend(_):
    data = api_get("/api/v1/analytics/revenue-trends?period=monthly")
    fig = go.Figure()

    if data:
        periods = [d["period"][:10] for d in data]
        orders = [d["orders"] for d in data]
        units = [d["units_sold"] for d in data]

        fig.add_trace(go.Bar(
            x=periods, y=orders, name="Orders",
            marker=dict(color=COLORS["purple"], cornerradius=6),
        ))
        fig.add_trace(go.Scatter(
            x=periods, y=units, name="Units Sold",
            line=dict(color=COLORS["cyan"], width=2),
            mode="lines+markers",
            yaxis="y2",
        ))

    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(
        yaxis2=dict(
            overlaying="y", side="right",
            gridcolor="rgba(255,255,255,0.04)",
            font=dict(color="#06b6d4"),
        ),
    )
    return fig


# ═══════════════════════════════════════════════════════════════
# PRODUCT DETAIL PAGE CALLBACKS
# ═══════════════════════════════════════════════════════════════

@callback(
    Output("filter-category", "options"),
    Input("filter-category", "id"),
)
def load_categories(_):
    data = api_get("/api/v1/analytics/category-performance")
    if data:
        return [{"label": d["category"], "value": d["category"]} for d in data]
    return []


@callback(
    Output("filter-product", "options"),
    Input("filter-category", "value"),
)
def load_products(category):
    endpoint = "/api/v1/products?limit=200"
    if category:
        endpoint += f"&category={category}"
    data = api_get(endpoint)
    if data and "items" in data:
        return [{"label": p["name"], "value": p["id"]} for p in data["items"]]
    return []


@callback(
    Output("product-kpi-cards", "children"),
    [Input("filter-category", "value"), Input("filter-product", "value")],
)
def update_product_kpis(category, product_id):
    if product_id:
        data = api_get(f"/api/v1/analytics/top-products?limit=50&sort_by=revenue")
        if data:
            product = next((p for p in data if p["product_id"] == product_id), None)
            if product:
                return [
                    create_kpi_card("Revenue", format_currency(float(product["lifetime_revenue"])), color="blue", icon="💰"),
                    create_kpi_card("Units Sold", format_number(product["lifetime_units"]), color="green", icon="📦"),
                    create_kpi_card("Orders", format_number(product["lifetime_orders"]), color="purple", icon="🛒"),
                    create_kpi_card("Profit Margin", f"{float(product['avg_profit_margin']):.1f}%", color="orange", icon="🎯"),
                ]

    data = api_get("/api/v1/analytics/overview")
    if data:
        return [
            create_kpi_card("Total Revenue", format_currency(data["total_revenue"]), color="blue", icon="💰"),
            create_kpi_card("Products", str(data["total_products"]), color="green", icon="📦"),
            create_kpi_card("Avg Order Value", f"${data['avg_order_value']:,.2f}", color="purple", icon="💵"),
            create_kpi_card("Profit Margin", f"{data['avg_profit_margin']:.1f}%", color="orange", icon="🎯"),
        ]
    return []


@callback(
    Output("product-sales-timeline", "figure"),
    [Input("filter-product", "value"), Input("filter-period", "value")],
)
def update_sales_timeline(product_id, period):
    endpoint = f"/api/v1/sales/aggregate?group_by={period}"
    if product_id:
        endpoint += f"&product_id={product_id}"
    data = api_get(endpoint)
    fig = go.Figure()

    if data:
        periods = [d["period"][:10] for d in data]
        revenues = [float(d["total_revenue"]) for d in data]
        orders = [d["total_orders"] for d in data]

        fig.add_trace(go.Scatter(
            x=periods, y=revenues, name="Revenue",
            line=dict(color=COLORS["blue"], width=3),
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.1)",
            mode="lines+markers",
            marker=dict(size=5),
        ))

    fig.update_layout(**CHART_LAYOUT)
    return fig


@callback(
    Output("product-revenue-profit", "figure"),
    [Input("filter-sort", "value")],
)
def update_revenue_profit(sort_by):
    data = api_get(f"/api/v1/analytics/top-products?limit=15&sort_by={sort_by}")
    fig = go.Figure()

    if data:
        names = [d["product_name"][:20] for d in data]
        revenues = [float(d["lifetime_revenue"]) for d in data]
        profits = [float(d["lifetime_profit"]) for d in data]

        fig.add_trace(go.Bar(
            x=names, y=revenues, name="Revenue",
            marker=dict(color=COLORS["blue"], cornerradius=6),
        ))
        fig.add_trace(go.Bar(
            x=names, y=profits, name="Profit",
            marker=dict(color=COLORS["green"], cornerradius=6),
        ))

    fig.update_layout(**CHART_LAYOUT, barmode="group")
    fig.update_layout(xaxis=dict(tickangle=-45))
    return fig


@callback(
    Output("product-comparison-chart", "figure"),
    [Input("filter-sort", "value"), Input("filter-category", "value")],
)
def update_product_comparison(sort_by, category):
    data = api_get(f"/api/v1/analytics/top-products?limit=20&sort_by={sort_by}")
    fig = go.Figure()

    if data:
        if category:
            data = [d for d in data if d["category"] == category]

        names = [d["product_name"][:25] for d in data]
        revenues = [float(d["lifetime_revenue"]) for d in data]
        units = [d["lifetime_units"] for d in data]
        margins = [float(d["avg_profit_margin"]) for d in data]

        fig.add_trace(go.Scatter(
            x=revenues, y=margins,
            mode="markers+text",
            marker=dict(
                size=[max(10, u / max(units) * 50) if max(units) > 0 else 10 for u in units],
                color=revenues,
                colorscale="Viridis",
                showscale=True,
                colorbar=dict(title="Revenue"),
            ),
            text=names,
            textposition="top center",
            textfont=dict(size=9, color="#94a3b8"),
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Revenue: $%{x:,.0f}<br>"
                "Margin: %{y:.1f}%<br>"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(
        xaxis=dict(title="Lifetime Revenue ($)"),
        yaxis=dict(title="Profit Margin (%)"),
    )
    return fig


@callback(
    Output("channel-analysis-chart", "figure"),
    Input("filter-product", "value"),
)
def update_channel_analysis(product_id):
    endpoint = "/api/v1/sales?limit=500"
    if product_id:
        endpoint += f"&product_id={product_id}"
    data = api_get(endpoint)
    fig = go.Figure()

    if data and "items" in data:
        import pandas as pd
        df = pd.DataFrame(data["items"])
        if not df.empty and "channel" in df.columns:
            channel_rev = df.groupby("channel")["total_amount"].sum().reset_index()
            channel_rev.columns = ["channel", "revenue"]
            channel_rev = channel_rev.sort_values("revenue", ascending=False)

            fig.add_trace(go.Pie(
                labels=channel_rev["channel"],
                values=channel_rev["revenue"],
                hole=0.55,
                marker=dict(colors=CATEGORY_COLORS),
                textinfo="label+percent",
                textfont=dict(color="#f1f5f9", size=12),
                hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
            ))

    fig.update_layout(**CHART_LAYOUT)
    return fig


@callback(
    Output("discount-impact-chart", "figure"),
    Input("filter-product", "value"),
)
def update_discount_impact(product_id):
    endpoint = "/api/v1/sales?limit=500"
    if product_id:
        endpoint += f"&product_id={product_id}"
    data = api_get(endpoint)
    fig = go.Figure()

    if data and "items" in data:
        import pandas as pd
        df = pd.DataFrame(data["items"])
        if not df.empty:
            df["discount_pct"] = df["discount_pct"].astype(float)
            df["total_amount"] = df["total_amount"].astype(float)

            # Bin discounts
            bins = [0, 1, 5, 10, 15, 20, 100]
            labels = ["0%", "1-5%", "5-10%", "10-15%", "15-20%", "20%+"]
            df["discount_bin"] = pd.cut(df["discount_pct"], bins=bins, labels=labels, right=True)

            agg = df.groupby("discount_bin", observed=True).agg(
                avg_amount=("total_amount", "mean"),
                count=("id", "count"),
            ).reset_index()

            fig.add_trace(go.Bar(
                x=agg["discount_bin"].astype(str),
                y=agg["avg_amount"],
                name="Avg Order Value",
                marker=dict(color=COLORS["purple"], cornerradius=6),
                text=[f"${v:,.0f}" for v in agg["avg_amount"]],
                textposition="auto",
                textfont=dict(color="#f1f5f9", size=11),
            ))
            fig.add_trace(go.Scatter(
                x=agg["discount_bin"].astype(str),
                y=agg["count"],
                name="Order Count",
                line=dict(color=COLORS["orange"], width=2),
                mode="lines+markers",
                yaxis="y2",
            ))

    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(
        xaxis=dict(title="Discount Range"),
        yaxis=dict(title="Avg Order Value ($)"),
        yaxis2=dict(
            overlaying="y", side="right", title="Order Count",
            gridcolor="rgba(255,255,255,0.04)",
        ),
    )
    return fig
