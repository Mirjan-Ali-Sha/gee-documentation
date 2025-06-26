"""
Basic Example 3: Simple Calculations and Spectral Indices
=========================================================

This example demonstrates:
- Basic mathematical operations on images
- Calculating common spectral indices (NDVI, NDWI, EVI)
- Working with image bands and band math
- Understanding Earth Engine data types
- Creating custom calculations and functions

Prerequisites:
- Authenticated Earth Engine environment
- Basic understanding of remote sensing concepts
- Familiarity with spectral indices
"""

import ee
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def demonstrate_basic_math():
    """
    Demonstrate basic mathematical operations on Earth Engine images.
    """
    print("🧮 Basic Mathematical Operations")
    print("-" * 40)
    
    # Load a Landsat 8 image
    image = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
             .filterDate('2023-06-01', '2023-09-01')
             .filterBounds(ee.Geometry.Point([-122.4, 37.8]))  # San Francisco
             .sort('CLOUD_COVER')
             .first())
    
    print(f"Working with image: {image.get('LANDSAT_PRODUCT_ID').getInfo()}")
    
    # Scale factors for Landsat Collection 2
    def apply_scale_factors(image):
        """Apply scale factors to Landsat Collection 2 data."""
        optical_bands = image.select('SR_B.').multiply(0.0000275).add(-0.2)
        thermal_bands = image.select('ST_B.*').multiply(0.00341802).add(149.0)
        return image.addBands(optical_bands, None, True).addBands(thermal_bands, None, True)
    
    # Apply scaling
    image = apply_scale_factors(image)
    
    # Basic arithmetic operations
    print("\n📊 Basic Arithmetic Operations:")
    
    # Addition
    red_plus_nir = image.select('SR_B4').add(image.select('SR_B5'))
    print("✓ Addition: Red + NIR")
    
    # Subtraction  
    nir_minus_red = image.select('SR_B5').subtract(image.select('SR_B4'))
    print("✓ Subtraction: NIR - Red")
    
    # Multiplication
    red_times_nir = image.select('SR_B4').multiply(image.select('SR_B5'))
    print("✓ Multiplication: Red × NIR")
    
    # Division
    nir_div_red = image.select('SR_B5').divide(image.select('SR_B4'))
    print("✓ Division: NIR ÷ Red")
    
    # Constants
    red_plus_constant = image.select('SR_B4').add(0.1)
    red_times_constant = image.select('SR_B4').multiply(2.0)
    print("✓ Operations with constants")
    
    # Power operations
    red_squared = image.select('SR_B4').pow(2)
    red_sqrt = image.select('SR_B4').sqrt()
    print("✓ Power operations: square and square root")
    
    return image

def calculate_spectral_indices(image):
    """
    Calculate common spectral indices for vegetation and water analysis.
    
    Args:
        image: Landsat 8 image (scaled)
    
    Returns:
        ee.Image: Image with spectral indices added as bands
    """
    print("\n🌱 Calculating Spectral Indices")
    print("-" * 40)
    
    # NDVI (Normalized Difference Vegetation Index)
    # NDVI = (NIR - Red) / (NIR + Red)
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
    print("✓ NDVI calculated")
    
    # NDWI (Normalized Difference Water Index)
    # NDWI = (Green - NIR) / (Green + NIR)
    ndwi = image.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI')
    print("✓ NDWI calculated")
    
    # NDBI (Normalized Difference Built-up Index)
    # NDBI = (SWIR1 - NIR) / (SWIR1 + NIR)
    ndbi = image.normalizedDifference(['SR_B6', 'SR_B5']).rename('NDBI')
    print("✓ NDBI calculated")
    
    # EVI (Enhanced Vegetation Index)
    # EVI = 2.5 * ((NIR - Red) / (NIR + 6 * Red - 7.5 * Blue + 1))
    evi = image.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
        {
            'NIR': image.select('SR_B5'),
            'RED': image.select('SR_B4'),
            'BLUE': image.select('SR_B2')
        }
    ).rename('EVI')
    print("✓ EVI calculated")
    
    # SAVI (Soil Adjusted Vegetation Index)
    # SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L), where L = 0.5
    savi = image.expression(
        '((NIR - RED) / (NIR + RED + 0.5)) * (1.5)',
        {
            'NIR': image.select('SR_B5'),
            'RED': image.select('SR_B4')
        }
    ).rename('SAVI')
    print("✓ SAVI calculated")
    
    # MNDWI (Modified Normalized Difference Water Index)
    # MNDWI = (Green - SWIR1) / (Green + SWIR1)
    mndwi = image.normalizedDifference(['SR_B3', 'SR_B6']).rename('MNDWI')
    print("✓ MNDWI calculated")
    
    # NBR (Normalized Burn Ratio)
    # NBR = (NIR - SWIR2) / (NIR + SWIR2)
    nbr = image.normalizedDifference(['SR_B5', 'SR_B7']).rename('NBR')
    print("✓ NBR calculated")
    
    # Add all indices to the image
    indices_image = image.addBands([ndvi, ndwi, ndbi, evi, savi, mndwi, nbr])
    
    return indices_image

def create_custom_calculations(image):
    """
    Demonstrate custom calculations using ee.Image.expression().
    
    Args:
        image: Input Earth Engine image
    
    Returns:
        ee.Image: Image with custom calculated bands
    """
    print("\n🔬 Custom Calculations with ee.Image.expression()")
    print("-" * 50)
    
    # Custom vegetation index combining multiple bands
    custom_vi = image.expression(
        '(NIR * 2.5 - RED * 1.5 - BLUE * 0.8) / (NIR + RED + BLUE)',
        {
            'NIR': image.select('SR_B5'),
            'RED': image.select('SR_B4'),
            'BLUE': image.select('SR_B2')
        }
    ).rename('Custom_VI')
    print("✓ Custom vegetation index")
    
    # Atmospheric visibility index
    # Uses the ratio of blue to red for atmospheric clarity
    visibility_index = image.expression(
        'BLUE / RED',
        {
            'BLUE': image.select('SR_B2'),
            'RED': image.select('SR_B4')
        }
    ).rename('Visibility_Index')
    print("✓ Atmospheric visibility index")
    
    # Soil brightness index
    # Average of visible bands
    soil_brightness = image.expression(
        '(BLUE + GREEN + RED) / 3',
        {
            'BLUE': image.select('SR_B2'),
            'GREEN': image.select('SR_B3'),
            'RED': image.select('SR_B4')
        }
    ).rename('Soil_Brightness')
    print("✓ Soil brightness index")
    
    # Shadow index (using multiple bands)
    shadow_index = image.expression(
        '(BLUE + GREEN) / (NIR + SWIR1)',
        {
            'BLUE': image.select('SR_B2'),
            'GREEN': image.select('SR_B3'),
            'NIR': image.select('SR_B5'),
            'SWIR1': image.select('SR_B6')
        }
    ).rename('Shadow_Index')
    print("✓ Shadow index")
    
    # Add custom calculations
    custom_image = image.addBands([custom_vi, visibility_index, soil_brightness, shadow_index])
    
    return custom_image

def analyze_image_statistics(image, region=None):
    """
    Calculate comprehensive statistics for image bands.
    
    Args:
        image: Earth Engine image
        region: Optional region for analysis (uses image bounds if None)
    
    Returns:
        dict: Dictionary containing statistics
    """
    print("\n📈 Statistical Analysis")
    print("-" * 30)
    
    if region is None:
        region = image.geometry()
    
    # Define bands to analyze
    spectral_bands = ['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']
    index_bands = ['NDVI', 'NDWI', 'NDBI', 'EVI', 'SAVI']
    
    all_bands = spectral_bands + index_bands
    
    # Calculate comprehensive statistics
    stats = image.select(all_bands).reduceRegion(
        reducer=ee.Reducer.minMax().combine(
            reducer2=ee.Reducer.mean(),
            sharedInputs=True
        ).combine(
            reducer2=ee.Reducer.stdDev(),
            sharedInputs=True
        ).combine(
            reducer2=ee.Reducer.percentile([25, 75]),
            sharedInputs=True
        ),
        geometry=region,
        scale=30,
        maxPixels=1e9
    )
    
    stats_dict = stats.getInfo()
    
    # Format and display statistics
    print("Band Statistics Summary:")
    print("-" * 60)
    
    for band in all_bands:
        if f'{band}_mean' in stats_dict:
            print(f"\n{band}:")
            print(f"  Mean: {stats_dict[f'{band}_mean']:.4f}")
            print(f"  StdDev: {stats_dict[f'{band}_stdDev']:.4f}")
            print(f"  Min: {stats_dict[f'{band}_min']:.4f}")
            print(f"  Max: {stats_dict[f'{band}_max']:.4f}")
            
            if f'{band}_p25' in stats_dict:
                print(f"  Q1 (25%): {stats_dict[f'{band}_p25']:.4f}")
                print(f"  Q3 (75%): {stats_dict[f'{band}_p75']:.4f}")
    
    return stats_dict

def demonstrate_conditional_operations(image):
    """
    Demonstrate conditional operations and masking.
    
    Args:
        image: Input Earth Engine image
    
    Returns:
        ee.Image: Image with conditional results
    """
    print("\n🎯 Conditional Operations and Masking")
    print("-" * 40)
    
    # Create vegetation mask (NDVI > 0.3)
    vegetation_mask = image.select('NDVI').gt(0.3)
    print("✓ Vegetation mask created (NDVI > 0.3)")
    
    # Create water mask (NDWI > 0.2)
    water_mask = image.select('NDWI').gt(0.2)
    print("✓ Water mask created (NDWI > 0.2)")
    
    # Create urban mask (NDBI > 0.1)
    urban_mask = image.select('NDBI').gt(0.1)
    print("✓ Urban mask created (NDBI > 0.1)")
    
    # Combined land cover classification using conditions
    land_cover = (ee.Image(0)  # Start with zeros
                  .where(water_mask, 1)      # Water = 1
                  .where(vegetation_mask, 2)  # Vegetation = 2
                  .where(urban_mask, 3))     # Urban = 3
    
    land_cover = land_cover.rename('Land_Cover')
    print("✓ Simple land cover classification")
    
    # Conditional value assignment
    # High vegetation areas get NDVI value, others get 0
    high_vegetation = image.select('NDVI').where(
        image.select('NDVI').lt(0.5), 0
    ).rename('High_Vegetation_Only')
    print("✓ Conditional value assignment")
    
    # Multiple conditions using ee.Image.expression()
    complex_condition = image.expression(
        '(NDVI > 0.4) && (NDWI < 0.1) && (EVI > 0.3) ? 1 : 0',
        {
            'NDVI': image.select('NDVI'),
            'NDWI': image.select('NDWI'),
            'EVI': image.select('EVI')
        }
    ).rename('Healthy_Vegetation')
    print("✓ Complex conditional expression")
    
    # Add conditional results
    conditional_image = image.addBands([
        land_cover, high_vegetation, complex_condition,
        vegetation_mask.rename('Vegetation_Mask'),
        water_mask.rename('Water_Mask'),
        urban_mask.rename('Urban_Mask')
    ])
    
    return conditional_image

def create_visualization_parameters():
    """
    Create visualization parameters for different types of data.
    
    Returns:
        dict: Dictionary of visualization parameters
    """
    vis_params = {
        'true_color': {
            'bands': ['SR_B4', 'SR_B3', 'SR_B2'],
            'min': 0.0,
            'max': 0.3,
            'gamma': 1.2
        },
        'false_color': {
            'bands': ['SR_B5', 'SR_B4', 'SR_B3'],
            'min': 0.0,
            'max': 0.3,
            'gamma': 1.2
        },
        'ndvi': {
            'bands': ['NDVI'],
            'min': -0.2,
            'max': 0.8,
            'palette': ['blue', 'white', 'green']
        },
        'ndwi': {
            'bands': ['NDWI'],
            'min': -0.3,
            'max': 0.5,
            'palette': ['white', 'blue']
        },
        'land_cover': {
            'bands': ['Land_Cover'],
            'min': 0,
            'max': 3,
            'palette': ['gray', 'blue', 'green', 'red']
        }
    }
    
    return vis_params

def main():
    """
    Main function demonstrating simple calculations and spectral indices.
    """
    # Initialize Earth Engine
    try:
        ee.Initialize(project='your-project-id')
        print("✓ Earth Engine initialized successfully!")
    except Exception as e:
        print(f"✗ Error initializing Earth Engine: {e}")
        return
    
    print("\n" + "="*70)
    print("🧮 EARTH ENGINE SIMPLE CALCULATIONS AND SPECTRAL INDICES")
    print("="*70)
    
    # Step 1: Basic mathematical operations
    image = demonstrate_basic_math()
    
    # Step 2: Calculate spectral indices
    indices_image = calculate_spectral_indices(image)
    
    # Step 3: Custom calculations
    custom_image = create_custom_calculations(indices_image)
    
    # Step 4: Statistical analysis
    san_francisco_region = ee.Geometry.Rectangle([-122.5, 37.7, -122.3, 37.9])
    stats = analyze_image_statistics(custom_image, san_francisco_region)
    
    # Step 5: Conditional operations
    final_image = demonstrate_conditional_operations(custom_image)
    
    # Step 6: Visualization setup
    print("\n🎨 Visualization Parameters")
    print("-" * 30)
    vis_params = create_visualization_parameters()
    
    for vis_name, params in vis_params.items():
        print(f"✓ {vis_name}: {params['bands']}")
    
    # Step 7: Export example
    print("\n📤 Export Configuration Example")
    print("-" * 35)
    
    # Select key bands for export
    export_image = final_image.select([
        'SR_B4', 'SR_B3', 'SR_B2',  # RGB bands
        'NDVI', 'NDWI', 'EVI',      # Vegetation indices
        'Land_Cover'                 # Classification
    ])
    
    export_config = {
        'image': export_image,
        'description': 'landsat_analysis_with_indices',
        'folder': 'EarthEngine_Exports',
        'region': san_francisco_region,
        'scale': 30,
        'crs': 'EPSG:4326',
        'maxPixels': 1e13
    }
    
    print("Export parameters configured:")
    for key, value in export_config.items():
        if key != 'image':
            print(f"  {key}: {value}")
    
    # Step 8: Summary of calculations performed
    print("\n📋 Summary of Calculations Performed")
    print("-" * 40)
    
    all_bands = final_image.bandNames().getInfo()
    
    spectral_bands = [b for b in all_bands if b.startswith('SR_B')]
    index_bands = [b for b in all_bands if b in ['NDVI', 'NDWI', 'NDBI', 'EVI', 'SAVI', 'MNDWI', 'NBR']]
    custom_bands = [b for b in all_bands if 'Custom' in b or 'Visibility' in b or 'Soil' in b or 'Shadow' in b]
    mask_bands = [b for b in all_bands if 'Mask' in b or 'Cover' in b or 'Vegetation' in b]
    
    print(f"Original spectral bands ({len(spectral_bands)}): {spectral_bands}")
    print(f"Standard indices ({len(index_bands)}): {index_bands}")
    print(f"Custom calculations ({len(custom_bands)}): {custom_bands}")
    print(f"Masks and classifications ({len(mask_bands)}): {mask_bands}")
    print(f"Total bands: {len(all_bands)}")
    
    print("\n✅ Simple Calculations Example Completed!")
    print("\n🎓 Key Concepts Demonstrated:")
    print("• Basic arithmetic operations on images")
    print("• Standard spectral index calculations")
    print("• Custom expressions and formulas")
    print("• Statistical analysis and summaries")
    print("• Conditional operations and masking")
    print("• Land cover classification basics")
    print("• Visualization parameter setup")
    
    print("\n📚 Next Steps:")
    print("• Experiment with different spectral indices")
    print("• Try custom mathematical expressions")
    print("• Apply calculations to different sensors")
    print("• Explore time series calculations")
    print("• Learn about image collection processing")

if __name__ == "__main__":
    main()
