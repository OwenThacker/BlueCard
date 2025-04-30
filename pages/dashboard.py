import dash
from dash import html, dcc, callback, Input, Output, State, register_page, clientside_callback
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import datetime
import calendar
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import json
import os
import random
from flask_login import current_user

# Register this file as the dashboard page
register_page(__name__, path='/dashboard', name='Dashboard')

COLORS = {
    'primary': '#2C3E50',
    'accent': '#3498DB', 
    'success': '#2ECC71',
    'white': '#FFFFFF',
    'light': '#F8F9FA',
    'warning': '#F39C12',
    'danger-light': '#e0796e',
    'danger': '#E74C3C',
    'gray': '#95A5A6',
    'dark': '#212529'
}

# Load session data
def get_session_data():
    """
    This function emulates the session state from Streamlit
    In a real implementation, you'd use Flask's session or another method
    """
    # Check if data file exists
    if os.path.exists('session_data.json'):
        with open('session_data.json', 'r') as f:
            return json.load(f)
    else:
        # Initialize with default values
        default_data = {
            'salary': 0.0,
            'before_tax': True,
            'consistent_salary': True,
            'expenses': [],
            'daily_expenses': [],
            'savings_goals': [],  # Remove 'savings_target' here
            'income_sources': []
        }
        with open('session_data.json', 'w') as f:
            json.dump(default_data, f)
        return default_data

# Change from 'layout()' function to 'layout' variable to work with Dash pages
layout = html.Div([

    # Session and Routing
    dcc.Store(id='session-data-store', storage_type='local'),
    dcc.Store(id='user-id', storage_type='local'),  # Make sure this is included
    dcc.Location(id='url', refresh=False),
    dcc.Store(id="dropdown-state", data=False),  # Default state is False (hidden)


    # Dashboard Header
    html.Div([
        
        html.Img(src="/assets/Logo_slogan.PNG", className="dashboard-logo"),

        # Navigation Bar
        html.Nav([
            html.Button([
                html.Span("BlueCard Finance", className="mobile-nav-toggle-text"),
                html.Span("≡")
            ], className="mobile-nav-toggle", id="mobile-nav-toggle"),

            # Navigation Menu
            html.Ul([

                html.Li([
                    html.A([
                        html.Span(className="nav-icon"),
                        "Home"
                    ], href="/", className="nav-link")
                ], className="nav-item"),

                html.Li([
                    html.A([
                        html.Span(className="nav-icon"),
                        "Dashboard"
                    ], href="/dashboard", className="nav-link active")
                ], className="nav-item"),
                
                html.Li([
                    html.A([
                        html.Span(className="nav-icon"),
                        "Income"
                    ], href="/income", className="nav-link")
                ], className="nav-item"),

                html.Li([
                    html.A([
                        html.Span(className="nav-icon"),
                        "Expenses"
                    ], href="/expenses", className="nav-link")
                ], className="nav-item"),

                html.Li([html.A([html.Span(className="nav-icon"), 
                                "Savings Analysis"], href="/savings",
                        className="nav-link")
                ], className="nav-item"),
                
                html.Li(html.A([html.Span(className="nav-icon"), "Settings"], href="/settings", className="nav-link"), className="nav-item")
                
            ], className="nav-menu", id="nav-menu"),
            # User account area (right side of navbar)
                html.Div([
                    # User profile dropdown
                    html.Div([
                        html.Button([
                            html.I(className="fas fa-user-circle", style={'fontSize': '24px'}),
                        ], id="user-dropdown-button", className="user-dropdown-button"),
                        
                        # Dropdown menu
                        html.Div([
                            html.Div(id="user-email-display", className="user-email"),
                            html.Hr(style={'margin': '8px 0'}),
                            html.A("Profile", href="/profile", className="dropdown-item"),
                            html.A("Logout", id="logout-link", href="/logout", className="dropdown-item")
                        ], id="user-dropdown-content", className="user-dropdown-content")
                    ], className="user-dropdown"),
                ], id="user-account-container", className="user-account-container"),
        ], className="nav-bar"),
    ], className="header-container"),

    # Optional Breadcrumb
    html.Ul([
        html.Li([
            html.A("Home", href="/", className="breadcrumb-link")
        ], className="breadcrumb-item"),
        html.Li("Dashboard", className="breadcrumb-item breadcrumb-current")
    ], className="breadcrumb"),
    
     # Main Content
    html.Div([
        # Welcome Banner for New Users - will be shown/hidden based on data
        html.Div([
            html.Div([
                html.Div([
                    html.Img(src="/assets/Logo_slogan.PNG", style={"height": "70px", "marginBottom": "15px"}),
                    html.H2("Welcome to Your Financial Dashboard", className="welcome-title", 
                            style={"color": COLORS['primary'], "marginBottom": "15px", "fontSize": "24px"}),
                    html.P("Let's set up your financial profile to get personalized insights and track your progress.", 
                           style={"color": "#5D6D7E", "fontSize": "16px", "marginBottom": "25px"}),
                    html.Div([
                        dbc.Button([
                            html.I(className="fas fa-arrow-right", style={"marginRight": "8px"}),
                            "Get Started"
                        ], href="/income", color="primary", className="get-started-btn", 
                           style={"backgroundColor": COLORS['accent'], "border": "none", "padding": "12px 25px"})
                    ], style={"textAlign": "center"})
                ], className="welcome-content", style={
                    "padding": "30px",
                    "textAlign": "center",
                    "maxWidth": "800px",
                    "margin": "0 auto"
                })
            ], className="welcome-banner", id="welcome-banner", style={
                "backgroundColor": "#F8F9FA",
                "borderRadius": "10px",
                "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
                "marginBottom": "30px",
                "border": f"1px solid {COLORS['light']}",
                "display": "none"  # Initially hidden, will show based on callback
            })
        ], id="new-user-welcome-container"),
        
        # Setup Steps Cards - for new users
        html.Div([
            html.H3("Complete Your Setup", className="section-title", 
                    style={'color': COLORS['primary'], 'borderBottom': f'2px solid {COLORS["accent"]}', 'paddingBottom': '10px'}),
            html.Div([
                # Income Setup Card
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div("1", className="step-number", style={
                                "backgroundColor": COLORS['accent'],
                                "color": "white",
                                "width": "30px",
                                "height": "30px",
                                "borderRadius": "50%",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "marginRight": "15px",
                                "fontWeight": "bold"
                            }),
                            html.H4("Add Your Income", style={"color": COLORS['primary'], "margin": "0"})
                        ], style={"display": "flex", "alignItems": "center", "marginBottom": "15px"}),
                        html.P("Set up your monthly income sources to calculate your budget and savings potential.", 
                               style={"color": "#5D6D7E", "marginBottom": "20px"}),
                        dbc.Button([
                            html.I(className="fas fa-plus", style={"marginRight": "8px"}),
                            "Add Income"
                        ], href="/income", color="primary", className="setup-btn", 
                           style={"backgroundColor": COLORS['accent'], "border": "none"})
                    ], className="setup-card-content", style={"padding": "20px"})
                ], className="setup-card", style={
                    "backgroundColor": "white",
                    "borderRadius": "8px",
                    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
                    "flex": "1",
                    "minWidth": "250px",
                    "marginRight": "20px",
                    "border": f"1px solid {COLORS['light']}"
                }),
                
                # Expenses Setup Card
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div("2", className="step-number", style={
                                "backgroundColor": COLORS['warning'],
                                "color": "white",
                                "width": "30px",
                                "height": "30px",
                                "borderRadius": "50%",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "marginRight": "15px",
                                "fontWeight": "bold"
                            }),
                            html.H4("Track Your Expenses", style={"color": COLORS['primary'], "margin": "0"})
                        ], style={"display": "flex", "alignItems": "center", "marginBottom": "15px"}),
                        html.P("Add your recurring monthly expenses and daily transactions to see where your money goes.", 
                               style={"color": "#5D6D7E", "marginBottom": "20px"}),
                        dbc.Button([
                            html.I(className="fas fa-list-ul", style={"marginRight": "8px"}),
                            "Add Expenses"
                        ], href="/expenses", color="warning", className="setup-btn", 
                           style={"backgroundColor": COLORS['warning'], "border": "none"}),
                    ], className="setup-card-content", style={"padding": "20px"})
                ], className="setup-card", style={
                    "backgroundColor": "white",
                    "borderRadius": "8px",
                    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
                    "flex": "1",
                    "minWidth": "250px",
                    "marginRight": "20px",
                    "border": f"1px solid {COLORS['light']}"
                }),
                
                # Savings Goals Setup Card
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div("3", className="step-number", style={
                                "backgroundColor": COLORS['success'],
                                "color": "white",
                                "width": "30px",
                                "height": "30px",
                                "borderRadius": "50%",
                                "display": "flex",
                                "alignItems": "center",
                                "justifyContent": "center",
                                "marginRight": "15px",
                                "fontWeight": "bold"
                            }),
                            html.H4("Set Savings Goals", style={"color": COLORS['primary'], "margin": "0"})
                        ], style={"display": "flex", "alignItems": "center", "marginBottom": "15px"}),
                        html.P("Create savings targets to build your financial future and track your progress over time.", 
                               style={"color": "#5D6D7E", "marginBottom": "20px"}),
                        dbc.Button([
                            html.I(className="fas fa-piggy-bank", style={"marginRight": "8px"}),
                            "Set Goals"
                        ], href="/savings", color="success", className="setup-btn", 
                           style={"backgroundColor": COLORS['success'], "border": "none"})
                    ], className="setup-card-content", style={"padding": "20px"})
                ], className="setup-card", style={
                    "backgroundColor": "white",
                    "borderRadius": "8px",
                    "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.1)",
                    "flex": "1",
                    "minWidth": "250px",
                    "border": f"1px solid {COLORS['light']}"
                })
            ], className="setup-cards-container", id="setup-steps-container", style={
                "display": "flex",
                "flexWrap": "wrap",
                "marginBottom": "30px",
                "gap": "20px"
            })
        ], id="setup-steps-section", style={"display": "none"}),  # Will be controlled by callback
        
        # Summary tiles section - remains the same
        html.H3("Financial Summary", className="section-title", 
                style={'color': COLORS['primary'], 'borderBottom': f'2px solid {COLORS["accent"]}', 'paddingBottom': '10px'}),
        html.Div(id="summary-tiles", className="metric-container"),
        
        html.Div(style={"height": "24px"}),
        
        # Expense breakdown and savings progress - with improved empty states
        html.Div([
            html.Div([
                # Expense Breakdown Card
                html.Div([
                    html.Div([
                        html.H3("Expense Breakdown", className="card-title")
                    ], className="card-header"),
                    
                    html.Div(id="expense-breakdown-content", className="card-content")
                ], className="dashboard-card", style={"height": "100%"}),
            ], className="column-left"),
            
            html.Div([
                # Savings Progress Card
                html.Div([
                    html.Div([
                        html.H3("Savings Progress", className="card-title")
                    ], className="card-header"),
                    
                    html.Div(id="savings-progress-content", className="card-content")
                ], className="dashboard-card", style={"height": "100%"}),
            ], className="column-right")
        ], className="row-container"),
        
        html.Div(style={"height": "24px"}),
        
        # Recent activity and spending trends - with improved empty states
        html.Div([
            html.Div([
                # Recent Activity Card
                html.Div([
                    html.Div([
                        html.H3("Recent Activity", className="card-title")
                    ], className="card-header"),
                    
                    html.Div(id="recent-activity-content", className="card-content")
                ], className="dashboard-card", style={"height": "100%"}),
            ], className="column-left-small"),
            
            html.Div([
                # Spending Trends Card
                html.Div([
                    html.Div([
                        html.H3("Spending Trends", className="card-title")
                    ], className="card-header"),

                    html.Div(id="spending-trends-content", className="card-content")
                ], className="dashboard-card", style={"height": "100%"}),
            ], className="column-right-large"),

        ], className="row-container"),
        
        html.Div(style={"height": "24px"}),
        
        # Finance insights - with improved empty states
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Finance Insights", className="card-title")
                ], className="card-header"),
                
                # Restructured insights container with consistent styling
                html.Div([
                    html.Div(id="savings-rate-insight", className="insight-card"),
                    html.Div(id="budget-balance-insight", className="insight-card"),
                    html.Div(id="spending-trend-insight", className="insight-card")
                ], className="insights-grid")
            ], className="dashboard-card")
        ], className="row-container")
    ], className="main-content-container p-3", style={"width": "100%", "maxWidth": "100%"}),

    html.Div(id='auth-check'),
    
    # Store components for data
    # dcc.Store(id='session-data-store', data=get_session_data()),
    dcc.Store(id="total-income-store", storage_type="local"),
    dcc.Store(id='expenses-store', storage_type='local'),
    dcc.Store(id='total-expenses-store', storage_type='local'),
    dcc.Store(id='savings-target-store', storage_type='local'),
    dcc.Store(id='Transaction-store', storage_type='local'),
    dcc.Store(id='is-new-user-store', storage_type='local'),  # New store for tracking if user is new
    
    # Include CSS
    html.Link(rel="stylesheet", href="/assets/style.css"),

    # Footer
    html.Footer([
    # Modern top section with logo and quick links
    html.Div([
        # Left side with logo and tagline
        html.Div([
            html.Img(src="/assets/Logo_slogan.PNG", className="footer-logo", style={
                "height": "140px",
                "marginBottom": "10px",
                "filter": "brightness(1.1) contrast(1.1)"
            }),
            # html.P("Empowering your financial future", style={
            #     "color": "#ffffff",
            #     "fontSize": "14px",
            #     "fontWeight": "300",
            #     "letterSpacing": "0.5px",
            #     "margin": "0"
            # })
        ], className="footer-branding", style={
            "flex": "2",
            "marginRight": "40px"
        }),
        
        # Middle section with quick links
        html.Div([
            html.H4("Quick Links", style={
                "fontSize": "16px",
                "fontWeight": "600",
                "color": "#ffffff",
                "marginBottom": "15px",
                "borderBottom": "2px solid rgba(255,255,255,0.2)",
                "paddingBottom": "8px"
            }),
            html.Ul([
                html.Li(html.A("Home", href="/", className="footer-link"), style={"marginBottom": "8px"}),
                html.Li(html.A("Dashboard", href="/dashboard", className="footer-link"), style={"marginBottom": "8px"}),
                html.Li(html.A("Income", href="/income", className="footer-link"), style={"marginBottom": "8px"}),
                html.Li(html.A("Expenses", href="/expenses", className="footer-link"), style={"marginBottom": "8px"}),
                html.Li(html.A("Savings Analysis", href="/savings", className="footer-link"), style={"marginBottom": "8px"}),
                html.Li(html.A("Settings", href="/settings", className="footer-link"), style={"marginBottom": "8px"}),
            ], style={
                "listStyleType": "none",
                "padding": "0",
                "margin": "0"
            })
        ], className="footer-links", style={"flex": "1"}),
        
        # Right section with contact info
        html.Div([
            html.H4("Contact", style={
                "fontSize": "16px",
                "fontWeight": "600",
                "color": "#ffffff",
                "marginBottom": "15px",
                "borderBottom": "2px solid rgba(255,255,255,0.2)",
                "paddingBottom": "8px"
            }),
            html.Div([
                html.P([
                    html.I(className="fas fa-envelope", style={"width": "20px", "marginRight": "10px"}),
                    "support@bluecardfinance.com"
                ], style={"marginBottom": "10px", "fontSize": "14px"}),
                html.P([
                    html.I(className="fas fa-phone", style={"width": "20px", "marginRight": "10px"}),
                    "(+44) 555-0XXX"
                ], style={"marginBottom": "10px", "fontSize": "14px"}),
                html.P([
                    html.I(className="fas fa-map-marker-alt", style={"width": "20px", "marginRight": "10px"}),
                    "123 Finance St, London, LN"
                ], style={"marginBottom": "10px", "fontSize": "14px"})
            ])
        ], className="footer-contact", style={"flex": "1"})
    ], className="footer-top", style={
        "display": "flex",
        "justifyContent": "space-between",
        "padding": "40px 60px",
        "backgroundColor": "rgba(0,0,0,0.1)",
        "borderBottom": "1px solid rgba(255,255,255,0.1)",
        "flexWrap": "wrap",
        "gap": "30px"
    }),
    
    # Middle social media section
    html.Div([
        html.H4("Connect With Us", style={
            "margin": "0 20px 0 0",
            "color": "#ffffff",
            "fontSize": "16px",
            "fontWeight": "400"
        }),
        html.Div([
            html.A(html.I(className="fab fa-facebook-f"), href="#", className="social-icon", style={
                "backgroundColor": "rgba(255,255,255,0.1)",
                "color": "#ffffff",
                "width": "40px",
                "height": "40px",
                "borderRadius": "50%",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "marginRight": "12px",
                "fontSize": "16px"
            }),
            html.A(html.I(className="fab fa-twitter"), href="#", className="social-icon", style={
                "backgroundColor": "rgba(255,255,255,0.1)",
                "color": "#ffffff",
                "width": "40px",
                "height": "40px",
                "borderRadius": "50%",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "marginRight": "12px",
                "fontSize": "16px"
            }),
            html.A(html.I(className="fab fa-linkedin-in"), href="#", className="social-icon", style={
                "backgroundColor": "rgba(255,255,255,0.1)",
                "color": "#ffffff",
                "width": "40px",
                "height": "40px",
                "borderRadius": "50%",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "marginRight": "12px",
                "fontSize": "16px"
            }),
            html.A(html.I(className="fab fa-instagram"), href="#", className="social-icon", style={
                "backgroundColor": "rgba(255,255,255,0.1)",
                "color": "#ffffff",
                "width": "40px",
                "height": "40px",
                "borderRadius": "50%",
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "center",
                "marginRight": "12px",
                "fontSize": "16px"
            })
        ], style={"display": "flex"})
    ], className="footer-social", style={
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center",
        "padding": "20px 60px",
        "borderBottom": "1px solid rgba(255,255,255,0.1)"
    }),
    
    # Bottom copyright section
    html.Div([
        html.P("© 2025 BlueCard Finance. All rights reserved.", style={
            "color": "rgba(255,255,255,0.7)",
            "margin": "0",
            "fontSize": "14px"
        }),
        html.Div([
            html.A("Privacy Policy", href="#", className="footer-link"),
            html.Span("•", style={"color": "rgba(255,255,255,0.4)", "margin": "0 10px"}),
            html.A("Terms of Service", href="#", className="footer-link"),
            html.Span("•", style={"color": "rgba(255,255,255,0.4)", "margin": "0 10px"}),
            html.A("Cookie Policy", href="#", className="footer-link")
        ])
    ], className="footer-bottom", style={
        "display": "flex",
        "justifyContent": "space-between",
        "padding": "20px 60px",
        "flexWrap": "wrap",
        "gap": "15px"
    })
], className="dashboard-footer", style={
    "backgroundColor": COLORS['primary'],
    "color": "#ffffff",
    "boxShadow": "0px -4px 10px rgba(0,0,0,0.1)"
})

], style={"width": "100%", "margin": "0", "padding": "0"})


# Add callback to check if user is new and show appropriate sections
@callback(
    [Output('welcome-banner', 'style'),
     Output('setup-steps-section', 'style'),
     Output('is-new-user-store', 'data')],
    [Input('total-income-store', 'data'),
     Input('total-expenses-store', 'data'),
     Input('savings-target-store', 'data'),
     Input('is-new-user-store', 'data')]
)
def toggle_new_user_ui(total_income, total_expenses, savings_target, is_new_user):
    # Check if any essential data exists
    has_income = total_income is not None and total_income > 0
    has_expenses = total_expenses is not None and total_expenses > 0
    has_savings_goal = savings_target is not None and savings_target > 0
    
    # First visit (is_new_user is None) or explicitly new
    is_new = is_new_user is None or is_new_user == True
    
    # If user has set up any of the key components, they're not new anymore
    if has_income or has_expenses or has_savings_goal:
        is_new = False
    
    # Style for welcome banner
    welcome_style = {
        "backgroundColor": "#F8F9FA",
        "borderRadius": "10px",
        "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.05)",
        "marginBottom": "30px",
        "border": f"1px solid {COLORS['light']}",
        "display": "block" if is_new else "none"
    }
    
    # Style for setup steps section
    steps_style = {
        "display": "block" if is_new else "none"
    }
    
    return welcome_style, steps_style, is_new

@callback(
    Output("total-income-store", "data", allow_duplicate=True),
    Input("session-data-store", "data"),
    prevent_initial_call=True
)
def update_total_income_store(session_data):
    # Get income sources from session data
    income_sources = session_data.get("income_sources", [])
    
    # Calculate total income
    total_income = sum(source["monthly_amount"] for source in income_sources) if income_sources else 0
    
    # Return the total income
    return total_income

@callback(
    Output("total-expenses-store", "data", allow_duplicate=True),
    Input("session-data-store", "data"),
    Input("expenses-store", "data"),
    prevent_initial_call=True
)
def update_total_expenses_store(session_data, expenses_store):
    # First try to get expenses from the expenses-store
    if expenses_store:
        expenses = expenses_store
    # Fall back to session data if expenses-store is empty
    else:
        expenses = session_data.get('expenses', [])
    
    # Calculate total expenses
    total_expenses = sum(expense["amount"] for expense in expenses) if expenses else 0
    
    # Return the total expenses
    return total_expenses

@callback(
    Output("dashboard-income-display", "children"),
    Input("total-income-store", "data")
)
def update_dashboard_income(total_income):
    # Default to 0 if None
    if total_income is None:
        total_income = 0
    
    # Format and return the income value
    return f"£{total_income:,.2f}"

# Add callback to populate summary tiles
@callback(
    Output('summary-tiles', 'children'),
    Input('total-income-store', 'data'),
    Input('total-expenses-store', 'data'),
    Input('savings-target-store', 'data')  
)
def update_summary_tiles(total_income, total_expenses, savings_target):
    print(f"Savings target in dashboard: {savings_target}")

    # Avoid division by zero errors
    if total_income is None:
        total_income = 0
    if total_expenses is None:
        total_expenses = 0
    if savings_target is None:
        savings_target = 0

    remaining = total_income - total_expenses if total_income > 0 else 0
    savings_progress = (savings_target / remaining * 100) if remaining > 0 and savings_target > 0 else 0

    # Consistent styling for all summary tiles
    tile_style = {
        "padding": "20px",
        "borderRadius": "8px",
        "boxShadow": "0 2px 10px rgba(0, 0, 0, 0.1)",
        "backgroundColor": COLORS['white'],
        "transition": "all 0.3s ease"
    }
    
    value_style = {
        "fontSize": "24px",
        "fontWeight": "600",
        "marginBottom": "8px",
        "fontFamily": "'Inter', sans-serif"
    }
    
    subtitle_style = {
        "fontSize": "14px",
        "color": "#6c757d",
        "marginBottom": "0"
    }

    return [
        # Monthly Income Tile
        html.Div([
            html.Div([
                html.H4("Monthly Income", className="summary-title"),
            ], className="summary-header"),
            html.P(id="dashboard-income-display", className="summary-value", 
                  style={**value_style, "color": COLORS['accent']}),
            html.P(f"Daily budget: £{(total_income - total_expenses)/30:,.2f}", className="summary-subtitle",
                 style=subtitle_style)
        ], className="summary-tile", style=tile_style),

        # Total Expenses Tile
        html.Div([
            html.Div([
                html.H4("Total Expenses", className="summary-title"),
            ], className="summary-header"),
            html.P(f"£{total_expenses:,.2f}", className="summary-value", 
                  style={**value_style, "color": COLORS['danger']}),
            html.P(f"{(total_expenses / total_income) * 100:.1f}% of income used" if total_income > 0 else "0% of income used", 
                  className="summary-subtitle", style=subtitle_style)
        ], className="summary-tile", style=tile_style),

        # Remaining Tile
        html.Div([
            html.Div([
                html.H4("Remaining", className="summary-title"),
            ], className="summary-header"),
            html.P(f"£{remaining:,.2f}", className="summary-value", 
                  style={**value_style, "color": COLORS['success']}),
            html.P(f"{(remaining / total_income) * 100:.1f}% of income available" if total_income > 0 else "0% of income available", 
                  className="summary-subtitle", style=subtitle_style)
        ], className="summary-tile", style=tile_style),

        # Savings Target Tile
        html.Div([
            html.Div([
                html.H4("Monthly Savings Target", className="summary-title"),
            ], className="summary-header"),
            html.P(f"£{savings_target:,.2f}", className="summary-value", 
                  style={**value_style, "color": COLORS['warning']}),
            html.P(f"Your savings target is {savings_progress:.1f}% of income after recurring expenses" if remaining > 0 else "Set a monthly savings target", 
                  className="summary-subtitle", style=subtitle_style),
        ], className="summary-tile", style=tile_style)
    ]

@callback(
    Output('expense-breakdown-content', 'children'),
    [Input('total-expenses-store', 'data'),
     Input('expenses-store', 'data'),
     Input('session-data-store', 'data')]
)
def update_expense_breakdown(total_expenses, expenses_store, session_data):
    # First try to use expenses from the expenses-store
    if expenses_store:
        expenses = expenses_store
    # Fall back to session data if expenses-store is empty
    else:
        expenses = session_data.get('expenses', [])
    
    if not expenses:
        return html.Div([
            html.Div([
                html.Img(src="/assets/placeholder-chart.png", style={
                    "width": "120px", 
                    "opacity": "0.6", 
                    "marginBottom": "15px"
                }) if os.path.exists("assets/placeholder-chart.png") else 
                html.I(className="fas fa-chart-pie", style={
                    "fontSize": "50px", 
                    "color": COLORS['gray'], 
                    "opacity": "0.5",
                    "marginBottom": "15px"
                }),
                html.H4("No Expenses Added Yet", style={
                    "color": COLORS['primary'],
                    "fontWeight": "600",
                    "marginBottom": "10px",
                    "fontSize": "18px"
                }),
                html.P("Add your monthly expenses to see a breakdown of where your money is going.", 
                      style={"color": "#5D6D7E", "marginBottom": "20px"}),
                dbc.Button([
                    html.I(className="fas fa-plus", style={"marginRight": "8px"}),
                    "Add Expenses"
                ], href="/expenses", color="primary", className="add-expenses-btn", 
                   style={"backgroundColor": COLORS['accent'], "border": "none"})
            ], className="empty-state-container", style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "justifyContent": "center",
                "padding": "40px 20px",
                "height": "100%",
                "textAlign": "center"
            })
        ])
    
    # Original code for when expenses exist
    # Group expenses by category
    expense_by_category = {}
    for expense in expenses:
        category = expense["category"]
        if category in expense_by_category:
            expense_by_category[category] += expense["amount"]
        else:
            expense_by_category[category] = expense["amount"]
    
    # Create dataframe for pie chart
    df_expenses = pd.DataFrame({
        'Category': list(expense_by_category.keys()),
        'Amount': list(expense_by_category.values()),
    })
    
    # Professional blue color palette
    blue_palette = [
        '#0e4d92', '#145da0', '#1b6eae', '#2281bd', '#2994cc', 
        '#30a7db', '#47b5e5', '#5fc4ee', '#77d2f8', '#98e0ff'
    ]
    
    # Create donut chart with blue shades
    fig = px.pie(
        df_expenses, 
        values='Amount', 
        names='Category', 
        hole=0.6,
        color_discrete_sequence=blue_palette
    )
    fig.update_traces(
        textposition='outside', 
        textinfo='percent+label',
        textfont=dict(family="Inter, sans-serif", size=12, color="#404040")
    )
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=450,
        legend=dict(
            orientation="h", 
            y=-0.2, 
            font=dict(family="Inter, sans-serif", size=11)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12, color="#404040")
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


@callback(
    Output('savings-progress-content', 'children'),
    [Input('Transaction-store', 'data'),
     Input('total-income-store', 'data'),
     Input('savings-target-store', 'data')],
    prevent_initial_call=True
)
def update_savings_progress_with_adjusted_budget(transaction_data, total_income, savings_target):
    if not transaction_data or total_income is None or savings_target is None:
        return html.Div([
            html.Div([
                html.Img(src="/assets/placeholder-savings.png", style={
                    "width": "120px", 
                    "opacity": "0.6", 
                    "marginBottom": "15px"
                }) if os.path.exists("assets/placeholder-savings.png") else 
                html.I(className="fas fa-piggy-bank", style={
                    "fontSize": "50px", 
                    "color": COLORS['gray'], 
                    "opacity": "0.5",
                    "marginBottom": "15px"
                }),
                html.H4("Track Your Savings Progress", style={
                    "color": COLORS['primary'],
                    "fontWeight": "600",
                    "marginBottom": "10px",
                    "fontSize": "18px"
                }),
                html.P([
                    "To track your savings progress: ",
                    html.Ol([
                        html.Li("Add your monthly income", style={"marginBottom": "5px", "textAlign": "left"}),
                        html.Li("Set a monthly savings goal", style={"marginBottom": "5px", "textAlign": "left"}),
                        html.Li("Record your transactions", style={"textAlign": "left"})
                    ], style={"paddingLeft": "20px", "marginBottom": "20px", "marginTop": "10px"})
                ], style={"color": "#5D6D7E"}),
                dbc.Button([
                    html.I(className="fas fa-piggy-bank", style={"marginRight": "8px"}),
                    "Set Savings Goal"
                ], href="/expenses", color="primary", className="set-goal-btn", 
                   style={"backgroundColor": COLORS['warning'], "border": "none"})
            ], className="empty-state-container", style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "justifyContent": "center",
                "padding": "40px 20px",
                "height": "100%",
                "textAlign": "center"
            })
        ])

    # Convert transaction data to a DataFrame
    df_transactions = pd.DataFrame(transaction_data)
    df_transactions['due_date'] = pd.to_datetime(df_transactions['due_date'])

    # Filter transactions for the current month
    today = datetime.datetime.now()
    start_of_month = today.replace(day=1)
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    end_of_month = today.replace(day=days_in_month)

    current_month_transactions = df_transactions[
        (df_transactions['due_date'] >= start_of_month) & (df_transactions['due_date'] <= today)
    ]

    # Calculate total spent so far
    total_spent = current_month_transactions['amount'].sum()

    # Calculate remaining budget
    remaining_budget = total_income - total_spent - savings_target
    days_left = (end_of_month - today).days + 1  # Include today
    adjusted_daily_budget = max(0, remaining_budget / days_left)  # Ensure no negative budget

    # Analyze daily spending
    daily_totals = current_month_transactions.groupby(current_month_transactions['due_date'].dt.date)['amount'].sum()
    daily_budget = (total_income - savings_target) / days_in_month
    days_under_budget = len(daily_totals[daily_totals <= daily_budget])
    days_over_budget = len(daily_totals[daily_totals > daily_budget])

    # Calculate savings progress
    savings_progress = min((savings_target / (total_income - total_spent)) * 100, 100) if total_income > total_spent else 0

    # Create progress wheel (gauge chart)
    progress_wheel = go.Figure(go.Indicator(
        mode="gauge+number",
        value=savings_progress,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#404040"},
            'bar': {'color': COLORS['accent']},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e5e5e5",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(52, 152, 219, 0.2)'},
                {'range': [30, 70], 'color': 'rgba(52, 152, 219, 0.4)'},
                {'range': [70, 100], 'color': 'rgba(52, 152, 219, 0.6)'}
            ],
        },
        title={
            'text': "Savings Progress",
            'font': {'size': 17, 'color': COLORS['primary'], 'family': 'Inter, sans-serif'}
        },
        number={
            'suffix': "%",
            'font': {'size': 23, 'color': COLORS['accent'], 'family': 'Inter, sans-serif'}
        }
    ))
    progress_wheel.update_layout(
        height=300,
        margin=dict(t=60, b=0, l=30, r=30),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif")
    )

    # Consistent style for insight items
    insight_item_style = {
        "padding": "12px 15px",
        "borderRadius": "8px",
        "backgroundColor": "#f8f9fa",
        "marginBottom": "10px",
        "fontSize": "14px",
        "fontFamily": "'Inter', sans-serif",
        "display": "flex",
        "alignItems": "center"
    }
    
    icon_style = {
        "marginRight": "10px",
        "fontSize": "16px"
    }

    # Create professional insights
    insights = [
        html.Div([
            html.I(className="fas fa-check-circle", style={**icon_style, "color": COLORS['success']}),
            html.Span(f"Your savings goal is {savings_progress:.1f}% of your income after all expenses for the month.")
        ], style=insight_item_style),
        html.Div([
            html.I(className="fas fa-check-circle", style={**icon_style, "color": COLORS['success']}),
            html.Span(f"You stayed under your daily budget on {days_under_budget} day(s).")
        ], style=insight_item_style),
        html.Div([
            html.I(className="fas fa-exclamation-triangle", style={**icon_style, "color": COLORS['danger']}),
            html.Span(f"You exceeded your daily budget on {days_over_budget} day(s).")
        ], style=insight_item_style),
        html.Div([
            html.I(className="fas fa-lightbulb", style={**icon_style, "color": COLORS['accent']}),
            html.Span(f"To achieve your savings goal by {end_of_month.strftime('%b %d')}, your daily budget is £{adjusted_daily_budget:,.2f}.")
        ], style=insight_item_style)
    ]

    # Combine progress wheel and insights with refined layout
    return html.Div([
        html.Div([
            dcc.Graph(figure=progress_wheel, config={'displayModeBar': False}),
        ], className="progress-wheel-container", style={"marginBottom": "20px"}),
        html.Div(insights, className="insights-container", style={
            "padding": "15px",
            "borderRadius": "8px",
            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.05)"
        })
    ], className="savings-progress-card")

@callback(
    Output('recent-activity-content', 'children'),
    Input('Transaction-store', 'data'),
    prevent_initial_call=True
)
def update_recent_activity(transaction_data):
    if not transaction_data:
        return html.Div([
            html.Div([
                html.I(className="fas fa-receipt", style={
                    "fontSize": "50px", 
                    "color": COLORS['gray'], 
                    "opacity": "0.5",
                    "marginBottom": "15px"
                }),
                html.H4("No Transaction History", style={
                    "color": COLORS['primary'],
                    "fontWeight": "600",
                    "marginBottom": "10px",
                    "fontSize": "18px"
                }),
                html.P("Start tracking your daily spending to see your recent transactions here.", 
                      style={"color": "#5D6D7E", "marginBottom": "20px"}),
                dbc.Button([
                    html.I(className="fas fa-plus", style={"marginRight": "8px"}),
                    "Add Transaction"
                ], href="/expenses", color="primary", className="add-transaction-btn", 
                   style={"backgroundColor": COLORS['accent'], "border": "none"})
            ], className="empty-state-container", style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "justifyContent": "center",
                "padding": "30px 20px",
                "height": "100%",
                "textAlign": "center"
            })
        ])
    
    # Convert transaction data to a DataFrame and sort by date
    df_recent = pd.DataFrame(transaction_data)
    df_recent['due_date'] = pd.to_datetime(df_recent['due_date'])
    df_recent = df_recent.sort_values('due_date', ascending=False).head(5)  # Show the 5 most recent transactions

    # Create transaction items with consistent styling
    transaction_item_style = {
        "padding": "15px",
        "marginBottom": "10px",
        "border": "1px solid #e5e5e5",
        "borderRadius": "8px",
        "boxShadow": "0 2px 4px rgba(0, 0, 0, 0.05)",
        "display": "flex",
        "justifyContent": "space-between",
        "alignItems": "center",
        "fontFamily": "'Inter', sans-serif"
    }
    
    transaction_title_style = {
        "fontSize": "14px", 
        "fontWeight": "600", 
        "color": COLORS['primary'],
        "marginBottom": "4px"
    }
    
    transaction_meta_style = {
        "fontSize": "12px", 
        "color": "#6c757d"
    }
    
    transaction_amount_style = {
        "fontSize": "15px", 
        "fontWeight": "600", 
        "color": COLORS['accent']
    }

    transaction_items = []
    for _, row in df_recent.iterrows():
        transaction_items.append(html.Div([
            html.Div([
                html.Div(row['description'], style=transaction_title_style),
                html.Div(row['due_date'].strftime('%b %d, %Y'), style=transaction_meta_style)
            ]),
            html.Div(f"£{row['amount']:.2f}", style=transaction_amount_style)
        ], style=transaction_item_style))
    
    return html.Div(transaction_items, style={"padding": "5px"})

@callback(
    Output('spending-trends-content', 'children'),
    Input('Transaction-store', 'data'),
    prevent_initial_call=True
)
def update_spending_trends(transaction_data):
    if not transaction_data:
        return html.Div([
            html.Div([
                html.I(className="fas fa-chart-line", style={
                    "fontSize": "50px", 
                    "color": COLORS['gray'], 
                    "opacity": "0.5",
                    "marginBottom": "15px"
                }),
                html.H4("No Spending Data Yet", style={
                    "color": COLORS['primary'],
                    "fontWeight": "600",
                    "marginBottom": "10px",
                    "fontSize": "18px"
                }),
                html.P([
                    "To see your spending trends over time, start by:",
                    html.Ul([
                        html.Li("Adding daily transactions", style={"marginBottom": "5px", "textAlign": "left"}),
                        html.Li("Categorizing your expenses", style={"marginBottom": "5px", "textAlign": "left"}),
                        html.Li("Tracking consistently for best insights", style={"textAlign": "left"})
                    ], style={"paddingLeft": "20px", "marginTop": "10px", "marginBottom": "20px"})
                ], style={"color": "#5D6D7E", "textAlign": "center"}),
                dbc.Button([
                    html.I(className="fas fa-plus", style={"marginRight": "8px"}),
                    "Record Expenses"
                ], href="/expenses", color="primary", className="record-expenses-btn", 
                   style={"backgroundColor": COLORS['accent'], "border": "none"})
            ], className="empty-state-container", style={
                "display": "flex",
                "flexDirection": "column",
                "alignItems": "center",
                "justifyContent": "center",
                "padding": "40px 20px",
                "height": "100%",
                "textAlign": "center"
            })
        ])
    
    # Convert transaction data to a DataFrame
    df_transactions = pd.DataFrame(transaction_data)
    df_transactions['due_date'] = pd.to_datetime(df_transactions['due_date'])
    
    # Group by due date and sum amounts
    daily_totals = df_transactions.groupby(df_transactions['due_date'].dt.date)['amount'].sum().reset_index()
    daily_totals['due_date'] = pd.to_datetime(daily_totals['due_date'])
    daily_totals = daily_totals.sort_values('due_date')

    # Ensure daily frequency
    date_range = pd.date_range(start=daily_totals['due_date'].min(), end=daily_totals['due_date'].max())
    daily_totals = daily_totals.set_index('due_date').reindex(date_range, fill_value=0).reset_index()
    daily_totals.columns = ['due_date', 'amount']

    # Dynamically adjust y-axis range
    y_max = daily_totals['amount'].max() * 1.2 if not daily_totals.empty else 100

    # Create line chart with more professional styling
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_totals['due_date'],
        y=daily_totals['amount'],
        mode='lines+markers',
        name='Daily Spending',
        line=dict(color=COLORS['accent'], width=3),
        marker=dict(size=8, color=COLORS['accent'])
    ))
    
    fig.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=450,
        legend=dict(orientation="h", y=1.1),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12, color=COLORS['primary']),
        xaxis=dict(
            showgrid=True,
            gridcolor='#e5e5e5',
            showline=True,
            linecolor='#e5e5e5',
            title="Date",
            tickformat="%b %d"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#e5e5e5',
            showline=True,
            linecolor='#e5e5e5',
            title="Amount (£)",
            range=[0, y_max],
            tickprefix='£'
        ),
        hovermode="x unified"
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False}, style={"padding": "10px"})

@callback(
    Output('budget-balance-insight', 'children'),
    Input('expenses-store', 'data'),
    Input('session-data-store', 'data')
)
def update_budget_balance_insight(expenses_store, data):
    # First try to use expenses from the expenses-store
    if expenses_store:
        expenses = expenses_store
    # Fall back to session data if expenses-store is empty
    else:
        expenses = data.get('expenses', [])
    
    if not expenses:
        return html.Div([
            html.Div([
                html.I(className="fas fa-balance-scale", style={
                    "fontSize": "24px", 
                    "color": COLORS['gray'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4("Budget Balance", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P("Add expenses in the Expenses tab to get budget balance insights.", style={
                        "fontSize": "14px", 
                        "margin": "0",
                        "color": COLORS['gray']
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['gray']}"
            })
        ])
    
    # Find the largest expense category
    expense_by_category = {}
    total_expenses = 0
    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]
        total_expenses += amount
        if category in expense_by_category:
            expense_by_category[category] += amount
        else:
            expense_by_category[category] = amount
    
    largest_category = max(expense_by_category.items(), key=lambda x: x[1])
    largest_percent = largest_category[1] / total_expenses * 100
    
    if largest_percent > 50:
        return html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-circle", style={
                    "fontSize": "24px", 
                    "color": COLORS['warning'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4(f"High {largest_category[0]} Expenses", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P([
                        f"{largest_category[0]} makes up ",
                        html.Strong(f"{largest_percent:.1f}%", style={"color": COLORS['warning']}),
                        " of your expenses. Consider rebalancing your budget."
                    ], style={
                        "fontSize": "14px", 
                        "margin": "0"
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['warning']}"
            })
        ])
    else:
        return html.Div([
            html.Div([
                html.I(className="fas fa-balance-scale", style={
                    "fontSize": "24px", 
                    "color": COLORS['success'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4("Balanced Budget", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P([
                        f"Your largest expense category ({largest_category[0]}) is ",
                        html.Strong(f"{largest_percent:.1f}%", style={"color": COLORS['success']}),
                        " of total expenses."
                    ], style={
                        "fontSize": "14px", 
                        "margin": "0"
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['success']}"
            })
        ])


@callback(
    Output('spending-trend-insight', 'children', allow_duplicate=True),
    Input('Transaction-store', 'data'),
    prevent_initial_call=True
)
def update_spending_trend_insight(transaction_data):
    if not transaction_data:
        return html.Div([
            html.Div([
                html.I(className="fas fa-chart-line", style={
                    "fontSize": "24px", 
                    "color": COLORS['gray'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4("Spending Trends", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P("Record daily transactions to get spending trend insights.", style={
                        "fontSize": "14px", 
                        "margin": "0",
                        "color": COLORS['gray']
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['gray']}"
            })
        ])

    # Convert transaction data to a DataFrame
    df_transactions = pd.DataFrame(transaction_data)
    df_transactions['due_date'] = pd.to_datetime(df_transactions['due_date'])

    # Group by date and calculate daily totals
    daily_totals = df_transactions.groupby(df_transactions['due_date'].dt.date)['amount'].sum().reset_index()
    daily_totals.columns = ['date', 'amount']

    # Get last 7 days and previous 7 days
    today = datetime.datetime.now().date()
    last_week = daily_totals[daily_totals['date'] >= (today - datetime.timedelta(days=7))]
    prev_week = daily_totals[(daily_totals['date'] < (today - datetime.timedelta(days=7))) &
                             (daily_totals['date'] >= (today - datetime.timedelta(days=14)))]

    # Calculate totals for last week and previous week
    last_week_total = last_week['amount'].sum() if not last_week.empty else 0
    prev_week_total = prev_week['amount'].sum() if not prev_week.empty else 0

    # Calculate percentage change
    if prev_week_total > 0:
        percent_change = (last_week_total - prev_week_total) / prev_week_total * 100
    else:
        percent_change = None

    # Generate insights based on percentage change
    if percent_change is None:
        return html.Div([
            html.Div([
                html.I(className="fas fa-info-circle", style={
                    "fontSize": "24px", 
                    "color": COLORS['gray'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4("Spending Analysis", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P("Not enough data to analyze spending trends.", style={
                        "fontSize": "14px", 
                        "margin": "0",
                        "color": COLORS['gray']
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['gray']}"
            })
        ])
    elif percent_change > 20:
        return html.Div([
            html.Div([
                html.I(className="fas fa-arrow-circle-up", style={
                    "fontSize": "24px", 
                    "color": COLORS['danger'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4("Spending Increase", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P([
                        "Your spending increased by ",
                        html.Strong(f"{percent_change:.1f}%", style={"color": COLORS['danger']}),
                        " compared to the previous week."
                    ], style={
                        "fontSize": "14px", 
                        "margin": "0"
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['danger']}"
            })
        ])
    elif percent_change < -10:
        return html.Div([
            html.Div([
                html.I(className="fas fa-arrow-circle-down", style={
                    "fontSize": "24px", 
                    "color": COLORS['success'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4("Reduced Spending", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P([
                        "Great job! You reduced spending by ",
                        html.Strong(f"{abs(percent_change):.1f}%", style={"color": COLORS['success']}),
                        " from last week."
                    ], style={
                        "fontSize": "14px", 
                        "margin": "0"
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['success']}"
            })
        ])
    else:
        return html.Div([
            html.Div([
                html.I(className="fas fa-equals", style={
                    "fontSize": "24px", 
                    "color": COLORS['accent'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4("Consistent Spending", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P([
                        "Your spending is within ",
                        html.Strong(f"{abs(percent_change):.1f}%", style={"color": COLORS['accent']}),
                        " of last week."
                    ], style={
                        "fontSize": "14px", 
                        "margin": "0"
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['accent']}"
            })
        ])
    
@callback(
    Output('some-dashboard-component', 'children'),
    Input('total-expenses-store', 'data'),
)
def use_expenses_in_dashboard(total_expenses):
    if total_expenses is None:
        return "No expense data available"

    return f"Total expenses: £{total_expenses:,.2f}"

@callback(
    Output('savings-goal-display', 'children'),
    Input('savings-target-store', 'data')  # Fetch data from the savings-target-store
)
def display_savings_goal(savings_target):
    if savings_target is None:
        return html.P("No savings target set.", className="text-muted")
    return html.H5(f"Savings Goal: £{savings_target:.2f}")

@callback(
    Output('savings-rate-insight', 'children'),
    Input('total-income-store', 'data'),
    Input('total-expenses-store', 'data'),
)
def update_savings_rate_insight(total_income, total_expenses):
    if total_income is None or total_income <= 0:
        return html.Div([
            html.Div([
                html.I(className="fas fa-chart-line", style={
                    "fontSize": "24px", 
                    "color": COLORS['gray'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4("Savings Rate", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P("Set your income to see savings rate insights.", style={
                        "fontSize": "14px", 
                        "margin": "0",
                        "color": COLORS['gray']
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['gray']}"
            })
        ])
    
    # Calculate savings rate with total_expenses
    if total_expenses is None:
        total_expenses = 0
        
    savings_rate = (total_income - total_expenses) / total_income * 100
    
    if savings_rate >= 20:
        return html.Div([
            html.Div([
                html.I(className="fas fa-check-circle", style={
                    "fontSize": "24px", 
                    "color": COLORS['success'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4("Excellent Savings Rate", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P([
                        f"Your savings rate is ",
                        html.Strong(f"{savings_rate:.1f}%", style={"color": COLORS['success']}),
                        ", which is excellent for long-term financial health."
                    ], style={
                        "fontSize": "14px", 
                        "margin": "0"
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['success']}"
            })
        ])
    elif savings_rate >= 10:
        return html.Div([
            html.Div([
                html.I(className="fas fa-thumbs-up", style={
                    "fontSize": "24px", 
                    "color": COLORS['accent'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4("Good Savings Rate", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P([
                        f"Your savings rate is ",
                        html.Strong(f"{savings_rate:.1f}%", style={"color": COLORS['accent']}),
                        ", which is a good foundation."
                    ], style={
                        "fontSize": "14px", 
                        "margin": "0"
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['accent']}"
            })
        ])
    else:
        return html.Div([
            html.Div([
                html.I(className="fas fa-exclamation-triangle", style={
                    "fontSize": "24px", 
                    "color": COLORS['warning'],
                    "marginRight": "15px"
                }),
                html.Div([
                    html.H4("Low Savings Rate", style={
                        "fontSize": "16px", 
                        "fontWeight": "600", 
                        "color": COLORS['primary'],
                        "marginBottom": "5px"
                    }),
                    html.P([
                        f"Your savings rate is only ",
                        html.Strong(f"{savings_rate:.1f}%", style={"color": COLORS['warning']}),
                        ". Try to reduce non-essential expenses."
                    ], style={
                        "fontSize": "14px", 
                        "margin": "0"
                    })
                ])
            ], style={
                "display": "flex", 
                "alignItems": "center",
                "padding": "18px",
                "backgroundColor": COLORS['light'],
                "borderRadius": "8px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.04)",
                "borderLeft": f"4px solid {COLORS['warning']}"
            })
        ])

from dash import callback_context

@callback(
    [Output("dropdown-state", "data", allow_duplicate=True),
     Output("user-dropdown-content", "className", allow_duplicate=True)],
    [Input("user-dropdown-button", "n_clicks"),
     Input("dropdown-state", "data")],
    prevent_initial_call=True
)
def toggle_and_update_dropdown(n_clicks, is_open):
    if n_clicks:
        # Toggle dropdown state
        is_open = not is_open if is_open is not None else False

    # Update dropdown content visibility
    dropdown_class = "user-dropdown-content show" if is_open else "user-dropdown-content"
    
    return is_open, dropdown_class

# Logout logic (client-side)
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            // Remove session data from localStorage
            localStorage.removeItem("session-data-store");
            // Trigger a redirect using Dash's dcc.Location to logout route
            return {pathname: '/'}; // Redirect to the logout route
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("session-data-store", "data", allow_duplicate=True),
    Input("logout-link", "n_clicks"),
    prevent_initial_call=True
)

# Sync user data for dropdown based on session
@callback(
    Output("user-id", "data", allow_duplicate=True),
    Input("session-data-store", "data"),
    prevent_initial_call=True
)
def sync_user_data(session_data):
    return {'user_id': session_data.get('user_id')} if session_data and 'user_id' in session_data else {}

