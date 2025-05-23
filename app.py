import dash
from dash import dcc, html, callback
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import psycopg2
import secrets
import os
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from dash.dependencies import Input, Output, State
from datetime import datetime, timedelta
import requests
from pages.feedback import add_feedback_to_app

# Load .env for the database URL
load_dotenv()

# DB Config
DATABASE_URL = os.getenv("DATABASE_URL")

# Flask Setup
server = Flask(__name__)
server.secret_key = secrets.token_hex(16)  # Set a random secret key

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'
login_manager.session_protection = "strong"
server.permanent_session_lifetime = timedelta(days=30)

# Dash Setup
app = dash.Dash(
    __name__,
    use_pages=True,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP, 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'],
    external_scripts=[
        {'src': '/assets/dashboard-draggable.js'},
    ],
    suppress_callback_exceptions=True,
    title="BlueCard Finance",
)

# Database connection function
def connect_db():
    return psycopg2.connect(DATABASE_URL)

# User model
class User(UserMixin):
    def __init__(self, user_id, email, password_hash):
        self.id = user_id
        self.email = email
        self.password_hash = password_hash

# Load user function (for Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(user_id=user_data[0], email=user_data[1], password_hash=user_data[2])
    return None

# Route for logout
@server.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect('/')

# API route for login
@server.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # Verify credentials
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data and check_password_hash(user_data[2], password):
        user = User(user_id=user_data[0], email=user_data[1], password_hash=user_data[2])
        login_user(user)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

# API route for signup
@server.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    email = data.get('email')
    print("Received data:", data)
    password = data.get('password')
    
    # Check if user exists
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        conn.close()
        return jsonify({"success": False, "message": "Email already exists"}), 400
    
    # Create new user
    hashed_password = generate_password_hash(password)
    cursor.execute(
        'INSERT INTO users (email, password_hash) VALUES (%s, %s)',
        (email, hashed_password)
    )
    conn.commit()
    
    # Get the new user ID
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        user = User(user_id=user_data[0], email=user_data[1], password_hash=user_data[2])
        login_user(user)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Error creating user"}), 500

# Dash Layout
app.layout = html.Div([

    # Session and Routing
    dcc.Location(id='url', refresh=False),

    dcc.Store(id="session-data-store", storage_type="local"),
    dcc.Interval(id="auth-check-trigger", interval=1, n_intervals=0, max_intervals=1),

    # Main Content
    html.Div(dash.page_container, id='page-content'),

    # Feedback form
    add_feedback_to_app(app),

    # Authentication Overlay
    html.Div(
        id='auth-overlay',
        style={
            'position': 'fixed',
            'top': 0,
            'left': 0,
            'width': '100%',
            'height': '100%',
            'backgroundColor': 'rgba(255, 255, 255, 0.7)',
            'backdropFilter': 'blur(3px)',
            'zIndex': 1000,
            'display': 'none',  # Toggle via callback
            'justifyContent': 'center',
            'alignItems': 'center',
            'pointerEvents': 'auto',
        },
        children=[
            dbc.Card(
                [
                    dbc.CardHeader(
                        dbc.Tabs(
                            [
                                dbc.Tab(label="Login", tab_id="login-tab", className="active"),
                                dbc.Tab(label="Sign Up", tab_id="signup-tab"),
                            ],
                            id="auth-tabs",
                            active_tab="login-tab",
                            className="mb-3"  # Optional spacing
                        )
                    ),
                    dbc.CardBody(id="auth-content")
                ],
                style={
                    "width": "24rem",
                    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.1)",
                    "borderRadius": "0.75rem",
                    "backgroundColor": "#ffffff",
                }
            )
        ]
    ),

    # Alert for login/signup messages
    dbc.Alert(id='auth-alert', is_open=False, duration=4000, fade=True)
])

# Create the login form content
def create_login_form():
    return [
        dbc.Input(id="login-email", type="email", placeholder="Email", className="mb-3"),
        dbc.Input(id="login-password", type="password", placeholder="Password", className="mb-3"),
        dbc.Button("Login", id="login-button", className="w-100 login-btn-primary-custom"),
        html.Div(id="login-feedback", className="mt-3")
    ]

# Create the signup form content
def create_signup_form():
    return [
        dbc.Input(id="signup-email", type="email", placeholder="Email", className="mb-3"),
        dbc.Input(id="signup-password", type="password", placeholder="Password", className="mb-3"),
        dbc.Input(id="signup-confirm", type="password", placeholder="Confirm Password", className="mb-3"),
        dbc.Button("Sign Up", id="signup-button", className="w-100 login-btn-primary-custom"),
        html.Div(id="signup-feedback", className="mt-3")
    ]

# Update the login callback to store user_id in session-data-store
@app.callback(
    [Output('login-feedback', 'children'),
     Output('session-data-store', 'data', allow_duplicate=True),
     Output('auth-overlay', 'style', allow_duplicate=True)],
    Input('login-button', 'n_clicks'),
    [State('login-email', 'value'),
     State('login-password', 'value')],
    prevent_initial_call=True
)
def process_login(n_clicks, email, password):
    if not n_clicks:
        return "", dash.no_update, dash.no_update

    if not email or not password:
        return dbc.Alert("Please fill all fields", color="danger"), dash.no_update, dash.no_update

    conn = connect_db()
    cursor = conn.cursor()
    
    # Debug query - print what's being searched
    print(f"Attempting login for email: {email}")
    
    # Make sure this matches your actual table structure
    cursor.execute('SELECT user_id, email, password_hash FROM users WHERE email = %s', (email,))
    user_data = cursor.fetchone()
    conn.close()
    
    # Debug - check if user was found
    if not user_data:
        print("No user found with that email")
        return dbc.Alert("Invalid email or password", color="danger"), dash.no_update, dash.no_update
    
    print(f"Found user: {user_data[0]}, {user_data[1]}")
    print(f"Stored hash: {user_data[2]}")
    
    # Check if the password hash verification is working
    is_valid = check_password_hash(user_data[2], password)
    print(f"Password valid: {is_valid}")

    if is_valid:
        user = User(user_id=user_data[0], email=user_data[1], password_hash=user_data[2])
        login_user(user, remember=True)

        session_data = {"user_id": user.id, "email": user.email}
        # Hide overlay after login
        overlay_style = {'display': 'none'}
        return dbc.Alert("Login successful", color="success"), session_data, overlay_style

    return dbc.Alert("Invalid email or password", color="danger"), dash.no_update, dash.no_update

# Callback for handling sign-up
@app.callback(
    [Output('signup-feedback', 'children', allow_duplicate=True),
     Output('session-data-store', 'data', allow_duplicate=True),  # Store session data after sign-up
     Output('url', 'pathname', allow_duplicate=True)],  
    Input('signup-button', 'n_clicks'),
    [State('signup-email', 'value'),
     State('signup-password', 'value'),
     State('signup-confirm', 'value')],
    prevent_initial_call=True
)
def process_signup(n_clicks, email, password, confirm_password):
    if not n_clicks:
        return "", dash.no_update, dash.no_update

    if not email or not password or not confirm_password:
        return dbc.Alert("Please fill all fields", color="danger"), dash.no_update, dash.no_update

    if password != confirm_password:
        return dbc.Alert("Passwords do not match", color="danger"), dash.no_update, dash.no_update

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        return dbc.Alert("Email already registered", color="danger"), dash.no_update, dash.no_update

    hashed_password = generate_password_hash(password)
    cursor.execute('INSERT INTO users (email, password_hash) VALUES (%s, %s)', (email, hashed_password))
    conn.commit()

    # Log the user in after successful sign-up
    user = User(user_id=cursor.lastrowid, email=email, password_hash=hashed_password)
    login_user(user, remember=True)

    session_data = {"user_id": user.id, "email": user.email}
    return dbc.Alert("Sign-up successful! You are now logged in.", color="success"), session_data, "/"


def get_monthly_active_users():
    conn = connect_db()
    cursor = conn.cursor()

    # Get users who logged in during the last 30 days
    cursor.execute("""
        SELECT COUNT(DISTINCT user_id) 
        FROM user_activity 
        WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
    """)
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

# Create user function
def create_user(cursor, email, password, is_paid_user=False):
    subscription_status = 'paid' if is_paid_user else 'free'
    query = """
    INSERT INTO users (email, password, subscription_status)
    VALUES (%s, %s, %s)
    """
    cursor.execute(query, (email, password, subscription_status))

# Update subscription status function
def update_subscription_status(cursor, user_id, new_status, subscription_length_days):
    if new_status == 'paid':
        subscription_start_date = datetime.now()
        expiration_date = datetime.now() + timedelta(days=subscription_length_days)
    else:
        subscription_start_date = None
        expiration_date = None
    
    query = """
    UPDATE users
    SET subscription_status = %s, 
        subscription_start_date = %s,
        subscription_expiration = %s
    WHERE id = %s
    """
    cursor.execute(query, (new_status, subscription_start_date, expiration_date, user_id))

# Get subscription status function
def get_subscription_status(cursor, user_id):
    query = "SELECT subscription_status FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    return result['subscription_status'] if result else None

# Allow all routes to pass through
@app.server.before_request
def protect_data_endpoints():
    # Restrict direct access to dashboard data endpoints for security
    if request.path.startswith('/api/') and not request.path.startswith('/api/login') and not request.path.startswith('/api/signup') and not current_user.is_authenticated:
        return redirect(url_for('login'))
    
from dash import callback_context

@callback( 
    Output("login-overlay", "style"), 
    [Input("session-data-store", "data"), 
     Input("url", "pathname")] 
) 
def update_login_overlay(session_data, pathname): 
    # Add debugging
    print(f"DEBUG - pathname: {pathname}")
    print(f"DEBUG - session_data: {session_data}")
    print(f"DEBUG - session_data type: {type(session_data)}")
    
    if pathname != '/chat': 
        return {'display': 'none'}
 
    if not session_data or 'user_id' not in session_data: 
        print("DEBUG - No valid session data found")
        return { 
            'display': 'flex',
            'backgroundColor': 'rgba(0, 0, 0, 0.7)', 
            'position': 'fixed', 
            'top': '0', 
            'left': '0', 
            'width': '100%', 
            'height': '100%', 
            'zIndex': '1000', 
            'justifyContent': 'center', 
            'alignItems': 'center', 
        } 
 
    print("DEBUG - Valid session found, hiding overlay")
    return {'display': 'none'}

@app.callback(
    Output("auth-content", "children"),
    Input("auth-tabs", "active_tab")
)
def update_auth_content(active_tab):
    if active_tab == "login-tab":
        return create_login_form()
    elif active_tab == "signup-tab":
        return create_signup_form()
    return ""

@app.callback(
    Output("auth-overlay", "style", allow_duplicate=True),
    [Input("auth-check-trigger", "n_intervals"),
     Input("url", "pathname")],
    [State("session-data-store", "data")],
    prevent_initial_call=True
)
def check_auth(n, pathname, session_data):
    if pathname == "/":
        return {"display": "none"}  # Hide overlay on landing page

    if session_data and session_data.get("user_id"):
        return {"display": "none"}  # User is logged in

    # Show overlay for all other cases
    return {
        'position': 'fixed',
        'top': 0,
        'left': 0,
        'width': '100%',
        'height': '100%',
        'backgroundColor': 'rgba(255, 255, 255, 0.4)',
        'backdropFilter': 'blur(2px)',
        'zIndex': 1000,
        'display': 'flex',
        'justifyContent': 'center',
        'alignItems': 'center',
        'pointerEvents': 'auto',
    }


app.clientside_callback(
    """
    function(n_intervals) {
        // Setup event listener for dashboard layout changes
        function setupListener() {
            document.addEventListener('dashboardLayoutChanged', function(event) {
                // Send position data to server
                const positionData = event.detail;
                return positionData;
            });
        }
        
        // Setup listener only once
        if (!window.dashboardListenerInitialized) {
            setupListener();
            window.dashboardListenerInitialized = true;
        }
        
        // Return no update initially
        return window.dash_clientside.no_update;
    }
    """,
    Output('dashboard-position-store', 'data'),
    Input('layout-update-interval', 'n_intervals')
)


# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))  # Render sets PORT as an env variable
    app.run(debug=False, host="0.0.0.0", port=port)
