"""
Intermediate Example 2: Image Collection Filtering
==================================================

This example demonstrates:
- Advanced filtering techniques for image collections
- Temporal, spatial, and metadata filtering
- Quality assessment and cloud filtering
- Collection reduction and compositing methods
- Working with large datasets efficiently

Prerequisites:
- Basic understanding of Earth Engine image collections
- Familiarity with filtering concepts
- Knowledge of satellite data characteristics
"""

import ee
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class ImageCollectionFilter:
    """Class for advanced image collection filtering operations."""
    
    def __init__(self, project_id):
        """Initialize the filter with Earth Engine project."""
        self.project_id = project_id
        self.initialize_ee()
    
    def initialize_ee(self):
        """Initialize Earth Engine."""
        try:
            ee.Initialize(project=self.project_id)
            print("✓ Earth Engine initialized successfully!")
        except Exception as e:
            print(f"✗ Error initializing Earth Engine: {e}")
            raise
    
    def basic_filtering_examples(self):
        """Demonstrate basic filtering techniques."""
        print("🔍 Basic Filtering Examples")
        print("-" * 40)
        
        # Date filtering
        print("1. Date Filtering:")
        collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        
        # Filter by date range
        date_filtered = collection.filterDate('2023-01-01', '2023-12-31')
        print(f"   Original collection size: {collection.size().getInfo()}")
        print(f"   After date filter: {date_filtered.size().getInfo()}")
        
        # Filter by specific months
        summer_images = collection.filter(
            ee.Filter.calendarRange(6, 8, 'month')
        )
        print(f"   Summer months only: {summer_images.size().getInfo()}")
        
        # Spatial filtering
        print("\n2. Spatial Filtering:")
        point = ee.Geometry.Point([-122.4, 37.8])
        region = ee.Geometry.Rectangle([-123, 37, -122, 38])
        
        # Filter by point intersection
        point_filtered = date_filtered.filterBounds(point)
        print(f"   Images containing point: {point_filtered.size().getInfo()}")
        
        # Filter by region intersection
        region_filtered = date_filtered.filterBounds(region)
        print(f"   Images intersecting region: {region_filtered.size().getInfo()}")
        
        return region_filtered
    
    def metadata_filtering(self, collection):
        """Demonstrate filtering by metadata properties."""
        print("\n📊 Metadata Filtering")
        print("-" * 30)
        
        # Cloud cover filtering
        print("1. Cloud Cover Filtering:")
        low_cloud = collection.filter(ee.Filter.lt('CLOUD_COVER', 10))
        medium_cloud = collection.filter(
            ee.Filter.And(
                ee.Filter.gte('CLOUD_COVER', 10),
                ee.Filter.lt('CLOUD_COVER', 30)
            )
        )
        print(f"   Low cloud cover (<10%): {low_cloud.size().getInfo()}")
        print(f"   Medium cloud cover (10-30%): {medium_cloud.size().getInfo()}")
        
        # Sun elevation filtering
        print("\n2. Sun Elevation Filtering:")
        high_sun = collection.filter(ee.Filter.gt('SUN_ELEVATION', 45))
        print(f"   High sun elevation (>45°): {high_sun.size().getInfo()}")
        
        # Acquisition DOY filtering
        print("\n3. Day of Year Filtering:")
        growing_season = collection.filter(
            ee.Filter.And(
                ee.Filter.gte('DAY_OF_YEAR', 120),  # May
                ee.Filter.lte('DAY_OF_YEAR', 243)   # August
            )
        )
        print(f"   Growing season images: {growing_season.size().getInfo()}")
        
        # Satellite path/row filtering
        print("\n4. Path/Row Filtering:")
        specific_tile = collection.filter(
            ee.Filter.And(
                ee.Filter.eq('WRS_PATH', 44),
                ee.Filter.eq('WRS_ROW', 34)
            )
        )
        print(f"   Specific Landsat tile: {specific_tile.size().getInfo()}")
        
        return low_cloud
    
    def advanced_filtering_techniques(self, collection):
        """Demonstrate advanced filtering techniques."""
        print("\n🎯 Advanced Filtering Techniques")
        print("-" * 40)
        
        # Custom filter functions
        def quality_filter(image):
            """Custom function to filter based on multiple quality criteria."""
            qa = image.select('QA_PIXEL')
            
            # Check for clear conditions
            clear_conditions = (
                qa.bitwiseAnd(1 << 3).eq(0).And(  # No cloud shadow
                qa.bitwiseAnd(1 << 4).eq(0).And(  # No cloud
                qa.bitwiseAnd(1 << 5).eq(0)))     # No cirrus
            
            # Calculate percentage of clear pixels
            clear_percentage = clear_conditions.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=image.geometry(),
                scale=1000,
                maxPixels=1e6
            ).values().get(0)
            
            # Return image with clear percentage property
            return image.set('CLEAR_PERCENTAGE', clear_percentage)
        
        print("1. Custom Quality Assessment:")
        # Apply custom filter
        quality_assessed = collection.map(quality_filter)
        
        # Filter by clear percentage
        high_quality = quality_assessed.filter(
            ee.Filter.gt('CLEAR_PERCENTAGE', 0.8)
        )
        print(f"   High quality images (>80% clear): {high_quality.size().getInfo()}")
        
        # Temporal proximity filtering
        print("\n2. Temporal Proximity Filtering:")
        target_date = ee.Date('2023-07-15')
        
        # Filter images within 30 days of target date
        temporal_proximity = collection.filter(
            ee.Filter.And(
                ee.Filter.gte('system:time_start', target_date.advance(-30, 'day').millis()),
                ee.Filter.lte('system:time_start', target_date.advance(30, 'day').millis())
            )
        )
        print(f"   Images within 30 days of July 15: {temporal_proximity.size().getInfo()}")
        
        # Seasonal filtering
        print("\n3. Seasonal Filtering:")
        def get_season_filter(season):
            """Get filter for specific season."""
            season_ranges = {
                'spring': [80, 171],   # March 21 - June 20
                'summer': [172, 264],  # June 21 - September 21
                'fall': [265, 354],    # September 22 - December 20
                'winter': [355, 79]    # December 21 - March 20
            }
            
            if season == 'winter':
                # Handle year boundary for winter
                return ee.Filter.Or(
                    ee.Filter.gte('DAY_OF_YEAR', 355),
                    ee.Filter.lte('DAY_OF_YEAR', 79)
                )
            else:
                start, end = season_ranges[season]
                return ee.Filter.And(
                    ee.Filter.gte('DAY_OF_YEAR', start),
                    ee.Filter.lte('DAY_OF_YEAR', end)
                )
        
        spring_images = collection.filter(get_season_filter('spring'))
        summer_images = collection.filter(get_season_filter('summer'))
        print(f"   Spring images: {spring_images.size().getInfo()}")
        print(f"   Summer images: {summer_images.size().getInfo()}")
        
        return high_quality
    
    def multi_sensor_filtering(self):
        """Demonstrate filtering across multiple sensor collections."""
        print("\n🛰️ Multi-Sensor Collection Filtering")
        print("-" * 45)
        
        # Define common parameters
        region = ee.Geometry.Rectangle([-122.5, 37.5, -122.0, 38.0])
        start_date = '2023-01-01'
        end_date = '2023-12-31'
        
        # Landsat 8
        landsat8 = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                   .filterBounds(region)
                   .filterDate(start_date, end_date)
                   .filter(ee.Filter.lt('CLOUD_COVER', 20)))
        
        # Landsat 9
        landsat9 = (ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
                   .filterBounds(region)
                   .filterDate(start_date, end_date)
                   .filter(ee.Filter.lt('CLOUD_COVER', 20)))
        
        # Sentinel-2
        sentinel2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                    .filterBounds(region)
                    .filterDate(start_date, end_date)
                    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)))
        
        print(f"Landsat 8 images: {landsat8.size().getInfo()}")
        print(f"Landsat 9 images: {landsat9.size().getInfo()}")
        print(f"Sentinel-2 images: {sentinel2.size().getInfo()}")
        
        # Merge collections
        merged_landsat = landsat8.merge(landsat9)
        print(f"Merged Landsat: {merged_landsat.size().getInfo()}")
        
        # Filter merged collection
        best_landsat = merged_landsat.filter(ee.Filter.lt('CLOUD_COVER', 10))
        print(f"Best Landsat images (<10% cloud): {best_landsat.size().getInfo()}")
        
        return {
            'landsat8': landsat8,
            'landsat9': landsat9,
            'sentinel2': sentinel2,
            'merged_landsat': merged_landsat
        }
    
    def temporal_filtering_strategies(self, collection):
        """Demonstrate various temporal filtering strategies."""
        print("\n⏰ Temporal Filtering Strategies")
        print("-" * 40)
        
        # Monthly composites
        print("1. Monthly Filtering:")
        months = [1, 4, 7, 10]  # Jan, Apr, Jul, Oct
        monthly_counts = {}
        
        for month in months:
            monthly = collection.filter(ee.Filter.calendarRange(month, month, 'month'))
            count = monthly.size().getInfo()
            monthly_counts[month] = count
            month_name = datetime(2023, month, 1).strftime('%B')
            print(f"   {month_name}: {count} images")
        
        # Annual time series
        print("\n2. Annual Time Series:")
        years = [2020, 2021, 2022, 2023]
        annual_counts = {}
        
        for year in years:
            annual = collection.filter(ee.Filter.calendarRange(year, year, 'year'))
            count = annual.size().getInfo()
            annual_counts[year] = count
            print(f"   {year}: {count} images")
        
        # Regular interval filtering
        print("\n3. Regular Interval Filtering (16-day):")
        start_date = ee.Date('2023-01-01')
        
        def create_16day_periods():
            """Create 16-day period filters."""
            periods = []
            for i in range(0, 365, 16):
                period_start = start_date.advance(i, 'day')
                period_end = period_start.advance(16, 'day')
                periods.append({
                    'start': period_start,
                    'end': period_end,
                    'day': i + 1
                })
            return periods
        
        periods = create_16day_periods()
        period_counts = []
        
        for i, period in enumerate(periods[:10]):  # Show first 10 periods
            period_images = collection.filterDate(period['start'], period['end'])
            count = period_images.size().getInfo()
            period_counts.append(count)
            print(f"   Period {i+1} (Day {period['day']}): {count} images")
        
        return {
            'monthly': monthly_counts,
            'annual': annual_counts,
            'periods': period_counts
        }
    
    def collection_reduction_methods(self, collection):
        """Demonstrate collection reduction and compositing methods."""
        print("\n📉 Collection Reduction Methods")
        print("-" * 40)
        
        # Basic reductions
        print("1. Basic Statistical Reductions:")
        
        # Median composite
        median_composite = collection.median()
        print("   ✓ Median composite created")
        
        # Mean composite
        mean_composite = collection.mean()
        print("   ✓ Mean composite created")
        
        # Min/Max composites
        min_composite = collection.min()
        max_composite = collection.max()
        print("   ✓ Min/Max composites created")
        
        # Standard deviation
        std_composite = collection.reduce(ee.Reducer.stdDev())
        print("   ✓ Standard deviation composite created")
        
        # Advanced reductions
        print("\n2. Advanced Reduction Methods:")
        
        # Quality mosaic (best pixel based on cloud score)
        def add_cloud_score(image):
            """Add cloud score to image."""
            cloud_score = ee.Algorithms.Landsat.simpleCloudScore(image)
            return image.addBands(cloud_score.select('cloud'))
        
        scored_collection = collection.map(add_cloud_score)
        quality_mosaic = scored_collection.qualityMosaic('cloud')
        print("   ✓ Quality mosaic created (lowest cloud score)")
        
        # Temporal percentiles
        percentile_composite = collection.reduce(
            ee.Reducer.percentile([10, 25, 50, 75, 90])
        )
        print("   ✓ Percentile composite created")
        
        # Custom reduction
        def custom_reduction(collection):
            """Custom reduction combining multiple statistics."""
            return collection.reduce(
                ee.Reducer.median()
                .combine(ee.Reducer.stdDev(), sharedInputs=True)
                .combine(ee.Reducer.count(), sharedInputs=True)
            )
        
        custom_composite = custom_reduction(collection)
        print("   ✓ Custom composite (median + stddev + count)")
        
        return {
            'median': median_composite,
            'mean': mean_composite,
            'quality': quality_mosaic,
            'percentiles': percentile_composite,
            'custom': custom_composite
        }
    
    def analyze_collection_temporal_distribution(self, collection):
        """Analyze temporal distribution of image collection."""
        print("\n📅 Temporal Distribution Analysis")
        print("-" * 40)
        
        # Get image dates
        def get_image_date(image):
            """Extract date from image."""
            return ee.Feature(None, {
                'date': image.date(),
                'timestamp': image.get('system:time_start'),
                'cloud_cover': image.get('CLOUD_COVER')
            })
        
        # Extract dates
        dates_collection = collection.map(get_image_date)
        dates_list = dates_collection.getInfo()['features']
        
        # Process dates
        dates_data = []
        for feature in dates_list:
            props = feature['properties']
            timestamp = props['timestamp']
            date = datetime.fromtimestamp(timestamp / 1000)
            
            dates_data.append({
                'date': date,
                'year': date.year,
                'month': date.month,
                'day_of_year': date.timetuple().tm_yday,
                'cloud_cover': props.get('cloud_cover', 0)
            })
        
        df = pd.DataFrame(dates_data)
        
        # Temporal statistics
        print(f"Total images: {len(df)}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"Average cloud cover: {df['cloud_cover'].mean():.1f}%")
        
        # Monthly distribution
        monthly_dist = df.groupby('month').size()
        print(f"\nMonthly distribution:")
        for month, count in monthly_dist.items():
            month_name = datetime(2023, month, 1).strftime('%B')
            print(f"   {month_name}: {count} images")
        
        # Yearly distribution
        if len(df['year'].unique()) > 1:
            yearly_dist = df.groupby('year').size()
            print(f"\nYearly distribution:")
            for year, count in yearly_dist.items():
                print(f"   {year}: {count} images")
        
        return df

def main():
    """Main function demonstrating image collection filtering."""
    
    # Initialize filter system
    filter_system = ImageCollectionFilter('your-project-id')
    
    print("="*60)
    print("🔍 EARTH ENGINE IMAGE COLLECTION FILTERING GUIDE")
    print("="*60)
    
    # Step 1: Basic filtering
    basic_collection = filter_system.basic_filtering_examples()
    
    # Step 2: Metadata filtering
    metadata_filtered = filter_system.metadata_filtering(basic_collection)
    
    # Step 3: Advanced filtering techniques
    advanced_filtered = filter_system.advanced_filtering_techniques(metadata_filtered)
    
    # Step 4: Multi-sensor filtering
    multi_sensor_collections = filter_system.multi_sensor_filtering()
    
    # Step 5: Temporal filtering strategies
    temporal_stats = filter_system.temporal_filtering_strategies(advanced_filtered)
    
    # Step 6: Collection reduction methods
    composites = filter_system.collection_reduction_methods(advanced_filtered)
    
    # Step 7: Temporal distribution analysis
    temporal_df = filter_system.analyze_collection_temporal_distribution(advanced_filtered)
    
    # Summary
    print("\n" + "="*60)
    print("📊 FILTERING SUMMARY")
    print("="*60)
    
    print("\n🎯 Key Filtering Techniques Demonstrated:")
    print("• Basic temporal and spatial filtering")
    print("• Metadata-based quality filtering")
    print("• Custom filter functions")
    print("• Multi-sensor collection handling")
    print("• Temporal pattern analysis")
    print("• Collection reduction and compositing")
    
    print("\n📈 Collection Statistics:")
    print(f"• Final filtered collection: {advanced_filtered.size().getInfo()} images")
    print(f"• Temporal range: {len(temporal_df)} images analyzed")
    print(f"• Average cloud cover: {temporal_df['cloud_cover'].mean():.1f}%")
    
    print("\n🏆 Best Practices Applied:")
    print("• Combine multiple filtering criteria")
    print("• Use quality assessment metrics")
    print("• Consider temporal distribution")
    print("• Apply appropriate reduction methods")
    print("• Validate filter effectiveness")
    
    print("\n✅ Image Collection Filtering Guide Complete!")

if __name__ == "__main__":
    main()
