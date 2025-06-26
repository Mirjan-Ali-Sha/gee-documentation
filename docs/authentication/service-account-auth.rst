Service Account Authentication
==============================

Service accounts provide secure, automated authentication for production applications and server environments.

What are Service Accounts?
---------------------------

Service accounts are special Google accounts designed for applications rather than humans:

* **Non-interactive**: No browser-based authentication required
* **Secure**: Use cryptographic keys instead of passwords
* **Scalable**: Perfect for automated workflows and production systems
* **Auditable**: Detailed logging and monitoring capabilities

When to Use Service Accounts
-----------------------------

**Production Applications**
  * Web applications serving Earth Engine data
  * Automated analysis pipelines
  * Scheduled data processing jobs
  * API services and microservices

**Server Environments**
  * Headless servers without browser access
  * Docker containers and cloud deployments
  * Continuous integration/deployment pipelines
  * Batch processing systems

**Team Collaboration**
  * Shared analysis environments
  * Jupyter Hub deployments
  * Research computing clusters
  * Educational platforms

Creating Service Accounts
--------------------------

**Step 1: Access Google Cloud Console**

1. Go to `Google Cloud Console <https://console.cloud.google.com>`_
2. Select your Earth Engine-enabled project
3. Navigate to "IAM & Admin" > "Service Accounts"

**Step 2: Create New Service Account**

1. Click "Create Service Account"
2. Fill in service account details:

   * **Name**: Descriptive name (e.g., "ee-production-service")
   * **ID**: Auto-generated or custom (e.g., "ee-prod-svc")
   * **Description**: Purpose and usage details

3. Click "Create and Continue"

**Step 3: Assign Roles**

Assign appropriate roles for Earth Engine access:

.. list-table::
   :widths: 30 40 30
   :header-rows: 1

   * - Role
     - Permissions
     - Use Case
   * - Earth Engine Resource Viewer
     - Read access to EE resources
     - Basic analysis and visualization
   * - Earth Engine Resource Writer
     - Read/write access to EE assets
     - Asset creation and management
   * - Service Account User
     - Use service account credentials
     - Required for impersonation
   * - Storage Object Viewer
     - Read Google Cloud Storage
     - Asset imports
   * - Storage Object Creator
     - Write to Cloud Storage
     - Export operations

**Step 4: Generate JSON Key**

1. Click on the created service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" format
5. Click "Create" to download the key file

.. warning::
   The JSON key file contains sensitive credentials. Store it securely and never commit it to version control.

JSON Key File Structure
-----------------------

The downloaded JSON file contains:

.. code-block:: json

   {
     "type": "service_account",
     "project_id": "your-project-id",
     "private_key_id": "key-id",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "service-account-name@your-project.iam.gserviceaccount.com",
     "client_id": "client-id",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
     "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account-name%40your-project.iam.gserviceaccount.com"
   }

Using Service Account Authentication
------------------------------------

**Method 1: Direct JSON File Path**

.. code-block:: python

   import ee
   
   # Path to your service account key file
   service_account_key = '/path/to/service-account-key.json'
   
   # Initialize with service account
   credentials = ee.ServiceAccountCredentials(
       email=None,  # Will be read from JSON file
       key_file=service_account_key
   )
   
   ee.Initialize(credentials, project='your-project-id')
   print("✓ Authenticated with service account")

**Method 2: Explicit Email and Key File**

.. code-block:: python

   import ee
   
   # Service account details
   service_account_email = 'your-service-account@your-project.iam.gserviceaccount.com'
   service_account_key = '/path/to/service-account-key.json'
   
   # Initialize with explicit parameters
   credentials = ee.ServiceAccountCredentials(
       email=service_account_email,
       key_file=service_account_key
   )
   
   ee.Initialize(credentials, project='your-project-id')

**Method 3: Environment Variables**

.. code-block:: python

   import ee
   import os
   
   # Set environment variable
   os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/service-account-key.json'
   
   # Initialize (will automatically use environment variable)
   ee.Initialize(project='your-project-id')

**Method 4: JSON String (for containerized environments)**

.. code-block:: python

   import ee
   import json
   import os
   
   # Read JSON key from environment variable
   service_account_info = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
   
   # Create credentials from JSON info
   credentials = ee.ServiceAccountCredentials(
       email=service_account_info['client_email'],
       key_data=json.dumps(service_account_info)
   )
   
   ee.Initialize(credentials, project='your-project-id')

Production Environment Setup
----------------------------

**Secure Credential Storage**

.. code-block:: python

   import ee
   import os
   from pathlib import Path
   
   def get_ee_credentials():
       """Securely load Earth Engine credentials."""
       
       # Try environment variable first
       cred_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
       if cred_path and Path(cred_path).exists():
           return ee.ServiceAccountCredentials(key_file=cred_path)
       
       # Try default locations
       default_paths = [
           '~/.config/gcloud/service-account-key.json',
           '/etc/gcloud/service-account-key.json',
           './credentials/service-account-key.json'
       ]
       
       for path in default_paths:
           full_path = Path(path).expanduser()
           if full_path.exists():
               return ee.ServiceAccountCredentials(key_file=str(full_path))
       
       raise FileNotFoundError("No valid credentials found")
   
   # Usage
   try:
       credentials = get_ee_credentials()
       ee.Initialize(credentials, project='your-project-id')
       print("✓ Service account authentication successful")
   except Exception as e:
       print(f"✗ Authentication failed: {e}")

**Docker Environment**

.. code-block:: dockerfile

   # Dockerfile
   FROM python:3.11-slim
   
   # Install Earth Engine API
   RUN pip install earthengine-api
   
   # Copy application code
   COPY . /app
   WORKDIR /app
   
   # Service account key will be mounted as volume or environment variable
   ENV GOOGLE_APPLICATION_CREDENTIALS=/credentials/service-account-key.json
   
   CMD ["python", "main.py"]

.. code-block:: bash

   # Run with mounted credentials
   docker run -v /host/path/to/credentials:/credentials my-ee-app

**Kubernetes Deployment**

.. code-block:: yaml

   # k8s-secret.yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: ee-service-account
   type: Opaque
   data:
     service-account-key.json: <base64-encoded-json-key>
   
   ---
   # deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: ee-application
   spec:
     template:
       spec:
         containers:
         - name: app
           image: my-ee-app:latest
           env:
           - name: GOOGLE_APPLICATION_CREDENTIALS
             value: /credentials/service-account-key.json
           volumeMounts:
           - name: credentials
             mountPath: /credentials
             readOnly: true
         volumes:
         - name: credentials
           secret:
             secretName: ee-service-account

Error Handling and Validation
------------------------------

**Comprehensive Authentication Function**

.. code-block:: python

   import ee
   import json
   import os
   from pathlib import Path
   import logging
   
   def authenticate_service_account(project_id, credential_path=None, max_retries=3):
       """
       Robust service account authentication with error handling.
       
       Args:
           project_id: Google Cloud project ID
           credential_path: Path to service account JSON file (optional)
           max_retries: Maximum authentication retry attempts
       
       Returns:
           bool: True if authentication successful
       """
       
       for attempt in range(max_retries):
           try:
               # Determine credential source
               if credential_path:
                   if not Path(credential_path).exists():
                       raise FileNotFoundError(f"Credential file not found: {credential_path}")
                   
                   credentials = ee.ServiceAccountCredentials(key_file=credential_path)
               
               elif os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
                   # Use environment variable
                   credentials = None  # ee.Initialize will auto-detect
               
               elif os.environ.get('SERVICE_ACCOUNT_JSON'):
                   # Use JSON string from environment
                   service_account_info = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
                   credentials = ee.ServiceAccountCredentials(
                       email=service_account_info['client_email'],
                       key_data=os.environ['SERVICE_ACCOUNT_JSON']
                   )
               
               else:
                   raise ValueError("No service account credentials found")
               
               # Initialize Earth Engine
               if credentials:
                   ee.Initialize(credentials, project=project_id)
               else:
                   ee.Initialize(project=project_id)
               
               # Test authentication with simple operation
               test_image = ee.Image('USGS/SRTMGL1_003')
               test_info = test_image.getInfo()
               
               logging.info("✓ Service account authentication successful")
               return True
               
           except Exception as e:
               logging.warning(f"Authentication attempt {attempt + 1} failed: {e}")
               if attempt == max_retries - 1:
                   logging.error("✗ All authentication attempts failed")
                   raise
               
       return False

**Credential Validation**

.. code-block:: python

   import ee
   import json
   
   def validate_service_account_key(key_file_path):
       """
       Validate service account key file format and contents.
       
       Args:
           key_file_path: Path to JSON key file
       
       Returns:
           dict: Validation results
       """
       
       validation_results = {
           'file_exists': False,
           'valid_json': False,
           'has_required_fields': False,
           'service_account_email': None,
           'project_id': None,
           'errors': []
       }
       
       try:
           # Check file existence
           if not Path(key_file_path).exists():
               validation_results['errors'].append(f"File does not exist: {key_file_path}")
               return validation_results
           
           validation_results['file_exists'] = True
           
           # Parse JSON
           with open(key_file_path, 'r') as f:
               key_data = json.load(f)
           
           validation_results['valid_json'] = True
           
           # Check required fields
           required_fields = [
               'type', 'project_id', 'private_key_id', 'private_key',
               'client_email', 'client_id', 'auth_uri', 'token_uri'
           ]
           
           missing_fields = [field for field in required_fields if field not in key_data]
           
           if missing_fields:
               validation_results['errors'].append(f"Missing required fields: {missing_fields}")
           else:
               validation_results['has_required_fields'] = True
               validation_results['service_account_email'] = key_data['client_email']
               validation_results['project_id'] = key_data['project_id']
               
               # Validate service account type
               if key_data.get('type') != 'service_account':
                   validation_results['errors'].append("Invalid credential type (not service_account)")
           
       except json.JSONDecodeError as e:
           validation_results['errors'].append(f"Invalid JSON format: {e}")
       except Exception as e:
           validation_results['errors'].append(f"Validation error: {e}")
       
       return validation_results

Security Best Practices
------------------------

**Credential Management**

.. code-block:: python

   import ee
   import os
   import stat
   from pathlib import Path
   
   def secure_credential_setup(credential_path):
       """
       Set up service account credentials with proper security.
       """
       
       # Ensure file has restrictive permissions (600 = owner read/write only)
       credential_file = Path(credential_path)
       credential_file.chmod(stat.S_IRUSR | stat.S_IWUSR)
       
       # Verify ownership (Unix systems)
       if os.name == 'posix':
           file_stat = credential_file.stat()
           if file_stat.st_uid != os.getuid():
               print("Warning: Credential file not owned by current user")
       
       print(f"✓ Credential file secured: {credential_path}")

**Key Rotation**

.. code-block:: python

   import ee
   import json
   import datetime
   from pathlib import Path
   
   def check_key_age(credential_path, max_age_days=90):
       """
       Check if service account key needs rotation.
       
       Args:
           credential_path: Path to credential file
           max_age_days: Maximum key age in days
       
       Returns:
           dict: Key age information
       """
       
       credential_file = Path(credential_path)
       
       if not credential_file.exists():
           return {'needs_rotation': True, 'reason': 'File not found'}
       
       # Check file modification time
       mtime = datetime.datetime.fromtimestamp(credential_file.stat().st_mtime)
       age = datetime.datetime.now() - mtime
       
       needs_rotation = age.days > max_age_days
       
       return {
           'needs_rotation': needs_rotation,
           'age_days': age.days,
           'max_age_days': max_age_days,
           'created_date': mtime.strftime('%Y-%m-%d'),
           'reason': f'Key is {age.days} days old' if needs_rotation else 'Key is current'
       }

**Access Monitoring**

.. code-block:: python

   import ee
   import logging
   import time
   from functools import wraps
   
   def monitor_ee_access(func):
       """
       Decorator to monitor Earth Engine API access.
       """
       @wraps(func)
       def wrapper(*args, **kwargs):
           start_time = time.time()
           
           try:
               result = func(*args, **kwargs)
               execution_time = time.time() - start_time
               
               logging.info(f"EE API call successful: {func.__name__} "
                          f"(execution time: {execution_time:.2f}s)")
               
               return result
               
           except Exception as e:
               execution_time = time.time() - start_time
               
               logging.error(f"EE API call failed: {func.__name__} "
                           f"(execution time: {execution_time:.2f}s) - {e}")
               raise
       
       return wrapper
   
   # Usage
   @monitor_ee_access
   def get_image_info(image_id):
       return ee.Image(image_id).getInfo()

Troubleshooting Service Account Issues
--------------------------------------

**Common Error Messages**

.. code-block:: text

   Error: Service account does not have permission to access Google Earth Engine.

**Solution**: Ensure proper IAM roles are assigned

.. code-block:: text

   Error: Could not load the default credentials.

**Solution**: Set GOOGLE_APPLICATION_CREDENTIALS environment variable

.. code-block:: text

   Error: Invalid service account key file.

**Solution**: Validate JSON key file format and contents

**Debugging Authentication**

.. code-block:: python

   import ee
   import json
   import os
   
   def debug_service_account_auth():
       """
       Debug service account authentication issues.
       """
       
       print("🔍 Debugging Service Account Authentication")
       print("=" * 50)
       
       # Check environment variables
       env_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
       print(f"GOOGLE_APPLICATION_CREDENTIALS: {env_creds}")
       
       if env_creds:
           print(f"Credential file exists: {Path(env_creds).exists()}")
           
           # Validate JSON
           try:
               with open(env_creds, 'r') as f:
                   key_data = json.load(f)
               print(f"Service account email: {key_data.get('client_email')}")
               print(f"Project ID: {key_data.get('project_id')}")
           except Exception as e:
               print(f"Error reading credential file: {e}")
       
       # Test authentication
       try:
           ee.Initialize()
           print("✓ Authentication successful")
       except Exception as e:
           print(f"✗ Authentication failed: {e}")

Next Steps
----------

After setting up service account authentication:

1. :doc:`colab-auth` - Learn about Colab authentication
2. :doc:`troubleshooting` - Solve common issues
3. :doc:`../examples/intermediate/index` - Try intermediate examples
4. Implement production workflows

.. note::
   Service account keys are sensitive credentials. Treat them like passwords and implement proper security measures.

.. tip::
   Use different service accounts for different environments (development, testing, production) to maintain security boundaries.

.. warning::
   Regularly rotate service account keys and monitor their usage. Compromised keys can lead to unauthorized access to your Google Cloud resources.
