Authentication Methods Reference
================================

Complete reference for all Google Earth Engine authentication methods.

Interactive Authentication
---------------------------

**ee.Authenticate()**

Initiates browser-based OAuth authentication flow.

.. code-block:: python

   ee.Authenticate(force=False, scopes=None)

**Parameters:**

* ``force`` (bool, optional): Force re-authentication even if credentials exist
* ``scopes`` (list, optional): OAuth scopes to request

**Example:**

.. code-block:: python

   import ee
   
   # Standard authentication
   ee.Authenticate()
   
   # Force new authentication
   ee.Authenticate(force=True)
   
   # Custom scopes
   ee.Authenticate(scopes=['https://www.googleapis.com/auth/earthengine'])

**Returns:** None

**Raises:**

* ``AuthenticationException``: If authentication fails
* ``NetworkException``: If network connection fails

Service Account Authentication
------------------------------

**ee.ServiceAccountCredentials()**

Creates service account credentials object.

.. code-block:: python

   ee.ServiceAccountCredentials(email, key_file=None, key_data=None)

**Parameters:**

* ``email`` (str): Service account email address
* ``key_file`` (str, optional): Path to JSON key file
* ``key_data`` (str, optional): JSON key data as string

**Example:**

.. code-block:: python

   import ee
   
   # Using key file
   credentials = ee.ServiceAccountCredentials(
       email='service-account@project.iam.gserviceaccount.com',
       key_file='/path/to/service-account-key.json'
   )
   
   # Using key data string
   import json
   with open('key.json', 'r') as f:
       key_data = f.read()
   
   credentials = ee.ServiceAccountCredentials(
       email='service-account@project.iam.gserviceaccount.com',
       key_data=key_data
   )

**Returns:** ServiceAccountCredentials object

**Raises:**

* ``IOError``: If key file cannot be read
* ``ValueError``: If key data is invalid
* ``AuthenticationException``: If credentials are invalid

Initialization
--------------

**ee.Initialize()**

Initializes Earth Engine with authentication credentials.

.. code-block:: python

   ee.Initialize(credentials=None, project=None, opt_url=None)

**Parameters:**

* ``credentials`` (Credentials, optional): Authentication credentials
* ``project`` (str, optional): Google Cloud project ID
* ``opt_url`` (str, optional): Custom Earth Engine API URL

**Example:**

.. code-block:: python

   import ee
   
   # Interactive authentication
   ee.Authenticate()
   ee.Initialize(project='your-project-id')
   
   # Service account authentication
   credentials = ee.ServiceAccountCredentials(
       email='service-account@project.iam.gserviceaccount.com',
       key_file='/path/to/key.json'
   )
   ee.Initialize(credentials, project='your-project-id')
   
   # Using environment credentials
   ee.Initialize(project='your-project-id')

**Returns:** None

**Raises:**

* ``EEException``: If initialization fails
* ``AuthenticationException``: If authentication is invalid
* ``ProjectException``: If project is not configured

Authentication Utilities
------------------------

**ee.Reset()**

Resets Earth Engine initialization state.

.. code-block:: python

   ee.Reset()

**Example:**

.. code-block:: python

   import ee
   
   # Reset Earth Engine state
   ee.Reset()
   
   # Re-initialize with different credentials
   ee.Initialize(project='different-project-id')

**ee.data.getInfo()**

Get information about current authentication state.

.. code-block:: python

   info = ee.data.getInfo()

**Returns:** Dictionary with authentication information

Environment Variables
---------------------

**GOOGLE_APPLICATION_CREDENTIALS**

Path to service account JSON key file.

.. code-block:: bash

   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

**EARTHENGINE_PROJECT**

Default project ID for Earth Engine operations.

.. code-block:: bash

   export EARTHENGINE_PROJECT="your-project-id"

**Example Usage:**

.. code-block:: python

   import ee
   import os
   
   # Will automatically use environment variables
   ee.Initialize()
   
   # Or explicitly specify
   project_id = os.environ.get('EARTHENGINE_PROJECT')
   ee.Initialize(project=project_id)

Error Handling
--------------

**Common Authentication Errors**

.. code-block:: python

   import ee
   
   try:
       ee.Initialize(project='your-project-id')
   except ee.EEException as e:
       if 'not been used' in str(e):
           print("Earth Engine API not enabled for project")
       elif 'does not have permission' in str(e):
           print("Insufficient permissions for Earth Engine")
       else:
           print(f"Earth Engine error: {e}")
   except Exception as e:
       print(f"General authentication error: {e}")

**Credential Validation**

.. code-block:: python

   def validate_credentials(credentials=None, project_id=None):
       """Validate Earth Engine credentials."""
       try:
           if credentials:
               ee.Initialize(credentials, project=project_id)
           else:
               ee.Initialize(project=project_id)
           
           # Test with simple operation
           ee.Image('USGS/SRTMGL1_003').getInfo()
           return True, "Credentials valid"
           
       except Exception as e:
           return False, str(e)

**Automatic Retry Logic**

.. code-block:: python

   def robust_initialize(project_id, max_retries=3):
       """Initialize Earth Engine with retry logic."""
       
       for attempt in range(max_retries):
           try:
               ee.Initialize(project=project_id)
               return True
               
           except Exception as e:
               print(f"Attempt {attempt + 1} failed: {e}")
               
               if attempt < max_retries - 1:
                   print("Trying authentication...")
                   ee.Authenticate()
               else:
                   print("All attempts failed")
                   raise e

Best Practices
--------------

**Development Environment**

.. code-block:: python

   import ee
   
   def setup_development_auth(project_id):
       """Setup authentication for development."""
       try:
           # Try existing credentials first
           ee.Initialize(project=project_id)
           print("✓ Using existing credentials")
       except:
           # Authenticate if needed
           print("Authentication required...")
           ee.Authenticate()
           ee.Initialize(project=project_id)
           print("✓ Authentication complete")

**Production Environment**

.. code-block:: python

   import ee
   import os
   
   def setup_production_auth():
       """Setup authentication for production."""
       
       # Use service account credentials
       key_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
       project_id = os.environ.get('EARTHENGINE_PROJECT')
       
       if not key_file or not project_id:
           raise ValueError("Missing required environment variables")
       
       credentials = ee.ServiceAccountCredentials(
           email=None,  # Will be read from key file
           key_file=key_file
       )
       
       ee.Initialize(credentials, project=project_id)

**Multi-Environment Support**

.. code-block:: python

   import ee
   import os
   
   def flexible_authentication(project_id=None):
       """Flexible authentication for multiple environments."""
       
       # Get project ID
       if not project_id:
           project_id = os.environ.get('EARTHENGINE_PROJECT')
       
       # Try service account first (production)
       key_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
       if key_file:
           try:
               credentials = ee.ServiceAccountCredentials(key_file=key_file)
               ee.Initialize(credentials, project=project_id)
               print("✓ Service account authentication")
               return
           except Exception as e:
               print(f"Service account failed: {e}")
       
       # Fall back to interactive (development)
       try:
           ee.Initialize(project=project_id)
           print("✓ Interactive authentication")
       except:
           ee.Authenticate()
           ee.Initialize(project=project_id)
           print("✓ New interactive authentication")

See Also
--------

* :doc:`../authentication/interactive-auth` - Interactive authentication guide
* :doc:`../authentication/service-account-auth` - Service account setup
* :doc:`../authentication/troubleshooting` - Common issues and solutions
* `Official Authentication Guide <https://developers.google.com/earth-engine/guides/auth>`_

.. note::
   Always use service accounts for production applications and interactive authentication for development and learning.

.. warning::
   Never commit authentication credentials to version control. Use environment variables or secure credential management systems.
