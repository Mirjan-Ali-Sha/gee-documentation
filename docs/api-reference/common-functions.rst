Common Functions Reference
==========================

Comprehensive reference for frequently used Google Earth Engine functions and operations.

Image Operations
----------------

**ee.Image()**

Create or load an Earth Engine Image.

.. code-block:: python

   # Load specific image
   image = ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_044034_20140318')
   
   # Create constant image
   constant = ee.Image.constant(1)
   
   # Create random image
   random = ee.Image.random()

**image.select()**

Select specific bands from an image.

.. code-block:: python

   # Select by band names
   rgb = image.select(['SR_B4', 'SR_B3', 'SR_B2'])
   
   # Select by index
   first_band = image.select(0)
   
   # Select and rename
   renamed = image.select(['SR_B4'], ['red'])

**image.normalizedDifference()**

Calculate normalized difference between two bands.

.. code-block:: python

   # NDVI calculation
   ndvi = image.normalizedDifference(['SR_B5', 'SR_B4'])
   
   # NDWI calculation
   ndwi = image.normalizedDifference(['SR_B3', 'SR_B5'])

**image.expression()**

Perform mathematical expressions on image bands.

.. code-block:: python

   # EVI calculation
   evi = image.expression(
       '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
       {
           'NIR': image.select('SR_B5'),
           'RED': image.select('SR_B4'),
           'BLUE': image.select('SR_B2')
       }
   )

**image.addBands()**

Add bands to an existing image.

.. code-block:: python

   # Add NDVI band to original image
   with_ndvi = image.addBands(ndvi)
   
   # Replace existing bands
   replaced = image.addBands(ndvi, None, True)

**image.updateMask()**

Apply a mask to an image.

.. code-block:: python

   # Mask cloudy pixels
   masked = image.updateMask(image.select('QA_PIXEL').lt(1000))
   
   # Mask based on NDVI
   vegetation_only = ndvi.updateMask(ndvi.gt(0.3))

Collection Operations
--------------------

**ee.ImageCollection()**

Create or load an Earth Engine ImageCollection.

.. code-block:: python

   # Load collection
   collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
   
   # Create from list of images
   image_list = [image1, image2, image3]
   collection = ee.ImageCollection.fromImages(image_list)

**collection.filterDate()**

Filter collection by date range.

.. code-block:: python

   # Filter by date strings
   filtered = collection.filterDate('2023-01-01', '2023-12-31')
   
   # Filter by Date objects
   start = ee.Date('2023-06-01')
   end = ee.Date('2023-08-31')
   summer = collection.filterDate(start, end)

**collection.filterBounds()**

Filter collection by geographic bounds.

.. code-block:: python

   # Filter by point
   point = ee.Geometry.Point([-122.4, 37.8])
   local = collection.filterBounds(point)
   
   # Filter by region
   region = ee.Geometry.Rectangle([-123, 37, -122, 38])
   regional = collection.filterBounds(region)

**collection.filter()**

Apply custom filters to collection.

.. code-block:: python

   # Filter by metadata
   low_cloud = collection.filter(ee.Filter.lt('CLOUD_COVER', 10))
   
   # Multiple filters
   quality = collection.filter(
       ee.Filter.And(
           ee.Filter.lt('CLOUD_COVER', 20),
           ee.Filter.gt('SUN_ELEVATION', 30)
       )
   )

**collection.map()**

Apply function to all images in collection.

.. code-block:: python

   def calculate_ndvi(image):
       ndvi = image.normalizedDifference(['SR_B5', 'SR_B4'])
       return image.addBands(ndvi.rename('NDVI'))
   
   # Apply to collection
   with_ndvi = collection.map(calculate_ndvi)

**collection.reduce()**

Reduce collection to single image.

.. code-block:: python

   # Median composite
   median = collection.median()
   
   # Mean composite
   mean = collection.mean()
   
   # Custom reduction
   stats = collection.reduce(
       ee.Reducer.median().combine(
           reducer2=ee.Reducer.stdDev(),
           sharedInputs=True
       )
   )

Geometry Operations
------------------

**ee.Geometry.Point()**

Create point geometry.

.. code-block:: python

   # Simple point
   point = ee.Geometry.Point([-122.4, 37.8])
   
   # Point with projection
   point_proj = ee.Geometry.Point([-122.4, 37.8], 'EPSG:4326')

**ee.Geometry.Rectangle()**

Create rectangular geometry.

.. code-block:: python

   # Bounding box
   bbox = ee.Geometry.Rectangle([-123, 37, -122, 38])
   
   # From coordinates list
   coords = [[-123, 37], [-122, 38]]
   rect = ee.Geometry.Rectangle(coords)

**geometry.buffer()**

Create buffer around geometry.

.. code-block:: python

   # Buffer in meters
   buffered = point.buffer(1000)
   
   # Buffer in map units
   buffered_deg = point.buffer(0.01, maxError=1)

**geometry.area()**

Calculate geometry area.

.. code-block:: python

   # Area in square meters
   area_m2 = region.area()
   
   # Area in hectares
   area_ha = region.area().divide(10000)

**geometry.centroid()**

Get geometry centroid.

.. code-block:: python

   # Centroid of polygon
   center = region.centroid()
   
   # Centroid coordinates
   coords = center.coordinates()

Reduction Operations
-------------------

**image.reduceRegion()**

Reduce image over region.

.. code-block:: python

   # Mean value
   mean_value = image.reduceRegion(
       reducer=ee.Reducer.mean(),
       geometry=region,
       scale=30,
       maxPixels=1e9
   )
   
   # Multiple statistics
   stats = image.reduceRegion(
       reducer=ee.Reducer.mean().combine(
           reducer2=ee.Reducer.minMax(),
           sharedInputs=True
       ),
       geometry=region,
       scale=30
   )

**image.reduceNeighborhood()**

Reduce image using neighborhood operations.

.. code-block:: python

   # Focal mean
   focal_mean = image.reduceNeighborhood(
       reducer=ee.Reducer.mean(),
       kernel=ee.Kernel.circle(radius=2, units='pixels')
   )
   
   # Focal standard deviation
   focal_std = image.reduceNeighborhood(
       reducer=ee.Reducer.stdDev(),
       kernel=ee.Kernel.square(radius=1, units='pixels')
   )

**collection.reduceRegion()**

Reduce collection over region.

.. code-block:: python

   # Time series extraction
   time_series = collection.map(lambda img: img.reduceRegion(
       reducer=ee.Reducer.mean(),
       geometry=point.buffer(1000),
       scale=30
   ))

Conditional Operations
---------------------

**image.where()**

Conditional assignment of values.

.. code-block:: python

   # Replace values based on condition
   replaced = image.where(image.gt(0.5), 1)
   
   # Multiple conditions
   classified = ee.Image(0).where(ndvi.gt(0.3), 1).where(ndwi.gt(0.1), 2)

**ee.Algorithms.If()**

Conditional execution.

.. code-block:: python

   # Conditional image selection
   result = ee.Algorithms.If(
       condition=collection.size().gt(0),
       trueCase=collection.median(),
       falseCase=ee.Image.constant(0)
   )

**image.updateMask()**

Apply conditional masking.

.. code-block:: python

   # Mask based on quality
   quality_masked = image.updateMask(
       image.select('QA_PIXEL').bitwiseAnd(1 << 4).eq(0)
   )

Mathematical Operations
----------------------

**Basic arithmetic:**

.. code-block:: python

   # Addition
   sum_image = image1.add(image2)
   
   # Subtraction
   diff_image = image1.subtract(image2)
   
   # Multiplication
   product = image1.multiply(image2)
   
   # Division
   ratio = image1.divide(image2)

**Advanced math:**

.. code-block:: python

   # Power
   squared = image.pow(2)
   
   # Square root
   sqrt_image = image.sqrt()
   
   # Logarithm
   log_image = image.log()
   
   # Trigonometric
   sin_image = image.sin()
   cos_image = image.cos()

**Statistical operations:**

.. code-block:: python

   # Absolute value
   abs_image = image.abs()
   
   # Round
   rounded = image.round()
   
   # Clip values
   clipped = image.clamp(0, 1)

Export Operations
----------------

**ee.batch.Export.image.toDrive()**

Export image to Google Drive.

.. code-block:: python

   # Basic export
   task = ee.batch.Export.image.toDrive(
       image=image,
       description='my_export',
       folder='EarthEngine',
       scale=30,
       region=region
   )
   
   # Advanced export
   task = ee.batch.Export.image.toDrive(
       image=image,
       description='detailed_export',
       folder='EarthEngine',
       fileNamePrefix='landsat_',
       scale=30,
       region=region,
       crs='EPSG:4326',
       maxPixels=1e13,
       fileFormat='GeoTIFF'
   )
   
   task.start()

**ee.batch.Export.table.toDrive()**

Export feature collection to Google Drive.

.. code-block:: python

   # Export as CSV
   task = ee.batch.Export.table.toDrive(
       collection=feature_collection,
       description='features_export',
       folder='EarthEngine',
       fileFormat='CSV'
   )
   
   # Export as Shapefile
   task = ee.batch.Export.table.toDrive(
       collection=feature_collection,
       description='shapefile_export',
       folder='EarthEngine',
       fileFormat='SHP'
   )

**ee.batch.Export.video.toDrive()**

Export image collection as video.

.. code-block:: python

   # Create animation
   task = ee.batch.Export.video.toDrive(
       collection=time_series_collection,
       description='time_lapse',
       folder='EarthEngine',
       framesPerSecond=2,
       dimensions=720,
       region=region
   )

Utility Functions
----------------

**ee.Date()**

Work with dates.

.. code-block:: python

   # Create date
   date = ee.Date('2023-06-15')
   
   # Date arithmetic
   later = date.advance(30, 'day')
   earlier = date.advance(-1, 'month')
   
   # Date formatting
   formatted = date.format('YYYY-MM-dd')

**ee.List()**

Work with lists.

.. code-block:: python

   # Create list
   numbers = ee.List([1, 2, 3, 4, 5])
   
   # List operations
   mapped = numbers.map(lambda x: ee.Number(x).multiply(2))
   filtered = numbers.filter(ee.Filter.gt('item', 3))

**ee.Dictionary()**

Work with dictionaries.

.. code-block:: python

   # Create dictionary
   properties = ee.Dictionary({'name': 'test', 'value': 42})
   
   # Dictionary operations
   keys = properties.keys()
   values = properties.values()
   value = properties.get('name')

**ee.String()**

String operations.

.. code-block:: python

   # String manipulation
   text = ee.String('Hello World')
   upper = text.toUpperCase()
   replaced = text.replace('World', 'Earth Engine')
   
   # String formatting
   formatted = ee.String('Value: ').cat(ee.Number(42).format('%.2f'))

Error Handling Patterns
-----------------------

**Try-catch patterns:**

.. code-block:: python

   try:
       result = image.getInfo()
       print("Success:", result)
   except ee.EEException as e:
       print("Earth Engine error:", e)
   except Exception as e:
       print("General error:", e)

**Validation functions:**

.. code-block:: python

   def validate_image(image):
       """Validate image properties."""
       if not isinstance(image, ee.Image):
           raise TypeError("Input must be ee.Image")
       
       bands = image.bandNames().getInfo()
       if not bands:
           raise ValueError("Image has no bands")
       
       return True

**Safe operations:**

.. code-block:: python

   def safe_reduce_region(image, geometry, scale=30):
       """Safely reduce region with error handling."""
       try:
           return image.reduceRegion(
               reducer=ee.Reducer.mean(),
               geometry=geometry,
               scale=scale,
               maxPixels=1e9
           ).getInfo()
       except Exception as e:
           print(f"Reduction failed: {e}")
           return None

See Also
--------

* :doc:`authentication-methods` - Authentication reference
* :doc:`../examples/index` - Practical examples
* `Official Earth Engine API <https://developers.google.com/earth-engine/apidocs>`_
* `Earth Engine Guides <https://developers.google.com/earth-engine/guides>`_

.. note::
   Functions may have additional parameters not shown here. Refer to the official documentation for complete parameter lists.

.. tip::
   Use the Earth Engine Code Editor's autocomplete feature to discover function parameters and options.
