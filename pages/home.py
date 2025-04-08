import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Register this file as the home page
dash.register_page(__name__, path="/", name="Home")

# Define colors for consistency
COLORS = {
    'primary': '#2C3E50',
    'accent': '#3498DB',
    'white': '#FFFFFF',
    'light': '#F8F9FA',
    'dark': '#212529'
}

# Layout for the Home page
layout = html.Div([

    # Dashboard Header
    html.Div([
        html.Div([
            html.Img(src="/assets/Logo_slogan.PNG", className="dashboard-logo"),
        ], className="dashboard-title"),
    ], className="dashboard-header"),


    # Navigation Bar
    html.Nav([
        html.Button([
            html.Span("BlueCard Finance", className="mobile-nav-toggle-text"),
            html.Span("≡")
        ], className="mobile-nav-toggle", id="mobile-nav-toggle"),

        html.Ul([
            html.Li(html.A([html.Span("🏠", className="nav-icon"), "Home"], href="/", className="nav-link active"), className="nav-item"),
            html.Li(html.A([html.Span("📊", className="nav-icon"), "Dashboard"], href="/dashboard", className="nav-link"), className="nav-item"),
            html.Li(html.A([html.Span("📈", className="nav-icon"), "Income"], href="/income", className="nav-link"), className="nav-item"),
            html.Li(html.A([html.Span("💰", className="nav-icon"), "Expenses"], href="/expenses", className="nav-link"), className="nav-item"),
            html.Li(html.A([html.Span("🎯", className="nav-icon"), "Savings Analysis"], href="/savings", className="nav-link"), className="nav-item"),
        ], className="nav-menu", id="nav-menu")
    ], className="nav-bar"),

    # Hero Section with Background Image and Light Blue Mask
    html.Div([
        html.Div([
            html.Div([
                html.H1("BlueCard Finance", className="hero-title"),
                html.P("Your trusted partner in financial management.", className="hero-subtitle"),
                dbc.Button("Get Started", href="/dashboard", color="primary", className="hero-button")
            ], className="hero-content"),
        ], className="hero-overlay"),
    ], className="hero-section", style={
        'backgroundImage': 'url("/assets/home_background.PNG")',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center',
        'height': '80vh',
        'position': 'relative',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'textAlign': 'center'
    }),

    # Features Section
    html.Div([
        html.H2("Why Choose BlueCard Finance?", className="section-title", style={'color': COLORS['primary']}),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div("📊", className="feature-icon"),
                    html.H4("Track Your Finances", className="feature-title"),
                    html.P("Monitor your income, expenses, and savings all in one place.", className="feature-description")
                ], className="feature-card")
            ], md=4),
            dbc.Col([
                html.Div([
                    html.Div("🎯", className="feature-icon"),
                    html.H4("Set Goals", className="feature-title"),
                    html.P("Define and achieve your financial goals with ease.", className="feature-description")
                ], className="feature-card")
            ], md=4),
            dbc.Col([
                html.Div([
                    html.Div("📈", className="feature-icon"),
                    html.H4("Gain Insights", className="feature-title"),
                    html.P("Get actionable insights to improve your financial health.", className="feature-description")
                ], className="feature-card")
            ], md=4),
        ], className="features-row")
    ], className="features-section", style={'padding': '40px 20px', 'backgroundColor': COLORS['light']}),

    # Footer
    html.Footer([
        html.Div("© 2025 BlueCard Finance. All rights reserved.", className="footer-text"),
        html.Div([
            html.A("Privacy Policy", href="#", className="footer-link"),
            html.Span(" | "),
            html.A("Terms of Service", href="#", className="footer-link")
        ], className="footer-links")
    ], className="dashboard-footer", style={
        "backgroundColor": COLORS['light'],
        "padding": "20px",
        "textAlign": "center",
        "fontSize": "14px",
        "color": COLORS['dark']
    }),
], style={"width": "100%", "margin": "0", "padding": "0"})