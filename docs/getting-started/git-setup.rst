Git Setup with Earth Engine
============================

Configure Git access for Earth Engine repositories hosted on earthengine.googlesource.com.

Understanding Earth Engine Git Integration
------------------------------------------

Google Earth Engine provides Git repositories for:

* **Code Sharing**: Collaborate on Earth Engine scripts
* **Version Control**: Track changes in your analyses
* **Asset Management**: Manage Earth Engine assets with Git
* **Team Collaboration**: Share code across research teams

Git repositories are hosted on `earthengine.googlesource.com` and require OAuth authentication.

Prerequisites
-------------

Before setting up Git access:

* **Git Installed**: Git 2.0 or later
* **Earth Engine Account**: Approved and verified account
* **Google Cloud Project**: Properly configured project
* **Command Line Access**: Terminal or command prompt

Setting Up Git Authentication
-----------------------------

**Step 1: Generate Git Password**

1. Visit `https://earthengine.googlesource.com/new-password <https://earthengine.googlesource.com/new-password>`_
2. Sign in with your Google Account
3. Click "Generate Password"
4. Complete OAuth authorization flow
5. Copy the generated Git configuration commands

**Step 2: Configure Git Credentials**

The generated commands will look like:

.. code-block:: bash

   git config --global credential.https://source.developers.google.com.helper store
   git config --global credential.https://earthengine.googlesource.com.helper store

Run these commands in your terminal.

**Step 3: Store Authentication Token**

.. code-block:: bash

   # The system will prompt for credentials when first accessing repositories
   git clone https://earthengine.googlesource.com/users/YOUR-USERNAME/default

Alternative Authentication Methods
----------------------------------

**Method 1: Manual Token Entry**

.. code-block:: bash

   # Clone repository (will prompt for credentials)
   git clone https://earthengine.googlesource.com/users/YOUR-USERNAME/default
   
   # Enter your username and generated password when prompted
   Username: your.email@gmail.com
   Password: [paste generated password]

**Method 2: Credential Helper Configuration**

.. code-block:: bash

   # Configure Git to use credential helper
   git config --global credential.helper 'store --file ~/.git-credentials'
   
   # Add credentials manually to ~/.git-credentials
   echo "https://username:password@earthengine.googlesource.com" >> ~/.git-credentials

**Method 3: Environment Variables**

.. code-block:: bash

   # Set environment variables (for scripts)
   export GIT_USERNAME="your.email@gmail.com"
   export GIT_PASSWORD="your-generated-password"
   
   # Use in clone commands
   git clone "https://${GIT_USERNAME}:${GIT_PASSWORD}@earthengine.googlesource.com/users/YOUR-USERNAME/default"

Working with Earth Engine Repositories
---------------------------------------

**Creating a New Repository**

1. Visit `Earth Engine Code Editor <https://code.earthengine.google.com>`_
2. Create a new script or project
3. Save to create repository structure
4. Access via Git:

.. code-block:: bash

   git clone https://earthengine.googlesource.com/users/YOUR-USERNAME/default

**Repository Structure**

Earth Engine Git repositories typically contain:

.. code-block:: text

   repository/
   ├── scripts/
   │   ├── analysis1.js
   │   ├── analysis2.js
   │   └── utils/
   │       └── helper_functions.js
   ├── assets/
   │   ├── images/
   │   ├── tables/
   │   └── image_collections/
   └── README.md

**Basic Git Workflow**

.. code-block:: bash

   # Clone repository
   git clone https://earthengine.googlesource.com/users/YOUR-USERNAME/default
   cd default
   
   # Create new branch for feature
   git checkout -b new-analysis
   
   # Add your changes
   git add scripts/new_analysis.js
   git commit -m "Add vegetation analysis script"
   
   # Push changes
   git push origin new-analysis

**Syncing with Code Editor**

Changes made in the Code Editor automatically sync with Git:

.. code-block:: bash

   # Pull latest changes from Code Editor
   git pull origin master
   
   # View changes
   git log --oneline
   
   # Push local changes to Code Editor
   git push origin master

Managing Earth Engine Assets with Git
--------------------------------------

**Asset Version Control**

.. code-block:: bash

   # Track asset metadata
   git add assets/metadata/
   
   # Commit asset changes
   git commit -m "Update training data polygons"
   
   # Tag important asset versions
   git tag -a v1.0-dataset -m "Initial training dataset release"

**Asset Documentation**

Create documentation for your assets:

.. code-block:: markdown

   # assets/README.md
   
   ## Earth Engine Assets
   
   ### Training Data
   - `training_polygons_v1`: Initial hand-digitized training areas
   - `training_polygons_v2`: Expanded training dataset
   
   ### Processed Images
   - `landsat_composite_2023`: Annual Landsat composite
   - `ndvi_time_series`: Monthly NDVI calculations

Collaboration Workflows
-----------------------

**Team Repository Setup**

.. code-block:: bash

   # Clone shared repository
   git clone https://earthengine.googlesource.com/users/TEAM-LEAD/shared-project
   
   # Create feature branch
   git checkout -b feature/land-cover-analysis
   
   # Work on your changes
   # ... make changes ...
   
   # Push feature branch
   git push origin feature/land-cover-analysis

**Code Review Process**

1. Create feature branches for new work
2. Push branches to shared repository
3. Use Code Editor for review and testing
4. Merge approved changes to main branch

**Handling Merge Conflicts**

.. code-block:: bash

   # Pull latest changes
   git pull origin master
   
   # If conflicts occur, resolve manually
   git status  # Shows conflicted files
   
   # Edit files to resolve conflicts
   # Remove conflict markers (<<<<<<< ======= >>>>>>>)
   
   # Add resolved files
   git add resolved_file.js
   
   # Complete merge
   git commit -m "Resolve merge conflict in analysis script"

Advanced Git Configuration
--------------------------

**Custom Git Aliases**

.. code-block:: bash

   # Add useful aliases
   git config --global alias.ee-status "status --short"
   git config --global alias.ee-log "log --oneline --graph"
   git config --global alias.ee-push "push origin HEAD"

**Branch Protection**

.. code-block:: bash

   # Create development branch
   git checkout -b development
   git push origin development
   
   # Set up branch protection (main branch)
   # Use Code Editor settings for repository configuration

**Large File Handling**

For large datasets (though Earth Engine assets are preferred):

.. code-block:: bash

   # Install Git LFS
   git lfs install
   
   # Track large files
   git lfs track "*.tif"
   git lfs track "*.nc"
   
   # Add .gitattributes
   git add .gitattributes
   git commit -m "Configure Git LFS for large files"

Troubleshooting Git Issues
--------------------------

**Authentication Failures**

.. code-block:: bash

   # Clear stored credentials
   git config --global --unset credential.helper
   
   # Regenerate password at earthengine.googlesource.com/new-password
   # Reconfigure credential helper
   git config --global credential.helper store

**Clone Failures**

.. code-block:: bash

   # Check repository URL
   git remote -v
   
   # Update remote URL if needed
   git remote set-url origin https://earthengine.googlesource.com/users/YOUR-USERNAME/default

**Sync Issues with Code Editor**

.. code-block:: bash

   # Force sync with Code Editor
   git fetch origin
   git reset --hard origin/master
   
   # Warning: This will overwrite local changes

**Large Repository Issues**

.. code-block:: bash

   # Shallow clone for large repositories
   git clone --depth 1 https://earthengine.googlesource.com/users/YOUR-USERNAME/default
   
   # Later get full history if needed
   git fetch --unshallow

Best Practices
--------------

**Repository Organization**

* Use clear directory structure
* Document scripts and assets
* Tag important versions
* Regular commits with descriptive messages

**Collaboration Guidelines**

* Create feature branches for new work
* Use pull requests for code review
* Keep commits focused and atomic
* Write clear commit messages

**Security Considerations**

* Never commit credentials or API keys
* Use .gitignore for sensitive files
* Regular credential rotation
* Monitor repository access

Integration with Development Workflow
-------------------------------------

**Connecting Local Development**

.. code-block:: python

   # sync_ee_repo.py - Script to sync with Earth Engine repository
   
   import subprocess
   import os
   
   def sync_with_ee_repo():
       """Sync local development with Earth Engine Git repository."""
       try:
           # Pull latest changes
           subprocess.run(['git', 'pull', 'origin', 'master'], check=True)
           print("✓ Synced with Earth Engine repository")
           
           # Copy local scripts to repository
           # ... your sync logic ...
           
       except subprocess.CalledProcessError as e:
           print(f"✗ Sync failed: {e}")

**Automated Workflows**

.. code-block:: bash

   #!/bin/bash
   # ee_git_workflow.sh - Automated Earth Engine Git workflow
   
   # Pull latest changes
   git pull origin master
   
   # Run tests
   python test_ee_scripts.py
   
   # If tests pass, push changes
   if [ $? -eq 0 ]; then
       git push origin master
       echo "✓ Changes pushed successfully"
   else
       echo "✗ Tests failed, not pushing"
   fi

Next Steps
----------

After setting up Git access:

1. :doc:`../authentication/index` - Complete authentication setup
2. :doc:`../examples/basic/index` - Start with basic examples
3. Create your first Earth Engine repository
4. Explore collaborative workflows

.. note::
   Git credentials for Earth Engine are separate from other Google services. You'll need to generate specific passwords for earthengine.googlesource.com.

.. tip::
   Use the Code Editor for initial development and Git for version control and collaboration. Both systems sync automatically.

.. warning::
   Generated Git passwords should be treated as sensitive credentials. Store them securely and rotate regularly.
