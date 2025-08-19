"""
Data Loading and Processing Module

This module contains functions for loading, cleaning, and preparing
e-commerce data for analysis.
"""

import pandas as pd
from typing import Dict, Tuple, Optional
import warnings


def load_raw_datasets(data_path: str = 'ecommerce_data/') -> Dict[str, pd.DataFrame]:
    """
    Load all raw CSV datasets from the specified path.
    
    Args:
        data_path (str): Path to the directory containing CSV files
        
    Returns:
        Dict[str, pd.DataFrame]: Dictionary containing all loaded datasets
    """
    datasets = {}
    
    file_mapping = {
        'orders': 'orders_dataset.csv',
        'order_items': 'order_items_dataset.csv',
        'products': 'products_dataset.csv',
        'customers': 'customers_dataset.csv',
        'reviews': 'order_reviews_dataset.csv',
        'payments': 'order_payments_dataset.csv'
    }
    
    for key, filename in file_mapping.items():
        try:
            datasets[key] = pd.read_csv(f"{data_path}{filename}")
            print(f"Loaded {key}: {datasets[key].shape[0]} rows, {datasets[key].shape[1]} columns")
        except FileNotFoundError:
            print(f"Warning: {filename} not found in {data_path}")
            
    return datasets


def clean_and_prepare_data(datasets: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Clean and prepare the combined sales dataset for analysis.
    
    Args:
        datasets (Dict[str, pd.DataFrame]): Dictionary of raw datasets
        
    Returns:
        pd.DataFrame: Cleaned and prepared sales dataset
    """
    # Extract required datasets
    orders = datasets['orders'].copy()
    order_items = datasets['order_items'].copy()
    products = datasets['products'].copy()
    customers = datasets['customers'].copy()
    reviews = datasets['reviews'].copy()
    
    # Create initial sales data by merging orders and order_items
    sales_data = pd.merge(
        order_items[['order_id', 'order_item_id', 'product_id', 'price']],
        orders[['order_id', 'order_status', 'order_purchase_timestamp', 
                'order_delivered_customer_date', 'customer_id']],
        on='order_id'
    )
    
    # Convert timestamp columns to datetime
    sales_data['order_purchase_timestamp'] = pd.to_datetime(sales_data['order_purchase_timestamp'])
    sales_data['order_delivered_customer_date'] = pd.to_datetime(sales_data['order_delivered_customer_date'])
    
    # Add date components
    sales_data['year'] = sales_data['order_purchase_timestamp'].dt.year
    sales_data['month'] = sales_data['order_purchase_timestamp'].dt.month
    sales_data['quarter'] = sales_data['order_purchase_timestamp'].dt.quarter
    
    # Add product information
    sales_data = pd.merge(
        sales_data,
        products[['product_id', 'product_category_name']],
        on='product_id',
        how='left'
    )
    
    # Add customer information
    sales_data = pd.merge(
        sales_data,
        customers[['customer_id', 'customer_state', 'customer_city']],
        on='customer_id',
        how='left'
    )
    
    # Add review information
    sales_data = pd.merge(
        sales_data,
        reviews[['order_id', 'review_score']],
        on='order_id',
        how='left'
    )
    
    return sales_data


def filter_delivered_orders(sales_data: pd.DataFrame) -> pd.DataFrame:
    """
    Filter dataset to include only delivered orders.
    
    Args:
        sales_data (pd.DataFrame): Combined sales dataset
        
    Returns:
        pd.DataFrame: Filtered dataset with delivered orders only
    """
    delivered_data = sales_data[sales_data['order_status'] == 'delivered'].copy()
    
    # Calculate delivery speed for delivered orders
    delivered_data['delivery_days'] = (
        delivered_data['order_delivered_customer_date'] - 
        delivered_data['order_purchase_timestamp']
    ).dt.days
    
    # Categorize delivery speed
    def categorize_delivery_speed(days):
        if pd.isna(days):
            return 'Unknown'
        elif days <= 3:
            return '1-3 days'
        elif days <= 7:
            return '4-7 days'
        else:
            return '8+ days'
    
    delivered_data['delivery_category'] = delivered_data['delivery_days'].apply(categorize_delivery_speed)
    
    print(f"Filtered to {delivered_data.shape[0]} delivered orders from {sales_data.shape[0]} total orders")
    
    return delivered_data


def filter_by_date_range(data: pd.DataFrame, 
                        start_year: Optional[int] = None, 
                        end_year: Optional[int] = None,
                        start_month: Optional[int] = None, 
                        end_month: Optional[int] = None) -> pd.DataFrame:
    """
    Filter dataset by date range.
    
    Args:
        data (pd.DataFrame): Dataset to filter
        start_year (int, optional): Starting year (inclusive)
        end_year (int, optional): Ending year (inclusive)
        start_month (int, optional): Starting month (1-12, inclusive)
        end_month (int, optional): Ending month (1-12, inclusive)
        
    Returns:
        pd.DataFrame: Filtered dataset
    """
    filtered_data = data.copy()
    
    if start_year is not None:
        filtered_data = filtered_data[filtered_data['year'] >= start_year]
    if end_year is not None:
        filtered_data = filtered_data[filtered_data['year'] <= end_year]
    if start_month is not None:
        filtered_data = filtered_data[filtered_data['month'] >= start_month]
    if end_month is not None:
        filtered_data = filtered_data[filtered_data['month'] <= end_month]
    
    date_range_desc = f"Years: {start_year or 'all'}-{end_year or 'all'}, Months: {start_month or 'all'}-{end_month or 'all'}"
    print(f"Filtered to {filtered_data.shape[0]} records for {date_range_desc}")
    
    return filtered_data


def get_data_summary(data: pd.DataFrame) -> Dict:
    """
    Generate summary statistics for the dataset.
    
    Args:
        data (pd.DataFrame): Dataset to summarize
        
    Returns:
        Dict: Summary statistics
    """
    summary = {
        'total_records': len(data),
        'unique_orders': data['order_id'].nunique(),
        'unique_customers': data['customer_id'].nunique(),
        'unique_products': data['product_id'].nunique(),
        'date_range': {
            'start': data['order_purchase_timestamp'].min(),
            'end': data['order_purchase_timestamp'].max()
        },
        'total_revenue': data['price'].sum(),
        'order_statuses': data['order_status'].value_counts().to_dict(),
        'product_categories': data['product_category_name'].nunique() if 'product_category_name' in data.columns else 0,
        'geographic_coverage': data['customer_state'].nunique() if 'customer_state' in data.columns else 0
    }
    
    return summary