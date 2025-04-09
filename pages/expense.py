# expenses.py - Dash Page for Expense Management with Professional Design

from dash import html, dcc, Input, Output, State, callback, ctx, ALL
import dash_bootstrap_components as dbc
import datetime
import dash
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.exceptions import PreventUpdate
import uuid

# Register this file as a page
dash.register_page(__name__, path='/expenses')

# Professional color palette
COLORS = {
    'primary': '#2C3E50',    # Dark blue-gray
    'secondary': '#34495E',  # Lighter blue-gray
    'accent': '#3498DB',     # Bright blue
    'success': '#2ECC71',    # Green
    'warning': '#F39C12',    # Orange
    'danger': '#E74C3C',     # Red
    'light': '#ECF0F1',      # Light gray
    'dark': '#1A252F',       # Very dark blue-gray
    'white': '#FFFFFF',      # White
    'muted': '#95A5A6'       # Muted gray
}

# Category color mapping for consistent visualization
CATEGORY_COLORS = {
    "Housing": "#3498DB",           # Blue
    "Transportation": "#2ECC71",    # Green
    "Food": "#F1C40F",              # Yellow
    "Utilities": "#9B59B6",         # Purple
    "Health": "#E74C3C",            # Red
    "Insurance": "#34495E",         # Dark Blue
    "Debt": "#16A085",              # Teal
    "Entertainment": "#F39C12",     # Orange
    "Personal": "#95A5A6",          # Gray
    "Education": "#3498DB",         # Blue
    "Savings": "#27AE60",           # Dark Green
    "Other": "#7F8C8D"              # Dark Gray
}

# Blue color palette
BLUE_PALETTE = ['#2C3E50', '#2980B9', '#3498DB', '#5DADE2', '#85C1E9', '#AED6F1']

# Updated card styles
CARD_STYLE = {
    'borderRadius': '12px',  # More rounded corners
    'boxShadow': '0 6px 12px rgba(0, 0, 0, 0.1)',  # Subtle shadow
    'border': f'1px solid {COLORS["light"]}',  # Light border
    'backgroundColor': COLORS['white'],  # White background
    'padding': '15px'  # Add padding for better spacing
}

HEADER_STYLE = {
    'backgroundColor': COLORS['primary'],  # Dark blue header
    'color': COLORS['white'],  # White text
    'borderBottom': f'2px solid {COLORS["accent"]}',  # Accent border
    'borderRadius': '12px 12px 0 0',  # Rounded top corners
    'padding': '15px 20px',  # Add padding
    'fontWeight': 'bold',  # Bold header text
    'fontSize': '16px'  # Slightly larger font
}

# Layout for the Expenses Page
# Layout for the Expenses Page
layout = html.Div([
    # Header - Keep as is per request
    # Logo and Title
    html.Div([
        html.Img(src="/assets/Logo_slogan.PNG", className="dashboard-logo"),
        

        # Navigation - Keep as is per request
        html.Nav([
            html.Button([
                html.Span("BlueCard Finance", className="mobile-nav-toggle-text"),
                html.Span("≡")
            ], className="mobile-nav-toggle", id="mobile-nav-toggle"),

            html.Ul([
                html.Li(html.A([html.Span(className="nav-icon"), "Home"], href="/", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Dashboard"], href="/dashboard", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Income"], href="/income", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Expenses"], href="/expenses", className="nav-link active"), className="nav-item"),
                html.Li([html.A([html.Span(className="nav-icon"), "Savings Analysis"], href="/savings", className="nav-link")], className="nav-item"),
                # html.Li(html.A([html.Span("⚙️", className="nav-icon"), "Settings"], href="/settings", className="nav-link"), className="nav-item")
            ], className="nav-menu", id="nav-menu")
        ], className="nav-bar"),
    ], className="header-container"),

    # Optional Breadcrumb with improved styling
    html.Ul([
        html.Li([
            html.A("Home", href="/", className="breadcrumb-link")
        ], className="breadcrumb-item"),
        html.Li("Expenses", className="breadcrumb-item breadcrumb-current")
    ], className="breadcrumb", style={'backgroundColor': COLORS['light'], 'borderRadius': '8px'}),

    # Main Content Container
    html.Div([

        html.H2("Expense Management", className="section-title mb-4",
                style={'color': COLORS['primary'], 'borderBottom': f'2px solid {COLORS["accent"]}', 'paddingBottom': '10px'}),

        dbc.Row([
            # Left Column: Expense Form & List with Categories
            dbc.Col([
                # Add Expense Card with improved styling
                dbc.Card([
                    dbc.CardHeader(html.H5("Add Monthly Expense", className="card-title m-0"), style=HEADER_STYLE),
                    dbc.CardBody([
                        dbc.Form([
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Description", className="text-muted"),
                                    dbc.Input(id='desc-input', placeholder='e.g., Rent, Netflix', type='text', 
                                             className='mb-2', style={'borderRadius': '6px'})
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Amount (£)", className="text-muted"),
                                    dbc.InputGroup([
                                        dbc.InputGroupText("£", style={'backgroundColor': COLORS['primary'], 'color': COLORS['white'], 'borderRadius': '6px 0 0 6px'}),
                                        dbc.Input(id='amount-input', placeholder='0.00', type='number', min=0, step=0.01,
                                                 style={'borderRadius': '0 6px 6px 0'})
                                    ], className='mb-2')
                                ], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Label("Category", className="text-muted"),
                                    dcc.Dropdown(
                                        id='category-input',
                                        options=[{'label': cat, 'value': cat} for cat in CATEGORY_COLORS.keys()],
                                        placeholder='Select Category',
                                        className='mb-2',
                                        style={'borderRadius': '6px'}
                                    )
                                ], width=6),
                                dbc.Col([
                                    dbc.Label("Due Date", className="text-muted"),
                                    dcc.DatePickerSingle(
                                        id='due-date-input',
                                        date=datetime.date.today(),
                                        display_format='MMM DD, YYYY',
                                        className='mb-2 w-100',
                                        style={'borderRadius': '6px'}
                                    )
                                ], width=6),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        dbc.Label("Recurring Type:", className="text-muted me-2"),
                                        dbc.RadioItems(
                                            options=[
                                                {"label": "One-time", "value": False},
                                                {"label": "Monthly", "value": True},
                                            ],
                                            value=False,
                                            id="recurring-input",
                                            inline=True,
                                            className="mb-0"
                                        ),
                                    ], style={'display': 'flex', 'alignItems': 'center'})
                                ], width=6),
                                dbc.Col([
                                    dbc.Button("Add Expense", id='submit-expense', 
                                               style={'backgroundColor': COLORS['accent'], 'border': 'none', 'borderRadius': '6px'},
                                               className="float-end")
                                ], width=6),
                            ]),
                        ])
                    ])
                ], className='mb-4', style=CARD_STYLE),

                # Expense Categories Card
                dbc.Card([
                    dbc.CardHeader(html.H5("Expense Categories", className="card-title m-0"), style=HEADER_STYLE),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div(id='expense-category-chart', className="chart-container")
                            ], width=12),
                        ]),
                        html.Hr(style={'margin': '15px 0', 'backgroundColor': COLORS['light']}),
                    ])
                ], className='mb-4', style=CARD_STYLE),

                # Current Monthly Expenses Card
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.H5("Current Monthly Expenses", className="card-title m-0"),
                            html.Span(id="total-expense-badge", className="badge",
                                    style={
                                        'backgroundColor': COLORS['accent'],
                                        'borderRadius': '20px',
                                        'padding': '8px 12px',
                                        'fontSize': '14px',
                                        'color': COLORS['white'],
                                        'marginLeft': 'auto'
                                    })
                        ], style={"display": "flex", "alignItems": "center", "width": "100%", "justifyContent": "space-between"})
                    ], style=HEADER_STYLE),
                    dbc.CardBody([
                        # Custom tabs with better styling
                        html.Div([
                            dbc.Row([
                                dbc.Col(
                                    html.Div(
                                        dbc.Button(
                                            "All Expenses", 
                                            id="tab-all-btn",
                                            className="tab-button active",
                                            style={
                                                "backgroundColor": COLORS['primary'],
                                                "color": COLORS['white'],
                                                "border": "none",
                                                "borderRadius": "6px 0 0 6px",
                                                "padding": "10px 15px"
                                            }
                                        ),
                                        className="d-grid"
                                    ),
                                    width=4,
                                    className="px-0"
                                ),
                                dbc.Col(
                                    html.Div(
                                        dbc.Button(
                                            "Monthly Recurring", 
                                            id="tab-recurring-btn",
                                            className="tab-button",
                                            style={
                                                "backgroundColor": COLORS['light'],
                                                "color": COLORS['dark'],
                                                "border": "none",
                                                "borderRadius": "0",
                                                "padding": "10px 15px"
                                            }
                                        ),
                                        className="d-grid"
                                    ),
                                    width=4,
                                    className="px-0"
                                ),
                                dbc.Col(
                                    html.Div(
                                        dbc.Button(
                                            "One-time Expenses", 
                                            id="tab-non-recurring-btn",
                                            className="tab-button",
                                            style={
                                                "backgroundColor": COLORS['light'],
                                                "color": COLORS['dark'],
                                                "border": "none",
                                                "borderRadius": "0 6px 6px 0",
                                                "padding": "10px 15px"
                                            }
                                        ),
                                        className="d-grid"
                                    ),
                                    width=4,
                                    className="px-0"
                                ),
                            ], className="mb-3 tab-container"),
                        ]),
                        # Container for the filtered expense list
                        html.Div(id='expense-list-container', className="mt-3"),
                    ])
                ], className='mb-4', style=CARD_STYLE),
            ], md=8),  # This is the missing closing bracket with the column width

            # Right Column: Summary & Savings
            dbc.Col([
                # Monthly Overview with enhanced styling
                dbc.Card([
                    dbc.CardHeader(html.H5("Monthly Overview", className="card-title m-0"), style=HEADER_STYLE),
                    dbc.CardBody([
                        html.Div(id='monthly-overview-chart', className="chart-container")
                    ])
                ], className='mb-4', style=CARD_STYLE),

                # Recurring vs One-time Analysis
                dbc.Card([
                    dbc.CardHeader(html.H5("Expense Type Analysis", className="card-title m-0"), style=HEADER_STYLE),
                    dbc.CardBody([
                        html.Div(id='recurring-analysis-chart', className="chart-container")
                    ])
                ], className='mb-4', style=CARD_STYLE),

                # Savings Target Card with enhanced styling
                dbc.Card([
                    dbc.CardHeader(html.H5("Set Savings Target", className="card-title m-0"), style=HEADER_STYLE),
                    dbc.CardBody([
                        dbc.Label("Monthly Savings Goal", className="text-muted"),
                        dbc.InputGroup([
                            dbc.InputGroupText("£", style={'backgroundColor': COLORS['primary'], 'color': COLORS['white'], 'borderRadius': '6px 0 0 6px'}),
                            dbc.Input(id='savings-goal-input', type='number', min=0, step=0.01, placeholder="0.00",
                                     className='mb-2', style={'borderRadius': '0 6px 6px 0'}),
                        ]),
                        dbc.Button("Update Savings Goal", id='update-savings-goal', 
                                  style={'backgroundColor': COLORS['accent'], 'border': 'none', 'borderRadius': '6px'},
                                  className="w-100 mt-2"),
                        html.Div(id='savings-summary', className='mt-3 p-3 rounded', 
                                style={"backgroundColor": COLORS['light'], 'borderRadius': '6px'})
                    ])
                ], style=CARD_STYLE)
            ], md=4)
        ])
    ], className="main-content-container p-3"),

    # Local storage for expenses and other variables
    dcc.Store(id='expenses-store', storage_type='local'),
    dcc.Store(id='salary-store', storage_type='local'),
    dcc.Store(id='savings-target-store', storage_type='local'),
    dcc.Store(id='total-income-store', storage_type='local'),  # Add this to access income data
    dcc.Store(id='Transaction-store', storage_type='local'), # Add this to access transaction data
    dcc.Store(id='active-tab-store', storage_type='memory', data=None),
    
    # Client-side stores are initialized with default values but don't persist
    dcc.Store(id='expense-data-filtered', storage_type='memory'),
    
    # Interval for initialization (runs once)
    dcc.Interval(id='interval-component', interval=1000, max_intervals=1),

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

])

# Initialize stores with default data (only runs once)
@callback(
    Output('expenses-store', 'data', allow_duplicate=True),
    Output('salary-store', 'data', allow_duplicate=True),
    Output('savings-target-store', 'data', allow_duplicate=True),
    Input('interval-component', 'n_intervals'),
    State('expenses-store', 'data'),
    prevent_initial_call=True
)
def initialize_stores(n_intervals, existing_expenses):
    # Only initialize if no data exists (prevent wiping out user data)
    if existing_expenses is not None:
        raise PreventUpdate
        
    # Default monthly income
    initial_income = 0
    
    # Default savings target
    initial_savings = 0
    
    return initial_income, initial_savings

# Add new expense
@callback(
    Output('expenses-store', 'data', allow_duplicate=True),
    Input('submit-expense', 'n_clicks'),
    State('desc-input', 'value'),
    State('amount-input', 'value'),
    State('category-input', 'value'),
    State('due-date-input', 'date'),
    State('recurring-input', 'value'),
    State('expenses-store', 'data'),
    prevent_initial_call=True
)
def add_expense(n_clicks, desc, amount, category, due_date, recurring, expenses_data):
    if not n_clicks or not desc or amount is None or not category or not due_date:
        raise PreventUpdate

    # Ensure we have data to work with
    if expenses_data is None:
        expenses_data = []
        
    # Generate unique ID based on description and timestamp
    expense_id = f"{desc.lower().replace(' ', '-')}-{uuid.uuid4().hex[:8]}"
    
    # Create new expense object
    new_expense = {
        'id': expense_id,
        'description': desc,
        'amount': float(amount),
        'category': category,
        'due_date': due_date,
        'recurring': bool(recurring),
        'date_added': datetime.date.today().isoformat()
    }
    
    # Add to expenses list
    updated_expenses = expenses_data + [new_expense]
    
    return updated_expenses

# Filter expenses based on user selection
@callback(
    Output('expense-data-filtered', 'data'),
    Input('expenses-store', 'data'),
    Input('active-tab-store', 'data')
)
def filter_expenses(expenses, active_tab):
    if not expenses:
        return {'all': [], 'recurring': [], 'non_recurring': [], 'total': 0}
    
    # Get recurring and non-recurring expenses
    recurring_expenses = [exp for exp in expenses if exp.get('recurring') is True]
    non_recurring_expenses = [exp for exp in expenses if exp.get('recurring') is not True]
    
    # If no tab is selected, return empty filtered expenses
    if active_tab is None:
        filtered_expenses = []
    # Otherwise filter based on the active tab
    elif active_tab == 'tab-recurring':
        filtered_expenses = recurring_expenses
    elif active_tab == 'tab-non-recurring':
        filtered_expenses = non_recurring_expenses
    else:  # Default to 'tab-all'
        filtered_expenses = expenses
    
    # Calculate totals
    total_expenses = sum(exp.get('amount', 0) for exp in expenses)
    
    return {
        'all': expenses,
        'recurring': recurring_expenses,
        'non_recurring': non_recurring_expenses,
        'filtered': filtered_expenses,  # New field for the filtered expenses
        'total': total_expenses,
        'total_recurring': sum(exp.get('amount', 0) for exp in recurring_expenses),
        'total_non_recurring': sum(exp.get('amount', 0) for exp in non_recurring_expenses)
    }

# Helper function to create expense cards
def create_expense_items(data):
    if not data or len(data) == 0:
        return [html.P("No expenses in this category.", className="text-muted text-center py-3")]
    
    expense_items = []
    
    for exp in data:
        try:
            # Get expense properties
            expense_id = exp.get('id')
            description = exp.get('description', "No description")
            amount = exp.get('amount', 0.0)
            category = exp.get('category', "Other")
            due_date = exp.get('due_date', "N/A")
            recurring = exp.get('recurring', False)
            
            # Format due date
            try:
                due_date_obj = datetime.date.fromisoformat(due_date)
                due_date_display = due_date_obj.strftime("%b %d, %Y")
            except:
                due_date_display = due_date
            
            # Get category color
            category_color = CATEGORY_COLORS.get(category, COLORS['muted'])
            
            # Create expense card with more professional styling
            item = dbc.Card([
                dbc.CardBody([
                    html.Div([
                        # Left section with category and description
                        html.Div([
                            html.Div([
                                html.Span(category, 
                                    className="badge me-2", 
                                    style={
                                        "backgroundColor": category_color, 
                                        "color": "white", 
                                        "borderRadius": "4px", 
                                        "padding": "4px 8px",
                                        "fontSize": "11px",
                                        "fontWeight": "600",
                                        "letterSpacing": "0.3px"
                                    }),
                                html.Strong(description, 
                                    className="expense-title",
                                    style={
                                        "fontSize": "14px",
                                        "color": COLORS['dark'],
                                        "letterSpacing": "0.2px"
                                    }),
                            ], style={"display": "flex", "alignItems": "center"}),
                            html.Small(f"Due: {due_date_display}", 
                                className='text-muted d-block mt-1',
                                style={"fontSize": "12px", "opacity": "0.8"})
                        ], style={'flex': 1}),
                        
                        # Middle section with amount
                        html.Div([
                            html.Span(f"£{amount:.2f}", 
                                className='h5 mb-0 font-weight-bold', 
                                style={
                                    "color": COLORS['primary'],
                                    "fontSize": "16px",
                                    "fontWeight": "600"
                                }),
                            html.Small(
                                "Monthly" if recurring else "One-time", 
                                className='d-block text-muted mt-1',
                                style={"fontSize": "11px", "opacity": "0.8"}
                            )
                        ], style={"textAlign": "right", "marginRight": "15px"}),
                        
                        # Delete button with improved styling
                        html.Button(
                            "✕", # Simple X instead of text
                            id={'type': 'delete-expense', 'index': expense_id},
                            className="btn btn-sm",
                            title="Delete this expense",
                            style={
                                'borderRadius': '50%',
                                'fontSize': '12px',
                                'fontWeight': '700',
                                'color': COLORS['muted'],
                                'backgroundColor': 'transparent',
                                'border': 'none',
                                'width': '28px',
                                'height': '28px',
                                'display': 'flex',
                                'alignItems': 'center',
                                'justifyContent': 'center',
                                'padding': '0',
                                'transition': 'all 0.2s',
                                'cursor': 'pointer'
                            }
                        ),
                    ], style={
                        'display': 'flex', 
                        'justifyContent': 'space-between', 
                        'alignItems': 'center'
                    })
                ], style={"padding": "12px 15px"})
            ], className="mb-2 expense-card", style={
                "boxShadow": "0 1px 3px rgba(0,0,0,0.08)",
                "border": f"1px solid {COLORS['light']}",
                "borderRadius": "6px",
                "transition": "transform 0.2s, box-shadow 0.2s",
                "overflow": "hidden"
            })
            
            expense_items.append(item)
            
        except Exception as e:
            print(f"Error rendering expense: {str(e)}")
    
    return expense_items

# Update expense lists
@callback(
    Output('expense-list-container', 'children'),
    Output('total-expense-badge', 'children'),
    Input('expense-data-filtered', 'data'),
    Input('active-tab-store', 'data')
)
def update_expense_lists(filtered_data, active_tab):
    if not filtered_data:
        return (
            html.P("No expenses found.", className="text-muted text-center py-3"),
            "Total: £0.00"
        )
    
    # If no tab is selected
    if active_tab is None:
        return (
            html.Div([
                html.Div(
                    html.P("Select a tab to view expenses", 
                           className="text-muted text-center py-5 border rounded"),
                    style={"marginTop": "30px"}
                )
            ]), 
            f"Total: £{filtered_data['total']:.2f}"
        )
    
    # Create expense items for the filtered expenses
    expense_items = create_expense_items(filtered_data['filtered'])
    
    # Total badge
    total_badge = f"Total: £{filtered_data['total']:.2f}"
    
    return expense_items, total_badge

# Update category chart
@callback(
    Output('expense-category-chart', 'children'),
    Input('expenses-store', 'data')
)
def update_category_chart(expenses_data):
    if not expenses_data or len(expenses_data) == 0:
        return html.P("Add expenses to see category breakdown.", className="text-muted text-center py-3")
    
    try:
        # Group expenses by category
        categories = {}
        for exp in expenses_data:
            cat = exp.get('category', 'Other')
            amount = exp.get('amount', 0)
            categories[cat] = categories.get(cat, 0) + amount
        
        # Create DataFrame
        df = pd.DataFrame([(k, v) for k, v in categories.items()], columns=['Category', 'Amount'])
        df = df.sort_values('Amount', ascending=False)
        
        # Create pie chart
        fig = px.pie(
            df,
            values='Amount',
            names='Category',
            hole=0.5,
            color_discrete_sequence=BLUE_PALETTE  # Use blue palette
        )
        
        # Update layout
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            height=300,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15,
                xanchor="center",
                x=0.5,
                font=dict(size=12, color=COLORS['dark'])  # Professional font
            ),
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
            uniformtext_minsize=12,
            uniformtext_mode='hide'
        )
        
        # Add center annotations
        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hoverinfo="label+percent+value",
            textfont_size=12
        )
        
        total = df['Amount'].sum()
        fig.add_annotation(
            text=f"£{total:.0f}",
            font=dict(size=18, color=COLORS['dark'], family="Arial, sans-serif"),
            showarrow=False,
            x=0.5,
            y=0.5
        )
        fig.add_annotation(
            text="Total Expenses",
            font=dict(size=12, color=COLORS['muted'], family="Arial, sans-serif"),
            showarrow=False,
            x=0.5,
            y=0.44
        )
        
        return dcc.Graph(figure=fig, config={'displayModeBar': False})
    
    except Exception as e:
        print(f"Error in category chart: {e}")
        return html.P("Error displaying category chart.", className="text-danger text-center py-3")

# Recurring vs Non-recurring chart
@callback(
    Output('recurring-analysis-chart', 'children'),
    Input('expense-data-filtered', 'data')
)
def update_recurring_analysis(data):
    if not data:
        return html.P("Add expenses to see recurring vs. one-time breakdown.", className="text-muted text-center py-3")
    
    # Get totals
    recurring_total = data.get('total_recurring', 0)
    non_recurring_total = data.get('total_non_recurring', 0)
    
    # Skip if no data
    if recurring_total == 0 and non_recurring_total == 0:
        return html.P("No expense amounts to display.", className="text-muted text-center py-3")
    
    # Create pie chart
    labels = ['Monthly Recurring', 'One-time']
    values = [recurring_total, non_recurring_total]
    
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(
            colors=BLUE_PALETTE[:2],  # Use two shades of blue
            line=dict(color='#FFFFFF', width=1)
        ),
        textinfo='label+percent',
        hoverinfo="label+percent+value",
        textfont=dict(size=12, color=COLORS['dark'])
    ))
    
    # Add center text
    total = recurring_total + non_recurring_total
    fig.add_annotation(
        x=0.5,
        y=0.5,
        text=f"£{total:.0f}",
        font=dict(size=18, color=COLORS['dark'], family="Arial, sans-serif"),
        showarrow=False
    )
    
    fig.add_annotation(
        x=0.5,
        y=0.42,
        text="Total",
        font=dict(size=12, color=COLORS['muted'], family="Arial, sans-serif"),
        showarrow=False
    )
    
    # Update layout
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=350,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(size=12, color=COLORS['dark'])
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

# Callback for monthly overview chart with improved design
@callback(
    Output('monthly-overview-chart', 'children'),
    Input('expenses-store', 'data'),
    Input('total-income-store', 'data'),
    Input('savings-target-store', 'data')
)
def update_monthly_overview(expenses_data, income, savings_target):
    # Handle missing data scenarios
    if not expenses_data:
        expenses_data = []
    
    income = income or 0
    savings_target = savings_target or 0
    
    # Calculate with error handling
    try:
        total_expenses = sum(e.get('amount', 0) for e in expenses_data)
        remaining = max(0, income - total_expenses)  # Ensure not negative
        discretionary = max(0, remaining - savings_target)
    except Exception as e:
        print(f"Error in monthly overview calculations: {e}")
        total_expenses = 0
        remaining = 0
        discretionary = 0
    
    # Create data for the chart
    data = {
        'Category': ['Expenses', 'Savings', 'Remaining'],
        'Amount': [total_expenses, savings_target, discretionary]
    }
    
    df = pd.DataFrame(data)
    
    # Use blue color palette
    colors = ['#2C3E50', '#3498DB', '#85C1E9']  # Dark to light blues
    
    # Use a more professional layout
    fig = go.Figure()
    
    # Add bars
    for i, (cat, amount) in enumerate(zip(df['Category'], df['Amount'])):
        fig.add_trace(go.Bar(
            x=[cat],
            y=[amount],
            name=cat,
            text=[f"£{amount:.2f}"],
            textposition='auto',
            marker_color=colors[i],
            hoverinfo="text",
            hovertext=f"{cat}: £{amount:.2f}"
        ))
    
    # Update layout for a more professional look
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        height=300,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=COLORS['light'],
            zeroline=False,
            showline=False,
            showticklabels=False
        ),
        bargap=0.4
    )
    
    # Add a total income annotation
    fig.add_annotation(
        x=0.5,
        y=1.1,
        text=f"Total Income: £{income:.2f}",
        showarrow=False,
        font=dict(size=12, color=COLORS['dark']),
        xref="paper",
        yref="paper"
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


# # Callback for updating savings target and showing savings summary
# Callback for updating savings target and showing savings summary
@callback(
    Output('savings-target-store', 'data'),
    Output('savings-summary', 'children'),
    Input('update-savings-goal', 'n_clicks'),
    State('savings-goal-input', 'value'),
    State('salary-store', 'data'),
    State('expenses-store', 'data'),
    prevent_initial_call=True
)
def update_savings_target(n, value, total_income, expenses_data):
    if not n or value is None:
        raise PreventUpdate

    value = float(value)
    
    # Calculate total expenses
    total_expenses = sum(e.get('amount', 0) for e in (expenses_data or []))
    
    # Calculate remaining income after expenses
    remaining = (total_income or 0) - total_expenses

    # Calculate savings percent
    savings_percent = (value / remaining * 100) if remaining > 0 else 0
    
    # Determine if savings goal is realistic with professional styling
    if remaining <= 0:
        status = COLORS['danger']
        status_icon = html.I(className="fas fa-exclamation-triangle")
        message = "You need to reduce expenses before setting a savings goal."
    elif value > remaining:
        status = COLORS['warning']
        status_icon = html.I(className="fas fa-exclamation-circle")
        message = "Your savings goal exceeds your remaining income."
    elif savings_percent > 50:
        status = COLORS['warning']
        status_icon = html.I(className="fas fa-chart-line")
        message = f"Your savings target is {savings_percent:.1f}% of remaining income."
    else:
        status = COLORS['success']
        status_icon = html.I(className="fas fa-check-circle")
        message = f"Your savings target is {savings_percent:.1f}% of remaining income."
        
    summary = html.Div([
        html.Div([
            html.Span(status_icon, className="me-2"),
            html.Span(message)
        ], style={"color": status, "fontWeight": "500", "marginBottom": "12px"}),
        
        html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div("Target:", className="text-muted small"),
                    html.Div(f"£{value:.2f}", className="h5 mb-0")
                ], width=6),
                dbc.Col([
                    html.Div("Available:", className="text-muted small"),
                    html.Div(f"£{remaining:.2f}", 
                             className="h5 mb-0", 
                             style={"color": COLORS['success'] if remaining >= value else COLORS['danger']})
                ], width=6)
            ]),
            html.Div([
                dbc.Progress(
                    value=min(100, (value/remaining*100) if remaining > 0 else 100),
                    color=COLORS['success'] if remaining >= value else COLORS['danger'],
                    className="mt-3",
                    style={"height": "6px", "borderRadius": "3px"}
                )
            ])
        ])
    ])
    
    return value, summary

@callback(
    Output('expenses-store', 'data', allow_duplicate=True),
    Input({'type': 'delete-expense', 'index': ALL}, 'n_clicks'),
    State('expenses-store', 'data'),
    prevent_initial_call=True
)
def delete_expense(clicks, expenses_data):
    # Check if any buttons were clicked
    if not ctx.triggered or not any(c for c in clicks if c):
        raise PreventUpdate
        
    # Find which button was clicked
    trigger = ctx.triggered[0]
    if not trigger['prop_id']:
        raise PreventUpdate
        
    # Extract the expense ID from the triggered component
    try:
        expense_id = json.loads(trigger['prop_id'].split('.')[0])['index']
        
        # Create a new list without the deleted expense
        updated_expenses = [exp for exp in expenses_data if exp.get('id') != expense_id]
        
        return updated_expenses
    except Exception as e:
        print(f"Error in delete_expense: {e}")
        # Return unmodified data if there's an error
        return expenses_data

import json

def update_transaction_store(expenses_data):
    """
    Filters non-recurring expenses and updates the Transaction-store.

    Args:
        expenses_data (list): The current list of expenses from the expenses-store.

    Returns:
        list: A list of non-recurring transactions to store in the Transaction-store.
    """
    if not expenses_data:
        return []

    # Filter non-recurring expenses
    non_recurring_transactions = [
        {
            'id': exp.get('id'),
            'description': exp.get('description'),
            'amount': exp.get('amount'),
            'category': exp.get('category'),
            'date_added': exp.get('date_added'),
            'due_date': exp.get('due_date'),
        }
        for exp in expenses_data if not exp.get('recurring', False)
    ]

    return non_recurring_transactions

@callback(
    Output('Transaction-store', 'data'),
    Input('expenses-store', 'data'),
    prevent_initial_call=True
)
def sync_transaction_store(expenses_data):
    # Use the helper function to filter non-recurring transactions
    updated_transactions = update_transaction_store(expenses_data)

    return updated_transactions

@callback(
    Output('active-tab-store', 'data'),
    Output('tab-all-btn', 'style'),
    Output('tab-recurring-btn', 'style'),
    Output('tab-non-recurring-btn', 'style'),
    Input('tab-all-btn', 'n_clicks'),
    Input('tab-recurring-btn', 'n_clicks'),
    Input('tab-non-recurring-btn', 'n_clicks'),
    State('active-tab-store', 'data'),
    prevent_initial_call=True
)
def update_active_tab(all_clicks, recurring_clicks, non_recurring_clicks, current_tab):
    # Default styles - all light gray when none are active
    all_style = {
        "backgroundColor": COLORS['light'],
        "color": COLORS['dark'],
        "border": "none",
        "borderRadius": "6px 0 0 6px",
        "padding": "10px 15px"
    }
    
    recurring_style = {
        "backgroundColor": COLORS['light'],
        "color": COLORS['dark'],
        "border": "none",
        "borderRadius": "0",
        "padding": "10px 15px"
    }
    
    non_recurring_style = {
        "backgroundColor": COLORS['light'],
        "color": COLORS['dark'],
        "border": "none",
        "borderRadius": "0 6px 6px 0",
        "padding": "10px 15px"
    }

    new_tab = None
    
    # Get the button that was clicked
    triggered = ctx.triggered_id
    
    # Handle first load with no clicks (no tab selected)
    if not triggered:
        # All tabs are light gray when none are active
        return None, all_style, recurring_style, non_recurring_style
    
    # Set active style for the clicked tab or toggle off if clicked again
    if triggered == 'tab-all-btn':
        # If tab is already active, deactivate it
        if current_tab == 'tab-all':
            new_tab = None  # Set to None to indicate no active tab
        else:
            # Otherwise, activate it
            all_style["backgroundColor"] = COLORS['primary']
            all_style["color"] = COLORS['white']
            new_tab = 'tab-all'
    elif triggered == 'tab-recurring-btn':
        if current_tab == 'tab-recurring':
            new_tab = None  # Set to None to indicate no active tab
        else:
            recurring_style["backgroundColor"] = COLORS['primary']
            recurring_style["color"] = COLORS['white']
            new_tab = 'tab-recurring'
    elif triggered == 'tab-non-recurring-btn':
        if current_tab == 'tab-non-recurring':
            new_tab = None  # Set to None to indicate no active tab
        else:
            non_recurring_style["backgroundColor"] = COLORS['primary']
            non_recurring_style["color"] = COLORS['white']
            new_tab = 'tab-non-recurring'
    else:
        new_tab = current_tab
        
    # Set active tab style only if there is an active tab
    if new_tab == 'tab-all':
        all_style["backgroundColor"] = COLORS['primary']
        all_style["color"] = COLORS['white']
    elif new_tab == 'tab-recurring':
        recurring_style["backgroundColor"] = COLORS['primary']
        recurring_style["color"] = COLORS['white']
    elif new_tab == 'tab-non-recurring':
        non_recurring_style["backgroundColor"] = COLORS['primary']
        non_recurring_style["color"] = COLORS['white']
    # If new_tab is None, all styles remain light gray (default)
    
    return new_tab, all_style, recurring_style, non_recurring_style