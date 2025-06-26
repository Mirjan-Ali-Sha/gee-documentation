API Reference
=============

Complete reference guide for Google Earth Engine authentication methods and common functions.

.. toctree::
   :maxdepth: 2
   :caption: API Reference:

   authentication-methods
   common-functions

Overview
--------

This section provides detailed documentation for:

* **Authentication Methods**: All available authentication approaches
* **Common Functions**: Frequently used Earth Engine operations
* **Code Examples**: Practical implementation patterns
* **Best Practices**: Recommended usage guidelines

Quick Reference
---------------

**Authentication Quick Start**

.. code-block:: python

   import ee
   
   # Interactive authentication
   ee.Authenticate()
   ee.Initialize(project='your-project-id')
   
   # Service account authentication
   credentials = ee.ServiceAccountCredentials(
       email='service-account@project.iam.gserviceaccount.com',
       key_file='path/to/key.json'
   )
   ee.Initialize(credentials, project='your-project-id')

**Common Operations**

.. code-block:: python

   # Load image
   image = ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_044034_20140318')
   
   # Load collection
   collection = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
   
   # Filter collection
   filtered = collection.filterDate('2023-01-01', '2023-12-31')
   
   # Calculate NDVI
   ndvi = image.normalizedDifference(['SR_B5', 'SR_B4'])
   
   # Reduce region
   stats = ndvi.reduceRegion(
       reducer=ee.Reducer.mean(),
       geometry=geometry,
       scale=30
   )

Function Categories
-------------------

**Authentication Functions**
  * ``ee.Authenticate()`` - Interactive authentication
  * ``ee.ServiceAccountCredentials()`` - Service account setup
  * ``ee.Initialize()`` - Initialize Earth Engine

**Data Loading Functions**
  * ``ee.Image()`` - Load single image
  * ``ee.ImageCollection()`` - Load image collection
  * ``ee.FeatureCollection()`` - Load vector data
  * ``ee.Geometry()`` - Create geometry objects

**Processing Functions**
  * ``image.select()`` - Select bands
  * ``image.normalizedDifference()`` - Calculate indices
  * ``collection.filterDate()`` - Temporal filtering
  * ``collection.map()`` - Apply function to collection

**Analysis Functions**
  * ``image.reduceRegion()`` - Zonal statistics
  * ``collection.reduce()`` - Collection reduction
  * ``image.classification()`` - Classification operations
  * ``geometry.buffer()`` - Spatial operations

**Export Functions**
  * ``ee.batch.Export.image.toDrive()`` - Export images
  * ``ee.batch.Export.table.toDrive()`` - Export tables
  * ``ee.batch.Export.video.toDrive()`` - Export videos

Usage Patterns
---------------

**Error Handling Pattern**

.. code-block:: python

   try:
       ee.Initialize(project='your-project-id')
       result = your_earth_engine_operation()
       print("✓ Operation successful")
   except ee.EEException as e:
       print(f"✗ Earth Engine error: {e}")
   except Exception as e:
       print(f"✗ General error: {e}")

**Safe Initialization Pattern**

.. code-block:: python

   def safe_ee_initialize(project_id, max_retries=3):
       for attempt in range(max_retries):
           try:
               ee.Initialize(project=project_id)
               return True
           except:
               if attempt < max_retries - 1:
                   ee.Authenticate()
               else:
                   return False

**Batch Processing Pattern**

.. code-block:: python

   def process_collection_safely(collection, process_func, batch_size=100):
       total = collection.size().getInfo()
       results = []
       
       for i in range(0, total, batch_size):
           batch = collection.limit(batch_size, i)
           batch_result = process_func(batch)
           results.append(batch_result)
       
       return results

See Also
--------

* :doc:`../authentication/index` - Authentication setup guides
* :doc:`../examples/index` - Practical examples
* :doc:`../getting-started/index` - Setup instructions
* `Official Earth Engine API <https://developers.google.com/earth-engine/apidocs>`_

.. note::
   API functions may change between Earth Engine versions. Always refer to the official documentation for the most current information.
