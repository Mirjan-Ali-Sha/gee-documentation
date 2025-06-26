"""
Basic Example 1: Hello World with Google Earth Engine
=====================================================

This example demonstrates the most basic Earth Engine operations:
- Authentication and initialization
- Accessing a simple image
- Printing basic information

Prerequisites:
- Google Earth Engine account
- Authenticated Python environment
"""

import ee

def main():
    """
    Basic Earth Engine Hello World example.
    """
    # Initialize Earth Engine
    # Replace 'your-project-id' with your actual project ID
    try:
        ee.Initialize(project='your-project-id')
        print("✓ Earth Engine initialized successfully!")
    except Exception as e:
        print(f"✗ Error initializing Earth Engine: {e}")
        return

    # Get a simple image from the catalog
    image = ee.Image('USGS/SRTMGL1_003')
    
    # Print basic image information
    print(f"Image ID: {image.getInfo()['id']}")
    print(f"Image type: {image.getInfo()['type']}")
    
    # Get image properties
    properties = image.propertyNames()
    print(f"Image properties: {properties.getInfo()}")
    
    # Get projection information
    projection = image.projection()
    print(f"Projection: {projection.getInfo()}")
    
    # Get image scale (resolution)
    scale = image.projection().nominalScale()
    print(f"Scale (meters): {scale.getInfo()}")
    
    print("\n🎉 Hello World example completed successfully!")

if __name__ == "__main__":
    main()
