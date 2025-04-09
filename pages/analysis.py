import dash
from dash import dcc, html, Input, Output, State, callback, ALL, ctx
import dash_bootstrap_components as dbc
from prophet import Prophet
import pandas as pd
import plotly.graph_objs as go
from datetime import date

dash.register_page(__name__, path="/savings", title="Savings Forecast", name="Savings Forecast")

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

CARD_STYLE = {
    'boxShadow': '0 4px 6px rgba(0, 0, 0, 0.1)',
    'borderRadius': '8px',
    'backgroundColor': COLORS['white'],
    'marginBottom': '20px'
}

HEADER_STYLE = {
    'backgroundColor': COLORS['primary'],
    'color': COLORS['white'],
    'borderBottom': f'2px solid {COLORS["accent"]}',
    'borderRadius': '8px 8px 0 0',
    'padding': '15px 20px',
    'fontWeight': 'bold',
    'fontSize': '16px'
}

layout = html.Div([
    # Hidden div for initialization
    html.Div(id='initialization-trigger', style={'display': 'none'}),
    
    # Header
    html.Div([
        html.Img(src="/assets/Logo_slogan.PNG", className="dashboard-logo"),
    
        # Navigation Bar
        html.Nav([
            html.Button([
                html.Span("BlueCard Finance", className="mobile-nav-toggle-text"),
                html.Span("≡")
            ], className="mobile-nav-toggle", id="mobile-nav-toggle"),

            html.Ul([
                html.Li(html.A([html.Span(className="nav-icon"), "Home"], href="/", className="nav-link"), className="nav-item"),
                html.Li([html.A([html.Span(className="nav-icon"), "Dashboard"], href="/dashboard", className="nav-link")], className="nav-item"),
                html.Li([html.A([html.Span(className="nav-icon"), "Income"], href="/income", className="nav-link")], className="nav-item"),
                html.Li([html.A([html.Span(className="nav-icon"), "Expenses"], href="/expenses", className="nav-link")], className="nav-item"),
                html.Li([html.A([html.Span(className="nav-icon"), "Savings Analysis"], href="/savings", className="nav-link active")], className="nav-item"),
            ], className="nav-menu", id="nav-menu")
        ], className="nav-bar"),
    ], className="header-container"),

    # Main Content Container
    html.Div([
        # Breadcrumb
        html.Ul([
            html.Li([html.A("Home", href="/", className="breadcrumb-link")], className="breadcrumb-item"),
            html.Li("Savings Analysis", className="breadcrumb-item breadcrumb-current")
        ], className="breadcrumb mb-4", style={'backgroundColor': COLORS['light'], 'borderRadius': '8px'}),

        html.H3("Savings Forecast", className="section-title mb-4", 
                style={'color': COLORS['primary'], 'borderBottom': f'2px solid {COLORS["accent"]}', 'paddingBottom': '10px'}),

        # Main content row with cards
        dbc.Row([
            # Left column with input forms
            dbc.Col([
                # Savings Entry Card
                html.Div([
                    html.Div("Add Savings Entry", style=HEADER_STYLE),
                    html.Div([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Amount (£)", className="form-label"),
                                dcc.Input(
                                    id='input-savings-amount',
                                    type='number',
                                    placeholder='Enter amount',
                                    value=100,
                                    className='form-control mb-3'
                                ),
                            ]),
                            dbc.Col([
                                html.Label("Date", className="form-label"),
                                dcc.DatePickerSingle(
                                    id='input-savings-date',
                                    date=date.today(),
                                    display_format='YYYY-MM-DD',
                                    className='mb-3 w-100'
                                ),
                            ]),
                        ]),
                        dbc.Button(
                            [html.I(className="fas fa-plus mr-2"), "Add Savings"], 
                            id='btn-add-savings', 
                            color='primary', 
                            className='w-100 mb-3'
                        ),
                    ], style={'padding': '20px'})
                ], style=CARD_STYLE),
                
                # Goal Setting Card
                html.Div([
                    html.Div("Set a Savings Goal", style=HEADER_STYLE),
                    html.Div([
                        html.Label("Goal Name", className="form-label"),
                        dcc.Input(
                            id='goal-name',
                            type='text',
                            placeholder='Goal name (e.g. New Car)',
                            className='form-control mb-3'
                        ),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Target Amount (£)", className="form-label"),
                                dcc.Input(
                                    id='goal-amount',
                                    type='number',
                                    placeholder='Target Amount',
                                    className='form-control mb-3'
                                ),
                            ]),
                            dbc.Col([
                                html.Label("Target Date", className="form-label"),
                                dcc.DatePickerSingle(
                                    id='goal-date',
                                    date=date.today(),
                                    display_format='YYYY-MM-DD',
                                    className='mb-3 w-100'
                                ),
                            ]),
                        ]),
                        dbc.Button(
                            [html.I(className="fas fa-bullseye mr-2"), "Add Goal"], 
                            id='btn-add-goal', 
                            color='primary', 
                            className='w-100 mb-2'
                        ),
                    ], style={'padding': '20px'})
                ], style=CARD_STYLE),
                
                # Data Tables Section - Modified to use dropdown instead of tabs
                html.Div([
                    html.Div("Data Management", style=HEADER_STYLE),
                    html.Div([
                        # Dropdown for selecting data view
                        html.Div([
                            html.Label("Select Data View", className="form-label"),
                            dcc.Dropdown(
                                id='data-view-dropdown',
                                options=[
                                    {'label': 'Hide Tables', 'value': 'none'},
                                    {'label': 'Savings Entries', 'value': 'savings'},
                                    {'label': 'Goals', 'value': 'goals'}
                                ],
                                value='none',
                                clearable=False,
                                className='mb-3'
                            ),
                        ]),
                        
                        # Container for the selected data view
                        html.Div(id='data-view-container', className='mt-3')
                    ], style={'padding': '20px'})
                ], style=CARD_STYLE),
            ], md=4),

            # Right column with graph
            dbc.Col([
                html.Div([
                    html.Div("Forecast Visualization", style=HEADER_STYLE),
                    html.Div([
                        dcc.Graph(
                            id='savings-forecast-graph',
                            config={'displayModeBar': True, 'scrollZoom': True},
                            style={'height': '700px'}
                        )
                    ], style={'padding': '20px'})
                ], style=CARD_STYLE)
            ], md=8)
        ]),

        dcc.Store(id='savings-store', storage_type='local'),
        dcc.Store(id='goals-store', storage_type='local'),
        dcc.Store(id='forecast-data-store', storage_type='session')  # Store for tracking forecast data
    ], style={'padding': '20px', 'backgroundColor': COLORS['light']}),

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
        "boxShadow": "0px -4px 10px rgba(0,0,0,0.1)",
        "padding": "0",
    })
], style={"width": "100%", "margin": "0", "padding": "0"})


# Add callback to initialize the stores when the page loads
@callback(
    [Output('savings-store', 'data', allow_duplicate=True),
     Output('goals-store', 'data', allow_duplicate=True)],
    Input('initialization-trigger', 'children'),  # Using a guaranteed page load trigger
    State('savings-store', 'data'),
    State('goals-store', 'data'),
    prevent_initial_call='initial_duplicate'  # This special value allows both initial call and duplicates
)
def initialize_stores(_, savings_data, goals_data):
    # Only initialize if data doesn't exist
    if savings_data is None:
        savings_data = {'records': []}
    if goals_data is None:
        goals_data = {'goals': []}
    return savings_data, goals_data

@callback(
    Output('savings-store', 'data', allow_duplicate=True),
    Input('btn-add-savings', 'n_clicks'),
    State('savings-store', 'data'),
    State('input-savings-amount', 'value'),
    State('input-savings-date', 'date'),
    prevent_initial_call=True
)
def save_savings(n_clicks, store_data, amount, date_val):
    if not amount or not date_val or n_clicks is None:
        raise dash.exceptions.PreventUpdate

    if store_data is None:
        store_data = {'records': []}

    new_record = {'amount': amount, 'date': date_val}
    store_data['records'].append(new_record)

    return store_data


@callback(
    [Output('savings-forecast-graph', 'figure'),
     Output('forecast-data-store', 'data')],  # Store the forecast data for status checking
    Input('savings-store', 'data'),
    Input('goals-store', 'data')
)
def update_forecast(data, goal_data):
    forecast_data = None  # Initialize forecast data
    
    if not data or not data.get('records'):
        return go.Figure().update_layout(
            title='No Data to Forecast',
            template='plotly_white',
            height=700,
            font={'family': 'Arial, sans-serif'},
        ), forecast_data

    # Prepare the data
    df = pd.DataFrame(data['records'])
    df['date'] = pd.to_datetime(df['date'])
    df = df.groupby('date').sum().reset_index()
    df = df.sort_values('date')

    df_prophet = df.rename(columns={'date': 'ds', 'amount': 'y'})

    if len(df_prophet) < 2:
        return go.Figure().update_layout(
            title='Not enough data to forecast',
            template='plotly_white',
            height=700,
            font={'family': 'Arial, sans-serif'}
        ), forecast_data

    # Fit the Prophet model
    model = Prophet(
        changepoint_prior_scale=0.2,  # Lower value to reduce sensitivity to trend changes
        yearly_seasonality=False,
        weekly_seasonality=True,
        daily_seasonality=True,
        seasonality_mode='additive',
        interval_width=0.95
    )
    model.fit(df_prophet)

    # Make future predictions
    future = model.make_future_dataframe(periods=30 * 12)
    forecast = model.predict(future)
    
    # Store forecast data for goal tracking
    forecast_data = forecast.to_dict('records')

    # Create the Plotly figure
    fig = go.Figure()

    # Add confidence intervals (shaded region)
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_upper'],
        mode='lines',
        line=dict(width=0),
        name='Upper Confidence',
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat_lower'],
        mode='lines',
        fill='tonexty',
        fillcolor='rgba(52, 152, 219, 0.2)',  # Light blue fill
        line=dict(width=0),
        name='Confidence Interval',
        showlegend=True
    ))

    # Add forecast points (line)
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color=COLORS['accent'], width=3),
    ))

    # Add actual data points (scatter + line combo)
    fig.add_trace(go.Scatter(
        x=df_prophet['ds'],
        y=df_prophet['y'],
        mode='lines+markers',
        name='Actual',
        line=dict(color=COLORS['primary'], width=3),
        marker=dict(color=COLORS['primary'], size=8)
    ))

    # Plot goals if any - using horizontal line with center dot as requested
    if goal_data and goal_data.get('goals'):
        for goal in goal_data['goals']:
            goal_date = pd.to_datetime(goal['date'])
            goal_amount = goal['amount']
            goal_name = goal.get('name', "Unnamed Goal")  # Use "Unnamed Goal" if 'name' is missing

            # Draw a small horizontal dash
            fig.add_trace(go.Scatter(
                x=[goal_date - pd.Timedelta(days=5), goal_date + pd.Timedelta(days=5)],  # Creates a small dash
                y=[goal_amount, goal_amount],
                mode='lines',
                line=dict(color='darkorange', width=2),
                showlegend=False
            ))

            # Add a dot in the center with label
            fig.add_trace(go.Scatter(
                x=[goal_date],
                y=[goal_amount],
                mode='markers+text',
                marker=dict(color='darkorange', size=10, symbol='circle'),
                text=[goal_name],
                textposition="top center",
                textfont=dict(color='darkorange', size=12),
                showlegend=False  # Hide goal from legend
            ))

    # Update layout with more professional styling
    fig.update_layout(
        title={
            'text': 'Savings Forecast with Confidence Intervals',
            'y': 0.98,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=18, color=COLORS['dark'])
        },
        xaxis_title={
            'text': 'Date',
            'font': dict(size=14, color=COLORS['dark'])
        },
        yaxis_title={
            'text': 'Cumulative Savings (£)',
            'font': dict(size=14, color=COLORS['dark'])
        },
        template='plotly_white',
        height=700,
        legend={
            'orientation': "h",
            'y': -0.15,
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=12)
        },
        margin=dict(t=60, b=80, l=60, r=40),
        paper_bgcolor='white',
        plot_bgcolor='white',
        font={'family': 'Arial, sans-serif'},
        hovermode='closest',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(230, 230, 230, 0.8)',
            showline=True,
            linecolor='rgba(200, 200, 200, 1)',
            linewidth=1
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(230, 230, 230, 0.8)',
            showline=True,
            linecolor='rgba(200, 200, 200, 1)',
            linewidth=1,
            tickprefix='£'
        )
    )

    return fig, forecast_data


# Create savings table content
def create_savings_table(data):
    if not data or not data.get('records'):
        return html.Div([
            html.I(className="fas fa-info-circle mr-2", style={'color': COLORS['accent']}),
            html.Span("No savings data available. Add your first entry above.", className="text-muted")
        ], className="text-center py-4")

    df = pd.DataFrame(data['records'])
    if df.empty:
        return html.Div([
            html.I(className="fas fa-info-circle mr-2", style={'color': COLORS['accent']}),
            html.Span("No savings data available. Add your first entry above.", className="text-muted")
        ], className="text-center py-4")
        
    df['index'] = df.index  # Add index for deletion

    table_header = [
        html.Thead(html.Tr([
            html.Th("Date", style={'width': '40%', 'fontWeight': '600', 'color': COLORS['primary']}),
            html.Th("Amount (£)", style={'width': '40%', 'fontWeight': '600', 'color': COLORS['primary']}),
            html.Th("Action", style={'width': '20%', 'fontWeight': '600', 'color': COLORS['primary']})
        ], className="table-header", style={'backgroundColor': COLORS['light']}))
    ]

    rows = []
    for _, row in df.iterrows():
        rows.append(html.Tr([
            html.Td(pd.to_datetime(row['date']).strftime('%Y-%m-%d'), 
                   style={'verticalAlign': 'middle'}),
            html.Td(f"£{row['amount']:,.2f}", 
                   style={'verticalAlign': 'middle', 'fontWeight': '500'}),
            html.Td(
                dbc.Button(
                    "Remove",
                    id={'type': 'delete-entry-btn', 'index': row['index']},
                    color='light',
                    size='sm',
                    outline=True,
                    style={
                        'borderRadius': '4px',
                        'fontSize': '12px',
                        'fontWeight': '500',
                        'color': COLORS['danger'],
                        'borderColor': COLORS['danger'],
                        'transition': 'all 0.2s',
                        'width': '100%'
                    }
                ),
                style={'textAlign': 'center', 'verticalAlign': 'middle'}
            )
        ], style={'borderBottom': f'1px solid {COLORS["light"]}'}, className='hover-row'))

    table_body = [html.Tbody(rows)]

    return html.Div([
        dbc.Table(
            table_header + table_body, 
            bordered=False,
            striped=False,
            hover=True, 
            responsive=True, 
            className='mt-3 table-sm shadow-sm',
            style={
                'borderCollapse': 'separate',
                'borderSpacing': '0',
                'width': '100%',
                'borderRadius': '8px',
                'overflow': 'hidden',
                'backgroundColor': COLORS['white']
            }
        )
    ], style={'padding': '5px'})


def check_goal_status(goal, forecast_data):
    """Check if a goal is on track based on forecast data"""
    if not forecast_data:
        return None  # No forecast data to determine status
        
    # Convert forecast data to DataFrame
    forecast_df = pd.DataFrame(forecast_data)
    
    # Convert date strings to datetime objects
    forecast_df['ds'] = pd.to_datetime(forecast_df['ds'])
    goal_date = pd.to_datetime(goal['date'])
    
    # Find the forecast value closest to the goal date
    closest_forecast = forecast_df.iloc[forecast_df['ds'].sub(goal_date).abs().argsort()[:1]]
    
    if closest_forecast.empty:
        return None
    
    # Get the predicted value
    predicted_value = closest_forecast['yhat'].values[0]
    
    # Compare with goal amount
    if predicted_value >= goal['amount']:
        return "On Track"
    else:
        return "Off Track"


# Create goals table content
def create_goals_table(data, forecast_data):
    if not data or not data.get('goals'):
        return html.Div([
            html.I(className="fas fa-info-circle mr-2", style={'color': COLORS['accent']}),
            html.Span("No goals set yet. Add your first goal above.", className="text-muted")
        ], className="text-center py-4")

    df = pd.DataFrame(data['goals'])
    if df.empty:
        return html.Div([
            html.I(className="fas fa-info-circle mr-2", style={'color': COLORS['accent']}),
            html.Span("No goals set yet. Add your first goal above.", className="text-muted")
        ], className="text-center py-4")
        
    df['index'] = df.index  # Add index for deletion
    
    # Add status column
    df['status'] = df.apply(lambda row: check_goal_status(row, forecast_data), axis=1)

    table_header = [
        html.Thead(html.Tr([
            html.Th("Goal Name", style={'width': '25%', 'fontWeight': '600', 'color': COLORS['primary']}),
            html.Th("Amount (£)", style={'width': '20%', 'fontWeight': '600', 'color': COLORS['primary']}),
            html.Th("Target Date", style={'width': '20%', 'fontWeight': '600', 'color': COLORS['primary']}),
            html.Th("Status", style={'width': '20%', 'fontWeight': '600', 'color': COLORS['primary']}),
            html.Th("Action", style={'width': '15%', 'fontWeight': '600', 'color': COLORS['primary']})
        ], className="table-header", style={'backgroundColor': COLORS['light']}))
    ]

    rows = []
    for _, row in df.iterrows():
        # Define professional status indicator
        status_style = {
            'padding': '6px 12px',
            'borderRadius': '20px',
            'fontSize': '12px',
            'fontWeight': '600',
            'display': 'inline-block',
            'minWidth': '90px',
            'textAlign': 'center'
        }
        
        if row['status'] == 'On Track':
            status_badge = html.Span("ON TRACK", style={
                **status_style,
                'backgroundColor': 'rgba(46, 204, 113, 0.15)',
                'color': COLORS['success'],
                'border': f'1px solid {COLORS["success"]}'
            })
        elif row['status'] == 'Off Track':
            status_badge = html.Span("OFF TRACK", style={
                **status_style,
                'backgroundColor': 'rgba(231, 76, 60, 0.15)',  
                'color': COLORS['danger'],
                'border': f'1px solid {COLORS["danger"]}'
            })
        else:
            status_badge = html.Span("PENDING", style={
                **status_style,
                'backgroundColor': 'rgba(149, 165, 166, 0.15)',
                'color': COLORS['gray'],
                'border': f'1px solid {COLORS["gray"]}'
            })
            
        rows.append(html.Tr([
            html.Td(row['name'], style={'verticalAlign': 'middle', 'fontWeight': '500'}),
            html.Td(f"£{row['amount']:,.2f}", style={'verticalAlign': 'middle', 'fontWeight': '500'}),
            html.Td(pd.to_datetime(row['date']).strftime('%Y-%m-%d'), style={'verticalAlign': 'middle'}),
            html.Td(status_badge, style={'verticalAlign': 'middle'}),
            html.Td(
                dbc.Button(
                    "Remove",
                    id={'type': 'delete-goal-btn', 'index': row['index']},
                    color='light',
                    size='sm',
                    outline=True,
                    style={
                        'borderRadius': '4px',
                        'fontSize': '12px',
                        'fontWeight': '500',
                        'color': COLORS['danger'],
                        'borderColor': COLORS['danger'],
                        'transition': 'all 0.2s',
                        'width': '100%'
                    }
                ),
                style={'textAlign': 'center', 'verticalAlign': 'middle'}
            )
        ], style={'borderBottom': f'1px solid {COLORS["light"]}'}, className='hover-row'))

    table_body = [html.Tbody(rows)]

    return html.Div([
        dbc.Table(
            table_header + table_body, 
            bordered=False,
            striped=False,
            hover=True, 
            responsive=True, 
            className='mt-3 table-sm shadow-sm',
            style={
                'borderCollapse': 'separate',
                'borderSpacing': '0',
                'width': '100%',
                'borderRadius': '8px',
                'overflow': 'hidden',
                'backgroundColor': COLORS['white']
            }
        )
    ], style={'padding': '5px'})


# New callback to handle the data view dropdown
@callback(
    Output('data-view-container', 'children'),
    Input('data-view-dropdown', 'value'),
    Input('savings-store', 'data'),
    Input('goals-store', 'data'),
    Input('forecast-data-store', 'data')
)
def update_data_view(view_type, savings_data, goals_data, forecast_data):
    if view_type == 'none':
        return html.Div([
            html.I(className="fas fa-info-circle mr-2", style={'color': COLORS['accent']}),
            html.Span("Select a data view from the dropdown above.", className="text-muted")
        ], className="text-center py-4")
    elif view_type == 'savings':
        return create_savings_table(savings_data)
    elif view_type == 'goals':
        return create_goals_table(goals_data, forecast_data)
    
    # Default empty state
    return html.Div()


@callback(
    Output('savings-store', 'data'),
    Input({'type': 'delete-entry-btn', 'index': ALL}, 'n_clicks'),
    State('savings-store', 'data'),
    prevent_initial_call=True
)
def delete_savings_entry(n_clicks_list, store_data):
    if not any(n_clicks for n_clicks in n_clicks_list if n_clicks):
        raise dash.exceptions.PreventUpdate

    triggered_index = ctx.triggered_id['index']
    if store_data and 'records' in store_data:
        store_data['records'].pop(triggered_index)
    return store_data


@callback(
    Output('goals-store', 'data', allow_duplicate=True),  # Added allow_duplicate
    Input('btn-add-goal', 'n_clicks'),
    State('goals-store', 'data'),
    State('goal-name', 'value'),
    State('goal-amount', 'value'),
    State('goal-date', 'date'),
    prevent_initial_call=True
)
def add_goal(add_clicks, goals_data, name, amount, target_date):
    if add_clicks is None or not amount or not target_date:
        raise dash.exceptions.PreventUpdate
    
    # Initialize goals data if it doesn't exist
    if goals_data is None:
        goals_data = {'goals': []}
        
    # Add new goal
    new_goal = {
        'name': name or "Unnamed Goal",  # Fallback to "Unnamed Goal" if name is missing
        'amount': amount,
        'date': target_date
    }
    goals_data['goals'].append(new_goal)
    
    return goals_data


@callback(
    Output('goals-store', 'data'),
    Input({'type': 'delete-goal-btn', 'index': ALL}, 'n_clicks'),
    State('goals-store', 'data'),
    prevent_initial_call=True
)
def delete_goal(n_clicks_list, goals_data):
    if not any(n_clicks for n_clicks in n_clicks_list if n_clicks):
        raise dash.exceptions.PreventUpdate

    triggered_index = ctx.triggered_id['index']
    if goals_data and 'goals' in goals_data:
        goals_data['goals'].pop(triggered_index)
    return goals_data