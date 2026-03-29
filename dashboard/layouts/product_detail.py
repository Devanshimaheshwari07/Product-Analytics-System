"""
Product Detail Layout — Drill-down analysis for individual products
with sales timeline, price analysis, and comparisons.
"""
from dash import html, dcc


def create_product_detail_layout():
    """Create the product drill-down analysis layout."""
    return html.Div(
        className="page-container",
        children=[
            # Page Header
            html.Div(
                className="page-header",
                children=[
                    html.H2("Product Analysis"),
                    html.P("Deep-dive analytics by product, category, and time period"),
                ],
            ),

            # Filters Bar
            html.Div(
                className="filters-bar",
                children=[
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Category"),
                            dcc.Dropdown(
                                id="filter-category",
                                placeholder="All Categories",
                                clearable=True,
                                style={"width": "200px"},
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Product"),
                            dcc.Dropdown(
                                id="filter-product",
                                placeholder="All Products",
                                clearable=True,
                                style={"width": "250px"},
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Time Period"),
                            dcc.Dropdown(
                                id="filter-period",
                                options=[
                                    {"label": "Daily", "value": "daily"},
                                    {"label": "Weekly", "value": "weekly"},
                                    {"label": "Monthly", "value": "monthly"},
                                ],
                                value="monthly",
                                clearable=False,
                                style={"width": "140px"},
                            ),
                        ],
                    ),
                    html.Div(
                        className="filter-group",
                        children=[
                            html.Label("Sort By"),
                            dcc.Dropdown(
                                id="filter-sort",
                                options=[
                                    {"label": "Revenue", "value": "revenue"},
                                    {"label": "Units Sold", "value": "units"},
                                    {"label": "Profit", "value": "profit"},
                                    {"label": "Margin", "value": "margin"},
                                ],
                                value="revenue",
                                clearable=False,
                                style={"width": "140px"},
                            ),
                        ],
                    ),
                ],
            ),

            # Product KPIs
            html.Div(id="product-kpi-cards", className="kpi-grid"),

            # Sales Timeline + Revenue Breakdown
            html.Div(
                className="chart-grid",
                children=[
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H3("📈 Sales Timeline"),
                            dcc.Graph(
                                id="product-sales-timeline",
                                config={"displayModeBar": False},
                                style={"height": "360px"},
                            ),
                        ],
                    ),
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H3("📊 Revenue vs Profit"),
                            dcc.Graph(
                                id="product-revenue-profit",
                                config={"displayModeBar": False},
                                style={"height": "360px"},
                            ),
                        ],
                    ),
                ],
            ),

            # Product Comparison Table
            html.Div(
                className="chart-grid full",
                children=[
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H3("📋 Product Performance Ranking"),
                            dcc.Graph(
                                id="product-comparison-chart",
                                config={"displayModeBar": False},
                                style={"height": "420px"},
                            ),
                        ],
                    ),
                ],
            ),

            # Channel Analysis + Discount Impact
            html.Div(
                className="chart-grid",
                children=[
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H3("🛒 Sales by Channel"),
                            dcc.Graph(
                                id="channel-analysis-chart",
                                config={"displayModeBar": False},
                                style={"height": "340px"},
                            ),
                        ],
                    ),
                    html.Div(
                        className="chart-card",
                        children=[
                            html.H3("💹 Discount Impact Analysis"),
                            dcc.Graph(
                                id="discount-impact-chart",
                                config={"displayModeBar": False},
                                style={"height": "340px"},
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
