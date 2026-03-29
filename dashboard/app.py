"""
Product Analytics Dashboard — Main Dash Application
=====================================================
Multi-page interactive dashboard for product performance monitoring.
"""
import os
from dash import Dash, html, dcc, Input, Output, callback

from layouts.overview import create_overview_layout
from layouts.product_detail import create_product_detail_layout
import callbacks  # noqa: F401  — registers all callbacks

# ─── Initialize Dash App ─────────────────────────────────────
app = Dash(
    __name__,
    title="Product Analytics Dashboard",
    update_title="Loading...",
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
        {"name": "description", "content": "End-to-End Product Analytics Dashboard"},
    ],
)

server = app.server

# ─── App Layout ───────────────────────────────────────────────
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),

    # Navigation Bar
    html.Nav(
        className="navbar",
        children=[
            html.Div(
                className="nav-brand",
                children=[
                    html.Span("📊", className="logo-icon"),
                    html.H1("Product Analytics"),
                ],
            ),
            html.Div(
                className="nav-links",
                children=[
                    dcc.Link("Overview", href="/", className="nav-link", id="nav-overview"),
                    dcc.Link("Products", href="/products", className="nav-link", id="nav-products"),
                ],
            ),
        ],
    ),

    # Page Content
    html.Div(id="page-content"),
])


# ─── Page Routing ─────────────────────────────────────────────
@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname == "/products":
        return create_product_detail_layout()
    return create_overview_layout()


@callback(
    [Output("nav-overview", "className"), Output("nav-products", "className")],
    Input("url", "pathname"),
)
def update_nav_active(pathname):
    if pathname == "/products":
        return "nav-link", "nav-link active"
    return "nav-link active", "nav-link"


# ─── Run Server ───────────────────────────────────────────────
if __name__ == "__main__":
    host = os.getenv("DASH_HOST", "0.0.0.0")
    port = int(os.getenv("DASH_PORT", "8050"))
    debug = os.getenv("DASH_DEBUG", "false").lower() == "true"

    print(f"🚀 Dashboard starting on http://{host}:{port}")
    app.run(host=host, port=port, debug=debug)
