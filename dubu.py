# import dash
# from dash import html, dcc, callback, Input, Output, State, register_page, ALL, MATCH, clientside_callback, callback_context
# import dash_bootstrap_components as dbc
# from dash.exceptions import PreventUpdate
# import pandas as pd
# import plotly.graph_objects as go
# import plotly.express as px
# import json
# import uuid
# from datetime import datetime, timedelta
# import psycopg2
# from psycopg2.extras import RealDictCursor
# from utils.db import connect_db
# import random
# import dash_draggable
# import copy

# # Register this file as the chat page
# register_page(__name__, path='/chat', name='Chat')

# # COLORS dictionary for consistent styling
# COLORS = {
#     'primary': '#2C3E50',
#     'accent': '#3498DB', 
#     'success': '#2ECC71',
#     'white': '#FFFFFF',
#     'light': '#F8F9FA',
#     'warning': '#F39C12',
#     'danger-light': '#e0796e',
#     'danger': '#E74C3C',
#     'gray': '#95A5A6',
#     'dark': '#212529'
# }

# # Chart COLORS_CHART and styling constants
# COLORS_CHART = {
#     'primary': '#1E40AF',      # Deep blue
#     'secondary': '#3B82F6',    # Mid blue
#     'accent': '#60A5FA',       # Bright blue
#     'highlight': '#93C5FD',    # Light blue
#     'background': '#F0F7FF',   # Very light blue
#     'text': '#1E293B',         # Slate for text
#     'chart_palette': ['#1E40AF', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#2563EB', '#1D4ED8', '#DBEAFE']
# }

# # Database connection function
# def get_db_connection():
#     """Connect to the PostgreSQL database"""
#     try:
#         conn = connect_db()
#         return conn
#     except Exception as e:
#         # # print(f"Error connecting to database: {e}")
#         return None

# def get_user_data(user_id):
#     """Get user data from database or return default for guest users"""
#     # Handle guest or invalid user IDs gracefully
#     if not user_id or user_id == 'Guest':
#         return {
#             'user_info': {'id': 'Guest', 'name': 'Guest User'},
#             'income': generate_demo_income_data(),
#             'expenses': generate_demo_expense_data(),
#             'savings_goals': [],
#             'transactions': [],
#             'dashboard_settings': {  # Return as object, not JSON string
#                 'components': [
#                     {
#                         'id': str(uuid.uuid4()),
#                         'type': 'income_chart',
#                         'title': 'Monthly Income',
#                         'position': {'x': 0, 'y': 0, 'w': 8, 'h': 6},
#                         'settings': {'chart_type': 'bar', 'color': COLORS['accent']}
#                     },
#                     {
#                         'id': str(uuid.uuid4()),
#                         'type': 'expense_breakdown',
#                         'title': 'Expense Breakdown',
#                         'position': {'x': 6, 'y': 0, 'w': 8, 'h': 6},
#                         'settings': {'chart_type': 'pie', 'color': COLORS['primary']}
#                     }
#                 ]
#             }
#         }

#     conn = get_db_connection()
#     if not conn:
#         return {}

#     user_data = {}
#     try:
#         with conn.cursor(cursor_factory=RealDictCursor) as cur:
#             # Get user info
#             cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
#             user = cur.fetchone()
#             if not user:
#                 # print(f"User {user_id} not found in database")
#                 return {}

#             user_data['user_info'] = dict(user)

#             # Get income data
#             cur.execute("SELECT * FROM income WHERE user_id = %s", (user_id,))
#             user_data['income'] = [dict(row) for row in cur.fetchall()]

#             # Get expense data
#             cur.execute("SELECT * FROM expense WHERE user_id = %s", (user_id,))
#             user_data['expenses'] = [dict(row) for row in cur.fetchall()]

#             # Get savings goals
#             cur.execute("SELECT * FROM saving_goals WHERE user_id = %s", (user_id,))
#             user_data['savings_goals'] = [dict(row) for row in cur.fetchall()]

#             # Get transactions
#             cur.execute(
#                 "SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC LIMIT 50",
#                 (user_id,)
#             )
#             user_data['transactions'] = [dict(row) for row in cur.fetchall()]

#             # Get dashboard settings
#             cur.execute("SELECT dashboard_settings FROM users WHERE user_id = %s", (user_id,))
#             dashboard_settings = cur.fetchone()

#     except Exception as e:
#          print(f"Error fetching user data: {e}")
#     finally:
#         conn.close()

#     return user_data

# # Generate demo data for development and guest users
# def generate_demo_income_data():
#     """Generate demo income data for testing"""
#     today = datetime.now()
#     data = []
    
#     for i in range(12):
#         month_date = today - timedelta(days=30 * i)
#         # Base amount with some randomness
#         base = 3500
#         variation = base * 0.1  # 10% variation
        
#         data.append({
#             'id': i,
#             'user_id': 'Guest',
#             'source': 'Primary Income',
#             'amount': base + ((variation * 2) * (0.5 - random.random())),
#             'date': month_date,
#             'monthly_amount': base + ((variation * 2) * (0.5 - random.random())),
#             'recurring': True
#         })
    
#     return data

# def generate_demo_expense_data():
#     """Generate demo expense data for testing"""
#     categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 'Utilities']
#     amounts = [1200, 500, 300, 200, 250]
    
#     data = []
#     for i, (category, amount) in enumerate(zip(categories, amounts)):
#         data.append({
#             'id': i,
#             'user_id': 'Guest',
#             'category': category,
#             'description': f'{category} expenses',
#             'amount': amount,
#             'date': datetime.now() - timedelta(days=i * 2)
#         })
    
#     return data

# # Add these new functions for multiple income charts

# def generate_income_breakdown_pie(income_data, settings=None):
#     """Generate income breakdown pie chart"""
#     import plotly.graph_objects as go
#     import pandas as pd
    
#     if not income_data:
#         # Return placeholder
#         fig = go.Figure()
#         fig.add_annotation(text="No income data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
#         return fig
    
#     # Group by source if available, otherwise use a simple breakdown
#     df = pd.DataFrame(income_data)
    
#     if 'source' in df.columns:
#         source_data = df.groupby('source')['amount'].sum().reset_index()
#         fig = go.Figure(go.Pie(
#             labels=source_data['source'],
#             values=source_data['amount'],
#             hole=0.4,
#             textinfo='label+percent',
#             marker=dict(
#                 colors=['#0082c8', '#38b0de', '#0069aa', '#4ca3dd', '#003c7f', '#76b7e5'],
#                 line=dict(color='#ffffff', width=2)
#             )
#         ))
#     else:
#         # Fallback to a simple representation
#         fig = go.Figure(go.Pie(
#             labels=['Primary Income', 'Secondary Income', 'Investments'],
#             values=[75, 15, 10],
#             hole=0.4,
#             textinfo='label+percent',
#             marker=dict(
#                 colors=['#0082c8', '#38b0de', '#0069aa'],
#                 line=dict(color='#ffffff', width=2)
#             )
#         ))
    
#     fig.update_layout(
#         title={
#             'text': 'Income Sources Breakdown',
#             'y':0.95,
#             'x':0.5,
#             'xanchor': 'center',
#             'yanchor': 'top',
#             'font': dict(family="Inter, Arial, sans-serif", size=20, color=COLORS_CHART['text'])
#         },
#         showlegend=True,
#         legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
#         margin=dict(l=20, r=20, t=80, b=20),
#         height=400,
#         paper_bgcolor='rgba(0,0,0,0)',
#         plot_bgcolor='rgba(0,0,0,0)'
#     )
    
#     return fig

# def generate_monte_carlo_simulation(income_data, settings=None, simulations=100):
#     """Generate Monte Carlo simulation for income projections"""
#     import plotly.graph_objects as go
#     import pandas as pd
#     import numpy as np
#     from datetime import datetime, timedelta
    
#     # Either use data or create sample data
#     if income_data and len(income_data) > 2:
#         df = pd.DataFrame(income_data)
#         df['date'] = pd.to_datetime(df['date'])
#         df = df.sort_values('date')
        
#         if 'monthly_amount' in df.columns:
#             df['value'] = df['monthly_amount']
#         else:
#             df['value'] = df['amount']
            
#         # Calculate statistics
#         avg_growth = df['value'].pct_change().mean()
#         std_dev = df['value'].pct_change().std()
#         last_value = df['value'].iloc[-1]
#     else:
#         # Sample data
#         avg_growth = 0.01  # 1% average monthly growth
#         std_dev = 0.03     # 3% standard deviation
#         last_value = 5000  # Starting income
    
#     # Project forward 24 months
#     months = 24
#     simulations = min(simulations, 200)  # Cap at 200 simulations for performance
    
#     # Create dates for projection
#     last_date = datetime.now()
#     dates = [last_date + timedelta(days=30*i) for i in range(months)]
    
#     # Run Monte Carlo simulations
#     all_simulations = []
#     for sim in range(simulations):
#         values = [last_value]
#         for i in range(1, months):
#             # Random growth with normal distribution
#             growth = np.random.normal(avg_growth, std_dev)
#             next_value = values[-1] * (1 + growth)
#             values.append(next_value)
#         all_simulations.append(values)
    
#     # Calculate median values
#     median_values = np.median(all_simulations, axis=0)
    
#     # Create the figure
#     fig = go.Figure()
    
#     # Add individual simulations
#     for i, sim_values in enumerate(all_simulations):
#         if i == 0:
#             fig.add_trace(go.Scatter(
#                 x=dates, 
#                 y=sim_values,
#                 line=dict(color='rgba(0, 130, 200, 0.1)', width=1),
#                 name='Simulation',
#                 hoverinfo='none',
#                 showlegend=False
#             ))
#         else:
#             fig.add_trace(go.Scatter(
#                 x=dates, 
#                 y=sim_values,
#                 line=dict(color='rgba(0, 130, 200, 0.1)', width=1),
#                 name='Simulation',
#                 hoverinfo='none',
#                 showlegend=False
#             ))
    
#     # Add median line
#     fig.add_trace(go.Scatter(
#         x=dates,
#         y=median_values,
#         line=dict(color='#0082c8', width=3),
#         name='Median Forecast',
#         hovertemplate='<b>%{x|%b %Y}</b><br>$%{y:,.2f}<extra></extra>'
#     ))
    
#     # Style the chart
#     fig.update_layout(
#         title={
#             'text': 'Income Monte Carlo Simulation (24 Months)',
#             'y':0.95,
#             'x':0.5,
#             'xanchor': 'center',
#             'yanchor': 'top',
#             'font': dict(family="Inter, Arial, sans-serif", size=18, color=COLORS_CHART['text'])
#         },
#         xaxis=dict(
#             title="Date",
#             tickformat='%b %Y'
#         ),
#         yaxis=dict(
#             title="Monthly Income ($)",
#             tickprefix='$',
#             tickformat=',.0f'
#         ),
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         ),
#         margin=dict(l=40, r=40, t=80, b=40),
#         height=450,
#         paper_bgcolor='rgba(0,0,0,0)',
#         plot_bgcolor='rgba(255,255,255,0)'
#     )
    
#     fig.update_xaxes(
#         showgrid=True,
#         gridwidth=1,
#         gridcolor='rgba(226, 232, 240, 0.8)'
#     )
    
#     fig.update_yaxes(
#         showgrid=True,
#         gridwidth=1,
#         gridcolor='rgba(226, 232, 240, 0.8)'
#     )
    
#     return fig

# def generate_income_heatmap(income_data, settings=None):
#     """Generate a heatmap showing income patterns by month and year"""
#     import plotly.graph_objects as go
#     import pandas as pd
#     import numpy as np
#     from datetime import datetime, timedelta
    
#     # Create sample data if no data available
#     if not income_data or len(income_data) < 12:
#         # Generate 24 months of sample data
#         today = datetime.now()
#         dates = []
#         values = []
        
#         for i in range(-12, 12):
#             month_date = today + timedelta(days=30*i)
#             dates.append(month_date)
            
#             # Random variations with seasonal pattern
#             month_num = month_date.month
#             seasonal_factor = 1.0 + 0.2 * np.sin((month_num - 1) * np.pi / 6)  # Peak in July
#             base_value = 5000
#             variation = np.random.normal(0, 500)
#             values.append(base_value * seasonal_factor + variation)
            
#         df = pd.DataFrame({
#             'date': dates,
#             'value': values
#         })
#     else:
#         df = pd.DataFrame(income_data)
#         df['date'] = pd.to_datetime(df['date'])
        
#         if 'monthly_amount' in df.columns:
#             df['value'] = df['monthly_amount']
#         else:
#             df['value'] = df['amount']
    
#     # Extract year and month
#     df['year'] = df['date'].dt.year
#     df['month'] = df['date'].dt.month
#     df['month_name'] = df['date'].dt.strftime('%b')
    
#     # Pivot data for heatmap
#     pivot_df = df.pivot_table(index='month', columns='year', values='value', aggfunc='mean')
    
#     # Get month names in correct order
#     month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
#     # Create heatmap
#     fig = go.Figure(data=go.Heatmap(
#         z=pivot_df.values,
#         x=pivot_df.columns,
#         y=month_names,
#         colorscale='Blues',
#         colorbar=dict(
#             title='Income ($)',
#             tickprefix='$',
#             tickformat=',.0f'
#         ),
#         hovertemplate='<b>%{y} %{x}</b><br>$%{z:,.2f}<extra></extra>'
#     ))
    
#     fig.update_layout(
#         title={
#             'text': 'Monthly Income Patterns by Year',
#             'y':0.95,
#             'x':0.5,
#             'xanchor': 'center',
#             'yanchor': 'top', 
#             'font': dict(family="Inter, Arial, sans-serif", size=18, color=COLORS_CHART['text'])
#         },
#         xaxis=dict(title='Year', type='category'),
#         yaxis=dict(title='Month', categoryorder='array', categoryarray=month_names),
#         margin=dict(l=40, r=40, t=80, b=40),
#         height=400,
#         paper_bgcolor='rgba(0,0,0,0)'
#     )
    
#     return fig

# def generate_income_seasonality(income_data, settings=None):
#     """Generate chart showing income seasonality by month"""
#     import plotly.graph_objects as go
#     import pandas as pd
#     from datetime import datetime
    
#     # Create sample data if no data available
#     if not income_data or len(income_data) < 6:
#         # Sample data with seasonal pattern
#         months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#         values = [4800, 4600, 4700, 5100, 5400, 5800, 6200, 6000, 5600, 5200, 5000, 5300]
        
#         df = pd.DataFrame({
#             'month': months,
#             'value': values,
#             'month_num': range(1, 13)
#         })
#     else:
#         df = pd.DataFrame(income_data)
#         df['date'] = pd.to_datetime(df['date'])
        
#         if 'monthly_amount' in df.columns:
#             df['value'] = df['monthly_amount']
#         else:
#             df['value'] = df['amount']
            
#         # Extract month
#         df['month'] = df['date'].dt.strftime('%b')
#         df['month_num'] = df['date'].dt.month
        
#         # Group by month
#         monthly_avg = df.groupby(['month', 'month_num'])['value'].mean().reset_index()
        
#         # Sort by month number
#         df = monthly_avg.sort_values('month_num')
    
#     # Create the figure
#     fig = go.Figure()
    
#     # Add bar chart
#     fig.add_trace(go.Bar(
#         x=df['month'],
#         y=df['value'],
#         name='Average Income',
#         marker_color='#0082c8',
#         hovertemplate='<b>%{x}</b><br>$%{y:,.2f}<extra></extra>'
#     ))
    
#     # Add line for overall average
#     overall_avg = df['value'].mean()
#     fig.add_trace(go.Scatter(
#         x=df['month'],
#         y=[overall_avg] * len(df),
#         mode='lines',
#         line=dict(color='#ff6b6b', width=2, dash='dash'),
#         name='Annual Average'
#     ))
    
#     # Style the chart
#     fig.update_layout(
#         title={
#             'text': 'Income Seasonality by Month',
#             'y':0.95,
#             'x':0.5,
#             'xanchor': 'center',
#             'yanchor': 'top',
#             'font': dict(family="Inter, Arial, sans-serif", size=18, color=COLORS_CHART['text'])
#         },
#         xaxis=dict(
#             title="Month",
#             categoryorder='array',
#             categoryarray=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
#         ),
#         yaxis=dict(
#             title="Average Monthly Income ($)",
#             tickprefix='$',
#             tickformat=',.0f'
#         ),
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         ),
#         margin=dict(l=40, r=40, t=80, b=40),
#         height=400,
#         paper_bgcolor='rgba(0,0,0,0)',
#         plot_bgcolor='rgba(255,255,255,0)'
#     )
    
#     fig.update_xaxes(
#         showgrid=False
#     )
    
#     fig.update_yaxes(
#         showgrid=True,
#         gridwidth=1,
#         gridcolor='rgba(226, 232, 240, 0.8)'
#     )
    
#     return fig

# def generate_income_growth_chart(income_data, settings=None):
#     """Generate year-over-year growth chart"""
#     import plotly.graph_objects as go
#     import pandas as pd
#     import numpy as np
#     from datetime import datetime, timedelta
    
#     # Create sample data if no data available
#     if not income_data or len(income_data) < 12:
#         # Generate sample data for 3 years
#         today = datetime.now()
#         dates = []
#         values = []
#         growth_rate = 0.08  # 8% annual growth
#         base_income = 4000
        
#         for i in range(-24, 12):
#             month_date = today + timedelta(days=30*i)
#             dates.append(month_date)
            
#             # Calculate years from start
#             years_from_start = (i + 24) / 12
            
#             # Compound growth with some randomness
#             compound_factor = (1 + growth_rate) ** years_from_start
#             variation = np.random.normal(0, 200)
#             values.append(base_income * compound_factor + variation)
            
#         df = pd.DataFrame({
#             'date': dates,
#             'value': values
#         })
#     else:
#         df = pd.DataFrame(income_data)
#         df['date'] = pd.to_datetime(df['date'])
        
#         if 'monthly_amount' in df.columns:
#             df['value'] = df['monthly_amount']
#         else:
#             df['value'] = df['amount']
    
#     # Extract year and month
#     df['year'] = df['date'].dt.year
#     df['month'] = df['date'].dt.month
#     df['year_month'] = df['date'].dt.strftime('%Y-%m')
    
#     # Calculate annual average
#     annual_avg = df.groupby('year')['value'].mean().reset_index()
    
#     # Calculate YoY growth
#     annual_avg['previous_year'] = annual_avg['value'].shift(1)
#     annual_avg['yoy_growth'] = (annual_avg['value'] - annual_avg['previous_year']) / annual_avg['previous_year'] * 100
#     annual_avg = annual_avg.dropna()
    
#     # Create the figure
#     fig = go.Figure()
    
#     # Add bar chart for growth rates
#     fig.add_trace(go.Bar(
#         x=annual_avg['year'].astype(str),
#         y=annual_avg['yoy_growth'],
#         name='YoY Growth',
#         marker_color=['#0082c8' if x > 0 else '#ff6b6b' for x in annual_avg['yoy_growth']],
#         hovertemplate='<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>'
#     ))
    
#     # Add line for absolute values
#     fig.add_trace(go.Scatter(
#         x=annual_avg['year'].astype(str),
#         y=annual_avg['value'],
#         mode='lines+markers',
#         line=dict(color='#228B22', width=2),
#         marker=dict(size=8),
#         name='Average Income',
#         yaxis='y2',
#         hovertemplate='<b>%{x}</b><br>Avg Income: $%{y:,.2f}<extra></extra>'
#     ))
    
#     # Style the chart
#     fig.update_layout(
#         title={
#             'text': 'Year-over-Year Income Growth',
#             'y':0.95,
#             'x':0.5,
#             'xanchor': 'center',
#             'yanchor': 'top',
#             'font': dict(family="Inter, Arial, sans-serif", size=18, color=COLORS_CHART['text'])
#         },
#         xaxis=dict(
#             title="Year"
#         ),
#         yaxis=dict(
#             title="YoY Growth (%)",
#             ticksuffix='%'
#         ),
#         yaxis2=dict(
#             title=dict(
#                 text="Average Income ($)",
#                 font=dict(color='#228B22')
#             ),
#             tickfont=dict(color='#228B22'),
#             tickprefix='$',
#             tickformat=',.0f',
#             overlaying='y',
#             side='right'
#         ),
#         legend=dict(
#             orientation="h",
#             yanchor="bottom",
#             y=1.02,
#             xanchor="right",
#             x=1
#         ),
#         margin=dict(l=40, r=80, t=80, b=40),
#         height=400,
#         paper_bgcolor='rgba(0,0,0,0)',
#         plot_bgcolor='rgba(255,255,255,0)'
#     )
    
#     fig.update_xaxes(
#         showgrid=False
#     )
    
#     fig.update_yaxes(
#         showgrid=True,
#         gridwidth=1,
#         gridcolor='rgba(226, 232, 240, 0.8)'
#     )
    
#     return fig

# def generate_income_chart(data, settings=None, months_ahead=6):
#     """Generate visually stunning income chart with forecast if requested"""
#     import pandas as pd
#     import plotly.graph_objects as go
#     from datetime import datetime, timedelta
#     import numpy as np
    
#     # Default settings
#     if settings is None:
#         settings = {}
    
#     # Get chart type from settings
#     chart_type = settings.get('chart_type', 'line')
    
#     # Colors for chart elements
#     COLORS_CHART = {
#         'primary': '#0082c8',  # Blue
#         'secondary': '#4ca3dd',  # Light blue
#         'accent': '#003c7f',  # Dark blue
#         'text': '#2d3748',  # Dark gray
#         'grid': 'rgba(226, 232, 240, 0.8)'  # Light gray
#     }
    
#     # Check if user_data is a list and convert to DataFrame
#     if isinstance(data, list) and len(data) > 0:
#         df = pd.DataFrame(data)
#     else:
#         # Return an elegant placeholder chart if no data
#         fig = go.Figure()
#         fig.add_annotation(
#             text="No income data available",
#             xref="paper", yref="paper",
#             x=0.5, y=0.5,
#             showarrow=False,
#             font=dict(size=18, family="Inter, Arial, sans-serif", color=COLORS_CHART['text'])
#         )
#         fig.update_layout(
#             paper_bgcolor='rgba(0,0,0,0)',
#             plot_bgcolor='rgba(255,255,255,0)',
#             height=450,
#             margin=dict(l=40, r=40, t=80, b=40),
#         )
#         return fig

#     # Prepare the data
#     df['date'] = pd.to_datetime(df['date'])
#     df = df.sort_values('date')
    
#     # Get monthly amounts
#     if 'monthly_amount' in df.columns:
#         df['value'] = df['monthly_amount']
#     else:
#         df['value'] = df['amount']
    
#     # Create forecast dates - next X months
#     forecast_months = months_ahead if isinstance(months_ahead, int) and months_ahead > 0 else 6
#     last_date = df['date'].max() if not df.empty else datetime.now()
#     forecast_dates = pd.date_range(start=last_date, periods=forecast_months+1, freq='ME')[1:]
    
#     # For forecasting, use trend-based projection
#     if len(df) >= 3:
#         # Calculate trend coefficient (simple linear regression)
#         x = np.arange(len(df))
#         y = df['value'].values
#         z = np.polyfit(x, y, 1)
#         slope = z[0]
        
#         # Use average of last 3 months as baseline
#         baseline = df['value'].tail(3).mean()
        
#         # Calculate trend
#         forecast_values = [baseline + (slope * i) for i in range(1, forecast_months+1)]
#     else:
#         # Fallback to simple growth model
#         avg_monthly = df['value'].mean() if not df.empty else 3000
#         forecast_values = [avg_monthly * (1 + (i * 0.02)) for i in range(forecast_months)]
    
#     # Create the figure
#     fig = go.Figure()
    
#     # Different chart types based on settings
#     if chart_type == 'bar':
#         # Historical data as bars
#         fig.add_trace(
#             go.Bar(
#                 x=df['date'],
#                 y=df['value'],
#                 name='Actual Income',
#                 marker_color=COLORS_CHART['primary'],
#                 hovertemplate='<b>%{x|%b %Y}</b><br>$%{y:,.2f}<extra></extra>'
#             )
#         )
        
#         # Forecast as bars with different color
#         fig.add_trace(
#             go.Bar(
#                 x=forecast_dates,
#                 y=forecast_values,
#                 name='Forecast',
#                 marker_color=COLORS_CHART['secondary'],
#                 marker_line=dict(width=1, color='white'),
#                 hovertemplate='<b>%{x|%b %Y} (Forecast)</b><br>$%{y:,.2f}<extra></extra>'
#             )
#         )
        
#     elif chart_type == 'area':
#         # Historical data with area
#         fig.add_trace(
#             go.Scatter(
#                 x=df['date'],
#                 y=df['value'],
#                 fill='tozeroy',
#                 fillcolor=f'rgba({int(COLORS_CHART["primary"][1:3], 16)}, {int(COLORS_CHART["primary"][3:5], 16)}, {int(COLORS_CHART["primary"][5:7], 16)}, 0.3)',
#                 line=dict(width=3, color=COLORS_CHART['primary']),
#                 name='Actual Income',
#                 hovertemplate='<b>%{x|%b %Y}</b><br>$%{y:,.2f}<extra></extra>'
#             )
#         )
        
#         # Forecast with area
#         fig.add_trace(
#             go.Scatter(
#                 x=forecast_dates,
#                 y=forecast_values,
#                 fill='tozeroy',
#                 fillcolor=f'rgba({int(COLORS_CHART["secondary"][1:3], 16)}, {int(COLORS_CHART["secondary"][3:5], 16)}, {int(COLORS_CHART["secondary"][5:7], 16)}, 0.2)',
#                 line=dict(width=2, color=COLORS_CHART['secondary'], dash='dot'),
#                 name='Forecast',
#                 hovertemplate='<b>%{x|%b %Y} (Forecast)</b><br>$%{y:,.2f}<extra></extra>'
#             )
#         )
    
#     elif chart_type == 'scatter':
#         # Historical data as scatter
#         fig.add_trace(
#             go.Scatter(
#                 x=df['date'],
#                 y=df['value'],
#                 mode='markers',
#                 marker=dict(
#                     size=10, 
#                     color=COLORS_CHART['primary'],
#                     line=dict(width=1, color='white')
#                 ),
#                 name='Actual Income',
#                 hovertemplate='<b>%{x|%b %Y}</b><br>$%{y:,.2f}<extra></extra>'
#             )
#         )
        
#         # Add trendline through the scatter
#         x_all = np.array(range(len(df) + forecast_months))
#         y_all = np.concatenate([df['value'].values, forecast_values])
#         z = np.polyfit(x_all, y_all, 1)
#         p = np.poly1d(z)
        
#         fig.add_trace(
#             go.Scatter(
#                 x=pd.concat([df['date'], pd.Series(forecast_dates)]),
#                 y=p(x_all),
#                 mode='lines',
#                 line=dict(color=COLORS_CHART['accent'], width=2),
#                 name='Trend',
#                 hovertemplate='<b>%{x|%b %Y} (Trend)</b><br>$%{y:,.2f}<extra></extra>'
#             )
#         )
        
#         # Forecast as different color scatter
#         fig.add_trace(
#             go.Scatter(
#                 x=forecast_dates,
#                 y=forecast_values,
#                 mode='markers',
#                 marker=dict(
#                     size=10, 
#                     color=COLORS_CHART['secondary'],
#                     line=dict(width=1, color='white'),
#                     symbol='diamond'
#                 ),
#                 name='Forecast',
#                 hovertemplate='<b>%{x|%b %Y} (Forecast)</b><br>$%{y:,.2f}<extra></extra>'
#             )
#         )
    
#     elif chart_type == 'pie':
#         # For pie chart, show income sources instead of time series
#         # Clear figure and create a new one
#         fig = go.Figure()
        
#         # Check if source exists in data
#         if 'source' in df.columns:
#             # Group by source
#             source_data = df.groupby('source')['value'].sum().reset_index()
            
#             fig.add_trace(
#                 go.Pie(
#                     labels=source_data['source'], 
#                     values=source_data['value'],
#                     textinfo='label+percent',
#                     marker=dict(
#                         colors=[COLORS_CHART['primary'], COLORS_CHART['secondary'], COLORS_CHART['accent']],
#                         line=dict(color='white', width=2)
#                     ),
#                     hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>'
#                 )
#             )
#         else:
#             # Default categories if source not available
#             fig.add_trace(
#                 go.Pie(
#                     labels=['Primary Income', 'Secondary Income', 'Investments'],
#                     values=[sum(df['value'])*0.7, sum(df['value'])*0.2, sum(df['value'])*0.1],
#                     textinfo='label+percent',
#                     marker=dict(
#                         colors=[COLORS_CHART['primary'], COLORS_CHART['secondary'], COLORS_CHART['accent']],
#                         line=dict(color='white', width=2)
#                     ),
#                     hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent}<extra></extra>'
#                 )
#             )
    
#     else:  # Default to line chart
#         # Add subtle area under the curve
#         fig.add_trace(
#             go.Scatter(
#                 x=df['date'],
#                 y=df['value'],
#                 fill='tozeroy',
#                 fillcolor=f'rgba({int(COLORS_CHART["primary"][1:3], 16)}, {int(COLORS_CHART["primary"][3:5], 16)}, {int(COLORS_CHART["primary"][5:7], 16)}, 0.1)',
#                 line=dict(width=0),
#                 showlegend=False,
#                 hoverinfo='none'
#             )
#         )
        
#         # Add historical data line
#         fig.add_trace(
#             go.Scatter(
#                 x=df['date'],
#                 y=df['value'],
#                 mode='lines+markers',
#                 name='Actual Income',
#                 marker=dict(
#                     size=8, 
#                     color=COLORS_CHART['primary'],
#                     line=dict(width=1, color='white')
#                 ),
#                 line=dict(width=3, color=COLORS_CHART['primary'], shape='spline'),
#                 hovertemplate='<b>%{x|%b %Y}</b><br>$%{y:,.2f}<extra></extra>'
#             )
#         )
        
#         # Add forecast line with elegant styling
#         fig.add_trace(
#             go.Scatter(
#                 x=forecast_dates,
#                 y=forecast_values,
#                 mode='lines+markers',
#                 name='Forecast',
#                 marker=dict(
#                     size=7, 
#                     color=COLORS_CHART['secondary'],
#                     line=dict(width=1, color='white')
#                 ),
#                 line=dict(width=2, color=COLORS_CHART['secondary'], dash='dot'),
#                 hovertemplate='<b>%{x|%b %Y} (Forecast)</b><br>$%{y:,.2f}<extra></extra>'
#             )
#         )
        
#         # Add moving average for trend visualization
#         if len(df) >= 3 and settings.get('show_trend', True):
#             df['moving_avg'] = df['value'].rolling(window=3, min_periods=1).mean()
#             fig.add_trace(
#                 go.Scatter(
#                     x=df['date'],
#                     y=df['moving_avg'],
#                     mode='lines',
#                     name='3-Month Trend',
#                     line=dict(width=2, color=COLORS_CHART['accent'], dash='dot'),
#                     opacity=0.7,
#                     hovertemplate='<b>%{x|%b %Y} (Trend)</b><br>$%{y:,.2f}<extra></extra>'
#                 )
#             )
    
#     # Style the chart based on the chart type
#     if chart_type == 'pie':
#         chart_title = 'Income Sources'
#         fig.update_layout(
#             title={
#                 'text': chart_title,
#                 'y':0.95,
#                 'x':0.5,
#                 'xanchor': 'center',
#                 'yanchor': 'top',
#                 'font': dict(family="Inter, Arial, sans-serif", size=22, color=COLORS_CHART['text'])
#             },
#             paper_bgcolor='rgba(0,0,0,0)',
#             plot_bgcolor='rgba(255,255,255,0)',
#             margin=dict(l=40, r=40, t=80, b=40),
#             height=450,
#             legend=dict(
#                 orientation="v",
#                 yanchor="middle",
#                 y=0.5,
#                 xanchor="right",
#                 x=1.1,
#                 bgcolor='rgba(255,255,255,0.9)',
#             ),
#             font=dict(family="Inter, Arial, sans-serif", color=COLORS_CHART['text']),
#             hoverlabel=dict(
#                 bgcolor="white",
#                 font_size=12,
#                 font_family="Inter, Arial, sans-serif"
#             )
#         )
#     else:
#         chart_title = 'Income Forecast'
#         if chart_type != 'line':
#             chart_title += f' ({chart_type.capitalize()})'
            
#         fig.update_layout(
#             title={
#                 'text': chart_title,
#                 'y':0.95,
#                 'x':0.5,
#                 'xanchor': 'center',
#                 'yanchor': 'top',
#                 'font': dict(family="Inter, Arial, sans-serif", size=22, color=COLORS_CHART['text'])
#             },
#             paper_bgcolor='rgba(0,0,0,0)',
#             plot_bgcolor='rgba(255,255,255,0)',
#             margin=dict(l=40, r=40, t=80, b=40),
#             height=450,
#             legend=dict(
#                 orientation="h",
#                 yanchor="bottom",
#                 y=1.02,
#                 xanchor="right",
#                 x=1,
#                 bgcolor='rgba(255,255,255,0.9)',
#             ),
#             font=dict(family="Inter, Arial, sans-serif", color=COLORS_CHART['text']),
#             hovermode="x unified",
#             hoverlabel=dict(
#                 bgcolor="white",
#                 font_size=12,
#                 font_family="Inter, Arial, sans-serif"
#             )
#         )
        
#         # Style axes for a refined, minimalist look
#         fig.update_xaxes(
#             title=dict(
#                 text="Date",
#                 font=dict(size=14, family="Inter, Arial, sans-serif")
#             ),
#             showgrid=True,
#             gridwidth=1,
#             gridcolor='rgba(226, 232, 240, 0.8)',
#             tickformat='%b %Y',
#             zeroline=False
#         )
        
#         fig.update_yaxes(
#             title=dict(
#                 text="Monthly Income ($)",
#                 font=dict(size=14, family="Inter, Arial, sans-serif")
#             ),
#             showgrid=True,
#             gridwidth=1,
#             gridcolor='rgba(226, 232, 240, 0.8)',
#             tickprefix='$',
#             tickformat=',.0f',
#             zeroline=False
#         )
    
#     return fig

# # Add this function to generate the multiple income charts modal
# def generate_income_insights_modal(user_data):
#     """Generate content for the income insights modal with multiple charts"""
#     income_data = user_data.get('income', [])
    
#     # Create a container with multiple charts and add buttons
#     modal_content = html.Div([
#         html.H3("Income Insights", className="insights-modal-title"),
#         html.P("Select charts to add to your dashboard.", className="insights-modal-subtitle"),
        
#         # Grid layout for charts
#         html.Div([
#             # Row 1
#             html.Div([
#                 # Chart 1: Income Forecast
#                 html.Div([
#                     html.Div([
#                         html.H4("Income Forecast", className="chart-title"),
#                         dcc.Graph(
#                             figure=generate_income_chart(income_data, {"chart_type": "line"}, 6),
#                             config={'displayModeBar': False},
#                             className="insights-chart"
#                         ),
#                         html.Button("Add to Dashboard", id="add-chart1", className="add-chart-btn")
#                     ], className="chart-card")
#                 ], className="chart-col"),
                
#                 # Chart 2: Income Sources
#                 html.Div([
#                     html.Div([
#                         html.H4("Income Sources", className="chart-title"),
#                         dcc.Graph(
#                             figure=generate_income_chart(income_data, {"chart_type": "pie"}),
#                             config={'displayModeBar': False},
#                             className="insights-chart"
#                         ),
#                         html.Button("Add to Dashboard", id="add-chart2", className="add-chart-btn")
#                     ], className="chart-card")
#                 ], className="chart-col")
#             ], className="chart-row"),
            
#             # Row 2
#             html.Div([
#                 # Chart 3: Monte Carlo Simulation
#                 html.Div([
#                     html.Div([
#                         html.H4("Monte Carlo Simulation", className="chart-title"),
#                         dcc.Graph(
#                             figure=generate_monte_carlo_simulation(income_data, {"simulations": 100}),
#                             config={'displayModeBar': False},
#                             className="insights-chart"
#                         ),
#                         html.Button("Add to Dashboard", id="add-chart3", className="add-chart-btn")
#                     ], className="chart-card")
#                 ], className="chart-col"),
                
#                 # Chart 4: Income Heatmap
#                 html.Div([
#                     html.Div([
#                         html.H4("Income Heatmap", className="chart-title"),
#                         dcc.Graph(
#                             figure=generate_income_heatmap(income_data, {}),
#                             config={'displayModeBar': False},
#                             className="insights-chart"
#                         ),
#                         html.Button("Add to Dashboard", id="add-chart4", className="add-chart-btn")
#                     ], className="chart-card")
#                 ], className="chart-col")
#             ], className="chart-row"),
            
#             # Row 3
#             html.Div([
#                 # Chart 5: Income Seasonality
#                 html.Div([
#                     html.Div([
#                         html.H4("Income Seasonality", className="chart-title"),
#                         dcc.Graph(
#                             figure=generate_income_seasonality(income_data, {}),
#                             config={'displayModeBar': False},
#                             className="insights-chart"
#                         ),
#                         html.Button("Add to Dashboard", id="add-chart5", className="add-chart-btn")
#                     ], className="chart-card")
#                 ], className="chart-col"),
                
#                 # Chart 6: Year-over-Year Growth
#                 html.Div([
#                     html.Div([
#                         html.H4("Year-over-Year Growth", className="chart-title"),
#                         dcc.Graph(
#                             figure=generate_income_growth_chart(income_data, {}),
#                             config={'displayModeBar': False},
#                             className="insights-chart"
#                         ),
#                         html.Button("Add to Dashboard", id="add-chart6", className="add-chart-btn")
#                     ], className="chart-card")
#                 ], className="chart-col")
#             ], className="chart-row")
#         ], className="insights-chart-grid")
#     ], className="insights-modal-content")
    
#     return modal_content

# # Add callback for opening the multi-chart insights modal
# @callback(
#     [
#         Output("income-insights-modal", "is_open"),
#         Output("income-insights-content", "children")
#     ],
#     [Input("current-chart-store", "data")],
#     [State("user-data-store", "data")],
#     prevent_initial_call=True
# )
# def handle_insights_modal(chart_data, user_data):
#     """Open insights modal with multiple charts when requested"""
#     print('Handing Insight modal generation')
#     if chart_data and chart_data.get("open_insights_modal") and chart_data.get("show_multiple_charts"):
#         modal_content = generate_income_insights_modal(user_data)
#         return True, modal_content
    
#     return False, None

# # Add callbacks for the add-chart buttons in the insights modal
# @callback(
#     [
#         Output("current-chart-store", "data", allow_duplicate=True),
#         Output("add-component-modal", "is_open", allow_duplicate=True),
#         Output("income-insights-modal", "is_open", allow_duplicate=True)
#     ],
#     [
#         Input("add-chart1", "n_clicks"),
#         Input("add-chart2", "n_clicks"),
#         Input("add-chart3", "n_clicks"),
#         Input("add-chart4", "n_clicks"),
#         Input("add-chart5", "n_clicks"),
#         Input("add-chart6", "n_clicks")
#     ],
#     [State("user-data-store", "data")],
#     prevent_initial_call=True
# )
# def add_chart_from_insights(n1, n2, n3, n4, n5, n6, user_data):
#     """Add a chart from the insights modal to the dashboard"""
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         raise PreventUpdate
    
#     # Determine which button was clicked
#     button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
#     chart_data = None
    
#     if button_id == "add-chart1":
#         chart_data = {
#             'type': 'income_forecast',
#             'title': 'Income Forecast',
#             'months_ahead': 6,
#             'settings': {'chart_type': 'line', 'show_trend': True}
#         }
#     elif button_id == "add-chart2":
#         chart_data = {
#             'type': 'income_chart',
#             'title': 'Income Sources',
#             'settings': {'chart_type': 'pie'}
#         }
#     elif button_id == "add-chart3":
#         chart_data = {
#             'type': 'monte_carlo',
#             'title': 'Monte Carlo Simulation',
#             'settings': {'simulations': 100}
#         }
#     elif button_id == "add-chart4":
#         chart_data = {
#             'type': 'income_heatmap',
#             'title': 'Income Heatmap',
#             'settings': {}
#         }
#     elif button_id == "add-chart5":
#         chart_data = {
#             'type': 'income_seasonality',
#             'title': 'Income Seasonality',
#             'settings': {}
#         }
#     elif button_id == "add-chart6":
#         chart_data = {
#             'type': 'income_growth',
#             'title': 'Year-over-Year Growth',
#             'settings': {}
#         }
    
#     # Close insights modal and open add component modal
#     return chart_data, True, False

# def generate_expense_breakdown(data, settings=None, period='monthly'):
#     """Generate visually stunning expense breakdown chart based on user data"""
#     import pandas as pd
#     import plotly.graph_objects as go
#     import plotly.express as px
#     from datetime import datetime
#     import numpy as np
    
#     # Default settings
#     if settings is None:
#         settings = {}
    
#     # Check if user_data is a list and convert to DataFrame
#     if isinstance(data, list) and len(data) > 0:
#         df = pd.DataFrame(data)
#     else:
#         # Create demo data with realistic categories
#         df = pd.DataFrame({
#             'category': ['Housing', 'Food & Groceries', 'Transportation', 'Entertainment', 
#                          'Utilities', 'Healthcare', 'Savings', 'Education'],
#             'amount': [1500, 600, 350, 250, 300, 200, 400, 150],
#             'date': [datetime.now()] * 8
#         })
    
#     # Prepare the data
#     if 'date' in df.columns:
#         df['date'] = pd.to_datetime(df['date'])
        
#         # Filter by period if specified
#         if period == 'monthly' and len(df) > 0:
#             current_month = df['date'].max().month
#             current_year = df['date'].max().year
#             df = df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year)]
#         elif period == 'yearly' and len(df) > 0:
#             current_year = df['date'].max().year
#             df = df[df['date'].dt.year == current_year]
    
#     # Group by category
#     df_grouped = df.groupby('category')['amount'].sum().reset_index()
#     df_grouped = df_grouped.sort_values('amount', ascending=False)
    
#     # Calculate percentages for labels
#     total = df_grouped['amount'].sum()
#     df_grouped['percent'] = df_grouped['amount'] / total * 100
    
#     # Chart selection - allow customization through settings
#     chart_type = settings.get('chart_type', 'donut') if settings else 'donut'
    
#     if chart_type == 'pie' or chart_type == 'donut':
#         # Create a clean, modern donut chart
#         hole_size = 0.6 if chart_type == 'donut' else 0
        
#         fig = go.Figure()
#         fig.add_trace(go.Pie(
#             labels=df_grouped['category'],
#             values=df_grouped['amount'],
#             textinfo='label+percent',
#             textposition='outside',
#             marker=dict(
#                 COLORS_CHART=COLORS_CHART['chart_palette'],
#                 line=dict(color='white', width=1)
#             ),
#             hole=hole_size,
#             hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{percent:.1f}%<extra></extra>',
#             rotation=90
#         ))
        
#         # Add center text for donut chart
#         if chart_type == 'donut':
#             fig.add_annotation(
#                 text=f"<b>${total:,.0f}</b>",
#                 x=0.5, y=0.5,
#                 font=dict(size=20, color=COLORS_CHART['primary'], family="Inter, Arial, sans-serif"),
#                 showarrow=False
#             )
    
#     elif chart_type == 'bar':
#         # Create a clean bar chart
#         fig = go.Figure()
        
#         # Determine gradient COLORS_CHART based on rank
#         color_scale = px.COLORS_CHART.sequential.Blues
        
#         # Create one trace with all bars
#         fig.add_trace(go.Bar(
#             x=df_grouped['category'],
#             y=df_grouped['amount'],
#             marker=dict(
#                 color=df_grouped['amount'],
#                 COLORS_CHARTcale=color_scale,
#                 line=dict(width=0)
#             ),
#             text=[f"${amount:,.0f}" for amount in df_grouped['amount']],
#             textposition='auto',
#             hovertemplate='<b>%{x}</b><br>$%{y:,.2f}<br>%{text}<extra></extra>'
#         ))
        
#         fig.update_layout(
#             xaxis=dict(
#                 categoryorder='total descending',
#                 title=None
#             )
#         )
    
#     elif chart_type == 'treemap':
#         # Create simple, elegant treemap
#         fig = px.treemap(
#             df_grouped,
#             path=['category'],
#             values='amount',
#             color='amount',
#             color_continuous_scale=px.COLORS_CHART.sequential.Blues,
#             hover_data=['percent']
#         )
#         fig.update_traces(
#             hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{customdata[0]:.1f}%<extra></extra>',
#             texttemplate='<b>%{label}</b><br>$%{value:,.0f}',
#             textfont=dict(family="Inter, Arial, sans-serif", size=14)
#         )
        
#     else:  # Default to sunburst for a clean, modern visualization
#         # Create simplified sunburst
#         fig = px.sunburst(
#             df_grouped,
#             path=['category'],
#             values='amount',
#             color='amount',
#             color_continuous_scale=px.COLORS_CHART.sequential.Blues,
#             hover_data=['percent']
#         )
#         fig.update_traces(
#             textinfo='label+value',
#             hovertemplate='<b>%{label}</b><br>$%{value:,.2f}<br>%{customdata[0]:.1f}%<extra></extra>'
#         )
    
#     # Apply clean, minimalist styling to all chart types
#     title_text = "Expense Breakdown"
#     if period == 'monthly':
#         if 'date' in df.columns and not df.empty:
#             month_year = df['date'].iloc[0].strftime('%B %Y')
#             title_text = f"Monthly Expenses - {month_year}"
#     elif period == 'yearly':
#         if 'date' in df.columns and not df.empty:
#             year = df['date'].iloc[0].strftime('%Y')
#             title_text = f"Yearly Expenses - {year}"
    
#     fig.update_layout(
#         title={
#             'text': title_text,
#             'y':0.95,
#             'x':0.5,
#             'xanchor': 'center',
#             'yanchor': 'top',
#             'font': dict(family="Inter, Arial, sans-serif", size=22, color=COLORS_CHART['text'])
#         },
#         paper_bgcolor='rgba(0,0,0,0)',
#         plot_bgcolor='rgba(255,255,255,0)',
#         margin=dict(l=20, r=20, t=80, b=20),
#         height=450,
#         font=dict(family="Inter, Arial, sans-serif", color=COLORS_CHART['text']),
#         hoverlabel=dict(
#             bgcolor="white",
#             font_size=12,
#             font_family="Inter, Arial, sans-serif"
#         )
#     )
    
#     # If it's a bar chart, style the axes
#     if chart_type == 'bar':
#         fig.update_yaxes(
#             title=dict(
#                 text="Amount ($)",
#                 font=dict(size=14, family="Inter, Arial, sans-serif")
#             ),
#             showgrid=True,
#             gridwidth=1,
#             gridcolor='rgba(226, 232, 240, 0.8)',
#             tickprefix='$',
#             tickformat=',.0f',
#             zeroline=False
#         )
    
#     return fig

# # Layout for the chat/AI dashboard page
# layout = html.Div([
#     # Stores for maintaining state
#     dcc.Store(id="session-data-store", storage_type="local"),
#     dcc.Store(id='user-id-store', storage_type='local'),
#     dcc.Store(id='user-data-store', storage_type='session'),
#     dcc.Store(id='dashboard-settings-store', storage_type='local'),
#     dcc.Store(id="dropdown-state", storage_type="memory", data=False),
#     dcc.Store(id='layouts-store', storage_type='local'),
#     dcc.Location(id='url', refresh=False),
    
#     # Page header with navigation
#     html.Div([
#         html.Img(src="/assets/Logo_slogan.PNG", className="dashboard-logo"),
        
#         html.Nav([
#             html.Button([
#                 html.Span("BlueCard Finance", className="mobile-nav-toggle-text"),
#                 html.Span("≡")
#             ], className="mobile-nav-toggle", id="mobile-nav-toggle"),

#             html.Ul([
#                 html.Li(html.A([html.Span(className="nav-icon"), "Home"], href="/", className="nav-link"), className="nav-item"),
#                 html.Li(html.A([html.Span(className="nav-icon"), "Dashboard"], href="/dashboard", className="nav-link"), className="nav-item"),
#                 html.Li(html.A([html.Span(className="nav-icon"), "Income"], href="/income", className="nav-link"), className="nav-item"),
#                 html.Li(html.A([html.Span(className="nav-icon"), "Expenses"], href="/expenses", className="nav-link"), className="nav-item"),
#                 html.Li(html.A([html.Span(className="nav-icon"), "Savings Analysis"], href="/savings", className="nav-link"), className="nav-item"),
#                 html.Li(html.A([html.Span(className="nav-icon"), "Chat"], href="/chat", className="nav-link active"), className="nav-item")
#             ], className="nav-menu", id="nav-menu"),
            
#             html.Div([
#                 html.Div([
#                     html.Button([
#                         html.I(className="fas fa-user-circle", style={'fontSize': '24px'}),
#                     ], id="user-dropdown-button", className="user-dropdown-button"),
                    
#                     html.Div([
#                         html.Div(id="user-email-display", className="user-email"),
#                         html.Hr(style={'margin': '8px 0'}),
#                         html.A("Profile", href="/profile", className="dropdown-item"),
#                         html.A("Logout", id="logout-link", href="/logout", className="dropdown-item")
#                     ], id="user-dropdown-content", className="user-dropdown-content")
#                 ], className="user-dropdown"),
#             ], id="user-account-container", className="user-account-container"),
#         ], className="nav-bar"),
#     ], className="header-container"),
    
#     # Main content area
#     html.Div([
#         # Sidebar for chat/AI interaction
#         html.Div([
#             html.H2("AI Financial Assistant", className="sidebar-title"),
#             html.P("Ask me anything about your finances or request specific charts.", className="sidebar-description"),
#             html.Div(id="chat-history", className="chat-history"),
#             html.Div([
#                 dcc.Input(id="chat-input", type="text", placeholder="Ask about your finances...", className="chat-input"),
#                 html.Button([html.I(className="fas fa-paper-plane")], id="send-chat", className="send-chat-button")
#             ], className="chat-input-container")
#         ], className="chat-sidebar"),
        
#         # Dashboard main area
#         html.Div([
#             html.Div([
#                 html.H1("Your Financial Dashboard", className="dashboard-title"),
#                 html.Div(id="last-updated", className="last-updated")
#             ], className="dashboard-header"),
            
#             # Empty state for new users
#             html.Div([
#                 html.Div([
#                     # Hero Image Section with a welcoming visual
#                     html.Div([
#                         html.Img(src="/assets/dashboard_pc.png", className="empty-dashboard-img"),
#                     ], className="empty-dashboard-img-container"),
                    
#                     # Title Section - Make the message more inviting
#                     html.H3("Welcome to Your Dashboard!", className="empty-dashboard-title"),

#                     # Subtitle or Description - Add a more friendly and engaging description
#                     html.P(
#                         "It looks like your dashboard is empty. Let's get started by adding your data and insights.",
#                         className="empty-dashboard-desc"
#                     ),
                    
#                     # Actionable prompt to guide the user (with button styles)
#                     html.P(
#                         "Need inspiration? Try this prompt to get started:",
#                         className="empty-dashboard-prompt-desc"
#                     ),
                    
#                     html.Button(
#                         "Show me my income forecast",
#                         id="sample-prompt-button",
#                         className="sample-prompt-button"
#                     ),

#                     # Optional: Add a small tip or fun fact to make it more engaging
#                     html.Div(
#                         "Tip: You can always chat with the AI assistant to get personalized insights!",
#                         className="empty-dashboard-tip"
#                     )
#                 ], className="empty-dashboard-content"),

#                 # Optional: You could add an animated illustration or an icon for fun
#                 html.Div(
#                     html.Img(src="/assets/assistant_welcome_icon.png", className="assistant-welcome-icon"),
#                     className="assistant-icon-container"
#                 )
#             ], id="empty-dashboard-state", className="empty-dashboard-state"),

#             # Dashboard grid (updated to dash_draggable)
#             dash_draggable.ResponsiveGridLayout(
#                 id="dashboard-grid",
#                 children=[],
#                 layouts={},
#                 isDraggable=True,
#                 isResizable=True,
#                 preventCollision=True,
#                 compactType=None,
#                 breakpoints={"lg": 1200, "md": 996, "sm": 768, "xs": 480, "xxs": 0},
#                 gridCols={"lg": 12, "md": 10, "sm": 6, "xs": 4, "xxs": 2},
#                 style={"backgroundColor": "#f8f9fa", "height": "100%", "minHeight": "600px"},
#                 save=True
#             ),
#         ], className="dashboard-main"),
#     ], className="chat-dashboard-container"),

#     # Modals
#     dbc.Modal([
#         dbc.ModalHeader("Income Management"),
#         dbc.ModalBody([
#             html.Iframe(
#                 id="income-page-iframe",
#                 src="",
#                 style={"width": "100%", "height": "70vh", "border": "none"},
#             )
#         ]),
#         dbc.ModalFooter([
#             dbc.Button("Close", id="close-income-modal", className="ml-auto")
#         ])
#     ], id="income-page-modal", size="xl", className="custom-modal"),
    
#     dbc.Modal([
#         dbc.ModalHeader("Add Component to Dashboard"),
#         dbc.ModalBody([
#             html.P("Do you want to add this chart to your dashboard?"),
#             html.Div(id="preview-component", className="preview-component")
#         ]),
#         dbc.ModalFooter([
#             dbc.Button("Cancel", id="add-component-cancel", className="mr-2"),
#             dbc.Button("Add to Dashboard", id="add-component-confirm", color="primary")
#         ])
#     ], id="add-component-modal"),

#     dbc.Modal([
#         dbc.ModalHeader("Income Insights"),
#         dbc.ModalBody([
#             html.Div(id="income-insights-content", className="insights-modal-content")
#         ]),
#         dbc.ModalFooter([
#             dbc.Button("Close", id="close-insights-modal", className="ml-auto")
#         ])
#     ], id="income-insights-modal", size="xl", className="custom-modal"),

#     # Footer
#     html.Footer([
#     # Modern top section with logo and quick links
#     html.Div([
#         # Left side with logo and tagline
#         html.Div([
#             html.Img(src="/assets/Logo_slogan.PNG", className="footer-logo", style={
#                 "height": "140px",
#                 "marginBottom": "10px",
#                 "filter": "brightness(1.1) contrast(1.1)"
#             }),
#             # html.P("Empowering your financial future", style={
#             #     "color": "#ffffff",
#             #     "fontSize": "14px",
#             #     "fontWeight": "300",
#             #     "letterSpacing": "0.5px",
#             #     "margin": "0"
#             # })
#         ], className="footer-branding", style={
#             "flex": "2",
#             "marginRight": "40px"
#         }),
        
#         # Middle section with quick links
#         html.Div([
#             html.H4("Quick Links", style={
#                 "fontSize": "16px",
#                 "fontWeight": "600",
#                 "color": "#ffffff",
#                 "marginBottom": "15px",
#                 "borderBottom": "2px solid rgba(255,255,255,0.2)",
#                 "paddingBottom": "8px"
#             }),
#             html.Ul([
#                 html.Li(html.A("Home", href="/", className="footer-link"), style={"marginBottom": "8px"}),
#                 html.Li(html.A("Dashboard", href="/dashboard", className="footer-link"), style={"marginBottom": "8px"}),
#                 html.Li(html.A("Income", href="/income", className="footer-link"), style={"marginBottom": "8px"}),
#                 html.Li(html.A("Expenses", href="/expenses", className="footer-link"), style={"marginBottom": "8px"}),
#                 html.Li(html.A("Savings Analysis", href="/savings", className="footer-link"), style={"marginBottom": "8px"}),
#                 html.Li(html.A("Settings", href="/settings", className="footer-link"), style={"marginBottom": "8px"}),
#             ], style={
#                 "listStyleType": "none",
#                 "padding": "0",
#                 "margin": "0"
#             })
#         ], className="footer-links", style={"flex": "1"}),
        
#         # Right section with contact info
#         html.Div([
#             html.H4("Contact", style={
#                 "fontSize": "16px",
#                 "fontWeight": "600",
#                 "color": "#ffffff",
#                 "marginBottom": "15px",
#                 "borderBottom": "2px solid rgba(255,255,255,0.2)",
#                 "paddingBottom": "8px"
#             }),
#             html.Div([
#                 html.P([
#                     html.I(className="fas fa-envelope", style={"width": "20px", "marginRight": "10px"}),
#                     "support@bluecardfinance.com"
#                 ], style={"marginBottom": "10px", "fontSize": "14px"}),
#                 html.P([
#                     html.I(className="fas fa-phone", style={"width": "20px", "marginRight": "10px"}),
#                     "(+44) 555-0XXX"
#                 ], style={"marginBottom": "10px", "fontSize": "14px"}),
#                 html.P([
#                     html.I(className="fas fa-map-marker-alt", style={"width": "20px", "marginRight": "10px"}),
#                     "123 Finance St, London, LN"
#                 ], style={"marginBottom": "10px", "fontSize": "14px"})
#             ])
#         ], className="footer-contact", style={"flex": "1"})
#     ], className="footer-top", style={
#         "display": "flex",
#         "justifyContent": "space-between",
#         "padding": "40px 60px",
#         "backgroundColor": "rgba(0,0,0,0.1)",
#         "borderBottom": "1px solid rgba(255,255,255,0.1)",
#         "flexWrap": "wrap",
#         "gap": "30px"
#     }),
    
#     # Middle social media section
#     html.Div([
#         html.H4("Connect With Us", style={
#             "margin": "0 20px 0 0",
#             "color": "#ffffff",
#             "fontSize": "16px",
#             "fontWeight": "400"
#         }),
#         html.Div([
#             html.A(html.I(className="fab fa-facebook-f"), href="#", className="social-icon", style={
#                 "backgroundColor": "rgba(255,255,255,0.1)",
#                 "color": "#ffffff",
#                 "width": "40px",
#                 "height": "40px",
#                 "borderRadius": "50%",
#                 "display": "flex",
#                 "alignItems": "center",
#                 "justifyContent": "center",
#                 "marginRight": "12px",
#                 "fontSize": "16px"
#             }),
#             html.A(html.I(className="fab fa-twitter"), href="#", className="social-icon", style={
#                 "backgroundColor": "rgba(255,255,255,0.1)",
#                 "color": "#ffffff",
#                 "width": "40px",
#                 "height": "40px",
#                 "borderRadius": "50%",
#                 "display": "flex",
#                 "alignItems": "center",
#                 "justifyContent": "center",
#                 "marginRight": "12px",
#                 "fontSize": "16px"
#             }),
#             html.A(html.I(className="fab fa-linkedin-in"), href="#", className="social-icon", style={
#                 "backgroundColor": "rgba(255,255,255,0.1)",
#                 "color": "#ffffff",
#                 "width": "40px",
#                 "height": "40px",
#                 "borderRadius": "50%",
#                 "display": "flex",
#                 "alignItems": "center",
#                 "justifyContent": "center",
#                 "marginRight": "12px",
#                 "fontSize": "16px"
#             }),
#             html.A(html.I(className="fab fa-instagram"), href="#", className="social-icon", style={
#                 "backgroundColor": "rgba(255,255,255,0.1)",
#                 "color": "#ffffff",
#                 "width": "40px",
#                 "height": "40px",
#                 "borderRadius": "50%",
#                 "display": "flex",
#                 "alignItems": "center",
#                 "justifyContent": "center",
#                 "marginRight": "12px",
#                 "fontSize": "16px"
#             })
#         ], style={"display": "flex"})
#     ], className="footer-social", style={
#         "display": "flex",
#         "justifyContent": "center",
#         "alignItems": "center",
#         "padding": "20px 60px",
#         "borderBottom": "1px solid rgba(255,255,255,0.1)"
#     }),
    
#     # Bottom copyright section
#     html.Div([
#         html.P("© 2025 BlueCard Finance. All rights reserved.", style={
#             "color": "rgba(255,255,255,0.7)",
#             "margin": "0",
#             "fontSize": "14px"
#         }),
#         html.Div([
#             html.A("Privacy Policy", href="#", className="footer-link"),
#             html.Span("•", style={"color": "rgba(255,255,255,0.4)", "margin": "0 10px"}),
#             html.A("Terms of Service", href="#", className="footer-link"),
#             html.Span("•", style={"color": "rgba(255,255,255,0.4)", "margin": "0 10px"}),
#             html.A("Cookie Policy", href="#", className="footer-link")
#         ])
#     ], className="footer-bottom", style={
#         "display": "flex",
#         "justifyContent": "space-between",
#         "padding": "20px 60px",
#         "flexWrap": "wrap",
#         "gap": "15px"
#     })
# ], className="dashboard-footer", style={
#     "backgroundColor": COLORS['primary'],
#     "color": "#ffffff",
#     "boxShadow": "0px -4px 10px rgba(0,0,0,0.1)"
# }),

#     # Draggable Script (no longer needed with dash_draggable) — you can remove this:
#     # html.Script(id="dashboard-draggable-script", src="/assets/dashboard-draggable.js"),

#     html.Div(id="listener-setup-trigger-div", style={"display": "none"}),
#     html.Div(id="dashboard-event-trigger", style={"display": "none"}),

#     dcc.Store(id='dashboard-position-store', storage_type='memory'),
#     dcc.Interval(id='layout-update-interval', interval=1000, n_intervals=0),
#     dcc.Store(id="insights-charts-store", storage_type="memory"),
#     dcc.Store(id="current-chart-store", storage_type="memory")
# ], className="chat-page-container")

# # Callbacks for chat functionality

# # Handle chat input
# # Update handle_chat_input to properly pass the modal flags
# @callback(
#     [
#         Output("chat-history", "children"),
#         Output("current-chart-store", "data", allow_duplicate=True),
#         Output("preview-component", "children"),
#         Output("add-component-modal", "is_open", allow_duplicate=True)
#     ],
#     [
#         Input("send-chat", "n_clicks"),
#         Input("chat-input", "n_submit"),
#         Input("sample-prompt-button", "n_clicks")
#     ],
#     [
#         State("chat-input", "value"),
#         State("chat-history", "children"),
#         State("user-data-store", "data")
#     ],
#     prevent_initial_call=True
# )
# def handle_chat_input(n_clicks, n_submit, sample_click, input_value, current_chat, user_data):
#     """Process user input and generate AI response with charts."""
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         return current_chat or [], dash.no_update, dash.no_update, dash.no_update
    
#     # Handle text input or sample prompt button
#     if ctx.triggered[0]['prop_id'] == "sample-prompt-button.n_clicks":
#         user_message = "Show me my income forecast"
#     else:
#         if not input_value:
#             return current_chat or [], dash.no_update, dash.no_update, dash.no_update
#         user_message = input_value
    
#     # Initialize chat history if needed
#     if not current_chat:
#         current_chat = []
    
#     # Add user message to chat
#     user_message_div = html.Div([html.Div(user_message, className="user-message-content")], className="user-message")
#     current_chat.append(user_message_div)
    
#     # Process the query and generate response
#     ai_message, chart_component, chart_data, modal_flags = process_chat_query(user_message, user_data)
    
#     # Create a unique index for this message pair
#     message_index = len(current_chat)
    
#     # Add AI response to chat
#     ai_message_div = html.Div([
#         html.Img(src="/assets/avatar.png", className="ai-avatar"),
#         html.Div([
#             html.Div(ai_message, className="ai-message-content"),
#             html.Div(chart_component, className="ai-chart-container") if chart_component else None
#         ], className="ai-message-wrapper")
#     ], className="ai-message")
#     current_chat.append(ai_message_div)
    
#     # Generate preview component if chart exists
#     preview_component = None
#     if chart_data:
#         if chart_data['type'] in ['income_chart', 'income_forecast']:
#             preview = dcc.Graph(
#                 print('Generating Income Chart Now'),
#                 figure=generate_income_chart(user_data.get('income', []), 
#                                             chart_data.get('settings', {}),
#                                             chart_data.get('months_ahead', 6)),
#                 config={'displayModeBar': False}
#             )
#         elif chart_data['type'] == 'expense_breakdown':
#             preview = dcc.Graph(
#                 figure=generate_expense_breakdown(user_data.get('expenses', []), 
#                                                  chart_data.get('settings', {})),
#                 config={'displayModeBar': False}
#             )
#         else:
#             preview = html.Div("Chart preview not available")
        
#         preview_component = preview
    
#     # If we have modal flags from process_chat_query, use those instead of chart_data
#     if modal_flags is not None:
#         chart_data = modal_flags  # This will pass the flags to current-chart-store
#         should_open_modal = False  # Don't open the add component modal in this case
#     else:
#         should_open_modal = chart_data is not None
    
#     return current_chat, chart_data, preview_component, should_open_modal

# def process_chat_query(query, user_data):
#     """Process the user query and generate appropriate response and chart"""
#     query = query.lower().strip()
#     income_data = user_data.get('income', [])

#     # Extract chart type if specified
#     chart_type = "line"  # Default chart type
#     if "bar chart" in query or "barchart" in query:
#         chart_type = "bar"
#     elif "pie chart" in query or "piechart" in query:
#         chart_type = "pie"
#     elif "area chart" in query or "areachart" in query:
#         chart_type = "area"
#     elif "scatter" in query:
#         chart_type = "scatter"
#     elif "line chart" in query or "linechart" in query:
#         chart_type = "line"
    
#     # Check for explicit requests to view or manage income
#     if any(phrase in query for phrase in [
#             "add to my income", 
#             "manage income",
#             "edit my income",
#             "manage my income"
#         ]):
#         # Return a flag to open the income modal
#         message = "I'll open the income management page for you where you can view and edit your income details."
#         return message, None, None, {"open_income_modal": True}
    
#     # Handle income-related queries
#     elif any(keyword in query for keyword in ["income", "earning", "revenue", "salary"]):
#         # Check if it's a general income question that should open the insights modal
#         print('Generating Deep Income Analysis')
#         if any(pattern in query for pattern in [
#             "what's my income", 
#             "what is my income",
#             "show me my income",
#             "how much do i earn",
#             "income breakdown",
#             "income overview",
#             "tell me about my income"
#         ]):
#             message = "I've prepared a detailed income analysis for you with multiple visualizations. You can view these charts and add any of them to your dashboard."
            
#             # Return a signal to open the income insights modal with multiple charts
#             return message, None, None, {"open_insights_modal": True, "show_multiple_charts": True}
        
#         # Check if it's a forecast request
#         elif any(keyword in query for keyword in ["forecast", "future", "predict", "projection"]):
#             print('Generating Forecast Income Chart')
#             # Extract number of months if specified
#             import re
#             months_match = re.search(r"(\d+)\s*months?", query)
#             months_ahead = int(months_match.group(1)) if months_match else 6
            
#             # Generate income forecast chart with specified chart type
#             figure = generate_income_chart(income_data, {"chart_type": chart_type}, months_ahead)
            
#             chart_component = dcc.Graph(
#                 figure=figure,
#                 config={'displayModeBar': False}
#             )
            
#             chart_data = {
#                 'type': 'income_forecast',
#                 'title': f'Income Forecast ({months_ahead} months)',
#                 'months_ahead': months_ahead,
#                 'settings': {'show_trend': True, 'chart_type': chart_type}
#             }
            
#             chart_type_name = chart_type.capitalize()
#             message = f"Based on your income history, I've created a {chart_type_name} chart forecast for the next {months_ahead} months."
#             if not income_data:
#                 message += " (Using sample data since no income history was found)"
            
#             return message, chart_component, chart_data, None
        
#         else:
#             # Basic income breakdown
#             print('Generating Basic Income Chart')
#             figure = generate_income_chart(income_data, {"chart_type": chart_type})
            
#             chart_component = dcc.Graph(
#                 figure=figure,
#                 config={'displayModeBar': False}
#             )
            
#             chart_data = {
#                 'type': 'income_chart',
#                 'title': 'Monthly Income',
#                 'settings': {'chart_type': chart_type}
#             }
            
#             chart_type_name = chart_type.capitalize()
#             message = f"Here's your monthly income overview as a {chart_type_name} chart with a short-term forecast."
#             if not income_data:
#                 message += " (Using sample data since no income history was found)"
            
#             return message, chart_component, chart_data, None
    
#     # Handle expense-related queries
#     elif any(keyword in query for keyword in ["expense", "spending", "cost", "payment"]):
#         expense_data = user_data.get('expenses', [])
        
#         # Default to pie chart for expenses if no specific chart type requested
#         if chart_type == "line" and "pie" not in query and "bar" not in query:
#             chart_type = "pie"
            
#         figure = generate_expense_breakdown(expense_data, {"chart_type": chart_type})
        
#         chart_component = dcc.Graph(
#             figure=figure,
#             config={'displayModeBar': False}
#         )
        
#         chart_data = {
#             'type': 'expense_breakdown',
#             'title': 'Expense Breakdown',
#             'settings': {'chart_type': chart_type}
#         }
        
#         chart_type_name = chart_type.capitalize()
#         message = f"Here's a breakdown of your expenses by category as a {chart_type_name} chart."
#         if not expense_data:
#             message += " (Using sample data since no expense history was found)"
        
#         return message, chart_component, chart_data, None
    
#     # Handle general financial advice
#     elif any(keyword in query for keyword in ["advice", "tip", "suggestion", "recommend"]):
#         message = """
#         Here are some financial tips based on best practices:
        
#         1. Aim to save at least 20% of your income
#         2. Build an emergency fund covering 3-6 months of expenses
#         3. Pay off high-interest debt first
#         4. Take advantage of employer retirement matching
#         5. Review your budget regularly
        
#         Would you like me to create a specific chart or analysis to help with any of these areas?
#         """
        
#         return message, None, None, None
    
#     # Default response for other queries
#     else:
#         message = """
#         I can help you analyze your finances in various ways. You can ask me to:
        
#         • Show income forecasts (as line, bar, or area charts)
#         • Create expense breakdowns (as pie or bar charts)
#         • Analyze savings goals
#         • Calculate budget recommendations
#         • Compare spending patterns
        
#         Try asking about your income or expenses to get started!
#         """
        
#         return message, None, None, None

# # Fix for the add_component_to_dashboard function
# @callback(
#     [
#         Output("dashboard-settings-store", "data", allow_duplicate=True),
#         Output("empty-dashboard-state", "style", allow_duplicate=True),
#         Output("dashboard-grid", "children", allow_duplicate=True),
#         Output("dashboard-grid", "layouts", allow_duplicate=True),
#         Output("add-component-modal", "is_open", allow_duplicate=True),
#         Output("current-chart-store", "data", allow_duplicate=True)
#     ],
#     [Input("add-component-confirm", "n_clicks")],
#     [
#         State("current-chart-store", "data"),
#         State("dashboard-settings-store", "data"),
#         State("user-data-store", "data"),
#         State("dashboard-grid", "children"),
#         State("dashboard-grid", "layouts")
#     ],
#     prevent_initial_call=True
# )
# def add_component_to_dashboard(n_clicks, chart_data, current_settings, user_data, current_children, current_layouts):
#     # Make a deep copy to avoid modifying the input state
#     current_layouts = copy.deepcopy(current_layouts)

#     ctx = dash.callback_context
#     if not ctx.triggered or not n_clicks or not chart_data:
#         raise PreventUpdate
    
#     if not current_settings:
#         current_settings = {'components': []}
#     if not isinstance(current_settings, dict):
#         current_settings = {'components': []}
#     if 'components' not in current_settings:
#         current_settings['components'] = []

#     # Standard dimensions for all components
#     component_width = 8
#     component_height = 6

#      # Add debugging
#     # print(f"DEBUG: Adding new component with standard width={component_width}, height={component_height}")
    
#     next_position = find_next_available_position(current_settings)
#     component_id = str(uuid.uuid4())

#     # print(f"DEBUG: Component position: x={next_position['x']}, y={next_position['y']}")
    
#     new_component = {
#         'id': component_id,
#         'type': chart_data['type'],
#         'title': chart_data['title'],
#         'position': {
#             'x': next_position['x'],
#             'y': next_position['y'],
#             'w': component_width,  # Consistent width
#             'h': component_height  # Consistent height
#         },
#         'settings': chart_data.get('settings', {})
#     }

#     if chart_data['type'] == 'income_forecast' and 'months_ahead' in chart_data:
#         new_component['settings']['months_ahead'] = chart_data['months_ahead']
    
#     current_settings['components'].append(new_component)

#     # --- Add new layout consistently for all breakpoints ---
#     for breakpoint in current_layouts.keys():
#         # Set width based on breakpoint to make it responsive
#         bp_width = component_width
#         if breakpoint == 'xs':
#             bp_width = 4  # Smaller for phones
#         elif breakpoint == 'sm':
#             bp_width = 6  # Medium for tablets

#         # print(f"DEBUG: Adding layout for breakpoint '{breakpoint}': width={bp_width}, height={component_height}")
            
#         current_layouts[breakpoint].append({
#             'i': component_id,
#             'x': next_position['x'],
#             'y': next_position['y'],
#             'w': bp_width,
#             'h': component_height,
#             'minW': 4,  # Minimum width constraint
#             'minH': 4   # Minimum height constraint
#         })

#     # # print final layout after adding component
#     # print(f"DEBUG: Final layouts: {json.dumps(current_layouts)}")

#     # Generate components with the updated settings
#     components, _ = generate_dashboard_components(current_settings, user_data)

#     # Save if user is not guest
#     user_id = user_data.get('user_info', {}).get('id')
#     if user_id and user_id != 'Guest':
#         save_dashboard_settings_to_db(user_id, current_settings)

#     empty_style = {"display": "none"}
    
#     return current_settings, empty_style, components, current_layouts, False, None

# # Remove dashboard component
# @callback(
#     [
#         Output("dashboard-settings-store", "data", allow_duplicate=True),
#         Output("empty-dashboard-state", "style", allow_duplicate=True),
#         Output("dashboard-grid", "children", allow_duplicate=True),
#         Output("dashboard-grid", "layouts", allow_duplicate=True)
#     ],
#     [Input({"type": "remove-component", "index": ALL}, "n_clicks")],
#     [
#         State({"type": "remove-component", "index": ALL}, "id"),
#         State("dashboard-settings-store", "data"),
#         State("user-data-store", "data"),
#         State("dashboard-grid", "layouts")
#     ],
#     prevent_initial_call=True
# )
# def remove_dashboard_component(n_clicks_list, id_list, current_settings, user_data, current_layouts):
#     ctx = dash.callback_context
#     if not ctx.triggered or not any(n for n in n_clicks_list if n):
#         raise PreventUpdate
    
#     # Identify which component (chart) to remove based on the button click
#     button_id = ctx.triggered[0]['prop_id'].split('.')[0]
#     clicked_id = json.loads(button_id)['index']

#     # --- Remove the selected component from the settings (components) ---
#     if current_settings and 'components' in current_settings:
#         current_settings['components'] = [
#             comp for comp in current_settings['components'] if comp['id'] != clicked_id
#         ]
    
#     # --- Remove the corresponding layout item for each breakpoint ---
#     for breakpoint in current_layouts.keys():
#         current_layouts[breakpoint] = [
#             item for item in current_layouts[breakpoint] if item['i'] != clicked_id
#         ]

#     # Check if dashboard is empty
#     is_empty = not current_settings or 'components' not in current_settings or len(current_settings['components']) == 0
#     empty_style = {"display": "block"} if is_empty else {"display": "none"}

#     # --- Regenerate only components ---
#     components, _ = generate_dashboard_components(current_settings, user_data)

#     # Reset layouts if dashboard becomes empty
#     if is_empty:
#         current_layouts = {'lg': [], 'md': [], 'sm': [], 'xs': []}

#     # Save the settings to the database if not a guest user
#     if user_data.get('user_info', {}).get('user_id') != 'Guest':
#         save_dashboard_settings_to_db(user_data['user_info']['user_id'], current_settings)

#     return current_settings, empty_style, components, current_layouts


# # Fix for the generate_dashboard_components function
# def generate_dashboard_components(settings, user_data):
#     """Generate dashboard components from settings"""
#     # print(f"DEBUG: Generating dashboard components from settings: {settings}")
    
#     if not settings or 'components' not in settings:
#         # print("DEBUG: No components in settings")
#         return [], {'lg': [], 'md': [], 'sm': [], 'xs': []}
    
#     components = []
#     layouts = {'lg': [], 'md': [], 'sm': [], 'xs': []}

#     # Ensure consistent size is applied to all components
#     component_width = 8  # Standard width
#     component_height = 6  # Standard height
    
#     # print(f"DEBUG: Standard component dimensions: {component_width}x{component_height}")

#     # Get user data
#     income_data = user_data.get('income', [])
#     expense_data = user_data.get('expenses', [])
    
#     # print(f"DEBUG: Processing {len(settings['components'])} components")
    
#     for idx, component in enumerate(settings['components']):
#         component_id = component['id']
#         component_type = component.get('type', 'unknown')
#         component_title = component.get('title', 'Untitled Component')
#         component_settings = component.get('settings', {})
        
#         # Get position with standard dimensions if missing
#         position = component.get('position', {})
#         x = position.get('x', 0)
#         y = position.get('y', 0)
#         w = position.get('w', component_width)  # Use standard width if not specified
#         h = position.get('h', component_height)  # Use standard height if not specified
        
#         # print(f"DEBUG: Component {idx+1} (ID: {component_id}) - Type: {component_type}, Size: {w}x{h}")
        
#         # Create layout item for each breakpoint with responsive sizing
#         for breakpoint in layouts:
#             bp_width = w
#             if breakpoint == 'xs':
#                 bp_width = 4  # Smaller for phones
#             elif breakpoint == 'sm':
#                 bp_width = 6  # Medium for tablets
                
#             layouts[breakpoint].append({
#                 'i': component_id,
#                 'x': x,
#                 'y': y,
#                 'w': bp_width,
#                 'h': h,
#                 'minW': 4,  # Minimum width
#                 'minH': 4   # Minimum height
#             })
        
#         # Create the component content
#         component_content = []
        
#         # Define card type-specific styling
#         card_theme = get_component_theme(component_type)
        
#         # Component header with title and controls
#         component_header = html.Div([ 
#             html.Div([
#                 html.I(className=f"fas {card_theme['icon']}", style={"marginRight": "10px", "fontSize": "18px"}),
#                 html.H3(component_title, className="component-title", style={"margin": 0, "display": "inline"})
#             ], style={"display": "flex", "alignItems": "center"}),
#             html.Div([
#                 html.Button(
#                     html.I(className="fas fa-trash-alt", style={"color": card_theme['icon_color']}),
#                     id={"type": "remove-component", "index": component_id},
#                     className="component-control-btn",
#                     title="Delete",
#                     style={"background": "transparent", "border": "none"}
#                 )
#             ], className="component-controls")
#         ], className="component-header", style={
#             "display": "flex", 
#             "justifyContent": "space-between",
#             "alignItems": "center",
#             "padding": "12px 15px",
#             "borderBottom": f"1px solid {card_theme['border_color']}",
#             "background": card_theme['header_bg'],
#             "color": card_theme['header_text'],
#             "borderTopLeftRadius": "8px",
#             "borderTopRightRadius": "8px"
#         })
        
#         component_content.append(component_header)
        
#         # Component body based on type
#         body_style = {
#             "padding": "15px",
#             "background": card_theme['body_bg'],
#             "height": "calc(100% - 50px)",  # Adjust for header height
#             "overflow": "auto",
#             "borderBottomLeftRadius": "8px",
#             "borderBottomRightRadius": "8px"
#         }
        
#         if component_type == 'income_chart' or component_type == 'income_forecast':
#             months_ahead = component_settings.get('months_ahead', 6)
#             forecast_graph = dcc.Graph(
#                 id={"type": "component-graph", "index": component_id},
#                 figure=generate_income_chart(income_data, component_settings, months_ahead),
#                 config={'displayModeBar': False},
#                 className="component-graph",
#                 style={"height": "100%", "width": "100%"}
#             )
#             component_content.append(html.Div(forecast_graph, style=body_style))
            
#         elif component_type == 'expense_breakdown':
#             expense_graph = dcc.Graph(
#                 id={"type": "component-graph", "index": component_id},
#                 figure=generate_expense_breakdown(expense_data, component_settings),
#                 config={'displayModeBar': False},
#                 className="component-graph",
#                 style={"height": "100%", "width": "100%"}
#             )
#             component_content.append(html.Div(expense_graph, style=body_style))
            
#         # Handle new chart types
#         elif component_type == 'monte_carlo':
#             monte_carlo_graph = dcc.Graph(
#                 id={"type": "component-graph", "index": component_id},
#                 figure=generate_monte_carlo_simulation(income_data, component_settings),
#                 config={'displayModeBar': False},
#                 className="component-graph",
#                 style={"height": "100%", "width": "100%"}
#             )
#             component_content.append(html.Div(monte_carlo_graph, style=body_style))
            
#         elif component_type == 'income_heatmap':
#             heatmap_graph = dcc.Graph(
#                 id={"type": "component-graph", "index": component_id},
#                 figure=generate_income_heatmap(income_data, component_settings),
#                 config={'displayModeBar': False},
#                 className="component-graph",
#                 style={"height": "100%", "width": "100%"}
#             )
#             component_content.append(html.Div(heatmap_graph, style=body_style))
            
#         elif component_type == 'income_seasonality':
#             seasonality_graph = dcc.Graph(
#                 id={"type": "component-graph", "index": component_id},
#                 figure=generate_income_seasonality(income_data, component_settings),
#                 config={'displayModeBar': False},
#                 className="component-graph",
#                 style={"height": "100%", "width": "100%"}
#             )
#             component_content.append(html.Div(seasonality_graph, style=body_style))
            
#         elif component_type == 'income_growth':
#             growth_graph = dcc.Graph(
#                 id={"type": "component-graph", "index": component_id},
#                 figure=generate_income_growth_chart(income_data, component_settings),
#                 config={'displayModeBar': False},
#                 className="component-graph",
#                 style={"height": "100%", "width": "100%"}
#             )
#             component_content.append(html.Div(growth_graph, style=body_style))
            
#         # Add more component types as needed
#         else:
#             # Generic placeholder for unknown component types
#             component_content.append(html.Div(
#                 f"Unknown component type: {component_type}",
#                 className="component-error",
#                 style=body_style
#             ))
        
#         # Create the component container with enhanced styling
#         component_div = html.Div(
#             component_content,
#             id={"type": "dashboard-component", "index": component_id},
#             className="dashboard-component",
#             style={
#                 "width": "100%", 
#                 "height": "100%", 
#                 "minHeight": "300px",
#                 "minWidth": "200px",
#                 "overflow": "hidden",     # Hide overflow
#                 "borderRadius": "8px",    # Rounded corners
#                 "boxShadow": "0 4px 20px rgba(0, 0, 0, 0.15)",  # Subtle shadow
#                 "border": f"1px solid {card_theme['border_color']}",
#                 "position": "relative"    # For absolute positioning of drag handles
#             }
#         )
        
#         components.append(component_div)
    
#     return components, layouts

# def get_component_theme(component_type):
#     """Returns theme colors based on component type - all with blue gradients and dark blue borders"""
    
#     # Common settings for all components
#     common_theme = {
#         'header_bg': 'linear-gradient(135deg, #0082c8 0%, #0082c8 100%)',  # Deep blue gradient
#         'header_text': '#ffffff',  # White text
#         'body_bg': '#ffffff',      # White background
#         'border_color': '#0a2463', # Darker blue border
#         'icon_color': '#ffffff'    # White icons
#     }
    
#     # Component-specific icons
#     icons = {
#         'income_chart': 'fa-chart-line',
#         'income_forecast': 'fa-chart-area',
#         'expense_breakdown': 'fa-chart-pie',
#         'default': 'fa-th-large'
#     }
    
#     # Get the theme and add the appropriate icon
#     theme = common_theme.copy()
#     theme['icon'] = icons.get(component_type, icons['default'])
    
#     return theme


# # Add a ClientsideFunction and callback to handle position updates

# # Add an interval component to the layout
# layout.children.append(dcc.Interval(id='layout-update-interval', interval=1000, n_intervals=0))
# layout.children.append(dcc.Store(id='dashboard-position-store', storage_type='memory'))

# @callback(
#     [
#         Output("add-component-modal", "is_open", allow_duplicate=True),
#         Output("current-chart-store", "data", allow_duplicate=True)
#     ],
#     [Input("add-component-cancel", "n_clicks")],
#     prevent_initial_call=True
# )
# def cancel_modal(cancel_clicks):
#     """Close the modal when cancel is clicked"""
#     ctx = dash.callback_context
#     if not ctx.triggered:
#         raise PreventUpdate
    
#     # Close the modal and clear the chart store when cancel is clicked
#     return False, None

# @callback(
#     Output("chat-input", "value"),
#     [Input("send-chat", "n_clicks"),
#      Input("chat-input", "n_submit")],
#     [State("chat-input", "value")],
#     prevent_initial_call=True
# )
# def clear_input(n_clicks, n_submit, current_value):
#     """Clear the input field after sending a message"""
#     if (n_clicks or n_submit) and current_value:
#         return ""
#     raise PreventUpdate

# # Add a callback for clicking the "Add to Dashboard" button directly in the chat
# @callback(
#     [Output("chat-input", "value", allow_duplicate=True)],
#     [Input({"type": "add-to-dashboard-button", "index": ALL}, "n_clicks")],
#     prevent_initial_call=True
# )
# def handle_add_dashboard_button_click(n_clicks_list):
#     """Handle the Add to Dashboard button click in the chat"""
#     if not any(n_clicks_list):
#         raise PreventUpdate
    
#     # Just to prevent update errors, doesn't change anything
#     return [""]

# # Add a simple callback to check if dashboard grid updates are working
# @callback(
#     Output("last-updated", "children"),
#     Input("dashboard-settings-store", "data")
# )
# def update_last_updated(settings):
#     """Update the last updated timestamp when settings change"""
#     if settings and 'components' in settings:
#         component_count = len(settings['components'])
#         return f"Last updated: {datetime.now().strftime('%H:%M:%S')} - Components: {component_count}"
#     return "No components"

# # Load user data when page loads or user ID changes
# @callback(
#     Output("user-data-store", "data"),
#     [Input("user-id-store", "data"),
#      Input("url", "pathname")],
#     prevent_initial_call=False  # Run on initial load
# )
# def load_user_data(user_id, pathname):
#     """Load user data from the database based on user ID"""
#     # print(f"Loading user data, ID: {user_id}, Path: {pathname}")
    
#     if user_id is None:
#         # Default to Guest if no user ID is found
#         return get_user_data('Guest')
    
#     # Get user data from database
#     user_data = get_user_data(user_id)
#     # print(f"Loaded data for user ID: {user_id}")
    
#     return user_data

# # Update user display in header
# @callback(
#     Output("user-email-display", "children"),
#     Input("user-data-store", "data"),
#     prevent_initial_call=False  # Run on initial load
# )
# def update_user_display(user_data):
#     """Update user display based on user data"""
#     if user_data and 'user_info' in user_data:
#         if 'email' in user_data['user_info']:
#             return user_data['user_info']['email']
#         elif 'name' in user_data['user_info']:
#             return user_data['user_info']['name']
#     return "Guest User"

# # Toggle dropdown visibility
# @callback(
#     Output("user-dropdown-content", "className", allow_duplicate=True),
#     [Input("user-dropdown-button", "n_clicks")],
#     [State("user-dropdown-content", "className")],
#     prevent_initial_call=True
# )
# def toggle_dropdown(n_clicks, current_class):
#     """Toggle user dropdown menu visibility"""
#     if n_clicks:
#         if "show" in current_class:
#             return "user-dropdown-content"
#         else:
#             return "user-dropdown-content show"
#     return current_class

# # Logout functionality
# clientside_callback(
#     """
#     function(n_clicks) {
#         if (n_clicks) {
#             // Clear all relevant stores
#             localStorage.removeItem("user-id-store");
#             sessionStorage.removeItem("user-data-store");
#             localStorage.removeItem("session-data-store");
#             localStorage.removeItem("dashboard-settings-store");
#             // Redirect to home
#             return '/';
#         }
#         return dash_clientside.no_update;
#     }
#     """,
#     Output("url", "pathname"),
#     Input("logout-link", "n_clicks"),
#     prevent_initial_call=True
# )
# # Add this to your existing clientside callbacks
# clientside_callback(
#     """
#     function(n) {
#         // This function runs periodically to ensure data persistence in local storage
#         const dashboardSettings = localStorage.getItem('dash_store:dashboard-settings-store');
#         // Simply returning n ensures the callback runs but doesn't change anything
#         return n;
#     }
#     """,
#     Output("layout-update-interval", "n_intervals", allow_duplicate=True),
#     Input("layout-update-interval", "n_intervals"),
#     prevent_initial_call=True
# )
# # Use a single clientside callback that does both jobs
# clientside_callback(
#     """
#     function(n_intervals) {
#         // If this is the first run, set up the event listener
#         if (!window.dashboardListenerInitialized) {
#             console.log("Setting up dashboard layout change listener");
            
#             document.addEventListener('dashboardLayoutChanged', function(e) {
#                 // Store the data in a dash store directly
#                 const store = document.getElementById('dashboard-position-store');
#                 if (store) {
#                     store._dashprivate_setValue(e.detail);
                    
#                     // Also trigger an event that Dash can listen for
#                     const triggerElement = document.getElementById('dashboard-event-trigger');
#                     if (triggerElement) {
#                         triggerElement.setAttribute('data-update', Date.now());
#                     }
#                 }
#             });
            
#             window.dashboardListenerInitialized = true;
#         }
        
#         return dash_clientside.no_update;
#     }
#     """,
#     Output('dashboard-event-trigger', 'data-update'),
#     Input('layout-update-interval', 'n_intervals'),
#     prevent_initial_call=True
# )

# # Check authentication (optional)
# @callback(
#     Output("chat-dashboard-container", "style"),
#     [Input("user-data-store", "data"),
#      Input("url", "pathname")],
# )
# def check_authentication(user_data, pathname):
#     """Check if user is authenticated and should access this page"""
#     if pathname == '/chat':
#         # Check if user is authenticated or if guest access is allowed
#         if not user_data:
#             # Hide the container if no user data
#             return {"display": "none"}
        
#         # If you want to restrict certain pages to logged-in users only
#         # Uncomment this if you want to restrict guest access
#         if user_data.get('user_info', {}).get('id') == 'Guest':
#             return {"display": "none"}
    
#     return {"display": "block"}

# @callback(
#     [
#         Output("income-page-modal", "is_open"),
#         Output("income-page-iframe", "src")
#     ],
#     [
#         Input("close-income-modal", "n_clicks"),
#         Input("chat-input", "n_submit"),
#         Input("send-chat", "n_clicks")
#     ],
#     [
#         State("chat-input", "value"),
#         State("income-page-modal", "is_open")
#     ],
#     prevent_initial_call=True
# )
# def manage_income_modal(close_clicks, n_submit, send_clicks, input_value, is_open):
#     """Open or close the income page modal"""
#     ctx = dash.callback_context
#     trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
#     # Close modal when close button is clicked
#     if trigger_id == "close-income-modal":
#         return False, dash.no_update
    
#     # Check if we should open the modal based on user input
#     if (trigger_id in ["chat-input", "send-chat"]) and input_value:
#         input_lower = input_value.lower()
#         if any(phrase in input_lower for phrase in [
#                 "add to my income", 
#                 "manage income",
#                 "interested in my income breakdown", 
#                 "view income page",
#                 "edit my income"
#             ]):
#             return True, "/income"
    
#     # Default - no changes
#     return dash.no_update, dash.no_update

# # @callback(
# #     [
# #         Output("income-insights-modal", "is_open"),
# #         Output("income-insights-content", "children"),
# #         Output("insights-charts-store", "data")
# #     ],
# #     [
# #         Input("close-insights-modal", "n_clicks"),
# #         Input("chat-input", "n_submit"),
# #         Input("send-chat", "n_clicks")
# #     ],
# #     [
# #         State("chat-input", "value"),
# #         State("income-insights-modal", "is_open"),
# #         State("user-data-store", "data")
# #     ],
# #     prevent_initial_call=True
# # )
# # def manage_income_insights_modal(close_clicks, n_submit, send_clicks, input_value, is_open, user_data):
# #     """Open or close the income insights modal and populate it with charts"""
# #     ctx = callback_context
# #     trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
# #     # Close modal when close button is clicked
# #     if trigger_id == "close-insights-modal":
# #         return False, dash.no_update, dash.no_update
    
# #     # Check if we should open the modal based on user input
# #     if (trigger_id in ["chat-input", "send-chat"]) and input_value:
# #         input_lower = input_value.lower()
# #         if any(pattern in input_lower for pattern in [
# #             "what's my income", 
# #             "what is my income",
# #             "show me my income",
# #             "how much do i earn",
# #             "income breakdown",
# #             "income overview",
# #             "tell me about my income"
# #         ]):
# #             # Get income data
# #             income_data = user_data.get('income', [])
            
# #             # Create multiple charts for different income insights
# #             charts_data = []
# #             modal_content = []
            
# #             # 1. Income Overview
# #             fig_overview = generate_income_chart(income_data)
# #             chart_id = str(uuid.uuid4())
# #             charts_data.append({
# #                 'id': chart_id,
# #                 'type': 'income_chart',
# #                 'title': 'Monthly Income',
# #                 'settings': {'chart_type': 'bar'}
# #             })
            
# #             modal_content.append(html.Div([
# #                 html.Div([
# #                     html.H3("Monthly Income Overview"),
# #                     html.Button(
# #                         "Add to Dashboard", 
# #                         id={'type': 'add-insight-chart', 'index': chart_id},
# #                         className="add-chart-btn"
# #                     )
# #                 ], className="insight-chart-header"),
# #                 dcc.Graph(figure=fig_overview, config={'displayModeBar': False})
# #             ], className="insight-chart-container"))
            
# #             # 2. Short-term Forecast (6 months)
# #             fig_forecast = generate_income_chart(income_data, None, 6)
# #             chart_id = str(uuid.uuid4())
# #             charts_data.append({
# #                 'id': chart_id,
# #                 'type': 'income_forecast',
# #                 'title': 'Income Forecast (6 months)',
# #                 'months_ahead': 6,
# #                 'settings': {'show_trend': True}
# #             })
            
# #             modal_content.append(html.Div([
# #                 html.Div([
# #                     html.H3("6-Month Income Forecast"),
# #                     html.Button(
# #                         "Add to Dashboard", 
# #                         id={'type': 'add-insight-chart', 'index': chart_id},
# #                         className="add-chart-btn"
# #                     )
# #                 ], className="insight-chart-header"),
# #                 dcc.Graph(figure=fig_forecast, config={'displayModeBar': False})
# #             ], className="insight-chart-container"))
            
# #             # 3. Long-term Forecast (12 months)
# #             fig_forecast_long = generate_income_chart(income_data, None, 12)
# #             chart_id = str(uuid.uuid4())
# #             charts_data.append({
# #                 'id': chart_id,
# #                 'type': 'income_forecast',
# #                 'title': 'Income Forecast (12 months)',
# #                 'months_ahead': 12,
# #                 'settings': {'show_trend': True}
# #             })
            
# #             modal_content.append(html.Div([
# #                 html.Div([
# #                     html.H3("12-Month Income Forecast"),
# #                     html.Button(
# #                         "Add to Dashboard", 
# #                         id={'type': 'add-insight-chart', 'index': chart_id},
# #                         className="add-chart-btn"
# #                     )
# #                 ], className="insight-chart-header"),
# #                 dcc.Graph(figure=fig_forecast_long, config={'displayModeBar': False})
# #             ], className="insight-chart-container"))
            
# #             # 4. Add more insights as needed
# #             # e.g., Income by source, Income growth rate, etc.
            
# #             # Wrap all content in a container
# #             final_content = html.Div([
# #                 html.H2("Income Analysis", className="insights-title"),
# #                 html.P("Here's a comprehensive analysis of your income. You can add any chart to your dashboard.", 
# #                        className="insights-description"),
# #                 html.Div(modal_content, className="insights-charts-grid")
# #             ])
            
# #             return True, final_content, charts_data
    
#     # Default - no changes
#     return dash.no_update, dash.no_update, dash.no_update

# @callback(
#     [
#         Output("dashboard-settings-store", "data", allow_duplicate=True),
#         Output("empty-dashboard-state", "style", allow_duplicate=True),
#         Output("dashboard-grid", "children", allow_duplicate=True),
#         Output("dashboard-grid", "layouts", allow_duplicate=True)
#     ],
#     [Input({"type": "add-insight-chart", "index": ALL}, "n_clicks")],
#     [
#         State({"type": "add-insight-chart", "index": ALL}, "id"),
#         State("insights-charts-store", "data"),
#         State("dashboard-settings-store", "data"),
#         State("user-data-store", "data"),
#         State("dashboard-grid", "layouts")
#     ],
#     prevent_initial_call=True
# )
# def add_insight_chart_to_dashboard(n_clicks_list, id_list, charts_data, current_settings, user_data, current_layouts):
#     """Add a specific chart from insights modal to the dashboard."""
#     # Make a deep copy to avoid modifying the input state
#     current_layouts = copy.deepcopy(current_layouts)

#     ctx = dash.callback_context
#     if not ctx.triggered or not any(n for n in n_clicks_list if n):
#         raise PreventUpdate
    
#     # Find which button was clicked
#     button_id = ctx.triggered[0]['prop_id'].split('.')[0]
#     chart_id = json.loads(button_id)['index']
    
#     # Find the selected chart data
#     selected_chart = next((chart for chart in charts_data if chart['id'] == chart_id), None)
#     if not selected_chart:
#         raise PreventUpdate
    
#     # Initialize or fix settings if needed
#     if not current_settings:
#         current_settings = {'components': []}
#     if not isinstance(current_settings, dict):
#         current_settings = {'components': []}
#     if 'components' not in current_settings:
#         current_settings['components'] = []
    
#     # Find next available position
#     next_position = find_next_available_position(current_settings)
    
#     # Standard component dimensions
#     component_width = 8
#     component_height = 6
    
#     # Create new component
#     new_component_id = str(uuid.uuid4())
#     new_component = {
#         'id': new_component_id,
#         'type': selected_chart['type'],
#         'title': selected_chart['title'],
#         'position': {
#             'x': next_position['x'],
#             'y': next_position['y'],
#             'w': component_width,
#             'h': component_height
#         },
#         'settings': selected_chart.get('settings', {})
#     }
    
#     # Add special settings for income forecast
#     if selected_chart['type'] == 'income_forecast' and 'months_ahead' in selected_chart:
#         new_component['settings']['months_ahead'] = selected_chart['months_ahead']
    
#     # Add to settings
#     current_settings['components'].append(new_component)

#     # --- Add the new layout consistently for all breakpoints ---
#     for breakpoint in current_layouts.keys():
#         # Set width based on breakpoint to make it responsive
#         bp_width = component_width
#         if breakpoint == 'xs':
#             bp_width = 4  # Smaller for phones
#         elif breakpoint == 'sm':
#             bp_width = 6  # Medium for tablets
            
#         current_layouts[breakpoint].append({
#             'i': new_component_id,
#             'x': next_position['x'],
#             'y': next_position['y'],
#             'w': bp_width,
#             'h': component_height,
#             'minW': 4,  # Minimum width constraint
#             'minH': 4   # Minimum height constraint
#         })

#     # Generate components
#     components, _ = generate_dashboard_components(current_settings, user_data)
    
#     # Save to database if not guest user
#     user_id = user_data.get('user_info', {}).get('id')
#     if user_id and user_id != 'Guest':
#         save_dashboard_settings_to_db(user_id, current_settings)
    
#     # Hide empty state
#     empty_style = {"display": "none"}
    
#     return current_settings, empty_style, components, current_layouts


# def find_next_available_position(current_settings):
#     """Find the next available grid position for a new component"""
#     # Default grid dimensions - make these consistent!
#     grid_width = 12  # Total width of grid (number of columns)
#     component_width = 8  # Default component width - ALWAYS use this
#     component_height = 6  # Default component height - ALWAYS use this
    
#     # If no components exist yet, start at top left
#     if not current_settings or 'components' not in current_settings or not current_settings['components']:
#         return {'x': 0, 'y': 0, 'w': component_width, 'h': component_height}
    
#     # Create a grid representation to track occupied cells
#     # First, determine how tall our grid needs to be based on existing components
#     max_row = 0
#     for comp in current_settings['components']:
#         pos = comp.get('position', {})
#         y = pos.get('y', 0)
#         h = pos.get('h', component_height)  # Use default if not specified
#         max_row = max(max_row, y + h)
    
#     # Initialize grid as all empty (None)
#     grid = [[None for _ in range(grid_width)] for _ in range(max_row + component_height + 1)]
    
#     # Mark occupied cells - IMPORTANT: Use FIXED sizes here!
#     for comp in current_settings['components']:
#         pos = comp.get('position', {})
#         x = max(0, pos.get('x', 0))
#         y = max(0, pos.get('y', 0))
#         w = component_width  # Always use the standard width
#         h = component_height  # Always use the standard height
        
#         # Mark each cell covered by this component
#         for row in range(y, min(y + h, len(grid))):
#             for col in range(x, min(x + w, grid_width)):
#                 if row < len(grid) and col < grid_width:
#                     grid[row][col] = comp['id']
    
#     # Find next available position using standard component size
#     for row in range(len(grid) - component_height + 1):
#         for col in range(grid_width - component_width + 1):
#             # Check if all cells for this position are free
#             position_available = True
#             for r in range(row, row + component_height):
#                 for c in range(col, col + component_width):
#                     if r < len(grid) and c < grid_width and grid[r][c] is not None:
#                         position_available = False
#                         break
#                 if not position_available:
#                     break
            
#             if position_available:
#                 return {'x': col, 'y': row, 'w': component_width, 'h': component_height}
    
#     # If no space found, put it in a new row at the bottom
#     return {'x': 0, 'y': max_row, 'w': component_width, 'h': component_height}


# @callback(
#     Output('dashboard-settings-store', 'data', allow_duplicate=True),
#     Input('dashboard-grid', 'layouts'),
#     [State('dashboard-settings-store', 'data'),
#      State('user-data-store', 'data')],
#     prevent_initial_call=True
# )
# def save_layout_changes(layouts, current_settings, user_data):
#     """Save layout changes from dash_draggable to dashboard settings"""
#     if not layouts or not current_settings:
#         raise PreventUpdate
    
#     # Add this debugging
#     # print("DEBUG: Layout change detected")
#     # print(f"DEBUG: Current layouts: {json.dumps(layouts)}")
    
#     # Initialize components if missing
#     if 'components' not in current_settings:
#         current_settings = {'components': []}
    
#     # Extract the current layout (usually the 'lg' or default layout)
#     current_layout = layouts.get('lg', [])
#     if not current_layout:
#         # Try other breakpoints if 'lg' is not available
#         for breakpoint in ['md', 'sm', 'xs', 'xxs']:
#             if breakpoint in layouts and layouts[breakpoint]:
#                 current_layout = layouts[breakpoint]
#                 break
    
#     if not current_layout:
#         raise PreventUpdate
    
#     # Make sure we're not working with a reference to avoid modifying the input state
#     current_settings = copy.deepcopy(current_settings)
    
#     # Update the positions of all components in settings
#     for layout_item in current_layout:
#         item_id = layout_item.get('i')
#         if not item_id:
#             continue
            
#         # Extract position data
#         position = {
#             'x': layout_item.get('x', 0),
#             'y': layout_item.get('y', 0),
#             'w': layout_item.get('w', 8),  # Force standard width here
#             'h': layout_item.get('h', 6)   # Force standard height here
#         }
        
#         # print(f"DEBUG: Updating component {item_id} position to {position}")
        
#         # Update the component position in settings
#         component_found = False
#         for component in current_settings['components']:
#             if component['id'] == item_id:
#                 component['position'] = position
#                 component_found = True
#                 break
                
#         # If component wasn't found in settings but exists in layout, add it
#         if not component_found:
#             print(f"Component {item_id} found in layout but not in settings")
    
#     # Save to database if not guest user
#     current_settings['layouts'] = layouts
#     user_id = user_data.get('user_info', {}).get('user_id')
#     if user_id and user_id != 'Guest':
#         save_dashboard_settings_to_db(user_id, current_settings)
#         # print(f"Saved dashboard settings after layout change for user {user_id}")
    
#     return current_settings

# def save_dashboard_settings_to_db(user_id, settings):
#     """Save dashboard settings to database"""
#     conn = get_db_connection()
#     if not conn:
#         return False
    
#     try:
#         with conn.cursor() as cur:
#             cur.execute(
#                 "UPDATE users SET dashboard_settings = %s WHERE user_id = %s",
#                 (json.dumps(settings), user_id)
#             )
#             conn.commit()
#         return True
#     except Exception as e:
#         # print(f"Error saving dashboard settings: {e}")
#         return False
#     finally:
#         conn.close()

# @callback(
#     [Output("dashboard-grid", "children"),
#      Output("dashboard-grid", "layouts"),
#      Output("empty-dashboard-state", "style")],
#     [Input("user-data-store", "data")],
#     [State("dashboard-settings-store", "data")],
#     prevent_initial_call=True
# )
# def initialize_dashboard(user_data, current_settings):
#     """Initialize dashboard with current live settings"""
#     if not user_data:
#         return [], {'lg': [], 'md': [], 'sm': [], 'xs': []}, {"display": "block"}

#     # Only hide empty state if we have components
#     components, generated_layouts = generate_dashboard_components(current_settings, user_data)
    
#     # Show empty state when no components exist
#     # Be explicit about checking if components exist
#     has_components = (
#         current_settings and 
#         'components' in current_settings and 
#         current_settings['components'] and  # Check if list is not empty
#         len(current_settings['components']) > 0
#     )
#     empty_style = {"display": "block" if not has_components else "none"}

#     # print(f"DEBUG: Has components: {has_components}, showing empty state: {empty_style['display'] == 'block'}")

#     # Use layouts from current_settings if available, otherwise use generated ones
#     layouts = current_settings.get('layouts', generated_layouts) if current_settings else generated_layouts
    
#     # Ensure layouts is properly initialized for all breakpoints
#     if not layouts or not isinstance(layouts, dict):
#         layouts = {'lg': [], 'md': [], 'sm': [], 'xs': []}
    
#     # Make sure all required breakpoints exist
#     for breakpoint in ['lg', 'md', 'sm', 'xs']:
#         if breakpoint not in layouts:
#             layouts[breakpoint] = []

#     return components, layouts, empty_style

# # want to change the background color of cards/components. I also want to make it so when the cards/components are generated, they at least get
# # generated with a decent size and not so small. Also the first component gets generated with a good size but the ones after are small?
# # Also in page initilization even thought i have 0 components, im not getting the empty page

# # Add this as a new callback that runs whenever the dashboard layout changes
# @callback(
#     Output("debug-output", "children"),  # Add this hidden div to your layout
#     [Input("dashboard-grid", "layouts")],
#     prevent_initial_call=True
# )
# def inspect_dashboard_layout(layouts):
#     """Debug function to inspect layouts"""
#     if not layouts:
#         return "No layouts"
    
#     debug_output = []
    
#     for breakpoint, items in layouts.items():
#         debug_output.append(f"Breakpoint: {breakpoint}")
#         for item in items:
#             debug_output.append(f"  Item {item.get('i')}: x={item.get('x')}, y={item.get('y')}, w={item.get('w')}, h={item.get('h')}")
    
#     # print("DEBUG LAYOUT:", "\n".join(debug_output))
#     return "\n".join(debug_output)

# # Add this div to your layout
# layout.children.append(html.Div(id="debug-output", style={"display": "none"}))
