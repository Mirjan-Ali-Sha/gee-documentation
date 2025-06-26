"""
Intermediate Example 1: Time Series Analysis
============================================

This example demonstrates:
- Working with image collections
- Filtering by date and location
- Time series chart creation
- Statistical analysis over time

Use case: Analyzing NDVI trends over agricultural areas
"""

import ee
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

def analyze_ndvi_time_series(geometry, start_date, end_date):
    """
    Analyze NDVI time series for a given geometry and date range.
    
    Args:
        geometry: ee.Geometry object defining the area of interest
        start_date: Start date as string ('YYYY-MM-DD')
        end_date: End date as string ('YYYY-MM-DD')
    
    Returns:
        Dictionary containing time series data and statistics
    """
    
    # Load Landsat 8 Surface Reflectance collection
    collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                 .filterDate(start_date, end_date)
                 .filterBounds(geometry)
                 .filter(ee.Filter.lt('CLOUD_COVER', 20)))
    
    print(f"Found {collection.size().getInfo()} images in the collection")
    
    # Function to calculate NDVI and add time properties
    def add_ndvi_and_time(image):
        # Calculate NDVI
        ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
        
        # Add time properties
        date = ee.Date(image.get('system:time_start'))
        years = date.difference(ee.Date('1970-01-01'), 'year')
        
        return (image.addBands(ndvi)
                    .set('date', date)
                    .set('year', date.get('year'))
                    .set('month', date.get('month'))
                    .set('day_of_year', date.getRelative('day', 'year'))
                    .set('decimal_year', years))
    
    # Apply NDVI calculation to collection
    ndvi_collection = collection.map(add_ndvi_and_time)
    
    # Create time series by reducing each image to mean NDVI
    def extract_ndvi_value(image):
        # Calculate mean NDVI over the geometry
        ndvi_mean = image.select('NDVI').reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=geometry,
            scale=30,
            maxPixels=1e9
        )
        
        # Return feature with date and NDVI value
        return ee.Feature(None, {
            'date': image.get('date'),
            'decimal_year': image.get('decimal_year'),
            'ndvi': ndvi_mean.get('NDVI'),
            'year': image.get('year'),
            'month': image.get('month'),
            'day_of_year': image.get('day_of_year')
        })
    
    # Extract time series data
    time_series = ndvi_collection.map(extract_ndvi_value)
    
    # Convert to pandas DataFrame for analysis
    time_series_list = time_series.getInfo()['features']
    df_data = []
    
    for feature in time_series_list:
        props = feature['properties']
        if props['ndvi'] is not None:  # Filter out null values
            df_data.append({
                'date': datetime.fromtimestamp(props['date']['value'] / 1000),
                'decimal_year': props['decimal_year'],
                'ndvi': props['ndvi'],
                'year': props['year'],
                'month': props['month'],
                'day_of_year': props['day_of_year']
            })
    
    df = pd.DataFrame(df_data)
    df = df.sort_values('date')
    
    # Calculate statistics
    stats = {
        'mean_ndvi': df['ndvi'].mean(),
        'std_ndvi': df['ndvi'].std(),
        'min_ndvi': df['ndvi'].min(),
        'max_ndvi': df['ndvi'].max(),
        'data_points': len(df)
    }
    
    return df, stats

def plot_time_series(df, stats, title="NDVI Time Series"):
    """
    Create time series plot with trend analysis.
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Main time series plot
    ax1.plot(df['date'], df['ndvi'], 'o-', linewidth=1, markersize=3, alpha=0.7)
    ax1.set_title(f"{title}\nMean: {stats['mean_ndvi']:.3f} ± {stats['std_ndvi']:.3f}")
    ax1.set_xlabel('Date')
    ax1.set_ylabel('NDVI')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=stats['mean_ndvi'], color='r', linestyle='--', alpha=0.5, label='Mean')
    ax1.legend()
    
    # Monthly aggregation
    monthly_mean = df.groupby(df['date'].dt.month)['ndvi'].mean()
    ax2.bar(monthly_mean.index, monthly_mean.values, alpha=0.7, color='green')
    ax2.set_title('Monthly Average NDVI')
    ax2.set_xlabel('Month')
    ax2.set_ylabel('Mean NDVI')
    ax2.set_xticks(range(1, 13))
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return fig

def main():
    """
    Main function demonstrating time series analysis.
    """
    # Initialize Earth Engine
    try:
        ee.Initialize(project='your-project-id')
        print("✓ Earth Engine initialized successfully!")
    except Exception as e:
        print(f"✗ Error initializing Earth Engine: {e}")
        return
    
    # Define area of interest (example: agricultural area in Iowa)
    geometry = ee.Geometry.Rectangle([-94.6, 41.9, -94.4, 42.1])
    
    # Define date range
    start_date = '2020-01-01'
    end_date = '2023-12-31'
    
    print(f"Analyzing NDVI time series from {start_date} to {end_date}")
    print("This may take a few minutes...")
    
    # Perform analysis
    df, stats = analyze_ndvi_time_series(geometry, start_date, end_date)
    
    # Print results
    print("\n📊 Time Series Analysis Results:")
    print(f"Data points: {stats['data_points']}")
    print(f"Mean NDVI: {stats['mean_ndvi']:.3f}")
    print(f"Standard deviation: {stats['std_ndvi']:.3f}")
    print(f"Range: {stats['min_ndvi']:.3f} to {stats['max_ndvi']:.3f}")
    
    # Create visualization
    plot_time_series(df, stats, "Agricultural Area NDVI Time Series")
    
    # Seasonal analysis
    print("\n🌱 Seasonal Analysis:")
    seasonal_stats = df.groupby(df['date'].dt.month)['ndvi'].agg(['mean', 'std', 'count'])
    print(seasonal_stats)
    
    print("\n✅ Time series analysis completed successfully!")

if __name__ == "__main__":
    main()
