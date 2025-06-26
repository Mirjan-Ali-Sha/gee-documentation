Account Verification
====================

After submitting your Earth Engine application, follow these steps to verify your access and complete the setup process.

Checking Application Status
---------------------------

**Email Notifications**
  Monitor your email for messages from the Earth Engine team:
  
  * Application received confirmation
  * Approval notification
  * Additional information requests

**Approval Timeline**
  * Non-commercial applications: 1-3 business days
  * Commercial applications: 3-7 business days
  * Peak periods may extend review times

First Login Process
-------------------

Once approved, verify your access:

1. **Visit the Code Editor**
   
   Navigate to `https://code.earthengine.google.com <https://code.earthengine.google.com>`_

2. **Accept Terms of Service**
   
   Read and accept the Earth Engine Terms of Service

3. **Complete Registration**
   
   Provide any additional required information

4. **Test Basic Access**
   
   Run a simple script to confirm functionality:

   .. code-block:: javascript

      // Basic test script
      var image = ee.Image('USGS/SRTMGL1_003');
      print('Image info:', image.getInfo());
      Map.addLayer(image, {min: 0, max: 3000}, 'Elevation');

Verification Checklist
----------------------

Confirm the following items work correctly:

**Code Editor Access**
  * Can login without errors
  * Code editor interface loads
  * Can run simple scripts

**API Access**
  * Earth Engine API is enabled in your project
  * Can access from Python environment
  * Authentication works properly

**Asset Access**
  * Can view public datasets
  * Can access your private assets folder
  * Can upload and manage assets

Common Verification Issues
--------------------------

**Application Rejected**
  
  Reasons for rejection:
  
  * Incomplete application information
  * Commercial use under non-commercial application
  * Unclear or insufficient use case description
  
  Solutions:
  
  * Review rejection email carefully
  * Reapply with complete information
  * Ensure use case aligns with application type

**Login Problems**
  
  * Clear browser cache and cookies
  * Try incognito/private browsing mode
  * Ensure JavaScript is enabled
  * Check for browser extensions conflicts

**API Access Issues**
  
  * Verify Google Cloud project is properly configured
  * Check that Earth Engine API is enabled
  * Confirm billing is set up (if required)

Next Steps
----------

After successful verification:

1. :doc:`cloud-project-setup` - Configure Google Cloud integration
2. :doc:`git-setup` - Set up version control access
3. :doc:`../authentication/index` - Choose authentication method
4. :doc:`../examples/basic/index` - Start with basic examples

Troubleshooting
---------------

If you encounter issues during verification:

* :doc:`../authentication/troubleshooting` - Common problems and solutions
* Contact Earth Engine support through the official channels
* Check the community forum for similar issues

.. note::
   Keep your approval email safe - it contains important project information and registration details.

.. warning::
   Some features may require billing to be enabled on your Google Cloud project, even for non-commercial use.
