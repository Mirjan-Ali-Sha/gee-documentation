Basic Examples
==============

Start your Earth Engine journey with these fundamental examples that demonstrate core concepts and basic operations.

.. toctree::
   :maxdepth: 2
   :caption: Basic Examples:

   first-script
   image-display
   simple-calculations

Overview
--------

These examples cover essential Earth Engine concepts:

* **Authentication and Initialization**: Setting up your environment
* **Image Loading and Display**: Working with satellite imagery
* **Basic Calculations**: Performing simple analyses
* **Visualization**: Creating maps and charts
* **Data Export**: Saving results for external use

Prerequisites
-------------

Before running these examples, ensure you have:

* Authenticated Earth Engine access
* Python 3.7+ with required packages
* Basic understanding of remote sensing concepts
* Familiarity with Python programming

Example Categories
------------------

**Getting Started**
  * :doc:`first-script` - Your first Earth Engine script
  * Basic image loading and information display
  * Understanding Earth Engine objects and methods

**Image Visualization**
  * :doc:`image-display` - Displaying images with different band combinations
  * Creating interactive maps
  * Understanding visualization parameters

**Simple Analysis**
  * :doc:`simple-calculations` - Basic mathematical operations
  * Spectral index calculations (NDVI, NDWI)
  * Regional statistics and summaries

Common Patterns
---------------

**Basic Script Structure**

.. code-block:: python

   import ee
   
   # Initialize Earth Engine
   ee.Initialize(project='your-project-id')
   
   # Load data
   image = ee.Image('DATASET/IMAGE_ID')
   
   # Process data
   result = image.someOperation()
   
   # Display or export results
   print(result.getInfo())

**Error Handling**

.. code-block:: python

   import ee
   
   try:
       ee.Initialize(project='your-project-id')
       # Your Earth Engine code here
   except Exception as e:
       print(f"Error: {e}")
       # Handle authentication or other issues

Running the Examples
--------------------

**Method 1: Direct Execution**

.. code-block:: bash

   python examples/basic/01_hello_world.py

**Method 2: Interactive Python**

.. code-block:: python

   exec(open('examples/basic/01_hello_world.py').read())

**Method 3: Jupyter Notebook**

Copy the code into Jupyter notebook cells and run interactively.

Learning Path
-------------

Follow this recommended sequence:

1. **Start Here**: :doc:`first-script`
   
   * Understand Earth Engine initialization
   * Learn basic image loading
   * Practice with simple operations

2. **Visualize Data**: :doc:`image-display`
   
   * Explore different imagery types
   * Master visualization parameters
   * Create interactive maps

3. **Analyze Data**: :doc:`simple-calculations`
   
   * Perform basic calculations
   * Calculate spectral indices
   * Generate summary statistics

Tips for Success
----------------

**Development Environment**
  * Use an IDE with good Python support
  * Keep Earth Engine documentation handy
  * Test code with small areas first

**Best Practices**
  * Comment your code thoroughly
  * Use descriptive variable names
  * Handle errors gracefully
  * Validate results before large-scale processing

**Common Mistakes to Avoid**
  * Forgetting to initialize Earth Engine
  * Using incorrect band names
  * Not handling authentication errors
  * Processing areas that are too large

Next Steps
----------

After mastering basic examples:

1. :doc:`../intermediate/index` - Intermediate examples
2. :doc:`../../api-reference/index` - API reference
3. :doc:`../../authentication/troubleshooting` - Problem solving

.. note::
   All examples use placeholder project IDs. Replace 'your-project-id' with your actual Google Cloud project ID.

.. tip::
   Start with small geographic areas and short time periods when learning. You can scale up once you understand the concepts.
