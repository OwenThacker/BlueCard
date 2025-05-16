import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc

# Register this file as the pricing page
dash.register_page(__name__, path="/pricing", name="Pricing")

# Define a cohesive color palette matching the home page
COLORS = {
    'primary': '#1a365d',      # Dark blue - primary brand color
    'secondary': '#2a4a7f',    # Medium-dark blue
    'accent': '#4299e1',       # Bright blue - accent color
    'accent-light': '#90cdf4', # Light blue
    'background': '#f8fafc',   # Very light blue/grey background
    'white': '#ffffff',
    'grey-light': '#e2e8f0',
    'grey': '#718096',         # Medium grey for text
    'dark': '#2d3748'          # Dark grey/blue for headings
}

# Helper function to create a pricing card
def create_pricing_card(tier, price, period, description, features, cta_text, is_highlighted=False):
    highlight_style = {
        'transform': 'scale(1.05)',
        'boxShadow': '0 8px 30px rgba(0, 0, 0, 0.15)',
        'borderColor': COLORS['accent'],
        'zIndex': '10'
    } if is_highlighted else {}
    
    # Calculate yearly price with 20% discount if it's a paid plan
    yearly_price = None
    if price > 0:
        yearly_price = price * 12 * 0.8
    
    return html.Div([
        # Popular badge for highlighted plan - adjusted position down and right
        html.Div("MOST POPULAR", className="popular-badge", style={
            'position': 'absolute',
            'top': '30px',     # Moved down from default position
            'right': '-50px',   # Moved right from default position
            'backgroundColor': COLORS['accent'],
            'color': COLORS['white'],
            'padding': '10px 60px',
            'fontSize': '0.7rem',
            'fontWeight': '600',
            'borderRadius': '3px',
            'zIndex': '20'
        }) if is_highlighted else None,
        
        # Tier name
        html.H3(tier, className="pricing-tier-title", style={
            'color': COLORS['primary'],
            'marginBottom': '10px',
            'fontWeight': '600'
        }),
        
        # Price display
        html.Div([
            html.Span("£", className="currency", style={'fontSize': '1.5rem', 'verticalAlign': 'top', 'position': 'relative', 'top': '10px'}) if price > 0 else None,
            html.Span(f"{price}", className="price-amount", style={'fontSize': '3.5rem', 'fontWeight': '700', 'letterSpacing': '-2px'}) if price > 0 else html.Span("Free", style={'fontSize': '3rem', 'fontWeight': '700'}),
            html.Span(f"/{period}", className="price-period", style={'fontSize': '1rem', 'color': COLORS['grey']}) if price > 0 else None,
        ], className="pricing-price", style={'marginBottom': '20px'}),
        
        # Yearly pricing option for paid plans
        html.Div([
            html.Span("Annual: "),
            html.Span(f"£{yearly_price:.2f}", style={'fontWeight': '600'}),
            html.Span(" per year", style={'fontSize': '0.9rem'}),
            html.Div("Save 20%", className="save-badge"),
        ], className="yearly-option", style={
            'backgroundColor': COLORS['grey-light'],
            'padding': '8px 12px',
            'borderRadius': '5px',
            'marginBottom': '20px',
            'fontSize': '0.9rem',
            'position': 'relative',
            'textAlign': 'center'
        }) if yearly_price else None,
        
        # Description
        html.P(description, className="pricing-description", style={
            'color': COLORS['grey'],
            'marginBottom': '20px',
            'fontSize': '0.95rem',
            'lineHeight': '1.5'
        }),
        
        # Divider
        html.Hr(style={'margin': '20px 0', 'opacity': '0.2'}),
        
        # Features list
        html.Ul([
            html.Li([
                html.I(className="fas fa-check", style={'color': COLORS['accent'], 'marginRight': '10px'}),
                feature
            ], style={'marginBottom': '12px', 'fontSize': '0.95rem'}) for feature in features
        ], className="pricing-features", style={'listStyleType': 'none', 'padding': '0', 'marginBottom': '30px'}),
        
        # CTA Button
        html.Button(cta_text, className="pricing-cta-button", style={
            'backgroundColor': COLORS['accent'] if is_highlighted else COLORS['white'],
            'color': COLORS['white'] if is_highlighted else COLORS['accent'],
            'border': f"2px solid {COLORS['accent']}",
            'borderRadius': '5px',
            'padding': '12px 20px',
            'fontSize': '1rem',
            'fontWeight': '600',
            'width': '100%',
            'cursor': 'pointer',
            'transition': 'all 0.3s ease',
        }),
        
    ], className="pricing-card", style={
        'backgroundColor': COLORS['white'],
        'border': f"1px solid {COLORS['grey-light']}",
        'borderRadius': '10px',
        'padding': '30px',
        'width': '350px',
        'textAlign': 'center',
        'transition': 'all 0.3s ease',
        'position': 'relative',
        'overflow': 'hidden',
        **highlight_style
    })

# Layout for the Pricing page
layout = html.Div([

    # Session and Routing
    dcc.Store(id='session-data-store', storage_type='local'),
    dcc.Store(id='user-id', storage_type='local'),  # Make sure this is included
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='dropdown-state', data=False),
    
    # Dashboard Header and Navigation Bar
    html.Div([
        # Logo and Title
        html.Div([
            html.Img(src="/assets/Logo_slogan.PNG", className="dashboard-logo"),
        ], className="header-logo"),

        # Navigation Bar
        html.Nav([
            html.Button([
                html.Span("BlueCard Finance", className="mobile-nav-toggle-text"),
                html.Span("≡")
            ], className="mobile-nav-toggle", id="mobile-nav-toggle"),

            html.Ul([
                html.Li(html.A([html.Span(className="nav-icon"), "Home"], href="/", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "About"], href="/about", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Dashboard"], href="/chat", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Pricing"], href="/pricing", className="nav-link active"), className="nav-item"),
                # html.Li(html.A([html.Span(className="nav-icon"), "Dashboard"], href="/dashboard", className="nav-link"), className="nav-item"),
                # html.Li(html.A([html.Span(className="nav-icon"), "Income"], href="/income", className="nav-link"), className="nav-item"),
                # html.Li(html.A([html.Span(className="nav-icon"), "Expenses"], href="/expenses", className="nav-link"), className="nav-item"),
                # html.Li(html.A([html.Span(className="nav-icon"), "Savings Analysis"], href="/savings", className="nav-link"), className="nav-item"),
                # html.Li(html.A([html.Span(className="nav-icon"), "Settings"], href="/settings", className="nav-link"), className="nav-item")
            ], className="nav-menu", id="nav-menu"),

            # User account area (right side of navbar)
                html.Div([
                    # User profile dropdown
                    html.Div([
                        html.Button([
                            html.I(className="fas fa-user-circle", style={'fontSize': '24px'}),
                        ], id="user-dropdown-button", className="user-dropdown-button"),
                        
                        # Dropdown menu
                        html.Div([
                            html.Div(id="user-email-display", className="user-email"),
                            html.Hr(style={'margin': '8px 0'}),
                            html.A("Profile", href="/profile", className="dropdown-item"),
                            html.A("Logout", id="logout-link", href="/", className="dropdown-item")
                        ], id="user-dropdown-content", className="user-dropdown-content")
                    ], className="user-dropdown"),
                ], id="user-account-container", className="user-account-container"),

        ], className="nav-bar"),
    ], className="header-container", style={
        'backgroundColor': COLORS['white'],
        'borderBottom': f'1px solid {COLORS["accent-light"]}'
    }),

    # Page header
    html.Div([
        html.H1("Pricing Plans", className="pricing-title", style={
            'color': COLORS['dark'],
            'fontWeight': '700',
            'marginBottom': '10px',
            'fontSize': '2.5rem'
        }),
        html.P("Choose the perfect plan for your financial journey", className="pricing-subtitle", style={
            'color': COLORS['grey'],
            'fontSize': '1.2rem',
            'maxWidth': '700px',
            'margin': '0 auto 50px auto',
            'lineHeight': '1.6'
        }),
        
        # Pricing toggle (monthly/yearly)
        html.Div([
            html.Span("Monthly", className="toggle-option", style={'fontWeight': '600', 'color': COLORS['accent']}),
            dbc.Switch(id="billing-toggle", className="pricing-toggle"),
            html.Span("Yearly (20% off)", className="toggle-option", style={'fontWeight': '600'})
        ], className="pricing-toggle-container", style={
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'gap': '15px',
            'marginBottom': '40px'
        }),
        
    ], className="pricing-header", style={
        'textAlign': 'center',
        'paddingTop': '80px',
        'paddingBottom': '30px'
    }),
    
    # Pricing cards container
    html.Div([
        # Free tier
        create_pricing_card(
            tier="Basic",
            price=0,
            period="month",
            description="Get started with essential financial insights",
            features=[
                "Access to all AI insights",
                "5 dashboard components",
                "10 AI inputs per month",
                "Only 1 Dashboard Tab",
                "Email support"
            ],
            cta_text="Get Started Free",
            is_highlighted=False
        ),
        
        # Premium tier (highlighted)
        create_pricing_card(
            tier="Premium",
            price=12.99,
            period="month",
            description="Everything you need for comprehensive financial management",
            features=[
                "Unlimited dashboard components",
                "Unlimited AI inputs",
                "Up to 3 Dashboard Tabs",
                "Priority customer support",
            ],
            # cta_text="Start Premium",
            cta_text="Free for Beta Testers",
            is_highlighted=True
        ),
        
        # Enterprise tier
        create_pricing_card(
            tier="Enterprise",
            price=29.99,
            period="month",
            description="Advanced solutions for businesses and teams",
            features=[
                "All Premium features",
                "Unlimited Dashboard Tabs",
                "Multiple user accounts",
                "Team collaboration tools",
                "API access",
                "Custom integrations",
                "Dedicated account manager",
                "Compliance reporting"
            ],
            # cta_text="Contact Sales",
            cta_text="Coming Soon",
            is_highlighted=False
        ),
        
    ], className="pricing-cards-container", style={
        'display': 'flex',
        'justifyContent': 'center',
        'gap': '30px',
        'flexWrap': 'wrap',
        'marginBottom': '80px'
    }),
    
    # FAQ Section
    html.Div([
        html.H2("Frequently Asked Questions", style={
            'fontWeight': '600',
            'marginBottom': '30px',
            'fontSize': '1.8rem',
            'color': COLORS['dark']
        }),
        
        # FAQs using Accordion
        dbc.Accordion([
            dbc.AccordionItem(
                html.P("BlueCard Finance offers a free Basic plan with limited features. Our Premium plan is £12.99/month or £124.70/year (saving 20%), and our Enterprise plan is tailored for businesses starting at £29.99/month.", 
                       style={'lineHeight': '1.6', 'color': COLORS['grey']}),
                title="How much does BlueCard Finance cost?",
            ),
            dbc.AccordionItem(
                html.P("You can upgrade your plan at any time. Your new features will be available immediately, and you'll be charged the prorated difference for the remainder of your billing cycle.", 
                       style={'lineHeight': '1.6', 'color': COLORS['grey']}),
                title="Can I upgrade my plan later?",
            ),
            dbc.AccordionItem(
                html.P("Yes, you can cancel your subscription at any time. If you cancel, you'll maintain access to premium features until the end of your current billing cycle.", 
                       style={'lineHeight': '1.6', 'color': COLORS['grey']}),
                title="Is there a contract or can I cancel anytime?",
            ),
            dbc.AccordionItem(
                html.P("We offer a 14-day money-back guarantee for all new Premium and Enterprise subscriptions. If you're not satisfied, contact our support team within 14 days of your purchase.", 
                       style={'lineHeight': '1.6', 'color': COLORS['grey']}),
                title="Do you offer refunds?",
            ),
            dbc.AccordionItem(
                html.P("AI inputs are requests you make to our AI assistant for financial advice, analyses, or insights. The Basic plan includes 10 inputs per month, while Premium and Enterprise plans offer unlimited inputs.", 
                       style={'lineHeight': '1.6', 'color': COLORS['grey']}),
                title="What counts as an AI input?",
            ),
        ], id="faq-accordion", className="faq-accordion", style={
            'maxWidth': '800px',
            'margin': '0 auto',
        }),
        
    ], className="faq-section", style={
        'backgroundColor': COLORS['background'],
        'padding': '60px 20px',
        'textAlign': 'center',
        'borderRadius': '10px',
        'maxWidth': '1200px',
        'margin': '0 auto 80px auto'
    }),
    
    # Call to action section
    html.Div([
        html.H2("Ready to Take Control of Your Finances?", style={
            'color': COLORS['white'],
            'fontWeight': '600',
            'marginBottom': '20px',
            'fontSize': '2rem'
        }),
        html.P("Join thousands of users who have transformed their financial management with BlueCard Finance", style={
            'color': COLORS['white'],
            'marginBottom': '30px',
            'fontSize': '1.1rem',
            'maxWidth': '700px',
            'margin': '0 auto 30px auto',
            'lineHeight': '1.6',
            'opacity': '0.9'
        }),
        html.Button("Start Your Free Trial", className="cta-button", style={
            'backgroundColor': COLORS['white'],
            'color': COLORS['primary'],
            'border': 'none',
            'borderRadius': '5px',
            'padding': '15px 30px',
            'fontSize': '1.1rem',
            'fontWeight': '600',
            'cursor': 'pointer',
            'transition': 'all 0.3s ease',
        }),
    ], className="cta-section", style={
        'backgroundColor': COLORS['primary'],
        'padding': '80px 20px',
        'textAlign': 'center',
        'borderRadius': '10px',
        'maxWidth': '1200px',
        'margin': '0 auto 80px auto'
    }),
    
    # Testimonials section
    html.Div([
        html.H2("What Our Customers Say", style={
            'fontWeight': '600',
            'marginBottom': '50px',
            'fontSize': '1.8rem',
            'color': COLORS['dark']
        }),
        
        # Testimonial cards
        html.Div([
            # Testimonial 1
            html.Div([
                html.Div([
                    html.I(className="fas fa-quote-left", style={
                        'fontSize': '30px',
                        'color': COLORS['accent-light'],
                        'marginBottom': '20px'
                    }),
                    html.P("BlueCard Finance has completely transformed how I manage my money. The AI insights are remarkably accurate and have helped me save over £2,000 in just 6 months.", style={
                        'fontSize': '1.1rem',
                        'lineHeight': '1.7',
                        'marginBottom': '30px',
                        'color': COLORS['grey']
                    }),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-user-circle", style={
                                'fontSize': '50px',
                                'color': COLORS['grey']
                            }),
                        ], className="testimonial-avatar", style={
                            'marginRight': '15px'
                        }),
                        html.Div([
                            html.H4("Sarah Johnson", style={
                                'fontWeight': '600',
                                'margin': '0',
                                'color': COLORS['dark']
                            }),
                            html.P("Premium Member", style={
                                'color': COLORS['grey'],
                                'margin': '0'
                            })
                        ])
                    ], style={
                        'display': 'flex',
                        'alignItems': 'center'
                    })
                ], style={
                    'padding': '30px'
                })
            ], className="testimonial-card", style={
                'backgroundColor': COLORS['white'],
                'borderRadius': '10px',
                'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
                'width': '350px',
                'margin': '0 15px 30px 15px'
            }),
            
            # Testimonial 2
            html.Div([
                html.Div([
                    html.I(className="fas fa-quote-left", style={
                        'fontSize': '30px',
                        'color': COLORS['accent-light'],
                        'marginBottom': '20px'
                    }),
                    html.P("As a small business owner, the Enterprise plan gives me incredible insights into cash flow and expense trends. The unlimited AI inputs have been invaluable for financial planning.", style={
                        'fontSize': '1.1rem',
                        'lineHeight': '1.7',
                        'marginBottom': '30px',
                        'color': COLORS['grey']
                    }),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-user-circle", style={
                                'fontSize': '50px',
                                'color': COLORS['grey']
                            }),
                        ], className="testimonial-avatar", style={
                            'marginRight': '15px'
                        }),
                        html.Div([
                            html.H4("David Chen", style={
                                'fontWeight': '600',
                                'margin': '0',
                                'color': COLORS['dark']
                            }),
                            html.P("Enterprise Member", style={
                                'color': COLORS['grey'],
                                'margin': '0'
                            })
                        ])
                    ], style={
                        'display': 'flex',
                        'alignItems': 'center'
                    })
                ], style={
                    'padding': '30px'
                })
            ], className="testimonial-card", style={
                'backgroundColor': COLORS['white'],
                'borderRadius': '10px',
                'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
                'width': '350px',
                'margin': '0 15px 30px 15px'
            }),
            
            # Testimonial 3
            html.Div([
                html.Div([
                    html.I(className="fas fa-quote-left", style={
                        'fontSize': '30px',
                        'color': COLORS['accent-light'],
                        'marginBottom': '20px'
                    }),
                    html.P("Even the Basic plan helped me get started with budgeting. When I saw the value, upgrading to Premium was a no-brainer. The yearly discount makes it even more affordable.", style={
                        'fontSize': '1.1rem',
                        'lineHeight': '1.7',
                        'marginBottom': '30px',
                        'color': COLORS['grey']
                    }),
                    html.Div([
                        html.Div([
                            html.I(className="fas fa-user-circle", style={
                                'fontSize': '50px',
                                'color': COLORS['grey']
                            }),
                        ], className="testimonial-avatar", style={
                            'marginRight': '15px'
                        }),
                        html.Div([
                            html.H4("Emma Taylor", style={
                                'fontWeight': '600',
                                'margin': '0',
                                'color': COLORS['dark']
                            }),
                            html.P("Premium Member", style={
                                'color': COLORS['grey'],
                                'margin': '0'
                            })
                        ])
                    ], style={
                        'display': 'flex',
                        'alignItems': 'center'
                    })
                ], style={
                    'padding': '30px'
                })
            ], className="testimonial-card", style={
                'backgroundColor': COLORS['white'],
                'borderRadius': '10px',
                'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
                'width': '350px',
                'margin': '0 15px 30px 15px'
            }),
        ], style={
            'display': 'flex',
            'justifyContent': 'center',
            'flexWrap': 'wrap',
            'maxWidth': '1200px',
            'margin': '0 auto'
        }),
        
    ], className="testimonials-section", style={
        'padding': '60px 20px',
        'textAlign': 'center',
        'margin': '0 auto'
    }),

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
                    html.Li(html.A("About", href="/about", className="footer-link"), style={"marginBottom": "8px"}),
                    html.Li(html.A("Dashboard", href="/chat", className="footer-link"), style={"marginBottom": "8px"}),
                    html.Li(html.A("Pricing", href="/pricing", className="footer-link"), style={"marginBottom": "8px"}),
                ], style={
                    "listStyleType": "none",
                    "padding": "0",
                    "margin": "0"
                })
            ], className="footer-links", style={"flex": "1"}),
            
            # Right section with contact info and feedback form
            html.Div([
                html.H4("Contact & Feedback", style={
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
                        "bluecardfinance@outlook.com"
                    ], style={"marginBottom": "10px", "fontSize": "14px"}),
                    # html.P([
                    #     html.I(className="fas fa-phone", style={"width": "20px", "marginRight": "10px"}),
                    #     "(+44) 555-0XXX"
                    # ], style={"marginBottom": "10px", "fontSize": "14px"}),
                    html.P([
                        html.I(className="fas fa-map-marker-alt", style={"width": "20px", "marginRight": "10px"}),
                        "United Kingdom, London, LN"
                    ], style={"marginBottom": "10px", "fontSize": "14px"}),
                    
                    # Feedback button
                    html.Button([
                        html.I(className="fas fa-comment-alt", style={"marginRight": "8px"}),
                        "Share Feedback"
                    ], 
                    id="feedback-toggle-btn",
                    className="feedback-toggle-btn")
                ], className="footer-contact-info"),
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
                html.A(html.I(className="fab fa-facebook-f"), href="#", className="social-icon"),
                html.A(html.I(className="fab fa-twitter"), href="#", className="social-icon"),
                html.A(html.I(className="fab fa-linkedin-in"), href="#", className="social-icon"),
                html.A(html.I(className="fab fa-instagram"), href="#", className="social-icon")
            ], className="social-icons-container")
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
        }),
        
        # Feedback Form Modal (positioned fixed over the page)
        html.Div([
            # Close button
            html.Button(
                html.I(className="fas fa-times"), 
                id="feedback-close-btn",
                className="feedback-close-btn"
            ),
            
            # Form header
            html.H4("We Value Your Feedback", style={
                "fontSize": "18px",
                "fontWeight": "600",
                "marginBottom": "15px",
                "color": COLORS['dark'],
                "borderBottom": f"2px solid {COLORS['accent']}",
                "paddingBottom": "10px"
            }),
            
            # Form fields
            # dcc.Input(
            #     id="feedback-email",
            #     type="email",
            #     placeholder="Your Email",
            #     className="feedback-field"
            # ),
            
            dcc.Input(
                id="feedback-subject",
                type="text",
                placeholder="Subject",
                className="feedback-field"
            ),
            
            dcc.Textarea(
                id="feedback-message",
                placeholder="Your message...",
                className="feedback-field feedback-textarea"
            ),
            
            # Submit button
            html.Button(
                "Submit Feedback",
                id="feedback-submit-btn",
                className="feedback-submit-btn"
            ),
            
            # Status message area
            html.Div(id="feedback-status", className="feedback-status")
            
        ], id="feedback-form-container", className="feedback-form-container")
        
    ], className="dashboard-footer", style={
        "backgroundColor": COLORS['primary'],
        "color": "#ffffff",
        "boxShadow": "0px -4px 10px rgba(0,0,0,0.1)",
        "position": "relative"  # Needed for the modal positioning
    }),
    
], className="pricing-page-container", style={
    'backgroundColor': COLORS['background'],
    'fontFamily': '"Segoe UI", Arial, sans-serif',
    'color': COLORS['dark'],
    'minHeight': '100vh',
    'paddingBottom': '0px'
})

# Callbacks for pricing toggle and other interactive elements
@callback(
    Output("billing-toggle", "checked"),
    Input("billing-toggle", "checked"),
)
def toggle_billing_cycle(checked):
    # This is a placeholder - in a real app, you would update the prices shown based on toggle state
    return checked