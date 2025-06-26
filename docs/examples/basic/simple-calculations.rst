Simple Calculations
===================

Learn to perform basic mathematical operations and calculate spectral indices in Earth Engine.

What You'll Learn
-----------------

* Basic arithmetic operations on images
* Calculating common spectral indices
* Working with image bands and band math
* Understanding Earth Engine expressions
* Conditional operations and masking

Prerequisites
-------------

* Completed first script and image display examples
* Understanding of remote sensing concepts
* Basic knowledge of spectral indices
* Familiarity with Python programming

Basic Mathematical Operations
-----------------------------

Earth Engine supports standard mathematical operations:

.. code-block:: python

   import ee
   
   # Initialize Earth Engine
   ee.Initialize(project='your-project-id')
   
   # Load a Landsat 8 image
   image = ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_044034_20140318')
   
   # Apply scaling factors
   image = image.select('SR_B.').multiply(0.0000275).add(-0.2)
   
   # Basic arithmetic
   red = image.select('SR_B4')
   nir = image.select('SR_B5')
   
   # Addition
   sum_bands = red.add(nir)
   
   # Subtraction
   difference = nir.subtract(red)
   
   # Multiplication
   product = red.multiply(nir)
   
   # Division
   ratio = nir.divide(red)

Common Spectral Indices
-----------------------

**NDVI (Normalized Difference Vegetation Index):**

.. code-block:: python

   # NDVI = (NIR - Red) / (NIR + Red)
   ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
   
   print("NDVI range: -1 to 1")
   print("Values > 0.3 typically indicate vegetation")

**NDWI (Normalized Difference Water Index):**

.. code-block:: python

   # NDWI = (Green - NIR) / (Green + NIR)
   ndwi = image.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI')
   
   print("NDWI > 0 typically indicates water")

**EVI (Enhanced Vegetation Index):**

.. code-block:: python

   # EVI = 2.5 * ((NIR - Red) / (NIR + 6 * Red - 7.5 * Blue + 1))
   evi = image.expression(
       '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
       {
           'NIR': image.select('SR_B5'),
           'RED': image.select('SR_B4'),
           'BLUE': image.select('SR_B2')
       }
   ).rename('EVI')

Using ee.Image.expression()
---------------------------

For complex calculations, use expressions:

.. code-block:: python

   # Custom vegetation index
   custom_vi = image.expression(
       '(NIR * 2.5 - RED * 1.5) / (NIR + RED + 1)',
       {
           'NIR': image.select('SR_B5'),
           'RED': image.select('SR_B4')
       }
   ).rename('Custom_VI')
   
   # Atmospheric visibility
   visibility = image.expression(
       'BLUE / RED',
       {
           'BLUE': image.select('SR_B2'),
           'RED': image.select('SR_B4')
       }
   ).rename('Visibility')

Conditional Operations
----------------------

Create masks and conditional values:

.. code-block:: python

   # Create vegetation mask
   vegetation_mask = ndvi.gt(0.3)
   
   # Create water mask  
   water_mask = ndwi.gt(0.2)
   
   # Conditional assignment
   land_cover = ee.Image(0)  # Start with zeros
   land_cover = land_cover.where(water_mask, 1)      # Water = 1
   land_cover = land_cover.where(vegetation_mask, 2) # Vegetation = 2
   
   # Apply mask to preserve only high vegetation
   high_veg_only = ndvi.updateMask(ndvi.gt(0.5))

Statistical Analysis
--------------------

Calculate statistics over regions:

.. code-block:: python

   # Define area of interest
   point = ee.Geometry.Point([-122.4, 37.8])
   region = point.buffer(1000)  # 1km buffer
   
   # Calculate statistics
   stats = ndvi.reduceRegion(
       reducer=ee.Reducer.mean().combine(
           reducer2=ee.Reducer.minMax(),
           sharedInputs=True
       ).combine(
           reducer2=ee.Reducer.stdDev(),
           sharedInputs=True
       ),
       geometry=region,
       scale=30,
       maxPixels=1e9
   )
   
   # Print results
   ndvi_mean = stats.get('NDVI_mean').getInfo()
   ndvi_min = stats.get('NDVI_min').getInfo()
   ndvi_max = stats.get('NDVI_max').getInfo()
   ndvi_std = stats.get('NDVI_stdDev').getInfo()
   
   print(f"NDVI Statistics:")
   print(f"  Mean: {ndvi_mean:.3f}")
   print(f"  Range: {ndvi_min:.3f} to {ndvi_max:.3f}")
   print(f"  Std Dev: {ndvi_std:.3f}")

Complete Example
----------------

Here's a complete script combining all concepts:

.. literalinclude:: ../../../examples/basic/03_simple_calculations.py
   :language: python
   :linenos:

Visualization Parameters
------------------------

Visualize your calculated indices:

.. code-block:: python

   # NDVI visualization
   ndvi_vis = {
       'bands': ['NDVI'],
       'min': -0.2,
       'max': 0.8,
       'palette': ['blue', 'white', 'green']
   }
   
   # Water index visualization
   ndwi_vis = {
       'bands': ['NDWI'],
       'min': -0.3,
       'max': 0.5,
       'palette': ['white', 'blue']
   }
   
   # Land cover visualization
   landcover_vis = {
       'bands': ['classification'],
       'min': 0,
       'max': 2,
       'palette': ['gray', 'blue', 'green']
   }

Common Applications
-------------------

**Agriculture Monitoring:**
* NDVI for crop health assessment
* EVI for biomass estimation
* SAVI for soil-adjusted vegetation monitoring

**Water Resources:**
* NDWI for water body mapping
* MNDWI for water extent monitoring
* Turbidity indices for water quality

**Urban Planning:**
* NDBI for built-up area detection
* Urban heat island analysis
* Green space monitoring

Best Practices
--------------

**Scale Considerations:**
* Use appropriate scale for your analysis
* Consider sensor resolution limits
* Match scale to feature size

**Data Quality:**
* Apply cloud masking before calculations
* Check for valid data ranges
* Handle no-data values appropriately

**Computational Efficiency:**
* Calculate indices only when needed
* Use appropriate data types
* Optimize expressions for performance

Common Issues
-------------

**Scale Factor Problems:**

.. code-block:: python

   # Wrong - using raw DN values
   ndvi_wrong = image.normalizedDifference(['SR_B5', 'SR_B4'])
   
   # Correct - apply scale factors first
   scaled = image.select('SR_B.').multiply(0.0000275).add(-0.2)
   ndvi_correct = scaled.normalizedDifference(['SR_B5', 'SR_B4'])

**Invalid Data Handling:**

.. code-block:: python

   # Mask invalid values
   valid_ndvi = ndvi.updateMask(ndvi.gte(-1).And(ndvi.lte(1)))

**Memory Issues:**

.. code-block:: python

   # For large areas, use appropriate scale
   stats = ndvi.reduceRegion(
       reducer=ee.Reducer.mean(),
       geometry=large_region,
       scale=100,  # Use coarser resolution for large areas
       maxPixels=1e9
   )

Next Steps
----------

* Try calculating different spectral indices
* Experiment with custom expressions
* Learn about time series calculations
* Explore classification applications

Next: :doc:`../intermediate/index`
