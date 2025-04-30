import dash
from dash import html, dcc, callback, Input, Output, State, register_page, ALL, MATCH, clientside_callback, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json
import uuid
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
from utils.db import connect_db
import random
import dash_draggable
import copy
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Register this file as the chat page
register_page(__name__, path='/chat', name='Chat')

# COLORS dictionary for consistent styling
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

# Chart COLORS_CHART and styling constants
COLORS_CHART = {
    'primary': '#1E40AF',      # Deep blue
    'secondary': '#3B82F6',    # Mid blue
    'accent': '#60A5FA',       # Bright blue
    'highlight': '#93C5FD',    # Light blue
    'background': '#F0F7FF',   # Very light blue
    'text': '#1E293B',         # Slate for text
    'chart_palette': ['#1E40AF', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#2563EB', '#1D4ED8', '#DBEAFE']
}

# Database connection function
def get_db_connection():
    """Connect to the PostgreSQL database"""
    try:
        conn = connect_db()
        return conn
    except Exception as e:
        # # print(f"Error connecting to database: {e}")
        return None

def get_user_data(user_id):
    """Get user data from database or return default for guest users"""
    # Handle guest or invalid user IDs gracefully
    if not user_id or user_id == 'Guest':
        return {
            'user_info': {'id': 'Guest', 'name': 'Guest User'},
            'income': generate_demo_income_data(),
            'expenses': generate_demo_expense_data(),
            'savings_goals': [],
            'transactions': [],
            'dashboard_settings': {  # Return as object, not JSON string
                'components': [
                    {
                        'id': str(uuid.uuid4()),
                        'type': 'income_chart',
                        'title': 'Monthly Income',
                        'position': {'x': 0, 'y': 0, 'w': 8, 'h': 6},
                        'settings': {'chart_type': 'bar', 'color': COLORS['accent']}
                    },
                    {
                        'id': str(uuid.uuid4()),
                        'type': 'expense_breakdown',
                        'title': 'Expense Breakdown',
                        'position': {'x': 6, 'y': 0, 'w': 8, 'h': 6},
                        'settings': {'chart_type': 'pie', 'color': COLORS['primary']}
                    }
                ]
            }
        }

    conn = get_db_connection()
    if not conn:
        return {}

    user_data = {}
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get user info
            cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()
            if not user:
                print(f"User {user_id} not found in database")
                return {}

            user_data['user_info'] = dict(user)

            # Get income data
            cur.execute("SELECT * FROM income WHERE user_id = %s", (user_id,))
            user_data['income'] = [dict(row) for row in cur.fetchall()]

            # Get expense data
            cur.execute("SELECT * FROM expense WHERE user_id = %s", (user_id,))
            user_data['expenses'] = [dict(row) for row in cur.fetchall()]

            # Get savings goals
            cur.execute("SELECT * FROM saving_goals WHERE user_id = %s", (user_id,))
            user_data['savings_goals'] = [dict(row) for row in cur.fetchall()]

            # Get transactions
            cur.execute(
                "SELECT * FROM transactions WHERE user_id = %s ORDER BY date DESC LIMIT 50",
                (user_id,)
            )
            user_data['transactions'] = [dict(row) for row in cur.fetchall()]

            # Get dashboard settings
            cur.execute("SELECT dashboard_settings FROM users WHERE user_id = %s", (user_id,))
            dashboard_settings = cur.fetchone()

    except Exception as e:
         print(f"Error fetching user data: {e}")
    finally:
        conn.close()

    return user_data

# Generate demo data for development and guest users
def generate_demo_income_data():
    """Generate demo income data for testing"""
    today = datetime.now()
    data = []
    
    for i in range(12):
        month_date = today - timedelta(days=30 * i)
        # Base amount with some randomness
        base = 3500
        variation = base * 0.1  # 10% variation
        
        data.append({
            'id': i,
            'user_id': 'Guest',
            'source': 'Primary Income',
            'amount': base + ((variation * 2) * (0.5 - random.random())),
            'date': month_date,
            'monthly_amount': base + ((variation * 2) * (0.5 - random.random())),
            'recurring': True
        })
    
    return data

def generate_demo_expense_data():
    """Generate demo expense data for testing"""
    categories = ['Housing', 'Food', 'Transportation', 'Entertainment', 'Utilities']
    amounts = [1200, 500, 300, 200, 250]
    
    data = []
    for i, (category, amount) in enumerate(zip(categories, amounts)):
        data.append({
            'id': i,
            'user_id': 'Guest',
            'category': category,
            'description': f'{category} expenses',
            'amount': amount,
            'date': datetime.now() - timedelta(days=i * 2)
        })
    
    return data

# Add these new functions for multiple income charts

def generate_income_breakdown_pie(income_data, settings=None):
    import plotly.graph_objects as go
    import pandas as pd
    import plotly.io as pio
    from plotly.subplots import make_subplots

    # Set base template
    pio.templates.default = "plotly_white"

    if not income_data:
        fig = go.Figure()
        fig.add_annotation(
            text="No income data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20, color="#1e3d58", family="Helvetica Neue, Arial, sans-serif")
        )
        return fig

    df = pd.DataFrame(income_data)
    source_data = df.groupby('source')['amount'].sum().reset_index()
    source_data = source_data.sort_values('amount', ascending=False)
    labels = source_data['source']
    values = source_data['amount']
    total_value = values.sum()

    # Refined gradient-inspired blue palette
    blue_palette = [
        "#e0f2ff", "#b3d8f5", "#85bdf0", "#5088c5", "#3d5a80", "#274472"
    ][:len(labels)]

    # Donut chart
    fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
    fig.add_trace(go.Pie(
        labels=labels,
        values=values,
        hole=0.65,
        textinfo='label+percent',
        textposition='outside',
        hoverinfo='label+percent+value',
        hovertemplate='<b>%{label}</b><br>Amount: £%{value:,.2f}<br>Share: %{percent}<extra></extra>',
        marker=dict(
            colors=blue_palette,
            line=dict(color='white', width=2)
        ),
        sort=False,
        direction='clockwise',
        pull=[0.02 if i == 0 else 0 for i in range(len(labels))],
    ))

    # Main layout
    fig.update_layout(
        annotations=[
            dict(
                text=f"<b>£{total_value:,.0f}</b><br><span style='font-size:13px;'>Total Income</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(
                    family="Helvetica Neue, Arial, sans-serif",
                    size=22,
                    color="#274472"
                )
            )
        ],
        legend=dict(
            orientation="h",
            yanchor="bottom", y=-0.2,
            xanchor="center", x=0.5,
            font=dict(family="Helvetica Neue, Arial", size=12, color="#274472")
        ),
        margin=dict(t=60, b=80, l=40, r=40),
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white',
        font=dict(family="Helvetica Neue, Arial, sans-serif", color="#274472"),
        showlegend=True
    )

    # Subtle radial shadow layer
    fig.add_shape(
        type="circle",
        xref="paper", yref="paper",
        x0=0.22, y0=0.22, x1=0.78, y1=0.78,
        fillcolor="rgba(200, 200, 200, 0.05)",
        layer="below", line_width=0
    )

    # Text polish
    fig.update_traces(textfont=dict(family="Helvetica Neue, Arial", size=14, color="#274472"))

    return fig

def generate_monte_carlo_simulation(income_data, settings=None, simulations=100):
    """Generate Monte Carlo simulation for income projections"""
    import plotly.graph_objects as go
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Either use data or create sample data
    if income_data and len(income_data) > 2:
        df = pd.DataFrame(income_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        if 'monthly_amount' in df.columns:
            df['value'] = df['monthly_amount']
        else:
            df['value'] = df['amount']
            
        # Calculate statistics
        avg_growth = df['value'].pct_change().mean()
        std_dev = df['value'].pct_change().std()
        last_value = df['value'].iloc[-1]
    else:
        # Sample data
        avg_growth = 0.01  # 1% average monthly growth
        std_dev = 0.03     # 3% standard deviation
        last_value = 5000  # Starting income
    
    # Project forward 24 months
    months = 24
    simulations = min(simulations, 200)  # Cap at 200 simulations for performance
    
    # Create dates for projection
    last_date = datetime.now()
    dates = [last_date + timedelta(days=30*i) for i in range(months)]
    
    # Run Monte Carlo simulations
    all_simulations = []
    for sim in range(simulations):
        values = [last_value]
        for i in range(1, months):
            # Random growth with normal distribution
            growth = np.random.normal(avg_growth, std_dev)
            next_value = values[-1] * (1 + growth)
            values.append(next_value)
        all_simulations.append(values)
    
    # Calculate median values
    median_values = np.median(all_simulations, axis=0)
    
    # Create the figure
    fig = go.Figure()
    
    # Add individual simulations
    for i, sim_values in enumerate(all_simulations):
        if i == 0:
            fig.add_trace(go.Scatter(
                x=dates, 
                y=sim_values,
                line=dict(color='rgba(0, 130, 200, 0.1)', width=1),
                name='Simulation',
                hoverinfo='none',
                showlegend=False
            ))
        else:
            fig.add_trace(go.Scatter(
                x=dates, 
                y=sim_values,
                line=dict(color='rgba(0, 130, 200, 0.1)', width=1),
                name='Simulation',
                hoverinfo='none',
                showlegend=False
            ))
    
    # Add median line
    fig.add_trace(go.Scatter(
        x=dates,
        y=median_values,
        line=dict(color='#0082c8', width=3),
        name='Median Forecast',
        hovertemplate='<b>%{x|%b %Y}</b><br>£%{y:,.2f}<extra></extra>'
    ))
    
    # Style the chart
    fig.update_layout(
        # title={
        #     'text': 'Income Monte Carlo Simulation (24 Months)',
        #     'y':0.95,
        #     'x':0.5,
        #     'xanchor': 'center',
        #     'yanchor': 'top',
        #     'font': dict(family="Inter, Arial, sans-serif", size=18, color=COLORS_CHART['text'])
        # },
        xaxis=dict(
            title="Date",
            tickformat='%b %Y'
        ),
        yaxis=dict(
            title="Monthly Income (£)",
            tickprefix='£',
            tickformat=',.0f'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=80, b=40),
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0)'
    )
    
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(226, 232, 240, 0.8)'
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(226, 232, 240, 0.8)'
    )
    
    return fig

def generate_income_heatmap(income_data, settings=None):
    """Generate a heatmap showing income patterns by month and year"""
    import plotly.graph_objects as go
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Create sample data if no data available
    if not income_data or len(income_data) < 12:
        # Generate 24 months of sample data
        today = datetime.now()
        dates = []
        values = []
        
        for i in range(-12, 12):
            month_date = today + timedelta(days=30*i)
            dates.append(month_date)
            
            # Random variations with seasonal pattern
            month_num = month_date.month
            seasonal_factor = 1.0 + 0.2 * np.sin((month_num - 1) * np.pi / 6)  # Peak in July
            base_value = 5000
            variation = np.random.normal(0, 500)
            values.append(base_value * seasonal_factor + variation)
            
        df = pd.DataFrame({
            'date': dates,
            'value': values
        })
    else:
        df = pd.DataFrame(income_data)
        df['date'] = pd.to_datetime(df['date'])
        
        if 'monthly_amount' in df.columns:
            df['value'] = df['monthly_amount']
        else:
            df['value'] = df['amount']
    
    # Extract year and month
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['month_name'] = df['date'].dt.strftime('%b')
    
    # Pivot data for heatmap
    pivot_df = df.pivot_table(index='month', columns='year', values='value', aggfunc='mean')
    
    # Get month names in correct order
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=month_names,
        colorscale='Blues',
        colorbar=dict(
            title='Income (£)',
            tickprefix='£',
            tickformat=',.0f'
        ),
        hovertemplate='<b>%{y} %{x}</b><br>£%{z:,.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        # title={
        #     'text': 'Monthly Income Patterns by Year',
        #     'y':0.95,
        #     'x':0.5,
        #     'xanchor': 'center',
        #     'yanchor': 'top', 
        #     'font': dict(family="Inter, Arial, sans-serif", size=18, color=COLORS_CHART['text'])
        # },
        xaxis=dict(title='Year', type='category'),
        yaxis=dict(title='Month', categoryorder='array', categoryarray=month_names),
        margin=dict(l=40, r=40, t=80, b=40),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def generate_income_seasonality(income_data, settings=None):
    """Generate chart showing income seasonality by month"""
    import plotly.graph_objects as go
    import pandas as pd
    from datetime import datetime
    
    # Create sample data if no data available
    if not income_data or len(income_data) < 6:
        # Sample data with seasonal pattern
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        values = [4800, 4600, 4700, 5100, 5400, 5800, 6200, 6000, 5600, 5200, 5000, 5300]
        
        df = pd.DataFrame({
            'month': months,
            'value': values,
            'month_num': range(1, 13)
        })
    else:
        df = pd.DataFrame(income_data)
        df['date'] = pd.to_datetime(df['date'])
        
        if 'monthly_amount' in df.columns:
            df['value'] = df['monthly_amount']
        else:
            df['value'] = df['amount']
            
        # Extract month
        df['month'] = df['date'].dt.strftime('%b')
        df['month_num'] = df['date'].dt.month
        
        # Group by month
        monthly_avg = df.groupby(['month', 'month_num'])['value'].mean().reset_index()
        
        # Sort by month number
        df = monthly_avg.sort_values('month_num')
    
    # Create the figure
    fig = go.Figure()
    
    # Add bar chart
    fig.add_trace(go.Bar(
        x=df['month'],
        y=df['value'],
        name='Average Income',
        marker_color='#0082c8',
        hovertemplate='<b>%{x}</b><br>£%{y:,.2f}<extra></extra>'
    ))
    
    # Add line for overall average
    overall_avg = df['value'].mean()
    fig.add_trace(go.Scatter(
        x=df['month'],
        y=[overall_avg] * len(df),
        mode='lines',
        line=dict(color='#ff6b6b', width=2, dash='dash'),
        name='Annual Average'
    ))
    
    # Style the chart
    fig.update_layout(
        # title={
        #     'text': 'Income Seasonality by Month',
        #     'y':0.95,
        #     'x':0.5,
        #     'xanchor': 'center',
        #     'yanchor': 'top',
        #     'font': dict(family="Inter, Arial, sans-serif", size=18, color=COLORS_CHART['text'])
        # },
        xaxis=dict(
            title="Month",
            categoryorder='array',
            categoryarray=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ),
        yaxis=dict(
            title="Average Monthly Income (£)",
            tickprefix='£',
            tickformat=',.0f'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=40, t=80, b=40),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0)'
    )
    
    fig.update_xaxes(
        showgrid=False
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(226, 232, 240, 0.8)'
    )
    
    return fig

def generate_income_growth_chart(income_data, settings=None):
    """Generate year-over-year growth chart"""
    import plotly.graph_objects as go
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Create sample data if no data available
    if not income_data or len(income_data) < 12:
        # Generate sample data for 3 years
        today = datetime.now()
        dates = []
        values = []
        growth_rate = 0.08  # 8% annual growth
        base_income = 4000
        
        for i in range(-24, 12):
            month_date = today + timedelta(days=30*i)
            dates.append(month_date)
            
            # Calculate years from start
            years_from_start = (i + 24) / 12
            
            # Compound growth with some randomness
            compound_factor = (1 + growth_rate) ** years_from_start
            variation = np.random.normal(0, 200)
            values.append(base_income * compound_factor + variation)
            
        df = pd.DataFrame({
            'date': dates,
            'value': values
        })
    else:
        df = pd.DataFrame(income_data)
        df['date'] = pd.to_datetime(df['date'])
        
        if 'monthly_amount' in df.columns:
            df['value'] = df['monthly_amount']
        else:
            df['value'] = df['amount']
    
    # Extract year and month
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['year_month'] = df['date'].dt.strftime('%Y-%m')
    
    # Calculate annual average
    annual_avg = df.groupby('year')['value'].mean().reset_index()
    
    # Calculate YoY growth
    annual_avg['previous_year'] = annual_avg['value'].shift(1)
    annual_avg['yoy_growth'] = (annual_avg['value'] - annual_avg['previous_year']) / annual_avg['previous_year'] * 100
    annual_avg = annual_avg.dropna()
    
    # Create the figure
    fig = go.Figure()
    
    # Add bar chart for growth rates
    fig.add_trace(go.Bar(
        x=annual_avg['year'].astype(str),
        y=annual_avg['yoy_growth'],
        name='YoY Growth',
        marker_color=['#0082c8' if x > 0 else '#ff6b6b' for x in annual_avg['yoy_growth']],
        hovertemplate='<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>'
    ))
    
    # Add line for absolute values
    fig.add_trace(go.Scatter(
        x=annual_avg['year'].astype(str),
        y=annual_avg['value'],
        mode='lines+markers',
        line=dict(color='#228B22', width=2),
        marker=dict(size=8),
        name='Average Income',
        yaxis='y2',
        hovertemplate='<b>%{x}</b><br>Avg Income: £%{y:,.2f}<extra></extra>'
    ))
    
    # Style the chart
    fig.update_layout(
        # title={
        #     'text': 'Year-over-Year Income Growth',
        #     'y':0.95,
        #     'x':0.5,
        #     'xanchor': 'center',
        #     'yanchor': 'top',
        #     'font': dict(family="Inter, Arial, sans-serif", size=18, color=COLORS_CHART['text'])
        # },
        xaxis=dict(
            title="Year"
        ),
        yaxis=dict(
            title="YoY Growth (%)",
            ticksuffix='%'
        ),
        yaxis2=dict(
            title=dict(
                text="Average Income (£)",
                font=dict(color='#228B22')
            ),
            tickfont=dict(color='#228B22'),
            tickprefix='£',
            tickformat=',.0f',
            overlaying='y',
            side='right'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(l=40, r=80, t=80, b=40),
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0)'
    )
    
    fig.update_xaxes(
        showgrid=False
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(226, 232, 240, 0.8)'
    )
    
    return fig

def generate_income_chart(data, settings=None, months_ahead=6):
    """Generate visually stunning income chart with forecast if requested"""
    import pandas as pd
    import plotly.graph_objects as go
    from datetime import datetime, timedelta
    import numpy as np
    
    # Default settings
    if settings is None:
        settings = {}
    
    # Get chart type from settings
    chart_type = settings.get('chart_type', 'line')
    
    # Colors for chart elements
    COLORS_CHART = {
        'primary': '#0082c8',  # Blue
        'secondary': '#4ca3dd',  # Light blue
        'accent': '#003c7f',  # Dark blue
        'text': '#2d3748',  # Dark gray
        'grid': 'rgba(226, 232, 240, 0.8)'  # Light gray
    }
    
    # Check if user_data is a list and convert to DataFrame
    if isinstance(data, list) and len(data) > 0:
        df = pd.DataFrame(data)
    else:
        # Return an elegant placeholder chart if no data
        fig = go.Figure()
        fig.add_annotation(
            text="No income data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=18, family="Inter, Arial, sans-serif", color=COLORS_CHART['text'])
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0)',
            height=450,
            margin=dict(l=40, r=40, t=80, b=40),
        )
        return fig

    # Prepare the data
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Get monthly amounts
    if 'monthly_amount' in df.columns:
        df['value'] = df['monthly_amount']
    else:
        df['value'] = df['amount']
    
    # Create forecast dates - next X months
    forecast_months = months_ahead if isinstance(months_ahead, int) and months_ahead > 0 else 6
    last_date = df['date'].max() if not df.empty else datetime.now()
    forecast_dates = pd.date_range(start=last_date, periods=forecast_months+1, freq='ME')[1:]
    
    # For forecasting, use trend-based projection
    if len(df) >= 3:
        # Calculate trend coefficient (simple linear regression)
        x = np.arange(len(df))
        y = df['value'].values
        z = np.polyfit(x, y, 1)
        slope = z[0]
        
        # Use average of last 3 months as baseline
        baseline = df['value'].tail(3).mean()
        
        # Calculate trend
        forecast_values = [baseline + (slope * i) for i in range(1, forecast_months+1)]
    else:
        # Fallback to simple growth model
        avg_monthly = df['value'].mean() if not df.empty else 3000
        forecast_values = [avg_monthly * (1 + (i * 0.02)) for i in range(forecast_months)]
    
    # Create the figure
    fig = go.Figure()
    
    # Different chart types based on settings
    if chart_type == 'bar':
        # Historical data as bars
        fig.add_trace(
            go.Bar(
                x=df['date'],
                y=df['value'],
                name='Actual Income',
                marker_color=COLORS_CHART['primary'],
                hovertemplate='<b>%{x|%b %Y}</b><br>£%{y:,.2f}<extra></extra>'
            )
        )
        
        # Forecast as bars with different color
        fig.add_trace(
            go.Bar(
                x=forecast_dates,
                y=forecast_values,
                name='Forecast',
                marker_color=COLORS_CHART['secondary'],
                marker_line=dict(width=1, color='white'),
                hovertemplate='<b>%{x|%b %Y} (Forecast)</b><br>£%{y:,.2f}<extra></extra>'
            )
        )
        
    elif chart_type == 'area':
        # Historical data with area
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['value'],
                fill='tozeroy',
                fillcolor=f'rgba({int(COLORS_CHART["primary"][1:3], 16)}, {int(COLORS_CHART["primary"][3:5], 16)}, {int(COLORS_CHART["primary"][5:7], 16)}, 0.3)',
                line=dict(width=3, color=COLORS_CHART['primary']),
                name='Actual Income',
                hovertemplate='<b>%{x|%b %Y}</b><br>£%{y:,.2f}<extra></extra>'
            )
        )
        
        # Forecast with area
        fig.add_trace(
            go.Scatter(
                x=forecast_dates,
                y=forecast_values,
                fill='tozeroy',
                fillcolor=f'rgba({int(COLORS_CHART["secondary"][1:3], 16)}, {int(COLORS_CHART["secondary"][3:5], 16)}, {int(COLORS_CHART["secondary"][5:7], 16)}, 0.2)',
                line=dict(width=2, color=COLORS_CHART['secondary'], dash='dot'),
                name='Forecast',
                hovertemplate='<b>%{x|%b %Y} (Forecast)</b><br>£%{y:,.2f}<extra></extra>'
            )
        )
    
    elif chart_type == 'scatter':
        # Historical data as scatter
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['value'],
                mode='markers',
                marker=dict(
                    size=10, 
                    color=COLORS_CHART['primary'],
                    line=dict(width=1, color='white')
                ),
                name='Actual Income',
                hovertemplate='<b>%{x|%b %Y}</b><br>£%{y:,.2f}<extra></extra>'
            )
        )
        
        # Add trendline through the scatter
        x_all = np.array(range(len(df) + forecast_months))
        y_all = np.concatenate([df['value'].values, forecast_values])
        z = np.polyfit(x_all, y_all, 1)
        p = np.poly1d(z)
        
        fig.add_trace(
            go.Scatter(
                x=pd.concat([df['date'], pd.Series(forecast_dates)]),
                y=p(x_all),
                mode='lines',
                line=dict(color=COLORS_CHART['accent'], width=2),
                name='Trend',
                hovertemplate='<b>%{x|%b %Y} (Trend)</b><br>£%{y:,.2f}<extra></extra>'
            )
        )
        
        # Forecast as different color scatter
        fig.add_trace(
            go.Scatter(
                x=forecast_dates,
                y=forecast_values,
                mode='markers',
                marker=dict(
                    size=10, 
                    color=COLORS_CHART['secondary'],
                    line=dict(width=1, color='white'),
                    symbol='diamond'
                ),
                name='Forecast',
                hovertemplate='<b>%{x|%b %Y} (Forecast)</b><br>£%{y:,.2f}<extra></extra>'
            )
        )
    
    elif chart_type == 'pie':
        # For pie chart, show income sources instead of time series
        # Clear figure and create a new one
        fig = go.Figure()
        
        # Check if source exists in data
        if 'source' in df.columns:
            # Group by source
            source_data = df.groupby('source')['value'].sum().reset_index()
            
            fig.add_trace(
                go.Pie(
                    labels=source_data['source'], 
                    values=source_data['value'],
                    textinfo='label+percent',
                    marker=dict(
                        colors=[COLORS_CHART['primary'], COLORS_CHART['secondary'], COLORS_CHART['accent']],
                        line=dict(color='white', width=2)
                    ),
                    hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{percent}<extra></extra>'
                )
            )
        else:
            # Default categories if source not available
            fig.add_trace(
                go.Pie(
                    labels=['Primary Income', 'Secondary Income', 'Investments'],
                    values=[sum(df['value'])*0.7, sum(df['value'])*0.2, sum(df['value'])*0.1],
                    textinfo='label+percent',
                    marker=dict(
                        colors=[COLORS_CHART['primary'], COLORS_CHART['secondary'], COLORS_CHART['accent']],
                        line=dict(color='white', width=2)
                    ),
                    hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{percent}<extra></extra>'
                )
            )
    
    else:  # Default to line chart
        # Add subtle area under the curve
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['value'],
                fill='tozeroy',
                fillcolor=f'rgba({int(COLORS_CHART["primary"][1:3], 16)}, {int(COLORS_CHART["primary"][3:5], 16)}, {int(COLORS_CHART["primary"][5:7], 16)}, 0.1)',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='none'
            )
        )
        
        # Add historical data line
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['value'],
                mode='lines+markers',
                name='Actual Income',
                marker=dict(
                    size=8, 
                    color=COLORS_CHART['primary'],
                    line=dict(width=1, color='white')
                ),
                line=dict(width=3, color=COLORS_CHART['primary'], shape='spline'),
                hovertemplate='<b>%{x|%b %Y}</b><br>£%{y:,.2f}<extra></extra>'
            )
        )
        
        # Add forecast line with elegant styling
        fig.add_trace(
            go.Scatter(
                x=forecast_dates,
                y=forecast_values,
                mode='lines+markers',
                name='Forecast',
                marker=dict(
                    size=7, 
                    color=COLORS_CHART['secondary'],
                    line=dict(width=1, color='white')
                ),
                line=dict(width=2, color=COLORS_CHART['secondary'], dash='dot'),
                hovertemplate='<b>%{x|%b %Y} (Forecast)</b><br>£%{y:,.2f}<extra></extra>'
            )
        )
        
        # Add moving average for trend visualization
        if len(df) >= 3 and settings.get('show_trend', True):
            df['moving_avg'] = df['value'].rolling(window=3, min_periods=1).mean()
            fig.add_trace(
                go.Scatter(
                    x=df['date'],
                    y=df['moving_avg'],
                    mode='lines',
                    name='3-Month Trend',
                    line=dict(width=2, color=COLORS_CHART['accent'], dash='dot'),
                    opacity=0.7,
                    hovertemplate='<b>%{x|%b %Y} (Trend)</b><br>£%{y:,.2f}<extra></extra>'
                )
            )
    
    # Style the chart based on the chart type
    if chart_type == 'pie':
        chart_title = 'Income Sources'
        fig.update_layout(
            title={
                'text': chart_title,
                'y':0.95,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(family="Inter, Arial, sans-serif", size=22, color=COLORS_CHART['text'])
            },
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0)',
            margin=dict(l=40, r=40, t=80, b=40),
            height=450,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="right",
                x=1.1,
                bgcolor='rgba(255,255,255,0.9)',
            ),
            font=dict(family="Inter, Arial, sans-serif", color=COLORS_CHART['text']),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Inter, Arial, sans-serif"
            )
        )
    else:
        chart_title = 'Income Forecast'
        if chart_type != 'line':
            chart_title += f' ({chart_type.capitalize()})'
            
        fig.update_layout(
            # title={
            #     'text': chart_title,
            #     'y':0.95,
            #     'x':0.5,
            #     'xanchor': 'center',
            #     'yanchor': 'top',
            #     'font': dict(family="Inter, Arial, sans-serif", size=22, color=COLORS_CHART['text'])
            # },
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0)',
            margin=dict(l=40, r=40, t=80, b=40),
            height=450,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor='rgba(255,255,255,0.9)',
            ),
            font=dict(family="Inter, Arial, sans-serif", color=COLORS_CHART['text']),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Inter, Arial, sans-serif"
            )
        )
        
        # Style axes for a refined, minimalist look
        fig.update_xaxes(
            title=dict(
                text="Date",
                font=dict(size=14, family="Inter, Arial, sans-serif")
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(226, 232, 240, 0.8)',
            tickformat='%b %Y',
            zeroline=False
        )
        
        fig.update_yaxes(
            title=dict(
                text="Monthly Income (£)",
                font=dict(size=14, family="Inter, Arial, sans-serif")
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(226, 232, 240, 0.8)',
            tickprefix='£',
            tickformat=',.0f',
            zeroline=False
        )
    
    return fig

# Add this function to generate the multiple income charts modal
def generate_income_insights_modal(user_data):
    """Generate content for the income insights modal with a 2x3 grid layout"""
    income_data = user_data.get('income', [])
    
    # Create a container with 2x3 grid layout for charts
    modal_content = html.Div([
        html.H3("Income Insights", className="insights-modal-title"),
        html.P("Select charts to add to your dashboard.", className="insights-modal-subtitle"),
        
        # Grid layout for charts (2 rows x 3 columns)
        html.Div([
            # Row 1
            html.Div([
                # Chart 1: Income Forecast
                html.Div([
                    html.Div([
                        html.H4("Income Forecast", className="chart-title"),
                        dcc.Graph(
                            figure=generate_income_chart(income_data, {"chart_type": "line"}, 6),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-insight-chart", "index": 1}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide"),
                
                # Chart 2: Income Sources
                html.Div([
                    html.Div([
                        html.H4("Income Sources", className="chart-title"),
                        dcc.Graph(
                            figure=generate_income_breakdown_pie(income_data, {"chart_type": "pie"}),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-insight-chart", "index": 2}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide"),
                
                # Chart 3: Monte Carlo Simulation
                html.Div([
                    html.Div([
                        html.H4("Income Forecast Simulation", className="chart-title"),
                        dcc.Graph(
                            figure=generate_monte_carlo_simulation(income_data, {"simulations": 100}),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-insight-chart", "index": 3}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide")
            ], className="chart-row-wide"),
            
            # Row 2
            html.Div([
                # Chart 4: Income Heatmap
                html.Div([
                    html.Div([
                        html.H4("Income Heatmap", className="chart-title"),
                        dcc.Graph(
                            figure=generate_income_heatmap(income_data, {}),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-insight-chart", "index": 4}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide"),
                
                # Chart 5: Income Seasonality
                html.Div([
                    html.Div([
                        html.H4("Income Seasonality", className="chart-title"),
                        dcc.Graph(
                            figure=generate_income_seasonality(income_data, {}),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-insight-chart", "index": 5}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide"),
                
                # Chart 6: Year-over-Year Growth
                html.Div([
                    html.Div([
                        html.H4("Year-over-Year Growth", className="chart-title"),
                        dcc.Graph(
                            figure=generate_income_growth_chart(income_data, {}),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-insight-chart", "index": 6}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide")
            ], className="chart-row-wide")
        ], className="insights-chart-grid-wide")
    ], className="insights-modal-content-wide")

    return modal_content

# Update the main insights modal callback to handle expenses insights
@callback(
    [
        Output("insights-specific-modal", "is_open"),
        Output("insights-specific-modal-content", "children"),
        Output("insights-specific-modal-header", "children")
    ],
    Input("insights-specific-store", "data"),
    State("user-data-store", "data"),
    prevent_initial_call=True
)
def handle_insights_specific_modal(insights_data, user_data):
    print('--- handle_insights_specific_modal triggered ---')
    print(f'Insights specific data: {insights_data}')
    
    if not insights_data or not insights_data.get("open"):
        print('Not opening insights specific modal')
        return False, dash.no_update, dash.no_update
    
    print('Opening insights specific modal and generating content...')
    print(f'User data available: {bool(user_data)}')
    
    # Default title
    modal_title = "Financial Insights"
    
    # Generate different content based on insight type
    insight_type = insights_data.get("type", "income_analysis")
    
    if insight_type == "income_analysis":
        income_data = user_data.get('income', [])
        print(f'Income data entries: {len(income_data)}')
        modal_content = generate_income_insights_modal(user_data)
        modal_title = "Income Analysis Dashboard"
    elif insight_type == "expenses_analysis":
        expenses_data = user_data.get('expenses', [])
        print(f'Expenses data entries: {len(expenses_data)}')
        modal_content = generate_expenses_insights_modal(user_data)
        modal_title = "Expenses Analysis Dashboard"
    else:
        # Default content if no specific type matched
        modal_content = html.Div([
            html.H3("Financial Insights"),
            html.P("Here are some insights about your finances.")
        ])
    
    return True, modal_content, modal_title

# Add a callback to close the modal
@callback(
    Output("insights-specific-modal", "is_open", allow_duplicate=True),
    Input("close-insights-specific-modal", "n_clicks"),
    prevent_initial_call=True
)
def close_insights_specific_modal(n_clicks):
    if n_clicks:
        return False
    raise PreventUpdate


@callback(
    Output("temp-insight-store", "data", allow_duplicate=True),
    Input({"type": "add-insight-chart", "index": ALL}, "n_clicks"),
    [
        State("dashboard-settings-store", "data"),
        State("user-data-store", "data"),
        State({"type": "add-insight-chart", "index": ALL}, "id")
    ],
    prevent_initial_call=True
)
def prepare_insight_for_dashboard(n_clicks_list, current_settings, user_data, button_ids):
    ctx = dash.callback_context
    
    # If no callback was triggered or no buttons were clicked
    if not ctx.triggered or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    
    # Get the exact triggered component's property ID
    triggered_prop_id = ctx.triggered[0]['prop_id']
    
    # Debug logging
    # print(f"Triggered property ID: {triggered_prop_id}")
    
    # Extract the exact button index that was clicked
    button_index = None
    
    # The triggered_prop_id will be in format: '{"index":X,"type":"add-insight-chart"}.n_clicks'
    if triggered_prop_id:
        try:
            # Parse the component ID from the property ID
            import json
            component_id = json.loads(triggered_prop_id.split('.')[0])
            button_index = component_id['index']
            print(f"Extracted button index: {button_index}")
        except Exception as e:
            print(f"Error parsing triggered ID: {e}")
            # Fallback to the old method if parsing fails
            for i, (n_clicks, button_id) in enumerate(zip(n_clicks_list, button_ids)):
                if n_clicks and n_clicks > 0:
                    button_index = button_id['index']
                    print(f"Fallback: found button index {button_index}")
                    break
    
    # If we couldn't determine which button was clicked
    if button_index is None:
        print("Could not determine which button was clicked")
        raise PreventUpdate
    
    # Chart types and their settings
    chart_types = {
        1: {"type": "income_forecast", "title": "Income Forecast", "settings": {"chart_type": "line"}, "months_ahead": 6},
        2: {"type": "income_breakdown_pie", "title": "Income Sources", "settings": {"chart_type": "pie"}},
        3: {"type": "income_monte_carlo", "title": "Income Forecast Simulation", "settings": {"simulations": 100}},
        4: {"type": "income_heatmap", "title": "Income Heatmap", "settings": {}},
        5: {"type": "income_seasonality", "title": "Income Seasonality", "settings": {}},
        6: {"type": "income_growth", "title": "Year-over-Year Growth", "settings": {}}
    }
    
    # Get the chart data for the clicked button
    chart_data = chart_types.get(button_index, {"type": "income_chart", "title": "Income Chart", "settings": {}})
    
    # print(f"Selected chart type: {chart_data['type']}, title: {chart_data['title']}")
    
    # Calculate position and prepare component
    if not current_settings:
        current_settings = {'components': []}
    if not isinstance(current_settings, dict):
        current_settings = {'components': []}
    if 'components' not in current_settings:
        current_settings['components'] = []

    component_width = 8
    component_height = 6
    
    next_position = find_next_available_position(current_settings)
    component_id = str(uuid.uuid4())
    
    new_component = {
        'id': component_id,
        'type': chart_data['type'],
        'title': chart_data['title'],
        'position': {
            'x': next_position['x'],
            'y': next_position['y'],
            'w': component_width,
            'h': component_height
        },
        'settings': chart_data['settings'].copy()  # Make a copy to avoid side effects
    }

    # Apply any additional settings
    if chart_data['type'] == 'income_forecast' and 'months_ahead' in chart_data:
        new_component['settings']['months_ahead'] = chart_data['months_ahead']
    
    # For debugging
    # print(f"Adding chart to dashboard: {chart_data['title']}")
    # print(f"New component: {new_component}")
    
    # Return the data needed to update the dashboard
    return {
        'new_component': new_component,
        'position': next_position,
        'width': component_width,
        'height': component_height,
        'close_modal': False  # Whether to close the modal
    }

@callback(
    [
        Output("dashboard-settings-store", "data", allow_duplicate=True),
        Output("empty-dashboard-state", "style", allow_duplicate=True), 
        Output("dashboard-grid", "children", allow_duplicate=True),
        Output("dashboard-grid", "layouts", allow_duplicate=True),
        Output("insights-specific-modal", "is_open", allow_duplicate=True)
    ],
    Input("temp-insight-store", "data"),
    [
        State("dashboard-settings-store", "data"),
        State("user-data-store", "data"),
        State("dashboard-grid", "children"),
        State("dashboard-grid", "layouts")
    ],
    prevent_initial_call=True
)
def update_dashboard_with_insight(insight_data, current_settings, user_data, current_children, current_layouts):
    if not insight_data:
        raise PreventUpdate
    
    print("Updating dashboard with insight data...")
    
    # Get data from the temporary store
    new_component = insight_data['new_component']
    next_position = insight_data['position']
    component_width = insight_data['width']
    component_height = insight_data['height']
    
    # Make a deep copy to avoid modifying the input state
    if current_layouts is None:
        current_layouts = {'lg': [], 'md': [], 'sm': [], 'xs': []}
    else:
        current_layouts = copy.deepcopy(current_layouts)
    
    if current_settings is None:
        current_settings = {'components': []}
    else:
        current_settings = copy.deepcopy(current_settings)
    
    if 'components' not in current_settings:
        current_settings['components'] = []
    
    # Add the new component to settings
    current_settings['components'].append(new_component)
    
    # Update layouts
    for breakpoint in current_layouts.keys():
        bp_width = component_width
        if breakpoint == 'xs':
            bp_width = 4
        elif breakpoint == 'sm':
            bp_width = 6
            
        current_layouts[breakpoint].append({
            'i': new_component['id'],
            'x': next_position['x'],
            'y': next_position['y'],
            'w': bp_width,
            'h': component_height,
            'minW': 4,
            'minH': 4
        })

    # Generate components with the updated settings
    components, _ = generate_dashboard_components(current_settings, user_data)

    # Save if user is not guest
    user_id = user_data.get('user_info', {}).get('id')
    if user_id and user_id != 'Guest':
        save_dashboard_settings_to_db(user_id, current_settings)

    empty_style = {"display": "none"}
    
    # Keep the modal open (False) or close it (True) based on what you want
    close_modal = insight_data.get('close_modal', False)
    
    print(f"Dashboard updated with new component: {new_component['title']}")
    
    return current_settings, empty_style, components, current_layouts, not close_modal  # Notice the NOT here


def generate_expense_breakdown(data, settings=None, period='monthly'):
    """Generate visually stunning expense breakdown chart based on user data"""
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    from datetime import datetime
    import numpy as np
    
    # Default settings
    if settings is None:
        settings = {}
    
    # Check if user_data is a list and convert to DataFrame
    if isinstance(data, list) and len(data) > 0:
        df = pd.DataFrame(data)
    else:
        # Create demo data with realistic categories
        df = pd.DataFrame({
            'category': ['Housing', 'Food & Groceries', 'Transportation', 'Entertainment', 
                         'Utilities', 'Healthcare', 'Savings', 'Education'],
            'amount': [1500, 600, 350, 250, 300, 200, 400, 150],
            'date': [datetime.now()] * 8
        })
    
    # Prepare the data
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter by period if specified
        if period == 'monthly' and len(df) > 0:
            current_month = df['date'].max().month
            current_year = df['date'].max().year
            df = df[(df['date'].dt.month == current_month) & (df['date'].dt.year == current_year)]
        elif period == 'yearly' and len(df) > 0:
            current_year = df['date'].max().year
            df = df[df['date'].dt.year == current_year]
    
    # Group by category
    df_grouped = df.groupby('category')['amount'].sum().reset_index()
    df_grouped = df_grouped.sort_values('amount', ascending=False)
    
    # Calculate percentages for labels
    total = df_grouped['amount'].sum()
    df_grouped['percent'] = df_grouped['amount'] / total * 100
    
    # Chart selection - allow customization through settings
    chart_type = settings.get('chart_type', 'donut') if settings else 'donut'
    
    if chart_type == 'pie' or chart_type == 'donut':
        # Create a clean, modern donut chart
        hole_size = 0.6 if chart_type == 'donut' else 0
        
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=df_grouped['category'],
            values=df_grouped['amount'],
            textinfo='label+percent',
            textposition='outside',
            marker=dict(
                COLORS_CHART=COLORS_CHART['chart_palette'],
                line=dict(color='white', width=1)
            ),
            hole=hole_size,
            hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{percent:.1f}%<extra></extra>',
            rotation=90
        ))
        
        # Add center text for donut chart
        if chart_type == 'donut':
            fig.add_annotation(
                text=f"<b>£{total:,.0f}</b>",
                x=0.5, y=0.5,
                font=dict(size=20, color=COLORS_CHART['primary'], family="Inter, Arial, sans-serif"),
                showarrow=False
            )
    
    elif chart_type == 'bar':
        # Create a clean bar chart
        fig = go.Figure()
        
        # Determine gradient COLORS_CHART based on rank
        color_scale = px.COLORS_CHART.sequential.Blues
        
        # Create one trace with all bars
        fig.add_trace(go.Bar(
            x=df_grouped['category'],
            y=df_grouped['amount'],
            marker=dict(
                color=df_grouped['amount'],
                COLORS_CHARTcale=color_scale,
                line=dict(width=0)
            ),
            text=[f"£{amount:,.0f}" for amount in df_grouped['amount']],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>£%{y:,.2f}<br>%{text}<extra></extra>'
        ))
        
        fig.update_layout(
            xaxis=dict(
                categoryorder='total descending',
                title=None
            )
        )
    
    elif chart_type == 'treemap':
        # Create simple, elegant treemap
        fig = px.treemap(
            df_grouped,
            path=['category'],
            values='amount',
            color='amount',
            color_continuous_scale=px.COLORS_CHART.sequential.Blues,
            hover_data=['percent']
        )
        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{customdata[0]:.1f}%<extra></extra>',
            texttemplate='<b>%{label}</b><br>£%{value:,.0f}',
            textfont=dict(family="Inter, Arial, sans-serif", size=14)
        )
        
    else:  # Default to sunburst for a clean, modern visualization
        # Create simplified sunburst
        fig = px.sunburst(
            df_grouped,
            path=['category'],
            values='amount',
            color='amount',
            color_continuous_scale=px.COLORS_CHART.sequential.Blues,
            hover_data=['percent']
        )
        fig.update_traces(
            textinfo='label+value',
            hovertemplate='<b>%{label}</b><br>£%{value:,.2f}<br>%{customdata[0]:.1f}%<extra></extra>'
        )
    
    # Apply clean, minimalist styling to all chart types
    title_text = "Expense Breakdown"
    if period == 'monthly':
        if 'date' in df.columns and not df.empty:
            month_year = df['date'].iloc[0].strftime('%B %Y')
            title_text = f"Monthly Expenses - {month_year}"
    elif period == 'yearly':
        if 'date' in df.columns and not df.empty:
            year = df['date'].iloc[0].strftime('%Y')
            title_text = f"Yearly Expenses - {year}"
    
    fig.update_layout(
        title={
            'text': title_text,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(family="Inter, Arial, sans-serif", size=22, color=COLORS_CHART['text'])
        },
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(255,255,255,0)',
        margin=dict(l=20, r=20, t=80, b=20),
        height=450,
        font=dict(family="Inter, Arial, sans-serif", color=COLORS_CHART['text']),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Inter, Arial, sans-serif"
        )
    )
    
    # If it's a bar chart, style the axes
    if chart_type == 'bar':
        fig.update_yaxes(
            title=dict(
                text="Amount (£)",
                font=dict(size=14, family="Inter, Arial, sans-serif")
            ),
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(226, 232, 240, 0.8)',
            tickprefix='£',
            tickformat=',.0f',
            zeroline=False
        )
    
    return fig


# Add callback for adding expense charts to dashboard
@callback(
    Output("temp-insight-store", "data", allow_duplicate=True),
    Input({"type": "add-expense-insight", "index": ALL}, "n_clicks"),
    [
        State("dashboard-settings-store", "data"),
        State("user-data-store", "data"),
        State({"type": "add-expense-insight", "index": ALL}, "id")
    ],
    prevent_initial_call=True
)
def prepare_expense_insight_for_dashboard(n_clicks_list, current_settings, user_data, button_ids):
    ctx = dash.callback_context
    if not ctx.triggered or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    
    # Find which button was clicked by using the triggered property
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Parse the JSON string to get the clicked button's index
    try:
        # Convert string representation of dict to actual dict
        triggered_dict = json.loads(triggered_id)
        clicked_index = triggered_dict['index']
    except:
        # Fallback in case parsing fails
        print("Failed to parse triggered ID:", triggered_id)
        raise PreventUpdate
    
    # Chart types for expenses
    chart_types = {
        1: {"type": "expenses_forecast", "title": "Expenses Month Over Month", "settings": {"chart_type": "line"}, "months_ahead": 6},
        2: {"type": "expenses_breakdown_pie", "title": "Expense By Category", "settings": {"chart_type": "pie"}},
        3: {"type": "expenses_trends", "title": "Budget VS Actual Spending", "settings": {"time_period": "monthly"}},
        4: {"type": "expenses_heatmap", "title": "Top Expenses (Last 30 Days)", "settings": {}},
        5: {"type": "expenses_seasonality", "title": "Expenses Seasonality", "settings": {}},
        6: {"type": "expenses_growth", "title": "Year-over-Year Spending", "settings": {}}
    }
    
    chart_data = chart_types.get(clicked_index, {"type": "expenses_chart", "title": "Expenses Chart", "settings": {}})
    
    # Calculate position and prepare component
    if not current_settings:
        current_settings = {'components': []}
    if not isinstance(current_settings, dict):
        current_settings = {'components': []}
    if 'components' not in current_settings:
        current_settings['components'] = []

    component_width = 8
    component_height = 6
    
    next_position = find_next_available_position(current_settings)
    component_id = str(uuid.uuid4())
    
    new_component = {
        'id': component_id,
        'type': chart_data['type'],
        'title': chart_data['title'],
        'position': {
            'x': next_position['x'],
            'y': next_position['y'],
            'w': component_width,
            'h': component_height
        },
        'settings': chart_data['settings']
    }
    
    # For debugging
    print(f"Adding expense chart to dashboard: {chart_data['title']}")
    print(f"New component: {new_component}")
    
    # Return the data needed to update the dashboard
    return {
        'new_component': new_component,
        'position': next_position,
        'width': component_width,
        'height': component_height,
        'close_modal': False  # Whether to close the modal
    }

# Add this function to generate the multiple expenses charts modal
def generate_expenses_insights_modal(user_data):
    """Generate content for the expenses insights modal with a 2x3 grid layout
    
    Creates an elegant, blue-themed insights dashboard with practical financial charts
    that provide genuine value for personal finance management.
    
    The expenses_data format is expected to be from the SQL expenses table with columns:
    - expense_id: UUID
    - user_id: Integer
    - description: String
    - amount: Decimal
    - category: String
    - date: Timestamp
    - due_date: Date
    """
    expenses_data = user_data.get('expenses', [])
    
    # Check if we have data
    if not expenses_data:
        return html.Div("No expense data available", className="no-data-message")
    
    # Professional blue color palette
    colors_expense = {
        'primary': '#1a73e8',
        'secondary': '#4285f4',
        'light': '#8ab4f8',
        'dark': '#174ea6',
        'background': '#f8f9fc',
        'text': '#202124'
    }
    
    # Create a container with 2x3 grid layout for charts
    modal_content = html.Div([
        html.H3("Expenses Insights", className="insights-modal-title"),
        html.P("Select charts to add to your dashboard.", className="insights-modal-subtitle"),
        
        # Grid layout for charts (2 rows x 3 columns)
        html.Div([
            # Row 1
            html.Div([
                # Chart 1: Monthly Spending Overview
                html.Div([
                    html.Div([
                        html.H4("Monthly Spending Overview", className="chart-title"),
                        dcc.Graph(
                            figure=generate_monthly_spending_overview(expenses_data, {"color_scheme": colors_expense}),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-expense-insight", "index": 1}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide"),
                
                # Chart 2: Expense Categories
                html.Div([
                    html.Div([
                        html.H4("Expense Breakdown", className="chart-title"),
                        dcc.Graph(
                            figure=generate_expense_categories_donut(expenses_data, {"color_scheme": colors_expense}),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-expense-insight", "index": 2}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide"),
                
                # Chart 3: Budget vs Actual
                html.Div([
                    html.Div([
                        html.H4("Budget vs. Actual", className="chart-title"),
                        dcc.Graph(
                            figure=generate_budget_vs_actual(expenses_data, user_data.get('budget', {}), {"color_scheme": colors_expense}),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-expense-insight", "index": 3}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide")
            ], className="chart-row-wide"),
            
            # Row 2
            html.Div([
                # Chart 4: Top Spending Categories
                html.Div([
                    html.Div([
                        html.H4("Top Spending Categories", className="chart-title"),
                        dcc.Graph(
                            figure=generate_top_spending_categories(expenses_data, {"color_scheme": colors_expense}),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-expense-insight", "index": 4}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide"),
                
                # Chart 5: Spending Trends
                html.Div([
                    html.Div([
                        html.H4("Spending Trends", className="chart-title"),
                        dcc.Graph(
                            figure=generate_spending_trends(expenses_data, {"color_scheme": colors_expense}),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-expense-insight", "index": 5}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide"),
                
                # Chart 6: Recurring Expenses
                html.Div([
                    html.Div([
                        html.H4("Recurring Expenses", className="chart-title"),
                        dcc.Graph(
                            figure=generate_recurring_expenses(expenses_data, {"color_scheme": colors_expense}),
                            config={'displayModeBar': False},
                            className="insights-chart"
                        ),
                        html.Button("Add to Dashboard", id={"type": "add-expense-insight", "index": 6}, className="add-chart-btn")
                    ], className="chart-card")
                ], className="chart-col-wide")
            ], className="chart-row-wide")
        ], className="insights-chart-grid-wide")
    ], className="insights-modal-content-wide", style={"backgroundColor": colors_expense['background']})

    return modal_content

# Helper functions for each chart

def generate_monthly_spending_overview(expenses_data, options):
    """Generate a bar chart showing monthly spending with trend line
    
    Parameters:
    - expenses_data: List of expense records from SQL database
    - options: Dictionary with chart customization options
    
    Returns:
    - Plotly figure object with monthly spending bar chart and trend line
    """
    default_colors = {
        'primary': '#1a73e8',
        'secondary': '#4285f4',
        'light': '#8ab4f8',
        'dark': '#174ea6',
        'background': '#f8f9fc',
        'text': '#202124'
    }
    
    # Use provided color scheme or fall back to default
    colors = options.get("color_scheme", default_colors)
    
    # Just in case the color_scheme is present but missing keys:
    for key, value in default_colors.items():
        colors.setdefault(key, value)
    
    # Process the actual expense data into monthly totals
    # Group expenses by month and calculate totals
    monthly_data = {}
    
    # Convert dates to datetime objects if they're strings
    for expense in expenses_data:
        date = expense['date'] if isinstance(expense['date'], datetime) else datetime.fromisoformat(expense['date'].replace('Z', '+00:00'))
        month_key = date.strftime('%Y-%m')
        amount = float(expense['amount'])
        
        if month_key in monthly_data:
            monthly_data[month_key] += amount
        else:
            monthly_data[month_key] = amount
    
    # Sort by month
    sorted_months = sorted(monthly_data.keys())
    
    # Format month labels for display
    month_labels = [datetime.strptime(m, '%Y-%m').strftime('%b %Y') for m in sorted_months]
    monthly_totals = [monthly_data[m] for m in sorted_months]
    
    # Create figure
    fig = go.Figure()
    
    # Add bar chart
    fig.add_trace(go.Bar(
        x=month_labels,
        y=monthly_totals,
        marker_color=colors['primary'],
        name="Monthly Spending"
    ))
    
    # Add trend line (rolling average)
    if len(monthly_totals) > 1:
        trend_data = []
        for i in range(len(monthly_totals)):
            trend_data.append(sum(monthly_totals[:i+1]) / (i+1))
        
        fig.add_trace(go.Scatter(
            x=month_labels,
            y=trend_data,
            mode='lines',
            line=dict(color=colors['dark'], width=2, dash='dot'),
            name="Running Average"
        ))
    
    # Update layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(tickprefix="£", tickfont=dict(size=10)),
        hovermode="x unified"
    )
    
    return fig

def generate_expense_categories_donut(expenses_data, options):
    """Generate a modern donut chart for expense categories
    
    Parameters:
    - expenses_data: List of expense records from SQL database
    - options: Dictionary with chart customization options
    
    Returns:
    - Plotly figure object with donut chart of expense categories
    """
    default_colors = {
        'primary': '#1a73e8',
        'secondary': '#4285f4',
        'light': '#8ab4f8',
        'dark': '#174ea6',
        'background': '#f8f9fc',
        'text': '#202124'
    }
    
    # Use provided color scheme or fall back to default
    colors = options.get("color_scheme", default_colors)
    
    # Just in case the color_scheme is present but missing keys:
    for key, value in default_colors.items():
        colors.setdefault(key, value)
    
    # Process the actual expense data into category totals
    category_totals = {}
    
    for expense in expenses_data:
        category = expense['category'] if expense['category'] else 'Uncategorized'
        amount = float(expense['amount'])
        
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount
    
    # Sort categories by amount (descending)
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    # If we have too many categories, group smaller ones as "Other"
    if len(sorted_categories) > 6:
        main_categories = sorted_categories[:5]
        other_total = sum(amount for _, amount in sorted_categories[5:])
        
        categories = [cat for cat, _ in main_categories] + ['Other']
        amounts = [amount for _, amount in main_categories] + [other_total]
    else:
        categories = [cat for cat, _ in sorted_categories]
        amounts = [amount for _, amount in sorted_categories]
    
    # Create color gradient based on the blue theme
    # Generate enough colors for all categories
    num_colors = len(categories)
    base_colors = [colors['primary'], colors['secondary'], colors['light'], 
                  '#5c9ce5', '#7baef2', '#a8c7f0']
    
    # If we need more colors, generate them
    if num_colors > len(base_colors):
        import colorsys
        
        # Generate more blue-themed colors
        hsv_tuples = [(210/360, 0.7, 0.5 + 0.5 * i/num_colors) for i in range(num_colors)]
        color_scale = ['#%02x%02x%02x' % tuple(int(x*255) for x in colorsys.hsv_to_rgb(*hsv)) 
                      for hsv in hsv_tuples]
    else:
        color_scale = base_colors[:num_colors]
    
    # Calculate total for the center of the donut
    total = sum(amounts)
    
    # Create figure
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=amounts,
        hole=.6,
        marker=dict(colors=color_scale),
        textinfo='label+percent',
        insidetextorientation='radial',
        hoverinfo='label+value+percent',
        hovertemplate='%{label}: £%{value:.2f}<br>%{percent}<extra></extra>'
    )])
    
    # Update layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        showlegend=False,
        annotations=[dict(text=f"£{total:.2f}", x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    return fig

def generate_budget_vs_actual(expenses_data, budget_data, options):
    """Generate a bar chart comparing budget vs actual spending by category
    
    Parameters:
    - expenses_data: List of expense records from SQL database
    - budget_data: Dictionary with budget amounts by category
    - options: Dictionary with chart customization options
    
    Returns:
    - Plotly figure object with budget vs. actual bar chart
    """
    default_colors = {
        'primary': '#1a73e8',
        'secondary': '#4285f4',
        'light': '#8ab4f8',
        'dark': '#174ea6',
        'background': '#f8f9fc',
        'text': '#202124'
    }
    
    # Use provided color scheme or fall back to default
    colors = options.get("color_scheme", default_colors)
    
    # Just in case the color_scheme is present but missing keys:
    for key, value in default_colors.items():
        colors.setdefault(key, value)
    
    # Process the actual expense data into category totals
    category_totals = {}
    
    # Get actual spending by category
    for expense in expenses_data:
        category = expense['category'] if expense['category'] else 'Uncategorized'
        amount = float(expense['amount'])
        
        if category in category_totals:
            category_totals[category] += amount
        else:
            category_totals[category] = amount
    
    # Get current month and year for budget comparison
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    
    # Filter expenses for the current month only
    current_month_expenses = {}
    for expense in expenses_data:
        date = expense['date'] if isinstance(expense['date'], datetime) else datetime.fromisoformat(expense['date'].replace('Z', '+00:00'))
        if date.month == current_month and date.year == current_year:
            category = expense['category'] if expense['category'] else 'Uncategorized'
            amount = float(expense['amount'])
            
            if category in current_month_expenses:
                current_month_expenses[category] += amount
            else:
                current_month_expenses[category] = amount
    
    # If no budget data is provided, create a simple estimate based on category totals
    if not budget_data:
        # Use average monthly spend as a simple budget estimate
        num_months = max(1, len(set((datetime.fromisoformat(expense['date'].replace('Z', '+00:00')).strftime('%Y-%m') 
                        for expense in expenses_data))))
        
        budget_estimates = {}
        for category, total in category_totals.items():
            budget_estimates[category] = total / num_months * 1.1  # 10% buffer on average
    else:
        budget_estimates = budget_data
    
    # Get top categories by total spending
    top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
    categories = [category for category, _ in top_categories]
    
    # Prepare data for chart
    budget_values = [budget_estimates.get(category, 0) for category in categories]
    actual_values = [current_month_expenses.get(category, 0) for category in categories]
    
    # Create figure
    fig = go.Figure()
    
    # Add bars for budget
    fig.add_trace(go.Bar(
        x=categories,
        y=budget_values,
        name='Budget',
        marker_color=colors['secondary'],
        opacity=0.7
    ))
    
    # Add bars for actual spending
    fig.add_trace(go.Bar(
        x=categories,
        y=actual_values,
        name='Actual',
        marker_color=colors['primary']
    ))
    
    # Update layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        barmode='group',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(tickprefix="£", tickfont=dict(size=10))
    )
    
    return fig

def generate_top_spending_categories(expenses_data, options):
    """Generate a horizontal bar chart showing top spending categories
    
    Parameters:
    - expenses_data: List of expense records from SQL database
    - options: Dictionary with chart customization options
    
    Returns:
    - Plotly figure object with horizontal bar chart of top spending categories
    """
    default_colors = {
        'primary': '#1a73e8',
        'secondary': '#4285f4',
        'light': '#8ab4f8',
        'dark': '#174ea6',
        'background': '#f8f9fc',
        'text': '#202124'
    }
    
    # Use provided color scheme or fall back to default
    colors = options.get("color_scheme", default_colors)
    
    # Just in case the color_scheme is present but missing keys:
    for key, value in default_colors.items():
        colors.setdefault(key, value)
    
    # Get time frame - default to past 30 days
    days = options.get("days", 30)
    
    # Calculate cutoff date
    today = datetime.now()
    cutoff_date = today - timedelta(days=days)
    
    # Filter expenses within the time period
    filtered_expenses = []
    for expense in expenses_data:
        date = expense['date'] if isinstance(expense['date'], datetime) else datetime.fromisoformat(expense['date'].replace('Z', '+00:00'))
        if date >= cutoff_date:
            filtered_expenses.append(expense)
    
    # Group by description and sum amounts
    merchant_totals = {}
    for expense in filtered_expenses:
        description = expense['description'].strip()
        # Skip empty descriptions
        if not description:
            continue
            
        amount = float(expense['amount'])
        
        if description in merchant_totals:
            merchant_totals[description] += amount
        else:
            merchant_totals[description] = amount
    
    # Sort and get top 10 merchants
    top_merchants = sorted(merchant_totals.items(), key=lambda x: x[1], reverse=True)[:10]
    
    if not top_merchants:
        # No data, return empty figure with message
        fig = go.Figure()
        fig.update_layout(
            annotations=[
                dict(
                    text="No expense data available for the selected period",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5
                )
            ],
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
        return fig
    
    # Extract merchants and amounts
    merchants = [merchant for merchant, _ in top_merchants]
    amounts = [amount for _, amount in top_merchants]
    
    # Create color gradient based on amounts
    color_scale = np.linspace(0.3, 1, len(merchants))
    bar_colors = [f'rgba({int(26)}, {int(115)}, {int(232)}, {alpha})' for alpha in color_scale]
    
    # Create figure
    fig = go.Figure()
    
    # Add horizontal bars
    fig.add_trace(go.Bar(
        y=merchants,
        x=amounts,
        orientation='h',
        marker=dict(
            color=bar_colors,
            line=dict(color=colors['dark'], width=1)
        ),
        hovertemplate='%{y}: £%{x:.2f}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        # title={
        #     'text': f"Top Merchants (Last {days} Days)",
        #     'y':0.95,
        #     'x':0.5,
        #     'xanchor': 'center',
        #     'yanchor': 'top',
        #     'font': {'size': 14}
        # },
        xaxis=dict(
            title=dict(
                text="Amount Spent (£)",
                font=dict(
                    family="Arial, sans-serif",
                    size=18,
                    color="gray"
                )
            ),
            tickprefix="£",
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=10)
        )
    )
    
    return fig

def generate_spending_trends(expenses_data, options):
    """Generate an area chart showing spending trends over time by category
    
    Parameters:
    - expenses_data: List of expense records from SQL database
    - options: Dictionary with chart customization options
    
    Returns:
    - Plotly figure object with stacked area chart of spending trends
    """
    default_colors = {
        'primary': '#1a73e8',
        'secondary': '#4285f4',
        'light': '#8ab4f8',
        'dark': '#174ea6',
        'background': '#f8f9fc',
        'text': '#202124'
    }
    
    # Use provided color scheme or fall back to default
    colors = options.get("color_scheme", default_colors)
    
    # Just in case the color_scheme is present but missing keys:
    for key, value in default_colors.items():
        colors.setdefault(key, value)
    
    # Get time frame - default to past 6 months
    months = options.get("months", 6)
    
    # Calculate cutoff date
    today = datetime.now()
    cutoff_date = today - timedelta(days=months*30)  # Approximate
    
    # Filter expenses within the time period
    filtered_expenses = []
    for expense in expenses_data:
        date = expense['date'] if isinstance(expense['date'], datetime) else datetime.fromisoformat(expense['date'].replace('Z', '+00:00'))
        if date >= cutoff_date:
            filtered_expenses.append(expense)
    
    if not filtered_expenses:
        # No data, return empty figure with message
        fig = go.Figure()
        fig.update_layout(
            annotations=[
                dict(
                    text="No expense data available for the selected period",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5
                )
            ],
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
        return fig
    
    # Classify expenses into major categories
    # For simplicity, let's use 3 major categories:
    # 1. Essentials (Housing, Utilities, Groceries, Transportation)
    # 2. Discretionary (Entertainment, Dining, Shopping, Travel)
    # 3. Financial (Savings, Investments, Debt payments)
    
    # Define category mappings (customize based on your actual categories)
    essential_categories = ['Housing', 'Utilities', 'Groceries', 'Transportation']
    discretionary_categories = ['Entertainment', 'Dining', 'Shopping', 'Travel', 'Restaurant']
    financial_categories = ['Savings', 'Investments', 'Debt']
    
    # Group expenses by month and category type
    monthly_data = {}
    
    for expense in filtered_expenses:
        date = expense['date'] if isinstance(expense['date'], datetime) else datetime.fromisoformat(expense['date'].replace('Z', '+00:00'))
        month_key = date.strftime('%Y-%m')
        category = expense['category'] if expense['category'] else 'Uncategorized'
        amount = float(expense['amount'])
        
        # Determine category type
        if any(cat.lower() in category.lower() for cat in essential_categories):
            category_type = 'Essentials'
        elif any(cat.lower() in category.lower() for cat in discretionary_categories):
            category_type = 'Discretionary'
        elif any(cat.lower() in category.lower() for cat in financial_categories):
            category_type = 'Financial'
        else:
            category_type = 'Other'
        
        # Initialize month data if not exists
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                'Essentials': 0,
                'Discretionary': 0,
                'Financial': 0,
                'Other': 0
            }
        
        # Accumulate the amount
        monthly_data[month_key][category_type] += amount
    
    # Sort months chronologically
    sorted_months = sorted(monthly_data.keys())
    
    # Prepare data for the area chart
    months_labels = [datetime.strptime(m, '%Y-%m').strftime('%b %Y') for m in sorted_months]
    essentials_data = [monthly_data[m]['Essentials'] for m in sorted_months]
    discretionary_data = [monthly_data[m]['Discretionary'] for m in sorted_months]
    financial_data = [monthly_data[m]['Financial'] for m in sorted_months]
    other_data = [monthly_data[m]['Other'] for m in sorted_months]
    
    # Create figure
    fig = go.Figure()
    
    # Add area traces
    fig.add_trace(go.Scatter(
        x=months_labels, y=essentials_data,
        mode='lines',
        line=dict(width=0.5, color=colors['dark']),
        stackgroup='one',
        groupnorm='percent',
        name='Essentials'
    ))
    
    fig.add_trace(go.Scatter(
        x=months_labels, y=discretionary_data,
        mode='lines',
        line=dict(width=0.5, color=colors['primary']),
        stackgroup='one',
        name='Discretionary'
    ))
    
    fig.add_trace(go.Scatter(
        x=months_labels, y=financial_data,
        mode='lines',
        line=dict(width=0.5, color=colors['secondary']),
        stackgroup='one',
        name='Financial'
    ))
    
    fig.add_trace(go.Scatter(
        x=months_labels, y=other_data,
        mode='lines',
        line=dict(width=0.5, color=colors['light']),
        stackgroup='one',
        name='Other'
    ))
    
    # Update layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode="x unified",
        xaxis=dict(tickfont=dict(size=10)),
        yaxis=dict(ticksuffix="%", tickfont=dict(size=10))
    )
    
    return fig

def generate_recurring_expenses(expenses_data, options):
    """Generate a visualization of recurring fixed expenses
    
    Parameters:
    - expenses_data: List of expense records from SQL database
    - options: Dictionary with chart customization options
    
    Returns:
    - Plotly figure object with recurring expenses visualization
    """
    from datetime import datetime
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    default_colors = {
        'primary': '#1a73e8',
        'secondary': '#4285f4',
        'light': '#8ab4f8',
        'dark': '#174ea6',
        'background': '#f8f9fc',
        'text': '#202124'
    }
    
    # Use provided color scheme or fall back to default
    colors = options.get("color_scheme", default_colors)
    
    # Just in case the color_scheme is present but missing keys:
    for key, value in default_colors.items():
        colors.setdefault(key, value)
    
    # Identify recurring expenses
    # Look for expenses with similar amounts and descriptions that occur regularly
    
    # Group expenses by description and amount (rounded to nearest dollar)
    expense_patterns = {}
    for expense in expenses_data:
        description = expense['description'].strip()
        amount = round(float(expense['amount']))  # Round to nearest dollar for pattern matching
        key = f"{description}_{amount}"
        
        if key in expense_patterns:
            expense_patterns[key]['occurrences'] += 1
            expense_patterns[key]['dates'].append(expense['date'] if isinstance(expense['date'], datetime) 
                                                else datetime.fromisoformat(expense['date'].replace('Z', '+00:00')))
            expense_patterns[key]['exact_amount'] = float(expense['amount'])  # Use most recent amount
        else:
            expense_patterns[key] = {
                'description': description,
                'amount': amount,
                'exact_amount': float(expense['amount']),
                'occurrences': 1,
                'dates': [expense['date'] if isinstance(expense['date'], datetime) 
                         else datetime.fromisoformat(expense['date'].replace('Z', '+00:00'))]
            }
    
    # Filter for likely recurring expenses (occurred at least twice)
    recurring_expenses = []
    for key, info in expense_patterns.items():
        if info['occurrences'] >= 2:
            # Check if it has occurred in at least 2 different months
            months = set(date.strftime('%Y-%m') for date in info['dates'])
            if len(months) >= 2:
                recurring_expenses.append({
                    'description': info['description'],
                    'amount': info['exact_amount'],
                    'occurrences': info['occurrences']
                })
    
    # Sort by amount (descending)
    recurring_expenses = sorted(recurring_expenses, key=lambda x: x['amount'], reverse=True)
    
    if not recurring_expenses:
        # No recurring expenses detected
        fig = go.Figure()
        fig.update_layout(
            annotations=[
                dict(
                    text="No recurring expenses detected",
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=0.5
                )
            ],
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
        return fig
    
    # Limit to top 5 recurring expenses
    top_recurring = recurring_expenses[:5]
    
    # Extract data for chart
    descriptions = [item['description'] for item in top_recurring]
    amounts = [item['amount'] for item in top_recurring]
    
    # Calculate monthly total
    monthly_total = sum(amounts)
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.1,
        specs=[[{"type": "domain"}], [{"type": "table"}]]
    )
    
    # Add pie chart
    fig.add_trace(
        go.Pie(
            labels=descriptions,
            values=amounts,
            hole=.4,
            marker=dict(
                colors=[colors['primary'], colors['secondary'], colors['light'], '#5c9ce5', '#7baef2']
            ),
            textinfo='percent',
            hoverinfo='label+value+percent',
            hovertemplate='%{label}: £%{value:.2f}<br>%{percent}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add table with just Expense and Amount (no Frequency)
    fig.add_trace(
        go.Table(
            header=dict(
                values=['Expense', 'Amount'],
                fill_color=colors['dark'],
                align='left',
                font=dict(color='white', size=10)
            ),
            cells=dict(
                values=[
                    descriptions,
                    ['£{:.2f}'.format(amount) for amount in amounts]
                ],
                fill_color=colors['background'],
                align='left',
                font=dict(color=colors['text'], size=10)
            )
        ),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        showlegend=False,
        annotations=[dict(text=f"£{monthly_total:.2f}/mo", x=0.5, y=0.5, font_size=18, showarrow=False)]
    )
    
    return fig

# Layout for the chat/AI dashboard page
# Layout for the chat/AI dashboard page
layout = html.Div([
    # Stores for maintaining state
    dcc.Store(id="session-data-store", storage_type="local"),
    dcc.Store(id='user-id-store', storage_type='local'),
    dcc.Store(id='user-id'),
    dcc.Store(id='user-data-store', storage_type='session'),
    dcc.Store(id='dashboard-settings-store', storage_type='local'),
    dcc.Store(id="dropdown-state", storage_type="memory", data=False),
    dcc.Store(id='layouts-store', storage_type='local'),
    dcc.Store(id='insights-modal-specific-store', storage_type='memory'),
    dcc.Store(id="temp-insight-store", storage_type="memory"),
    dcc.Location(id='url', refresh=True),
    
    # Page header with navigation
    html.Div([
        html.Img(src="/assets/Logo_slogan.PNG", className="dashboard-logo"),
        
        html.Nav([
            html.Button([
                html.Span("BlueCard Finance", className="mobile-nav-toggle-text"),
                html.Span("≡")
            ], className="mobile-nav-toggle", id="mobile-nav-toggle"),

            html.Ul([
                html.Li(html.A([html.Span(className="nav-icon"), "Home"], href="/", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "About"], href="/about", className="nav-link"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Chat"], href="/chat", className="nav-link active"), className="nav-item"),
                html.Li(html.A([html.Span(className="nav-icon"), "Pricing"], href="/pricing", className="nav-link"), className="nav-item"),
                # html.Li(html.A([html.Span(className="nav-icon"), "Dashboard"], href="/dashboard", className="nav-link"), className="nav-item"),
                # html.Li(html.A([html.Span(className="nav-icon"), "Income"], href="/income", className="nav-link"), className="nav-item"),
                # html.Li(html.A([html.Span(className="nav-icon"), "Expenses"], href="/expenses", className="nav-link"), className="nav-item"),
                # html.Li(html.A([html.Span(className="nav-icon"), "Savings Analysis"], href="/savings", className="nav-link"), className="nav-item"),
                
            ], className="nav-menu", id="nav-menu"),
            
            html.Div([
                html.Div([
                    html.Button([
                        html.I(className="fas fa-user-circle", style={'fontSize': '24px'}),
                    ], id="user-dropdown-button", className="user-dropdown-button"),
                    
                    html.Div([
                        html.Div(id="user-email-display", className="user-email"),
                        html.Hr(style={'margin': '8px 0'}),
                        html.A("Profile", href="/profile", className="dropdown-item"),
                        html.A("Logout", id="logout-link", href="/logout", className="dropdown-item")
                    ], id="user-dropdown-content", className="user-dropdown-content")
                ], className="user-dropdown"),
            ], id="user-account-container", className="user-account-container"),
        ], className="nav-bar"),
    ], className="header-container"),
    
    # Main content area
    html.Div([
        # Sidebar for chat/AI interaction - Premium Version
        html.Div([
            # Premium badge and title
            html.Div([
                html.Div([
                    # html.I(className="fas fa-robot", style={
                    #     "color": "#0052CC",
                    #     "fontSize": "20px",
                    #     "marginRight": "10px"
                    # }),
                    html.H2("BlueCard AI", className="sidebar-title", style={
                        "color": "#0A2540",
                        "fontWeight": "600",
                        "fontSize": "1.5rem",
                        "marginLeft": "40px"
                    })
                ], style={"display": "flex", "alignItems": "center"}),
                # html.Div([
                #     html.Span("ELITE", className="ai-badge", style={
                #         "backgroundColor": "#0A2540",
                #         "color": "white",
                #         "padding": "4px 8px",
                #         "borderRadius": "20px",
                #         "fontSize": "0.7rem",
                #         "fontWeight": "600",
                #         "letterSpacing": "1px"
                #     })
                # ])
            ], style={
                "display": "flex", 
                "justifyContent": "space-between", 
                "alignItems": "center",
                "marginBottom": "5px"
            }),
            
            # Premium AI description
            html.P([
                "Your advanced financial intelligence assistant. Ask anything about your portfolio, investments, or financial planning.",
            ], className="sidebar-description", style={
                "color": "#4A5568",
                "lineHeight": "1.5",
                "fontSize": "0.95rem",
                "marginBottom": "20px"
            }),
            
            # Premium chat features description
            html.Div([
                html.Div([
                    html.I(className="fas fa-chart-line", style={"color": "#0052CC"}),
                    html.Span("In-Depth Analysis", style={"marginLeft": "10px", "fontWeight": "500"})
                ], style={"marginBottom": "8px"}),
                # html.Div([
                #     html.I(className="fas fa-lock", style={"color": "#0052CC"}),
                #     html.Span("Exclusive Insights", style={"marginLeft": "10px", "fontWeight": "500"})
                # ], style={"marginBottom": "8px"}),
                html.Div([
                    html.I(className="fas fa-bolt", style={"color": "#0052CC"}),
                    html.Span("Predictive Intelligence", style={"marginLeft": "10px", "fontWeight": "500"})
                ])
            ], className="premium-features", style={
                "padding": "15px",
                "backgroundColor": "rgba(0, 82, 204, 0.05)",
                "borderRadius": "8px",
                "fontSize": "0.9rem",
                "color": "#2D3748",
                "marginBottom": "20px",
                "border": "1px solid rgba(0, 82, 204, 0.1)"
            }),
            
            # Enhanced chat history
            html.Div(id="chat-history", className="chat-history", style={
                "backgroundColor": "#FFFFFF",
                "borderRadius": "8px",
                "padding": "15px",
                "height": "calc(100vh - 380px)",
                "overflowY": "auto",
                "border": "1px solid rgba(203, 213, 224, 0.5)",
                "boxShadow": "inset 0 2px 4px rgba(0,0,0,0.03)"
            }),
            
            # Premium chat input container
            html.Div([
                dcc.Input(
                    id="chat-input", 
                    type="text", 
                    placeholder="Ask your financial advisor...", 
                    className="chat-input",
                    style={
                        "width": "100%",
                        "padding": "12px 15px",
                        "borderRadius": "8px",
                        "border": "1px solid rgba(203, 213, 224, 0.7)",
                        "fontSize": "0.95rem",
                        "backgroundColor": "#FFFFFF",
                        "boxShadow": "inset 0 2px 4px rgba(0,0,0,0.03)"
                    }
                ),
                html.Button(
                    [html.I(className="fas fa-paper-plane")], 
                    id="send-chat", 
                    className="send-chat-button",
                    style={
                        "backgroundColor": "#0052CC",
                        "color": "white",
                        "border": "none",
                        "borderRadius": "8px",
                        "padding": "12px 18px",
                        "marginLeft": "10px",
                        "cursor": "pointer",
                        "transition": "all 0.2s ease",
                        "boxShadow": "0 2px 5px rgba(0, 82, 204, 0.2)"
                    }
                )
            ], className="chat-input-container", style={
                "display": "flex", 
                "alignItems": "center",
                "marginTop": "15px",
            }),
            
            # # Premium badge at the bottom
            # html.Div([
            #     html.Div([
            #         html.I(className="fas fa-shield-alt", style={
            #             "color": "#0052CC",
            #             "fontSize": "16px",
            #             "marginRight": "8px"
            #         }),
            #         html.Span("BlueCard Premium", style={
            #             "fontWeight": "600", 
            #             "color": "#0A2540",
            #             "fontSize": "0.9rem"
            #         })
            #     ], style={"display": "flex", "alignItems": "center"})
            # ], style={
            #     "marginTop": "25px",
            #     "textAlign": "center",
            #     "padding": "10px",
            #     "backgroundColor": "rgba(0, 82, 204, 0.05)",
            #     "borderRadius": "8px",
            #     "border": "1px solid rgba(0, 82, 204, 0.1)"
            # })
        ], className="chat-sidebar", style={
            "borderRadius": "12px",
            "backgroundColor": "#F8FAFC",
            "padding": "25px",
            "boxShadow": "0 10px 25px rgba(0, 0, 0, 0.05)",
            "border": "1px solid rgba(203, 213, 224, 0.5)",
            "marginLeft": "20px",
            "marginTop": "1px"    # Optional: adjust this to reduce top gap
        }),

        # Dashboard main area
        html.Div([
            # Dashboard header that will only show if dashboard has components
            html.Div([
                html.H1("Your Financial Dashboard", className="dashboard-title"),
                html.Div(id="last-updated", className="last-updated")
            ], className="dashboard-header", id="dashboard-header-section", style={"display": "none"}),
            
            # For new users (Welcome Page) - PREMIUM VERSION
            html.Div([
                # Main container with premium styling
                html.Div([
                    # Top accent bar with premium gradient
                    html.Div(className="premium-accent-bar", style={
                        "height": "6px",
                        "background": "linear-gradient(90deg, #0A2540 0%, #0052CC 35%, #00C7FA 100%)",
                        "borderRadius": "4px 4px 0 0",
                        "marginBottom": "2px"
                    }),
                    
                    # Header section with logo, title and premium badge
                    html.Div([
                        html.Div([
                            html.Img(src="/assets/Logo_slogan.png", className="welcome-logo"),
                            html.Div([
                                html.H2("Welcome to BlueCard Finance", className="welcome-title", style={
                                    "fontWeight": "600",
                                    "color": "#0A2540",
                                    "marginBottom": "4px"
                                }),
                                html.P("Premium Financial Intelligence", style={
                                    "fontSize": "1.1rem",
                                    "color": "#4A5568",
                                    "letterSpacing": "0.5px",
                                    "margin": "0"
                                }),
                            ], className="welcome-title-container")
                        ], className="welcome-header-left", style={"display": "flex", "alignItems": "center", "gap": "20px"}),
                        
                        # html.Div([
                        #     html.Span("PREMIUM", className="premium-badge", style={
                        #         "backgroundColor": "#0A2540",
                        #         "color": "white",
                        #         "padding": "6px 12px",
                        #         "borderRadius": "20px",
                        #         "fontSize": "0.8rem",
                        #         "fontWeight": "600",
                        #         "letterSpacing": "1px",
                        #         "display": "inline-flex",
                        #         "alignItems": "center",
                        #         "boxShadow": "0 2px 10px rgba(10, 37, 64, 0.2)"
                        #     }),
                        # ], className="welcome-header-right")
                    ], className="welcome-header", style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                        "paddingBottom": "15px",
                        "borderBottom": "1px solid rgba(10, 37, 64, 0.1)"
                    }),
                    
                    # Main content area
                    html.Div([
                        # Left side - Enhanced Video with frame
                        html.Div([
                            html.Div([
                                html.Video(
                                    controls=True,
                                    src="/assets/welcome_video.mp4",  # Update this path to your actual video file
                                    className="welcome-video",
                                    autoPlay=False,
                                    style={
                                        "width": "100%",
                                        "borderRadius": "4px",
                                        "boxShadow": "0 10px 25px rgba(0,0,0,0.1)"
                                    }
                                ),
                                html.Div(className="video-frame-accent", style={
                                    "position": "absolute",
                                    "bottom": "-10px",
                                    "right": "-10px",
                                    "width": "80%",
                                    "height": "80%",
                                    "border": "2px solid #0052CC",
                                    "borderRadius": "4px",
                                    "zIndex": "-1"
                                })
                            ], className="video-container", style={
                                "position": "relative",
                                "margin": "20px 0"
                            }),
                            
                            # Video testimonial note
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-quote-left", style={
                                        "color": "#0052CC",
                                        "fontSize": "24px",
                                        "marginRight": "10px"
                                    })
                                ], style={"marginBottom": "8px"}),
                                html.P("BlueCard Finance transformed how I manage my wealth. The insights are incredible.", style={
                                    "fontStyle": "italic",
                                    "marginBottom": "10px",
                                    "color": "#4A5568"
                                }),
                                html.Div([
                                    html.Span("James Harrington", style={
                                        "fontWeight": "600",
                                        "color": "#0A2540"
                                    }),
                                    html.Span(" • ", style={"color": "#CBD5E0"}),
                                    html.Span("CEO, Harrington Ventures", style={
                                        "color": "#718096",
                                        "fontSize": "0.9rem"
                                    })
                                ])
                            ], className="video-testimonial", style={
                                "padding": "20px",
                                "backgroundColor": "#F7FAFC",
                                "borderRadius": "4px",
                                "borderLeft": "3px solid #0052CC",
                                "marginTop": "25px"
                            })
                        ], className="welcome-visual"),
                        
                        # Right side - Getting started content with premium feel
                        html.Div([
                            html.Div([
                                html.H3("Elite Financial Management", className="getting-started-title", style={
                                    "color": "#0A2540",
                                    "fontSize": "1.5rem",
                                    "fontWeight": "600",
                                    "marginBottom": "8px"
                                }),
                                html.P("Harness the power of premium financial intelligence with your personal AI assistant.", 
                                    className="getting-started-subtitle", style={
                                        "color": "#4A5568",
                                        "fontSize": "1rem",
                                        "marginBottom": "24px"
                                    }),
                                
                                # Premium features list
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-check-circle", style={
                                            "color": "#0052CC",
                                            "fontSize": "16px"
                                        }),
                                        html.Span("Advanced financial insights", style={
                                            "marginLeft": "10px",
                                            "color": "#2D3748"
                                        })
                                    ], className="premium-feature"),
                                    html.Div([
                                        html.I(className="fas fa-check-circle", style={
                                            "color": "#0052CC",
                                            "fontSize": "16px"
                                        }),
                                        html.Span("Personalized wealth strategies", style={
                                            "marginLeft": "10px",
                                            "color": "#2D3748"
                                        })
                                    ], className="premium-feature"),
                                    html.Div([
                                        html.I(className="fas fa-check-circle", style={
                                            "color": "#0052CC",
                                            "fontSize": "16px"
                                        }),
                                        html.Span("Real-time market analysis", style={
                                            "marginLeft": "10px",
                                            "color": "#2D3748"
                                        })
                                    ], className="premium-feature"),
                                ], className="premium-features-list", style={
                                    "display": "flex",
                                    "flexDirection": "column",
                                    "gap": "12px",
                                    "marginBottom": "30px"
                                })
                            ], className="premium-introduction", style={
                                "marginBottom": "30px"
                            }),
                            
                            html.H3("Start Your Financial Journey", className="getting-started-title", style={
                                "color": "#0A2540",
                                "fontSize": "1.2rem",
                                "fontWeight": "600",
                                "marginBottom": "15px"
                            }),
                            
                            # Command cards - visual, engaging way to show commands with premium styling
                            html.Div([
                                # Income card
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.I(className="fas fa-plus-circle command-icon", style={
                                                "color": "#0052CC",
                                                "fontSize": "18px"
                                            }),
                                        ], style={
                                            "width": "34px",
                                            "height": "34px",
                                            "borderRadius": "50%",
                                            "backgroundColor": "rgba(0, 82, 204, 0.1)",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center"
                                        }),
                                        html.Span("Add Income", className="command-label", style={
                                            "fontWeight": "600",
                                            "color": "#0A2540"
                                        })
                                    ], className="command-header"),
                                    html.P("\"I want to add to my income\"", className="command-example", style={
                                        "color": "#718096",
                                        "margin": "8px 0"
                                    }),
                                    html.Button("Try It", id="try-income-cmd", className="try-command-btn", style={
                                        "backgroundColor": "#0052CC",
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "4px",
                                        "padding": "8px 16px",
                                        "cursor": "pointer",
                                        "fontWeight": "500",
                                        "transition": "all 0.2s ease"
                                    })
                                ], className="command-card", style={
                                    "width": "100%",
                                    "maxWidth": "500px",
                                    "padding": "20px",
                                    "backgroundColor": "white",
                                    "borderRadius": "8px",
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
                                    "transition": "transform 0.2s ease, box-shadow 0.2s ease",
                                    "border": "1px solid rgba(203, 213, 224, 0.5)",
                                    "marginRight": "5px"
                                }),
                                
                                # Expense card
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.I(className="fas fa-minus-circle command-icon", style={
                                                "color": "#0052CC",
                                                "fontSize": "18px"
                                            }),
                                        ], style={
                                            "width": "34px",
                                            "height": "34px",
                                            "borderRadius": "50%",
                                            "backgroundColor": "rgba(0, 82, 204, 0.1)",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center"
                                        }),
                                        html.Span("Add Expense", className="command-label", style={
                                            "fontWeight": "600",
                                            "color": "#0A2540"
                                        })
                                    ], className="command-header"),
                                    html.P("\"I want to add an expense\"", className="command-example", style={
                                        "color": "#718096",
                                        "margin": "8px 0"
                                    }),
                                    html.Button("Try It", id="try-expense-cmd", className="try-command-btn", style={
                                        "backgroundColor": "#0052CC",
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "4px",
                                        "padding": "8px 16px",
                                        "cursor": "pointer",
                                        "fontWeight": "500",
                                        "transition": "all 0.2s ease"
                                    })
                                ], className="command-card", style={
                                    "padding": "20px",
                                    "backgroundColor": "white",
                                    "borderRadius": "8px",
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
                                    "transition": "transform 0.2s ease, box-shadow 0.2s ease",
                                    "border": "1px solid rgba(203, 213, 224, 0.5)"
                                }),
                                
                                # View breakdown card
                                html.Div([
                                    html.Div([
                                        html.Div([
                                            html.I(className="fas fa-chart-pie command-icon", style={
                                                "color": "#0052CC",
                                                "fontSize": "18px"
                                            }),
                                        ], style={
                                            "width": "34px",
                                            "height": "34px",
                                            "borderRadius": "50%",
                                            "backgroundColor": "rgba(0, 82, 204, 0.1)",
                                            "display": "flex",
                                            "alignItems": "center",
                                            "justifyContent": "center"
                                        }),
                                        html.Span("View Reports", className="command-label", style={
                                            "fontWeight": "600",
                                            "color": "#0A2540"
                                        })
                                    ], className="command-header"),
                                    html.P("\"I want my income breakdown\"", className="command-example", style={
                                        "color": "#718096",
                                        "margin": "8px 0"
                                    }),
                                    html.Button("Try It", id="try-breakdown-cmd", className="try-command-btn", style={
                                        "backgroundColor": "#0052CC",
                                        "color": "white",
                                        "border": "none",
                                        "borderRadius": "4px",
                                        "padding": "8px 16px",
                                        "cursor": "pointer",
                                        "fontWeight": "500",
                                        "transition": "all 0.2s ease"
                                    })
                                ], className="command-card", style={
                                    "padding": "20px",
                                    "backgroundColor": "white",
                                    "borderRadius": "8px",
                                    "boxShadow": "0 4px 12px rgba(0,0,0,0.05)",
                                    "transition": "transform 0.2s ease, box-shadow 0.2s ease",
                                    "border": "1px solid rgba(203, 213, 224, 0.5)"
                                }),
                            ], className="command-cards-container", style={
                                "display": "grid",
                                "gridTemplateColumns": "repeat(auto-fit, minmax(250px, 1fr))",
                                "gap": "16px",
                                "marginBottom": "24px"
                            }),
                            
                            # Quick tip section with premium styling
                            html.Div([
                                html.Div([
                                    html.Div([
                                        html.I(className="fas fa-lightbulb tip-icon", style={
                                            "color": "#FDBA74",
                                            "fontSize": "18px"
                                        })
                                    ], style={
                                        "width": "32px",
                                        "height": "32px",
                                        "borderRadius": "50%",
                                        "backgroundColor": "rgba(251, 211, 141, 0.2)",
                                        "display": "flex",
                                        "alignItems": "center",
                                        "justifyContent": "center",
                                        "marginRight": "12px"
                                    }),
                                    html.Span("EXPERT TIP", className="tip-label", style={
                                        "fontWeight": "600",
                                        "color": "#0A2540",
                                        "letterSpacing": "0.5px",
                                        "fontSize": "0.9rem"
                                    })
                                ], style={"display": "flex", "alignItems": "center"}),
                                html.P("Ask advanced questions like \"What's my financial health?\" or \"How can I optimize my investment portfolio?\"", 
                                    className="tip-text", style={
                                        "margin": "10px 0 0 44px",
                                        "color": "#4A5568"
                                    })
                            ], className="quick-tip", style={
                                "padding": "16px",
                                "backgroundColor": "#FFFAF0",
                                "borderRadius": "8px",
                                "marginTop": "10px",
                                "border": "1px solid #FEEBC8"
                            }),
                        ], className="welcome-content")
                    ], className="welcome-main-content", style={
                        "display": "grid",
                        "gridTemplateColumns": "45% 55%",
                        "gap": "20px",
                        "marginTop": "1px"
                    }),
                    
                    # Bottom accent bar
                    html.Div(className="premium-accent-bar", style={
                        "height": "6px",
                        "background": "linear-gradient(90deg, #00C7FA 0%, #0052CC 65%, #0A2540 100%)",
                        "borderRadius": "0 0 4px 4px",
                        "marginTop": "40px"
                    }),
                ], className="welcome-container", style={
                    "backgroundColor": "#FFFFFF",
                    "borderRadius": "8px",
                    "boxShadow": "0 10px 30px rgba(0, 0, 0, 0.08)",
                    "padding": "0 0 2px 0",  # Minimal padding to show accent bars
                    "marginBottom": "40px",
                    "border": "1px solid rgba(203, 213, 224, 0.5)"
                })
            ], id="empty-dashboard-state", className="premium-welcome-page", style={
                "margin": "20px 0"
            }),

            # Dashboard grid (updated to dash_draggable)
            html.Div([
                dash_draggable.ResponsiveGridLayout(
                    id="dashboard-grid",
                    children=[],
                    layouts={},
                    isDraggable=True,
                    isResizable=True,
                    preventCollision=True,
                    compactType=None,
                    breakpoints={"lg": 1200, "md": 996, "sm": 768, "xs": 480, "xxs": 0},
                    gridCols={"lg": 12, "md": 10, "sm": 6, "xs": 4, "xxs": 2},
                    style={"backgroundColor": "#f8f9fa", "minHeight": "600px"},  # removed height: 100%
                    save=True
                )
            ], style={"marginBottom": "100px", "paddingBottom": "100px"})
        ], className="dashboard-main"),
    ], className="chat-dashboard-container"),

    # Empty spacer div
    html.Div(style={"height": "100px"}),  # This creates 100px of empty space

    # Modals
    dbc.Modal([
        dbc.ModalHeader("Income Management"),
        dbc.ModalBody([
            html.Iframe(
                id="income-page-iframe",
                src="",
                style={"width": "100%", "height": "70vh", "border": "none"},
            )
        ]),
        dbc.ModalFooter([
            dbc.Button("Close", id="close-income-modal", className="ml-auto")
        ])
    ], id="income-page-modal", size="xl", className="custom-modal"),

    dbc.Modal([
        dbc.ModalHeader("Expense Management"),
        dbc.ModalBody([
            html.Iframe(
                id="expenses-page-iframe",
                src="",
                style={"width": "100%", "height": "70vh", "border": "none"},
            )
        ]),
        dbc.ModalFooter([
            dbc.Button("Close", id="close-expenses-modal", className="ml-auto")
        ])
    ], id="expenses-page-modal", size="xl", className="custom-modal"),
    
    dbc.Modal([
        dbc.ModalHeader("Add Component to Dashboard"),
        dbc.ModalBody([
            html.P("Do you want to add this chart to your dashboard?"),
            html.Div(id="preview-component", className="preview-component")
        ]),
        dbc.ModalFooter([
            dbc.Button("Cancel", id="add-component-cancel", className="mr-2"),
            dbc.Button("Add to Dashboard", id="add-component-confirm", color="primary")
        ])
    ], id="add-component-modal"),

    # Add these new components to your layout
    dcc.Store(id='insights-specific-store', storage_type='memory'),
    html.Div([
        dbc.Modal([
            dbc.ModalHeader("Income Insights", id="insights-specific-modal-header"),
            dbc.ModalBody(id="insights-specific-modal-content", className="insights-modal-content-wide"),
            dbc.ModalFooter([
                dbc.Button("Close", id="close-insights-specific-modal", className="ml-auto")
            ])
        ], id="insights-specific-modal", size="xl", is_open=False, className="custom-modal")
    ]),

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
}),

    html.Div(id="listener-setup-trigger-div", style={"display": "none"}),
    html.Div(id="dashboard-event-trigger", style={"display": "none"}),

    dcc.Store(id='dashboard-position-store', storage_type='memory'),
    dcc.Interval(id='layout-update-interval', interval=1000, n_intervals=0),
    dcc.Store(id="insights-charts-store", storage_type="memory"),
    dcc.Store(id="current-chart-store", storage_type="memory"),
    dcc.Store(id="insights-modal-store", data={"open": False}),
    
    # Add a callback trigger to handle the dashboard state display toggling
    dcc.Store(id="dashboard-has-components", storage_type="memory", data=False)
], className="chat-page-container")

# Add this callback to toggle dashboard header visibility based on whether components exist
@callback(
    [Output("dashboard-header-section", "style"),
     Output("dashboard-has-components", "data")],
    [Input("dashboard-grid", "children")],
    [State("dashboard-has-components", "data")]
)
def toggle_dashboard_header(dashboard_children, current_state):
    """
    Toggle the dashboard header visibility based on whether there are components
    in the dashboard grid.
    """
    # Check if dashboard has components
    has_components = len(dashboard_children) > 0 if dashboard_children else False
    
    # Set the display style for dashboard header
    header_style = {"display": "block"} if has_components else {"display": "none"}
    
    # Return the style and update the state store
    return header_style, has_components

# Handle chat input
@callback(
    [
        Output("chat-history", "children"),
        Output("current-chart-store", "data", allow_duplicate=True),
        Output("preview-component", "children"),
        Output("add-component-modal", "is_open", allow_duplicate=True),
        Output("insights-modal-store", "data", allow_duplicate=True),  # Keep original for compatibility
        Output("insights-specific-store", "data")  # Add new specific store
    ],
    [
        Input("send-chat", "n_clicks"),
        Input("chat-input", "n_submit"),
        Input("try-income-cmd", "n_clicks"),
        Input("try-expense-cmd", "n_clicks"),
        Input("try-breakdown-cmd", "n_clicks")
    ],
    [
        State("chat-input", "value"),
        State("chat-history", "children"),
        State("user-data-store", "data"),
        State("current-chart-store", "data")
    ],
    prevent_initial_call=True
)
def handle_chat_input(n_clicks, n_submit, try_income, try_expense, try_breakdown, input_value, current_chat, user_data, current_chart_data):
    """Process user input and generate AI response with charts."""
    ctx = dash.callback_context
    
    # If there's no triggered input, return current state
    if not ctx.triggered:
        return current_chat or [], dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
    # Determine which button triggered the callback
    triggered_button = ctx.triggered[0]['prop_id'].split('.')[0]

    # Handle button-specific actions
    if triggered_button == "try-income-cmd":
        user_message = "I want to add to my income"
    elif triggered_button == "try-expense-cmd":
        user_message = "I want to add an expense"
    elif triggered_button == "try-breakdown-cmd":
        user_message = "I want my income breakdown"
    else:
        if not input_value:
            return current_chat or [], dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
        user_message = input_value
    
    # Initialize chat history if needed
    if not current_chat:
        current_chat = []
    
    # Add user message to chat
    user_message_div = html.Div([html.Div(user_message, className="user-message-content")], className="user-message")
    current_chat.append(user_message_div)
    
    # Process the query and generate response
    print(f"Processing user message: '{user_message}'")
    ai_message, chart_component, chart_data, modal_flags = process_chat_query(user_message, user_data)
    
    # Initialize output values
    insights_modal_data = dash.no_update
    insights_specific_data = dash.no_update
    add_component_modal_open = dash.no_update
    preview = dash.no_update
    
    # Add AI response to chat
    ai_message_div = html.Div([  
        html.Img(src="/assets/avatar.png", className="ai-avatar"),
        html.Div([  
            html.Div(ai_message, className="ai-message-content"),
            html.Div(chart_component, className="ai-chart-container") if chart_component else None
        ], className="ai-message-wrapper")
    ], className="ai-message")
    current_chat.append(ai_message_div)
    
    # Generate preview component if chart exists
    if chart_component and chart_data:
        print(f"Generating preview for chart type: {chart_data.get('type')}")
        preview = chart_component
    
    # Handle modal flags if present
    if modal_flags is not None:
        if 'open_insights_modal' in modal_flags and modal_flags['open_insights_modal']:
            print("Setting insights specific modal to open")
            insights_specific_data = {
                "open": True, 
                "type": modal_flags.get("insight_type", "income_analysis"),
                "timestamp": datetime.now().isoformat()  # Add timestamp to ensure uniqueness
            }
            insights_modal_data = {"open": True, "type": modal_flags.get("insight_type", "income_analysis")}
            add_component_modal_open = False
            chart_data = None  # Don't update chart data when opening insights modal
        elif 'open_income_modal' in modal_flags:
            print("Setting income management modal to open")
            add_component_modal_open = False
            insights_modal_data = {"open": False}
            insights_specific_data = dash.no_update
            chart_data = modal_flags  # Pass flags to chart store
        
        elif 'open_expense_modal' in modal_flags:
            print("Setting expense management modal to open")
            add_component_modal_open = False
            insights_modal_data = {"open": False}
            insights_specific_data = dash.no_update
            chart_data = modal_flags  # Pass flags to chart store
    
    print(f"Final return values: chart_data={chart_data}, modal={add_component_modal_open}, " + 
          f"insights_modal={insights_modal_data}, insights_specific={insights_specific_data}")
    
    return current_chat, chart_data, preview, add_component_modal_open, insights_modal_data, insights_specific_data

def process_chat_query(query, user_data):
    """Process the user query and generate appropriate response and chart"""
    query = query.lower().strip()
    income_data = user_data.get('income', [])
    
    # First, check if it's a general income question that should open the insights modal
    # Place this check BEFORE other income-related checks
    if any(pattern in query for pattern in [
        "what's my income", 
        "what is my income",
        "show me my income",
        "how much do i earn",
        "income breakdown",
        "income overview",
        "tell me about my income"
    ]):
        print('Generating Deep Income Analysis for insights modal')
        message = "I've prepared a detailed income analysis for you with multiple visualizations. You can view these charts and add any of them to your dashboard."
        
        # Return a signal to open the income insights modal with multiple charts
        return message, None, None, {"open_insights_modal": True, "insight_type": "income_analysis"}
    
    # Check for explicit requests to view or manage income
    if any(phrase in query for phrase in [
            "add to my income", 
            "manage income",
            "edit my income",
            "manage my income",
            "I want to add to my income"
        ]):
        # Return a flag to open the income modal
        message = "I'll open the income management page for you where you can view and edit your income details."
        return message, None, None, {"open_income_modal": True}

    # Check for explicit requests to view or manage expenses ( THIS OPENS EXPENSE PAGE)
    elif any(phrase in query for phrase in [
            "add to my expenses",
            "add an expense", 
            "manage expenses",
            "edit my expenses",
            "manage my expenses"
        ]):
        # Return a flag to open the income modal
        message = "I'll open the expenses management page for you where you can view and edit your income details."
        return message, None, None, {"open_expense_modal": True}
    
    # ( THIS OPEN EXPENSE CHARTS)
    elif any(phrase in query for phrase in [
            "what's my expenses", 
            "what is my expense",
            "show me my expenses",
            "how much do i spend",
            "expense breakdown",
            "expense overview",
            "tell me about my expenses"
        ]):
        # Return a flag to open the income modal
        message = "I'll open the expenses management page for you where you can view and edit your income details."
        return message, None, None, {"open_insights_modal": True, "insight_type": "expenses_analysis"}
    
    # Handle general financial advice
    elif any(keyword in query for keyword in ["advice", "tip", "suggestion", "recommend"]):
        message = """
        Here are some financial tips based on best practices:
        
        1. Aim to save at least 20% of your income
        2. Build an emergency fund covering 3-6 months of expenses
        3. Pay off high-interest debt first
        4. Take advantage of employer retirement matching
        5. Review your budget regularly
        
        Would you like me to create a specific chart or analysis to help with any of these areas?
        """
        
        return message, None, None, None
    
    # Default response for other queries
    else:
        message = """
        I can help you analyze your finances in various ways. You can ask me to:
        
        • Show income forecasts (as line, bar, or area charts)
        • Create expense breakdowns (as pie or bar charts)
        • Analyze savings goals
        • Calculate budget recommendations
        • Compare spending patterns
        
        Try asking about your income or expenses to get started!
        """
        
        return message, None, None, None

# Fix for the add_component_to_dashboard function
@callback(
    [
        Output("dashboard-settings-store", "data", allow_duplicate=True),
        Output("empty-dashboard-state", "style", allow_duplicate=True),
        Output("dashboard-grid", "children", allow_duplicate=True),
        Output("dashboard-grid", "layouts", allow_duplicate=True),
        Output("add-component-modal", "is_open", allow_duplicate=True),
        Output("current-chart-store", "data", allow_duplicate=True)
    ],
    [Input("add-component-confirm", "n_clicks")],
    [
        State("current-chart-store", "data"),
        State("dashboard-settings-store", "data"),
        State("user-data-store", "data"),
        State("dashboard-grid", "children"),
        State("dashboard-grid", "layouts")
    ],
    prevent_initial_call=True
)
def add_component_to_dashboard(n_clicks, chart_data, current_settings, user_data, current_children, current_layouts):
    # Make a deep copy to avoid modifying the input state
    current_layouts = copy.deepcopy(current_layouts)

    ctx = dash.callback_context
    if not ctx.triggered or not n_clicks or not chart_data:
        raise PreventUpdate
    
    if not current_settings:
        current_settings = {'components': []}
    if not isinstance(current_settings, dict):
        current_settings = {'components': []}
    if 'components' not in current_settings:
        current_settings['components'] = []

    # Standard dimensions for all components
    component_width = 8
    component_height = 6

     # Add debugging
    # print(f"DEBUG: Adding new component with standard width={component_width}, height={component_height}")
    
    next_position = find_next_available_position(current_settings)
    component_id = str(uuid.uuid4())

    # print(f"DEBUG: Component position: x={next_position['x']}, y={next_position['y']}")
    
    new_component = {
        'id': component_id,
        'type': chart_data['type'],
        'title': chart_data['title'],
        'position': {
            'x': next_position['x'],
            'y': next_position['y'],
            'w': component_width,  # Consistent width
            'h': component_height  # Consistent height
        },
        'settings': chart_data.get('settings', {})
    }

    if chart_data['type'] == 'income_forecast' and 'months_ahead' in chart_data:
        new_component['settings']['months_ahead'] = chart_data['months_ahead']
    
    current_settings['components'].append(new_component)

    # --- Add new layout consistently for all breakpoints ---
    for breakpoint in current_layouts.keys():
        # Set width based on breakpoint to make it responsive
        bp_width = component_width
        if breakpoint == 'xs':
            bp_width = 4  # Smaller for phones
        elif breakpoint == 'sm':
            bp_width = 6  # Medium for tablets

        # print(f"DEBUG: Adding layout for breakpoint '{breakpoint}': width={bp_width}, height={component_height}")
            
        current_layouts[breakpoint].append({
            'i': component_id,
            'x': next_position['x'],
            'y': next_position['y'],
            'w': bp_width,
            'h': component_height,
            'minW': 4,  # Minimum width constraint
            'minH': 4   # Minimum height constraint
        })

    # # print final layout after adding component
    # print(f"DEBUG: Final layouts: {json.dumps(current_layouts)}")

    # Generate components with the updated settings
    components, _ = generate_dashboard_components(current_settings, user_data)

    # Save if user is not guest
    user_id = user_data.get('user_info', {}).get('id')
    if user_id and user_id != 'Guest':
        save_dashboard_settings_to_db(user_id, current_settings)

    empty_style = {"display": "none"}
    
    return current_settings, empty_style, components, current_layouts, False, no_update

# Remove dashboard component
@callback(
    [
        Output("dashboard-settings-store", "data", allow_duplicate=True),
        Output("empty-dashboard-state", "style", allow_duplicate=True),
        Output("dashboard-grid", "children", allow_duplicate=True),
        Output("dashboard-grid", "layouts", allow_duplicate=True)
    ],
    [Input({"type": "remove-component", "index": ALL}, "n_clicks")],
    [
        State({"type": "remove-component", "index": ALL}, "id"),
        State("dashboard-settings-store", "data"),
        State("user-data-store", "data"),
        State("dashboard-grid", "layouts")
    ],
    prevent_initial_call=True
)
def remove_dashboard_component(n_clicks_list, id_list, current_settings, user_data, current_layouts):
    ctx = dash.callback_context
    if not ctx.triggered or not any(n for n in n_clicks_list if n):
        raise PreventUpdate
    
    # Identify which component (chart) to remove based on the button click
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    clicked_id = json.loads(button_id)['index']

    # --- Remove the selected component from the settings (components) ---
    if current_settings and 'components' in current_settings:
        current_settings['components'] = [
            comp for comp in current_settings['components'] if comp['id'] != clicked_id
        ]
    
    # --- Remove the corresponding layout item for each breakpoint ---
    for breakpoint in current_layouts.keys():
        current_layouts[breakpoint] = [
            item for item in current_layouts[breakpoint] if item['i'] != clicked_id
        ]

    # Check if dashboard is empty
    is_empty = not current_settings or 'components' not in current_settings or len(current_settings['components']) == 0
    empty_style = {"display": "block"} if is_empty else {"display": "none"}

    # --- Regenerate only components ---
    components, _ = generate_dashboard_components(current_settings, user_data)

    # Reset layouts if dashboard becomes empty
    if is_empty:
        current_layouts = {'lg': [], 'md': [], 'sm': [], 'xs': []}

    # Save the settings to the database if not a guest user
    if user_data.get('user_info', {}).get('user_id') != 'Guest':
        save_dashboard_settings_to_db(user_data['user_info']['user_id'], current_settings)

    return current_settings, empty_style, components, current_layouts


# Fix for the generate_dashboard_components function
def generate_dashboard_components(settings, user_data):
    """Generate dashboard components from settings"""
    # print(f"DEBUG: Generating dashboard components from settings: {settings}")
    
    if not settings or 'components' not in settings:
        # print("DEBUG: No components in settings")
        return [], {'lg': [], 'md': [], 'sm': [], 'xs': []}
    
    components = []
    layouts = {'lg': [], 'md': [], 'sm': [], 'xs': []}

    # Ensure consistent size is applied to all components
    component_width = 8  # Standard width
    component_height = 6  # Standard height
    
    # print(f"DEBUG: Standard component dimensions: {component_width}x{component_height}")

    # Get user data
    income_data = user_data.get('income', [])
    expense_data = user_data.get('expenses', [])
    
    # print(f"DEBUG: Processing {len(settings['components'])} components")
    
    for idx, component in enumerate(settings['components']):
        component_id = component['id']
        component_type = component.get('type', 'unknown')
        component_title = component.get('title', 'Untitled Component')
        component_settings = component.get('settings', {})
        
        # Get position with standard dimensions if missing
        position = component.get('position', {})
        x = position.get('x', 0)
        y = position.get('y', 0)
        w = position.get('w', component_width)  # Use standard width if not specified
        h = position.get('h', component_height)  # Use standard height if not specified
        
        # print(f"DEBUG: Component {idx+1} (ID: {component_id}) - Type: {component_type}, Size: {w}x{h}")
        
        # Create layout item for each breakpoint with responsive sizing
        for breakpoint in layouts:
            bp_width = w
            if breakpoint == 'xs':
                bp_width = 4  # Smaller for phones
            elif breakpoint == 'sm':
                bp_width = 6  # Medium for tablets
                
            layouts[breakpoint].append({
                'i': component_id,
                'x': x,
                'y': y,
                'w': bp_width,
                'h': h,
                'minW': 4,  # Minimum width
                'minH': 4   # Minimum height
            })
        
        # Create the component content
        component_content = []
        
        # Define card type-specific styling
        card_theme = get_component_theme(component_type)
        
        # Component header with title and controls
        component_header = html.Div([ 
            html.Div([
                html.I(className=f"fas {card_theme['icon']}", style={"marginRight": "10px", "fontSize": "18px"}),
                html.H3(component_title, className="component-title", style={"margin": 0, "display": "inline"})
            ], style={"display": "flex", "alignItems": "center"}),
            html.Div([
                html.Button(
                    html.I(className="fas fa-trash-alt", style={"color": card_theme['icon_color']}),
                    id={"type": "remove-component", "index": component_id},
                    className="component-control-btn",
                    title="Delete",
                    style={"background": "transparent", "border": "none"}
                )
            ], className="component-controls")
        ], className="component-header", style={
            "display": "flex", 
            "justifyContent": "space-between",
            "alignItems": "center",
            "padding": "12px 15px",
            "borderBottom": f"1px solid {card_theme['border_color']}",
            "background": card_theme['header_bg'],
            "color": card_theme['header_text'],
            "borderTopLeftRadius": "8px",
            "borderTopRightRadius": "8px",
            "overflow": "hidden"  # Add this line
        })
        
        component_content.append(component_header)
        
        # Component body based on type
        body_style = {
            "padding": "15px",
            "background": card_theme['body_bg'],
            "height": "calc(100% - 50px)",  # Adjust for header height
            "overflow": "auto",
            "borderBottomLeftRadius": "8px",
            "borderBottomRightRadius": "8px"
        }
        
        if component_type == 'income_chart' or component_type == 'income_forecast':
            months_ahead = component_settings.get('months_ahead', 6)
            forecast_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_income_chart(income_data, component_settings, months_ahead),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(forecast_graph, style=body_style))\
        
        elif component_type == "income_breakdown_pie":
            fig = generate_income_breakdown_pie(income_data, component_settings)
            chart_component = dcc.Graph(
                id=f"chart-{component_id}",
                figure=fig,
                config={'displayModeBar': False},
                className="dashboard-chart"
            )
            component_content.append(chart_component)
            
        elif component_type == 'expense_breakdown':
            expense_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_expense_breakdown(expense_data, component_settings),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(expense_graph, style=body_style))
            
        # Handle new chart types
        elif component_type == 'income_monte_carlo':
            monte_carlo_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_monte_carlo_simulation(income_data, component_settings),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(monte_carlo_graph, style=body_style))
            
        elif component_type == 'income_heatmap':
            heatmap_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_income_heatmap(income_data, component_settings),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(heatmap_graph, style=body_style))
            
        elif component_type == 'income_seasonality':
            seasonality_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_income_seasonality(income_data, component_settings),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(seasonality_graph, style=body_style))
            
        elif component_type == 'income_growth':
            growth_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_income_growth_chart(income_data, component_settings),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(growth_graph, style=body_style))

        # Chart 1: Monthly Spending Overview Component
        elif component_type == 'expenses_forecast':
            monthly_spending_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_monthly_spending_overview(expense_data, component_settings),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(monthly_spending_graph, style=body_style))

        # Chart 2: Expense Categories Component
        elif component_type == 'expenses_breakdown_pie':
            expense_breakdown_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_expense_categories_donut(expense_data, component_settings),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(expense_breakdown_graph, style=body_style))

        # Chart 3: Budget vs Actual Component
        elif component_type == 'expenses_trends':
            budget_data = None # Setting this to None for now
            budget_vs_actual_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_budget_vs_actual(expense_data, budget_data, component_settings),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(budget_vs_actual_graph, style=body_style))

        # Chart 4: Top Spending Categories Component
        elif component_type == 'expenses_heatmap':
            top_spending_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_top_spending_categories(expense_data, component_settings),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(top_spending_graph, style=body_style))

        # Chart 5: Spending Trends Component
        elif component_type == 'expenses_seasonality':
            spending_trends_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_spending_trends(expense_data, component_settings),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(spending_trends_graph, style=body_style))

        # Chart 6: Recurring Expenses Component
        elif component_type == 'expenses_growth':
            recurring_expenses_graph = dcc.Graph(
                id={"type": "component-graph", "index": component_id},
                figure=generate_recurring_expenses(expense_data, component_settings),
                config={'displayModeBar': False},
                className="component-graph",
                style={"height": "100%", "width": "100%"}
            )
            component_content.append(html.Div(recurring_expenses_graph, style=body_style))
            
        # Add more component types as needed
        else:
            # Generic placeholder for unknown component types
            component_content.append(html.Div(
                f"Unknown component type: {component_type}",
                className="component-error",
                style=body_style
            ))
        
        # Create the component container with enhanced styling
        component_div = html.Div(
            component_content,
            id={"type": "dashboard-component", "index": component_id},
            className="dashboard-component",
            style={
                "width": "100%", 
                "height": "100%", 
                "minHeight": "300px",
                "minWidth": "200px",
                "overflow": "hidden",     # Hide overflow
                "borderRadius": "8px",    # Rounded corners
                "boxShadow": "0 4px 20px rgba(0, 0, 0, 0.15)",  # Subtle shadow
                "border": f"1px solid {card_theme['border_color']}",
                "position": "relative"    # For absolute positioning of drag handles
            }
        )
        
        components.append(component_div)
    
    return components, layouts

def get_component_theme(component_type):
    """Returns theme colors based on component type - blue gradients for income and orange gradients for expense components"""
    
    # Determine if the component is income or expense based
    is_expense = 'expense' in component_type.lower()
    
    # Set theme based on component type
    if is_expense:
        # Orange gradient theme for expense components
        theme = {
            'header_bg': 'linear-gradient(135deg, #ff9966 0%, #ff5e62 100%)',  # Orange gradient
            'header_text': '#ffffff',  # White text
            'body_bg': '#ffffff',      # White background
            'border_color': '#ffcccc', # Light orange border
            'icon_color': '#ffffff'    # White icons
        }
    else:
        # Blue gradient theme for income components
        theme = {
            'header_bg': 'linear-gradient(135deg, #0082c8 0%, #0066aa 100%)',  # Deep blue gradient
            'header_text': '#ffffff',  # White text
            'body_bg': '#ffffff',      # White background
            'border_color': '#87ceeb', # Light gray border
            'icon_color': '#ffffff'    # White icons
        }
    
    # Component-specific icons that better match the visualization types
    icons = {
        # Income chart icons
        'income_chart': 'fa-chart-line',
        'income_forecast': 'fa-chart-area',
        'income_breakdown_pie': 'fa-chart-pie',
        'income_monte_carlo': 'fa-random',
        'income_heatmap': 'fa-th',
        'income_seasonality': 'fa-calendar-alt',
        'income_growth': 'fa-arrow-trend-up',
        
        # Expense chart icons
        'expense_breakdown': 'fa-chart-pie',
        'expenses_forecast': 'fa-chart-line',
        'expenses_breakdown_pie': 'fa-chart-pie',
        'expenses_trends': 'fa-chart-bar',
        'expenses_heatmap': 'fa-th',
        'expenses_seasonality': 'fa-calendar-alt',
        'expenses_growth': 'fa-arrow-trend-down',
        
        # Default icon
        'default': 'fa-th-large'
    }
    
    # Add the appropriate icon to the theme
    theme['icon'] = icons.get(component_type, icons['default'])
    
    return theme


# Add a ClientsideFunction and callback to handle position updates

# Add an interval component to the layout
layout.children.append(dcc.Interval(id='layout-update-interval', interval=1000, n_intervals=0))
layout.children.append(dcc.Store(id='dashboard-position-store', storage_type='memory'))

@callback(
    [
        Output("add-component-modal", "is_open", allow_duplicate=True),
        Output("current-chart-store", "data", allow_duplicate=True)
    ],
    [Input("add-component-cancel", "n_clicks")],
    prevent_initial_call=True
)
def cancel_modal(cancel_clicks):
    """Close the modal when cancel is clicked"""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    # Close the modal and clear the chart store when cancel is clicked
    return False, None

@callback(
    Output("chat-input", "value"),
    [Input("send-chat", "n_clicks"),
     Input("chat-input", "n_submit")],
    [State("chat-input", "value")],
    prevent_initial_call=True
)
def clear_input(n_clicks, n_submit, current_value):
    """Clear the input field after sending a message"""
    if (n_clicks or n_submit) and current_value:
        return ""
    raise PreventUpdate

# Add a callback for clicking the "Add to Dashboard" button directly in the chat
@callback(
    [Output("chat-input", "value", allow_duplicate=True)],
    [Input({"type": "add-to-dashboard-button", "index": ALL}, "n_clicks")],
    prevent_initial_call=True
)
def handle_add_dashboard_button_click(n_clicks_list):
    """Handle the Add to Dashboard button click in the chat"""
    if not any(n_clicks_list):
        raise PreventUpdate
    
    # Just to prevent update errors, doesn't change anything
    return [""]

# Add a simple callback to check if dashboard grid updates are working
@callback(
    Output("last-updated", "children"),
    Input("dashboard-settings-store", "data")
)
def update_last_updated(settings):
    """Update the last updated timestamp when settings change"""
    if settings and 'components' in settings:
        component_count = len(settings['components'])
        return f"Last updated: {datetime.now().strftime('%H:%M:%S')} - Components: {component_count}"
    return "No components"

# Load user data when page loads or user ID changes
@callback(
    Output("user-data-store", "data"),
    [Input("user-id-store", "data"),
     Input("url", "pathname"),
     Input("session-data-store", "data")],
    prevent_initial_call=False  # Run on initial load
)
def load_user_data(user_id, pathname, session_data):
    """Load user data from the database based on user ID"""
    # print(f"Loading user data, ID: {user_id}, Path: {pathname}")
    # print('printing session store data', session_data)
    if session_data:
        user_id = session_data['user_id']
    else:
        user_id = None
    
    if user_id is None:
        # Default to Guest if no user ID is found
        return get_user_data('Guest')
    
    # Get user data from database
    user_data = get_user_data(user_id)
    # print('printing user data', user_data)
    # print(f"Loaded data for user ID: {user_id}")
    
    return user_data

# Update user display in header
@callback(
    Output("user-email-display", "children"),
    Input("user-data-store", "data"),
    prevent_initial_call=False  # Run on initial load
)
def update_user_display(user_data):
    """Update user display based on user data"""
    if user_data and 'user_info' in user_data:
        if 'email' in user_data['user_info']:
            return user_data['user_info']['email']
        elif 'name' in user_data['user_info']:
            return user_data['user_info']['name']
    return "Guest User"

# Toggle dropdown visibility
@callback(
    Output("user-dropdown-content", "className", allow_duplicate=True),
    [Input("user-dropdown-button", "n_clicks")],
    [State("user-dropdown-content", "className")],
    prevent_initial_call=True
)
def toggle_dropdown(n_clicks, current_class):
    """Toggle user dropdown menu visibility"""
    if n_clicks:
        if "show" in current_class:
            return "user-dropdown-content"
        else:
            return "user-dropdown-content show"
    return current_class

# Logout functionality
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks) {
            // Clear all relevant stores
            localStorage.removeItem("user-id-store");
            sessionStorage.removeItem("user-data-store");
            localStorage.removeItem("session-data-store");
            localStorage.removeItem("dashboard-settings-store");
            // Redirect to home
            return '/';
        }
        return dash_clientside.no_update;
    }
    """,
    Output("url", "pathname"),
    Input("logout-link", "n_clicks"),
    prevent_initial_call=True
)
# Add this to your existing clientside callbacks
clientside_callback(
    """
    function(n) {
        // This function runs periodically to ensure data persistence in local storage
        const dashboardSettings = localStorage.getItem('dash_store:dashboard-settings-store');
        // Simply returning n ensures the callback runs but doesn't change anything
        return n;
    }
    """,
    Output("layout-update-interval", "n_intervals", allow_duplicate=True),
    Input("layout-update-interval", "n_intervals"),
    prevent_initial_call=True
)
# Use a single clientside callback that does both jobs
clientside_callback(
    """
    function(n_intervals) {
        // If this is the first run, set up the event listener
        if (!window.dashboardListenerInitialized) {
            console.log("Setting up dashboard layout change listener");
            
            document.addEventListener('dashboardLayoutChanged', function(e) {
                // Store the data in a dash store directly
                const store = document.getElementById('dashboard-position-store');
                if (store) {
                    store._dashprivate_setValue(e.detail);
                    
                    // Also trigger an event that Dash can listen for
                    const triggerElement = document.getElementById('dashboard-event-trigger');
                    if (triggerElement) {
                        triggerElement.setAttribute('data-update', Date.now());
                    }
                }
            });
            
            window.dashboardListenerInitialized = true;
        }
        
        return dash_clientside.no_update;
    }
    """,
    Output('dashboard-event-trigger', 'data-update'),
    Input('layout-update-interval', 'n_intervals'),
    prevent_initial_call=True
)

@callback(
    [
        Output("income-page-modal", "is_open"),
        Output("income-page-iframe", "src")
    ],
    [
        Input("close-income-modal", "n_clicks"),
        Input("chat-input", "n_submit"),
        Input("send-chat", "n_clicks"),
        Input("try-income-cmd", "n_clicks"),
    ],
    [
        State("chat-input", "value"),
        State("income-page-modal", "is_open")
    ],
    prevent_initial_call=True
)
def manage_income_modal(close_clicks, n_submit, send_clicks, try_income, input_value, is_open):
    """Open or close the income page modal"""
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Close modal when close button is clicked
    if trigger_id == "close-income-modal":
        return False, dash.no_update
    # print("printing trigger id before", trigger_id)

    # Debugging: Print input_value
    # print(f"input_value: {input_value}")

    # Check if we should open the modal based on user input
    if trigger_id in ["chat-input", "send-chat", "try-income-cmd"]:
        # print(f"trigger_id: {trigger_id}")
        
        # If the trigger was try-income-cmd, we don’t need input_value check, just open the modal
        if trigger_id == "try-income-cmd":
            # print("Opening modal for try-income-cmd")
            return True, "/income"

        # For chat-input and send-chat, check the input_value
        if input_value:
            input_lower = input_value.lower()
            # print(f"input_lower: {input_lower}")
            
            if any(phrase in input_lower for phrase in [
                "add to my income", 
                "manage income",
                "interested in my income breakdown", 
                "view income page",
                "edit my income",
                "I want to add to my income"
            ]):
                # print("Opening modal based on chat input")
                return True, "/income"
    
    # Default - no changes
    # print("Returning default (no changes)")
    return dash.no_update, dash.no_update

@callback(
    [
        Output("expenses-page-modal", "is_open"),
        Output("expenses-page-iframe", "src")
    ],
    [
        Input("close-expenses-modal", "n_clicks"),
        Input("chat-input", "n_submit"),
        Input("send-chat", "n_clicks"),
        Input("try-expense-cmd", "n_clicks"),
    ],
    [
        State("chat-input", "value"),
        State("expenses-page-modal", "is_open")
    ],
    prevent_initial_call=True
)
def manage_expenses_modal(close_clicks, n_submit, send_clicks, try_expense, input_value, is_open):
    """Open or close the expenses page modal"""
    ctx = dash.callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Close modal when close button is clicked
    if trigger_id == "close-expenses-modal":
        return False, dash.no_update
    
    # Debugging: Print trigger_id and input_value
    # print(f"trigger_id: {trigger_id}")
    # print(f"input_value: {input_value}")

    # Check if we should open the modal based on user input
    if trigger_id in ["chat-input", "send-chat", "try-expense-cmd"]:
        # print(f"trigger_id: {trigger_id}")
        
        # If the trigger was try-expense-cmd, we don’t need input_value check, just open the modal
        if trigger_id == "try-expense-cmd":
            # print("Opening modal for try-expense-cmd")
            return True, "/expenses"

        # For chat-input and send-chat, check the input_value
        if input_value:
            input_lower = input_value.lower()
            # print(f"input_lower: {input_lower}")
            
            if any(phrase in input_lower for phrase in [
                "add to my expenses", 
                "add an expense",
                "manage expenses",
                "interested in my expenses breakdown", 
                "view expenses page",
                "edit my expenses"
            ]):
                print("Opening modal based on chat input")
                return True, "/expenses"
    
    # Default - no changes
    # print("Returning default (no changes)")
    return dash.no_update, dash.no_update


def find_next_available_position(current_settings):
    """Find the next available grid position for a new component"""
    # Default grid dimensions - make these consistent!
    grid_width = 12  # Total width of grid (number of columns)
    component_width = 8  # Default component width - ALWAYS use this
    component_height = 6  # Default component height - ALWAYS use this
    
    # If no components exist yet, start at top left
    if not current_settings or 'components' not in current_settings or not current_settings['components']:
        return {'x': 0, 'y': 0, 'w': component_width, 'h': component_height}
    
    # Create a grid representation to track occupied cells
    # First, determine how tall our grid needs to be based on existing components
    max_row = 0
    for comp in current_settings['components']:
        pos = comp.get('position', {})
        y = pos.get('y', 0)
        h = pos.get('h', component_height)  # Use default if not specified
        max_row = max(max_row, y + h)
    
    # Initialize grid as all empty (None)
    grid = [[None for _ in range(grid_width)] for _ in range(max_row + component_height + 1)]
    
    # Mark occupied cells - IMPORTANT: Use FIXED sizes here!
    for comp in current_settings['components']:
        pos = comp.get('position', {})
        x = max(0, pos.get('x', 0))
        y = max(0, pos.get('y', 0))
        w = component_width  # Always use the standard width
        h = component_height  # Always use the standard height
        
        # Mark each cell covered by this component
        for row in range(y, min(y + h, len(grid))):
            for col in range(x, min(x + w, grid_width)):
                if row < len(grid) and col < grid_width:
                    grid[row][col] = comp['id']
    
    # Find next available position using standard component size
    for row in range(len(grid) - component_height + 1):
        for col in range(grid_width - component_width + 1):
            # Check if all cells for this position are free
            position_available = True
            for r in range(row, row + component_height):
                for c in range(col, col + component_width):
                    if r < len(grid) and c < grid_width and grid[r][c] is not None:
                        position_available = False
                        break
                if not position_available:
                    break
            
            if position_available:
                return {'x': col, 'y': row, 'w': component_width, 'h': component_height}
    
    # If no space found, put it in a new row at the bottom
    return {'x': 0, 'y': max_row, 'w': component_width, 'h': component_height}


@callback(
    Output('dashboard-settings-store', 'data', allow_duplicate=True),
    Input('dashboard-grid', 'layouts'),
    [State('dashboard-settings-store', 'data'),
     State('user-data-store', 'data')],
    prevent_initial_call=True
)
def save_layout_changes(layouts, current_settings, user_data):
    """Save layout changes from dash_draggable to dashboard settings"""
    if not layouts or not current_settings:
        raise PreventUpdate
    
    # Add this debugging
    # print("DEBUG: Layout change detected")
    # print(f"DEBUG: Current layouts: {json.dumps(layouts)}")
    
    # Initialize components if missing
    if 'components' not in current_settings:
        current_settings = {'components': []}
    
    # Extract the current layout (usually the 'lg' or default layout)
    current_layout = layouts.get('lg', [])
    if not current_layout:
        # Try other breakpoints if 'lg' is not available
        for breakpoint in ['md', 'sm', 'xs', 'xxs']:
            if breakpoint in layouts and layouts[breakpoint]:
                current_layout = layouts[breakpoint]
                break
    
    if not current_layout:
        raise PreventUpdate
    
    # Make sure we're not working with a reference to avoid modifying the input state
    current_settings = copy.deepcopy(current_settings)
    
    # Update the positions of all components in settings
    for layout_item in current_layout:
        item_id = layout_item.get('i')
        if not item_id:
            continue
            
        # Extract position data
        position = {
            'x': layout_item.get('x', 0),
            'y': layout_item.get('y', 0),
            'w': layout_item.get('w', 8),  # Force standard width here
            'h': layout_item.get('h', 6)   # Force standard height here
        }
        
        # print(f"DEBUG: Updating component {item_id} position to {position}")
        
        # Update the component position in settings
        component_found = False
        for component in current_settings['components']:
            if component['id'] == item_id:
                component['position'] = position
                component_found = True
                break
                
        # If component wasn't found in settings but exists in layout, add it
        if not component_found:
            print(f"Component {item_id} found in layout but not in settings")
    
    # Save to database if not guest user
    current_settings['layouts'] = layouts
    user_id = user_data.get('user_info', {}).get('user_id')
    if user_id and user_id != 'Guest':
        save_dashboard_settings_to_db(user_id, current_settings)
        # print(f"Saved dashboard settings after layout change for user {user_id}")
    
    return current_settings

def save_dashboard_settings_to_db(user_id, settings):
    """Save dashboard settings to database"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET dashboard_settings = %s WHERE user_id = %s",
                (json.dumps(settings), user_id)
            )
            conn.commit()
        return True
    except Exception as e:
        # print(f"Error saving dashboard settings: {e}")
        return False
    finally:
        conn.close()

@callback(
    [Output("dashboard-grid", "children"),
     Output("dashboard-grid", "layouts", allow_duplicate=True),
     Output("empty-dashboard-state", "style")],
    [Input("user-data-store", "data")],
    [State("dashboard-settings-store", "data")],
    prevent_initial_call=True
)
def initialize_dashboard(user_data, current_settings):
    """Initialize dashboard with current live settings"""
    if not user_data:
        return [], {'lg': [], 'md': [], 'sm': [], 'xs': []}, {"display": "block"}

    # Only hide empty state if we have components
    components, generated_layouts = generate_dashboard_components(current_settings, user_data)
    
    # Show empty state when no components exist
    # Be explicit about checking if components exist
    has_components = (
        current_settings and 
        'components' in current_settings and 
        current_settings['components'] and  # Check if list is not empty
        len(current_settings['components']) > 0
    )
    empty_style = {"display": "block" if not has_components else "none"}

    # print(f"DEBUG: Has components: {has_components}, showing empty state: {empty_style['display'] == 'block'}")

    # Use layouts from current_settings if available, otherwise use generated ones
    layouts = current_settings.get('layouts', generated_layouts) if current_settings else generated_layouts
    
    # Ensure layouts is properly initialized for all breakpoints
    if not layouts or not isinstance(layouts, dict):
        layouts = {'lg': [], 'md': [], 'sm': [], 'xs': []}
    
    # Make sure all required breakpoints exist
    for breakpoint in ['lg', 'md', 'sm', 'xs']:
        if breakpoint not in layouts:
            layouts[breakpoint] = []

    return components, layouts, empty_style

# want to change the background color of cards/components. I also want to make it so when the cards/components are generated, they at least get
# generated with a decent size and not so small. Also the first component gets generated with a good size but the ones after are small?
# Also in page initilization even thought i have 0 components, im not getting the empty page

# Add this as a new callback that runs whenever the dashboard layout changes
@callback(
    Output("debug-output", "children"),  # Add this hidden div to your layout
    [Input("dashboard-grid", "layouts")],
    prevent_initial_call=True
)
def inspect_dashboard_layout(layouts):
    """Debug function to inspect layouts"""
    if not layouts:
        return "No layouts"
    
    debug_output = []
    
    for breakpoint, items in layouts.items():
        debug_output.append(f"Breakpoint: {breakpoint}")
        for item in items:
            debug_output.append(f"  Item {item.get('i')}: x={item.get('x')}, y={item.get('y')}, w={item.get('w')}, h={item.get('h')}")
    
    # print("DEBUG LAYOUT:", "\n".join(debug_output))
    return "\n".join(debug_output)

# Add this div to your layout
layout.children.append(html.Div(id="debug-output", style={"display": "none"}))
