import dash
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
from flask import request

# Add these imports if not already present
import re
import json
from dash.exceptions import PreventUpdate
import requests

# Register this file as the about page
dash.register_page(__name__, path="/about", name="About")

# Define a cohesive color palette matching the home and pricing pages
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

# Layout for the About page
layout = html.Div([
    # Session and Routing
    dcc.Store(id='session-data-store', storage_type='local'),
    dcc.Store(id='user-id', storage_type='local'),
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
                html.Li(html.A([html.Span(className="nav-icon"), "About"], href="/about", className="nav-link active"), className="nav-item"),
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

    # Hero Section
    html.Div([
        html.Div([
            html.H1("Our Mission is Your Financial Success", style={
                'color': COLORS['white'],
                'fontWeight': '700',
                'fontSize': '3.5rem',
                'marginBottom': '20px',
                'maxWidth': '800px'
            }),
            html.P("At BlueCard Finance, we're revolutionizing financial management through AI-powered insights and intuitive tools designed for everyone.", style={
                'color': COLORS['white'],
                'fontSize': '1.25rem',
                'marginBottom': '30px',
                'maxWidth': '600px',
                'lineHeight': '1.8'
            }),
            dcc.Link(
                html.Button("Start Your Journey", className="cta-button", style={
                    'backgroundColor': COLORS['white'],
                    'color': COLORS['primary'],
                    'border': 'none',
                    'borderRadius': '5px',
                    'padding': '15px 30px',
                    'fontSize': '1.1rem',
                    'fontWeight': '600',
                    'cursor': 'pointer',
                    'transition': 'all 0.3s ease',
                    'marginRight': '15px'
                }),
                href='/chat'  # This is the URL the button will link to
            ),
            # html.Button("Watch Video", className="secondary-button", style={
            #     'backgroundColor': 'transparent',
            #     'color': COLORS['white'],
            #     'border': f'2px solid {COLORS["white"]}',
            #     'borderRadius': '5px',
            #     'padding': '15px 30px',
            #     'fontSize': '1.1rem',
            #     'fontWeight': '600',
            #     'cursor': 'pointer',
            #     'transition': 'all 0.3s ease',
            #     'display': 'inline-flex',
            #     'alignItems': 'center'
            # }),
        ], className="hero-content", style={
            'maxWidth': '1200px',
            'margin': '0 auto',
            'padding': '0 20px',
            'position': 'relative',
            'zIndex': '2',
            'textAlign': 'left'
        })
    ], className="hero-section", style={
        'background': f'linear-gradient(135deg, {COLORS["primary"]} 0%, {COLORS["secondary"]} 100%)',
        'color': COLORS['white'],
        'padding': '120px 0',
        'position': 'relative',
        'overflow': 'hidden',
        'width': '100%'
    }),
    
    # Our Story Section
    html.Div([
        html.Div([
            # Left column - text content
            html.Div([
                html.H2("Our Story", style={
                    'color': COLORS['dark'],
                    'fontWeight': '700',
                    'fontSize': '2.5rem',
                    'marginBottom': '20px',
                    'position': 'relative',
                    'paddingBottom': '15px',
                }),
                html.Div(style={
                    'width': '80px',
                    'height': '4px',
                    'backgroundColor': COLORS['accent'],
                    'marginBottom': '30px'
                }),
                html.P("BlueCard Finance was born at the beginning of 2025 from a shared frustration with existing personal finance tools that failed to meet our expectations. Too often, these tools felt to miss what mattered the most. Most critically, they lacked the engagement to hold our interest and the empathy to understand the real emotional landscape of managing finances.", style={
                    'fontSize': '1.1rem',
                    'lineHeight': '1.8',
                    'marginBottom': '20px',
                    'color': COLORS['grey']
                }),
                html.P("We set out to create something truly different, something that feels more human. BlueCard is built on the belief that your financial tool should act as a personal finance buddy, someone you can confide in, address concerns with and rely on during tricky financial times. Because money isn’t just numbers, it’s personal, and your tools should resonate with that reality.", style={
                    'fontSize': '1.1rem',
                    'lineHeight': '1.8',
                    'marginBottom': '20px',
                    'color': COLORS['grey']
                }),
                html.P("At the core of BlueCard is an engaging conversation, an AI-driven experience designed to be intuitive, responsive, and genuinely supportive. We understand that each person’s financial journey is unique, which is why we've made our platform fully customizable. With a personalized dashboard, users can shape their experience around what matters most to them.", style={
                    'fontSize': '1.1rem',
                    'lineHeight': '1.8',
                    'marginBottom': '20px',
                    'color': COLORS['grey']
                }),
                html.P("This is just the beginning of our mission. We're committed to creating a future where managing your finances becomes a seamless conversation, a true partnership, and a dynamic tool that evolves alongside your life. Join us on this transformative journey!", style={
                    'fontSize': '1.1rem',
                    'lineHeight': '1.8',
                    'color': COLORS['grey']
                }),
            ], className="story-text", style={
                'flex': '1',
                'padding': '20px'
            }),

            # Right column - image
            html.Div([
                html.Img(src="/assets/modern_city2.png", alt="Our Story", style={
                    'width': '800px',
                    'borderRadius': '10px',
                    'boxShadow': '0 10px 30px rgba(0,0,0,0.1)'
                })
            ], className="story-image", style={
                'flex': '1',
                'padding': '0 10px 0 0',
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'flex-end'
            })
        ], style={
            'display': 'flex',
            'flexWrap': 'wrap',
            'alignItems': 'center',
            'maxWidth': '1800px',
            'margin': '0 auto'
        })
    ], className="story-section", style={
        'padding': '100px 20px',
        'backgroundColor': COLORS['white']
    }),
    
    # Our Values Section
    html.Div([
        html.Div([
            html.H2("Our Core Values", style={
                'color': COLORS['dark'],
                'fontWeight': '700',
                'fontSize': '2.5rem',
                'marginBottom': '20px',
                'textAlign': 'center'
            }),
            html.Div(style={
                'width': '80px',
                'height': '4px',
                'backgroundColor': COLORS['accent'],
                'margin': '0 auto 60px auto'
            }),
            
            # Values cards container
            html.Div([
                # Value 1
                html.Div([
                    html.Div([
                        html.I(className="fas fa-lightbulb", style={
                            'fontSize': '40px',
                            'color': COLORS['accent'],
                            'marginBottom': '20px'
                        }),
                        html.H3("Innovation", style={
                            'fontSize': '1.5rem',
                            'fontWeight': '600',
                            'marginBottom': '15px',
                            'color': COLORS['dark']
                        }),
                        html.P("We're constantly pushing the boundaries of what's possible in financial technology, developing new ways to make your financial life easier and more successful.", style={
                            'fontSize': '1rem',
                            'lineHeight': '1.7',
                            'color': COLORS['grey']
                        })
                    ], style={
                        'padding': '30px',
                        'height': '100%'
                    })
                ], className="value-card", style={
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '10px',
                    'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
                    'width': 'calc(33.333% - 30px)',
                    'minWidth': '300px',
                    'margin': '15px',
                    'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
                }),
                
                # Value 2
                html.Div([
                    html.Div([
                        html.I(className="fas fa-lock", style={
                            'fontSize': '40px',
                            'color': COLORS['accent'],
                            'marginBottom': '20px'
                        }),
                        html.H3("Security & Trust", style={
                            'fontSize': '1.5rem',
                            'fontWeight': '600',
                            'marginBottom': '15px',
                            'color': COLORS['dark']
                        }),
                        html.P("Your financial data is sacred. We employ the highest standards of security and privacy protection, ensuring your information is always safe and used only to benefit you.", style={
                            'fontSize': '1rem',
                            'lineHeight': '1.7',
                            'color': COLORS['grey']
                        })
                    ], style={
                        'padding': '30px',
                        'height': '100%'
                    })
                ], className="value-card", style={
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '10px',
                    'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
                    'width': 'calc(33.333% - 30px)',
                    'minWidth': '300px',
                    'margin': '15px',
                    'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
                }),
                
                # Value 3
                html.Div([
                    html.Div([
                        html.I(className="fas fa-users", style={
                            'fontSize': '40px',
                            'color': COLORS['accent'],
                            'marginBottom': '20px'
                        }),
                        html.H3("Inclusivity", style={
                            'fontSize': '1.5rem',
                            'fontWeight': '600',
                            'marginBottom': '15px',
                            'color': COLORS['dark']
                        }),
                        html.P("Financial intelligence shouldn't be a privilege. We design our platform to be accessible and useful for everyone, from financial novices to seasoned investors.", style={
                            'fontSize': '1rem',
                            'lineHeight': '1.7',
                            'color': COLORS['grey']
                        })
                    ], style={
                        'padding': '30px',
                        'height': '100%'
                    })
                ], className="value-card", style={
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '10px',
                    'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
                    'width': 'calc(33.333% - 30px)',
                    'minWidth': '300px',
                    'margin': '15px',
                    'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
                }),
                
                # Value 4
                html.Div([
                    html.Div([
                        html.I(className="fas fa-chart-line", style={
                            'fontSize': '40px',
                            'color': COLORS['accent'],
                            'marginBottom': '20px'
                        }),
                        html.H3("Empowerment", style={
                            'fontSize': '1.5rem',
                            'fontWeight': '600',
                            'marginBottom': '15px',
                            'color': COLORS['dark']
                        }),
                        html.P("Our goal is to give you the tools, knowledge, and confidence to take control of your financial future and make decisions that align with your unique goals and values.", style={
                            'fontSize': '1rem',
                            'lineHeight': '1.7',
                            'color': COLORS['grey']
                        })
                    ], style={
                        'padding': '30px',
                        'height': '100%'
                    })
                ], className="value-card", style={
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '10px',
                    'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
                    'width': 'calc(33.333% - 30px)',
                    'minWidth': '300px',
                    'margin': '15px',
                    'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
                }),
                
                # Value 5
                html.Div([
                    html.Div([
                        html.I(className="fas fa-handshake", style={
                            'fontSize': '40px',
                            'color': COLORS['accent'],
                            'marginBottom': '20px'
                        }),
                        html.H3("Transparency", style={
                            'fontSize': '1.5rem',
                            'fontWeight': '600',
                            'marginBottom': '15px',
                            'color': COLORS['dark']
                        }),
                        html.P("We believe in being clear, honest, and straightforward in everything we do—from our pricing structure to how we use your data to generate insights.", style={
                            'fontSize': '1rem',
                            'lineHeight': '1.7',
                            'color': COLORS['grey']
                        })
                    ], style={
                        'padding': '30px',
                        'height': '100%'
                    })
                ], className="value-card", style={
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '10px',
                    'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
                    'width': 'calc(33.333% - 30px)',
                    'minWidth': '300px',
                    'margin': '15px',
                    'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
                }),
                
                # Value 6
                html.Div([
                    html.Div([
                        html.I(className="fas fa-brain", style={
                            'fontSize': '40px',
                            'color': COLORS['accent'],
                            'marginBottom': '20px'
                        }),
                        html.H3("Intelligence", style={
                            'fontSize': '1.5rem',
                            'fontWeight': '600',
                            'marginBottom': '15px',
                            'color': COLORS['dark']
                        }),
                        html.P("Our sophisticated AI algorithms learn from your financial patterns to deliver increasingly personalized insights that help you make smarter decisions over time.", style={
                            'fontSize': '1rem',
                            'lineHeight': '1.7',
                            'color': COLORS['grey']
                        })
                    ], style={
                        'padding': '30px',
                        'height': '100%'
                    })
                ], className="value-card", style={
                    'backgroundColor': COLORS['white'],
                    'borderRadius': '10px',
                    'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
                    'width': 'calc(33.333% - 30px)',
                    'minWidth': '300px',
                    'margin': '15px',
                    'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
                }),
                
            ], style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'justifyContent': 'center',
                'maxWidth': '1600px',
                'margin': '0 auto'
            })
        ])
    ], className="values-section", style={
        'padding': '100px 20px',
        'backgroundColor': COLORS['background'],
    }),
    
    # # Meet Our Team Section
    # html.Div([
    #     html.Div([
    #         html.H2("Meet Our Leadership Team", style={
    #             'color': COLORS['dark'],
    #             'fontWeight': '700',
    #             'fontSize': '2.5rem',
    #             'marginBottom': '20px',
    #             'textAlign': 'center'
    #         }),
    #         html.Div(style={
    #             'width': '80px',
    #             'height': '4px',
    #             'backgroundColor': COLORS['accent'],
    #             'margin': '0 auto 60px auto'
    #         }),
            
    #         # Team members container
    #         html.Div([
    #             # Team Member 1
    #             html.Div([
    #                 html.Div([
    #                     html.Div([
    #                         html.Img(src="/api/placeholder/300/300", alt="Emma Watson", style={
    #                             'width': '100%',
    #                             'height': '100%',
    #                             'objectFit': 'cover',
    #                             'borderRadius': '10px 10px 0 0'
    #                         })
    #                     ], style={
    #                         'height': '300px',
    #                         'overflow': 'hidden'
    #                     }),
    #                     html.Div([
    #                         html.H3("Emma Watson", style={
    #                             'fontSize': '1.5rem',
    #                             'fontWeight': '600',
    #                             'marginBottom': '5px',
    #                             'color': COLORS['dark']
    #                         }),
    #                         html.P("Founder & CEO", style={
    #                             'fontSize': '1rem',
    #                             'color': COLORS['accent'],
    #                             'marginBottom': '15px'
    #                         }),
    #                         html.P("Former investment manager with a passion for making financial intelligence accessible to everyone.", style={
    #                             'fontSize': '0.95rem',
    #                             'lineHeight': '1.6',
    #                             'color': COLORS['grey']
    #                         }),
    #                         html.Div([
    #                             html.A(html.I(className="fab fa-linkedin"), href="#", style={
    #                                 'color': COLORS['primary'],
    #                                 'fontSize': '18px',
    #                                 'marginRight': '15px'
    #                             }),
    #                             html.A(html.I(className="fab fa-twitter"), href="#", style={
    #                                 'color': COLORS['primary'],
    #                                 'fontSize': '18px',
    #                             })
    #                         ], style={
    #                             'marginTop': '15px'
    #                         })
    #                     ], style={
    #                         'padding': '20px'
    #                     })
    #                 ])
    #             ], className="team-card", style={
    #                 'backgroundColor': COLORS['white'],
    #                 'borderRadius': '10px',
    #                 'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
    #                 'width': 'calc(33.333% - 30px)',
    #                 'minWidth': '300px',
    #                 'margin': '15px',
    #                 'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
    #                 'overflow': 'hidden'
    #             }),
                
    #             # Team Member 2
    #             html.Div([
    #                 html.Div([
    #                     html.Div([
    #                         html.Img(src="/api/placeholder/300/300", alt="David Chen", style={
    #                             'width': '100%',
    #                             'height': '100%',
    #                             'objectFit': 'cover',
    #                             'borderRadius': '10px 10px 0 0'
    #                         })
    #                     ], style={
    #                         'height': '300px',
    #                         'overflow': 'hidden'
    #                     }),
    #                     html.Div([
    #                         html.H3("David Chen", style={
    #                             'fontSize': '1.5rem',
    #                             'fontWeight': '600',
    #                             'marginBottom': '5px',
    #                             'color': COLORS['dark']
    #                         }),
    #                         html.P("CTO & AI Lead", style={
    #                             'fontSize': '1rem',
    #                             'color': COLORS['accent'],
    #                             'marginBottom': '15px'
    #                         }),
    #                         html.P("AI expert with 15+ years of experience developing intelligent financial systems and predictive algorithms.", style={
    #                             'fontSize': '0.95rem',
    #                             'lineHeight': '1.6',
    #                             'color': COLORS['grey']
    #                         }),
    #                         html.Div([
    #                             html.A(html.I(className="fab fa-linkedin"), href="#", style={
    #                                 'color': COLORS['primary'],
    #                                 'fontSize': '18px',
    #                                 'marginRight': '15px'
    #                             }),
    #                             html.A(html.I(className="fab fa-github"), href="#", style={
    #                                 'color': COLORS['primary'],
    #                                 'fontSize': '18px',
    #                             })
    #                         ], style={
    #                             'marginTop': '15px'
    #                         })
    #                     ], style={
    #                         'padding': '20px'
    #                     })
    #                 ])
    #             ], className="team-card", style={
    #                 'backgroundColor': COLORS['white'],
    #                 'borderRadius': '10px',
    #                 'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
    #                 'width': 'calc(33.333% - 30px)',
    #                 'minWidth': '300px',
    #                 'margin': '15px',
    #                 'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
    #                 'overflow': 'hidden'
    #             }),
                
    #             # Team Member 3
    #             html.Div([
    #                 html.Div([
    #                     html.Div([
    #                         html.Img(src="/api/placeholder/300/300", alt="Sarah Johnson", style={
    #                             'width': '100%',
    #                             'height': '100%',
    #                             'objectFit': 'cover',
    #                             'borderRadius': '10px 10px 0 0'
    #                         })
    #                     ], style={
    #                         'height': '300px',
    #                         'overflow': 'hidden'
    #                     }),
    #                     html.Div([
    #                         html.H3("Sarah Johnson", style={
    #                             'fontSize': '1.5rem',
    #                             'fontWeight': '600',
    #                             'marginBottom': '5px',
    #                             'color': COLORS['dark']
    #                         }),
    #                         html.P("Chief Financial Officer", style={
    #                             'fontSize': '1rem',
    #                             'color': COLORS['accent'],
    #                             'marginBottom': '15px'
    #                         }),
    #                         html.P("Financial strategist who previously led financial planning at major banking institutions.", style={
    #                             'fontSize': '0.95rem',
    #                             'lineHeight': '1.6',
    #                             'color': COLORS['grey']
    #                         }),
    #                         html.Div([
    #                             html.A(html.I(className="fab fa-linkedin"), href="#", style={
    #                                 'color': COLORS['primary'],
    #                                 'fontSize': '18px',
    #                                 'marginRight': '15px'
    #                             }),
    #                             html.A(html.I(className="fab fa-twitter"), href="#", style={
    #                                 'color': COLORS['primary'],
    #                                 'fontSize': '18px',
    #                             })
    #                         ], style={
    #                             'marginTop': '15px'
    #                         })
    #                     ], style={
    #                         'padding': '20px'
    #                     })
    #                 ])
    #             ], className="team-card", style={
    #                 'backgroundColor': COLORS['white'],
    #                 'borderRadius': '10px',
    #                 'boxShadow': '0 5px 15px rgba(0,0,0,0.05)',
    #                 'width': 'calc(33.333% - 30px)',
    #                 'minWidth': '300px',
    #                 'margin': '15px',
    #                 'transition': 'transform 0.3s ease, box-shadow 0.3s ease',
    #                 'overflow': 'hidden'
    #             }),
    #         ], style={
    #             'display': 'flex',
    #             'flexWrap': 'wrap',
    #             'justifyContent': 'center',
    #             'maxWidth': '1200px',
    #             'margin': '0 auto'
    #         })
    #     ])
    # ], className="team-section", style={
    #     'padding': '100px 20px',
    #     'backgroundColor': COLORS['white']
    # }),
    
    # # Stats & Achievements Section
    # html.Div([
    #     html.Div([
    #         html.H2("Our Impact", style={
    #             'color': COLORS['white'],
    #             'fontWeight': '700',
    #             'fontSize': '2.5rem',
    #             'marginBottom': '60px',
    #             'textAlign': 'center'
    #         }),
            
    #         # Stats counters
    #         html.Div([
    #             # Stat 1
    #             html.Div([
    #                 html.Div([
    #                     html.H3("25,000+", style={
    #                         'fontSize': '3rem',
    #                         'fontWeight': '700',
    #                         'marginBottom': '15px',
    #                         'color': COLORS['white']
    #                     }),
    #                     html.P("Active Users", style={
    #                         'fontSize': '1.25rem',
    #                         'color': COLORS['accent-light']
    #                     })
    #                 ], style={
    #                     'textAlign': 'center'
    #                 })
    #             ], className="stat-box", style={
    #                 'flex': '1',
    #                 'minWidth': '200px',
    #                 'margin': '15px',
    #                 'padding': '30px'
    #             }),
                
    #             # Stat 2
    #             html.Div([
    #                 html.Div([
    #                     html.H3("£1.3M", style={
    #                         'fontSize': '3rem',
    #                         'fontWeight': '700',
    #                         'marginBottom': '15px',
    #                         'color': COLORS['white']
    #                     }),
    #                     html.P("Saved by Users Monthly", style={
    #                         'fontSize': '1.25rem',
    #                         'color': COLORS['accent-light']
    #                     })
    #                 ], style={
    #                     'textAlign': 'center'
    #                 })
    #             ], className="stat-box", style={
    #                 'flex': '1',
    #                 'minWidth': '200px',
    #                 'margin': '15px',
    #                 'padding': '30px'
    #             }),
                
    #             # Stat 3
    #             html.Div([
    #                 html.Div([
    #                     html.H3("94%", style={
    #                         'fontSize': '3rem',
    #                         'fontWeight': '700',
    #                         'marginBottom': '15px',
    #                         'color': COLORS['white']
    #                     }),
    #                     html.P("User Satisfaction", style={
    #                         'fontSize': '1.25rem',
    #                         'color': COLORS['accent-light']
    #                     })
    #                 ], style={
    #                     'textAlign': 'center'
    #                 })
    #             ], className="stat-box", style={
    #                 'flex': '1',
    #                 'minWidth': '200px',
    #                 'margin': '15px',
    #                 'padding': '30px'
    #             }),
    #         ], style={
    #             'display': 'flex',
    #             'flexWrap': 'wrap',
    #             'justifyContent': 'space-around'
    #         })

    #     ], style={
    #         'maxWidth': '1000px',
    #         'margin': '0 auto',
    #         'padding': '50px 20px'
    #     })
    # ], style={
    #     'backgroundColor': COLORS['primary'],
    #     'padding': '100px 0'
    # }),

    # Vision & Mission Section
    html.Div([
        html.Div([
            html.H2("Built for the Future of Finance", style={
                'color': COLORS['white'],
                'fontWeight': '700',
                'fontSize': '2.5rem',
                'marginBottom': '60px',
                'textAlign': 'center'
            }),
            
            html.Div([
                # Vision 1 – Customisation
                html.Div([
                    html.Div([
                        html.H3("Fully Customisable", style={
                            'fontSize': '2rem',
                            'fontWeight': '700',
                            'marginBottom': '15px',
                            'color': COLORS['white']
                        }),
                        html.P("Finance that fits *you*, not the other way around.", style={
                            'fontSize': '1.25rem',
                            'color': COLORS['accent-light']
                        })
                    ], style={'textAlign': 'center'})
                ], className="stat-box", style={
                    'flex': '1',
                    'minWidth': '250px',
                    'margin': '15px',
                    'padding': '30px'
                }),

                # Vision 2 – AI-first, Human-Centered
                html.Div([
                    html.Div([
                        html.H3("AI with Empathy", style={
                            'fontSize': '2rem',
                            'fontWeight': '700',
                            'marginBottom': '15px',
                            'color': COLORS['white']
                        }),
                        html.P("A personal finance buddy you can talk to, not just track with.", style={
                            'fontSize': '1.25rem',
                            'color': COLORS['accent-light']
                        })
                    ], style={'textAlign': 'center'})
                ], className="stat-box", style={
                    'flex': '1',
                    'minWidth': '250px',
                    'margin': '15px',
                    'padding': '30px'
                }),

                # Vision 3 – Early-Stage but Bold
                html.Div([
                    html.Div([
                        html.H3("Just Getting Started", style={
                            'fontSize': '2rem',
                            'fontWeight': '700',
                            'marginBottom': '15px',
                            'color': COLORS['white']
                        }),
                        html.P("We're a small team with a big mission: to make personal finance feel personal again.", style={
                            'fontSize': '1.25rem',
                            'color': COLORS['accent-light']
                        })
                    ], style={'textAlign': 'center'})
                ], className="stat-box", style={
                    'flex': '1',
                    'minWidth': '250px',
                    'margin': '15px',
                    'padding': '30px'
                }),
            ], style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'justifyContent': 'space-around'
            })

        ], style={
            'maxWidth': '1000px',
            'margin': '0 auto',
            'padding': '50px 20px'
        })
    ], style={
        'backgroundColor': COLORS['primary'],
        'padding': '100px 0'
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
                        "support@bluecardfinance.com"
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
    })
])

