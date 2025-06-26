Interactive Authentication
==========================

Interactive authentication is the simplest method for local development and learning Earth Engine.

How Interactive Authentication Works
------------------------------------

Interactive authentication uses OAuth 2.0 flow:

1. **Authorization Request**: Opens web browser for user consent
2. **User Consent**: User grants permission to Earth Engine
3. **Authorization Code**: Google returns authorization code
4. **Token Exchange**: Code is exchanged for access tokens
5. **Credential Storage**: Tokens stored locally for reuse

Setting Up Interactive Authentication
-------------------------------------

**Step 1: Install Required Packages**

.. code-block:: bash

   pip install earthengine-api
   pip install google-auth-oauthlib

**Step 2: Run Authentication**

.. code-block:: python

   import ee
   
   # Trigger authentication flow
   ee.Authenticate()

**Step 3: Complete Browser Flow**

1. Browser window opens automatically
2. Sign in with your Google account
3. Grant permission to Earth Engine
4. Copy authorization code (if needed)
5. Return to Python environment

**Step 4: Initialize Earth Engine**

.. code-block:: python

   import ee
   
   # Initialize with your project
   ee.Initialize(project='your-project-id')
   
   # Test the connection
   print("Earth Engine initialized successfully!")
   image = ee.Image('USGS/SRTMGL1_003')
   print(f"Test image: {image.getInfo()['type']}")

Alternative Authentication Methods
----------------------------------

**Method 1: Command Line**

.. code-block:: bash

   earthengine authenticate

**Method 2: Explicit Project Specification**

.. code-block:: python

   import ee
   
   # Authenticate with specific project
   ee.Authenticate(project='your-project-id')
   ee.Initialize(project='your-project-id')

**Method 3: Custom Authentication Flow**

.. code-block:: python

   import ee
   from google.auth.transport.requests import Request
   
   # Custom authentication with specific scopes
   ee.Authenticate(
       scopes=['https://www.googleapis.com/auth/earthengine']
   )
   ee.Initialize(project='your-project-id')

Credential Management
---------------------

**Credential Storage Location**

Credentials are stored in:

* **Linux/macOS**: `~/.config/earthengine/credentials`
* **Windows**: `%USERPROFILE%\.config\earthengine\credentials`

**Credential File Format**

.. code-block:: json

   {
     "client_id": "your-client-id",
     "client_secret": "your-client-secret",
     "refresh_token": "your-refresh-token",
     "type": "authorized_user"
   }

**Managing Multiple Credentials**

.. code-block:: python

   import ee
   
   # Use specific credential file
   credentials_path = '/path/to/custom/credentials'
   ee.Initialize(project='your-project-id', credentials_path=credentials_path)

Troubleshooting Interactive Authentication
------------------------------------------

**Browser Doesn't Open**

.. code-block:: python

   import ee
   
   # Force manual authentication
   ee.Authenticate(force=True)

**Permission Denied Errors**

Check these common issues:

1. **Project Not Registered**: Ensure project is registered with Earth Engine
2. **API Not Enabled**: Enable Earth Engine API in Google Cloud Console
3. **Account Not Approved**: Verify Earth Engine account approval

**Token Refresh Issues**

.. code-block:: python

   import ee
   
   # Clear cached credentials and re-authenticate
   ee.Authenticate(force=True)
   ee.Initialize(project='your-project-id')

**Firewall/Proxy Issues**

For corporate networks:

.. code-block:: python

   import ee
   import os
   
   # Set proxy if needed
   os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
   os.environ['HTTPS_PROXY'] = 'https://proxy.company.com:8080'
   
   ee.Authenticate()
   ee.Initialize(project='your-project-id')

Advanced Configuration
----------------------

**Custom Authentication Parameters**

.. code-block:: python

   import ee
   
   # Authenticate with custom parameters
   ee.Authenticate(
       authorization_code='your-auth-code',  # If copying manually
       code_verifier='your-code-verifier'    # For PKCE flow
   )

**Token Validation**

.. code-block:: python

   import ee
   from google.auth.transport.requests import Request
   
   # Initialize and validate token
   ee.Initialize(project='your-project-id')
   
   # Test API access
   try:
       test_image = ee.Image('USGS/SRTMGL1_003')
       info = test_image.getInfo()
       print("✓ Authentication successful")
   except Exception as e:
       print(f"✗ Authentication failed: {e}")

**Credential Refresh**

.. code-block:: python

   import ee
   
   def refresh_credentials():
       """Refresh Earth Engine credentials if needed."""
       try:
           ee.Initialize(project='your-project-id')
           # Test with a simple operation
           ee.Image('USGS/SRTMGL1_003').getInfo()
           return True
       except Exception as e:
           print(f"Refreshing credentials: {e}")
           ee.Authenticate()
           ee.Initialize(project='your-project-id')
           return True
   
   # Use in your scripts
   if refresh_credentials():
       print("Ready to use Earth Engine!")

Best Practices
--------------

**Development Workflow**

1. **One-time Setup**: Run authentication once per development environment
2. **Credential Reuse**: Stored credentials work for future sessions
3. **Regular Refresh**: Re-authenticate if tokens expire
4. **Project Consistency**: Use same project ID across development

**Security Guidelines**

* Never share credential files
* Use separate accounts for different projects
* Regular credential rotation for sensitive projects
* Monitor API usage for unusual activity

**Error Handling**

.. code-block:: python

   import ee
   
   def safe_initialize(project_id, max_retries=3):
       """Safely initialize Earth Engine with retries."""
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
                   print("Max retries exceeded")
                   raise
       return False
   
   # Usage
   if safe_initialize('your-project-id'):
       print("Earth Engine ready!")

Testing Authentication
----------------------

**Basic Connection Test**

.. code-block:: python

   import ee
   
   def test_authentication(project_id):
       """Test Earth Engine authentication and basic functionality."""
       try:
           # Initialize
           ee.Initialize(project=project_id)
           print("✓ Authentication successful")
           
           # Test image access
           image = ee.Image('USGS/SRTMGL1_003')
           info = image.getInfo()
           print(f"✓ Image access successful: {info['type']}")
           
           # Test computation
           mean_elevation = image.reduceRegion(
               reducer=ee.Reducer.mean(),
               geometry=ee.Geometry.Point([0, 0]).buffer(1000),
               scale=1000
           )
           print(f"✓ Computation successful: {mean_elevation.getInfo()}")
           
           return True
           
       except Exception as e:
           print(f"✗ Authentication test failed: {e}")
           return False
   
   # Run test
   test_authentication('your-project-id')

Next Steps
----------

After setting up interactive authentication:

1. :doc:`../examples/basic/index` - Try basic examples
2. :doc:`service-account-auth` - Set up production authentication
3. :doc:`troubleshooting` - Solve common issues

.. note::
   Interactive authentication is perfect for development but not suitable for production applications or automated workflows.

.. warning::
   Credential files contain sensitive information. Protect them like passwords and never commit them to version control.
