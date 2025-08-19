"""
Dashboard Utilities Module

Utility functions for creating charts and formatting data for the Streamlit dashboard.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.colors as colors


def format_currency(value):
    """
    Format currency values with appropriate units (K, M, B).
    
    Args:
        value (float): The value to format
        
    Returns:
        str: Formatted currency string
    """
    if pd.isna(value) or value == 0:
        return "$0"
    
    abs_value = abs(value)
    if abs_value >= 1e9:
        return f"${value/1e9:.1f}B"
    elif abs_value >= 1e6:
        return f"${value/1e6:.1f}M"
    elif abs_value >= 1e3:
        return f"${value/1e3:.0f}K"
    else:
        return f"${value:.0f}"


def calculate_trend_indicator(current_value, previous_value):
    """
    Calculate trend percentage and direction.
    
    Args:
        current_value (float): Current period value
        previous_value (float): Previous period value
        
    Returns:
        tuple: (percentage_change, direction, css_class)
    """
    if pd.isna(previous_value) or previous_value == 0:
        return 0.0, "→", "trend-neutral"
    
    change = ((current_value - previous_value) / previous_value) * 100
    
    if change > 0:
        return change, "↗", "trend-positive"
    elif change < 0:
        return abs(change), "↘", "trend-negative"
    else:
        return 0.0, "→", "trend-neutral"


def create_kpi_card(title, value, trend_pct, trend_direction):
    """
    Create HTML for KPI card.
    
    Args:
        title (str): KPI title
        value (str): Formatted KPI value
        trend_pct (float): Trend percentage
        trend_direction (str): Trend direction arrow
        
    Returns:
        str: HTML string for KPI card
    """
    trend_class = "trend-positive" if trend_direction == "↗" else "trend-negative" if trend_direction == "↘" else "trend-neutral"
    
    return f"""
    <div class="kpi-card">
        <p class="kpi-label">{title}</p>
        <p class="kpi-value">{value}</p>
        <p class="{trend_class}">{trend_direction} {trend_pct:.2f}%</p>
    </div>
    """


def create_revenue_trend_chart(current_data, comparison_data=None):
    """
    Create revenue trend line chart with current and previous period.
    
    Args:
        current_data (pd.DataFrame): Current period data
        comparison_data (pd.DataFrame): Previous period data (optional)
        
    Returns:
        plotly.graph_objects.Figure: Revenue trend chart
    """
    fig = go.Figure()
    
    # Current period revenue trend
    if not current_data.empty:
        monthly_revenue = current_data.groupby(
            current_data['order_purchase_timestamp'].dt.to_period('M')
        )['price'].sum().reset_index()
        
        monthly_revenue['month_str'] = monthly_revenue['order_purchase_timestamp'].astype(str)
        
        fig.add_trace(go.Scatter(
            x=monthly_revenue['month_str'],
            y=monthly_revenue['price'],
            mode='lines+markers',
            name='Current Period',
            line=dict(color='#2E8B57', width=3),
            marker=dict(size=8),
            hovertemplate='<b>%{x}</b><br>Revenue: %{customdata}<extra></extra>',
            customdata=[format_currency(val) for val in monthly_revenue['price']]
        ))
    
    # Previous period revenue trend (dashed line)
    if comparison_data is not None and not comparison_data.empty:
        comparison_monthly = comparison_data.groupby(
            comparison_data['order_purchase_timestamp'].dt.to_period('M')
        )['price'].sum().reset_index()
        
        comparison_monthly['month_str'] = comparison_monthly['order_purchase_timestamp'].astype(str)
        
        fig.add_trace(go.Scatter(
            x=comparison_monthly['month_str'],
            y=comparison_monthly['price'],
            mode='lines+markers',
            name='Previous Period',
            line=dict(color='#4682B4', width=2, dash='dash'),
            marker=dict(size=6),
            hovertemplate='<b>%{x}</b><br>Revenue: %{customdata}<extra></extra>',
            customdata=[format_currency(val) for val in comparison_monthly['price']]
        ))
    
    # Update layout
    fig.update_layout(
        title="",
        xaxis_title="Month",
        yaxis_title="Revenue",
        showlegend=True,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1,
            tickformat='$.0s'  # Format as $300K, $2M, etc.
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig


def create_category_bar_chart(data):
    """
    Create top 10 product categories bar chart with blue gradient.
    
    Args:
        data (pd.DataFrame): Sales data with product categories
        
    Returns:
        plotly.graph_objects.Figure: Category performance bar chart
    """
    if 'product_category_name' not in data.columns:
        # Return empty chart if no category data
        fig = go.Figure()
        fig.add_annotation(
            text="Product category data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Calculate category revenue
    category_revenue = data.groupby('product_category_name')['price'].sum().reset_index()
    category_revenue = category_revenue.sort_values('price', ascending=False).head(10)
    
    # Create blue gradient colors
    n_categories = len(category_revenue)
    blue_colors = colors.sample_colorscale('Blues', np.linspace(0.3, 1.0, n_categories))
    
    # Clean category names for display
    category_revenue['display_name'] = category_revenue['product_category_name'].str.replace('_', ' ').str.title()
    
    fig = go.Figure(data=[
        go.Bar(
            x=category_revenue['price'],
            y=category_revenue['display_name'],
            orientation='h',
            marker=dict(
                color=blue_colors,
                colorscale='Blues'
            ),
            hovertemplate='<b>%{y}</b><br>Revenue: %{customdata}<extra></extra>',
            customdata=[format_currency(val) for val in category_revenue['price']]
        )
    ])
    
    fig.update_layout(
        title="",
        xaxis_title="Revenue",
        yaxis_title="",
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(autorange="reversed"),  # Top category at top
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1,
            tickformat='$.0s'
        )
    )
    
    return fig


def create_geographic_map(data):
    """
    Create US choropleth map colored by revenue amount.
    
    Args:
        data (pd.DataFrame): Sales data with customer states
        
    Returns:
        plotly.graph_objects.Figure: Geographic revenue map
    """
    if 'customer_state' not in data.columns:
        # Return empty chart if no geographic data
        fig = go.Figure()
        fig.add_annotation(
            text="Geographic data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Calculate state-level revenue
    state_revenue = data.groupby('customer_state').agg({
        'price': 'sum',
        'order_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()
    
    state_revenue.columns = ['state', 'revenue', 'orders', 'customers']
    
    fig = go.Figure(data=go.Choropleth(
        locations=state_revenue['state'],
        z=state_revenue['revenue'],
        locationmode='USA-states',
        colorscale='Blues',
        hovertemplate='<b>%{locations}</b><br>' +
                      'Revenue: %{customdata[0]}<br>' +
                      'Orders: %{customdata[1]}<br>' +
                      'Customers: %{customdata[2]}<extra></extra>',
        customdata=np.column_stack([
            [format_currency(val) for val in state_revenue['revenue']],
            state_revenue['orders'],
            state_revenue['customers']
        ]),
        colorbar=dict(
            title="Revenue",
            tickformat='$.0s'
        )
    ))
    
    fig.update_layout(
        title="",
        geo=dict(
            scope='usa',
            projection_type='albers usa',
            showlakes=True,
            lakecolor='rgb(255, 255, 255)',
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(size=12)
    )
    
    return fig


def create_satisfaction_delivery_chart(data):
    """
    Create satisfaction vs delivery time bar chart.
    
    Args:
        data (pd.DataFrame): Sales data with review scores and delivery days
        
    Returns:
        plotly.graph_objects.Figure: Satisfaction vs delivery time chart
    """
    if 'review_score' not in data.columns or 'delivery_days' not in data.columns:
        # Return empty chart if no required data
        fig = go.Figure()
        fig.add_annotation(
            text="Review or delivery data not available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
    
    # Create delivery time buckets
    def categorize_delivery_time(days):
        if pd.isna(days):
            return 'Unknown'
        elif days <= 3:
            return '1-3 days'
        elif days <= 7:
            return '4-7 days'
        elif days <= 14:
            return '8-14 days'
        else:
            return '15+ days'
    
    # Filter out duplicate orders for accurate review analysis
    review_delivery = data[['order_id', 'delivery_days', 'review_score']].drop_duplicates(subset=['order_id'])
    review_delivery = review_delivery.dropna(subset=['delivery_days', 'review_score'])
    
    review_delivery['delivery_bucket'] = review_delivery['delivery_days'].apply(categorize_delivery_time)
    
    # Calculate average satisfaction by delivery bucket
    satisfaction_by_delivery = review_delivery.groupby('delivery_bucket')['review_score'].mean().reset_index()
    
    # Define order for delivery buckets
    bucket_order = ['1-3 days', '4-7 days', '8-14 days', '15+ days', 'Unknown']
    satisfaction_by_delivery['bucket_order'] = satisfaction_by_delivery['delivery_bucket'].apply(
        lambda x: bucket_order.index(x) if x in bucket_order else len(bucket_order)
    )
    satisfaction_by_delivery = satisfaction_by_delivery.sort_values('bucket_order')
    
    fig = go.Figure(data=[
        go.Bar(
            x=satisfaction_by_delivery['delivery_bucket'],
            y=satisfaction_by_delivery['review_score'],
            marker=dict(
                color='#2E8B57',
                opacity=0.8
            ),
            hovertemplate='<b>%{x}</b><br>Avg Review Score: %{y:.2f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="",
        xaxis_title="Delivery Time",
        yaxis_title="Average Review Score",
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(
            range=[1, 5],
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=1
        )
    )
    
    return fig