Google Cloud Project Setup
===========================

Google Earth Engine now requires all usage to be associated with a Google Cloud project. This guide walks you through the complete setup process.

Why Google Cloud Projects?
---------------------------

As of November 2024, Earth Engine requires Google Cloud projects to:

* Enable better resource management and monitoring
* Provide clearer billing and usage tracking
* Integrate with other Google Cloud services
* Support advanced authentication methods

Creating a Google Cloud Project
--------------------------------

**Step 1: Access Google Cloud Console**

1. Visit `Google Cloud Console <https://console.cloud.google.com>`_
2. Sign in with your Google Account
3. Accept terms of service if prompted

**Step 2: Create New Project**

1. Click the project selector dropdown
2. Select "New Project"
3. Provide project details:
   
   * **Project Name**: Descriptive name (e.g., "Earth Engine Analysis")
   * **Project ID**: Unique identifier (auto-generated or custom)
   * **Organization**: Select if applicable
   * **Location**: Choose billing account location

4. Click "Create"

**Step 3: Project ID Requirements**

Project IDs must meet these criteria:

* 6-30 characters long
* Lowercase letters, numbers, and hyphens only
* Start with a letter
* End with a letter or number
* Globally unique across Google Cloud

Project Configuration
---------------------

**Enable Earth Engine API**

1. Navigate to "APIs & Services" > "Library"
2. Search for "Earth Engine API"
3. Click on "Google Earth Engine API"
4. Click "Enable"
5. Wait for activation (usually 1-2 minutes)

**Set Up Billing (If Required)**

Some Earth Engine usage requires billing:

1. Go to "Billing" in the Cloud Console
2. Link a billing account or create new one
3. Verify payment method
4. Set up budget alerts (recommended)

**Configure IAM and Permissions**

1. Navigate to "IAM & Admin" > "IAM"
2. Ensure your account has necessary roles:
   
   * **Earth Engine Resource Viewer**: Basic access
   * **Earth Engine Resource Writer**: Asset management
   * **Project Editor**: Full project access

Registering Project with Earth Engine
-------------------------------------

**Method 1: Through Code Editor**

1. Visit `https://code.earthengine.google.com/register?project=YOUR-PROJECT-ID`
2. Replace `YOUR-PROJECT-ID` with your actual project ID
3. Complete the registration flow
4. Specify usage type (commercial or non-commercial)

**Method 2: Through Python API**

.. code-block:: python

   import ee
   
   # Initialize with your project
   ee.Initialize(project='your-project-id')

**Method 3: Command Line**

.. code-block:: bash

   earthengine set_project your-project-id

Project Settings and Quotas
----------------------------

**Understanding Quotas**

Different quota limits apply based on registration type:

.. list-table::
   :widths: 30 35 35
   :header-rows: 1

   * - Resource
     - Non-Commercial
     - Commercial
   * - Compute seconds/day
     - 10,000
     - Based on billing
   * - Storage (GB)
     - 250
     - Based on billing
   * - Concurrent operations
     - 100
     - Based on billing
   * - Export size (GB/day)
     - 10
     - Based on billing

**Monitoring Usage**

Track your usage through:

1. **Cloud Console**: Monitoring and billing sections
2. **Earth Engine Code Editor**: Resource usage panel
3. **API calls**: Built-in usage reporting

Managing Multiple Projects
--------------------------

**Project Switching**

Switch between projects in your code:

.. code-block:: python

   import ee
   
   # Initialize with specific project
   ee.Initialize(project='project-1')
   
   # Later switch to different project
   ee.Initialize(project='project-2')

**Organizing Projects**

Best practices for multiple projects:

* **Development**: `my-org-ee-dev`
* **Testing**: `my-org-ee-test`
* **Production**: `my-org-ee-prod`
* **Research**: `my-org-ee-research`

Security and Access Control
----------------------------

**Service Accounts**

For production applications:

1. Create service accounts for automated access
2. Assign minimal required permissions
3. Use JSON key files securely
4. Rotate keys regularly

**Access Management**

Control who can access your project:

1. Navigate to "IAM & Admin" > "IAM"
2. Add members with appropriate roles
3. Use groups for team management
4. Regular audit access permissions

Troubleshooting Common Issues
-----------------------------

**API Not Enabled Error**

.. code-block:: text

   Error: Earth Engine API has not been used in project...

Solution: Ensure Earth Engine API is enabled in your project

**Permission Denied Errors**

.. code-block:: text

   Error: User does not have permission to access project...

Solutions:
* Verify you're using the correct project ID
* Check IAM permissions
* Ensure project is registered with Earth Engine

**Billing Account Issues**

.. code-block:: text

   Error: Project requires billing to be enabled...

Solutions:
* Link a valid billing account
* Verify payment method is current
* Check billing account permissions

Best Practices
--------------

**Project Organization**

* Use descriptive project names
* Implement consistent naming conventions
* Document project purposes and owners
* Set up proper IAM hierarchies

**Cost Management**

* Monitor usage regularly
* Set up budget alerts
* Use resource quotas appropriately
* Clean up unused resources

**Security**

* Enable audit logging
* Use service accounts for automation
* Implement least-privilege access
* Regular security reviews

Next Steps
----------

After completing project setup:

1. :doc:`git-setup` - Configure Git access
2. :doc:`../authentication/index` - Set up authentication
3. :doc:`../examples/basic/index` - Try basic examples

.. note::
   Project setup is a one-time process per project. Keep your project ID handy for future authentication.

.. warning::
   Billing charges may apply for certain Earth Engine operations, even under non-commercial usage. Monitor your usage carefully.
