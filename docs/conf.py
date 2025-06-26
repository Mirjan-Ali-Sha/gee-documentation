import os
import sys
sys.path.insert(0, os.path.abspath('../'))

# Project information
project = 'Google Earth Engine Documentation'
copyright = '2025, Your Name'
author = 'Your Name'
release = '1.0.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
    'myst_parser',
]

# Templates path
templates_path = ['_templates']

# Exclude patterns
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# HTML theme
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']

# Theme options
html_theme_options = {
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Copy button configuration
copybutton_prompt_text = "$ "
copybutton_only_copy_prompt_lines = False

# Intersphinx mapping
# Intersphinx mapping - remove the broken Earth Engine URL
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    # Remove this line: 'ee': ('https://developers.google.com/earth-engine/apidocs', None),
}


# MyST configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]
