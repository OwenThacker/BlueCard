import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask import Flask
import secrets
import os

# Create Flask server
server = Flask(__name__)
server.secret_key = secrets.token_hex(16)

# Create Dash app
app = dash.Dash(
    __name__,
    use_pages=True,
    server=server,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="BlueCard Finance"
)

# Global layout
app.layout = html.Div([
    dcc.Store(id='session-data-store', storage_type='local'),  # Add this here
    dash.page_container
])

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=True, host='0.0.0.0', port=port)