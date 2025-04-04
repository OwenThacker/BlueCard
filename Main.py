import streamlit as st
import pandas as pd
import numpy as np
import datetime
import calendar
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

# Set page configuration
st.set_page_config(
    page_title="BlueCard Finance",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern professional design system
st.markdown("""
<style>
    /* Design system - Professional financial dashboard */
    :root {
        /* Color palette - modern finance */
        --primary: #0466c8;
        --primary-light: #0353a4;
        --primary-dark: #023e7d;
        --secondary: #001845;
        --accent: #33415c;
        --success: #38b000;
        --warning: #f48c06;
        --danger: #d00000;
        --info: #48cae4;
        --neutral-50: #fafafa;
        --neutral-100: #f5f5f5;
        --neutral-200: #e5e5e5;
        --neutral-300: #d4d4d4;
        --neutral-400: #a3a3a3;
        --neutral-500: #737373;
        --neutral-600: #525252;
        --neutral-700: #404040;
        --neutral-800: #262626;
        --neutral-900: #171717;
        
        /* Elevation & effects */
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        
        /* Typography */
        --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
        --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        --border-radius: 8px;
    }
    
    /* Base styling */
    .stApp {
        background-color: var(--neutral-100);
        font-family: var(--font-primary);
    }
    
    /* Dashboard header */
    .dashboard-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 24px 0;
        margin-bottom: 20px;
        border-bottom: 1px solid var(--neutral-200);
    }
    
    .dashboard-title {
        font-size: 22px;
        font-weight: 700;
        color: var(--neutral-900);
        display: flex;
        align-items: center;
        gap: 12px;
        letter-spacing: -0.025em;
    }
    
    .dashboard-logo {
        font-size: 28px;
        background: linear-gradient(45deg, var(--primary), var(--primary-light));
        color: white;
        height: 40px;
        width: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
    }
    
    /* Card components */
    .dashboard-card {
        background: white;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-md);
        padding: 24px;
        height: 100%;
        border: 1px solid var(--neutral-200);
        transition: var(--transition-smooth);
        position: relative;
        overflow: hidden;
    }
    
    .dashboard-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--neutral-200);
    }
    
    .card-title {
        font-size: 16px;
        font-weight: 600;
        color: var(--neutral-800);
        margin: 0;
        letter-spacing: -0.01em;
    }
    
    /* Metric tiles */
    .metric-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .metric-card {
        background: white;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-sm);
        padding: 20px;
        position: relative;
        overflow: hidden;
        border: 1px solid var(--neutral-200);
        transition: var(--transition-smooth);
    }
    
    .metric-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }
    
    .metric-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: var(--primary);
    }
    
    .metric-label {
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
        color: var(--neutral-500);
        margin-bottom: 8px;
    }
    
    .metric-value {
        font-size: 24px;
        font-weight: 700;
        color: var(--neutral-900);
        margin-bottom: 4px;
        letter-spacing: -0.025em;
        display: flex;
        align-items: baseline;
    }
    
    .metric-trend {
        font-size: 12px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 4px;
    }
    
    .trend-up {
        color: var(--success);
    }
    
    .trend-down {
        color: var(--danger);
    }
    
    /* Button styling */
    div.stButton > button {
        background: var(--primary);
        border: none;
        color: white;
        padding: 10px 16px;
        font-weight: 500;
        border-radius: var(--border-radius);
        transition: var(--transition-smooth);
        box-shadow: var(--shadow-sm);
        text-transform: none;
    }
    
    div.stButton > button:hover {
        background: var(--primary-dark);
        box-shadow: var(--shadow-md);
    }
    
    /* Form styling */
    .stNumberInput input, .stTextInput input, .stDateInput input {
        border-radius: var(--border-radius);
        padding: 12px 16px;
        border: 1px solid var(--neutral-300);
        box-shadow: var(--shadow-sm);
        font-size: 14px;
        transition: var(--transition-smooth);
    }
    
    .stNumberInput input:focus, .stTextInput input:focus, .stDateInput input:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(4, 102, 200, 0.15);
    }
    
    /* Select and dropdowns */
    .stSelectbox > div > div {
        border-radius: var(--border-radius);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background-color: var(--neutral-50);
        padding: 4px;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--neutral-200);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 20px;
        border-radius: var(--border-radius);
        font-weight: 500;
        font-size: 14px;
        color: var(--neutral-600);
        transition: var(--transition-smooth);
        border-bottom: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: white;
        color: var(--primary);
        box-shadow: var(--shadow-sm);
        font-weight: 600;
    }
    
    /* Transaction records */
    .transaction-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 16px;
        border-radius: var(--border-radius);
        margin-bottom: 8px;
        background-color: white;
        border: 1px solid var(--neutral-200);
        transition: var(--transition-smooth);
    }
    
    .transaction-item:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--neutral-300);
    }
    
    .transaction-icon {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: rgba(4, 102, 200, 0.1);
        border-radius: 8px;
        color: var(--primary);
        margin-right: 12px;
        font-size: 16px;
    }
    
    .transaction-details {
        flex: 1;
    }
    
    .transaction-title {
        font-weight: 600;
        color: var(--neutral-800);
        margin-bottom: 2px;
        font-size: 14px;
    }
    
    .transaction-meta {
        font-size: 12px;
        color: var(--neutral-500);
    }
    
    .transaction-amount {
        font-weight: 600;
        color: var(--neutral-800);
        font-size: 14px;
    }
    
    /* Tags/badges */
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        line-height: 1;
        white-space: nowrap;
        margin-left: 8px;
    }
    
    .badge-blue {
        background-color: rgba(4, 102, 200, 0.1);
        color: var(--primary);
    }
    
    .badge-green {
        background-color: rgba(56, 176, 0, 0.1);
        color: var(--success);
    }
    
    .badge-orange {
        background-color: rgba(244, 140, 6, 0.1);
        color: var(--warning);
    }
    
    .badge-red {
        background-color: rgba(208, 0, 0, 0.1);
        color: var(--danger);
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background-color: var(--primary);
        border-radius: 999px;
    }
    
    .stProgress > div > div > div {
        background-color: var(--neutral-200);
        border-radius: 999px;
    }
    
    /* Custom progress bar */
    .progress-container {
        width: 100%;
        height: 8px;
        background-color: var(--neutral-200);
        border-radius: 999px;
        margin-top: 8px;
        margin-bottom: 8px;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 999px;
        transition: width 0.5s ease;
    }
    
    .progress-stats {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: var(--neutral-500);
        margin-top: 4px;
    }
    
    /* Chart containers */
    .chart-container {
        background: white;
        border-radius: var(--border-radius);
        padding: 16px;
        box-shadow: var(--shadow-sm);
        height: 100%;
        border: 1px solid var(--neutral-200);
    }
    
    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
    }
    
    .chart-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--neutral-700);
        margin: 0;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: white;
        border-right: 1px solid var(--neutral-200);
    }
    
    section[data-testid="stSidebar"] > div {
        padding: 2rem 1rem;
    }
    
    /* Info boxes */
    .info-box {
        background-color: rgba(72, 202, 228, 0.1);
        border-left: 4px solid var(--info);
        padding: 12px 16px;
        border-radius: var(--border-radius);
        margin-bottom: 16px;
    }
    
    .warning-box {
        background-color: rgba(244, 140, 6, 0.1);
        border-left: 4px solid var(--warning);
        padding: 12px 16px;
        border-radius: var(--border-radius);
        margin-bottom: 16px;
    }
    
    /* Form spacings */
    .form-group {
        margin-bottom: 20px;
    }
    
    /* Extra spacing for main container */
    .main-container {
        padding: 10px 0;
    }
    
    /* Expense category icons */
    .category-icons {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 16px;
    }
    
    .category-icon {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 12px;
        border-radius: var(--border-radius);
        background-color: white;
        border: 1px solid var(--neutral-200);
        transition: var(--transition-smooth);
        cursor: pointer;
        min-width: 80px;
    }
    
    .category-icon:hover, .category-icon.active {
        background-color: rgba(4, 102, 200, 0.1);
        border-color: var(--primary);
    }
    
    .icon-symbol {
        font-size: 20px;
        margin-bottom: 4px;
    }
    
    .icon-label {
        font-size: 11px;
        color: var(--neutral-700);
        font-weight: 500;
    }
    
    /* Custom footer */
    .app-footer {
        text-align: center;
        padding: 24px 0;
        color: var(--neutral-500);
        font-size: 12px;
        margin-top: 40px;
        border-top: 1px solid var(--neutral-200);
    }
    
    /* Streamlit specifics */
    div.block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {
        visibility: hidden;
    }
    
    /* Summary tiles */
    .summary-tile {
        background: white;
        border-radius: var(--border-radius);
        padding: 20px;
        box-shadow: var(--shadow-sm);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        height: 100%;
        transition: var(--transition-smooth);
        border: 1px solid var(--neutral-200);
    }
    
    .summary-tile:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
    }
    
    .summary-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .summary-title {
        font-size: 14px;
        font-weight: 600;
        color: var(--neutral-600);
        margin: 0;
    }
    
    .summary-icon {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
        font-size: 16px;
    }
    
    .summary-value {
        font-size: 22px;
        font-weight: 700;
        color: var(--neutral-900);
        margin: 0;
    }
    
    .summary-subtitle {
        font-size: 12px;
        color: var(--neutral-500);
        margin-top: 4px;
    }
    
    /* Icon backgrounds */
    .icon-blue {
        background-color: rgba(4, 102, 200, 0.1);
        color: var(--primary);
    }
    
    .icon-green {
        background-color: rgba(4, 102, 200, 0.1); /* Darker green */
        color: var(--success);
    }
    
    .icon-orange {
        background-color: rgba(244, 140, 6, 0.1);
        color: var(--warning);
    }
    
    .icon-red {
        background-color: rgba(208, 0, 0, 0.1);
        color: var(--danger);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data persistence
if 'salary' not in st.session_state:
    st.session_state.salary = 0.0  
if 'before_tax' not in st.session_state:
    st.session_state.before_tax = True
if 'consistent_salary' not in st.session_state:
    st.session_state.consistent_salary = True
if 'expenses' not in st.session_state:
    st.session_state.expenses = []
if 'daily_expenses' not in st.session_state:
    st.session_state.daily_expenses = []
if 'savings_target' not in st.session_state:
    st.session_state.savings_target = 0.0
if 'savings_goals' not in st.session_state:
    st.session_state.savings_goals = []
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0.0

# Dashboard Header
st.markdown('''
<div class="dashboard-header">
    <div class="dashboard-title">
        <div class="dashboard-logo">💎</div>
        BlueCard Finance
    </div>
</div>
''', unsafe_allow_html=True)

# Create main tabs with professional styling
tabs = st.tabs(["Dashboard", "Income", "Expenses", "Transactions", "Savings & Goals", "Financial Reports", 'App Settings'])

# Dashboard Overview Tab
with tabs[0]:
    # Main metrics row
    st.markdown("### Financial Summary")
    
    # Avoid division by zero errors
    salary = st.session_state.salary if 'salary' in st.session_state and st.session_state.salary > 0 else 1

    total_expenses = sum(expense["amount"] for expense in st.session_state.expenses) if st.session_state.expenses else 0
    remaining = st.session_state.salary - total_expenses if st.session_state.salary > 0 else 0
    savings_progress = (st.session_state.savings_target / remaining * 100) if remaining > 0 and st.session_state.savings_target > 0 else 0
    
    # Create the metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('''
        <div class="summary-tile">
            <div class="summary-header">
                <h4 class="summary-title">Monthly Income</h4>
                <div class="summary-icon icon-blue">💰</div>
            </div>
            <p class="summary-value">$''' + f"{st.session_state.salary:,.2f}" + '''</p>
            <p class="summary-subtitle">Daily budget: $''' + f"{st.session_state.salary/30:,.2f}" + '''</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''
        <div class="summary-tile">
            <div class="summary-header">
                <h4 class="summary-title">Total Expenses</h4>
                <div class="summary-icon icon-red">📊</div>
            </div>
            <p class="summary-value">$''' + f"{total_expenses:,.2f}" + '''</p>
            <p class="summary-subtitle">''' + f"{(total_expenses / salary) * 100:.1f}% of income" + ''' used</p>
        </div>
        ''', unsafe_allow_html=True)

    with col3:
        st.markdown('''
        <div class="summary-tile">
            <div class="summary-header">
                <h4 class="summary-title">Remaining</h4>
                <div class="summary-icon icon-green">✅</div>
            </div>
            <p class="summary-value">$''' + f"{remaining:,.2f}" + '''</p>
            <p class="summary-subtitle">''' + f"{(remaining / salary) * 100:.1f}% of income" + ''' available</p>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        daily_remaining = remaining / 30 if remaining > 0 else 0
        st.markdown('''
        <div class="summary-tile">
            <div class="summary-header">
                <h4 class="summary-title">Savings Target</h4>
                <div class="summary-icon icon-orange">🎯</div>
            </div>
            <p class="summary-value">$''' + f"{st.session_state.savings_target:,.2f}" + '''</p>
            <p class="summary-subtitle">''' + f"{savings_progress:.1f}% completed" + '''</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # Budget overview section
    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Expense Breakdown</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.expenses:
            # Group expenses by category
            expense_by_category = {}
            for expense in st.session_state.expenses:
                category = expense["category"]
                if category in expense_by_category:
                    expense_by_category[category] += expense["amount"]
                else:
                    expense_by_category[category] = expense["amount"]
            
            # Create dataframe for pie chart
            df_expenses = pd.DataFrame({
                'Category': list(expense_by_category.keys()),
                'Amount': list(expense_by_category.values()),
            })
            
            # Custom color palette
            custom_colors = ['#0466c8', '#0353a4', '#023e7d', '#001845', '#001233', 
                            '#33415c', '#5c677d', '#7d8597', '#979dac', '#33415c']
            
            # Create a professional donut chart
            fig = px.pie(
                df_expenses, 
                values='Amount', 
                names='Category', 
                hole=0.6,
                color_discrete_sequence=custom_colors
            )
            fig.update_traces(textposition='outside', textinfo='percent+label')
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=350,
                legend=dict(orientation="h", y=-0.2),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12, color="#404040")
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">No expenses added yet. Add expenses in the Expenses tab to see your breakdown.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Savings Progress</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.savings_target > 0:
            # Create a gauge chart for savings progress
            savings_percent = min(savings_progress, 100) / 100
            
            # Create a gauge chart with plotly
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=savings_percent * 100,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#404040"},
                    'bar': {'color': "#0466c8"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "#e5e5e5",
                    'steps': [
                        {'range': [0, 30], 'color': 'rgba(4, 102, 200, 0.2)'},
                        {'range': [30, 70], 'color': 'rgba(4, 102, 200, 0.4)'},
                        {'range': [70, 100], 'color': 'rgba(4, 102, 200, 0.6)'}
                    ],
                },
                title={
                    'text': f"${st.session_state.savings_target:,.2f}",
                    'font': {'size': 20, 'color': '#262626', 'family': 'Inter, sans-serif'}
                },
                number={
                    'suffix': "%",
                    'font': {'size': 26, 'color': '#0466c8', 'family': 'Inter, sans-serif'}
                }
            ))
            
            fig.update_layout(
                height=300,
                margin=dict(t=60, b=0, l=30, r=30),
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif")
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">Set a savings target in the Expenses tab to track your progress.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recent activity and spending trends
    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Recent Activity</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.daily_expenses:
            # Convert to DataFrame and sort
            df_recent = pd.DataFrame(st.session_state.daily_expenses)
            df_recent['date'] = pd.to_datetime(df_recent['date'])
            df_recent = df_recent.sort_values('date', ascending=False).head(5)
            
            for _, row in df_recent.iterrows():
                st.markdown(f'''
                <div class="transaction-item">
                    <div style="display: flex; align-items: center;">
                        <div class="transaction-icon">{row['emoji']}</div>
                        <div class="transaction-details">
                            <div class="transaction-title">{row['description']}</div>
                            <div class="transaction-meta">{row['date'].strftime('%b %d, %Y')}</div>
                        </div>
                    </div>
                    <div class="transaction-amount">${row['amount']:.2f}</div>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">No recent transactions. Record your spending in the Transactions tab.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Spending Trends</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.daily_expenses:
            # Convert to DataFrame for analysis
            df_daily = pd.DataFrame(st.session_state.daily_expenses)
            df_daily['date'] = pd.to_datetime(df_daily['date'])
            
            # Group by date and sum amounts
            daily_totals = df_daily.groupby(df_daily['date'].dt.date)['amount'].sum().reset_index()
            daily_totals['date'] = pd.to_datetime(daily_totals['date'])
            daily_totals = daily_totals.sort_values('date')
            
            # Calculate daily budget
            remaining_after_expenses = st.session_state.salary - total_expenses
            daily_budget = (remaining_after_expenses - st.session_state.savings_target) / 30
            daily_totals['budget_line'] = daily_budget
            
            # Create line chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily_totals['date'],
                y=daily_totals['amount'],
                mode='lines+markers',
                name='Daily Spending',
                line=dict(color='#0466c8', width=3),
                marker=dict(size=8, color='#0466c8')
            ))
            
            # Add budget reference line
            fig.add_trace(go.Scatter(
                x=daily_totals['date'],
                y=daily_totals['budget_line'],
                mode='lines',
                name='Daily Budget',
                line=dict(color='#38b000', width=2, dash='dash')
            ))
            
            fig.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=250,
                legend=dict(orientation="h", y=1.1),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif", size=12, color="#404040"),
                xaxis=dict(
                    showgrid=False,
                    showline=True,
                    linecolor='#e5e5e5'
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='#e5e5e5',
                    showline=True,
                    linecolor='#e5e5e5',
                    tickprefix='$'
                ),
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">No transaction data available. Record your daily expenses to see trends.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Recommendations section
    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
    st.markdown('''<div class="dashboard-card">
        <div class="card-header">
            <h3 class="card-title">Finance Insights</h3>
        </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.salary > 0:
            # Calculate savings rate
            savings_rate = (st.session_state.salary - total_expenses) / st.session_state.salary * 100
            
            if savings_rate >= 20:
                st.markdown('''
                    <div class="info-box" style="border-left-color: #38b000;">
                        <p style="margin: 0; font-size: 14px; font-weight: 600; color: #38b000;">✓ Excellent Savings Rate</p>
                        <p style="margin: 5px 0 0 0; font-size: 13px;">Your savings rate is above 20%, which is excellent for long-term financial health.</p>
                    </div>
                ''', unsafe_allow_html=True)
            elif savings_rate >= 10:
                st.markdown('''
                    <div class="info-box">
                        <p style="margin: 0; font-size: 14px; font-weight: 600; color: #0466c8;">✓ Good Savings Rate</p>
                        <p style="margin: 5px 0 0 0; font-size: 13px;">Your savings rate is between 10-20%, which is a good foundation.</p>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown('''
                    <div class="warning-box">
                        <p style="margin: 0; font-size: 14px; font-weight: 600; color: #f48c06;">! Low Savings Rate</p>
                        <p style="margin: 5px 0 0 0; font-size: 13px;">Your savings rate is below 10%. Try to reduce non-essential expenses.</p>
                    </div>
                ''', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.expenses:
            # Find the largest expense category
            expense_by_category = {}
            for expense in st.session_state.expenses:
                category = expense["category"]
                if category in expense_by_category:
                    expense_by_category[category] += expense["amount"]
                else:
                    expense_by_category[category] = expense["amount"]
            
            largest_category = max(expense_by_category.items(), key=lambda x: x[1])
            largest_percent = largest_category[1] / total_expenses * 100
            
            if largest_percent > 50:
                st.markdown(f'''
                    <div class="warning-box">
                        <p style="margin: 0; font-size: 14px; font-weight: 600; color: #f48c06;">! High {largest_category[0]} Expenses</p>
                        <p style="margin: 5px 0 0 0; font-size: 13px;">{largest_category[0]} makes up {largest_percent:.1f}% of your expenses. Consider rebalancing your budget.</p>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                    <div class="info-box" style="border-left-color: #38b000;">
                        <p style="margin: 0; font-size: 14px; font-weight: 600; color: #38b000;">✓ Balanced Budget</p>
                        <p style="margin: 5px 0 0 0; font-size: 13px;">Your largest expense category ({largest_category[0]}) is {largest_percent:.1f}% of total expenses.</p>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">Add expenses in the Expenses tab to get budget balance insights.</p>
                </div>
            ''', unsafe_allow_html=True)
    
    with col3:
        if st.session_state.daily_expenses:
            # Analyze recent spending trends
            df_daily = pd.DataFrame(st.session_state.daily_expenses)
            df_daily['date'] = pd.to_datetime(df_daily['date'])
            
            # Get last 7 days vs previous 7 days
            today = datetime.datetime.now().date()
            last_week = df_daily[df_daily['date'] >= (pd.Timestamp(today) - pd.Timedelta(days=7))]
            prev_week = df_daily[(df_daily['date'] < (pd.Timestamp(today) - pd.Timedelta(days=7))) & 
                                (df_daily['date'] >= (pd.Timestamp(today) - pd.Timedelta(days=14)))]
            
            last_week_total = last_week['amount'].sum() if not last_week.empty else 0
            prev_week_total = prev_week['amount'].sum() if not prev_week.empty else 0
            
            if prev_week_total > 0:
                percent_change = (last_week_total - prev_week_total) / prev_week_total * 100
                
                if percent_change > 20:
                    st.markdown(f'''
                        <div class="warning-box">
                            <p style="margin: 0; font-size: 14px; font-weight: 600; color: #d00000;">! Spending Increase</p>
                            <p style="margin: 5px 0 0 0; font-size: 13px;">Your spending increased by {percent_change:.1f}% compared to previous week.</p>
                        </div>
                    ''', unsafe_allow_html=True)
                elif percent_change < -10:
                    st.markdown(f'''
                        <div class="info-box" style="border-left-color: #38b000;">
                            <p style="margin: 0; font-size: 14px; font-weight: 600; color: #38b000;">✓ Reduced Spending</p>
                            <p style="margin: 5px 0 0 0; font-size: 13px;">Great job! You reduced spending by {abs(percent_change):.1f}% from last week.</p>
                        </div>
                    ''', unsafe_allow_html=True)
                else:
                    st.markdown(f'''
                        <div class="info-box">
                            <p style="margin: 0; font-size: 14px; font-weight: 600; color: #0466c8;">✓ Consistent Spending</p>
                            <p style="margin: 5px 0 0 0; font-size: 13px;">Your spending is within {abs(percent_change):.1f}% of last week.</p>
                        </div>
                    ''', unsafe_allow_html=True)
            else:
                st.markdown('''
                    <div class="info-box">
                        <p style="margin: 0; font-size: 14px;">Need more data to analyze spending trends.</p>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">Record daily transactions to get spending trend insights.</p>
                </div>
            ''', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Income Tab
with tabs[1]:
    st.markdown("### Income Settings")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Set Your Monthly Income</h3>
            </div>
            <div class="form-group">
        ''', unsafe_allow_html=True)
        
        # Salary input
        salary = st.number_input(
            "Enter your monthly salary/income ($)",
            min_value=0.0,
            value=st.session_state.salary,
            step=100.0,
            format="%.2f"
        )
        
        # Save changes
        if st.button("Update Income", key="update_income"):
            st.session_state.salary = salary
            st.success("Income updated successfully!")
        
        st.markdown('''</div></div>''', unsafe_allow_html=True)
    
    with col2:
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Income Insights</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.salary > 0:
            # Calculate daily, weekly, yearly equivalents
            daily = st.session_state.salary / 30
            weekly = st.session_state.salary * 12 / 52
            yearly = st.session_state.salary * 12
            
            st.markdown(f'''
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Daily Equivalent</div>
                    <div class="metric-value">${daily:.2f}</div>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Weekly Equivalent</div>
                    <div class="metric-value">${weekly:.2f}</div>
                </div>
                
                <div>
                    <div class="metric-label">Annual Equivalent</div>
                    <div class="metric-value">${yearly:.2f}</div>
                </div>
            ''', unsafe_allow_html=True)
            
            if st.session_state.before_tax:
                st.markdown('''
                    <div class="info-box" style="margin-top: 20px;">
                        <p style="margin: 0; font-size: 14px;">Remember that your actual take-home pay will be lower after taxes.</p>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">Set your income to see the breakdown.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Expenses Tab
with tabs[2]:
    st.markdown("### Expense Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Add Monthly Expense</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        # Define expense categories
        categories = [
            "Housing", "Transportation", "Food", "Utilities", 
            "Health", "Insurance", "Debt", "Entertainment", 
            "Personal", "Education", "Savings", "Other"
        ]

        st.markdown("""
            <style>
                /* Make sure the input field label is styled properly */
                .stTextInput label {
                    display: block !important;
                    color: black !important;
                    font-weight: bold !important;
                }
            </style>
        """, unsafe_allow_html=True)

        
        # Expense form
        with st.form("expense_form"):
            description = st.text_input("Expense Description")
            amount = st.number_input("Amount ($)", min_value=0.0, step=10.0, format="%.2f")
            category = st.selectbox("Category", categories)
            due_date = st.date_input("Due Date", value=date.today())
            recurring = st.checkbox("This is a recurring expense")
            
            submitted = st.form_submit_button("Add Expense")
            
            if submitted and description and amount > 0:
                # Add the expense to our list
                st.session_state.expenses.append({
                    "description": description,
                    "amount": amount,
                    "category": category,
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "recurring": recurring
                })
                st.success(f"Added {description} expense successfully!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # List of current expenses
        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Current Monthly Expenses</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.expenses:
            for i, expense in enumerate(st.session_state.expenses):
                st.markdown(f'''
                <div class="transaction-item">
                    <div style="display: flex; align-items: center; flex: 1;">
                        <div class="transaction-icon">{expense["category"][0]}</div>
                        <div class="transaction-details">
                            <div class="transaction-title">{expense["description"]}</div>
                            <div class="transaction-meta">{expense["category"]} • Due: {expense["due_date"]}</div>
                        </div>
                    </div>
                    <div class="transaction-amount">${expense["amount"]:.2f}</div>
                    <button style="background: none; border: none; cursor: pointer; color: #d00000; margin-left: 12px;" 
                            onclick="this.innerHTML='...'; setTimeout(() => {{ Streamlit.setComponentValue('delete_expense_{i}', true); }}, 100)">
                        🗑️
                    </button>
                </div>
                ''', unsafe_allow_html=True)
                
                # Check if delete button was clicked (this is for demonstration - actual deletion 
                # would require JavaScript event handling that's more complex in Streamlit)
                if st.button("Delete", key=f"delete_btn_{i}", help="Delete this expense"):
                    st.session_state.expenses.pop(i)
                    st.rerun()
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">No expenses added yet. Use the form above to add your monthly expenses.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Expense summary
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Expense Summary</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.expenses:
            total_expenses = sum(expense["amount"] for expense in st.session_state.expenses)
            remaining = st.session_state.salary - total_expenses if st.session_state.salary > 0 else 0
            
            st.markdown(f'''
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Total Monthly Expenses</div>
                    <div class="metric-value">${total_expenses:.2f}</div>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Remaining After Expenses</div>
                    <div class="metric-value">${remaining:.2f}</div>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Expense Ratio</div>
                    <div class="metric-value">{total_expenses/st.session_state.salary*100:.1f}%</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {min(total_expenses/st.session_state.salary*100, 100)}%; background-color: var(--primary);"></div>
                    </div>
                    <div class="progress-stats">
                        <span>0%</span>
                        <span>50%</span>
                        <span>100%</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">Add expenses to see your expense summary.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Savings target
        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Set Savings Target</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        savings_target = st.number_input(
            "Monthly savings goal ($)",
            min_value=0.0,
            value=float(st.session_state.savings_target),  # Convert explicitly to float
            step=0.01
        )
        
        if st.button("Update Savings Goal"):
            st.session_state.savings_target = savings_target
            st.success("Savings target updated!")
        
        if st.session_state.savings_target > 0:
            remaining = st.session_state.salary - total_expenses if st.session_state.expenses else st.session_state.salary
            savings_percent = st.session_state.savings_target / remaining * 100 if remaining > 0 else 0
            
            st.markdown(f'''
                <div class="info-box" style="margin-top: 16px;">
                    <p style="margin: 0; font-size: 14px;">Your savings target is {savings_percent:.1f}% of your remaining income after expenses.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Transactions Tab
with tabs[3]:
    st.markdown("### Daily Transactions")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Record Transaction</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        # Emoji mapper for categories
        emoji_map = {
            "Housing": "🏠", "Transportation": "🚗", "Food": "🍔", 
            "Utilities": "💡", "Health": "🏥", "Insurance": "🛡️", 
            "Debt": "💳", "Entertainment": "🎬", "Personal": "👤", 
            "Education": "📚", "Savings": "💰", "Other": "📦"
        }
        
        # Transaction form
        with st.form("transaction_form"):
            description = st.text_input("Transaction Description")
            amount = st.number_input("Amount ($)", min_value=0.0, step=5.0, format="%.2f")
            category = st.selectbox("Category", list(emoji_map.keys()))
            transaction_date = st.date_input("Date", value=date.today())
            
            submitted = st.form_submit_button("Record Transaction")
            
            if submitted and description and amount > 0:
                # Add the transaction to our list
                st.session_state.daily_expenses.append({
                    "description": description,
                    "amount": amount,
                    "category": category,
                    "date": transaction_date.strftime("%Y-%m-%d"),
                    "emoji": emoji_map.get(category, "📝")
                })
                st.success(f"Recorded {description} transaction successfully!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Transaction history
        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Transaction History</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.daily_expenses:
            # Convert to DataFrame and sort
            df_transactions = pd.DataFrame(st.session_state.daily_expenses)
            df_transactions['date'] = pd.to_datetime(df_transactions['date'])
            df_transactions = df_transactions.sort_values('date', ascending=False)
            
            # Group by date
            grouped_dates = df_transactions.groupby(df_transactions['date'].dt.date)
            
            for date, group in grouped_dates:
                st.markdown(f"<h5 style='margin-top: 16px; margin-bottom: 8px; color: var(--neutral-700);'>{pd.to_datetime(date).strftime('%A, %B %d, %Y')}</h5>", unsafe_allow_html=True)
                
                daily_total = group['amount'].sum()
                st.markdown(f"<p style='color: var(--neutral-500); font-size: 13px; margin-bottom: 12px;'>Total: <strong>${daily_total:.2f}</strong></p>", unsafe_allow_html=True)
                
                for i, (_, row) in enumerate(group.iterrows()):
                    st.markdown(f'''
                    <div class="transaction-item">
                        <div style="display: flex; align-items: center; flex: 1;">
                            <div class="transaction-icon">{row['emoji']}</div>
                            <div class="transaction-details">
                                <div class="transaction-title">{row['description']}</div>
                                <div class="transaction-meta">{row['category']}</div>
                            </div>
                        </div>
                        <div class="transaction-amount">${row['amount']:.2f}</div>
                    </div>
                    ''', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">No transactions recorded yet. Use the form above to track your daily spending.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Weekly spending summary
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Weekly Summary</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.daily_expenses:
            # Convert to DataFrame for analysis
            df_daily = pd.DataFrame(st.session_state.daily_expenses)
            df_daily['date'] = pd.to_datetime(df_daily['date'])
            
            # Get current week data
            today = datetime.datetime.now().date()
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            
            this_week = df_daily[(df_daily['date'] >= pd.Timestamp(start_of_week)) & 
                               (df_daily['date'] <= pd.Timestamp(end_of_week))]
            
            weekly_total = this_week['amount'].sum() if not this_week.empty else 0
            
            # Calculate remaining budget
            remaining_after_expenses = st.session_state.salary - sum(expense["amount"] for expense in st.session_state.expenses) if st.session_state.expenses else st.session_state.salary
            monthly_discretionary = remaining_after_expenses - st.session_state.savings_target
            weekly_budget = monthly_discretionary * 12 / 52
            
            # Display metrics
            st.markdown(f'''
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">This Week's Spending</div>
                    <div class="metric-value">${weekly_total:.2f}</div>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Weekly Budget</div>
                    <div class="metric-value">${weekly_budget:.2f}</div>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Remaining This Week</div>
                    <div class="metric-value">${max(weekly_budget - weekly_total, 0):.2f}</div>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Budget Progress</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {min(weekly_total/weekly_budget*100, 100) if weekly_budget > 0 else 100}%; 
                            background-color: {('#38b000' if weekly_total <= weekly_budget else '#d00000') if weekly_budget > 0 else '#d00000'};"></div>
                    </div>
                    <div class="progress-stats">
                        <span>0%</span>
                        <span>50%</span>
                        <span>100%</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
            # Category breakdown this week
            if not this_week.empty:
                st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
                st.markdown("<h5 style='margin-bottom: 12px; color: var(--neutral-700);'>Category Breakdown</h5>", unsafe_allow_html=True)
                
                category_totals = this_week.groupby('category')['amount'].sum().sort_values(ascending=False)
                
                for category, amount in category_totals.items():
                    percent = amount / weekly_total * 100
                    st.markdown(f'''
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <div style="display: flex; align-items: center;">
                            <span style="margin-right: 8px;">{emoji_map.get(category, '📝')}</span>
                            <span style="color: var(--neutral-700);">{category}</span>
                        </div>
                        <div>
                            <span style="color: var(--neutral-800); font-weight: 500;">${amount:.2f}</span>
                            <span style="color: var(--neutral-500); font-size: 12px; margin-left: 4px;">({percent:.1f}%)</span>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)
                
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">Record transactions to see your weekly summary.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Category spending chart
        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Category Analysis</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.daily_expenses:
            # Convert to DataFrame for analysis
            df_cat = pd.DataFrame(st.session_state.daily_expenses)
            
            # Group by category
            cat_totals = df_cat.groupby('category')['amount'].sum().reset_index()
            cat_totals = cat_totals.sort_values('amount', ascending=True)
            
            # Continue the Category Analysis section
            # Create horizontal bar chart
            fig = px.bar(
                cat_totals,
                y='category',
                x='amount',
                orientation='h',
                title='Spending by Category',
                color='amount',
                color_continuous_scale='Blues',
                labels={'amount': 'Amount ($)', 'category': ''}
            )
            fig.update_layout(
                margin=dict(l=0, r=0, t=30, b=0),
                height=min(400, max(30 * len(cat_totals), 150)),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">Record transactions to see your category analysis.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Savings Tab
with tabs[4]:
    st.markdown("### Savings & Goals")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Savings Goals
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Set Financial Goals</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        with st.form("savings_goal_form"):
            goal_name = st.text_input("Goal Description")
            goal_amount = st.number_input("Target Amount ($)", min_value=0.0, step=100.0, format="%.2f")
            goal_date = st.date_input("Target Date", value=date.today() + datetime.timedelta(days=365))
            goal_priority = st.select_slider(
                "Priority",
                options=["Low", "Medium", "High"]
            )
            
            submitted = st.form_submit_button("Add Goal")
            
            if submitted and goal_name and goal_amount > 0:
                # Calculate required monthly saving
                today = date.today()
                months_remaining = ((goal_date.year - today.year) * 12 + 
                                 goal_date.month - today.month +
                                 (1 if goal_date.day > today.day else 0))
                
                # Handle case where goal date is in the past or current month
                monthly_amount = goal_amount / max(months_remaining, 1)
                
                # Add the goal to our list
                st.session_state.savings_goals.append({
                    "name": goal_name,
                    "amount": goal_amount,
                    "target_date": goal_date.strftime("%Y-%m-%d"),
                    "monthly_amount": monthly_amount,
                    "priority": goal_priority,
                    "current_saved": 0.0
                })
                st.success(f"Added {goal_name} goal successfully!")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Active Goals
        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Active Financial Goals</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.savings_goals:
            for i, goal in enumerate(st.session_state.savings_goals):
                # Calculate progress percentage
                progress = min(goal["current_saved"] / goal["amount"] * 100, 100) if goal["amount"] > 0 else 0
                
                # Priority color
                priority_color = {
                    "Low": "#98c1d9",
                    "Medium": "#3d5a80",
                    "High": "#ee6c4d"
                }
                
                st.markdown(f'''
                <div style="margin-bottom: 24px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <div>
                            <span style="font-weight: 500; font-size: 16px;">{goal["name"]}</span>
                            <span style="background-color: {priority_color[goal["priority"]]}; color: white; 
                                  padding: 2px 6px; border-radius: 4px; font-size: 12px; margin-left: 8px;">
                                {goal["priority"]}
                            </span>
                        </div>
                        <div style="color: var(--neutral-800);">${goal["current_saved"]:.2f} / ${goal["amount"]:.2f}</div>
                    </div>
                    
                    <div class="progress-container" style="height: 10px; margin-bottom: 8px;">
                        <div class="progress-bar" style="width: {progress}%; background-color: var(--primary);"></div>
                    </div>
                    
                    <div style="display: flex; justify-content: space-between; font-size: 13px; color: var(--neutral-500);">
                        <div>Target: {goal["target_date"]}</div>
                        <div>Monthly: ${goal["monthly_amount"]:.2f}</div>
                        <div>{progress:.1f}% Complete</div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Update progress form
                with st.expander(f"Update progress for '{goal['name']}'"):
                    col1, col2 = st.columns(2)
                    with col1:
                        add_amount = st.number_input(
                            "Add amount ($)", 
                            min_value=0.0,
                            step=10.0,
                            key=f"add_goal_{i}"
                        )
                    with col2:
                        if st.button("Update", key=f"update_goal_{i}"):
                            st.session_state.savings_goals[i]["current_saved"] += add_amount
                            st.success(f"Updated progress for {goal['name']}!")
                            st.rerun()
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">No financial goals set yet. Use the form above to create your first goal.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Savings Summary
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Savings Summary</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        # Calculate savings metrics
        if st.session_state.savings_goals:
            total_goals = len(st.session_state.savings_goals)
            total_target = sum(goal["amount"] for goal in st.session_state.savings_goals)
            total_saved = sum(goal["current_saved"] for goal in st.session_state.savings_goals)
            total_monthly_needed = sum(goal["monthly_amount"] for goal in st.session_state.savings_goals)
            overall_progress = (total_saved / total_target * 100) if total_target > 0 else 0
            
            st.markdown(f'''
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Active Goals</div>
                    <div class="metric-value">{total_goals}</div>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Total Savings Target</div>
                    <div class="metric-value">${total_target:.2f}</div>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Total Saved</div>
                    <div class="metric-value">${total_saved:.2f}</div>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Monthly Required</div>
                    <div class="metric-value">${total_monthly_needed:.2f}</div>
                </div>
                
                <div style="margin-bottom: 16px;">
                    <div class="metric-label">Overall Progress</div>
                    <div class="progress-container">
                        <div class="progress-bar" style="width: {overall_progress}%; background-color: var(--primary);"></div>
                    </div>
                    <div class="progress-stats">
                        <span>0%</span>
                        <span>50%</span>
                        <span>100%</span>
                    </div>
                </div>
            ''', unsafe_allow_html=True)
            
            # Compare against savings target from expenses tab
            remaining_income = st.session_state.salary - sum(expense["amount"] for expense in st.session_state.expenses) if st.session_state.expenses else st.session_state.salary
            
            if total_monthly_needed > st.session_state.savings_target:
                st.markdown(f'''
                    <div class="alert alert-warning">
                        <p style="margin: 0;">Your monthly goals ({total_monthly_needed:.2f}) exceed your savings target (${st.session_state.savings_target:.2f}).</p>
                    </div>
                ''', unsafe_allow_html=True)
            
            if total_monthly_needed > remaining_income:
                st.markdown(f'''
                    <div class="alert alert-danger">
                        <p style="margin: 0;">Your monthly goals (${total_monthly_needed:.2f}) exceed your remaining income after expenses (${remaining_income:.2f}).</p>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">Create financial goals to see your savings summary.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Savings Tips
        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Savings Tips</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        savings_tips = [
            "Follow the 50/30/20 rule: 50% needs, 30% wants, 20% savings.",
            "Set up automatic transfers to your savings account on payday.",
            "Review and cancel unused subscriptions.",
            "Use the 24-hour rule for impulse purchases.",
            "Meal prep to reduce food expenses.",
            "Create specific accounts for each savings goal.",
            "Increase your retirement contributions by 1% annually.",
            "Keep an emergency fund of 3-6 months of expenses."
        ]
        
        tip_index = int(datetime.datetime.now().day) % len(savings_tips)
        
        st.markdown(f'''
            <div class="quote-box">
                <p style="margin: 0; font-style: italic;">"{savings_tips[tip_index]}"</p>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Reports Tab
with tabs[5]:
    st.markdown("### Financial Reports")
    
    # Time period selection
    report_period = st.selectbox(
        "Select Report Period",
        ["Current Month", "Last Month", "Last 3 Months", "Year to Date", "Last Year"]
    )
    
    # Create report date range
    today = datetime.datetime.now().date()
    if report_period == "Current Month":
        start_date = datetime.date(today.year, today.month, 1)
        end_date = today
    elif report_period == "Last Month":
        first_day_current = date(today.year, today.month, 1)
        last_month = first_day_current - datetime.timedelta(days=1)
        start_date = datetime.date(last_month.year, last_month.month, 1)
        end_date = last_month
    elif report_period == "Last 3 Months":
        start_date = today - datetime.timedelta(days=90)
        end_date = today
    elif report_period == "Year to Date":
        start_date = datetime.date(today.year, 1, 1)
        end_date = today
    else:  # Last Year
        start_date = datetime.date(today.year - 1, 1, 1)
        end_date = datetime.date(today.year - 1, 12, 31)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Spending Trends
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Spending Trends</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.daily_expenses:
            # Convert to DataFrame for analysis
            df_expenses = pd.DataFrame(st.session_state.daily_expenses)
            df_expenses['date'] = pd.to_datetime(df_expenses['date'])
            
            # Filter by date range
            filtered_expenses = df_expenses[
                (df_expenses['date'] >= pd.Timestamp(start_date)) & 
                (df_expenses['date'] <= pd.Timestamp(end_date))
            ]
            
            if not filtered_expenses.empty:
                # Group by date and calculate daily totals
                daily_totals = filtered_expenses.groupby(filtered_expenses['date'].dt.date)['amount'].sum().reset_index()
                daily_totals['date'] = pd.to_datetime(daily_totals['date'])
                
                # Create time series chart
                fig = px.line(
                    daily_totals,
                    x='date',
                    y='amount',
                    title=f'Daily Spending ({start_date} to {end_date})',
                    labels={'amount': 'Amount ($)', 'date': 'Date'},
                )
                fig.update_layout(
                    margin=dict(l=0, r=0, t=30, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Category breakdown
                cat_totals = filtered_expenses.groupby('category')['amount'].sum().reset_index()
                cat_totals = cat_totals.sort_values('amount', ascending=False)
                
                # Create pie chart
                fig = px.pie(
                    cat_totals,
                    values='amount',
                    names='category',
                    title=f'Spending by Category ({report_period})',
                )
                fig.update_layout(
                    margin=dict(l=0, r=0, t=30, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown('''
                    <div class="info-box">
                        <p style="margin: 0; font-size: 14px;">No transactions found for the selected date range.</p>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">Record transactions to see spending trends.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Report Summary
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Report Summary</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.session_state.daily_expenses:
            # Convert to DataFrame for analysis
            df_summary = pd.DataFrame(st.session_state.daily_expenses)
            df_summary['date'] = pd.to_datetime(df_summary['date'])
            
            # Filter by date range
            filtered_summary = df_summary[
                (df_summary['date'] >= pd.Timestamp(start_date)) & 
                (df_summary['date'] <= pd.Timestamp(end_date))
            ]
            
            if not filtered_summary.empty:
                # Calculate metrics
                total_spent = filtered_summary['amount'].sum()
                avg_daily = total_spent / max((end_date - start_date).days, 1)
                max_day_amount = filtered_summary.groupby(filtered_summary['date'].dt.date)['amount'].sum().max()
                max_transaction = filtered_summary['amount'].max()
                top_category = filtered_summary.groupby('category')['amount'].sum().idxmax()
                
                st.markdown(f'''
                    <div style="margin-bottom: 16px;">
                        <div class="metric-label">Total Spent</div>
                        <div class="metric-value">${total_spent:.2f}</div>
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <div class="metric-label">Average Daily</div>
                        <div class="metric-value">${avg_daily:.2f}</div>
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <div class="metric-label">Highest Spending Day</div>
                        <div class="metric-value">${max_day_amount:.2f}</div>
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <div class="metric-label">Largest Transaction</div>
                        <div class="metric-value">${max_transaction:.2f}</div>
                    </div>
                    
                    <div style="margin-bottom: 16px;">
                        <div class="metric-label">Top Spending Category</div>
                        <div class="metric-value">{top_category}</div>
                    </div>
                ''', unsafe_allow_html=True)
                
                # Generate downloadable report
                st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
                st.markdown("<h5 style='margin-bottom: 12px; color: var(--neutral-700);'>Export Report</h5>", unsafe_allow_html=True)
                
                if st.button("Download Report CSV"):
                    # This would normally generate a downloadable file
                    st.success("Report ready for download!")
                    
                    # For demonstration purposes, display the data
                    st.dataframe(filtered_summary[['description', 'amount', 'category', 'date']])
            else:
                st.markdown('''
                    <div class="info-box">
                        <p style="margin: 0; font-size: 14px;">No transactions found for the selected date range.</p>
                    </div>
                ''', unsafe_allow_html=True)
        else:
            st.markdown('''
                <div class="info-box">
                    <p style="margin: 0; font-size: 14px;">Record transactions to see report summary.</p>
                </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

# Settings Tab
with tabs[6]:
    st.markdown("### App Settings")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Theme Settings
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Theme Settings</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        theme = st.selectbox(
            "Color Theme",
            ["Default", "Dark Mode", "Light Mode", "Blue", "Green"],
            index=0
        )
        
        currency = st.selectbox(
            "Currency",
            ["USD ($)", "EUR (€)", "GBP (£)", "JPY (¥)", "CAD ($)"],
            index=0
        )
        
        date_format = st.selectbox(
            "Date Format",
            ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"],
            index=0
        )
        
        if st.button("Save Settings"):
            st.session_state.theme = theme
            st.session_state.currency = currency
            st.session_state.date_format = date_format
            st.success("Settings saved!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Data Management
        st.markdown('''<div class="dashboard-card">
            <div class="card-header">
                <h3 class="card-title">Data Management</h3>
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown('''
            <div style="margin-bottom: 16px;">
                <p style="margin: 0; font-size: 15px;">Export your data for backup or transfer.</p>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button("Export All Data"):
            # This would normally generate a downloadable file
            st.success("Data ready for download!")
            
            # For demonstration, show sample of what would be exported
            export_data = {
                "salary": st.session_state.salary,
                "expenses": st.session_state.expenses[:2] if st.session_state.expenses else [],
                "daily_expenses": st.session_state.daily_expenses[:2] if st.session_state.daily_expenses else [],
                "savings_goals": st.session_state.savings_goals[:2] if st.session_state.savings_goals else []
            }
            st.json(export_data)
        
        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        st.markdown('''
            <div style="margin-bottom: 16px;">
                <p style="margin: 0; font-size: 15px;">Import data from backup file.</p>
            </div>
        ''', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Upload backup file", type=["json"])
        if uploaded_file is not None:
            st.success("Data imported successfully!")
        
        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        
        with st.expander("Reset Application Data"):
            st.warning("This will delete all your financial data. This action cannot be undone.")
            if st.button("Reset All Data", key="reset_data"):
                # Clear session state variables
                st.warning("All data has been reset.")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# Add custom CSS for dashboard styling
st.markdown('''
<style>
:root {
    --primary: #3d5a80;
    --primary-light: #98c1d9;
    --primary-dark: #293241;
    --secondary: #ee6c4d;
    --success: #38b000;
    --warning: #ffb703;
    --danger: #d00000;
    --neutral-100: #f8f9fa;
    --neutral-200: #e9ecef;
    --neutral-300: #dee2e6;
    --neutral-400: #ced4da;
    --neutral-500: #adb5bd;
    --neutral-600: #6c757d;
    --neutral-700: #495057;
    --neutral-800: #343a40;
    --neutral-900: #212529;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    white-space: pre-wrap;
    background-color: white;
    border-radius: 4px;
    color: var(--neutral-700);
    border: 1px solid var(--neutral-300);
}

.stTabs [aria-selected="true"] {
    background-color: var(--primary) !important;
    color: white !important;
}

.dashboard-card {
    background-color: white;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 16px;
}

.card-header {
    margin-bottom: 16px;
    border-bottom: 1px solid var(--neutral-200);
    padding-bottom: 12px;
}

.card-title {
    margin: 0;
    color: var(--neutral-800);
    font-size: 18px;
    font-weight: 600;
}

.metric-label {
    font-size: 14px;
    color: var(--neutral-700); /* Darkened from 600 to 700 for better contrast */
    margin-bottom: 4px;
    font-weight: 500; /* Added font weight for better visibility */
}

.metric-value {
    font-size: 20px;
    font-weight: 600;
    color: var(--neutral-900); /* Darkened from 800 to 900 for better contrast */
}

.info-box {
    background-color: var(--neutral-100);
    border-left: 4px solid var(--primary-light);
    padding: 12px;
    border-radius: 4px;
}

.info-box p {
    color: var(--neutral-800) !important; /* Force darker text in info boxes */
}

.alert {
    padding: 12px;
    border-radius: 4px;
    margin-top: 16px;
}

.alert-warning {
    background-color: #fff3cd;
    border-left: 4px solid var(--warning);
    color: #856404; /* Added darker text color for better contrast */
}

.alert-danger {
    background-color: #f8d7da;
    border-left: 4px solid var(--danger);
    color: #721c24; /* Added darker text color for better contrast */
}
            
[class^="stAlert"] {  /* Selects any class that starts with "stAlert" */
    background-color: rgba(4, 102, 200, 0.1) !important;
    color: var(--success) !important;
    padding: 10px;
    border-radius: 5px;
}

.progress-container {
    height: 8px;
    background-color: var(--neutral-200);
    border-radius: 4px;
    margin: 8px 0;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    background-color: var(--primary);
    border-radius: 4px;
    transition: width 0.3s ease;
}

.progress-stats {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: var(--neutral-700); /* Darkened from 500 to 700 for better contrast */
    font-weight: 500; /* Added font weight for better visibility */
}

.transaction-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 0;
    border-bottom: 1px solid var(--neutral-200);
}

.transaction-icon {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background-color: var(--primary);
    color: white; /* Changed from primary-dark to white for better contrast */
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 12px;
    font-size: 16px;
    font-weight: bold; /* Added font weight for better visibility */
}

.transaction-details {
    flex: 1;
}

.transaction-title {
    font-weight: 500;
    color: var(--neutral-900); /* Darkened from 800 to 900 for better contrast */
}

.transaction-meta {
    font-size: 12px;
    color: var(--neutral-700); /* Darkened from 500 to 700 for better contrast */
    font-weight: 500; /* Added font weight for better visibility */
}

.transaction-amount {
    font-weight: 600;
    color: var(--neutral-900); /* Darkened from 800 to 900 for better contrast */
}

.quote-box {
    background-color: var(--neutral-100);
    border-left: 4px solid var(--secondary);
    padding: 16px;
    border-radius: 4px;
}

.quote-box p {
    color: var(--neutral-800) !important; /* Force darker text in quote boxes */
}

/* Custom form styling */
.stTextInput > div > div > input {
    border-radius: 4px;
}

.stNumberInput > div > div > input {
    border-radius: 4px;
}

.stButton > button {
    border-radius: 4px;
    background-color: var(--primary);
    color: white;
}

.stButton > button:hover {
    background-color: var(--primary-dark);
}

/* Additional styles for better visibility */
.stSelectbox label, .stDateInput label, .stNumberInput label {
    color: var(--neutral-800) !important; /* Ensure form labels are visible */
}

/* Fix for progress bar text */
.metric-label + .metric-value + .progress-container + .progress-stats span {
    color: var(--neutral-800);
    font-weight: 500;
}

/* Fix for category breakdown text */
div[style*="display: flex; justify-content: space-between; margin-bottom: 8px;"] span {
    color: var(--neutral-800) !important;
}

/* Additional fix for any light text on white backgrounds */
p, span, div {
    color: inherit;
}

h5, h4, h3 {
    color: var(--neutral-800) !important;
}
            
.stCheckbox label {
    color: blue !important; /* Force the text to be blue */
    font-size: 14px !important;
    opacity: 2 !important;
    visibility: visible !important;
    user-select: text !important; /* Allow text selection */
}

/* Style the container to ensure everything stays inline */
.stCheckbox div {
    display: inline-block !important; 
    margin-right: 8px !important; 
    background-color: white !important; 
}

/* Ensure the checkbox label is on top */
.stCheckbox div > label {
    position: relative !important;
    z-index: 10 !important;
}
            
</style>
''', unsafe_allow_html=True)