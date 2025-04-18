import dash
from dash import dcc, html, Input, Output, State, callback, ALL, MATCH
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import uuid
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from prophet import Prophet
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import json  # Make sure json is imported at the top level

# Register this file as a page
dash.register_page(__name__, path='/income')

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

HEADER_STYLE = {
    'backgroundColor': COLORS['primary'],  # Dark blue header
    'color': COLORS['white'],  # White text
    'borderBottom': f'2px solid {COLORS["accent"]}',  # Accent border
    'borderRadius': '12px 12px 0 0',  # Rounded top corners
    'padding': '15px 20px',  # Add padding
    'fontWeight': 'bold',  # Bold header text
    'fontSize': '16px'  # Slightly larger font
}

# Helper function to create pie chart
def create_pie_chart(income_sources):
    if not income_sources:
        # Return an empty chart with a message
        fig = go.Figure()
        fig.add_annotation(
            text="No income sources available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#555")
        )
        fig.update_layout(
            height=300, 
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    # Group by category
    categories = {}
    for source in income_sources:
        category = source.get("category", "other").title()
        amount = source.get("monthly_amount", 0)
        categories[category] = categories.get(category, 0) + amount

    # Create a DataFrame for the pie chart
    df = pd.DataFrame({
        'Category': list(categories.keys()),
        'Amount': list(categories.values())
    })
    
    # Blue color scheme palette - from light to dark blue
    blue_palette = [
        '#E6F2FF', '#B3D9FF', '#80BFFF', '#4DA6FF', '#1A8CFF', 
        '#0073E6', '#0059B3', '#004080', '#00264D', '#001F3F'
    ]
    
    # Use only as many colors as needed
    colors_needed = min(len(categories), len(blue_palette))
    color_sequence = blue_palette[:colors_needed]
    
    # Create the pie chart with enhanced styling
    fig = px.pie(
        df,
        values='Amount',
        names='Category',
        hole=0.6,  # Larger donut hole for modern look
        color_discrete_sequence=color_sequence
    )
    
    # Update trace styling
    fig.update_traces(
        textposition='outside', 
        textinfo='percent+label',
        pull=[0.01] * len(categories),  # Slight pull for 3D effect
        marker=dict(
            line=dict(color='#FFFFFF', width=1.5)  # White borders between sections
        ),
        textfont=dict(size=12, color="#333", family="Arial, sans-serif"),
        hoverinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>%{percent:.1%}<br>£%{value:,.2f}<extra></extra>'
    )
    
    # Update layout with improved styling
    fig.update_layout(
        showlegend=False,
        height=300,
        margin=dict(t=10, b=10, l=10, r=10),
        uniformtext_minsize=10,
        uniformtext_mode='hide',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif")
    )
    
    # Add center text for total with currency formatting
    total = sum(categories.values())
    fig.add_annotation(
        text=f"£{total:,.0f}",
        x=0.5, y=0.5,
        font=dict(size=18, color='#0066CC', family="Arial, sans-serif", weight="bold"),
        showarrow=False
    )
    
    # Add "Monthly" label under the total
    fig.add_annotation(
        text="Monthly",
        x=0.5, y=0.44,
        font=dict(size=12, color='#666666', family="Arial, sans-serif"),
        showarrow=False
    )
    
    return fig

# Helper function to generate past and future dates
def generate_date_range(months_back=12, months_forward=12):
    today = datetime.now()
    # Generate past dates
    past_dates = [(today - timedelta(days=30 * i)) for i in range(months_back, 0, -1)]
    # Generate future dates including current month
    future_dates = [(today + timedelta(days=30 * i)) for i in range(0, months_forward + 1)]
    
    # Combine past and future dates
    all_dates = past_dates + future_dates[1:]  # Exclude duplicate of current month
    
    # Format dates as strings
    date_labels = [date.strftime("%b %Y") for date in all_dates]
    date_keys = [f"month_{i}" for i in range(-months_back, months_forward + 1)]
    
    return date_labels, date_keys, all_dates

# Enhanced timeline chart function with Prophet forecasting
def create_timeline_chart(income_sources):
    if not income_sources:
        # Return an empty chart with a message
        fig = go.Figure()
        fig.add_annotation(
            text="No income data available for forecast",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=14, color="#555")
        )
        fig.update_layout(
            height=400,
            margin=dict(t=10, b=10, l=10, r=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    # Generate date range for x-axis
    today = datetime.now()
    past_dates = [(today - timedelta(days=30 * i)) for i in range(12, 0, -1)]
    future_dates = [(today + timedelta(days=30 * i)) for i in range(0, 13)]
    all_dates = past_dates + future_dates[1:]  # Exclude duplicate of current month
    date_labels = [date.strftime("%b %Y") for date in all_dates]

    # Initialize data for each source
    data = []
    total_monthly = np.zeros(len(date_labels))

    # Blue color palette
    blue_palette = [
        '#E6F2FF', '#B3D9FF', '#80BFFF', '#4DA6FF', '#1A8CFF',
        '#0073E6', '#0059B3', '#004080', '#00264D', '#001F3F'
    ]

    # Create forecast for each source
    for i, source in enumerate(income_sources):
        monthly_amount = source.get("monthly_amount", 0)
        name = source.get("name", "Income")
        color_idx = i % len(blue_palette)

        # Initialize y values with the default monthly amount
        y_values = [monthly_amount] * len(date_labels)

        # Update with historical values if they exist
        historical_data = source.get("historical_data", {})

        # Check if we have enough historical data for Prophet forecasting
        if len(historical_data) >= 3 and source.get("consistency", "fixed") == "variable":
            # Prepare data for Prophet
            prophet_data = []

            # Convert historical data to Prophet format
            for j, key in enumerate([f"month_{k}" for k in range(-12, 0)]):  # Only historical keys
                if key in historical_data:
                    ds = past_dates[j]
                    y = historical_data[key]
                    prophet_data.append({"ds": ds, "y": y})

            if prophet_data:
                # Create Prophet DataFrame
                prophet_df = pd.DataFrame(prophet_data)

                # Initialize and fit Prophet model
                m = Prophet(
                    changepoint_prior_scale=0.1,  # Lower value to reduce sensitivity to trend changes
                    yearly_seasonality=False,
                    weekly_seasonality=True,
                    daily_seasonality=False,
                    seasonality_mode='additive',
                    interval_width=0.95
                )
                m.fit(prophet_df)

                # Create future dataframe for forecasting
                future = pd.DataFrame({"ds": all_dates})
                forecast = m.predict(future)

                # Update y_values with forecasted values
                for j, (date, yhat) in enumerate(zip(all_dates, forecast["yhat"])):
                    y_values[j] = max(0, yhat)  # Ensure no negative values
        else:
            # For fixed income or insufficient historical data, use actual values and then constant
            for j, key in enumerate([f"month_{k}" for k in range(-12, 0)]):  # Only historical keys
                if key in historical_data:
                    y_values[j] = historical_data[key]

        # Add this source to the plot
        data.append(go.Scatter(
            x=date_labels,
            y=y_values,
            mode='lines+markers',
            name=name,
            line=dict(width=2, color=blue_palette[color_idx]),
            marker=dict(size=6, color=blue_palette[color_idx])
        ))

        # Add to total
        total_monthly += np.array(y_values)

    # Add total line
    data.append(go.Scatter(
        x=date_labels,
        y=total_monthly,
        mode='lines+markers',
        name='Total Income',
        line=dict(width=4, color='#004080'),  # Dark blue for total
        marker=dict(size=8, color='#004080')
    ))

    # Add vertical line to indicate "Today"
    forecast_start_idx = 12  # Index where forecast begins
    data.append(go.Scatter(
        x=[date_labels[forecast_start_idx], date_labels[forecast_start_idx]],
        y=[0, max(total_monthly) * 1.1],
        mode='lines',
        name='Today',
        line=dict(width=2, color='rgba(0, 0, 0, 0.5)', dash='dash'),
        hoverinfo='none'
    ))

    # Add annotations for "Historical Data" and "Forecast"
    annotations = [
        dict(
            x=date_labels[max(0, forecast_start_idx - 3)],
            y=max(total_monthly) * 1.05,
            text="Historical Data",
            showarrow=False,
            font=dict(size=12, color='#004080')
        ),
        dict(
            x=date_labels[min(len(date_labels) - 1, forecast_start_idx + 3)],
            y=max(total_monthly) * 1.05,
            text="Forecast",
            showarrow=False,
            font=dict(size=12, color='#004080')
        )
    ]

    # Create the figure
    fig = go.Figure(data=data)
    fig.update_layout(
        title=None,
        height=400,
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis_title=None,
        yaxis_title="Monthly Amount (£)",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color="#333")
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.02)',
        font=dict(family="Arial, sans-serif"),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            tickangle=-45,  # Angle the date labels for better readability
            tickfont=dict(size=10, color="#333")
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.1)',
            tickprefix="£",
            tickfont=dict(size=10, color="#333")
        ),
        annotations=annotations
    )

    return fig

# Function to generate income source cards
def generate_income_cards(income_sources):
    if not income_sources:
        return [], html.Div([
            html.I(className="fas fa-info-circle me-2"),
            "No income sources added yet. Add your first income source above."
        ], className="text-muted"), "£0", "0"

    income_cards = []
    total_monthly_income = 0
    
    # Category display names without emojis
    category_display = {
        "employment": "Employment",
        "business": "Business",
        "investments": "Investments",
        "rental": "Rental",
        "freelance": "Freelance",
        "other": "Other"
    }
    
    # Frequency display mapping
    frequency_display = {
        "monthly": "Monthly",
        "biweekly": "Bi-weekly",
        "weekly": "Weekly",
        "annually": "Annually"
    }

    for idx, source in enumerate(income_sources):
        # Safely get monthly_amount with a default of 0
        monthly_amount = source.get("monthly_amount", 0)
        total_monthly_income += monthly_amount
        
        # Get category name
        category = source.get("category", "other")
        cat_display = category_display.get(category, "Other")
        freq = frequency_display.get(source.get("frequency", "monthly"), "Monthly")
        
        # Check if we have historical data and it's variable income
        has_history = "historical_data" in source and source["historical_data"]
        is_variable = source.get("consistency", "fixed") == "variable"
        
        # Extra info for variable income with history
        history_info = ""
        if has_history and is_variable:
            # Count how many historical months we have data for
            months_with_data = len(source["historical_data"])
            if months_with_data > 0:
                history_info = f" • {months_with_data} month{'s' if months_with_data > 1 else ''} history"

        # Create a more refined, professional card
        income_cards.append(
            dbc.Card([
                dbc.CardBody([
                    # Top row with name and buttons
                    html.Div([
                        # Left side: name and category
                        html.Div([
                            html.Div([
                                html.H5(source.get("name", f"Income Source #{idx+1}"), 
                                        className="mb-0 fw-semibold", 
                                        style={"color": "#2C3E50"}),
                                html.Small(f"{cat_display} • {freq}{history_info}", 
                                           className="text-muted",
                                           style={"fontSize": "12px", "letterSpacing": "0.3px"})
                            ])
                        ], className="d-flex align-items-center"),
                        
                        # Right side: Edit and Delete buttons
                        html.Div([
                            # Edit button
                            html.Button(
                                "Edit",
                                id={"type": "edit-income", "index": source["id"]},
                                className="btn btn-sm btn-outline-primary px-2 py-1 me-2",
                                title="Edit historical income data",
                                style={
                                    'borderRadius': '4px',
                                    'fontSize': '11px',
                                    'fontWeight': '500',
                                    'color': '#3498DB',
                                    'border': '1px solid #3498DB',
                                    'transition': 'all 0.2s',
                                    'letterSpacing': '0.3px'
                                }
                            ),
                            # Delete button
                            html.Button(
                                "Remove",
                                id={"type": "delete-income", "index": source["id"]},
                                className="btn btn-sm btn-outline-danger px-2 py-1",
                                title="Delete this income source",
                                style={
                                    'borderRadius': '4px',
                                    'fontSize': '11px',
                                    'fontWeight': '500',
                                    'color': '#E74C3C',
                                    'border': '1px solid #E74C3C',
                                    'transition': 'all 0.2s',
                                    'letterSpacing': '0.3px'
                                }
                            )
                        ], className="d-flex")
                    ], className="d-flex justify-content-between align-items-center mb-3"),
                    
                    # Amount row
                    html.Div([
                        # Left: Amount display 
                        html.Div([
                            html.H4(f"£{monthly_amount:,.2f}", 
                                   className="mb-0 fw-bold", 
                                   style={"color": "#3498DB", "fontFamily": "'Arial', sans-serif"}),
                            html.Small(
                                "Variable average" if is_variable else "Fixed income",
                                className="text-muted",
                                style={"fontSize": "11px", "letterSpacing": "0.2px"}
                            ) if is_variable else None
                        ], className="pe-3"),
                        
                        # Right: Equivalents
                        html.Div([
                            html.Div([
                                html.Span("Daily: ", className="small text-muted", style={"fontSize": "11px"}),
                                html.Span(f"£{source.get('daily_amount', 0):,.2f}", 
                                          className="small fw-semibold",
                                          style={"fontSize": "11px", "color": "#2C3E50"})
                            ], className="d-flex justify-content-between"),
                            html.Div([
                                html.Span("Weekly: ", className="small text-muted", style={"fontSize": "11px"}),
                                html.Span(f"£{source.get('weekly_amount', 0):,.2f}", 
                                          className="small fw-semibold",
                                          style={"fontSize": "11px", "color": "#2C3E50"})
                            ], className="d-flex justify-content-between")
                        ], className="flex-grow-1")
                    ], className="d-flex align-items-center mt-2")
                ], className="p-3")
            ], className="income-source-card mb-3 shadow-sm", 
            style={"borderLeft": f"3px solid #3498DB", "borderRadius": "3px"})
        )

    return income_cards, "", f"£{total_monthly_income:,.2f}", str(len(income_sources))

# Helper function to create historical income form fields
def create_historical_income_fields(source_id, source_data):
    # Generate date labels
    date_labels, date_keys, _ = generate_date_range(12, 0)  # Only past months
    
    # Get historical data if it exists
    historical_data = source_data.get("historical_data", {})
    
    # Generate fields for each month
    fields = []
    
    fields.append(html.H5(f"Edit Historical Income for {source_data.get('name', 'Income Source')}", className="mb-3"))
    fields.append(html.P("Enter your actual income for previous months:", className="text-muted mb-3"))
    
    for i, (label, key) in enumerate(zip(date_labels, date_keys)):
        default_value = historical_data.get(key, source_data.get("monthly_amount", 0))
        
        fields.append(
            dbc.Row([
                dbc.Col(html.Label(label, className="form-label mt-2"), width=4),
                dbc.Col(
                    dcc.Input(
                        id={"type": "historical-income", "index": source_id, "month": key},
                        type="number",
                        min=0,
                        step=10,
                        value=default_value,
                        className="form-control mb-2"
                    ),
                    width=8
                )
            ])
        )
    
    # Add save button
    fields.append(
        html.Button(
            "Save Historical Data", 
            id={"type": "save-historical", "index": source_id},
            className="btn btn-primary mt-3 w-100"
        )
    )
    
    # Add a status message div
    fields.append(
        html.Div(id={"type": "historical-save-status", "index": source_id}, className="mt-2")
    )
    
    return fields

# Layout
layout = html.Div([
    # Header
    html.Div([
        html.Img(src="/assets/Logo_slogan.PNG", className="dashboard-logo"),

    

        # Navigation
        html.Nav([
            html.Button([
                html.Span("BlueCard Finance", className="mobile-nav-toggle-text"),
                html.Span("≡")
            ], className="mobile-nav-toggle", id="mobile-nav-toggle"),

            html.Ul([
                html.Li(html.A([html.Span(className="nav-icon"), "Home"], href="/", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Dashboard"], href="/dashboard", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Income"], href="/income", className="nav-link active"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Expenses"], href="/expenses", className="nav-link"), className="nav-item"),
                html.Li([html.A([html.Span(className="nav-icon"), "Savings Analysis"], href="/savings", className="nav-link")], className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Settings"], href="/settings", className="nav-link"), className="nav-item")
            ], className="nav-menu", id="nav-menu")
        ], className="nav-bar"),
    ], className="header-container"),

    # Breadcrumb
    html.Ul([
        html.Li(html.A("Home", href="/", className="breadcrumb-link"), className="breadcrumb-item"),
        html.Li("Income", className="breadcrumb-item breadcrumb-current")
    ], className="breadcrumb"),

    # Page Content
    html.Div([
        html.H2("Income Management", className="section-title mb-4",
                style={'color': COLORS['primary'], 'borderBottom': f'2px solid {COLORS["accent"]}', 'paddingBottom': '10px'}),

        dbc.Row([
            # Left Column: Summary and Pie Chart
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H4("Income Summary", className="card-title m-0"),
                        className="d-flex flex-column",
                        style=HEADER_STYLE  # Apply HEADER_STYLE to the entire CardHeader
                    ),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H6("Total Monthly Income", className="stat-label text-muted"),
                                    html.H3(id="total-income-display", className="stat-value")
                                ], className="stat-card")
                            ], width=6),
                            dbc.Col([
                                html.Div([
                                    html.H6("Income Sources", className="stat-label text-muted"),
                                    html.H3(id="income-sources-count", className="stat-value")
                                ], className="stat-card")
                            ], width=6)
                        ], className="mb-3"),

                        # Income Pie Chart
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    dcc.Graph(id="income-pie-chart", className="p-0 m-0",
                                              config={'displayModeBar': False})
                                ], className="graph-container")
                            ], width=12)
                        ]),

                        # Togglable Buttons for Forecast and What-If Analysis
                        dbc.ButtonGroup([
                            dbc.Button("Income Forecast", id="toggle-forecast", color="primary", outline=True, className="toggle-button"),
                            dbc.Button("What-If Analysis", id="toggle-whatif", color="primary", outline=True, className="toggle-button"),
                        ], className="mt-3"),
                    ])
                ], className="shadow-sm mb-4"),
            ], width=12, lg=5),

            # Right Column: Add Income Source
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(
                        html.H4("Add Income Source", className="card-title m-0"),
                        className="d-flex flex-column",
                        style=HEADER_STYLE  # Apply HEADER_STYLE to the entire CardHeader
                    ),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Source Name", className="form-label fw-bold"),
                                dcc.Input(
                                    id="income-source-name",
                                    type="text",
                                    className="form-control mb-3",
                                    placeholder="e.g. Salary, Freelance, Rental Income"
                                ),
                            ], width=12),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                html.Label("Amount (£)", className="form-label fw-bold"),
                                dcc.Input(
                                    id="income-amount-input",
                                    type="number",
                                    min=0,
                                    step=100,
                                    className="form-control mb-3",
                                    placeholder="e.g. 3000"
                                ),
                            ], width=6),
                            dbc.Col([
                                html.Label("Frequency", className="form-label fw-bold"),
                                dcc.Dropdown(
                                    id="income-frequency",
                                    options=[
                                        {"label": "Monthly", "value": "monthly"},
                                        {"label": "Bi-weekly", "value": "biweekly"},
                                        {"label": "Weekly", "value": "weekly"},
                                        {"label": "Annually", "value": "annually"}
                                    ],
                                    value="monthly",
                                    className="mb-3"
                                ),
                            ], width=6),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                html.Label("Category", className="form-label fw-bold"),
                                dcc.Dropdown(
                                    id="income-category",
                                    options=[
                                        {"label": "Employment", "value": "employment"},
                                        {"label": "Business", "value": "business"},
                                        {"label": "Investments", "value": "investments"},
                                        {"label": "Rental", "value": "rental"},
                                        {"label": "Freelance", "value": "freelance"},
                                        {"label": "Other", "value": "other"}
                                    ],
                                    value="employment",
                                    className="mb-4"
                                ),
                            ], width=12),
                        ]),

                        dbc.Row([
                            dbc.Col([
                                html.Label("Income Type", className="form-label fw-bold"),
                                dbc.RadioItems(
                                    id="income-type",
                                    options=[
                                        {"label": "Before Tax", "value": "before_tax"},
                                        {"label": "After Tax", "value": "after_tax"}
                                    ],
                                    value="after_tax",
                                    inline=True,
                                    className="mb-3"
                                ),
                            ], width=6),
                            dbc.Col([
                                html.Label("Consistency", className="form-label fw-bold"),
                                dbc.RadioItems(
                                    id="income-consistency",
                                    options=[
                                        {"label": "Fixed", "value": "fixed"},
                                        {"label": "Variable", "value": "variable"}
                                    ],
                                    value="fixed",
                                    inline=True,
                                    className="mb-3"
                                ),
                            ], width=6),
                        ]),

                        html.Button("Add Income Source", id="add-income-button", className="btn btn-primary w-100"),
                        html.Div(id="income-add-success-message", className="mt-3"),
                    ])
                ], className="shadow-sm mb-4 h-100")
            ], width=12, lg=7),
        ]),

        # New Row for Collapsible Sections
        dbc.Row([
            dbc.Col([
                dbc.Collapse(
                    dbc.Card([
                        dbc.CardHeader(html.H4("Income Forecast", className="text-primary m-0")),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    dcc.Graph(id="income-timeline-chart", config={'displayModeBar': False})
                                ], width=12)
                            ])
                        ])
                    ], className="shadow-sm mb-4"),
                    id="collapse-forecast",
                    is_open=False
                ),

                dbc.Collapse(
                    dbc.Card([
                        dbc.CardHeader(html.H4("What-If Analysis", className="text-primary m-0")),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Remove Income Source", className="form-label fw-bold"),
                                    dcc.Dropdown(
                                        id="income-source-whatif-dropdown",
                                        className="mb-3",
                                        style={"width": "100%"}
                                    )
                                ], width=12)
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id="whatif-analysis-result", className="py-3")
                                ], width=12)
                            ])
                        ])
                    ], className="shadow-sm mb-4"),
                    id="collapse-whatif",
                    is_open=False
                ),
            ], width=12),

                # Income Sources List
                dbc.Row([
                    dbc.Col([
                        dbc.Card([
                            dbc.CardHeader(
                                html.H4("Income Sources", className="card-title m-0"),
                                className="d-flex flex-column",
                                style=HEADER_STYLE  # Apply HEADER_STYLE to the entire CardHeader
                            ),
                            dbc.CardBody([
                                html.Div(id="income-sources-container", className="income-sources-list"),
                                html.Div(id="no-income-sources-message", className="text-center py-4")
                            ], style={"backgroundColor": "#ffffff"})
                        ], className="shadow-sm", style={"border": "1px solid rgba(0,0,0,0.125)", "borderRadius": "4px"})
                    ], width=12)
                ]),

                # Historical Income Modal - update to match professional styling
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Edit Historical Income"), 
                                        style={"backgroundColor": "#f8f9fa", "borderBottom": "1px solid rgba(0,0,0,0.1)"}),
                        dbc.ModalBody(id="historical-income-modal-body"),
                        dbc.ModalFooter(
                            dbc.Button("Close", 
                                    id="close-history-modal", 
                                    className="ms-auto", 
                                    n_clicks=0,
                                    style={"backgroundColor": "#3498DB", "borderColor": "#3498DB"})
                        ),
                    ],
                    id="historical-income-modal",
                    size="lg",
                    is_open=False,
                ),

            ]),
        ], className="container-fluid mt-4"),

    # Client-side storage - use localStorage for better persistence across tab changes
    dcc.Store(id="income-sources-store", storage_type="local"),
    dcc.Store(id="total-income-store", data=0, storage_type="local"),
    dcc.Store(id="edit-income-id", storage_type="memory"),  # To track which income is being edited
    
    # Page initialization state
    dcc.Store(id="page-loaded", data=False, storage_type="session"),
    
    # An interval for page initialization
    dcc.Interval(id="income-tab-interval", interval=500, n_intervals=0, max_intervals=1),
    
    # Hidden div for triggering callbacks
    html.Div(id="hidden-div-trigger", style={"display": "none"}),

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

])

# Modified page initialization callback - handle initial page load
@callback(
    [Output("page-loaded", "data"),
     Output("income-sources-container", "children"),
     Output("no-income-sources-message", "children"),
     Output("total-income-display", "children"),
     Output("income-sources-count", "children"),
     Output("income-pie-chart", "figure"),
     Output("income-timeline-chart", "figure"),
     Output("income-source-whatif-dropdown", "options"),
     Output("income-source-whatif-dropdown", "value")],
    [Input("income-tab-interval", "n_intervals")],
    [State("income-sources-store", "data"),
     State("page-loaded", "data")],
)
def initialize_page(n_intervals, stored_income_sources, page_loaded):
    # Only run once when the page first loads
    if page_loaded:
        raise PreventUpdate
    
    # Ensure stored_income_sources is a valid list
    if stored_income_sources is None:
        stored_income_sources = []
    
    # Print for debugging
    print(f"Initializing page with {len(stored_income_sources)} sources")
    
    # Generate cards and other UI elements
    cards, no_sources_msg, total_display, sources_count = generate_income_cards(stored_income_sources)
    
    # Create pie chart
    pie_fig = create_pie_chart(stored_income_sources)
    
    # Create timeline chart
    timeline_fig = create_timeline_chart(stored_income_sources)
    
    # Create dropdown options for what-if analysis
    dropdown_options = [{"label": source.get("name", f"Income Source {i+1}"), "value": source["id"]} 
                       for i, source in enumerate(stored_income_sources)]
    dropdown_value = dropdown_options[0]["value"] if dropdown_options else None
    
    # Mark page as loaded
    return True, cards, no_sources_msg, total_display, sources_count, pie_fig, timeline_fig, dropdown_options, dropdown_value

# Add callback for opening the historical income modal
@callback(
    [Output("historical-income-modal", "is_open"),
     Output("historical-income-modal-body", "children"),
     Output("edit-income-id", "data")],
    [Input({"type": "edit-income", "index": ALL}, "n_clicks"),
     Input("close-history-modal", "n_clicks")],
    [State("historical-income-modal", "is_open"),
     State("income-sources-store", "data")]
)
def toggle_historical_modal(edit_clicks, close_clicks, is_open, income_sources):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    # Close modal if close button is clicked or if no trigger
    if triggered_id == "close-history-modal" or triggered_id == "":
        return False, [], None
    
    # Handle edit button click
    if "edit-income" in triggered_id:
        # Find which edit button was clicked
        for i, clicks in enumerate(edit_clicks):
            if clicks:
                button_id = json.loads(triggered_id)["index"]
                break
        else:
            raise PreventUpdate
        
        # Find the source data for this ID
        source_data = next((s for s in income_sources if s["id"] == button_id), None)
        if not source_data:
            return False, [], None
        
        # Create historical income form fields
        form_fields = create_historical_income_fields(button_id, source_data)
        
        # Return with modal open and the form fields
        return True, form_fields, button_id
    
    return is_open, [], None

# First we need to split the callback that saves historical income
# This callback will update the save status message
@callback(
    Output({"type": "historical-save-status", "index": MATCH}, "children"),
    [Input({"type": "save-historical", "index": MATCH}, "n_clicks")],
    [State({"type": "historical-income", "index": MATCH, "month": ALL}, "id"),
     State({"type": "historical-income", "index": MATCH, "month": ALL}, "value"),
     State("income-sources-store", "data"),
     State({"type": "save-historical", "index": MATCH}, "id")],
    prevent_initial_call=True
)
def update_historical_save_status(save_clicks, field_ids, field_values, income_sources, button_id):
    if not save_clicks or save_clicks <= 0:
        raise PreventUpdate
    
    # Get the source ID from the button ID
    source_id = button_id["index"]
    
    # Check if we can find the source
    source_exists = any(source["id"] == source_id for source in income_sources)
    if not source_exists:
        return html.Div("Error: Income source not found", className="alert alert-danger py-2")
    
    # If we found the source, return success message
    return html.Div("Historical data saved successfully!", className="alert alert-success py-2")

# This callback will update the income-sources-store data
@callback(
    Output("income-sources-store", "data", allow_duplicate=True),
    [Input({"type": "save-historical", "index": ALL}, "n_clicks")],
    [State({"type": "historical-income", "index": ALL, "month": ALL}, "id"),
     State({"type": "historical-income", "index": ALL, "month": ALL}, "value"),
     State("income-sources-store", "data"),
     State({"type": "save-historical", "index": ALL}, "id")],
    prevent_initial_call=True
)
def update_income_sources_with_historical(save_clicks_list, all_field_ids, all_field_values, income_sources, all_button_ids):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Check if any save button was clicked
    if not any(clicks and clicks > 0 for clicks in save_clicks_list):
        raise PreventUpdate
    
    # Find which save button was clicked
    for i, clicks in enumerate(save_clicks_list):
        if clicks and clicks > 0:
            button_id = all_button_ids[i]["index"]
            
            # Find the source in the income sources list
            for j, source in enumerate(income_sources):
                if source["id"] == button_id:
                    # Get just the field IDs and values for this source
                    # Group field IDs and values by source ID
                    source_field_ids = []
                    source_field_values = []
                    
                    for k, field_id in enumerate(all_field_ids):
                        if isinstance(field_id, dict) and field_id.get("index") == button_id:
                            source_field_ids.append(field_id)
                            source_field_values.append(all_field_values[k])
                    
                    # Create or update historical_data dictionary
                    historical_data = source.get("historical_data", {})
                    
                    # Populate with form values
                    for field_id, value in zip(source_field_ids, source_field_values):
                        month_key = field_id["month"]
                        historical_data[month_key] = value
                    
                    # Update the source data
                    income_sources[j]["historical_data"] = historical_data
                    
                    # Recalculate monthly average if variable
                    if source.get("consistency") == "variable":
                        # Calculate average from historical data
                        total = sum(historical_data.values())
                        count = len(historical_data)
                        if count > 0:
                            income_sources[j]["monthly_amount"] = total / count
                            # Update daily and weekly amounts
                            income_sources[j]["daily_amount"] = income_sources[j]["monthly_amount"] / 30.42
                            income_sources[j]["weekly_amount"] = income_sources[j]["monthly_amount"] / 4.33
                    
                    break
            
            break
    
    return income_sources

# Modify the manage_income_sources callback to properly handle existing data
@callback(
    [Output("income-sources-store", "data", allow_duplicate=True),
     Output("income-add-success-message", "children"),
     Output("income-source-name", "value"),
     Output("income-amount-input", "value")],
    [Input("add-income-button", "n_clicks"),
     Input({"type": "delete-income", "index": ALL}, "n_clicks")],
    [State("income-source-name", "value"),
     State("income-amount-input", "value"),
     State("income-frequency", "value"),
     State("income-type", "value"),
     State("income-consistency", "value"),
     State("income-category", "value"),
     State("income-sources-store", "data")],
    prevent_initial_call=True
)
def manage_income_sources(
    add_n_clicks, delete_n_clicks_list,
    source_name, amount, frequency, income_type, consistency, category,
    current_sources
):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    # Initialize current_sources if it doesn't exist
    if current_sources is None:
        current_sources = []

    # Determine which input triggered the callback
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Handle adding a new income source
    if triggered_id == "add-income-button":
        if add_n_clicks is None or add_n_clicks <= 0:
            raise PreventUpdate

        if not source_name or not amount:
            return current_sources, html.Div(
                "Please fill in all required fields.", className="alert alert-warning p-2"
            ), dash.no_update, dash.no_update

        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return current_sources, html.Div(
                "Amount must be a valid number.", className="alert alert-warning p-2"
            ), dash.no_update, dash.no_update

        # Normalize monthly amount based on frequency
        monthly_amount = amount
        if frequency == "weekly":
            monthly_amount = amount * 4.33
        elif frequency == "biweekly":
            monthly_amount = amount * 2.17
        elif frequency == "annually":
            monthly_amount = amount / 12

        # Calculate daily and weekly equivalents
        daily_amount = monthly_amount / 30.42
        weekly_amount = monthly_amount / 4.33

        # Create a unique income source
        income_id = str(uuid.uuid4())
        income_data = {
            "id": income_id,
            "name": source_name,
            "amount": amount,
            "monthly_amount": monthly_amount,
            "weekly_amount": weekly_amount,
            "daily_amount": daily_amount,
            "frequency": frequency,
            "type": income_type,
            "consistency": consistency,
            "category": category
        }

        # Append the new income source to the current list
        current_sources.append(income_data)

        # Return updated data and clear input fields
        success_msg = html.Div(
            f"Added {source_name} ({frequency}) as a new income source.",
            className="alert alert-success p-2"
        )
        return current_sources, success_msg, None, None

    # Handle deleting an income source
    elif "delete-income" in triggered_id:
        # Check if any delete button was clicked
        if not delete_n_clicks_list or all(n_clicks is None or n_clicks == 0 for n_clicks in delete_n_clicks_list):
            raise PreventUpdate

        # Find which delete button was clicked
        for i, n_clicks in enumerate(delete_n_clicks_list):
            if n_clicks:
                button_id = ctx.inputs_list[1][i]["id"]["index"]
                break
        else:
            raise PreventUpdate

        # Filter out the deleted source
        updated_sources = [source for source in current_sources if source["id"] != button_id]

        return updated_sources, None, dash.no_update, dash.no_update

    raise PreventUpdate

# Update all UI elements when income sources change
@callback(
    [Output("income-sources-container", "children", allow_duplicate=True),
     Output("no-income-sources-message", "children", allow_duplicate=True),
     Output("total-income-display", "children", allow_duplicate=True),
     Output("income-sources-count", "children", allow_duplicate=True),
     Output("income-pie-chart", "figure", allow_duplicate=True),
     Output("income-timeline-chart", "figure", allow_duplicate=True),
     Output("income-source-whatif-dropdown", "options", allow_duplicate=True),
     Output("income-source-whatif-dropdown", "value", allow_duplicate=True)],
    [Input("income-sources-store", "data")],
    prevent_initial_call=True
)
def update_all_ui_elements(income_sources):
    # Generate cards and other UI elements
    cards, no_sources_msg, total_display, sources_count = generate_income_cards(income_sources)
    
    # Create pie chart
    pie_fig = create_pie_chart(income_sources)
    
    # Create timeline chart
    timeline_fig = create_timeline_chart(income_sources)
    
    # Create dropdown options for what-if analysis
    dropdown_options = [{"label": source.get("name", f"Income Source {i+1}"), "value": source["id"]} 
                       for i, source in enumerate(income_sources)]
    dropdown_value = dropdown_options[0]["value"] if dropdown_options else None
    
    return cards, no_sources_msg, total_display, sources_count, pie_fig, timeline_fig, dropdown_options, dropdown_value

# What-if analysis result
@callback(
    Output("whatif-analysis-result", "children"),
    [Input("income-source-whatif-dropdown", "value")],
    [State("income-sources-store", "data")],
)
def update_whatif_analysis(source_id, sources):
    if not source_id or not sources:
        return html.Div("Select an income source to see the impact", className="text-muted")
    
    # Find the selected source
    selected_source = next((s for s in sources if s["id"] == source_id), None)
    
    if not selected_source:
        return html.Div("Income source not found", className="text-danger")
    
    source_name = selected_source.get("name", "Selected source")
    monthly_amount = selected_source.get("monthly_amount", 0)
    
    # Calculate total income
    total_income = sum(source.get("monthly_amount", 0) for source in sources)
    
    # Calculate new total
    new_total = total_income - monthly_amount
    
    # Calculate percentage decrease
    percent_decrease = (monthly_amount / total_income * 100) if total_income > 0 else 0
    
    return html.Div([
        html.Div([
            html.Div([
                html.H5("Current Monthly Income:", className="mb-0"),
                html.H5(f"£{total_income:,.2f}", className="text-primary mb-0")
            ], className="d-flex justify-content-between"),
            
            html.Div([
                html.H5("Without This Source:", className="mb-0"),
                html.H5(f"£{new_total:,.2f}", className="text-danger mb-0")
            ], className="d-flex justify-content-between"),
            
            html.Hr(),
            
            html.Div([
                html.H5("Impact:", className="mb-0"),
                html.H5([
                    f"-£{monthly_amount:,.2f}",
                    html.Small(f" ({percent_decrease:.1f}%)", className="ms-1")
                ], className="text-danger mb-0")
            ], className="d-flex justify-content-between"),
            
            html.Div([
                html.Small(f"If you lose {source_name}, your monthly income would decrease by {percent_decrease:.1f}%.")
            ], className="mt-3 fst-italic")
        ], className="p-3 border rounded")
    ])

@callback(
    Output("total-income-store", "data"),
    Input("income-sources-store", "data")
)
def update_total_income_store(income_sources):
    if not income_sources:
        return 0
    
    # Calculate total monthly income
    total_monthly = sum(source.get("monthly_amount", 0) for source in income_sources)
    return total_monthly

# Required function to make mobile nav work
@callback(
    Output("nav-menu", "className"),
    Input("mobile-nav-toggle", "n_clicks"),
    State("nav-menu", "className"),
    prevent_initial_call=True
)
def toggle_mobile_nav(n_clicks, current_class):
    if current_class == "nav-menu":
        return "nav-menu show"
    return "nav-menu"

# Import json for pattern-matching callbacks
import json

@callback(
    [Output("collapse-forecast", "is_open"),
     Output("collapse-whatif", "is_open")],
    [Input("toggle-forecast", "n_clicks"),
     Input("toggle-whatif", "n_clicks")],
    [State("collapse-forecast", "is_open"),
     State("collapse-whatif", "is_open")],
    prevent_initial_call=True
)
def toggle_sections(forecast_clicks, whatif_clicks, forecast_open, whatif_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if triggered_id == "toggle-forecast":
        return not forecast_open, False
    elif triggered_id == "toggle-whatif":
        return False, not whatif_open

    return False, False

@callback(
    [Output("toggle-forecast", "outline"),
     Output("toggle-whatif", "outline")],
    [Input("collapse-forecast", "is_open"),
     Input("collapse-whatif", "is_open")],
)
def update_button_styles(forecast_open, whatif_open):
    # If the section is open, remove the outline (highlight the button)
    forecast_outline = not forecast_open
    whatif_outline = not whatif_open
    return forecast_outline, whatif_outline