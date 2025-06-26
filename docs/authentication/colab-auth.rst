Google Colab Authentication
===========================

Google Colab provides simplified authentication for Earth Engine through built-in integration with Google services.

Why Use Colab for Earth Engine?
--------------------------------

Google Colab offers several advantages for Earth Engine development:

* **Pre-installed Packages**: Earth Engine API comes pre-installed
* **Free GPU/TPU Access**: Accelerated computing for analysis
* **Easy Sharing**: Share notebooks with colleagues and students
* **No Local Setup**: No need to install packages locally
* **Integrated Authentication**: Streamlined authentication process

Authentication Methods in Colab
--------------------------------

**Method 1: Standard Colab Authentication**

.. code-block:: python

   import ee
   
   # Trigger authentication in Colab
   ee.Authenticate()
   
   # Initialize with your project
   ee.Initialize(project='your-project-id')
   
   print("✓ Earth Engine initialized in Colab!")

**Method 2: Token-Based Authentication**

.. code-block:: python

   import ee
   from google.colab import auth
   
   # Authenticate with Google Colab
   auth.authenticate_user()
   
   # Initialize Earth Engine
   ee.Initialize(project='your-project-id')

**Method 3: Service Account in Colab**

.. code-block:: python

   import ee
   import json
   from google.colab import files
   
   # Upload service account key file
   uploaded = files.upload()
   
   # Get the uploaded file name
   key_file = list(uploaded.keys())[0]
   
   # Initialize with service account
   credentials = ee.ServiceAccountCredentials(
       email=None,
       key_file=key_file
   )
   
   ee.Initialize(credentials, project='your-project-id')

**Method 4: Using Colab Secrets**

.. code-block:: python

   import ee
   import json
   from google.colab import userdata
   
   # Store your service account JSON as a secret named 'EE_SERVICE_ACCOUNT'
   service_account_info = json.loads(userdata.get('EE_SERVICE_ACCOUNT'))
   
   # Create credentials
   credentials = ee.ServiceAccountCredentials(
       email=service_account_info['client_email'],
       key_data=json.dumps(service_account_info)
   )
   
   ee.Initialize(credentials, project='your-project-id')

Setting Up Colab Secrets
-------------------------

**Step 1: Access Secrets Manager**

1. In your Colab notebook, click the 🔑 key icon in the left sidebar
2. Click "Add new secret"
3. Enter secret details

**Step 2: Store Earth Engine Credentials**

.. code-block:: python

   # Secret Name: EE_SERVICE_ACCOUNT
   # Secret Value: [paste your entire service account JSON here]
   
   # Secret Name: EE_PROJECT_ID  
   # Secret Value: your-project-id

**Step 3: Use Secrets in Code**

.. code-block:: python

   import ee
   import json
   from google.colab import userdata
   
   # Retrieve secrets
   project_id = userdata.get('EE_PROJECT_ID')
   service_account_json = userdata.get('EE_SERVICE_ACCOUNT')
   
   # Parse service account
   service_account_info = json.loads(service_account_json)
   
   # Initialize Earth Engine
   credentials = ee.ServiceAccountCredentials(
       email=service_account_info['client_email'],
       key_data=service_account_json
   )
   
   ee.Initialize(credentials, project=project_id)

Complete Colab Setup Template
------------------------------

.. code-block:: python

   """
   Google Colab Earth Engine Setup Template
   ========================================
   
   This cell sets up Earth Engine authentication in Google Colab
   with error handling and multiple authentication methods.
   """
   
   import ee
   import json
   import sys
   from google.colab import userdata, auth
   
   def setup_earth_engine(project_id=None, use_service_account=False):
       """
       Set up Earth Engine authentication in Google Colab.
       
       Args:
           project_id: Google Cloud project ID (optional if stored in secrets)
           use_service_account: Whether to use service account authentication
       
       Returns:
           bool: True if setup successful
       """
       
       try:
           # Get project ID
           if not project_id:
               try:
                   project_id = userdata.get('EE_PROJECT_ID')
                   print(f"✓ Using project ID from secrets: {project_id}")
               except:
                   project_id = input("Enter your Google Cloud project ID: ")
           
           if use_service_account:
               # Service account authentication
               print("🔐 Setting up service account authentication...")
               
               try:
                   service_account_json = userdata.get('EE_SERVICE_ACCOUNT')
                   service_account_info = json.loads(service_account_json)
                   
                   credentials = ee.ServiceAccountCredentials(
                       email=service_account_info['client_email'],
                       key_data=service_account_json
                   )
                   
                   ee.Initialize(credentials, project=project_id)
                   print("✓ Service account authentication successful!")
                   
               except Exception as e:
                   print(f"✗ Service account authentication failed: {e}")
                   print("Falling back to interactive authentication...")
                   use_service_account = False
           
           if not use_service_account:
               # Interactive authentication
               print("🔐 Setting up interactive authentication...")
               
               try:
                   # Try to initialize (may work if already authenticated)
                   ee.Initialize(project=project_id)
                   print("✓ Using existing authentication!")
                   
               except:
                   # Trigger authentication flow
                   print("Please complete the authentication process...")
                   ee.Authenticate()
                   ee.Initialize(project=project_id)
                   print("✓ Interactive authentication successful!")
           
           # Test the connection
           print("🧪 Testing Earth Engine connection...")
           test_image = ee.Image('USGS/SRTMGL1_003')
           info = test_image.getInfo()
           print(f"✓ Connection test successful! Image type: {info['type']}")
           
           return True
           
       except Exception as e:
           print(f"✗ Earth Engine setup failed: {e}")
           return False
   
   # Run setup
   if setup_earth_engine(project_id='your-project-id'):
       print("\n🎉 Earth Engine is ready to use!")
   else:
       print("\n❌ Setup failed. Please check your configuration.")

Troubleshooting Colab Authentication
------------------------------------

**Common Issues and Solutions**

**Authentication Popup Blocked**

.. code-block:: python

   # If popup is blocked, try this approach
   import ee
   
   print("If popup is blocked, manually visit this URL:")
   print("https://code.earthengine.google.com/")
   print("Then come back and run ee.Initialize()")
   
   ee.Authenticate(force=True)  # Force new authentication
   ee.Initialize(project='your-project-id')

**Session Timeout Issues**

.. code-block:: python

   import ee
   
   def refresh_ee_authentication(project_id):
       """Refresh Earth Engine authentication in Colab."""
       try:
           # Test current authentication
           ee.Image('USGS/SRTMGL1_003').getInfo()
           print("✓ Authentication still valid")
           return True
       except:
           print("🔄 Refreshing authentication...")
           ee.Authenticate()
           ee.Initialize(project=project_id)
           return True
   
   # Use this function when you get authentication errors
   refresh_ee_authentication('your-project-id')

**Runtime Restart Required**

.. code-block:: python

   # Sometimes you need to restart the runtime
   # Runtime > Restart runtime, then re-run authentication
   
   import ee
   
   # Clear any cached credentials
   try:
       ee.Reset()
   except:
       pass
   
   # Re-authenticate
   ee.Authenticate()
   ee.Initialize(project='your-project-id')

**Memory Issues with Large Operations**

.. code-block:: python

   import ee
   import gc
   
   def optimize_colab_memory():
       """Optimize memory usage in Colab for Earth Engine operations."""
       
       # Clear variables
       gc.collect()
       
       # Reset Earth Engine (clears cache)
       try:
           ee.Reset()
           ee.Initialize(project='your-project-id')
       except:
           pass
       
       print("✓ Memory optimized")
   
   # Use this function if you encounter memory issues
   optimize_colab_memory()

Colab-Specific Best Practices
-----------------------------

**Notebook Organization**

.. code-block:: python

   # Cell 1: Setup and Authentication
   import ee
   import numpy as np
   import matplotlib.pyplot as plt
   
   # Setup Earth Engine
   ee.Authenticate()
   ee.Initialize(project='your-project-id')
   
   # Cell 2: Helper Functions
   def display_image(image, vis_params, title="Image"):
       """Display Earth Engine image in Colab."""
       # Your display code here
       pass
   
   # Cell 3: Main Analysis
   # Your analysis code here

**Sharing Notebooks**

.. code-block:: python

   # Template for shared notebooks
   """
   # Earth Engine Analysis in Google Colab
   
   ## Setup Instructions
   1. Run the authentication cell below
   2. Replace 'your-project-id' with your actual project ID
   3. Execute cells in order
   
   ## Authentication
   """
   
   import ee
   
   # Users will need to run this
   PROJECT_ID = 'your-project-id'  # Replace with your project ID
   
   try:
       ee.Initialize(project=PROJECT_ID)
       print("✓ Earth Engine ready!")
   except:
       print("Please authenticate:")
       ee.Authenticate()
       ee.Initialize(project=PROJECT_ID)

**Data Visualization in Colab**

.. code-block:: python

   import ee
   import folium
   import matplotlib.pyplot as plt
   
   def create_colab_map(image, vis_params, center, zoom=10):
       """Create interactive map for Colab."""
       
       # Create folium map
       m = folium.Map(location=center, zoom_start=zoom)
       
       # Add Earth Engine layer
       map_id_dict = ee.Image(image).getMapId(vis_params)
       folium.raster_layers.TileLayer(
           tiles=map_id_dict['tile_fetcher'].url_format,
           attr='Google Earth Engine',
           name='EE Image',
           overlay=True,
           control=True
       ).add_to(m)
       
       return m
   
   def plot_time_series_colab(data, title="Time Series"):
       """Create time series plot optimized for Colab."""
       
       plt.figure(figsize=(12, 6))
       plt.plot(data['dates'], data['values'], 'o-', linewidth=2)
       plt.title(title)
       plt.xlabel('Date')
       plt.ylabel('Value')
       plt.grid(True, alpha=0.3)
       plt.xticks(rotation=45)
       plt.tight_layout()
       plt.show()

Advanced Colab Integration
--------------------------

**Using Colab with Drive Integration**

.. code-block:: python

   import ee
   from google.colab import drive
   import os
   
   # Mount Google Drive
   drive.mount('/content/drive')
   
   # Set up paths
   drive_path = '/content/drive/MyDrive/EarthEngine'
   os.makedirs(drive_path, exist_ok=True)
   
   # Save results to Drive
   def save_to_drive(data, filename):
       """Save analysis results to Google Drive."""
       filepath = os.path.join(drive_path, filename)
       # Your save logic here
       print(f"✓ Saved to: {filepath}")

**Batch Processing in Colab**

.. code-block:: python

   import ee
   import time
   
   def batch_process_colab(image_collection, process_func, batch_size=10):
       """Process large image collections in batches for Colab."""
       
       total_images = image_collection.size().getInfo()
       print(f"Processing {total_images} images in batches of {batch_size}")
       
       results = []
       
       for i in range(0, total_images, batch_size):
           print(f"Processing batch {i//batch_size + 1}/{(total_images//batch_size) + 1}")
           
           # Get batch
           batch = image_collection.limit(batch_size, i)
           
           # Process batch
           batch_result = process_func(batch)
           results.append(batch_result)
           
           # Small delay to avoid rate limits
           time.sleep(1)
       
       return results

Educational Templates
---------------------

**Student Template**

.. code-block:: python

   """
   Earth Engine Tutorial Template for Students
   ==========================================
   
   Instructions:
   1. Click "Copy to Drive" to save your own copy
   2. Run the setup cell below
   3. Complete the exercises
   """
   
   # Setup Cell - Run This First!
   import ee
   
   print("🌍 Welcome to Earth Engine in Google Colab!")
   print("Please complete authentication when prompted.")
   
   ee.Authenticate()
   ee.Initialize(project='your-project-id')
   
   print("✅ Setup complete! You're ready to explore Earth Engine.")
   
   # Exercise 1: Load and display an image
   # TODO: Complete this exercise
   
   # Exercise 2: Calculate NDVI
   # TODO: Complete this exercise

**Instructor Template**

.. code-block:: python

   """
   Earth Engine Course Template for Instructors
   ===========================================
   
   This template provides a complete lesson structure.
   """
   
   # Course Setup
   import ee
   import matplotlib.pyplot as plt
   
   # Pre-authentication for demonstration
   print("🎓 Earth Engine Course - Lesson 1")
   print("Students: Please run authentication when prompted")
   
   def setup_student_environment():
       """Setup function for students."""
       ee.Authenticate()
       ee.Initialize(project='your-project-id')
       print("✅ Student environment ready!")
   
   # Lesson Content
   def lesson_1_basics():
       """Lesson 1: Earth Engine Basics."""
       
       print("📚 Lesson 1: Introduction to Earth Engine")
       
       # Load example image
       image = ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_044034_20140318')
       
       # Display information
       print(f"Image ID: {image.get('system:id').getInfo()}")
       print(f"Bands: {image.bandNames().getInfo()}")
       
       return image

Next Steps
----------

After mastering Colab authentication:

1. :doc:`troubleshooting` - Solve common issues
2. :doc:`../examples/basic/index` - Try basic examples in Colab
3. Create shareable educational notebooks
4. Explore advanced Colab features

.. note::
   Colab sessions have time limits. Save your work frequently and be prepared to re-authenticate if your session expires.

.. tip::
   Use Colab secrets to store credentials securely when sharing notebooks. Never hardcode sensitive information in shared notebooks.

.. warning::
   Free Colab accounts have usage limits. Consider upgrading to Colab Pro for intensive Earth Engine workloads.
