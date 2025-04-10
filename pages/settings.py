from dash import html, dcc, callback, Input, Output, State
import dash
import datetime

# Register this file as a page
dash.register_page(__name__, path='/settings', name='Settings')

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

# Updated card styles
CARD_STYLE = {
    'borderRadius': '12px',  # More rounded corners
    'boxShadow': '0 6px 12px rgba(0, 0, 0, 0.1)',  # Subtle shadow
    'border': f'1px solid {COLORS["light"]}',  # Light border
    'backgroundColor': COLORS['white'],  # White background
    'padding': '15px',  # Add padding for better spacing
    'width': '100%'  # Full width
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

BUTTON_STYLE = {
    'backgroundColor': COLORS['accent'],
    'color': COLORS['white'],
    'border': 'none',
    'borderRadius': '8px',
    'padding': '10px 20px',
    'fontSize': '16px',
    'cursor': 'pointer',
    'transition': 'background-color 0.3s ease',
    'fontWeight': '500',
    'display': 'block',
    'margin': '20px auto',
}

DANGER_BUTTON_STYLE = {
    **BUTTON_STYLE,
    'backgroundColor': COLORS['danger'],
}

# Layout for the settings page
layout = html.Div([
    # Header container
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
                html.Li(html.A([html.Span(className="nav-icon"), "Expenses"], href="/expenses", className="nav-link"), className="nav-item"),
                html.Li([html.A([html.Span(className="nav-icon"), "Savings Analysis"], href="/savings", className="nav-link")], className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Settings"], href="/settings", className="nav-link active"), className="nav-item")
            ], className="nav-menu", id="nav-menu")
        ], className="nav-bar"),
    ], className="header-container"),

    # Corrected Breadcrumb - Full width
    html.Ul([
        html.Li([
            html.A("Home", href="/", className="breadcrumb-link")
        ], className="breadcrumb-item"),
        html.Li("Settings", className="breadcrumb-item breadcrumb-current")
    ], className="breadcrumb", style={
        'backgroundColor': COLORS['light'], 
        'borderRadius': '8px',
        'width': '100%',
        'margin': '0 0 20px 0',
        'padding': '10px 20px'
    }),

    # Main content - Full width
    html.Div([
        html.H2("Settings", className="section-title mb-4",
                style={
                    'color': COLORS['primary'], 
                    'borderBottom': f'2px solid {COLORS["accent"]}', 
                    'paddingBottom': '10px',
                    'width': '100%'
                }),
        
        # Settings panels - Using grid layout for responsive design
        html.Div([
            # Left column - Data Management Panel
            html.Div([
                html.Div([
                    html.H3("Data Management", style={'margin': '0', 'color': COLORS['white']})
                ], style=HEADER_STYLE),
                
                html.Div([
                    html.P("Manage your stored application data", style={'marginBottom': '20px'}),
                    
                    # Export data option
                    html.Div([
                        html.H4("Export Your Data", style={'color': COLORS['secondary'], 'marginBottom': '10px'}),
                        html.P("Download all your financial data as a JSON file for backup or transfer.", 
                               style={'marginBottom': '15px', 'fontSize': '14px'}),
                        html.Button("Export Data", id="export-data-button", style={
                            **BUTTON_STYLE,
                            'margin': '10px 0 20px',
                            'backgroundColor': COLORS['secondary'],
                        }),
                        html.Div(id="export-status", style={'marginBottom': '20px', 'color': COLORS['success']})
                    ], style={'marginBottom': '25px', 'borderBottom': f'1px solid {COLORS["light"]}', 'paddingBottom': '20px'}),
                    
                    # Reset data option
                    html.Div([
                        html.H4("Reset Application Data", style={'color': COLORS['danger'], 'marginBottom': '10px'}),
                        html.P("This will reset all stored data to default values. This action cannot be undone.", 
                               style={'marginBottom': '15px', 'fontSize': '14px'}),
                        html.Div([
                            html.Button("Reset All Data", id="reset-button", style=DANGER_BUTTON_STYLE),
                            html.Div(id="reset-confirmation", style={'display': 'none', 'marginTop': '15px', 'padding': '15px', 
                                                                     'backgroundColor': COLORS['light'], 'borderRadius': '8px'}, children=[
                                html.P("Are you sure? This action cannot be undone.", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                                html.Div([
                                    html.Button("Yes, Reset Data", id="confirm-reset", style={
                                        **DANGER_BUTTON_STYLE,
                                        'margin': '0 10px 0 0'
                                    }),
                                    html.Button("Cancel", id="cancel-reset", style={
                                        **BUTTON_STYLE,
                                        'backgroundColor': COLORS['muted'],
                                        'margin': '0'
                                    }),
                                ], style={'display': 'flex', 'justifyContent': 'center'})
                            ])
                        ]),
                        html.Div(id="reset-status", style={'marginTop': '15px', 'color': COLORS['success']})
                    ])
                ], style={'padding': '20px'})
            ], style={
                **CARD_STYLE, 
                'marginBottom': '30px'
            }, className="settings-card"),
            
            # Right column - Preferences Panel
            html.Div([
                html.Div([
                    html.H3("Application Preferences", style={'margin': '0', 'color': COLORS['white']})
                ], style=HEADER_STYLE),
                
                html.Div([
                    html.P("Customize your application experience", style={'marginBottom': '20px'}),
                    
                    # Currency preference
                    html.Div([
                        html.Label("Default Currency", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': '500'}),
                        dcc.Dropdown(
                            id='currency-preference',
                            options=[
                                {'label': '£ GBP - British Pound', 'value': 'GBP'},
                                {'label': '$ USD - US Dollar', 'value': 'USD'},
                                {'label': '€ EUR - Euro', 'value': 'EUR'},
                                {'label': '¥ JPY - Japanese Yen', 'value': 'JPY'},
                            ],
                            value='GBP',
                            clearable=False,
                            style={'borderRadius': '6px', 'border': f'1px solid {COLORS["light"]}'}
                        ),
                    ], style={'marginBottom': '20px'}),
                    
                    # Theme preference
                    html.Div([
                        html.Label("Theme", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': '500'}),
                        dcc.RadioItems(
                            id='theme-preference',
                            options=[
                                {'label': 'Light', 'value': 'light'},
                                {'label': 'Dark', 'value': 'dark'},
                                {'label': 'System Default', 'value': 'system'}
                            ],
                            value='light',
                            labelStyle={'marginRight': '15px', 'display': 'inline-block'}
                        ),
                    ], style={'marginBottom': '20px'}),
                    
                    # Date format preference
                    html.Div([
                        html.Label("Date Format", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': '500'}),
                        dcc.RadioItems(
                            id='date-format-preference',
                            options=[
                                {'label': 'DD/MM/YYYY', 'value': 'dd/mm/yyyy'},
                                {'label': 'MM/DD/YYYY', 'value': 'mm/dd/yyyy'},
                                {'label': 'YYYY-MM-DD', 'value': 'yyyy-mm-dd'}
                            ],
                            value='dd/mm/yyyy',
                            labelStyle={'marginRight': '15px', 'display': 'inline-block'}
                        ),
                    ], style={'marginBottom': '20px'}),
                    
                    # Save preferences button
                    html.Button("Save Preferences", id="save-preferences", style=BUTTON_STYLE),
                    html.Div(id="preferences-status", style={'textAlign': 'center', 'marginTop': '10px', 'color': COLORS['success']})
                ], style={'padding': '20px'})
            ], style={
                **CARD_STYLE
            }, className="settings-card"),
        ], style={
            'display': 'grid',
            'gridTemplateColumns': 'repeat(auto-fit, minmax(300px, 1fr))',
            'gap': '30px',
            'width': '100%',
            'margin': '0 auto 40px auto'
        }, className="settings-grid"),
    ], className="main-content", style={'padding': '20px', 'width': '100%', 'maxWidth': 'none'}),

    # Store components for data persistence
    dcc.Store(id='session-data-store', storage_type='local'),
    dcc.Store(id='total-income-store', storage_type='local'),
    dcc.Store(id='expenses-store', storage_type='local'),
    dcc.Store(id='total-expenses-store', storage_type='local'),
    dcc.Store(id='savings-target-store', storage_type='local'),
    dcc.Store(id='transaction-store', storage_type='local'),
    dcc.Store(id='preferences-store', storage_type='local'),
    dcc.Store(id='income-sources-store', storage_type='local'),
    dcc.Store(id='savings-store', storage_type='local'),
    dcc.Store(id='goals-store', storage_type='local'),
    dcc.Download(id="download-data"),

    # Footer - Keep as is per request
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
    }),
], style={'width': '100%'})  # Make the entire layout full width

# Callback to show reset confirmation
@callback(
    Output('reset-confirmation', 'style'),
    Input('reset-button', 'n_clicks'),
    prevent_initial_call=True
)
def show_reset_confirmation(n_clicks):
    if n_clicks:
        return {'display': 'block', 'marginTop': '15px', 'padding': '15px', 
                'backgroundColor': COLORS['light'], 'borderRadius': '8px'}
    return {'display': 'none'}

# Callback to cancel reset
@callback(
    [Output('reset-confirmation', 'style', allow_duplicate=True),
     Output('reset-button', 'n_clicks')],
    Input('cancel-reset', 'n_clicks'),
    prevent_initial_call=True
)
def cancel_reset(n_clicks):
    if n_clicks:
        return {'display': 'none'}, None
    return dash.no_update, dash.no_update


# Update this callback to properly handle the reset confirmation
@callback(
    [Output('session-data-store', 'data', allow_duplicate=True),
     Output('total-income-store', 'data', allow_duplicate=True),
     Output('expenses-store', 'data', allow_duplicate=True),
     Output('total-expenses-store', 'data', allow_duplicate=True),
     Output('savings-target-store', 'data', allow_duplicate=True),
     Output('transaction-store', 'data', allow_duplicate=True),
     Output('income-sources-store', 'data', allow_duplicate=True),
     Output('goals-store', 'data', allow_duplicate=True),  # Changed from style to data
     Output('savings-store', 'data', allow_duplicate=True),  # Changed from style to data
     Output('reset-status', 'children'),
     Output('reset-confirmation', 'style', allow_duplicate=True)],
    Input('confirm-reset', 'n_clicks'),
    prevent_initial_call=True
)
def reset_all_data(n_clicks):
    if n_clicks:
        # Default values for all stores
        default_session_data = {
            'salary': 0.0,
            'before_tax': True,
            'consistent_salary': True,
            'expenses': [],
            'daily_expenses': [],
            'savings_goals': [],
            'income_sources': []
        }
        default_total_income = 0
        default_expenses = []
        default_total_expenses = 0
        default_savings_target = 0
        default_transactions = []
        default_goals = {'goals': []}  # Default structure for goals-store
        default_savings = {'records': []}  # Default structure for savings-store
        
        return (
            default_session_data, 
            default_total_income, 
            default_expenses,
            default_total_expenses, 
            default_savings_target, 
            default_transactions,
            [],  # This clears the income-sources-store
            default_goals,  # Reset goals data
            default_savings,  # Reset savings data
            "All data has been reset successfully!",
            {'display': 'none'}
        )
    return dash.no_update

# Callback to save preferences
@callback(
    [Output('preferences-store', 'data'),
     Output('preferences-status', 'children')],
    [Input('save-preferences', 'n_clicks')],
    [State('currency-preference', 'value'),
     State('theme-preference', 'value'),
     State('date-format-preference', 'value'),
     State('preferences-store', 'data')],
    prevent_initial_call=True
)
def save_preferences(n_clicks, currency, theme, date_format, existing_prefs):
    if n_clicks:
        new_prefs = existing_prefs or {}
        new_prefs.update({
            'currency': currency,
            'theme': theme,
            'date_format': date_format,
            'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        return new_prefs, "Preferences saved successfully!"
    return dash.no_update, dash.no_update

# Callback to export data
@callback(
    [Output('download-data', 'data'),
     Output('export-status', 'children')],
    Input('export-data-button', 'n_clicks'),
    [State('session-data-store', 'data'),
     State('total-income-store', 'data'),
     State('expenses-store', 'data'),
     State('total-expenses-store', 'data'),
     State('savings-target-store', 'data'),
     State('transaction-store', 'data'),
     State('preferences-store', 'data')],
    prevent_initial_call=True
)
def export_data(n_clicks, session_data, total_income, expenses, total_expenses, savings_target, transactions, preferences):
    if n_clicks:
        export_data = {
            'session_data': session_data,
            'total_income': total_income,
            'expenses': expenses,
            'total_expenses': total_expenses,
            'savings_target': savings_target,
            'transactions': transactions,
            'preferences': preferences,
            'export_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return dict(
            content=str(export_data),
            filename=f"bluecard_finance_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        ), "Data exported successfully!"
    
    return dash.no_update, dash.no_update

# Load preferences on page load
@callback(
    [Output('currency-preference', 'value'),
     Output('theme-preference', 'value'),
     Output('date-format-preference', 'value')],
    Input('preferences-store', 'data')
)
def load_preferences(data):
    if data:
        return data.get('currency', 'GBP'), data.get('theme', 'light'), data.get('date_format', 'dd/mm/yyyy')
    return 'GBP', 'light', 'dd/mm/yyyy'