"""
E-Commerce Business Analytics Dashboard
Professional Streamlit dashboard for e-commerce performance analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
from data_loader import (
    load_raw_datasets, 
    clean_and_prepare_data, 
    filter_delivered_orders,
    filter_by_date_range
)
from business_metrics import (
    calculate_revenue_metrics,
    calculate_monthly_trends,
    analyze_product_performance,
    analyze_geographic_performance,
    analyze_customer_satisfaction,
    analyze_delivery_performance
)
from dashboard_utils import (
    create_kpi_card,
    create_revenue_trend_chart,
    create_category_bar_chart,
    create_geographic_map,
    create_satisfaction_delivery_chart,
    format_currency,
    calculate_trend_indicator
)

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E8B57;
        margin-bottom: 0;
    }
    .kpi-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e6ed;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #6B7280;
        margin: 0;
    }
    .trend-positive {
        color: #10B981;
    }
    .trend-negative {
        color: #EF4444;
    }
    .trend-neutral {
        color: #6B7280;
    }
    .bottom-card {
        background: white;
        padding: 2rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e6ed;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        height: 160px;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-large {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
    }
    .metric-subtitle {
        font-size: 1rem;
        color: #6B7280;
        margin-top: 0.5rem;
    }
    .stars {
        color: #FCD34D;
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_prepare_data():
    """Load and prepare data with caching for better performance"""
    try:
        # Load raw datasets
        raw_datasets = load_raw_datasets('ecommerce_data/')
        
        # Clean and prepare combined dataset
        sales_data = clean_and_prepare_data(raw_datasets)
        
        # Filter for delivered orders only
        delivered_orders = filter_delivered_orders(sales_data)
        
        return delivered_orders
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def main():
    # Load data
    delivered_orders = load_and_prepare_data()
    
    if delivered_orders.empty:
        st.error("No data available. Please check your data files.")
        return
    
    # Get available years and months from data
    delivered_orders['year'] = delivered_orders['order_purchase_timestamp'].dt.year
    delivered_orders['month'] = delivered_orders['order_purchase_timestamp'].dt.month
    
    available_years = sorted(delivered_orders['year'].unique(), reverse=True)
    available_months = ['All Months'] + list(range(1, 13))
    month_names = ['All Months', 'January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    # Header with title and filters
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<h1 class="main-header">E-Commerce Analytics Dashboard</h1>', 
                   unsafe_allow_html=True)
    
    with col2:
        # Year and month dropdowns
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            selected_year = st.selectbox(
                "Year",
                options=available_years,
                index=available_years.index(2023) if 2023 in available_years else 0,
                key="year_filter"
            )
        
        with filter_col2:
            selected_month = st.selectbox(
                "Month",
                options=available_months,
                format_func=lambda x: month_names[available_months.index(x)],
                index=0,  # All Months (index 0)
                key="month_filter"
            )
    
    # Filter data by selected year and month
    if selected_month == 'All Months':
        # Filter by year only (all months)
        filtered_data = delivered_orders[
            delivered_orders['year'] == selected_year
        ].copy()
        
        # Get comparison period (all months from previous year)
        comparison_year = selected_year - 1
        comparison_data = delivered_orders[
            delivered_orders['year'] == comparison_year
        ].copy()
    else:
        # Filter by specific year and month
        filtered_data = delivered_orders[
            (delivered_orders['year'] == selected_year) &
            (delivered_orders['month'] == selected_month)
        ].copy()
        
        # Get comparison period (same month, previous year)
        comparison_year = selected_year - 1
        comparison_data = delivered_orders[
            (delivered_orders['year'] == comparison_year) &
            (delivered_orders['month'] == selected_month)
        ].copy()
    
    if filtered_data.empty:
        st.warning("No data available for the selected date range.")
        return
    
    # Calculate metrics for current and comparison periods
    current_metrics = {
        'total_revenue': filtered_data['price'].sum(),
        'total_orders': filtered_data['order_id'].nunique(),
        'total_customers': filtered_data['customer_id'].nunique(),
        'avg_order_value': filtered_data.groupby('order_id')['price'].sum().mean()
    }
    
    # Calculate monthly growth for current period
    current_period_monthly = filtered_data.groupby(
        filtered_data['order_purchase_timestamp'].dt.to_period('M')
    )['price'].sum()
    
    monthly_growth = current_period_monthly.pct_change().mean() * 100 if len(current_period_monthly) > 1 else 0
    
    # Calculate comparison metrics if data available
    if not comparison_data.empty:
        comparison_metrics = {
            'total_revenue': comparison_data['price'].sum(),
            'total_orders': comparison_data['order_id'].nunique(),
            'avg_order_value': comparison_data.groupby('order_id')['price'].sum().mean()
        }
        
        # Calculate trends
        revenue_trend = ((current_metrics['total_revenue'] - comparison_metrics['total_revenue']) / 
                        comparison_metrics['total_revenue'] * 100) if comparison_metrics['total_revenue'] > 0 else 0
        
        orders_trend = ((current_metrics['total_orders'] - comparison_metrics['total_orders']) / 
                       comparison_metrics['total_orders'] * 100) if comparison_metrics['total_orders'] > 0 else 0
        
        aov_trend = ((current_metrics['avg_order_value'] - comparison_metrics['avg_order_value']) / 
                    comparison_metrics['avg_order_value'] * 100) if comparison_metrics['avg_order_value'] > 0 else 0
    else:
        revenue_trend = orders_trend = aov_trend = 0
    
    # KPI Row - 4 cards
    st.markdown("---")
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        trend_class = "trend-positive" if revenue_trend > 0 else "trend-negative" if revenue_trend < 0 else "trend-neutral"
        trend_arrow = "↗" if revenue_trend > 0 else "↘" if revenue_trend < 0 else "→"
        
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-label">Total Revenue</p>
            <p class="kpi-value">{format_currency(current_metrics['total_revenue'])}</p>
            <p class="{trend_class}">{trend_arrow} {abs(revenue_trend):.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col2:
        trend_class = "trend-positive" if monthly_growth > 0 else "trend-negative" if monthly_growth < 0 else "trend-neutral"
        trend_arrow = "↗" if monthly_growth > 0 else "↘" if monthly_growth < 0 else "→"
        
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-label">Monthly Growth</p>
            <p class="kpi-value">{abs(monthly_growth):.2f}%</p>
            <p class="{trend_class}">{trend_arrow} Monthly Avg</p>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col3:
        trend_class = "trend-positive" if aov_trend > 0 else "trend-negative" if aov_trend < 0 else "trend-neutral"
        trend_arrow = "↗" if aov_trend > 0 else "↘" if aov_trend < 0 else "→"
        
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-label">Average Order Value</p>
            <p class="kpi-value">{format_currency(current_metrics['avg_order_value'])}</p>
            <p class="{trend_class}">{trend_arrow} {abs(aov_trend):.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with kpi_col4:
        trend_class = "trend-positive" if orders_trend > 0 else "trend-negative" if orders_trend < 0 else "trend-neutral"
        trend_arrow = "↗" if orders_trend > 0 else "↘" if orders_trend < 0 else "→"
        
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-label">Total Orders</p>
            <p class="kpi-value">{current_metrics['total_orders']:,}</p>
            <p class="{trend_class}">{trend_arrow} {abs(orders_trend):.2f}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts Grid - 2x2 layout
    st.markdown("---")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Revenue trend line chart
        st.subheader("Revenue Trend")
        revenue_chart = create_revenue_trend_chart(filtered_data, comparison_data)
        st.plotly_chart(revenue_chart, use_container_width=True)
    
    with chart_col2:
        # Top 10 categories bar chart
        st.subheader("Top 10 Product Categories")
        if 'product_category_name' in filtered_data.columns:
            category_chart = create_category_bar_chart(filtered_data)
            st.plotly_chart(category_chart, use_container_width=True)
        else:
            st.info("Product category data not available")
    
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        # Revenue by state choropleth map
        st.subheader("Revenue by State")
        if 'customer_state' in filtered_data.columns:
            geo_chart = create_geographic_map(filtered_data)
            st.plotly_chart(geo_chart, use_container_width=True)
        else:
            st.info("Geographic data not available")
    
    with chart_col4:
        # Satisfaction vs delivery time
        st.subheader("Satisfaction vs Delivery Time")
        if 'review_score' in filtered_data.columns and 'delivery_days' in filtered_data.columns:
            satisfaction_chart = create_satisfaction_delivery_chart(filtered_data)
            st.plotly_chart(satisfaction_chart, use_container_width=True)
        else:
            st.info("Review or delivery data not available")
    
    # Bottom Row - 2 cards
    st.markdown("---")
    bottom_col1, bottom_col2 = st.columns(2)
    
    with bottom_col1:
        # Average delivery time
        if 'delivery_days' in filtered_data.columns:
            avg_delivery = filtered_data['delivery_days'].mean()
            
            # Calculate delivery trend if comparison data available
            if 'delivery_days' in comparison_data.columns and not comparison_data.empty:
                comparison_delivery = comparison_data['delivery_days'].mean()
                delivery_trend = ((avg_delivery - comparison_delivery) / comparison_delivery * 100) if comparison_delivery > 0 else 0
                trend_class = "trend-negative" if delivery_trend > 0 else "trend-positive" if delivery_trend < 0 else "trend-neutral"
                trend_arrow = "↗" if delivery_trend > 0 else "↘" if delivery_trend < 0 else "→"
            else:
                delivery_trend = 0
                trend_class = "trend-neutral"
                trend_arrow = "→"
            
            st.markdown(f"""
            <div class="bottom-card">
                <p class="metric-large">{avg_delivery:.1f}</p>
                <p class="metric-subtitle">Average Delivery Time (days)</p>
                <p class="{trend_class}">{trend_arrow} {abs(delivery_trend):.2f}%</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="bottom-card">
                <p class="metric-subtitle">Delivery data not available</p>
            </div>
            """, unsafe_allow_html=True)
    
    with bottom_col2:
        # Review Score with stars
        if 'review_score' in filtered_data.columns:
            avg_review = filtered_data['review_score'].mean()
            stars = "★" * int(round(avg_review))
            
            st.markdown(f"""
            <div class="bottom-card">
                <p class="metric-large">{avg_review:.1f}</p>
                <p class="stars">{stars}</p>
                <p class="metric-subtitle">Average Review Score</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="bottom-card">
                <p class="metric-subtitle">Review data not available</p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()