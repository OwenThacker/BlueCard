# expenses.py - Dash Page for Expense Management with Professional Design

from dash import html, dcc, Input, Output, State, callback, ctx, ALL, clientside_callback
import dash_bootstrap_components as dbc
import datetime
from datetime import date
import dash
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.exceptions import PreventUpdate
import uuid

from utils.db import connect_db
import psycopg2
import psycopg2.extras
from psycopg2.extras import RealDictCursor, Json  # Add Json here
import json

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


# Database connection function
def get_db_connection():
    """Connect to the PostgreSQL database"""
    try:
        conn = connect_db()
        return conn
    except Exception as e:
        # print(f"Error connecting to database: {e}")
        return None

def get_user_data(user_id):
    """Get user data from database or return default for guest users"""

    conn = get_db_connection()
    if not conn:
        return {}
    print('printing user_id', user_id)

    # Extract the actual user ID value from the dictionary
    if isinstance(user_id, dict):
        actual_user_id = user_id.get('user_id')
        print(f'Extracted user_id value: {actual_user_id}')
    else:
        actual_user_id = user_id

    user_data = {}
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get user info
            cur.execute("SELECT * FROM users WHERE user_id = %s", (actual_user_id,))
            user = cur.fetchone()
            if not user:
                print(f"User {actual_user_id} not found in database")
                return {}

            user_data['user_info'] = dict(user)

            # Get income data
            cur.execute("SELECT * FROM income WHERE user_id = %s", (actual_user_id,))
            user_data['income'] = [dict(row) for row in cur.fetchall()]

            # Get expense data
            cur.execute("SELECT * FROM expense WHERE user_id = %s", (actual_user_id,))
            user_data['expenses'] = [dict(row) for row in cur.fetchall()]

            # Get savings goals
            cur.execute("SELECT * FROM saving_goals WHERE user_id = %s", (actual_user_id,))
            user_data['savings_goals'] = [dict(row) for row in cur.fetchall()]

            # Get transactions
            cur.execute(
                "SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC LIMIT 50",
                (actual_user_id,)
            )
            user_data['transactions'] = [dict(row) for row in cur.fetchall()]

            # Get savings target
            cur.execute("SELECT amount FROM savings_target WHERE user_id = %s", (actual_user_id,))
            savings_target = cur.fetchone()
            if savings_target:
                user_data['savings_target'] = savings_target['amount']
            else:
                user_data['savings_target'] = 0

            # Get dashboard settings
            cur.execute("SELECT dashboard_settings FROM users WHERE user_id = %s", (actual_user_id,))
            dashboard_settings = cur.fetchone()
            
            # Initialize with empty component list
            user_data['dashboard_settings'] = {'components': []}
            
            if dashboard_settings and dashboard_settings['dashboard_settings']:
                # Parse JSON string to object
                try:
                    if isinstance(dashboard_settings['dashboard_settings'], str):
                        parsed_settings = json.loads(dashboard_settings['dashboard_settings'])
                    else:
                        parsed_settings = dashboard_settings['dashboard_settings']
                        
                    # Ensure the settings have the expected structure
                    if isinstance(parsed_settings, dict) and 'components' in parsed_settings:
                        user_data['dashboard_settings'] = parsed_settings
                        print(f"Successfully loaded dashboard settings for user {actual_user_id}")
                        print(f"Found {len(parsed_settings.get('components', []))} components")
                    else:
                        print(f"Dashboard settings missing components for user {actual_user_id}")
                        user_data['dashboard_settings'] = {'components': []}
                except Exception as e:
                    print(f"Error parsing dashboard settings: {e}")
                    user_data['dashboard_settings'] = {'components': []}
            else:
                print(f"No dashboard settings found for user {actual_user_id}")

    except Exception as e:
         print(f"Error fetching user data: {e}")
    finally:
        conn.close()

    return user_data

# Load user data when page loads or user ID changes
@callback(
    Output("user-data-store", "data", allow_duplicate=True),
    [Input("user-id", "data"),
     Input("url", "pathname")],
    prevent_initial_call=True
)
def load_user_data(user_id, pathname):
    """Load user data from the database based on user ID"""
    
    if user_id is None:
        # Default to Guest if no user ID is found
        return get_user_data('Guest')
    print('Loading Data in Expense.py')
    print(user_id)
    # Get user data from database
    user_data = get_user_data(user_id)
    
    return user_data

# Check authentication (optional)
@callback(
    Output("chat-dashboard-container", "style", allow_duplicate=True),
    [Input("user-data-store", "data"),
     Input("url", "pathname")],
     prevent_initial_call=True
)
def check_authentication(user_data, pathname):
    """Check if user is authenticated and should access this page"""
    if pathname == '/expenses':
        # Check if user is authenticated or if guest access is allowed
        if not user_data:
            # Hide the container if no user data
            return {"display": "none"}
        
        # If you want to restrict certain pages to logged-in users only
        # Uncomment this if you want to restrict guest access
        if user_data.get('user_info', {}).get('id') == 'Guest':
            return {"display": "none"}
    
    return {"display": "block"}


# Layout for the Expenses Page
layout = html.Div([
    # Header - Keep as is per request
    # Logo and Title
    # html.Div([

        # Session and Routing
        dcc.Store(id='session-data-store', storage_type='local'),
        dcc.Store(id='user-id', storage_type='local'),  # Make sure this is included
        dcc.Location(id='url', refresh=False),
        dcc.Store(id="app-loaded-store", data=False),

        html.Img(src="/assets/Logo_slogan.PNG", className="dashboard-logo"),
        

    #     # Navigation - Keep as is per request
    #     html.Nav([
    #         html.Button([
    #             html.Span("BlueCard Finance", className="mobile-nav-toggle-text"),
    #             html.Span("≡")
    #         ], className="mobile-nav-toggle", id="mobile-nav-toggle"),

    #         html.Ul([
    #             html.Li(html.A([html.Span(className="nav-icon"), "Home"], href="/", className="nav-link"), className="nav-item"),
    #             html.Li(html.A([html.Span(className="nav-icon"), "Dashboard"], href="/dashboard", className="nav-link"), className="nav-item"),
    #             html.Li(html.A([html.Span(className="nav-icon"), "Income"], href="/income", className="nav-link"), className="nav-item"),
    #             html.Li(html.A([html.Span(className="nav-icon"), "Expenses"], href="/expenses", className="nav-link active"), className="nav-item"),
    #             html.Li([html.A([html.Span(className="nav-icon"), "Savings Analysis"], href="/savings", className="nav-link")], className="nav-item"),
    #             html.Li(html.A([html.Span(className="nav-icon"), "Settings"], href="/settings", className="nav-link"), className="nav-item")
    #         ], className="nav-menu", id="nav-menu"),
    #         # User account area (right side of navbar)
    #             html.Div([
    #                 # User profile dropdown
    #                 html.Div([
    #                     html.Button([
    #                         html.I(className="fas fa-user-circle", style={'fontSize': '24px'}),
    #                     ], id="user-dropdown-button", className="user-dropdown-button"),
                        
    #                     # Dropdown menu
    #                     html.Div([
    #                         html.Div(id="user-email-display", className="user-email"),
    #                         html.Hr(style={'margin': '8px 0'}),
    #                         html.A("Profile", href="/profile", className="dropdown-item"),
    #                         html.A("Logout", id="logout-link", href="/logout", className="dropdown-item")
    #                     ], id="user-dropdown-content", className="user-dropdown-content")
    #                 ], className="user-dropdown"),
    #             ], id="user-account-container", className="user-account-container"),
    #     ], className="nav-bar"),
    # ], className="header-container"),

    # # Optional Breadcrumb with improved styling
    # html.Ul([
    #     html.Li([
    #         html.A("Home", href="/", className="breadcrumb-link")
    #     ], className="breadcrumb-item"),
    #     html.Li("Expenses", className="breadcrumb-item breadcrumb-current")
    # ], className="breadcrumb", style={'backgroundColor': COLORS['light'], 'borderRadius': '8px'}),

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
                                            className="mb-0 my-custom-radio",
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
                    dbc.CardHeader(html.H5("Account For Monthly Savings Target", className="card-title m-0"), style=HEADER_STYLE),
                    dbc.CardBody([
                        dbc.Label("Monthly Savings Goal", className="text-muted"),
                        dbc.InputGroup([
                            dbc.InputGroupText("£", style={'backgroundColor': COLORS['primary'], 'color': COLORS['white'], 'borderRadius': '6px 0 0 6px'}),
                            dbc.Input(id='savings-goal-input', type='number', min=0, step=0.01, placeholder="0.00",
                                     className='mb-2', style={'borderRadius': '0 6px 6px 0'}),
                        ]),
                        dbc.Button("Update Monthly Savings Goal", id='update-savings-goal', 
                                  style={'backgroundColor': COLORS['accent'], 'border': 'none', 'borderRadius': '6px'},
                                  className="w-100 mt-2"),
                        html.Div(id='savings-summary', className='mt-3 p-3 rounded', 
                                style={"backgroundColor": COLORS['light'], 'borderRadius': '6px'})
                    ])
                ], style=CARD_STYLE)
            ], md=4)
        ])
    ], className="main-content-container p-3"),

    # Stores from chat
    dcc.Store(id="session-data-store", storage_type="local"),
    dcc.Store(id='user-id-store', storage_type='local'),
    dcc.Store(id='user-data-store', storage_type='session'),

    # Interval
    # dcc.Interval(
    #     id='interval-component',
    #     interval=1000,  # in milliseconds (1 second)
    #     n_intervals=0   # starting value
    # ),

    # Local storage for expenses and other variables
    dcc.Store(id='expenses-store', storage_type='local'),
    dcc.Store(id='salary-store', storage_type='local'),
    dcc.Store(id='savings-target-store', storage_type='local'),
    dcc.Store(id='total-income-store', storage_type='local'),  # Add this to access income data
    dcc.Store(id='Transaction-store', storage_type='local'), # Add this to access transaction data
    dcc.Store(id='active-tab-store', storage_type='memory', data=None),
    

    # Will use PostgreSQL instead of these stores
    dcc.Store(id='active-tab-store', storage_type='memory', data=None),
    dcc.Store(id='expense-data-filtered', storage_type='memory'),
    
    # Placeholder for the current user ID (to be implemented with authentication)
    dcc.Store(id='current-user-store', storage_type='memory', data='user1'),
    
    # Interval for initialization (runs once)
    dcc.Interval(id='interval-component', interval=1000, max_intervals=0),

])

# Initialize Income data
@callback(
    Output("total-income-store", "data", allow_duplicate=True),
    [Input("user-data-store", "data"),
     Input("interval-component", "n_intervals"),
     Input("app-loaded-store", "data")],  # Add this input
    prevent_initial_call=True
)
def initialize_income_data(user_data, n_intervals, app_loaded):
    """Initialize income data from user data"""
    if not user_data:
        return []
    
    # Determine what triggered the callback
    triggered_id = ctx.triggered_id
    
    # If triggered by app load but no user data, prevent update
    if triggered_id == "app-loaded-store" and not user_data:
        raise PreventUpdate
    
    # Load income data from user_data
    total_income = user_data.get('income', [])
    
    return total_income

# Similarly modify your initialize_expense_data callback
@callback(
    [Output("expenses-store", "data"),
     Output("savings-target-store", "data")],
    [Input("user-data-store", "data"),
     Input("interval-component", "n_intervals"),
     Input("app-loaded-store", "data")],  # Add this input
    prevent_initial_call=True
)
def initialize_expense_data(user_data, n_intervals, app_loaded):
    """Initialize expense data from user data"""
    if not user_data:
        return [], 0
    
    # Determine what triggered the callback
    triggered_id = ctx.triggered_id
    
    # If triggered by app load but no user data, prevent update
    if triggered_id == "app-loaded-store" and not user_data:
        raise PreventUpdate
    
    # Extract expenses and return
    expenses = user_data.get('expenses', [])
    transactions = user_data.get('transactions', [])
    
    # Combine monthly expenses and one-time expenses (transactions)
    combined_expenses = []
    
    # Add monthly expenses
    for expense in expenses:
        expense_item = {
            'id': expense.get('expense_id', str(uuid.uuid4())),
            'description': expense.get('description', ''),
            'amount': expense.get('amount', 0),
            'category': expense.get('category', 'Other'),
            'due_date': expense.get('due_date', datetime.date.today().isoformat()),
            'recurring': True  # Monthly expenses are recurring
        }
        combined_expenses.append(expense_item)
    
    # Add one-time expenses from transactions
    for transaction in transactions:
        # Only add expense transactions (not income)
        if transaction.get('type', '') == 'expense':
            transaction_item = {
                'id': transaction.get('transaction_id', str(uuid.uuid4())),
                'description': transaction.get('description', ''),
                'amount': transaction.get('amount', 0),
                'category': transaction.get('category', 'Other'),
                'due_date': transaction.get('date', datetime.date.today().isoformat()),
                'recurring': False  # Transactions are one-time
            }
            combined_expenses.append(transaction_item)
    
    # Get savings target
    savings_target = user_data.get('savings_target', 0)
    
    return combined_expenses, savings_target

# Add expense callback
@callback(
    [Output("expenses-store", "data", allow_duplicate=True),
     Output("desc-input", "value"),
     Output("amount-input", "value"),
     Output("category-input", "value"),
     Output("due-date-input", "date"),
     Output("recurring-input", "value")],
    [Input("submit-expense", "n_clicks")],
    [State("desc-input", "value"),
     State("amount-input", "value"),
     State("category-input", "value"),
     State("due-date-input", "date"),
     State("recurring-input", "value"),
     State("expenses-store", "data"),
     State("user-id", "data")],
    prevent_initial_call=True
)
def add_expense(n_clicks, desc, amount, category, due_date, recurring, expenses, user_id):
    """Add a new expense to the database and update the store"""
    if n_clicks is None or not desc or not amount or not category:
        raise PreventUpdate
    
    # Extract the actual user ID value from the dictionary
    if isinstance(user_id, dict):
        actual_user_id = user_id.get('user_id')
        print(f'Extracted user_id value: {actual_user_id}')
    else:
        actual_user_id = user_id

    # Create a new expense record
    expense_id = str(uuid.uuid4())
    new_expense = {
        'id': expense_id,
        'description': desc,
        'amount': float(amount),
        'category': category,
        'due_date': due_date,
        'recurring': recurring
    }

    # Print debug info before DB insert
    print(f"Adding new expense:")
    print(f"  Expense ID: {expense_id}")
    print(f"  Description: {desc}")
    print(f"  Amount: {amount}")
    print(f"  Category: {category}")
    print(f"  Due Date: {due_date}")
    print(f"  Recurring: {recurring}")
    print(f"  User ID: {user_id}")

    # Save to database
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                if recurring:
                    # Insert into the expense table for monthly recurring expenses
                    print("  -> Inserting into 'expense' table")
                    cur.execute(
                        """
                        INSERT INTO expense (expense_id, user_id, amount, category, description, due_date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (expense_id, actual_user_id, float(amount), category, desc, due_date)
                    )
                else:
                    # Insert into the transactions table for one-time expenses
                    print("  -> Inserting into 'transactions' table")
                    cur.execute(
                        """
                        INSERT INTO transactions (transaction_id, user_id, amount, type, category, description, date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """,
                        (expense_id, actual_user_id, float(amount), 'expense', category, desc, due_date)
                    )
                conn.commit()
                print("  -> Insert committed.")
        except Exception as e:
            print(f"Error adding expense: {e}")
        finally:
            conn.close()

    # Update the local store
    if expenses:
        expenses.append(new_expense)
    else:
        expenses = [new_expense]

    # Clear form fields
    return expenses, "", None, None, datetime.date.today(), False

# Delete expense callback
@callback(
    Output("expenses-store", "data", allow_duplicate=True),
    [Input({"type": "delete-expense", "index": ALL}, "n_clicks")],
    [State("expenses-store", "data"),
     State("user-id", "data")],
    prevent_initial_call=True
)
def delete_expense(n_clicks_list, expenses, user_id):
    """Delete an expense from the database and update the store"""
    # Extract the actual user ID value from the dictionary
    if isinstance(user_id, dict):
        actual_user_id = user_id.get('user_id')
        print(f'Extracted user_id value: {actual_user_id}')
    else:
        actual_user_id = user_id

    if not any(n_clicks_list) or not expenses:
        raise PreventUpdate
    
    # Get the index of the button that was clicked
    triggered_id = ctx.triggered_id
    if triggered_id is None:
        raise PreventUpdate
    
    # Extract the index from the triggered ID
    expense_index = triggered_id.get('index')

    print('Removing Expense at index:', expense_index)
    
    # Find the expense to delete
    if expense_index < len(expenses):
        expense_to_delete = expenses[expense_index]
        expense_id = expense_to_delete.get('id')
        is_recurring = expense_to_delete.get('recurring', False)
        
        # Delete from database
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    if is_recurring:
                        # Delete from expense table
                        cur.execute(
                            "DELETE FROM expense WHERE expense_id = %s AND user_id = %s",
                            (expense_id, actual_user_id)
                        )
                    else:
                        # Delete from transactions table
                        cur.execute(
                            "DELETE FROM transactions WHERE transaction_id = %s AND user_id = %s",
                            (expense_id, actual_user_id)
                        )
                    conn.commit()
            except Exception as e:
                print(f"Error deleting expense: {e}")
            finally:
                conn.close()
        
        # Update the local store
        expenses.pop(expense_index)
    
    return expenses

# Update savings target callback
@callback(
    Output("savings-target-store", "data", allow_duplicate=True),
    Output("user-data-store", "data", allow_duplicate=True),
    [Input("update-savings-goal", "n_clicks"),
     Input("user-data-store", "data")],
    [State("savings-goal-input", "value"),
     State("user-id", "data")],
    prevent_initial_call=True
)
def update_savings_target(n_clicks, user_data, savings_goal, user_id):
    """Update the savings target in the database and store"""
    # Extract the actual user ID value from the dictionary
    if isinstance(user_id, dict):
        actual_user_id = user_id.get('user_id')
        print(f'Extracted user_id value: {actual_user_id}')
    else:
        actual_user_id = user_id

    if n_clicks is None or savings_goal is None:
        raise PreventUpdate
    
    today = date.today()

    savings_amount = float(savings_goal)

    user_data['savings_target'] = savings_amount
    
    # Update database
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Check if a record already exists
                cur.execute("SELECT amount FROM savings_target WHERE user_id = %s", (actual_user_id,))
                existing = cur.fetchone()
                
                if existing:
                    # Update existing record
                    cur.execute(
                        "UPDATE savings_target SET amount = %s, date = %s WHERE user_id = %s",
                        (savings_amount, today, actual_user_id)
                    )
                else:
                    # Insert new record
                    cur.execute(
                        "INSERT INTO savings_target (user_id, amount, date) VALUES (%s, %s, %s)",
                        (actual_user_id, savings_amount, today)
                    )
                conn.commit()
        except Exception as e:
            print(f"Error updating savings target: {e}")
        finally:
            conn.close()
    
    return savings_amount, user_data

# Tab switching callbacks
@callback(
    [Output("tab-all-btn", "style"),
     Output("tab-recurring-btn", "style"),
     Output("tab-non-recurring-btn", "style"),
     Output("active-tab-store", "data")],
    [Input("tab-all-btn", "n_clicks"),
     Input("tab-recurring-btn", "n_clicks"),
     Input("tab-non-recurring-btn", "n_clicks")],
    [State("active-tab-store", "data")],
    prevent_initial_call=True
)
def switch_expense_tab(all_clicks, recurring_clicks, non_recurring_clicks, active_tab):
    """Switch between expense tabs"""
    ctx_triggered = ctx.triggered_id
    
    if ctx_triggered is None:
        # Default to 'all' if no tab is active
        active_tab = active_tab or 'all'
    else:
        # Set active tab based on which button was clicked
        if ctx_triggered == "tab-all-btn":
            active_tab = 'all'
        elif ctx_triggered == "tab-recurring-btn":
            active_tab = 'recurring'
        elif ctx_triggered == "tab-non-recurring-btn":
            active_tab = 'non-recurring'
    
    # Base styles
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
    
    # Update style for active tab
    if active_tab == 'all':
        all_style["backgroundColor"] = COLORS['primary']
        all_style["color"] = COLORS['white']
    elif active_tab == 'recurring':
        recurring_style["backgroundColor"] = COLORS['primary']
        recurring_style["color"] = COLORS['white']
    elif active_tab == 'non-recurring':
        non_recurring_style["backgroundColor"] = COLORS['primary']
        non_recurring_style["color"] = COLORS['white']
    
    return all_style, recurring_style, non_recurring_style, active_tab

# Filter expenses based on active tab
@callback(
    Output("expense-data-filtered", "data"),
    [Input("active-tab-store", "data"),
     Input("expenses-store", "data")],
    prevent_initial_call=True
)
def filter_expenses(active_tab, expenses):
    """Filter expenses based on the active tab"""
    if not expenses:
        return []
    
    # Default to all expenses
    if active_tab is None or active_tab == 'all':
        return expenses
    
    # Filter by recurring status
    if active_tab == 'recurring':
        return [exp for exp in expenses if exp.get('recurring', False)]
    elif active_tab == 'non-recurring':
        return [exp for exp in expenses if not exp.get('recurring', False)]
    
    # Default case: return all expenses
    return expenses

# Generate expense list
@callback(
    Output("expense-list-container", "children"),
    [Input("expense-data-filtered", "data")],
    prevent_initial_call=True
)
def generate_expense_list(expenses):
    """Generate the expense list based on filtered data"""
    if not expenses:
        return html.Div("No expenses to display.", className="text-muted p-3")
    
    # Create a list of expense items
    expense_items = []
    
    # Get current date for comparison
    today = datetime.date.today()
    
    for i, expense in enumerate(expenses):
        # Get expense details
        desc = expense.get('description', 'N/A')
        amount = expense.get('amount', 0)
        category = expense.get('category', 'Other')
        due_date = expense.get('due_date', today.isoformat())
        recurring = expense.get('recurring', False)
        
        # Format due date
        try:
            if isinstance(due_date, str):
                due_date_obj = datetime.datetime.fromisoformat(due_date).date()
            else:
                due_date_obj = due_date
                
            # If expense is recurring and due date has passed, calculate next due date
            if recurring and due_date_obj < today:
                # Keep adding 30 days until the due date is in the future
                while due_date_obj < today:
                    due_date_obj = due_date_obj + datetime.timedelta(days=30)
                
                # Format the adjusted date for display
                due_date_str = due_date_obj.strftime("%b %d, %Y")
            else:
                # Format the original date for display
                due_date_str = due_date_obj.strftime("%b %d, %Y")
        except:
            due_date_str = "Unknown"
        
        # Create expense list item
        expense_item = html.Div([
            dbc.Row([
                # Description and category
                dbc.Col([
                    html.Div([
                        html.H6(desc, className="mb-0"),
                        html.Span(category, className="badge badge-light",
                                 style={
                                     "backgroundColor": CATEGORY_COLORS.get(category, COLORS['muted']),
                                     "color": COLORS['white'],
                                     "fontSize": "12px",
                                     "borderRadius": "30px",
                                     "padding": "4px 8px",
                                     "marginTop": "4px"
                                 })
                    ])
                ], width=6),
                # Amount
                dbc.Col([
                    html.Div([
                        html.H6(f"£{amount:.2f}", className="mb-0 text-end",
                               style={"color": COLORS['accent'], "fontWeight": "bold"})
                    ])
                ], width=2),
                # Due date and recurring status
                dbc.Col([
                    html.Div([
                        html.P(due_date_str, className="mb-0 text-muted text-end",
                              style={"fontSize": "12px"}),
                        html.P(
                            "Monthly" if recurring else "One-time",
                            className="mb-0 text-end",
                            style={
                                "fontSize": "11px",
                                "color": COLORS['success'] if recurring else COLORS['warning']
                            }
                        )
                    ])
                ], width=2),
                # Delete button
                dbc.Col([
                    html.Button(
                        html.I(className="fas fa-trash"),
                        id={"type": "delete-expense", "index": i},
                        className="btn btn-link btn-sm",
                        style={"fontSize": "14px", "padding": "4px"}
                    )
                ], width=2, className="text-end")
            ], className="align-items-center"),
            html.Hr(style={"margin": "10px 0", "opacity": "0.2"})
        ], className="expense-item mb-2")
        
        expense_items.append(expense_item)
    
    return html.Div(expense_items, className="expense-list")

# Update total expense badge
@callback(
    Output("total-expense-badge", "children"),
    [Input("expenses-store", "data")],
    prevent_initial_call=True
)
def update_total_expense_badge(expenses):
    """Update the total expense badge"""
    if not expenses:
        return "Total: £0.00"
    
    # Calculate total expenses
    total = sum(exp.get('amount', 0) for exp in expenses)
    
    return f"Total: £{total:.2f}"

# Update savings summary
@callback(
    Output("savings-summary", "children"),
    [Input("savings-target-store", "data"),
     Input("expenses-store", "data"),
     Input("total-income-store", "data")],
    prevent_initial_call=True
)
def update_savings_summary(savings_target, expenses, total_income):
    """Update the savings summary based on income, expenses, and savings target"""
    # Default values
    if not savings_target:
        savings_target = 0
    
    if not expenses:
        total_expenses = 0
    else:
        total_expenses = sum(exp.get('amount', 0) for exp in expenses)
    
    if not total_income:
        total_income = 0
    else:
        total_income = sum(income.get('amount', 0) for income in total_income)
    
    # Calculate remaining income after expenses
    remaining = total_income - total_expenses
    
    # Calculate if savings target can be met
    if savings_target > remaining:
        # Not enough remaining for savings target
        style = {"color": COLORS['danger']}
        message = f"You need to reduce expenses by £{(savings_target - remaining):.2f} to meet your savings goal."
    else:
        # Enough remaining for savings target
        style = {"color": COLORS['success']}
        message = f"You will have £{(remaining - savings_target):.2f} left after meeting your savings goal."
    
    return html.Div([
        html.H5(f"Monthly Budget Summary", className="mb-3"),
        html.P([
            "Income: ",
            html.Span(f"£{total_income:.2f}", style={"fontWeight": "bold"})
        ]),
        html.P([
            "Expenses: ",
            html.Span(f"£{total_expenses:.2f}", style={"fontWeight": "bold"})
        ]),
        html.P([
            "Savings Goal: ",
            html.Span(f"£{float(savings_target):.2f}", style={"fontWeight": "bold"})
        ]),
        html.Hr(style={"margin": "10px 0"}),
        html.P([
            "Remaining: ",
            html.Span(f"£{remaining:.2f}", style={"fontWeight": "bold", "color": COLORS['accent']})
        ]),
        html.P(message, style=style)
    ])

# Generate category sunburst chart
@callback(
    Output("expense-category-chart", "children"),
    [Input("expenses-store", "data")],
    prevent_initial_call=True
)
def generate_category_chart(user_data):
    """Generate professional charts for expense analysis by category and recurring status."""
    if not user_data:
        return html.P("No transaction data available.", className="text-muted")

    data = []

    # Process the data into categories and recurring status
    for item in user_data:
        status = "Recurring" if item.get('recurring', False) else "Non-Recurring"
        data.append({
            'Recurring': status,
            'Category': item.get('category', 'Other'),
            'Description': item.get('description', 'Unlabeled'),
            'Amount': item.get('amount', 0)
        })

    # Create a DataFrame from the processed data
    df = pd.DataFrame(data)
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    
    # Sophisticated blue color palette
    professional_blues = [
        "#1a365d", "#2a4a7f", "#3c64a1", "#5682c3", "#7ba0e5", 
        "#a8c0ff", "#d4e0ff", "#e8f0ff"
    ]
    
    # Create a container for both charts
    chart_container = html.Div([
        # Top section: Category distribution
        html.Div([
            # html.H6("Expense Distribution by Category", 
            #        className="chart-title mb-0",
            #        style={"fontSize": "14px", "fontWeight": "600", "color": "#2c3e50"}),
            
            dcc.Graph(
                id="category-treemap",
                figure=create_category_sunburst(df, professional_blues),
                config={'displayModeBar': False, 'responsive': True},
                style={"height": "450px"}
            )
        ], className="mb-4"),

        # Bottom section: Recurring vs Non-recurring
        html.Div([
            # html.H6("Recurring vs. Non-Recurring Expenses", 
            #        className="chart-title mb-0",
            #        style={"fontSize": "14px", "fontWeight": "600", "color": "#2c3e50"}),
                   
            dcc.Graph(
                id="recurring-bar-chart",
                figure=create_recurring_bar_chart(df, professional_blues),
                config={'displayModeBar': False, 'responsive': True},
                style={"height": "250px"}
            )
        ])

    ], className="chart-container")
    
    return chart_container

def create_category_sunburst(df, color_palette):
    """Create a professional sunburst chart showing Recurring > Category > Description."""
    # Clean and group data
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
    df = df[df['Amount'] > 0]  # Filter zero/negative amounts

    fig = px.sunburst(
        df,
        path=['Recurring', 'Category', 'Description'],
        values='Amount',
        color='Amount',
        color_continuous_scale=color_palette,
        color_continuous_midpoint=df['Amount'].median()
    )

    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{percentRoot:.1%} of total',
        textinfo='label+percent entry',
        textfont=dict(
            family="'Inter', 'Segoe UI', Arial, sans-serif",
            size=11
        ),
        insidetextorientation='auto'
    )

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white',
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        font=dict(
            family="'Inter', 'Segoe UI', Arial, sans-serif",
            color="#2c3e50"
        ),
        coloraxis_showscale=False
    )

    return fig

def create_recurring_bar_chart(df, color_palette):
    """Create a professional bar chart comparing recurring vs non-recurring expenses."""
    # Group by recurring status and category
    recurring_category = df.pivot_table(
        index='Category', 
        columns='Recurring', 
        values='Amount', 
        aggfunc='sum'
    ).fillna(0).reset_index()
    
    # Sort by total amount
    if 'Recurring' in recurring_category.columns and 'Non-Recurring' in recurring_category.columns:
        recurring_category['Total'] = recurring_category['Recurring'] + recurring_category['Non-Recurring']
    elif 'Recurring' in recurring_category.columns:
        recurring_category['Total'] = recurring_category['Recurring']
    elif 'Non-Recurring' in recurring_category.columns:
        recurring_category['Total'] = recurring_category['Non-Recurring']
    else:
        recurring_category['Total'] = 0
        
    recurring_category = recurring_category.sort_values('Total', ascending=False)
    
    # Create a horizontal grouped bar chart
    fig = go.Figure()
    
    # Add bars for recurring expenses if they exist
    if 'Recurring' in recurring_category.columns:
        fig.add_trace(go.Bar(
            y=recurring_category['Category'],
            x=recurring_category['Recurring'],
            name='Recurring',
            orientation='h',
            marker=dict(color=color_palette[1]),
            hovertemplate='<b>%{y}</b><br>Recurring: £%{x:,.2f}<extra></extra>'
        ))
    
    # Add bars for non-recurring expenses if they exist
    if 'Non-Recurring' in recurring_category.columns:
        fig.add_trace(go.Bar(
            y=recurring_category['Category'],
            x=recurring_category['Non-Recurring'],
            name='Non-Recurring',
            orientation='h',
            marker=dict(color=color_palette[5]),
            hovertemplate='<b>%{y}</b><br>Non-Recurring: £%{x:,.2f}<extra></extra>'
        ))
    
    # Update layout for professional appearance
    fig.update_layout(
        barmode='group',
        margin=dict(l=5, r=5, t=5, b=5, pad=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="'Inter', 'Segoe UI', Arial, sans-serif",
            size=12,
            color="#2c3e50"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=11)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(220,220,220,0.4)',
            showline=True,
            linewidth=1,
            linecolor='rgba(220,220,220,0.8)',
            tickformat='£,.0f'
        ),
        yaxis=dict(
            showgrid=False,
            showline=False
        ),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#1a365d",
            font_family="'Inter', 'Segoe UI', Arial, sans-serif"
        )
    )
    
    return fig

# Generate monthly overview chart
@callback(
    Output("monthly-overview-chart", "children"),
    [Input("expenses-store", "data"),
     Input("total-income-store", "data"),
     Input("savings-target-store", "data")],
    prevent_initial_call=True
)
def generate_monthly_overview(expenses, total_income, savings_target):
    """Generate a chart showing monthly income, expenses, and savings"""
    if not expenses and not total_income:
        return html.P("No data available", className="text-muted")
    
    # Handle missing data gracefully
    total_income_amount = 0
    total_expenses = 0
    savings_target_amount = 0

    if total_income:
        total_income_amount = sum(income.get('amount', 0) for income in total_income)

    if expenses:
        total_expenses = sum(exp.get('amount', 0) for exp in expenses)

    if savings_target:
        savings_target_amount = savings_target
    
    # Calculate remaining after expenses and savings
    remaining = max(0, total_income_amount - total_expenses - savings_target_amount)
    
    # Create data for the chart
    categories = ['Income', 'Expenses', 'Savings Target', 'Remaining']
    values = [total_income_amount, total_expenses, savings_target_amount, remaining]

    # Sophisticated blue color palette
    professional_blues = [
        "#1a365d", "#2a4a7f", "#3c64a1", "#5682c3", "#7ba0e5", 
        "#a8c0ff", "#d4e0ff", "#e8f0ff"
    ]
    
    # Premium professional blue palette with sophisticated gradient
    colors = professional_blues[:4]
    
    # Create bar chart with modern gradient fill
    fig = go.Figure()
    
            # Add bars with premium styling and gradient effect
    for i, (cat, val, color) in enumerate(zip(categories, values, colors)):
        fig.add_trace(go.Bar(
            x=[cat],
            y=[val],
            text=[f"£{val:.2f}"],
            textposition='inside',
            textfont=dict(
                family='Segoe UI, Arial, sans-serif',
                size=13,
                color='rgba(255,255,255,0.95)'
            ),
            marker=dict(
                color=color,  # ✅ valid
                line=dict(width=0.5, color='#ffffff')
            ),
            hoverinfo='text',
            hovertext=f"<b>{cat}</b><br>£{val:.2f}",
            width=0.7
        ))

    
    # Update layout with premium, sophisticated styling
    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#E0E0E0',
            zeroline=False,
            tickfont=dict(family='Segoe UI, Arial, sans-serif', size=12, color="#555555")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(230,230,230,0.3)',
            zeroline=True,
            zerolinecolor='#E0E0E0',
            showline=True,
            linecolor='#E0E0E0',
            tickfont=dict(family='Segoe UI, Arial, sans-serif', size=12, color="#555555"),
            title=None
        ),
        margin=dict(l=10, r=10, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family='Segoe UI, Arial, sans-serif',
            color='#333333'
        ),
        hoverlabel=dict(
            bgcolor='#f8f9fa',
            font_size=12,
            font_family='Segoe UI, Arial, sans-serif'
        ),
        bargap=0.35,
        showlegend=False,
        shapes=[
            # Add subtle background shading for professional look
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                fillcolor="rgba(240,249,255,0.5)",
                opacity=0.2,
                layer="below",
                line=dict(width=0)
            )
        ]
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

# Generate recurring vs one-time analysis chart
@callback(
    Output("recurring-analysis-chart", "children"),
    [Input("expenses-store", "data")],
    prevent_initial_call=True
)
def generate_recurring_analysis(expenses):
    """Generate a chart showing recurring vs one-time expenses"""
    if not expenses:
        return html.P("No expense data available", className="text-muted")
    
    # Sophisticated blue color palette
    professional_blues = [
        "#1a365d", "#2a4a7f", "#3c64a1", "#5682c3", "#7ba0e5", 
        "#a8c0ff", "#d4e0ff", "#e8f0ff"
    ]
    
    # Categorize expenses as recurring or one-time
    recurring_expenses = [exp for exp in expenses if exp.get('recurring', False)]
    one_time_expenses = [exp for exp in expenses if not exp.get('recurring', False)]
    
    # Calculate totals
    recurring_total = sum(exp.get('amount', 0) for exp in recurring_expenses)
    one_time_total = sum(exp.get('amount', 0) for exp in one_time_expenses)
    
    # Create data for the donut chart
    labels = ['Recurring', 'One-time']
    values = [recurring_total, one_time_total]
    colors = [professional_blues[1], professional_blues[3]]
    
    # Create donut chart with enhanced styling
    fig = go.Figure()
    
    # Add donut chart with premium styling
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        textinfo='label+percent',
        insidetextorientation='radial',
        textfont=dict(
            family='Segoe UI, Arial, sans-serif',
            size=14,
            color='#ffffff'
        ),
        marker=dict(
            colors=colors,
            line=dict(color='#ffffff', width=1),
            pattern=dict(
                shape=['', ''],
                solidity=0.9
            )
        ),
        hole=0.75,  # Even larger hole for premium donut look
        hoverinfo='label+value+percent',
        hovertemplate='<b>%{label}</b><br>£%{value:.2f}<br>%{percent}',
        pull=[0, 0],  # No pull for cleaner look
        rotation=90  # Start from the top
    ))
    
    # Update layout with premium styling
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family='Segoe UI, Arial, sans-serif',
            color='#333333',
            size=12
        ),
        hoverlabel=dict(
            bgcolor='rgba(240,249,255,0.95)',
            bordercolor='#0353a4',
            font_size=12,
            font_family='Segoe UI, Arial, sans-serif'
        ),
        annotations=[
            dict(
                text=f'£{recurring_total + one_time_total:.2f}',
                showarrow=False,
                font=dict(size=20, color='#023e7d', family='Segoe UI, Arial, sans-serif', weight='bold'),
                x=0.5,
                y=0.5
            ),
            dict(
                text='TOTAL',
                showarrow=False,
                font=dict(size=12, color='#555555', family='Segoe UI, Arial, sans-serif'),
                x=0.5,
                y=0.42
            )
        ],
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(
                family='Segoe UI, Arial, sans-serif',
                size=12,
                color='#333333'
            ),
            bordercolor='#E0E0E0',
            borderwidth=1
        ),
        shapes=[
            # Add subtle background gradient for professional look
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                fillcolor="rgba(240,249,255,0.5)",
                opacity=0.2,
                layer="below",
                line=dict(width=0)
            )
        ]
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

# Add this callback to trigger on page load
@callback(
    Output("app-loaded-store", "data"),
    Input("app-loaded-store", "id"),
    prevent_initial_call=False  # Important: Allow initial call
)
def set_app_loaded(_):
    """Set the app-loaded flag to True when the page loads"""
    return True