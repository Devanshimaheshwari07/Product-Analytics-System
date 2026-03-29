"""
KPI Cards — Reusable KPI card components with trend indicators.
"""
from dash import html


def create_kpi_card(label, value, change=None, color="blue", icon="📊"):
    """
    Create a KPI card component.

    Args:
        label: KPI name/label
        value: Formatted KPI value string
        change: Percentage change (positive or negative float)
        color: Card accent color (blue, green, purple, orange)
        icon: Emoji icon for the card
    """
    change_element = None
    if change is not None:
        is_positive = change >= 0
        arrow = "↑" if is_positive else "↓"
        change_class = "kpi-change positive" if is_positive else "kpi-change negative"
        change_element = html.Div(
            f"{arrow} {abs(change):.1f}%",
            className=change_class,
        )

    return html.Div(
        className=f"kpi-card {color}",
        children=[
            html.Div(label, className="kpi-label"),
            html.Div(
                children=[
                    html.Span(icon, style={"marginRight": "8px", "fontSize": "1.2rem"}),
                    html.Span(value),
                ],
                className="kpi-value",
            ),
            change_element,
        ],
    )


def format_currency(value):
    """Format a number as USD currency."""
    if value >= 1_000_000:
        return f"${value / 1_000_000:,.1f}M"
    elif value >= 1_000:
        return f"${value / 1_000:,.1f}K"
    else:
        return f"${value:,.2f}"


def format_number(value):
    """Format a large number with K/M suffix."""
    if value >= 1_000_000:
        return f"{value / 1_000_000:,.1f}M"
    elif value >= 1_000:
        return f"{value / 1_000:,.1f}K"
    else:
        return f"{value:,.0f}"
