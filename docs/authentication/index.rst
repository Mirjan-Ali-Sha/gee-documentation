Authentication Methods
======================

Google Earth Engine supports multiple authentication methods depending on your use case and environment.

.. toctree::
   :maxdepth: 2
   :caption: Authentication Methods:

   interactive-auth
   service-account-auth
   colab-auth
   troubleshooting

Overview
--------

Authentication is required for all Earth Engine operations. Choose the method that best fits your needs:

.. list-table::
   :widths: 25 25 25 25
   :header-rows: 1

   * - Method
     - Use Case
     - Setup Complexity
     - Security Level
   * - Interactive
     - Local development
     - Simple
     - Medium
   * - Service Account
     - Production/Automation
     - Complex
     - High
   * - Colab
     - Notebooks/Teaching
     - Simple
     - Medium
   * - Command Line
     - Server environments
     - Medium
     - Medium

Authentication Flow
-------------------

All authentication methods follow this general pattern:

1. **Credential Creation**: Generate or obtain authentication credentials
2. **Credential Storage**: Store credentials securely on your system
3. **Initialization**: Use credentials to initialize Earth Engine
4. **Token Refresh**: Automatically refresh expired tokens

Choosing the Right Method
-------------------------

**Interactive Authentication**
  Best for:
  * Local development and testing
  * Learning and experimentation
  * One-time scripts and analysis

**Service Account Authentication**
  Best for:
  * Production applications
  * Automated workflows
  * Server environments
  * Sharing code without sharing credentials

**Google Colab Authentication**
  Best for:
  * Jupyter notebooks
  * Educational content
  * Collaborative analysis
  * Quick prototyping

Security Considerations
-----------------------

**Credential Protection**
  * Never commit credentials to version control
  * Use environment variables for sensitive data
  * Implement proper file permissions
  * Rotate credentials regularly

**Access Control**
  * Use minimum required permissions
  * Monitor API usage patterns
  * Implement access logging
  * Regular security audits

Common Authentication Patterns
------------------------------

**Development Environment**

.. code-block:: python

   import ee
   
   # Interactive authentication for development
   try:
       ee.Initialize(project='your-project-id')
   except Exception as e:
       print("Authentication required")
       ee.Authenticate()
       ee.Initialize(project='your-project-id')

**Production Environment**

.. code-block:: python

   import ee
   import os
   
   # Service account authentication for production
   service_account = os.environ.get('EE_SERVICE_ACCOUNT')
   private_key = os.environ.get('EE_PRIVATE_KEY_PATH')
   
   credentials = ee.ServiceAccountCredentials(service_account, private_key)
   ee.Initialize(credentials, project='your-project-id')

**Notebook Environment**

.. code-block:: python

   import ee
   
   # Colab-specific authentication
   try:
       ee.Initialize(project='your-project-id')
   except:
       ee.Authenticate()
       ee.Initialize(project='your-project-id')

Environment Setup
-----------------

**Required Packages**

.. code-block:: bash

   pip install earthengine-api
   pip install google-auth
   pip install google-auth-oauthlib

**Environment Variables**

Set these for consistent authentication:

.. code-block:: bash

   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
   export EE_PROJECT_ID="your-project-id"
   export EE_SERVICE_ACCOUNT="service-account@your-project.iam.gserviceaccount.com"

Next Steps
----------

Choose your authentication method:

1. :doc:`interactive-auth` - For local development
2. :doc:`service-account-auth` - For production use
3. :doc:`colab-auth` - For notebook environments
4. :doc:`troubleshooting` - If you encounter issues

.. note::
   You can use multiple authentication methods on the same system. Each method stores credentials independently.
