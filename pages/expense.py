# expenses.py - Dash Page for Expense Management

from dash import html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import datetime
import dash

# Register this file as a page
dash.register_page(__name__, path='/expenses')

# Layout for the Expenses Page
layout = html.Div([

    # Header
    html.Div([
        html.Div([
            html.Img(src="/assets/Logo_slogan.PNG", className="dashboard-logo"),
        ], className="dashboard-title"),
    ], className="dashboard-header"),

    # Navigation
    html.Nav([
        html.Button([
            html.Span("BlueCard Finance", className="mobile-nav-toggle-text"),
            html.Span("≡")
        ], className="mobile-nav-toggle", id="mobile-nav-toggle"),

        html.Ul([
            html.Li(html.A([html.Span("📊", className="nav-icon"), "Dashboard"], href="/", className="nav-link"), className="nav-item"),
            html.Li(html.A([html.Span("📈", className="nav-icon"), "Income"], href="/income", className="nav-link"), className="nav-item"),
            html.Li(html.A([html.Span("💰", className="nav-icon"), "Expenses"], href="/expenses", className="nav-link active"), className="nav-item"),
            html.Li(html.A([html.Span("📝", className="nav-icon"), "Transactions"], href="/transactions", className="nav-link"), className="nav-item"),
            html.Li(html.A([html.Span("🎯", className="nav-icon"), "Goals"], href="/goals", className="nav-link"), className="nav-item"),
            html.Li(html.A([html.Span("⚙️", className="nav-icon"), "Settings"], href="/settings", className="nav-link"), className="nav-item")
        ], className="nav-menu", id="nav-menu")
    ], className="nav-bar"),

    # Optional Breadcrumb
    html.Ul([
        html.Li([
            html.A("Home", href="/", className="breadcrumb-link")
        ], className="breadcrumb-item"),
        html.Li("Dashboard", className="breadcrumb-item breadcrumb-current")
    ], className="breadcrumb"),

    dbc.Row([
        # Left Column: Expense Form & List
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Add Monthly Expense")),
                dbc.CardBody([
                    dbc.Form([
                        dbc.Input(id='desc-input', placeholder='Expense Description', type='text', className='mb-2'),
                        dbc.Input(id='amount-input', placeholder='Amount ($)', type='number', min=0, step=0.01, className='mb-2'),
                        dcc.Dropdown(
                            id='category-input',
                            options=[{'label': cat, 'value': cat} for cat in [
                                "Housing", "Transportation", "Food", "Utilities", "Health", "Insurance",
                                "Debt", "Entertainment", "Personal", "Education", "Savings", "Other"
                            ]],
                            placeholder='Select Category',
                            className='mb-2'
                        ),
                        dcc.DatePickerSingle(
                            id='due-date-input',
                            date=datetime.date.today(),
                            className='mb-2'
                        ),
                        dbc.Checkbox(id='recurring-input', label='Recurring Expense', className='mb-3'),
                        dbc.Button("Add Expense", id='submit-expense', color='primary')
                    ])
                ])
            ], className='mb-4'),

            dbc.Card([
                dbc.CardHeader(html.H5("Current Monthly Expenses")),
                dbc.CardBody(html.Div(id='expense-list'))
            ])
        ], width=8),

        # Right Column: Summary & Savings
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(html.H5("Expense Summary")),
                dbc.CardBody(id='expense-summary')
            ], className='mb-4'),

            dbc.Card([
                dbc.CardHeader(html.H5("Set Savings Target")),
                dbc.CardBody([
                    dbc.Input(id='savings-goal-input', type='number', min=0, step=0.01, placeholder="Monthly savings goal ($)", className='mb-2'),
                    dbc.Button("Update Savings Goal", id='update-savings-goal', color='secondary'),
                    html.Div(id='savings-summary', className='mt-3')
                ])
            ])
        ], width=4)
    ]),

    # Local storage for expenses and other variables
    dcc.Store(id='expenses-store', storage_type='local'),
    dcc.Store(id='salary-store', storage_type='local'),
    dcc.Store(id='savings-target-store', storage_type='local'),
    dcc.Store(id='total-expenses-store', storage_type='local'),
    dcc.Store(id="total-income-store", storage_type="local")
])

# Callback to add expense to the store
@callback(
    Output('expenses-store', 'data'),
    Output('total-expenses-store', 'data'),
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
    if not all([desc, amount, category, due_date]):
        raise dash.exceptions.PreventUpdate

    new_expense = {
        'description': desc,
        'amount': amount,
        'category': category,
        'due_date': due_date,
        'recurring': bool(recurring)
    }

    expenses_data = expenses_data or []
    expenses_data.append(new_expense)
    total = sum(e['amount'] for e in expenses_data)
    return expenses_data, total


# Callback to display current expenses
@callback(
    Output('expense-list', 'children'),
    Input('expenses-store', 'data')
)
def update_expense_list(data):
    if not data:
        return html.P("No expenses added yet.", className="text-muted")

    return [
        dbc.ListGroupItem([
            html.Div([
                html.Div([
                    html.Strong(exp['description']),
                    html.Div(f"{exp['category']} • Due: {exp['due_date']}", className='text-muted', style={"fontSize": "13px"})
                ], style={'flex': 1}),
                html.Div(f"${exp['amount']:.2f}", className='ms-3 fw-bold text-danger')
            ], style={'display': 'flex', 'justifyContent': 'space-between'})
        ]) for exp in data
    ]

# Callback for summary
@callback(
    Output('expense-summary', 'children'),
    Input('total-expenses-store', 'data'),
    Input('total-income-store', 'data')
)
def update_summary(total, total_income):
    if not total:
        return html.P("Add expenses to see your summary.", className="text-muted")

    total_income = total_income or 0
    remaining = total_income - total
    ratio = (total / total_income * 100) if total_income > 0 else 0

    return html.Div([
        html.Div([html.Div("Total Monthly Expenses", className="text-muted"),
                  html.H5(f"${total:.2f}")], className="mb-3"),
        html.Div([html.Div("Remaining After Expenses", className="text-muted"),
                  html.H5(f"${remaining:.2f}")], className="mb-3"),
        html.Div([html.Div("Expense Ratio", className="text-muted"),
                  html.Div([dbc.Progress(value=ratio, color='info', striped=True),
                            html.Div(f"{ratio:.1f}%", className="mt-1")])])
    ])

@callback(
    Output('income-display', 'children'),  # this is the ID of the HTML component you'll update
    Input('total-income-store', 'data')    # pulling value from the store
)
def display_income(total_income):
    if total_income is None:
        return html.P("No income data available", className="text-muted")
    return total_income

@callback(
    Output('savings-target-store', 'data'),
    Output('savings-summary', 'children'),
    Input('update-savings-goal', 'n_clicks'),
    State('savings-goal-input', 'value'),
    State('total-income-store', 'data'),
    State('total-expenses-store', 'data'),
    prevent_initial_call=True
)
def update_savings_target(n, value, total_income, total_expenses):
    if not value:
        raise dash.exceptions.PreventUpdate

    # Calculate remaining income after expenses
    remaining = (total_income - total_expenses) if total_income and total_expenses else 0

    # Calculate savings percent
    savings_percent = (value / remaining * 100) if remaining > 0 else 0
    summary = html.P(f"Your savings target is {savings_percent:.1f}% of your remaining income after expenses.", className="text-info")
    print(f"Updated savings target: {value}")
    return value, summary
