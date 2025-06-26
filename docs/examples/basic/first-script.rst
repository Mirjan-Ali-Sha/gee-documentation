Your First Earth Engine Script
===============================

Learn to write your first Google Earth Engine script step by step.

What You'll Learn
-----------------

* Basic Earth Engine initialization
* Loading your first image
* Displaying image information
* Understanding Earth Engine objects
* Simple operations and calculations

Prerequisites
-------------

* Authenticated Earth Engine account
* Python environment with Earth Engine API
* Basic Python programming knowledge

Step 1: Initialize Earth Engine
--------------------------------

Every Earth Engine script starts with initialization:

.. code-block:: python

   import ee
   
   # Initialize Earth Engine
   ee.Initialize(project='your-project-id')
   
   print("Earth Engine initialized successfully!")

**What's happening here?**

1. Import the Earth Engine Python API
2. Initialize connection to Google's servers
3. Authenticate your access to the platform

Step 2: Load Your First Image
------------------------------

Let's load a satellite image:

.. code-block:: python

   # Load a Landsat 8 image
   image = ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_044034_20140318')
   
   print("Image loaded:", image)

**Understanding the image ID:**

* ``LANDSAT/LC08/C02/T1_L2`` - Dataset collection
* ``LC08_044034_20140318`` - Specific image identifier
* Contains path, row, and date information

Step 3: Explore Image Properties
---------------------------------

Get information about your image:

.. code-block:: python

   # Get image information
   image_info = image.getInfo()
   
   print("Image type:", image_info['type'])
   print("Image ID:", image_info['id'])
   print("Number of bands:", len(image_info['bands']))

**Common image properties:**

.. code-block:: python

   # Get specific properties
   print("Acquisition date:", image.get('DATE_ACQUIRED').getInfo())
   print("Cloud cover:", image.get('CLOUD_COVER').getInfo())
   print("Sun elevation:", image.get('SUN_ELEVATION').getInfo())

Step 4: Work with Image Bands
------------------------------

Explore the spectral bands:

.. code-block:: python

   # Get band names
   band_names = image.bandNames()
   print("Available bands:", band_names.getInfo())
   
   # Select specific bands
   rgb_bands = image.select(['SR_B4', 'SR_B3', 'SR_B2'])
   nir_band = image.select('SR_B5')
   
   print("RGB bands selected")
   print("Near-infrared band selected")

Step 5: Simple Calculations
----------------------------

Perform basic mathematical operations:

.. code-block:: python

   # Calculate NDVI (vegetation index)
   ndvi = image.normalizedDifference(['SR_B5', 'SR_B4'])
   ndvi = ndvi.rename('NDVI')
   
   print("NDVI calculated")
   
   # Get NDVI statistics
   geometry = ee.Geometry.Point([-122.4, 37.8])  # San Francisco
   
   ndvi_stats = ndvi.reduceRegion(
       reducer=ee.Reducer.mean(),
       geometry=geometry.buffer(1000),  # 1km buffer
       scale=30
   )
   
   print("Average NDVI:", ndvi_stats.getInfo())

Complete First Script
---------------------

Here's your complete first Earth Engine script:

.. code-block:: python

   """
   My First Earth Engine Script
   ============================
   
   This script demonstrates basic Earth Engine operations:
   - Initialize Earth Engine
   - Load a satellite image
   - Explore image properties
   - Calculate a vegetation index
   - Extract statistics
   """
   
   import ee
   
   def main():
       # Step 1: Initialize Earth Engine
       try:
           ee.Initialize(project='your-project-id')
           print("✓ Earth Engine initialized successfully!")
       except Exception as e:
           print(f"✗ Initialization failed: {e}")
           return
       
       # Step 2: Load image
       image = ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_044034_20140318')
       print("✓ Image loaded")
       
       # Step 3: Get image information
       print(f"✓ Image date: {image.get('DATE_ACQUIRED').getInfo()}")
       print(f"✓ Cloud cover: {image.get('CLOUD_COVER').getInfo()}%")
       
       # Step 4: Calculate NDVI
       ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
       print("✓ NDVI calculated")
       
       # Step 5: Get statistics
       point = ee.Geometry.Point([-122.4, 37.8])
       stats = ndvi.reduceRegion(
           reducer=ee.Reducer.mean(),
           geometry=point.buffer(1000),
           scale=30
       )
       
       print(f"✓ Average NDVI: {stats.getInfo()['NDVI']:.3f}")
       print("🎉 First script completed successfully!")
   
   if __name__ == "__main__":
       main()

Understanding the Results
-------------------------

**NDVI Values:**
* -1 to 0: Water, bare soil, rock
* 0 to 0.3: Sparse vegetation, urban areas
* 0.3 to 0.7: Moderate to dense vegetation
* 0.7 to 1: Very dense vegetation

**Next Steps:**
* Try different images and locations
* Experiment with other spectral indices
* Learn about image collections
* Explore visualization options

Common Issues and Solutions
---------------------------

**Authentication Error**

.. code-block:: text

   Error: Please authorize access to your Earth Engine account

**Solution:** Run ``ee.Authenticate()`` first

**Project Not Found**

.. code-block:: text

   Error: Project not found or not registered

**Solution:** Check your project ID and ensure it's registered with Earth Engine

**Network Timeout**

.. code-block:: text

   Error: Connection timeout

**Solution:** Check internet connection and try again

What You've Learned
-------------------

✅ **Earth Engine Basics**
* How to initialize Earth Engine
* Loading and exploring satellite images
* Understanding image properties and metadata

✅ **Core Concepts**
* Earth Engine objects (Image, Geometry)
* Server-side vs client-side operations
* Getting information with ``.getInfo()``

✅ **Simple Analysis**
* Calculating spectral indices
* Extracting regional statistics
* Basic mathematical operations

Next: :doc:`image-display`
