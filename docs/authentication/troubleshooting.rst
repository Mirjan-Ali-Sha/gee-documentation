Authentication Troubleshooting
===============================

Common authentication issues and their solutions for Google Earth Engine.

General Authentication Issues
------------------------------

**Problem: "Google Earth Engine API has not been used"**

.. code-block:: text

   HttpError 403: Google Earth Engine API has not been used in project...

**Solution:**

1. Go to `Google Cloud Console <https://console.cloud.google.com>`_
2. Select your project
3. Navigate to "APIs & Services" > "Library"
4. Search for "Google Earth Engine API"
5. Click "Enable"

**Problem: "User does not have permission"**

.. code-block:: text

   HttpError 403: User does not have permission to access Google Earth Engine

**Solutions:**

1. **Check Account Registration**: Ensure your Earth Engine account is approved
2. **Verify Project Registration**: Register your project at `https://code.earthengine.google.com/register`
3. **Check IAM Permissions**: Ensure proper roles in Google Cloud Console

**Problem: "Default credentials not found"**

.. code-block:: text

   DefaultCredentialsError: Could not automatically determine credentials

**Solutions:**

.. code-block:: python

   # Method 1: Set environment variable
   import os
   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/service-account-key.json'
   
   # Method 2: Explicit authentication
   import ee
   ee.Authenticate()
   ee.Initialize(project='your-project-id')

Interactive Authentication Issues
---------------------------------

**Problem: Browser doesn't open for authentication**

**Solutions:**

.. code-block:: python

   # Force authentication
   import ee
   ee.Authenticate(force=True)
   
   # Or use command line
   # earthengine authenticate

**Problem: "Permission denied" after browser authentication**

**Check these items:**

1. **Correct Google Account**: Ensure you're using the registered account
2. **Project ID**: Verify you're using the correct project ID
3. **Browser Issues**: Try incognito mode or different browser

.. code-block:: python

   import ee
   
   # Clear cached credentials and retry
   ee.Authenticate(force=True)
   ee.Initialize(project='your-correct-project-id')

**Problem: Token refresh failures**

.. code-block:: python

   import ee
   import os
   from pathlib import Path
   
   # Clear cached credentials
   cred_path = Path.home() / '.config' / 'earthengine' / 'credentials'
   if cred_path.exists():
       cred_path.unlink()
       print("Cleared cached credentials")
   
   # Re-authenticate
   ee.Authenticate()
   ee.Initialize(project='your-project-id')

Service Account Authentication Issues
-------------------------------------

**Problem: "Service account key file not found"**

.. code-block:: python

   import ee
   from pathlib import Path
   
   def validate_key_file(key_path):
       """Validate service account key file."""
       
       key_file = Path(key_path)
       
       if not key_file.exists():
           print(f"❌ Key file not found: {key_path}")
           return False
       
       if not key_file.is_file():
           print(f"❌ Path is not a file: {key_path}")
           return False
       
       try:
           import json
           with open(key_file) as f:
               key_data = json.load(f)
           
           required_fields = ['type', 'project_id', 'private_key', 'client_email']
           missing = [field for field in required_fields if field not in key_data]
           
           if missing:
               print(f"❌ Missing required fields: {missing}")
               return False
           
           print("✅ Key file is valid")
           return True
           
       except json.JSONDecodeError:
           print("❌ Invalid JSON format")
           return False
       except Exception as e:
           print(f"❌ Error validating key file: {e}")
           return False
   
   # Usage
   validate_key_file('/path/to/your/service-account-key.json')

**Problem: "Invalid service account credentials"**

**Common causes and solutions:**

1. **Incorrect JSON format**: Validate JSON structure
2. **Wrong project**: Ensure service account is from correct project
3. **Missing permissions**: Check IAM roles

.. code-block:: python

   import ee
   import json
   
   def debug_service_account(key_file):
       """Debug service account issues."""
       
       try:
           with open(key_file) as f:
               key_data = json.load(f)
           
           print(f"Service Account Email: {key_data.get('client_email')}")
           print(f"Project ID: {key_data.get('project_id')}")
           print(f"Key Type: {key_data.get('type')}")
           
           # Test credentials
           credentials = ee.ServiceAccountCredentials(
               email=key_data['client_email'],
               key_file=key_file
           )
           
           ee.Initialize(credentials, project=key_data['project_id'])
           print("✅ Service account authentication successful")
           
       except Exception as e:
           print(f"❌ Service account authentication failed: {e}")

**Problem: "Service account doesn't have Earth Engine access"**

**Solution: Check and assign proper IAM roles**

1. Go to Google Cloud Console > IAM & Admin > IAM
2. Find your service account
3. Ensure it has these roles:
   - Earth Engine Resource Viewer (minimum)
   - Earth Engine Resource Writer (for asset operations)

Google Colab Authentication Issues
----------------------------------

**Problem: Authentication popup blocked**

**Solutions:**

.. code-block:: python

   # Method 1: Allow popups for colab.research.google.com
   # Check browser popup settings
   
   # Method 2: Use incognito mode
   # Open Colab in incognito/private browsing
   
   # Method 3: Manual authentication
   import ee
   print("Visit: https://code.earthengine.google.com/")
   print("Then run: ee.Initialize(project='your-project-id')")

**Problem: Session timeout in Colab**

.. code-block:: python

   import ee
   
   def refresh_colab_auth(project_id):
       """Refresh authentication in Colab."""
       try:
           # Test current authentication
           ee.Image('USGS/SRTMGL1_003').getInfo()
           print("✅ Authentication still valid")
       except:
           print("🔄 Refreshing authentication...")
           ee.Authenticate()
           ee.Initialize(project=project_id)
           print("✅ Authentication refreshed")
   
   # Use when getting authentication errors
   refresh_colab_auth('your-project-id')

**Problem: Runtime restart required**

.. code-block:: python

   # After runtime restart, re-run authentication
   import ee
   
   # Clear any cached state
   try:
       ee.Reset()
   except:
       pass
   
   # Re-authenticate
   ee.Authenticate()
   ee.Initialize(project='your-project-id')

Network and Firewall Issues
---------------------------

**Problem: Connection timeout or network errors**

**Corporate/Institutional Networks:**

.. code-block:: python

   import ee
   import os
   
   # Set proxy if required
   os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
   os.environ['HTTPS_PROXY'] = 'https://proxy.company.com:8080'
   
   # Disable SSL verification if needed (not recommended for production)
   os.environ['PYTHONHTTPSVERIFY'] = '0'
   
   ee.Initialize(project='your-project-id')

**Firewall Issues:**

Ensure these domains are accessible:
- `*.googleapis.com`
- `*.google.com`
- `earthengine.googleapis.com`
- `accounts.google.com`

Project Configuration Issues
----------------------------

**Problem: "Project not found" or "Invalid project ID"**

**Verification steps:**

.. code-block:: python

   import ee
   
   def verify_project_setup(project_id):
       """Verify project configuration."""
       
       print(f"🔍 Verifying project: {project_id}")
       
       try:
           # Test basic initialization
           ee.Initialize(project=project_id)
           
           # Test API access
           image = ee.Image('USGS/SRTMGL1_003')
           info = image.getInfo()
           
           print("✅ Project verification successful")
           print(f"   - Project ID: {project_id}")
           print(f"   - API Access: Working")
           print(f"   - Test Image: {info['type']}")
           
       except Exception as e:
           print(f"❌ Project verification failed: {e}")
           
           print("\n🔧 Troubleshooting steps:")
           print("1. Check project ID spelling")
           print("2. Ensure Earth Engine API is enabled")
           print("3. Verify project registration with Earth Engine")
           print("4. Check IAM permissions")
   
   # Usage
   verify_project_setup('your-project-id')

**Problem: Billing account issues**

Some operations require billing to be enabled:

1. Go to Google Cloud Console > Billing
2. Ensure billing account is linked and active
3. Verify payment method is current

Diagnostic Tools
----------------

**Comprehensive Authentication Diagnostic**

.. code-block:: python

   import ee
   import os
   import json
   from pathlib import Path
   
   def diagnose_authentication():
       """Comprehensive authentication diagnostic."""
       
       print("🔍 Earth Engine Authentication Diagnostic")
       print("=" * 50)
       
       # Check environment variables
       print("\n📋 Environment Variables:")
       gac = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
       print(f"GOOGLE_APPLICATION_CREDENTIALS: {gac}")
       
       if gac:
           print(f"Credential file exists: {Path(gac).exists()}")
       
       # Check credential file locations
       print("\n📁 Credential File Locations:")
       possible_paths = [
           Path.home() / '.config' / 'earthengine' / 'credentials',
           Path.home() / '.config' / 'gcloud' / 'application_default_credentials.json',
           '/etc/gcloud/application_default_credentials.json'
       ]
       
       for path in possible_paths:
           exists = path.exists()
           print(f"   {path}: {'✅' if exists else '❌'}")
       
       # Test different authentication methods
       print("\n🧪 Testing Authentication Methods:")
       
       # Method 1: Default initialization
       try:
           ee.Initialize()
           print("✅ Default initialization: Success")
           test_passed = True
       except Exception as e:
           print(f"❌ Default initialization: {e}")
           test_passed = False
       
       # If default failed, try with project
       if not test_passed:
           project_id = input("Enter your project ID for testing: ")
           try:
               ee.Initialize(project=project_id)
               print("✅ Project-specific initialization: Success")
           except Exception as e:
               print(f"❌ Project-specific initialization: {e}")
       
       # Test API access
       print("\n🌐 Testing API Access:")
       try:
           image = ee.Image('USGS/SRTMGL1_003')
           info = image.getInfo()
           print(f"✅ API access successful: {info['type']}")
       except Exception as e:
           print(f"❌ API access failed: {e}")
       
       print("\n" + "=" * 50)
       print("Diagnostic complete!")
   
   # Run diagnostic
   diagnose_authentication()

**Connection Test Function**

.. code-block:: python

   import ee
   import time
   
   def test_ee_connection(project_id, num_tests=3):
       """Test Earth Engine connection stability."""
       
       print(f"🧪 Testing Earth Engine connection ({num_tests} tests)")
       
       success_count = 0
       total_time = 0
       
       for i in range(num_tests):
           try:
               start_time = time.time()
               
               # Initialize
               ee.Initialize(project=project_id)
               
               # Simple operation
               image = ee.Image('USGS/SRTMGL1_003')
               info = image.getInfo()
               
               # More complex operation
               mean_elevation = image.reduceRegion(
                   reducer=ee.Reducer.mean(),
                   geometry=ee.Geometry.Point([0, 0]).buffer(1000),
                   scale=1000
               ).getInfo()
               
               elapsed = time.time() - start_time
               total_time += elapsed
               success_count += 1
               
               print(f"   Test {i+1}: ✅ Success ({elapsed:.2f}s)")
               
           except Exception as e:
               print(f"   Test {i+1}: ❌ Failed - {e}")
           
           time.sleep(1)  # Brief pause between tests
       
       print(f"\n📊 Results: {success_count}/{num_tests} tests passed")
       if success_count > 0:
           avg_time = total_time / success_count
           print(f"   Average response time: {avg_time:.2f}s")
       
       return success_count == num_tests

Getting Help
------------

**Official Resources:**

* `Earth Engine Help Center <https://developers.google.com/earth-engine/help>`_
* `Google Earth Engine Developers Group <https://groups.google.com/g/google-earth-engine-developers>`_
* `Stack Overflow <https://stackoverflow.com/questions/tagged/google-earth-engine>`_

**Before Asking for Help:**

1. Run the diagnostic tools above
2. Check official documentation
3. Search existing forum posts
4. Provide specific error messages and code

**Information to Include:**

* Complete error message
* Your authentication method
* Operating system and Python version
* Project ID (if not sensitive)
* Minimal code that reproduces the issue

.. code-block:: python

   # Template for help requests
   """
   Earth Engine Authentication Issue
   
   Problem: [Brief description]
   
   Error Message:
   [Complete error message]
   
   Environment:
   - OS: [Windows/macOS/Linux]
   - Python: [version]
   - Earth Engine API: [version]
   - Authentication method: [Interactive/Service Account/Colab]
   
   Code that reproduces the issue:
   [Minimal example]
   
   What I've tried:
   [List troubleshooting steps attempted]
   """

Next Steps
----------

If authentication issues persist:

1. Try the diagnostic tools provided
2. Check the official documentation
3. Ask for help in the community forums
4. Consider alternative authentication methods

.. note::
   Most authentication issues are related to project configuration or API permissions. Double-check these settings first.

.. tip::
   Keep your Earth Engine API and authentication libraries up to date. Many issues are resolved in newer versions.
