"""
Business Metrics Calculation Module

This module contains functions for calculating various business metrics
from e-commerce data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, Union
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


def calculate_revenue_metrics(data: pd.DataFrame, 
                            current_period_filter: Dict = None,
                            comparison_period_filter: Dict = None) -> Dict:
    """
    Calculate revenue metrics for current period vs comparison period.
    
    Args:
        data (pd.DataFrame): Sales dataset
        current_period_filter (Dict): Filter criteria for current period (e.g., {'year': 2023})
        comparison_period_filter (Dict): Filter criteria for comparison period (e.g., {'year': 2022})
        
    Returns:
        Dict: Revenue metrics including totals, growth rates, and comparisons
    """
    results = {}
    
    # Filter data for current period
    if current_period_filter:
        current_data = data.copy()
        for key, value in current_period_filter.items():
            current_data = current_data[current_data[key] == value]
    else:
        current_data = data.copy()
    
    # Filter data for comparison period
    if comparison_period_filter:
        comparison_data = data.copy()
        for key, value in comparison_period_filter.items():
            comparison_data = comparison_data[comparison_data[key] == value]
    else:
        comparison_data = pd.DataFrame()  # Empty dataframe if no comparison period
    
    # Calculate current period metrics
    results['current_period'] = {
        'total_revenue': current_data['price'].sum(),
        'total_orders': current_data['order_id'].nunique(),
        'total_customers': current_data['customer_id'].nunique(),
        'average_order_value': current_data.groupby('order_id')['price'].sum().mean(),
        'period_description': str(current_period_filter) if current_period_filter else 'All data'
    }
    
    # Calculate comparison period metrics if available
    if not comparison_data.empty:
        results['comparison_period'] = {
            'total_revenue': comparison_data['price'].sum(),
            'total_orders': comparison_data['order_id'].nunique(),
            'total_customers': comparison_data['customer_id'].nunique(),
            'average_order_value': comparison_data.groupby('order_id')['price'].sum().mean(),
            'period_description': str(comparison_period_filter)
        }
        
        # Calculate growth rates
        results['growth_rates'] = {
            'revenue_growth': (
                (results['current_period']['total_revenue'] - results['comparison_period']['total_revenue']) /
                results['comparison_period']['total_revenue'] * 100
            ),
            'order_growth': (
                (results['current_period']['total_orders'] - results['comparison_period']['total_orders']) /
                results['comparison_period']['total_orders'] * 100
            ),
            'aov_growth': (
                (results['current_period']['average_order_value'] - results['comparison_period']['average_order_value']) /
                results['comparison_period']['average_order_value'] * 100
            )
        }
    
    return results


def calculate_monthly_trends(data: pd.DataFrame, year: int) -> pd.DataFrame:
    """
    Calculate monthly revenue trends for a specific year.
    
    Args:
        data (pd.DataFrame): Sales dataset
        year (int): Year to analyze
        
    Returns:
        pd.DataFrame: Monthly revenue data with growth rates
    """
    year_data = data[data['year'] == year].copy()
    
    # Group by month and calculate metrics
    monthly_metrics = year_data.groupby('month').agg({
        'price': 'sum',
        'order_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()
    
    monthly_metrics.columns = ['month', 'revenue', 'orders', 'customers']
    
    # Calculate month-over-month growth rates
    monthly_metrics['revenue_growth'] = monthly_metrics['revenue'].pct_change() * 100
    monthly_metrics['order_growth'] = monthly_metrics['orders'].pct_change() * 100
    
    # Add month names
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                   7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    monthly_metrics['month_name'] = monthly_metrics['month'].map(month_names)
    
    return monthly_metrics


def analyze_product_performance(data: pd.DataFrame) -> Dict:
    """
    Analyze product category performance.
    
    Args:
        data (pd.DataFrame): Sales dataset with product category information
        
    Returns:
        Dict: Product performance metrics by category
    """
    if 'product_category_name' not in data.columns:
        return {'error': 'Product category information not available'}
    
    category_metrics = data.groupby('product_category_name').agg({
        'price': ['sum', 'mean', 'count'],
        'order_id': 'nunique',
        'product_id': 'nunique'
    }).round(2)
    
    # Flatten column names
    category_metrics.columns = ['total_revenue', 'avg_price', 'total_items', 'unique_orders', 'unique_products']
    category_metrics = category_metrics.reset_index()
    
    # Sort by total revenue
    category_metrics = category_metrics.sort_values('total_revenue', ascending=False)
    
    # Calculate percentages
    total_revenue = category_metrics['total_revenue'].sum()
    category_metrics['revenue_share'] = (category_metrics['total_revenue'] / total_revenue * 100).round(2)
    
    return {
        'category_performance': category_metrics,
        'top_category': category_metrics.iloc[0]['product_category_name'],
        'total_categories': len(category_metrics)
    }


def analyze_geographic_performance(data: pd.DataFrame) -> Dict:
    """
    Analyze sales performance by geographic location (state).
    
    Args:
        data (pd.DataFrame): Sales dataset with customer state information
        
    Returns:
        Dict: Geographic performance metrics
    """
    if 'customer_state' not in data.columns:
        return {'error': 'Geographic information not available'}
    
    state_metrics = data.groupby('customer_state').agg({
        'price': ['sum', 'mean'],
        'order_id': 'nunique',
        'customer_id': 'nunique'
    }).round(2)
    
    # Flatten column names
    state_metrics.columns = ['total_revenue', 'avg_order_value', 'total_orders', 'unique_customers']
    state_metrics = state_metrics.reset_index()
    
    # Sort by total revenue
    state_metrics = state_metrics.sort_values('total_revenue', ascending=False)
    
    # Calculate percentages
    total_revenue = state_metrics['total_revenue'].sum()
    state_metrics['revenue_share'] = (state_metrics['total_revenue'] / total_revenue * 100).round(2)
    
    return {
        'state_performance': state_metrics,
        'top_state': state_metrics.iloc[0]['customer_state'],
        'total_states': len(state_metrics),
        'top_5_states': state_metrics.head(5)
    }


def analyze_customer_satisfaction(data: pd.DataFrame) -> Dict:
    """
    Analyze customer satisfaction metrics based on review scores.
    
    Args:
        data (pd.DataFrame): Sales dataset with review scores
        
    Returns:
        Dict: Customer satisfaction metrics
    """
    if 'review_score' not in data.columns:
        return {'error': 'Review score information not available'}
    
    # Remove duplicates to get unique order reviews
    review_data = data[['order_id', 'review_score']].drop_duplicates()
    
    satisfaction_metrics = {
        'average_score': review_data['review_score'].mean(),
        'median_score': review_data['review_score'].median(),
        'score_distribution': review_data['review_score'].value_counts().sort_index().to_dict(),
        'total_reviews': len(review_data),
        'satisfaction_rate': (review_data['review_score'] >= 4).sum() / len(review_data) * 100
    }
    
    return satisfaction_metrics


def analyze_delivery_performance(data: pd.DataFrame) -> Dict:
    """
    Analyze delivery performance metrics.
    
    Args:
        data (pd.DataFrame): Sales dataset with delivery information
        
    Returns:
        Dict: Delivery performance metrics
    """
    if 'delivery_days' not in data.columns:
        return {'error': 'Delivery information not available'}
    
    # Filter out orders with missing delivery dates
    delivery_data = data.dropna(subset=['delivery_days'])
    
    delivery_metrics = {
        'average_delivery_days': delivery_data['delivery_days'].mean(),
        'median_delivery_days': delivery_data['delivery_days'].median(),
        'delivery_categories': delivery_data['delivery_category'].value_counts().to_dict() if 'delivery_category' in data.columns else {},
        'on_time_percentage': (delivery_data['delivery_days'] <= 7).sum() / len(delivery_data) * 100
    }
    
    # Analyze relationship between delivery speed and satisfaction
    if 'review_score' in data.columns:
        delivery_satisfaction = delivery_data.groupby('delivery_category')['review_score'].mean().to_dict()
        delivery_metrics['satisfaction_by_delivery_speed'] = delivery_satisfaction
    
    return delivery_metrics


def calculate_order_status_metrics(data: pd.DataFrame) -> Dict:
    """
    Calculate order status distribution and metrics.
    
    Args:
        data (pd.DataFrame): Sales dataset with order status information
        
    Returns:
        Dict: Order status metrics
    """
    status_counts = data['order_status'].value_counts()
    status_percentages = (status_counts / status_counts.sum() * 100).round(2)
    
    return {
        'status_counts': status_counts.to_dict(),
        'status_percentages': status_percentages.to_dict(),
        'total_orders': status_counts.sum(),
        'completion_rate': status_percentages.get('delivered', 0)
    }


def generate_comprehensive_report(data: pd.DataFrame,
                                analysis_year: int = 2023,
                                comparison_year: int = 2022) -> Dict:
    """
    Generate a comprehensive business metrics report.
    
    Args:
        data (pd.DataFrame): Complete sales dataset
        analysis_year (int): Primary year for analysis
        comparison_year (int): Comparison year for YoY metrics
        
    Returns:
        Dict: Comprehensive business metrics report
    """
    report = {
        'analysis_period': f'{analysis_year} vs {comparison_year}',
        'generated_at': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Revenue metrics
    report['revenue_metrics'] = calculate_revenue_metrics(
        data,
        current_period_filter={'year': analysis_year},
        comparison_period_filter={'year': comparison_year}
    )
    
    # Monthly trends
    report['monthly_trends'] = calculate_monthly_trends(data, analysis_year)
    
    # Product performance
    analysis_data = data[data['year'] == analysis_year]
    report['product_performance'] = analyze_product_performance(analysis_data)
    
    # Geographic performance
    report['geographic_performance'] = analyze_geographic_performance(analysis_data)
    
    # Customer satisfaction
    report['customer_satisfaction'] = analyze_customer_satisfaction(analysis_data)
    
    # Delivery performance
    report['delivery_performance'] = analyze_delivery_performance(analysis_data)
    
    # Order status metrics
    report['order_status'] = calculate_order_status_metrics(analysis_data)
    
    return report