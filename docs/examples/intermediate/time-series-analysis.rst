Time Series Analysis
====================

Learn to analyze temporal patterns and changes using Earth Engine image collections.

What You'll Learn
-----------------

* Loading and filtering image collections
* Creating time series datasets
* Temporal analysis and trend detection
* Seasonal pattern analysis
* Change detection techniques
* Time series visualization

Prerequisites
-------------

* Understanding of image collections
* Knowledge of filtering techniques
* Basic statistical concepts
* Familiarity with temporal data

Loading Time Series Data
------------------------

**Basic time series setup:**

.. code-block:: python

   import ee
   
   # Initialize Earth Engine
   ee.Initialize(project='your-project-id')
   
   # Define study area and time range
   geometry = ee.Geometry.Point([-122.4, 37.8])  # San Francisco
   start_date = '2020-01-01'
   end_date = '2023-12-31'
   
   # Load Landsat collection
   collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                .filterDate(start_date, end_date)
                .filterBounds(geometry)
                .filter(ee.Filter.lt('CLOUD_COVER', 20)))
   
   print(f"Found {collection.size().getInfo()} images")

**Adding temporal properties:**

.. code-block:: python

   def add_date_properties(image):
       """Add useful date properties to each image."""
       date = ee.Date(image.get('system:time_start'))
       return image.set({
           'year': date.get('year'),
           'month': date.get('month'),
           'day_of_year': date.getRelative('day', 'year'),
           'decimal_year': date.difference(ee.Date('1970-01-01'), 'year')
       })
   
   # Apply to collection
   collection = collection.map(add_date_properties)

Creating Time Series
--------------------

**Extract time series values:**

.. code-block:: python

   def extract_time_series(image_collection, geometry, scale=30):
       """Extract time series data from image collection."""
       
       def calculate_indices(image):
           """Calculate spectral indices for time series."""
           # Apply scale factors
           scaled = image.select('SR_B.').multiply(0.0000275).add(-0.2)
           
           # Calculate indices
           ndvi = scaled.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
           ndwi = scaled.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI')
           evi = scaled.expression(
               '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
               {
                   'NIR': scaled.select('SR_B5'),
                   'RED': scaled.select('SR_B4'),
                   'BLUE': scaled.select('SR_B2')
               }
           ).rename('EVI')
           
           return image.addBands([ndvi, ndwi, evi])
       
       # Calculate indices for all images
       with_indices = image_collection.map(calculate_indices)
       
       # Extract values
       def extract_values(image):
           # Calculate mean values over geometry
           values = image.select(['NDVI', 'NDWI', 'EVI']).reduceRegion(
               reducer=ee.Reducer.mean(),
               geometry=geometry,
               scale=scale,
               maxPixels=1e9
           )
           
           # Return feature with date and values
           return ee.Feature(None, {
               'date': image.get('system:time_start'),
               'year': image.get('year'),
               'month': image.get('month'),
               'day_of_year': image.get('day_of_year'),
               'decimal_year': image.get('decimal_year'),
               'ndvi': values.get('NDVI'),
               'ndwi': values.get('NDWI'),
               'evi': values.get('EVI'),
               'cloud_cover': image.get('CLOUD_COVER')
           })
       
       return with_indices.map(extract_values)

Temporal Compositing
-------------------

**Monthly composites:**

.. code-block:: python

   def create_monthly_composites(collection, start_year, end_year):
       """Create monthly median composites."""
       
       months = ee.List.sequence(1, 12)
       years = ee.List.sequence(start_year, end_year)
       
       def create_monthly_composite(year):
           def create_month_composite(month):
               # Filter to specific year and month
               monthly = collection.filter(
                   ee.Filter.calendarRange(year, year, 'year')
               ).filter(
                   ee.Filter.calendarRange(month, month, 'month')
               )
               
               # Create composite
               composite = monthly.median()
               
               # Add date information
               date = ee.Date.fromYMD(year, month, 1)
               return composite.set({
                   'year': year,
                   'month': month,
                   'system:time_start': date.millis(),
                   'image_count': monthly.size()
               })
           
           return months.map(create_month_composite)
       
       # Create all composites
       composites = years.map(create_monthly_composite).flatten()
       return ee.ImageCollection.fromImages(composites)

**Seasonal composites:**

.. code-block:: python

   def create_seasonal_composites(collection):
       """Create seasonal composites."""
       
       # Define seasons by day of year
       seasons = {
           'spring': [80, 171],   # March 21 - June 20
           'summer': [172, 264],  # June 21 - September 21
           'fall': [265, 354],    # September 22 - December 20
           'winter': [355, 79]    # December 21 - March 20 (spans years)
       }
       
       seasonal_composites = []
       
       for season_name, day_range in seasons.items():
           if season_name == 'winter':
               # Handle winter spanning years
               winter_images = collection.filter(
                   ee.Filter.Or(
                       ee.Filter.gte('day_of_year', day_range[0]),
                       ee.Filter.lte('day_of_year', day_range[1])
                   )
               )
           else:
               winter_images = collection.filter(
                   ee.Filter.And(
                       ee.Filter.gte('day_of_year', day_range[0]),
                       ee.Filter.lte('day_of_year', day_range[1])
                   )
               )
           
           composite = winter_images.median().set('season', season_name)
           seasonal_composites.append(composite)
       
       return seasonal_composites

Trend Analysis
--------------

**Linear trend calculation:**

.. code-block:: python

   def calculate_temporal_trend(collection, band_name):
       """Calculate linear trend for a specific band."""
       
       # Add time variable (years since start)
       def add_time_band(image):
           time_start = ee.Date(image.get('system:time_start'))
           years_since_start = time_start.difference(ee.Date('2020-01-01'), 'year')
           return image.addBands(ee.Image(years_since_start).rename('time'))
       
       # Add time band to all images
       collection_with_time = collection.map(add_time_band)
       
       # Calculate linear regression
       linear_fit = collection_with_time.select(['time', band_name]).reduce(
           ee.Reducer.linearFit()
       )
       
       return linear_fit

**Harmonic analysis for seasonality:**

.. code-block:: python

   def harmonic_analysis(collection, band_name):
       """Perform harmonic analysis to detect seasonal patterns."""
       
       def add_harmonic_terms(image):
           # Get time in fractional years
           time_start = ee.Date(image.get('system:time_start'))
           t = time_start.difference(ee.Date('2020-01-01'), 'year')
           
           # Add harmonic terms
           omega = 2 * 3.14159
           cos_1 = t.multiply(omega).cos().rename('cos_1')
           sin_1 = t.multiply(omega).sin().rename('sin_1')
           cos_2 = t.multiply(omega * 2).cos().rename('cos_2')
           sin_2 = t.multiply(omega * 2).sin().rename('sin_2')
           
           return image.addBands([
               ee.Image(t).rename('time'),
               cos_1, sin_1, cos_2, sin_2
           ])
       
       # Add harmonic terms
       harmonic_collection = collection.map(add_harmonic_terms)
       
       # Perform harmonic regression
       harmonic_fit = harmonic_collection.select([
           'time', 'cos_1', 'sin_1', 'cos_2', 'sin_2', band_name
       ]).reduce(ee.Reducer.linearRegression({
           'numX': 5,
           'numY': 1
       }))
       
       return harmonic_fit

Change Detection
----------------

**Simple change detection:**

.. code-block:: python

   def detect_change(before_collection, after_collection, threshold=0.1):
       """Simple change detection between two time periods."""
       
       # Create composites
       before_composite = before_collection.median()
       after_composite = after_collection.median()
       
       # Calculate NDVI for both periods
       before_ndvi = before_composite.normalizedDifference(['SR_B5', 'SR_B4'])
       after_ndvi = after_composite.normalizedDifference(['SR_B5', 'SR_B4'])
       
       # Calculate change
       change = after_ndvi.subtract(before_ndvi)
       
       # Classify change
       change_mask = change.abs().gt(threshold)
       increase = change.gt(threshold)
       decrease = change.lt(-threshold)
       
       return {
           'change': change,
           'change_mask': change_mask,
           'increase': increase,
           'decrease': decrease
       }

**LandTrendr for advanced change detection:**

.. code-block:: python

   def run_landtrendr(collection):
       """Run LandTrendr algorithm for change detection."""
       
       # Prepare collection for LandTrendr
       def prepare_image(image):
           scaled = image.select('SR_B.').multiply(0.0000275).add(-0.2)
           ndvi = scaled.normalizedDifference(['SR_B5', 'SR_B4']).multiply(1000)
           return image.addBands(ndvi.rename('NDVI')).select('NDVI')
       
       lt_collection = collection.map(prepare_image)
       
       # LandTrendr parameters
       lt_params = {
           'maxSegments': 6,
           'spikeThreshold': 0.9,
           'vertexCountOvershoot': 3,
           'preventOneYearRecovery': True,
           'recoveryThreshold': 0.25,
           'pvalThreshold': 0.05,
           'bestModelProportion': 0.75,
           'minObservationsNeeded': 6
       }
       
       # Run LandTrendr
       lt_result = ee.Algorithms.TemporalSegmentation.LandTrendr(
           timeSeries=lt_collection,
           **lt_params
       )
       
       return lt_result

Complete Example
----------------

Here's the complete time series analysis example:

.. literalinclude:: ../../../examples/intermediate/01_time_series.py
   :language: python
   :linenos:

Visualization Techniques
------------------------

**Time series plots:**

.. code-block:: python

   # Extract data for plotting
   time_series_fc = extract_time_series(collection, geometry)
   time_series_list = time_series_fc.getInfo()['features']
   
   # Convert to pandas DataFrame
   import pandas as pd
   from datetime import datetime
   
   data = []
   for feature in time_series_list:
       props = feature['properties']
       if props.get('ndvi') is not None:
           data.append({
               'date': datetime.fromtimestamp(props['date']['value'] / 1000),
               'ndvi': props['ndvi'],
               'evi': props['evi'],
               'cloud_cover': props['cloud_cover']
           })
   
   df = pd.DataFrame(data)
   
   # Create plots
   import matplotlib.pyplot as plt
   
   fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
   
   # NDVI time series
   ax1.plot(df['date'], df['ndvi'], 'g-', linewidth=1, alpha=0.7)
   ax1.set_title('NDVI Time Series')
   ax1.set_ylabel('NDVI')
   ax1.grid(True, alpha=0.3)
   
   # Monthly averages
   monthly_avg = df.groupby(df['date'].dt.month)['ndvi'].mean()
   ax2.bar(monthly_avg.index, monthly_avg.values, alpha=0.7)
   ax2.set_title('Monthly Average NDVI')
   ax2.set_xlabel('Month')
   ax2.set_ylabel('NDVI')
   
   plt.tight_layout()
   plt.show()

Best Practices
--------------

**Data Quality:**
* Apply cloud masking consistently
* Filter by metadata quality indicators
* Handle missing data appropriately

**Temporal Sampling:**
* Consider sensor revisit frequency
* Account for seasonal variations
* Use appropriate temporal windows

**Scale Considerations:**
* Match analysis scale to phenomena
* Consider mixed pixel effects
* Validate with ground truth data

Next: :doc:`image-collection-filtering`
