import dash
from dash import html, dcc, clientside_callback
import dash_bootstrap_components as dbc
from dash import Input, Output, State, callback
from utils.db import connect_db

# Register this file as the home page
dash.register_page(__name__, path="/", name="Home")

# Define a cohesive color palette with different shades of blue
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

# Layout for the Home page
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
                html.Li(html.A([html.Span(className="nav-icon"), "Home"], href="/", className="nav-link active"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "About"], href="/about", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Dashboard"], href="/chat", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Pricing"], href="/pricing", className="nav-link"), className="nav-item"),
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

    # Hero Section with Enhanced Design
    html.Div([
        html.Div([
            html.Div([
                html.H1("BlueCard Finance", className="hero-title", style={
                    'color': COLORS['white'],
                    'fontSize': '3.8rem',
                    'fontWeight': '700',
                    'marginBottom': '1rem',
                    'textShadow': '0 2px 8px rgba(0, 0, 0, 0.3)',
                    'letterSpacing': '1px',
                    'animation': 'slideDown 0.8s ease-out'
                }),
                html.P([
                    "Your trusted partner in ",
                    html.Span("financial management", style={
                        'color': COLORS['accent-light'], 
                        'fontWeight': '600',
                        'position': 'relative',
                        'display': 'inline-block',
                        'animation': 'pulse 2s infinite'
                    })
                ], className="hero-subtitle", style={
                    'color': COLORS['white'],
                    'fontSize': '1.5rem',
                    'marginBottom': '2rem',
                    'textShadow': '0 1px 3px rgba(0, 0, 0, 0.2)',
                    'animation': 'fadeIn 1.2s ease-in-out 0.5s both'
                }),
                dcc.Link(
                    dbc.Button(
                        "Get Started",
                        href="/dashboard",
                        className="hero-button",
                        style={
                            'backgroundColor': COLORS['accent'],
                            'border': 'none',
                            'color': COLORS['white'],
                            'padding': '15px 35px',
                            'fontSize': '1.2rem',
                            'borderRadius': '8px',
                            'fontWeight': '600',
                            'boxShadow': '0 4px 15px rgba(0, 0, 0, 0.15)',
                            'transition': 'all 0.3s ease',
                            'position': 'relative',
                            'overflow': 'hidden',
                            'animation': 'slideUp 1s ease-out 1s both'
                        }
                ),
                href='/chat'  # This is the URL the button will link to
            ),
            ], className="hero-content")
        ], className="hero-overlay", style={
            'backgroundImage': 'linear-gradient(135deg, rgba(26, 54, 93, 0.85) 0%, rgba(42, 74, 127, 0.65) 100%)',
            'width': '100%',
            'height': '100%',
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'padding': '0 20px'
        })
    ], className="hero-section", style={
        'backgroundImage': 'url("/assets/geodesign.png")',
        'backgroundSize': 'cover',
        'backgroundPosition': 'center',
        'height': '85vh',
        'position': 'relative',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'textAlign': 'center',
        'boxShadow': 'inset 0 -10px 20px rgba(0, 0, 0, 0.2)',
        'transition': 'background-position 0.5s ease-out, transform 0.5s ease-out',
    }),

    # Add these to your hero section with enhanced animations
    html.Div(className="floating-circle-1", style={
        'position': 'absolute',
        'width': '300px',
        'height': '300px',
        'borderRadius': '50%',
        'backgroundColor': 'rgba(255, 255, 255, 0.03)',
        'top': '20%',
        'left': '15%',
        'animation': 'float 8s ease-in-out infinite',
        'zIndex': '1'
    }),
    html.Div(className="floating-circle-2", style={
        'position': 'absolute',
        'width': '220px',
        'height': '220px',
        'borderRadius': '50%',
        'backgroundColor': 'rgba(144, 205, 244, 0.07)',
        'bottom': '15%',
        'right': '10%',
        'animation': 'float 12s ease-in-out infinite 1s',
        'zIndex': '1'
    }),
    # Add more floating elements for visual interest
    html.Div(className="floating-circle-3", style={
        'position': 'absolute',
        'width': '150px',
        'height': '150px',
        'borderRadius': '50%',
        'backgroundColor': 'rgba(255, 255, 255, 0.05)',
        'top': '30%',
        'right': '25%',
        'animation': 'float 10s ease-in-out infinite 0.5s',
        'zIndex': '1'
    }),
    html.Div(className="floating-circle-2", style={
        'position': 'absolute',
        'width': '100px',
        'height': '100px',
        'borderRadius': '50%',
        'backgroundColor': 'rgba(144, 205, 244, 0.05)',
        'bottom': '30%',
        'left': '25%',
        'animation': 'float 9s ease-in-out infinite 1.5s',
        'zIndex': '1'
    }),

    # Features Section with Enhanced Design and Animations
    html.Div([
        html.H2("Why Choose BlueCard Finance?", className="section-title", style={
            'color': COLORS['primary'],
            'textAlign': 'center',
            'fontSize': '2.5rem',
            'fontWeight': '600',
            'marginBottom': '3rem',
            'position': 'relative',
            'paddingBottom': '15px',
            'animation': 'fadeIn 1s ease-in-out'
        }),
        
        # Decorative line under the section title
        html.Div(style={
            'position': 'absolute',
            'width': '80px',
            'height': '4px',
            'backgroundColor': COLORS['accent'],
            'left': '50%',
            'transform': 'translateX(-50%)',
            'marginTop': '-2.7rem',
            'animation': 'slideInRight 1.2s ease-out'
        }),
        
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Img(
                            src="/assets/bar-chart.png",
                            alt="Bar Chart Icon",
                            className="feature-icon",
                            style={
                                "width": "60px", 
                                "height": "60px",
                                "marginBottom": "10px",
                                "animation": "pulse 2s infinite"
                            }
                        )
                    ], className="feature-icon-container", style={
                        'backgroundColor': COLORS['primary'],
                        'borderRadius': '50%',
                        'width': '100px',
                        'height': '100px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'margin': '0 auto 25px auto'
                    }),
                    html.H4("Track Your Finances", className="feature-title", style={
                        'color': COLORS['primary'],
                        'fontSize': '1.5rem',
                        'fontWeight': '600',
                        'marginBottom': '15px',
                        'textAlign': 'center'
                    }),
                    html.P("Monitor your income, expenses, and savings all in one place with intuitive visualizations and real-time updates.", 
                        className="feature-description",
                        style={
                            'color': COLORS['grey'],
                            'fontSize': '1.1rem',
                            'lineHeight': '1.6',
                            'textAlign': 'center'
                        }
                    )
                ], className="feature-card", style={
                    'padding': '30px 20px',
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '10px',
                    'boxShadow': '0 5px 15px rgba(0, 0, 0, 0.05)',
                    'height': '100%',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'alignItems': 'center',
                    'animation': 'fadeIn 0.8s ease-in-out, slideUp 0.8s ease-out'
                })
            ], md=4, style={'marginBottom': '30px'}),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Img(
                            src="/assets/goals.png",
                            alt="Goals Icon",
                            className="feature-icon",
                            style={
                                "width": "60px", 
                                "height": "60px",
                                "marginBottom": "5px",
                                "animation": "pulse 2s infinite 0.3s"
                            }
                        )
                    ], className="feature-icon-container", style={
                        'backgroundColor': COLORS['primary'],
                        'borderRadius': '50%',
                        'width': '100px',
                        'height': '100px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'margin': '0 auto 25px auto'
                    }),
                    html.H4("Set & Achieve Goals", className="feature-title", style={
                        'color': COLORS['primary'],
                        'fontSize': '1.5rem',
                        'fontWeight': '600',
                        'marginBottom': '15px',
                        'textAlign': 'center'
                    }),
                    html.P("Define your financial goals, track your progress, and receive personalized strategies to achieve them faster.", 
                        className="feature-description",
                        style={
                            'color': COLORS['grey'],
                            'fontSize': '1.1rem',
                            'lineHeight': '1.6',
                            'textAlign': 'center'
                        }
                    )
                ], className="feature-card", style={
                    'padding': '30px 20px',
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '10px',
                    'boxShadow': '0 5px 15px rgba(0, 0, 0, 0.05)',
                    'height': '100%',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'alignItems': 'center',
                    'animation': 'fadeIn 0.8s ease-in-out 0.2s, slideUp 0.8s ease-out 0.2s'
                })
            ], md=4, style={'marginBottom': '30px'}),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Img(
                            src="/assets/insight.png",
                            alt="Insights Icon",
                            className="feature-icon",
                            style={
                                "width": "60px", 
                                "height": "60px",
                                "marginBottom": "10px",
                                "animation": "pulse 2s infinite 0.6s"
                            }
                        )
                    ], className="feature-icon-container", style={
                        'backgroundColor': COLORS['primary'],
                        'borderRadius': '50%',
                        'width': '100px',
                        'height': '100px',
                        'display': 'flex',
                        'alignItems': 'center',
                        'justifyContent': 'center',
                        'margin': '0 auto 25px auto'
                    }),
                    html.H4("Smart Insights", className="feature-title", style={
                        'color': COLORS['primary'],
                        'fontSize': '1.5rem',
                        'fontWeight': '600',
                        'marginBottom': '15px',
                        'textAlign': 'center'
                    }),
                    html.P("Get actionable insights and recommendations based on your spending patterns to improve your financial health.", 
                        className="feature-description",
                        style={
                            'color': COLORS['grey'],
                            'fontSize': '1.1rem',
                            'lineHeight': '1.6',
                            'textAlign': 'center'
                        }
                    )
                ], className="feature-card", style={
                    'padding': '30px 20px',
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '10px',
                    'boxShadow': '0 5px 15px rgba(0, 0, 0, 0.05)',
                    'height': '100%',
                    'display': 'flex',
                    'flexDirection': 'column',
                    'alignItems': 'center',
                    'animation': 'fadeIn 0.8s ease-in-out 0.4s, slideUp 0.8s ease-out 0.4s'
                })
            ], md=4, style={'marginBottom': '30px'})
        ], className="features-row")
    ], className="features-section", style={
        'padding': '80px 40px',
        'backgroundColor': COLORS['background']
    }),

    # Testimonials Section with a different shade of blue and animated elements
    html.Div([
        html.H2("What Our Clients Say", className="section-title", style={
            'color': COLORS['white'],
            'textAlign': 'center',
            'fontSize': '2.5rem',
            'fontWeight': '600',
            'marginBottom': '3rem',
            'paddingBottom': '15px',
            'position': 'relative',
            'animation': 'fadeIn 1s ease-in-out'
        }),
        
        # Decorative line under the section title
        html.Div(style={
            'position': 'absolute',
            'width': '80px',
            'height': '4px',
            'backgroundColor': COLORS['accent-light'],
            'left': '50%',
            'transform': 'translateX(-50%)',
            'marginTop': '-2.7rem',
            'animation': 'slideInLeft 1.2s ease-out'
        }),
        
        # Animated stars background elements
        html.Div([
            html.Div(className="star-1", style={
                'position': 'absolute',
                'fontSize': '24px',
                'color': 'rgba(255, 255, 255, 0.3)',
                'top': '10%',
                'left': '10%',
                'animation': 'float 6s ease-in-out infinite'
            }, children="★"),
            html.Div(className="star-2", style={
                'position': 'absolute',
                'fontSize': '18px',
                'color': 'rgba(255, 255, 255, 0.3)',
                'top': '20%',
                'right': '15%',
                'animation': 'float 9s ease-in-out infinite 0.5s'
            }, children="★"),
            html.Div(className="star-3", style={
                'position': 'absolute',
                'fontSize': '30px',
                'color': 'rgba(255, 255, 255, 0.3)',
                'bottom': '15%',
                'left': '20%',
                'animation': 'float 7s ease-in-out infinite 1s'
            }, children="★"),
            html.Div(className="star-4", style={
                'position': 'absolute',
                'fontSize': '22px',
                'color': 'rgba(255, 255, 255, 0.3)',
                'bottom': '25%',
                'right': '10%',
                'animation': 'float 8s ease-in-out infinite 1.5s'
            }, children="★"),
        ]),
        
        # Testimonial Cards Row
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Img(src="/assets/avatar.png", alt="Client Avatar", className="testimonial-avatar", style={
                            'width': '70px',
                            'height': '70px',
                            'borderRadius': '50%',
                            'objectFit': 'cover',
                            'border': f'3px solid {COLORS["accent-light"]}',
                            'animation': 'pulse 3s infinite'
                        })
                    ], style={
                        'marginBottom': '15px',
                        'display': 'flex',
                        'justifyContent': 'center'
                    }),
                    html.Div([
                        html.I(className="fas fa-quote-left", style={
                            'fontSize': '24px',
                            'color': COLORS['accent-light'],
                            'marginRight': '8px',
                            'opacity': '0.6',
                            'animation': 'pulse 2s infinite'
                        }),
                    ], style={'marginBottom': '10px'}),
                    html.P("BlueCard Finance transformed how I manage my finances. The dashboard is intuitive, and I've saved more in 6 months than I did all of last year!", 
                        className="testimonial-text",
                        style={
                            'color': COLORS['white'],
                            'fontSize': '1.1rem',
                            'lineHeight': '1.7',
                            'marginBottom': '20px',
                            'fontStyle': 'italic'
                        }
                    ),
                    html.H5("Sarah Johnson", style={
                        'color': COLORS['white'],
                        'fontSize': '1.1rem',
                        'fontWeight': '600',
                        'marginBottom': '5px'
                    }),
                    html.P("Small Business Owner", style={
                        'color': COLORS['accent-light'],
                        'fontSize': '0.9rem'
                    })
                ], className="testimonial-card", style={
                    'padding': '30px 25px',
                    'backgroundColor': 'rgba(255, 255, 255, 0.1)',
                    'borderRadius': '10px',
                    'height': '100%',
                    'textAlign': 'center',
                    'backdropFilter': 'blur(10px)',
                    'boxShadow': '0 8px 20px rgba(0, 0, 0, 0.2)',
                    'animation': 'fadeIn 0.8s ease-in-out, slideInLeft 0.8s ease-out'
                })
            ], md=4, className="mb-4"),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Img(src="/assets/avatar.png", alt="Client Avatar", className="testimonial-avatar", style={
                            'width': '70px',
                            'height': '70px',
                            'borderRadius': '50%',
                            'objectFit': 'cover',
                            'border': f'3px solid {COLORS["accent-light"]}',
                            'animation': 'pulse 3s infinite 0.5s'
                        })
                    ], style={
                        'marginBottom': '15px',
                        'display': 'flex',
                        'justifyContent': 'center'
                    }),
                    html.Div([
                        html.I(className="fas fa-quote-left", style={
                            'fontSize': '24px',
                            'color': COLORS['accent-light'],
                            'marginRight': '8px',
                            'opacity': '0.6',
                            'animation': 'pulse 2s infinite 0.5s'
                        }),
                    ], style={'marginBottom': '10px'}),
                    html.P("The insights feature highlighted spending patterns I never noticed before. I've cut unnecessary expenses by 30% and reached my savings goal earlier than expected.", 
                        className="testimonial-text",
                        style={
                            'color': COLORS['white'],
                            'fontSize': '1.1rem',
                            'lineHeight': '1.7',
                            'marginBottom': '20px',
                            'fontStyle': 'italic'
                        }
                    ),
                    html.H5("Michael Torres", style={
                        'color': COLORS['white'],
                        'fontSize': '1.1rem',
                        'fontWeight': '600',
                        'marginBottom': '5px'
                    }),
                    html.P("Financial Analyst", style={
                        'color': COLORS['accent-light'],
                        'fontSize': '0.9rem'
                    })
                ], className="testimonial-card", style={
                    'padding': '30px 25px',
                    'backgroundColor': 'rgba(255, 255, 255, 0.1)',
                    'borderRadius': '10px',
                    'height': '100%',
                    'textAlign': 'center',
                    'backdropFilter': 'blur(10px)',
                    'boxShadow': '0 8px 20px rgba(0, 0, 0, 0.2)',
                    'animation': 'fadeIn 0.8s ease-in-out 0.2s, slideUp 0.8s ease-out 0.2s'
                })
            ], md=4, className="mb-4"),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Img(src="/assets/avatar.png", alt="Client Avatar", className="testimonial-avatar", style={
                            'width': '70px',
                            'height': '70px',
                            'borderRadius': '50%',
                            'objectFit': 'cover',
                            'border': f'3px solid {COLORS["accent-light"]}',
                            'animation': 'pulse 3s infinite 1s'
                        })
                    ], style={
                        'marginBottom': '15px',
                        'display': 'flex',
                        'justifyContent': 'center'
                    }),
                    html.Div([
                        html.I(className="fas fa-quote-left", style={
                            'fontSize': '24px',
                            'color': COLORS['accent-light'],
                            'marginRight': '8px',
                            'opacity': '0.6',
                            'animation': 'pulse 2s infinite 1s'
                        }),
                    ], style={'marginBottom': '10px'}),
                    html.P("Setting financial goals has never been easier. The visual progress trackers keep me motivated, and the personalized tips have been invaluable for my long-term planning.", 
                        className="testimonial-text",
                        style={
                            'color': COLORS['white'],
                            'fontSize': '1.1rem',
                            'lineHeight': '1.7',
                            'marginBottom': '20px',
                            'fontStyle': 'italic'
                        }
                    ),
                    html.H5("Emma Chen", style={
                        'color': COLORS['white'],
                        'fontSize': '1.1rem',
                        'fontWeight': '600',
                        'marginBottom': '5px'
                    }),
                    html.P("Marketing Director", style={
                        'color': COLORS['accent-light'],
                        'fontSize': '0.9rem'
                    })
                ], className="testimonial-card", style={
                    'padding': '30px 25px',
                    'backgroundColor': 'rgba(255, 255, 255, 0.1)',
                    'borderRadius': '10px',
                    'height': '100%',
                    'textAlign': 'center',
                    'backdropFilter': 'blur(10px)',
                    'boxShadow': '0 8px 20px rgba(0, 0, 0, 0.2)'
                })
            ], md=4, className="mb-4")
        ])
    ], className="testimonials-section", style={
        'padding': '80px 40px',
        'backgroundColor': COLORS['secondary'],  # Different shade of blue
        'backgroundImage': 'linear-gradient(135deg, rgba(42, 74, 127, 0.95) 0%, rgba(26, 54, 93, 0.95) 100%)',
        'color': COLORS['white'],
        'position': 'relative',
        'overflow': 'hidden'
    }),
    # # Then add this section before the statistics section
    # html.Div([
    #     html.Div([
    #         html.H2("Help Us Shape the Future of Personal Finance", className="section-title", style={
    #             'color': COLORS['white'],
    #             'textAlign': 'center',
    #             'fontSize': '2.3rem',
    #             'fontWeight': '600',
    #             'marginBottom': '1.5rem',
    #             'position': 'relative',
    #             'paddingBottom': '15px'
    #         }),
            
    #         # Decorative line under the section title
    #         html.Div(style={
    #             'position': 'absolute',
    #             'width': '80px',
    #             'height': '4px',
    #             'backgroundColor': COLORS['accent-light'],
    #             'left': '50%',
    #             'transform': 'translateX(-50%)',
    #             'marginTop': '-1.2rem'
    #         }),
            
    #         html.P("Interested in our future features and updates? Join our mailing list to share feedback and be the first to know about new tools that can improve your financial journey.", 
    #             className="mailing-list-description",
    #             style={
    #                 'color': COLORS['white'],
    #                 'fontSize': '1.2rem',
    #                 'maxWidth': '700px',
    #                 'margin': '0 auto 2rem auto',
    #                 'textAlign': 'center',
    #                 'lineHeight': '1.6'
    #             }),
            
    #         # Email signup form with animation
    #         html.Div([
    #             dbc.Input(
    #                 id="mailing-list-email",
    #                 type="email",
    #                 placeholder="Enter your email address",
    #                 style={
    #                     'border': 'none',
    #                     'borderRadius': '8px 0 0 8px',
    #                     'padding': '12px 20px',
    #                     'fontSize': '1.1rem',
    #                     'width': '100%',
    #                     'backgroundColor': 'rgba(255, 255, 255, 0.9)',
    #                     'boxShadow': 'inset 0 2px 5px rgba(0, 0, 0, 0.1)'
    #                 }
    #             ),
    #             dbc.Button(
    #                 "Subscribe",
    #                 id="subscribe-button",
    #                 className="signup-button",
    #                 style={
    #                     'backgroundColor': COLORS['accent-light'],
    #                     'border': 'none',
    #                     'borderRadius': '0 8px 8px 0',
    #                     'color': COLORS['primary'],
    #                     'fontWeight': '600',
    #                     'padding': '12px 25px',
    #                     'fontSize': '1.1rem',
    #                     'whiteSpace': 'nowrap',
    #                     'boxShadow': '0 4px 10px rgba(0, 0, 0, 0.1)'
    #                 }
    #             )
    #         ], className="email-signup-form", style={
    #             'display': 'flex',
    #             'maxWidth': '550px',
    #             'margin': '0 auto',
    #             'animation': 'fadeIn 1s ease-in-out'
    #         }),
            
    #         # Success message (hidden by default)
    #         html.Div([
    #             html.P([
    #                 html.I(className="fas fa-check-circle", style={'marginRight': '10px', 'color': COLORS['accent-light']}),
    #                 "Thank you for subscribing! We'll keep you updated on new features."
    #             ], style={'fontSize': '1.1rem'})
    #         ], id="signup-success", style={'display': 'none', 'marginTop': '15px', 'color': 'white', 'textAlign': 'center'})
            
    #     ], className="mailing-list-content", style={
    #         'maxWidth': '900px',
    #         'margin': '0 auto',
    #         'padding': '20px',
    #         'position': 'relative',
    #         'zIndex': '2'
    #     })
    # ], className="mailing-list-section", style={
    #     'padding': '60px 40px',
    #     'backgroundColor': COLORS['secondary'],
    #     'backgroundImage': f'linear-gradient(135deg, {COLORS["secondary"]} 0%, {COLORS["primary"]} 100%)',
    #     'position': 'relative',
    #     'overflow': 'hidden'
    # }),

    # Add some animated elements in the background for visual interest
    html.Div(className="floating-circle-ml-1", style={
        'position': 'absolute',
        'width': '200px',
        'height': '200px',
        'borderRadius': '50%',
        'backgroundColor': 'rgba(255, 255, 255, 0.03)',
        'top': '20%',
        'right': '10%',
        'animation': 'float 10s ease-in-out infinite',
        'zIndex': '1'
    }),
    html.Div(className="floating-circle-ml-2", style={
        'position': 'absolute',
        'width': '120px',
        'height': '120px',
        'borderRadius': '50%',
        'backgroundColor': 'rgba(144, 205, 244, 0.05)',
        'bottom': '15%',
        'left': '10%',
        'animation': 'float 8s ease-in-out infinite 1s',
        'zIndex': '1'
    }),

    # Statistics Section with Stacked Blue Metric Icons
    html.Div([
        html.H2("BlueCard by the Numbers", className="section-title", style={
            'color': COLORS['primary'],
            'textAlign': 'center',
            'fontSize': '2.5rem',
            'fontWeight': '600',
            'marginBottom': '3rem',
            'position': 'relative',
            'paddingBottom': '15px'
        }),
        
        # Decorative line under the section title
        html.Div(style={
            'position': 'absolute',
            'width': '80px',
            'height': '4px',
            'backgroundColor': COLORS['accent'],
            'left': '50%',
            'transform': 'translateX(-50%)',
            'marginTop': '-2.7rem'
        }),
        
        # Metrics Row with Stacked Icons
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        # Stacked Icons with 3D Effect
                        html.Div([
                            html.Img(src="/assets/users.png", alt="Users Icon", style={
                                'width': '60px',
                                'height': '60px',
                                'position': 'absolute',
                                'top': '0',
                                'left': '0',
                                'zIndex': '3',
                                'filter': 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.2))'
                            }),
                            html.Div(style={
                                'width': '60px',
                                'height': '60px',
                                'backgroundColor': COLORS['accent-light'],
                                'borderRadius': '15px',
                                'position': 'absolute',
                                'top': '5px',
                                'left': '5px',
                                'zIndex': '1',
                                'transform': 'rotate(15deg)'
                            }),
                            html.Div(style={
                                'width': '60px',
                                'height': '60px',
                                'backgroundColor': COLORS['accent'],
                                'borderRadius': '15px',
                                'position': 'absolute',
                                'top': '10px',
                                'left': '10px',
                                'zIndex': '2',
                                'transform': 'rotate(30deg)'
                            })
                        ], style={
                            'position': 'relative',
                            'width': '100px',
                            'height': '100px',
                            'margin': '0 auto 40px auto'
                        })
                    ]),
                    html.H2("100+", style={
                        'color': COLORS['primary'],
                        'fontSize': '2.5rem',
                        'fontWeight': '700',
                        'marginBottom': '10px'
                    }),
                    html.P("Active Users", style={
                        'color': COLORS['grey'],
                        'fontSize': '1.2rem',
                        'fontWeight': '500'
                    })
                ], className="metric-card", style={
                    'textAlign': 'center',
                    'padding': '40px 20px',
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '8px',
                    'boxShadow': '0 10px 25px rgba(0, 0, 0, 0.05)',
                    'height': '100%'
                })
            ], md=3, sm=6, className="mb-4"),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        # Stacked Icons with 3D Effect
                        html.Div([
                            html.Img(src="/assets/savings_vault.png", alt="Savings Icon", style={
                                'width': '60px',
                                'height': '60px',
                                'position': 'absolute',
                                'top': '0',
                                'left': '0',
                                'zIndex': '3',
                                'filter': 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.2))'
                            }),
                            html.Div(style={
                                'width': '60px',
                                'height': '60px',
                                'backgroundColor': COLORS['accent-light'],
                                'borderRadius': '15px',
                                'position': 'absolute',
                                'top': '5px',
                                'left': '5px',
                                'zIndex': '1',
                                'transform': 'rotate(15deg)'
                            }),
                            html.Div(style={
                                'width': '60px',
                                'height': '60px',
                                'backgroundColor': COLORS['accent'],
                                'borderRadius': '15px',
                                'position': 'absolute',
                                'top': '10px',
                                'left': '10px',
                                'zIndex': '2',
                                'transform': 'rotate(30deg)'
                            })
                        ], style={
                            'position': 'relative',
                            'width': '100px',
                            'height': '100px',
                            'margin': '0 auto 40px auto'
                        })
                    ]),
                    html.H2("£10,000+", style={
                        'color': COLORS['primary'],
                        'fontSize': '2.5rem',
                        'fontWeight': '700',
                        'marginBottom': '10px'
                    }),
                    html.P("Savings Tracked", style={
                        'color': COLORS['grey'],
                        'fontSize': '1.2rem',
                        'fontWeight': '500'
                    })
                ], className="metric-card", style={
                    'textAlign': 'center',
                    'padding': '40px 20px',
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '8px',
                    'boxShadow': '0 10px 25px rgba(0, 0, 0, 0.05)',
                    'height': '100%'
                })
            ], md=3, sm=6, className="mb-4"),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        # Stacked Icons with 3D Effect
                        html.Div([
                            html.Img(src="/assets/goal.png", alt="Goals Icon", style={
                                'width': '60px',
                                'height': '60px',
                                'position': 'absolute',
                                'top': '0',
                                'left': '0',
                                'zIndex': '3',
                                'filter': 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.2))'
                            }),
                            html.Div(style={
                                'width': '60px',
                                'height': '60px',
                                'backgroundColor': COLORS['accent-light'],
                                'borderRadius': '15px',
                                'position': 'absolute',
                                'top': '5px',
                                'left': '5px',
                                'zIndex': '1',
                                'transform': 'rotate(15deg)'
                            }),
                            html.Div(style={
                                'width': '60px',
                                'height': '60px',
                                'backgroundColor': COLORS['accent'],
                                'borderRadius': '15px',
                                'position': 'absolute',
                                'top': '10px',
                                'left': '10px',
                                'zIndex': '2',
                                'transform': 'rotate(30deg)'
                            })
                        ], style={
                            'position': 'relative',
                            'width': '100px',
                            'height': '100px',
                            'margin': '0 auto 40px auto'
                        })
                    ]),
                    html.H2("50+", style={
                        'color': COLORS['primary'],
                        'fontSize': '2.5rem',
                        'fontWeight': '700',
                        'marginBottom': '10px'
                    }),
                    html.P("Goals Achieved", style={
                        'color': COLORS['grey'],
                        'fontSize': '1.2rem',
                        'fontWeight': '500'
                    })
                ], className="metric-card", style={
                    'textAlign': 'center',
                    'padding': '40px 20px',
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '8px',
                    'boxShadow': '0 10px 25px rgba(0, 0, 0, 0.05)',
                    'height': '100%'
                })
            ], md=3, sm=6, className="mb-4"),
            
            dbc.Col([
                html.Div([
                    html.Div([
                        # Stacked Icons with 3D Effect
                        html.Div([
                            html.Img(src="/assets/globe.png", alt="Countries Icon", style={
                                'width': '60px',
                                'height': '60px',
                                'position': 'absolute',
                                'top': '0',
                                'left': '0',
                                'zIndex': '3',
                                'filter': 'drop-shadow(0 4px 6px rgba(0, 0, 0, 0.2))'
                            }),
                            html.Div(style={
                                'width': '60px',
                                'height': '60px',
                                'backgroundColor': COLORS['accent-light'],
                                'borderRadius': '15px',
                                'position': 'absolute',
                                'top': '5px',
                                'left': '5px',
                                'zIndex': '1',
                                'transform': 'rotate(15deg)'
                            }),
                            html.Div(style={
                                'width': '60px',
                                'height': '60px',
                                'backgroundColor': COLORS['accent'],
                                'borderRadius': '15px',
                                'position': 'absolute',
                                'top': '10px',
                                'left': '10px',
                                'zIndex': '2',
                                'transform': 'rotate(30deg)'
                            })
                        ], style={
                            'position': 'relative',
                            'width': '100px',
                            'height': '100px',
                            'margin': '0 auto 40px auto'
                        })
                    ]),
                    html.H2("2+", style={
                        'color': COLORS['primary'],
                        'fontSize': '2.5rem',
                        'fontWeight': '700',
                        'marginBottom': '10px'
                    }),
                    html.P("Countries Served", style={
                        'color': COLORS['grey'],
                        'fontSize': '1.2rem',
                        'fontWeight': '500'
                    })
                ], className="metric-card", style={
                    'textAlign': 'center',
                    'padding': '40px 20px',
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '8px',
                    'boxShadow': '0 10px 25px rgba(0, 0, 0, 0.05)',
                    'height': '100%'
                })
            ], md=3, sm=6, className="mb-4")
        ])
    ], className="stats-section", style={
        'padding': '80px 40px',
        'backgroundColor': COLORS['background'],  # Light blue-grey
        'position': 'relative'
    }),

    # ----------------------------------------

    # # Image Collage Section with diagonal blue overlay
    # html.Div([
    #     html.Div([
    #         html.H2("Financial Success Stories", className="section-title", style={
    #             'color': COLORS['white'],
    #             'textAlign': 'center',
    #             'fontSize': '2.5rem',
    #             'fontWeight': '600',
    #             'marginBottom': '3rem',
    #             'position': 'relative',
    #             'paddingBottom': '15px',
    #             'zIndex': '2'
    #         }),
            
    #         # Decorative line under the section title
    #         html.Div(style={
    #             'position': 'absolute',
    #             'width': '80px',
    #             'height': '4px',
    #             'backgroundColor': COLORS['accent-light'],
    #             'left': '50%',
    #             'transform': 'translateX(-50%)',
    #             'marginTop': '-2.7rem',
    #             'zIndex': '2'
    #         }),
            
    #         # Modern Image Collage
    #         html.Div([
    #             dbc.Row([
    #                 # Left Column - Larger Images
    #                 dbc.Col([
    #                     html.Div([
    #                         html.Img(src="/assets/finance-success1.png", alt="Finance Success Story", className="collage-img", style={
    #                             'width': '100%',
    #                             'height': '300px',
    #                             'objectFit': 'cover',
    #                             'borderRadius': '10px',
    #                             'marginBottom': '20px',
    #                             'boxShadow': '0 15px 25px rgba(0, 0, 0, 0.2)',
    #                             'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
    #                         })
    #                     ], className="collage-img-container"),
    #                     html.Div([
    #                         html.Img(src="/assets/finance-success2.png", alt="Finance Success Story", className="collage-img", style={
    #                             'width': '100%',
    #                             'height': '200px',
    #                             'objectFit': 'cover',
    #                             'borderRadius': '10px',
    #                             'boxShadow': '0 15px 25px rgba(0, 0, 0, 0.2)',
    #                             'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
    #                         })
    #                     ], className="collage-img-container"),
    #                 ], md=6, style={'padding': '10px'}),
                    
    #                 # Right Column - Smaller Images
    #                 dbc.Col([
    #                     html.Div([
    #                         html.Img(src="/assets/finance-success3.png", alt="Finance Success Story", className="collage-img", style={
    #                             'width': '100%',
    #                             'height': '200px',
    #                             'objectFit': 'cover',
    #                             'borderRadius': '10px',
    #                             'marginBottom': '20px',
    #                             'boxShadow': '0 15px 25px rgba(0, 0, 0, 0.2)',
    #                             'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
    #                         })
    #                     ], className="collage-img-container"),
    #                     html.Div([
    #                         html.Img(src="/assets/finance-success4.png", alt="Finance Success Story", className="collage-img", style={
    #                             'width': '100%',
    #                             'height': '300px',
    #                             'objectFit': 'cover',
    #                             'borderRadius': '10px',
    #                             'boxShadow': '0 15px 25px rgba(0, 0, 0, 0.2)',
    #                             'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
    #                         })
    #                     ], className="collage-img-container"),
    #                 ], md=6, style={'padding': '10px'})
    #             ]),
                
    #             # Bottom Row with 3 equal images
    #             dbc.Row([
    #                 dbc.Col([
    #                     html.Div([
    #                         html.Img(src="/assets/finance-success5.png", alt="Finance Success Story", className="collage-img", style={
    #                             'width': '100%',
    #                             'height': '180px',
    #                             'objectFit': 'cover',
    #                             'borderRadius': '10px',
    #                             'boxShadow': '0 15px 25px rgba(0, 0, 0, 0.2)',
    #                             'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
    #                         })
    #                     ], className="collage-img-container"),
    #                 ], md=4, style={'padding': '10px'}),
                    
    #                 dbc.Col([
    #                     html.Div([
    #                         html.Img(src="/assets/finance-success6.png", alt="Finance Success Story", className="collage-img", style={
    #                             'width': '100%',
    #                             'height': '180px',
    #                             'objectFit': 'cover',
    #                             'borderRadius': '10px',
    #                             'boxShadow': '0 15px 25px rgba(0, 0, 0, 0.2)',
    #                             'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
    #                         })
    #                     ], className="collage-img-container"),
    #                 ], md=4, style={'padding': '10px'}),
                    
    #                 dbc.Col([
    #                     html.Div([
    #                         html.Img(src="/assets/finance-success7.png", alt="Finance Success Story", className="collage-img", style={
    #                             'width': '100%',
    #                             'height': '180px',
    #                             'objectFit': 'cover',
    #                             'borderRadius': '10px',
    #                             'boxShadow': '0 15px 25px rgba(0, 0, 0, 0.2)',
    #                             'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
    #                         })
    #                     ], className="collage-img-container"),
    #                 ], md=4, style={'padding': '10px'})
    #             ], className="mt-3")
    #         ], className="image-collage", style={'zIndex': '2', 'position': 'relative'})
    #     ], className="collage-section-content", style={
    #         'position': 'relative',
    #         'zIndex': '2'
    #     })
    # ], className="collage-section", style={
    #     'padding': '80px 40px',
    #     'backgroundColor': COLORS['accent'],  # Bright blue
    #     'backgroundImage': f'linear-gradient(135deg, {COLORS["accent"]} 0%, {COLORS["primary"]} 100%)',
    #     'position': 'relative',
    #     'overflow': 'hidden'
    # }),

# Call to Action Section with a different blue shade
html.Div([
    dbc.Row([
        dbc.Col([
            html.H2("Ready to Transform Your Financial Future?", className="cta-title", style={
                'color': COLORS['white'],
                'fontSize': '2.8rem',
                'fontWeight': '700',
                'marginBottom': '1.5rem',
                'lineHeight': '1.2'
            }),
            html.P("Join hundreds of satisfied users who are taking control of their finances with BlueCard Finance.", style={
                'color': COLORS['white'],
                'fontSize': '1.2rem',
                'marginBottom': '2.5rem',
                'opacity': '0.9',
                'maxWidth': '600px'
            }),
            dcc.Link(
                dbc.Button(
                    "Get Started Today",
                    href="/dashboard",
                    className="cta-button",
                    size="lg",
                    style={
                        'backgroundColor': COLORS['white'],
                        'color': COLORS['primary'],
                        'border': 'none',
                        'borderRadius': '8px',
                        'padding': '15px 40px',
                        'fontSize': '1.2rem',
                        'fontWeight': '600',
                        'boxShadow': '0 10px 20px rgba(0, 0, 0, 0.1)',
                        'transition': 'all 0.3s ease'
                    }
                ),
                href='/chat'  # This is the URL the button will link to
            ),
        ], md=7, className="cta-content", style={
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'center'
        }),
        dbc.Col([
        # Stacked Device Mockups
        html.Div([
            html.Img(src="/assets/dashboard_pc.png", alt="Dashboard on Desktop", style={
                'width': '60%',  # Increase size
                'borderRadius': '8px',
                'boxShadow': '0 20px 40px rgba(0, 0, 0, 0.2)',
                'position': 'relative',
                'zIndex': '3',
                'transform': 'translateX(-20px)'  # Offset to the left
            }),
            html.Img(src="/assets/savings_analysis_pc.PNG", style={
                'width': '60%',  # Match size with the first image
                'borderRadius': '8px',
                'boxShadow': '0 15px 30px rgba(0, 0, 0, 0.25)',
                'position': 'absolute',
                'right': '0',
                'bottom': '-30px',  # Adjust overlap
                'zIndex': '2',  # Place behind the first image
                'transform': 'translateX(-10px)'  # Slight offset for alignment
            })
        ], style={
            'position': 'relative',
            'height': '400px',  # Increase height to accommodate larger images
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center'
        })
    ], md=5, className="d-none d-md-block")  # Hide on mobile
    ])
], className="cta-section", style={
    'padding': '80px 40px',
    'backgroundColor': COLORS['secondary'],  # Medium dark blue
    'backgroundImage': 'linear-gradient(135deg, rgba(42, 74, 127, 0.98) 0%, rgba(20, 44, 82, 0.98) 100%)',
    'position': 'relative'
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

], style={"width": "100%", "margin": "0", "padding": "0"})

# Mailing list needs updating
# @callback(
#     [Output("signup-success", "style"),
#      Output("mailing-list-email", "value")],
#     Input("subscribe-button", "n_clicks"),
#     State("mailing-list-email", "value"),
#     prevent_initial_call=True
# )
# def submit_email(n_clicks, email):
#     if n_clicks and email:
#         try:
#             # Validate email format
#             import re
#             email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
#             if not re.match(email_pattern, email):
#                 # Invalid email format - could show error message instead
#                 return {'display': 'none'}, email
            
#             # Option 1: If you're using a database like PostgreSQL (Render supports this)
#             # import psycopg2
#             # DATABASE_URL = os.environ.get('DATABASE_URL')
#             # conn = psycopg2.connect(DATABASE_URL)
#             # cursor = conn.cursor()
#             # cursor.execute("INSERT INTO mailing_list (email, signup_date) VALUES (%s, NOW())", (email,))
#             # conn.commit()
#             # cursor.close()
#             # conn.close()
            
#             # Option 2: Store in a CSV file (for simpler deployments)
#             import os
#             import csv
#             from datetime import datetime
            
#             # Make sure this directory exists and is writable in your Render deployment
#             data_dir = os.path.join(os.getcwd(), 'data')
#             os.makedirs(data_dir, exist_ok=True)
            
#             file_path = os.path.join(data_dir, 'mailing_list.csv')
#             file_exists = os.path.isfile(file_path)
            
#             with open(file_path, mode='a', newline='') as file:
#                 writer = csv.writer(file)
#                 if not file_exists:
#                     writer.writerow(['Email', 'Signup Date'])
#                 writer.writerow([email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            
#             # Option 3: Send to a third-party API like Mailchimp
#             # import requests
#             # api_key = os.environ.get('MAILCHIMP_API_KEY')
#             # list_id = os.environ.get('MAILCHIMP_LIST_ID')
#             # data = {
#             #     "email_address": email,
#             #     "status": "subscribed"
#             # }
#             # url = f"https://<dc>.api.mailchimp.com/3.0/lists/{list_id}/members"
#             # response = requests.post(
#             #     url, 
#             #     auth=("username", api_key),
#             #     json=data
#             # )
            
#             # Show success message and clear the input
#             return {'display': 'block', 'marginTop': '15px', 'color': 'white', 'textAlign': 'center'}, ""
        
#         except Exception as e:
#             print(f"Error saving email: {str(e)}")
#             # For security, don't show the actual error to users
#             # You could log this error or send yourself a notification
#                # Return a neutral message or no message
#             return {'display': 'none'}, email
    
#     return {'display': 'none'}, ""

# Callback to update user email based on user_id
@callback(
    Output("user-email-display", "children", allow_duplicate=True),
    Input("user-id", "data"),
    prevent_initial_call=True
)
def update_user_email(user_data):
    if user_data and 'user_id' in user_data:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM users WHERE user_id = %s', (user_data['user_id'],))
        user = cursor.fetchone()
        conn.close()
        if user:
            return user[0]
    return "Guest"

# Logout logic (client-side)
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            // Remove session data from localStorage
            localStorage.removeItem("session-data-store");
            // Trigger a redirect using Dash's dcc.Location to logout route
            return {pathname: '/'}; // Redirect to the logout route
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output("session-data-store", "data"),
    Input("logout-link", "n_clicks"),
    prevent_initial_call=True
)

# Sync user data for dropdown based on session
@callback(
    Output("user-id", "data"),
    Input("session-data-store", "data")
)
def sync_user_data(session_data):
    if session_data and 'user_id' in session_data:
        return {'user_id': session_data['user_id']}
    return {}

# Toggle overlay based on authentication and page
@callback(
    Output("auth-check", "children"),
    [Input("session-data-store", "data"),
     Input("url", "pathname")]
)
def check_auth_overlay(session_data, pathname):
    # Skip overlay display if on the home page
    if pathname == '/':
        return None
    
    # If not authenticated, show overlay
    if not session_data or 'user_id' not in session_data:
        return html.Div(
            "You must be logged in to access this page.",
            id="auth-overlay",
            className="overlay"  # You can style this with CSS
        )

    # If authenticated, remove the overlay
    return None