"""
Overview Layout — Executive dashboard with KPI cards, revenue trends,
top products, and regional performance.
"""
from dash import html, dcc


def create_overview_layout():
    """Create the executive overview dashboard layout."""
    return html.Div(
        className="page-container",
        children=[
            # Page Header
            html.Div(
                className="page-header",
                children=[
                    html.H2("Executive Overview"),
                    html.P("Real-time product performance metrics and business intelligence"),
                ],
            ),

            # KPI Cards Row
            html.Div(id="overview-kpi-cards", className="kpi-grid"),

            # Revenue Trend + Category Breakdown
            html.Div(
                className="chart-grid",
                children=[
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H3("📈 Revenue Trend"),
                            dcc.Graph(
                                id="revenue-trend-chart",
                                config={"displayModeBar": False},
                                style={"height": "340px"},
                            ),
                        ],
                    ),
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H3("🏷️ Revenue by Category"),
                            dcc.Graph(
                                id="category-revenue-chart",
                                config={"displayModeBar": False},
                                style={"height": "340px"},
                            ),
                        ],
                    ),
                ],
            ),

            # Top Products + Regional Performance
            html.Div(
                className="chart-grid",
                children=[
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H3("🏆 Top 10 Products by Revenue"),
                            dcc.Graph(
                                id="top-products-chart",
                                config={"displayModeBar": False},
                                style={"height": "380px"},
                            ),
                        ],
                    ),
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H3("🌍 Regional Performance"),
                            dcc.Graph(
                                id="regional-performance-chart",
                                config={"displayModeBar": False},
                                style={"height": "380px"},
                            ),
                        ],
                    ),
                ],
            ),

            # Profit Margin + Orders Trend
            html.Div(
                className="chart-grid",
                children=[
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H3("💰 Profit Margin by Category"),
                            dcc.Graph(
                                id="profit-margin-chart",
                                config={"displayModeBar": False},
                                style={"height": "340px"},
                            ),
                        ],
                    ),
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H3("📦 Monthly Orders & Units Sold"),
                            dcc.Graph(
                                id="orders-trend-chart",
                                config={"displayModeBar": False},
                                style={"height": "340px"},
                            ),
                        ],
                    ),
                ],
            ),

            # Auto-refresh interval (every 60 seconds)
            dcc.Interval(
                id="overview-refresh-interval",
                interval=60 * 1000,
                n_intervals=0,
            ),
        ],
    )
