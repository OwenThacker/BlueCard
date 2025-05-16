# feedback_form.py
from dash import html, dcc, callback, Input, Output, State, dash, no_update, ctx
from dash.exceptions import PreventUpdate
from datetime import datetime

def create_feedback_form():
    """Create the feedback form with a hidden iframe for submission"""
    return html.Div([
        # Feedback button - with proper className
        # html.Button([
        #     html.I(className="fas fa-comment-alt", style={"marginRight": "8px"}),
        #     "Share Feedback"
        # ], 
        # id="feedback-toggle-btn",
        # className="feedback-toggle-btn",  # Using className as in your snippet
        # style={
        #     "backgroundColor": "#528AAE",
        #     "color": "white",
        #     "border": "none",
        #     "padding": "8px 12px",
        #     "borderRadius": "4px",
        #     "fontSize": "14px",
        #     "cursor": "pointer",
        #     "display": "flex",
        #     "alignItems": "center",
        #     "marginTop": "15px",
        #     "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
        #     "transition": "all 0.3s ease",
        #     "position": "fixed",
        #     "bottom": "20px",
        #     "right": "20px",
        #     "zIndex": "999",
        # }),
        
        # Feedback form modal/popup
        html.Div([
            # Close button
            html.Button(
                html.I(className="fas fa-times"), 
                id="feedback-close-btn",
                style={
                    "position": "absolute",
                    "top": "12px",
                    "right": "12px",
                    "background": "transparent",
                    "border": "none",
                    "color": "#333",
                    "fontSize": "16px",
                    "cursor": "pointer"
                }
            ),
            
            # Form header
            html.H4("We Value Your Feedback", style={
                "fontSize": "18px",
                "fontWeight": "600",
                "marginBottom": "15px",
                "color": "#333",
                "borderBottom": "2px solid #4CAF50",
                "paddingBottom": "10px"
            }),
            
            # Form fields
            dcc.Input(
                id="feedback-subject",
                type="text",
                placeholder="Subject",
                style={
                    "width": "100%",
                    "padding": "10px",
                    "marginBottom": "12px",
                    "borderRadius": "4px",
                    "border": "1px solid #ddd",
                    "fontSize": "14px"
                }
            ),
            
            dcc.Textarea(
                id="feedback-message",
                placeholder="Your message...",
                style={
                    "width": "100%",
                    "padding": "10px",
                    "marginBottom": "15px",
                    "borderRadius": "4px",
                    "border": "1px solid #ddd",
                    "minHeight": "120px",
                    "fontSize": "14px",
                    "resize": "vertical"
                }
            ),
            
            # Submit button
            html.Button(
                "Submit Feedback",
                id="feedback-submit-btn",
                style={
                    "width": "100%",
                    "backgroundColor": "#2196F3",
                    "color": "white",
                    "border": "none",
                    "padding": "12px",
                    "borderRadius": "4px",
                    "fontSize": "14px",
                    "fontWeight": "600",
                    "cursor": "pointer",
                    "transition": "all 0.3s ease"
                }
            ),
            
            # Status message area
            html.Div(id="feedback-status", style={
                "marginTop": "12px",
                "fontSize": "14px",
                "textAlign": "center",
                "padding": "8px",
                "borderRadius": "4px",
                "display": "none"
            }),
            
            # Hidden iframe for submission
            html.Iframe(
                id="hidden-form-target",
                name="hidden-form-target",
                style={"display": "none"}
            ),
            
            # This is the key part - the form that submits to Google
            html.Form([
                # Use the correct entry IDs for your Google Form
                dcc.Input(id="hidden-subject-field", type="hidden", name="entry.2089030541"),
                dcc.Input(id="hidden-message-field", type="hidden", name="entry.288083223"),
                
                # Add a timestamp field (optional)
                dcc.Input(id="timestamp-field", type="hidden", name="entry.timestamp"),
                
                # Hidden submit button
                html.Button("Submit", id="hidden-submit-btn", type="submit", style={"display": "none"})
            ],
            id="hidden-google-form",
            # IMPORTANT: Use the formResponse URL, not the viewform URL
            action="https://docs.google.com/forms/d/e/1FAIpQLSdmfcjCMhIWuw_BzlsH_0Eot3PP6TkT78Y6Gjp1kupjOE-saA/formResponse",
            method="post",
            target="hidden-form-target"
            )
            
        ], id="feedback-form-container", style={
            "position": "fixed",
            "width": "350px",
            "backgroundColor": "white",
            "boxShadow": "0 5px 20px rgba(0,0,0,0.25)",
            "borderRadius": "8px",
            "padding": "20px",
            "bottom": "80px",
            "right": "60px",
            "zIndex": "1000",
            "display": "none",
            "transition": "all 0.3s ease"
        })
    ])

# Register all the callback functions for the feedback form
def register_feedback_callbacks(app):
    # Toggle feedback form visibility - FIXED
    @app.callback(
        Output("feedback-form-container", "style"),
        [Input("feedback-toggle-btn", "n_clicks"),
         Input("feedback-close-btn", "n_clicks")],
        [State("feedback-form-container", "style")],
        prevent_initial_call=True
    )
    def toggle_feedback_form(open_clicks, close_clicks, current_style):
        # Fixed triggered_id check
        triggered_id = ctx.triggered_id
        
        if current_style is None:
            current_style = {}
        
        # Make a copy of the current style to avoid modifying the input dict
        new_style = dict(current_style)
        
        if triggered_id == "feedback-toggle-btn":
            new_style["display"] = "block"
        elif triggered_id == "feedback-close-btn":
            new_style["display"] = "none"
        
        return new_style

    # Add timestamp to form
    @app.callback(
        Output("timestamp-field", "value"),
        Input("feedback-submit-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def update_timestamp(n_clicks):
        if n_clicks is None:
            raise PreventUpdate
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Handle form submission and trigger the hidden form submit
    @app.callback(
        [Output("feedback-status", "children"),
         Output("feedback-status", "style"),
         Output("feedback-subject", "value"),
         Output("feedback-message", "value"),
         Output("hidden-subject-field", "value"),
         Output("hidden-message-field", "value")],
        Input("feedback-submit-btn", "n_clicks"),
        [State("feedback-subject", "value"),
         State("feedback-message", "value")],
        prevent_initial_call=True
    )
    def handle_feedback_submission(n_clicks, subject, message):
        if n_clicks is None:
            raise PreventUpdate
        
        # Validate inputs
        if not subject or not message:
            return (
                "Please fill in all fields", 
                {"display": "block", "backgroundColor": "#ffebee", "color": "#c62828", "border": "1px solid #ef9a9a"},
                subject, message,
                "", ""  # Don't update hidden fields if validation fails
            )
        
        # If validation passes, show success message
        return (
            "Thank you! Your feedback has been submitted.", 
            {"display": "block", "backgroundColor": "#e8f5e9", "color": "#2e7d32", "border": "1px solid #a5d6a7"},
            "", "",  # Clear form fields
            subject, message  # Update hidden fields with form values
        )

    # Add a client-side callback to trigger the form submission
    app.clientside_callback(
        """
        function(subject, message) {
            if(subject && message) {
                // Small timeout to ensure hidden fields are populated
                setTimeout(function() {
                    document.getElementById('hidden-submit-btn').click();
                }, 100);
            }
            return window.dash_clientside.no_update;
        }
        """,
        Output("hidden-google-form", "data-submitted", allow_duplicate=True),
        [Input("hidden-subject-field", "value"),
         Input("hidden-message-field", "value")],
        prevent_initial_call=True
    )

# Usage example in your main app
def add_feedback_to_app(app):
    """
    Helper function to add the feedback form to your app
    Call this in your main app.py file after creating your Dash app
    """
    # Add the feedback form to your app layout
    # Make sure to include it in the layout (typically at the end)
    feedback_form = create_feedback_form()
    
    # Register all callbacks
    register_feedback_callbacks(app)
    
    return feedback_form