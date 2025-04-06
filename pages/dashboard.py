import dash
from dash import html, dcc, callback, Input, Output, register_page
import pandas as pd
import numpy as np
import datetime
import calendar
import plotly.express as px
import plotly.graph_objects as go
from datetime import date
import json
import os
# from app import app

# Register this file as the dashboard page
register_page(__name__, path='/', name='Dashboard')

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
            html.Li([
                html.A([
                    html.Span("📊", className="nav-icon"),
                    "Dashboard"
                ], href="/", className="nav-link active")
            ], className="nav-item"),
            
            html.Li([
                html.A([
                    html.Span("📈", className="nav-icon"),
                    "Income"
                ], href="/income", className="nav-link")
            ], className="nav-item"),

            html.Li([
                html.A([
                    html.Span("💰", className="nav-icon"),
                    "Expenses"
                ], href="/expenses", className="nav-link")
            ], className="nav-item"),
            
            html.Li([
                html.A([
                    html.Span("📝", className="nav-icon"),
                    "Transactions"
                ], href="/transactions", className="nav-link")
            ], className="nav-item"),
            
            html.Li([
                html.A([
                    html.Span("🎯", className="nav-icon"),
                    "Goals"
                ], href="/goals", className="nav-link")
            ], className="nav-item"),
            
            html.Li([
                html.A([
                    html.Span("⚙️", className="nav-icon"),
                    "Settings"
                ], href="/settings", className="nav-link")
            ], className="nav-item")
        ], className="nav-menu", id="nav-menu")
    ], className="nav-bar"),

    # Optional Breadcrumb
    html.Ul([
        html.Li([
            html.A("Home", href="/", className="breadcrumb-link")
        ], className="breadcrumb-item"),
        html.Li("Dashboard", className="breadcrumb-item breadcrumb-current")
    ], className="breadcrumb"),
    
    # Main Content
    html.Div([
        # Summary tiles
        html.H3("Financial Summary", className="section-title"),
        html.Div(id="summary-tiles", className="metric-container"),
        
        html.Div(style={"height": "24px"}),
        
        # Expense breakdown and savings progress
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
        
        # Recent activity and spending trends
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
            ], className="column-right-large")
        ], className="row-container"),
        
        html.Div(style={"height": "24px"}),
        
        # Finance insights
        html.Div([
            html.Div([
                html.Div([
                    html.H3("Finance Insights", className="card-title")
                ], className="card-header"),
                
                html.Div([
                    html.Div([
                        html.Div(id="savings-rate-insight", className="insight-item")
                    ], className="column-insight"),
                    
                    html.Div([
                        html.Div(id="budget-balance-insight", className="insight-item")
                    ], className="column-insight"),
                    
                    html.Div([
                        html.Div(id="spending-trend-insight", className="insight-item")
                    ], className="column-insight")
                ], className="insights-container")
            ], className="dashboard-card")
        ], className="row-container")
    ], className="main-container"),
    
    # Store components for data
    dcc.Store(id='session-data-store', data=get_session_data()),
    dcc.Store(id="total-income-store", storage_type="local"),
    dcc.Store(id='expenses-store', storage_type='local'),
    dcc.Store(id='total-expenses-store', storage_type='local'),
    dcc.Store(id='savings-target-store', storage_type='local'),
    
    # Include CSS
    html.Link(rel="stylesheet", href="/assets/style.css")
])

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
    return f"${total_income:,.2f}"

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
        total_income = 1
    if total_expenses is None:
        total_expenses = 0

    remaining = total_income - total_expenses if total_income > 0 else 0
    savings_progress = (savings_target / remaining * 100) if remaining > 0 and savings_target > 0 else 0

    return [
        # Monthly Income Tile
        html.Div([
            html.Div([
                html.H4("Monthly Income", className="summary-title"),
                html.Div("💰", className="summary-icon icon-blue")
            ], className="summary-header"),
            html.P(id="dashboard-income-display", className="summary-value"),
            html.P(f"Daily budget: ${(total_income - total_expenses)/30:,.2f}", className="summary-subtitle")
        ], className="summary-tile"),

        # Total Expenses Tile
        html.Div([
            html.Div([
                html.H4("Total Expenses", className="summary-title"),
                html.Div("📊", className="summary-icon icon-red")
            ], className="summary-header"),
            html.P(f"${total_expenses:,.2f}", className="summary-value"),
            html.P(f"{(total_expenses / total_income) * 100:.1f}% of income used", className="summary-subtitle")
        ], className="summary-tile"),

        # Remaining Tile
        html.Div([
            html.Div([
                html.H4("Remaining", className="summary-title"),
                html.Div("✅", className="summary-icon icon-green")
            ], className="summary-header"),
            html.P(f"${remaining:,.2f}", className="summary-value"),
            html.P(f"{(remaining / total_income) * 100:.1f}% of income available", className="summary-subtitle")
        ], className="summary-tile"),

        # Savings Target Tile
        html.Div([
            html.Div([
                html.H4("Savings Target", className="summary-title"),
                html.Div("🎯", className="summary-icon icon-orange")
            ], className="summary-header"),
            html.P(f"${savings_target:,.2f}", className="summary-value"),
            html.P(f"Your savings target is {savings_progress:.1f}% of total income after expenses", className="summary-subtitle"),
            html.P(f"Daily spending budget to meet target: ${(total_income - total_expenses)/30 - savings_target/30:,.2f}", className="summary-subtitle"),
        ], className="summary-tile")
    ]

@callback(
    Output('expense-breakdown-content', 'children'),
    Input('total-expenses-store', 'data'),
    Input('expenses-store', 'data'),
    Input('session-data-store', 'data')
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
            html.P("No expenses added yet. Add expenses in the Expenses tab to see your breakdown.", className="info-message")
        ], className="info-box")
    
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
    
    # Custom color palette
    custom_colors = ['#0466c8', '#0353a4', '#023e7d', '#001845', '#001233', 
                     '#33415c', '#5c677d', '#7d8597', '#979dac', '#33415c']
    
    # Create donut chart
    fig = px.pie(
        df_expenses, 
        values='Amount', 
        names='Category', 
        hole=0.6,
        color_discrete_sequence=custom_colors
    )
    fig.update_traces(textposition='outside', textinfo='percent+label')
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=350,
        legend=dict(orientation="h", y=-0.2),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12, color="#404040")
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})


@callback(
    Output('savings-progress-content', 'children'),
    Input('total-income-store', 'data'),
    Input('total-expenses-store', 'data'),
    Input('savings-target-store', 'data')
)
def update_savings_progress(total_income, total_expenses, saving_target):

    if saving_target <= 0:
        return html.Div([
            html.P("Set a savings target in the Expenses tab to track your progress.", className="info-message")
        ], className="info-box")
    
    # Calculate savings progress using total_income and total_expenses
    if total_income is None:
        total_income = total_income  # Fallback to salary if total_income not available
    if total_expenses is None:
        total_expenses = 0
        
    remaining = total_income - total_expenses if total_income > 0 else 0
    savings_percent = min((saving_target / remaining * 100), 100) / 100 if remaining > 0 and saving_target > 0 else 0
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=savings_percent * 100,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#404040"},
            'bar': {'color': "#0466c8"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#e5e5e5",
            'steps': [
                {'range': [0, 30], 'color': 'rgba(4, 102, 200, 0.2)'},
                {'range': [30, 70], 'color': 'rgba(4, 102, 200, 0.4)'},
                {'range': [70, 100], 'color': 'rgba(4, 102, 200, 0.6)'}
            ],
        },
        title={
            'text': f"${saving_target:,.2f}",
            'font': {'size': 20, 'color': '#262626', 'family': 'Inter, sans-serif'}
        },
        number={
            'suffix': "%",
            'font': {'size': 26, 'color': '#0466c8', 'family': 'Inter, sans-serif'}
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(t=60, b=0, l=30, r=30),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif")
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

@callback(
    Output('recent-activity-content', 'children'),
    Input('session-data-store', 'data')
)
def update_recent_activity(data):
    if not data['daily_expenses']:
        return html.Div([
            html.P("No recent transactions. Record your spending in the Transactions tab.", className="info-message")
        ], className="info-box")
    
    # Convert to DataFrame and sort
    df_recent = pd.DataFrame(data['daily_expenses'])
    df_recent['date'] = pd.to_datetime(df_recent['date'])
    df_recent = df_recent.sort_values('date', ascending=False).head(5)
    
    # Create transaction items
    transaction_items = []
    for _, row in df_recent.iterrows():
        transaction_items.append(html.Div([
            html.Div([
                html.Div(row['emoji'], className="transaction-icon"),
                html.Div([
                    html.Div(row['description'], className="transaction-title"),
                    html.Div(pd.to_datetime(row['date']).strftime('%b %d, %Y'), className="transaction-meta")
                ], className="transaction-details")
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div(f"${row['amount']:.2f}", className="transaction-amount")
        ], className="transaction-item"))
    
    return html.Div(transaction_items)

@callback(
    Output('spending-trends-content', 'children'),
    Input('total-income-store', 'data'),
    Input('total-expenses-store', 'data'),
    Input('session-data-store', 'data')
)
def update_spending_trends(total_income, total_expenses, data):
    if not data['daily_expenses']:
        return html.Div([
            html.P("No transaction data available. Record your daily expenses to see trends.", className="info-message")
        ], className="info-box")
    
    # Convert to DataFrame for analysis
    df_daily = pd.DataFrame(data['daily_expenses'])
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    
    # Group by date and sum amounts
    daily_totals = df_daily.groupby(df_daily['date'].dt.date)['amount'].sum().reset_index()
    daily_totals['date'] = pd.to_datetime(daily_totals['date'])
    daily_totals = daily_totals.sort_values('date')
    
    # Calculate daily budget using total_income and total_expenses
    if total_income is None:
        total_income = data['salary']  # Fallback to salary if not available
    if total_expenses is None:
        total_expenses = 0
        
    remaining_after_expenses = total_income - total_expenses
    daily_budget = (remaining_after_expenses - data['savings_target']) / 30
    daily_totals['budget_line'] = daily_budget
    
    # Create line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_totals['date'],
        y=daily_totals['amount'],
        mode='lines+markers',
        name='Daily Spending',
        line=dict(color='#0466c8', width=3),
        marker=dict(size=8, color='#0466c8')
    ))
    
    # Add budget reference line
    fig.add_trace(go.Scatter(
        x=daily_totals['date'],
        y=daily_totals['budget_line'],
        mode='lines',
        name='Daily Budget',
        line=dict(color='#38b000', width=2, dash='dash')
    ))
    
    fig.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        height=250,
        legend=dict(orientation="h", y=1.1),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=12, color="#404040"),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor='#e5e5e5'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#e5e5e5',
            showline=True,
            linecolor='#e5e5e5',
            tickprefix='$'
        ),
        hovermode="x unified"
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

@callback(
    Output('savings-rate-insight', 'children'),
    Input('total-income-store', 'data'),
    Input('total-expenses-store', 'data'),
)
def update_savings_rate_insight(total_income, total_expenses):
    if total_income is None or total_income <= 0:
        return html.Div([
            html.P("Set your income to see savings rate insights.", className="info-message")
        ], className="info-box")
    
    # Calculate savings rate with total_expenses
    if total_expenses is None:
        total_expenses = 0
        
    savings_rate = (total_income - total_expenses) / total_income * 100
    
    if savings_rate >= 20:
        return html.Div([
            html.P([
                "✓ Excellent Savings Rate"
            ], style={"margin": 0, "fontSize": "14px", "fontWeight": 600, "color": "#38b000"}),
            html.P([
                f"Your savings rate is above 20%, which is excellent for long-term financial health."
            ], style={"margin": "5px 0 0 0", "fontSize": "13px"})
        ], className="info-box", style={"borderLeftColor": "#38b000"})
    elif savings_rate >= 10:
        return html.Div([
            html.P([
                "✓ Good Savings Rate"
            ], style={"margin": 0, "fontSize": "14px", "fontWeight": 600, "color": "#0466c8"}),
            html.P([
                f"Your savings rate is between 10-20%, which is a good foundation."
            ], style={"margin": "5px 0 0 0", "fontSize": "13px"})
        ], className="info-box")
    else:
        return html.Div([
            html.P([
                "! Low Savings Rate"
            ], style={"margin": 0, "fontSize": "14px", "fontWeight": 600, "color": "#f48c06"}),
            html.P([
                f"Your savings rate is below 10%. Try to reduce non-essential expenses."
            ], style={"margin": "5px 0 0 0", "fontSize": "13px"})
        ], className="warning-box")

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
            html.P("Add expenses in the Expenses tab to get budget balance insights.", className="info-message")
        ], className="info-box")
    
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
            html.P([
                f"! High {largest_category[0]} Expenses"
            ], style={"margin": 0, "fontSize": "14px", "fontWeight": 600, "color": "#f48c06"}),
            html.P([
                f"{largest_category[0]} makes up {largest_percent:.1f}% of your expenses. Consider rebalancing your budget."
            ], style={"margin": "5px 0 0 0", "fontSize": "13px"})
        ], className="warning-box")
    else:
        return html.Div([
            html.P([
                "✓ Balanced Budget"
            ], style={"margin": 0, "fontSize": "14px", "fontWeight": 600, "color": "#38b000"}),
            html.P([
                f"Your largest expense category ({largest_category[0]}) is {largest_percent:.1f}% of total expenses."
            ], style={"margin": "5px 0 0 0", "fontSize": "13px"})
        ], className="info-box", style={"borderLeftColor": "#38b000"})

@callback(
    Output('spending-trend-insight', 'children'),
    Input('session-data-store', 'data')
)
def update_spending_trend_insight(data):
    if not data['daily_expenses']:
        return html.Div([
            html.P("Record daily transactions to get spending trend insights.", className="info-message")
        ], className="info-box")
    
    # Analyze recent spending trends
    df_daily = pd.DataFrame(data['daily_expenses'])
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    
    # Get last 7 days vs previous 7 days
    today = datetime.datetime.now().date()
    last_week = df_daily[df_daily['date'] >= (pd.Timestamp(today) - pd.Timedelta(days=7))]
    prev_week = df_daily[(df_daily['date'] < (pd.Timestamp(today) - pd.Timedelta(days=7))) & 
                          (df_daily['date'] >= (pd.Timestamp(today) - pd.Timedelta(days=14)))]
    
    last_week_total = last_week['amount'].sum() if not last_week.empty else 0
    prev_week_total = prev_week['amount'].sum() if not prev_week.empty else 0
    
    if prev_week_total > 0:
        percent_change = (last_week_total - prev_week_total) / prev_week_total * 100
        
        if percent_change > 20:
            return html.Div([
                html.P([
                    "! Spending Increase"
                ], style={"margin": 0, "fontSize": "14px", "fontWeight": 600, "color": "#d00000"}),
                html.P([
                    f"Your spending increased by {percent_change:.1f}% compared to previous week."
                ], style={"margin": "5px 0 0 0", "fontSize": "13px"})
            ], className="warning-box")
        elif percent_change < -10:
            return html.Div([
                html.P([
                    "✓ Reduced Spending"
                ], style={"margin": 0, "fontSize": "14px", "fontWeight": 600, "color": "#38b000"}),
                html.P([
                    f"Great job! You reduced spending by {abs(percent_change):.1f}% from last week."
                ], style={"margin": "5px 0 0 0", "fontSize": "13px"})
            ], className="info-box", style={"borderLeftColor": "#38b000"})
        else:
            return html.Div([
                html.P([
                    "✓ Consistent Spending"
                ], style={"margin": 0, "fontSize": "14px", "fontWeight": 600, "color": "#0466c8"}),
                html.P([
                    f"Your spending is within {abs(percent_change):.1f}% of last week."
                ], style={"margin": "5px 0 0 0", "fontSize": "13px"})
            ], className="info-box")
    else:
        return html.Div([
            html.P("Need more data to analyze spending trends.", className="info-message")
        ], className="info-box")
    
@callback(
    Output('some-dashboard-component', 'children'),
    Input('total-expenses-store', 'data'),
)
def use_expenses_in_dashboard(total_expenses):
    if total_expenses is None:
        return "No expense data available"

    return f"Total expenses: ${total_expenses:,.2f}"

@callback(
    Output('savings-goal-display', 'children'),
    Input('savings-target-store', 'data')  # Fetch data from the savings-target-store
)
def display_savings_goal(savings_target):
    if savings_target is None:
        return html.P("No savings target set.", className="text-muted")
    return html.H5(f"Savings Goal: ${savings_target:.2f}")


