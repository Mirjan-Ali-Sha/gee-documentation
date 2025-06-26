"""
Basic Example 2: Image Display and Visualization
================================================

This example demonstrates:
- Loading different types of Earth Engine images
- Basic visualization parameters
- Adding images to the map
- Working with different band combinations
- Understanding image properties and metadata

Prerequisites:
- Authenticated Earth Engine environment
- Understanding of remote sensing basics
"""

import ee
import folium
import numpy as np

def display_single_band_image():
    """
    Display a single-band image with custom visualization.
    """
    print("🖼️  Loading and displaying single-band image...")
    
    # Load elevation data (single band)
    elevation = ee.Image('USGS/SRTMGL1_003')
    
    # Print basic information
    print(f"Image ID: {elevation.get('system:id').getInfo()}")
    print(f"Band names: {elevation.bandNames().getInfo()}")
    
    # Define visualization parameters
    vis_params = {
        'min': 0,
        'max': 4000,
        'palette': ['blue', 'green', 'yellow', 'orange', 'red']
    }
    
    # Get image properties
    properties = elevation.propertyNames()
    print(f"Available properties: {properties.getInfo()}")
    
    # Get projection info
    projection = elevation.projection()
    print(f"Projection: {projection.getInfo()}")
    
    return elevation, vis_params

def display_multi_band_image():
    """
    Display multi-band satellite imagery with different band combinations.
    """
    print("🛰️  Loading and displaying multi-band satellite image...")
    
    # Load Landsat 8 image
    landsat = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
               .filterDate('2023-06-01', '2023-09-01')
               .filterBounds(ee.Geometry.Point([-122.4, 37.8]))  # San Francisco
               .sort('CLOUD_COVER')
               .first())
    
    print(f"Scene ID: {landsat.get('LANDSAT_PRODUCT_ID').getInfo()}")
    print(f"Cloud cover: {landsat.get('CLOUD_COVER').getInfo()}%")
    print(f"Date: {landsat.get('DATE_ACQUIRED').getInfo()}")
    
    # Define different visualization combinations
    visualizations = {
        'true_color': {
            'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
            'min': 0.0,
            'max': 0.3,
            'description': 'True Color (Red, Green, Blue)'
        },
        'false_color': {
            'bands': ['SR_B5', 'SR_B4', 'SR_B3'],
            'min': 0.0,
            'max': 0.3,
            'description': 'False Color Infrared (NIR, Red, Green)'
        },
        'agriculture': {
            'bands': ['SR_B6', 'SR_B5', 'SR_B2'],
            'min': 0.0,
            'max': 0.3,
            'description': 'Agriculture (SWIR1, NIR, Blue)'
        },
        'urban': {
            'bands': ['SR_B7', 'SR_B6', 'SR_B4'],
            'min': 0.0,
            'max': 0.3,
            'description': 'Urban (SWIR2, SWIR1, Red)'
        }
    }
    
    return landsat, visualizations

def create_folium_map(image, vis_params, center_coords, zoom_level=10):
    """
    Create an interactive map using Folium to display Earth Engine images.
    
    Args:
        image: Earth Engine image
        vis_params: Visualization parameters
        center_coords: [latitude, longitude] for map center
        zoom_level: Initial zoom level
    
    Returns:
        folium.Map: Interactive map object
    """
    print("🗺️  Creating interactive map...")
    
    # Create base map
    m = folium.Map(
        location=center_coords,
        zoom_start=zoom_level,
        control_scale=True
    )
    
    # Get the tile URL for the Earth Engine image
    map_id_dict = ee.Image(image).getMapId(vis_params)
    
    # Add Earth Engine layer to map
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Google Earth Engine',
        name='EE Image',
        overlay=True,
        control=True
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m

def analyze_image_statistics(image, geometry=None):
    """
    Calculate and display basic statistics for an image.
    
    Args:
        image: Earth Engine image
        geometry: Optional geometry for regional statistics
    
    Returns:
        dict: Dictionary containing statistics
    """
    print("📊 Calculating image statistics...")
    
    if geometry is None:
        # Use image footprint if no geometry provided
        geometry = image.geometry()
    
    # Calculate statistics
    stats = image.reduceRegion(
        reducer=ee.Reducer.minMax().combine(
            reducer2=ee.Reducer.mean(),
            sharedInputs=True
        ).combine(
            reducer2=ee.Reducer.stdDev(),
            sharedInputs=True
        ),
        geometry=geometry,
        scale=30,
        maxPixels=1e9
    )
    
    stats_dict = stats.getInfo()
    
    # Print formatted statistics
    print("\n📈 Image Statistics:")
    for key, value in stats_dict.items():
        if value is not None:
            print(f"  {key}: {value:.4f}")
    
    return stats_dict

def create_histogram_data(image, band_name, geometry=None, scale=30):
    """
    Create histogram data for a specific band.
    
    Args:
        image: Earth Engine image
        band_name: Name of the band to analyze
        geometry: Optional geometry for regional analysis
        scale: Scale for analysis
    
    Returns:
        dict: Histogram data
    """
    print(f"📊 Creating histogram for band: {band_name}")
    
    if geometry is None:
        geometry = image.geometry()
    
    # Calculate histogram
    histogram = image.select(band_name).reduceRegion(
        reducer=ee.Reducer.histogram(maxBuckets=256),
        geometry=geometry,
        scale=scale,
        maxPixels=1e9
    )
    
    hist_data = histogram.getInfo()
    return hist_data

def apply_cloud_masking(image):
    """
    Apply cloud masking to Landsat 8 image.
    
    Args:
        image: Landsat 8 image
    
    Returns:
        ee.Image: Cloud-masked image
    """
    print("☁️ Applying cloud masking...")
    
    # Get QA band
    qa = image.select('QA_PIXEL')
    
    # Create cloud mask
    cloud_mask = qa.bitwiseAnd(1 << 3).eq(0).And(  # Cloud shadow
                 qa.bitwiseAnd(1 << 4).eq(0))       # Cloud
    
    # Apply mask and scale
    masked_image = image.updateMask(cloud_mask).multiply(0.0000275).add(-0.2)
    
    return masked_image

def main():
    """
    Main function demonstrating image display techniques.
    """
    # Initialize Earth Engine
    try:
        ee.Initialize(project='your-project-id')
        print("✓ Earth Engine initialized successfully!")
    except Exception as e:
        print(f"✗ Error initializing Earth Engine: {e}")
        return
    
    print("\n" + "="*60)
    print("🎯 EARTH ENGINE IMAGE DISPLAY EXAMPLES")
    print("="*60)
    
    # Example 1: Single-band elevation image
    print("\n1️⃣ Single-Band Image Display")
    elevation, elev_vis = display_single_band_image()
    
    # Calculate statistics for elevation
    elev_stats = analyze_image_statistics(
        elevation,
        ee.Geometry.Rectangle([-122.5, 37.5, -122.0, 38.0])  # San Francisco Bay Area
    )
    
    # Example 2: Multi-band satellite imagery
    print("\n2️⃣ Multi-Band Satellite Image Display")
    landsat, visualizations = display_multi_band_image()
    
    # Apply cloud masking
    landsat_masked = apply_cloud_masking(landsat)
    
    # Example 3: Different visualization combinations
    print("\n3️⃣ Visualization Combinations")
    for vis_name, vis_params in visualizations.items():
        print(f"  📷 {vis_params['description']}")
        print(f"     Bands: {vis_params['bands']}")
        print(f"     Min/Max: {vis_params['min']} - {vis_params['max']}")
    
    # Example 4: Image properties and metadata
    print("\n4️⃣ Image Properties and Metadata")
    
    # Get all properties
    all_properties = landsat.propertyNames().getInfo()
    print(f"Total properties: {len(all_properties)}")
    
    # Display key properties
    key_properties = [
        'LANDSAT_PRODUCT_ID', 'DATE_ACQUIRED', 'CLOUD_COVER',
        'SUN_ELEVATION', 'SUN_AZIMUTH', 'EARTH_SUN_DISTANCE'
    ]
    
    print("\n🔍 Key Image Properties:")
    for prop in key_properties:
        try:
            value = landsat.get(prop).getInfo()
            print(f"  {prop}: {value}")
        except:
            print(f"  {prop}: Not available")
    
    # Example 5: Band information
    print("\n5️⃣ Band Information")
    band_names = landsat_masked.bandNames().getInfo()
    print(f"Available bands: {band_names}")
    
    # Get band-specific information
    for band in ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5']:
        try:
            band_info = landsat_masked.select(band).getInfo()
            print(f"  {band}: {band_info['bands'][0]['id']}")
        except:
            print(f"  {band}: Information not available")
    
    # Example 6: Create interactive map
    print("\n6️⃣ Interactive Map Creation")
    
    # Create map with true color visualization
    true_color_vis = visualizations['true_color']
    center_coords = [37.8, -122.4]  # San Francisco coordinates
    
    # Note: In a real application, you would save and display this map
    print("  🗺️ Map would be created with:")
    print(f"     Center: {center_coords}")
    print(f"     Bands: {true_color_vis['bands']}")
    print(f"     Visualization: {true_color_vis['description']}")
    
    # Example 7: Export visualization
    print("\n7️⃣ Image Export Setup")
    
    # Define export parameters
    export_params = {
        'image': landsat_masked.select(['SR_B4', 'SR_B3', 'SR_B2']),
        'description': 'landsat_true_color_export',
        'folder': 'EarthEngine_Exports',
        'region': ee.Geometry.Rectangle([-122.5, 37.5, -122.0, 38.0]),
        'scale': 30,
        'crs': 'EPSG:4326',
        'maxPixels': 1e13
    }
    
    print("  📤 Export configuration:")
    for key, value in export_params.items():
        if key != 'image':
            print(f"     {key}: {value}")
    
    print("\n✅ Image Display Examples Completed!")
    print("\n🎓 Key Concepts Learned:")
    print("• Loading single and multi-band images")
    print("• Understanding visualization parameters")
    print("• Working with different band combinations")
    print("• Analyzing image properties and metadata")
    print("• Applying cloud masking techniques")
    print("• Creating interactive visualizations")
    print("\n📚 Next Steps:")
    print("• Try different visualization parameters")
    print("• Experiment with other satellite datasets")
    print("• Learn about spectral indices (NDVI, NDWI)")
    print("• Explore time series visualization")

if __name__ == "__main__":
    main()
