# E-Commerce Business Analytics Dashboard

A comprehensive analytics platform featuring both Jupyter notebook analysis and a professional Streamlit dashboard for e-commerce business performance evaluation with real-time KPIs and interactive visualizations.

## Overview

This project provides a complete analytics solution including:
1. **Refactored Jupyter Notebook**: Professional analysis framework with configurable date ranges
2. **Streamlit Dashboard**: Interactive web dashboard with real-time filtering and professional visualizations
3. **Modular Architecture**: Reusable data processing and business metrics modules

The analysis focuses on key business metrics including revenue performance, customer satisfaction, product category performance, and geographic insights.

## Project Structure

```
├── app.py                        # Streamlit dashboard application
├── dashboard_utils.py            # Dashboard chart generation utilities
├── EDA_Refactored.ipynb          # Main analysis notebook
├── data_loader.py                # Data loading and preprocessing functions
├── business_metrics.py           # Business metrics calculation functions  
├── requirements.txt              # Python dependencies (includes Streamlit)
├── README.md                     # This documentation
└── ecommerce_data/              # Data directory
    ├── orders_dataset.csv
    ├── order_items_dataset.csv
    ├── products_dataset.csv
    ├── customers_dataset.csv
    ├── order_reviews_dataset.csv
    └── order_payments_dataset.csv
```

## Key Improvements

### 1. Code Quality & Structure
- **Eliminated pandas warnings**: Fixed all SettingWithCopyWarning issues
- **Modular design**: Separated data processing and business logic into reusable modules
- **Consistent naming**: Implemented clear, descriptive variable and function names
- **Documentation**: Added comprehensive docstrings and comments

### 2. Enhanced Analytics Framework
- **Configurable analysis**: Easy date range modifications via configuration variables
- **Comprehensive metrics**: Revenue, growth rates, customer satisfaction, delivery performance
- **Geographic analysis**: State-level performance with interactive maps
- **Product insights**: Category performance and revenue distribution

### 3. Professional Visualizations
- **Business-oriented design**: Consistent color schemes and professional styling
- **Clear labeling**: Descriptive titles, axis labels, and value annotations
- **Interactive elements**: Plotly maps for geographic analysis
- **Multi-panel layouts**: Comprehensive dashboard-style presentations

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Data files in `ecommerce_data/` directory

### Option 1: Streamlit Dashboard (Recommended)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch dashboard**:
   ```bash
   streamlit run app.py
   ```

3. **Open in browser**: Dashboard opens automatically at `http://localhost:8501`

### Option 2: Jupyter Notebook Analysis

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Launch Jupyter**:
   ```bash
   jupyter notebook EDA_Refactored.ipynb
   ```

## 📊 Streamlit Dashboard Features

### Professional Layout
- **Header**: Global date range filter affecting all visualizations
- **KPI Row**: 4 key metrics with trend indicators (Revenue, Growth, AOV, Orders)
- **Charts Grid**: 2x2 interactive visualizations
- **Bottom Cards**: Delivery performance and review scores

### Interactive Features
- **Real-time Filtering**: Date range picker updates all charts instantly
- **Trend Indicators**: Color-coded arrows showing performance vs previous period
- **Professional Styling**: Clean cards with consistent heights and business colors
- **Responsive Charts**: Hover tooltips and formatted currency values

### Chart Types
1. **Revenue Trend**: Line chart with solid (current) and dashed (previous) period lines
2. **Top Categories**: Horizontal bar chart with blue gradient
3. **Geographic Map**: US choropleth map with revenue color-coding
4. **Satisfaction Analysis**: Bar chart showing review scores by delivery time

### Dashboard Usage
```bash
# Launch dashboard
streamlit run app.py

# Dashboard automatically opens at http://localhost:8501
# Use date picker to filter all visualizations
# Hover over charts for detailed information
```

## Usage Guide

### Basic Usage

1. **Open the notebook**: `EDA_Refactored.ipynb`
2. **Configure analysis parameters** in the Configuration section:
   ```python
   ANALYSIS_YEAR = 2023      # Primary analysis year
   COMPARISON_YEAR = 2022    # Comparison year for YoY metrics
   DATA_PATH = 'ecommerce_data/'
   ```
3. **Run all cells** to generate the complete analysis

### Customizing the Analysis

#### Changing Analysis Period
```python
# Analyze 2024 vs 2023
ANALYSIS_YEAR = 2024
COMPARISON_YEAR = 2023

# Analyze single year without comparison
ANALYSIS_YEAR = 2023
COMPARISON_YEAR = None  # No comparison
```

#### Filtering by Date Range
```python
# Using data_loader functions for custom filtering
from data_loader import filter_by_date_range

# Filter to specific months
q1_data = filter_by_date_range(data, 
                              start_year=2023, end_year=2023,
                              start_month=1, end_month=3)
```

#### Custom Business Metrics
```python
# Using business_metrics functions
from business_metrics import calculate_revenue_metrics

# Custom period comparison
metrics = calculate_revenue_metrics(
    data,
    current_period_filter={'year': 2023, 'month': 12},
    comparison_period_filter={'year': 2022, 'month': 12}
)
```

## Module Documentation

### data_loader.py
Core functions for data preparation and cleaning.

**Key Functions:**
- `load_raw_datasets(data_path)`: Load all CSV files from directory
- `clean_and_prepare_data(datasets)`: Merge and prepare combined dataset  
- `filter_delivered_orders(data)`: Filter to delivered orders only
- `filter_by_date_range(data, ...)`: Filter by configurable date ranges
- `get_data_summary(data)`: Generate data quality summary

### business_metrics.py
Business logic for calculating key performance metrics.

**Key Functions:**
- `calculate_revenue_metrics(data, ...)`: Revenue and growth calculations
- `calculate_monthly_trends(data, year)`: Monthly performance trends
- `analyze_product_performance(data)`: Product category analysis
- `analyze_geographic_performance(data)`: State-level performance
- `analyze_customer_satisfaction(data)`: Review score analysis
- `analyze_delivery_performance(data)`: Shipping and delivery metrics
- `generate_comprehensive_report(data, ...)`: Complete business report

## Business Metrics Explained

### Revenue Metrics
- **Total Revenue**: Sum of all delivered order values
- **Revenue Growth**: Year-over-year percentage change
- **Average Order Value (AOV)**: Revenue divided by number of orders
- **Monthly Growth Rate**: Month-over-month percentage change

### Customer Experience Metrics  
- **Customer Satisfaction Rate**: Percentage of 4+ star reviews
- **Average Review Score**: Mean rating across all reviews (1-5 scale)
- **Delivery Performance**: Average days from purchase to delivery
- **On-time Delivery Rate**: Percentage delivered within 7 days

### Geographic & Product Metrics
- **Revenue by State**: Geographic distribution of sales
- **Category Performance**: Revenue and share by product category
- **Market Penetration**: Number of states with active customers

## Troubleshooting

### Common Issues

**1. Data Files Not Found**
```
FileNotFoundError: ecommerce_data/orders_dataset.csv not found
```
**Solution**: Verify CSV files are in `ecommerce_data/` directory

**2. Import Errors**
```
ModuleNotFoundError: No module named 'plotly'
```
**Solution**: Install requirements: `pip install -r requirements.txt`

**3. Empty Analysis Results**
```
Warning: No data found for year 2024
```
**Solution**: Check `ANALYSIS_YEAR` configuration matches available data

### Performance Optimization

For large datasets:
- Filter date ranges early in the analysis
- Use `delivered_orders` dataset instead of full `sales_data`
- Consider sampling for visualization development

## Future Enhancements

### Planned Features
- **Automated report generation**: PDF/HTML export functionality
- **Advanced forecasting**: Predictive analytics for revenue trends  
- **Cohort analysis**: Customer lifetime value calculations
- **A/B testing framework**: Statistical significance testing
- **Real-time dashboard**: Streamlit/Dash web interface

### Extension Ideas
- **Inventory analysis**: Stock level and turnover metrics
- **Marketing attribution**: Channel performance analysis
- **Profitability analysis**: Cost and margin calculations
- **Customer segmentation**: RFM analysis and clustering

## Contributing

To extend or modify this framework:

1. **Add new metrics** to `business_metrics.py`
2. **Create new visualizations** in the notebook
3. **Extend data processing** in `data_loader.py`  
4. **Update documentation** in README.md

Follow the existing code patterns and maintain comprehensive docstrings.

## Dependencies

Core requirements (see `requirements.txt` for versions):
- `streamlit`: Web dashboard framework
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computing
- `plotly`: Interactive visualizations
- `matplotlib`: Static plotting
- `seaborn`: Statistical visualization
- `jupyter`: Notebook environment

### Dashboard-Specific Features
- **Real-time Updates**: Streamlit's reactive framework
- **Professional Styling**: Custom CSS for business aesthetics
- **Interactive Charts**: Plotly integration with hover effects
- **Responsive Design**: Adaptive layouts for different screen sizes

## License

This project is provided as-is for educational and analysis purposes. Modify and extend as needed for your specific use case.

---

**Generated using Claude Code refactoring framework**

For questions, issues, or feature requests, please refer to the inline documentation or create an issue in the project repository.