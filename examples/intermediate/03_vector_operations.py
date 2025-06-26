"""
Intermediate Example 3: Vector Operations
=========================================

This example demonstrates:
- Working with Earth Engine vector data (FeatureCollections)
- Geometric operations and spatial analysis
- Zonal statistics and aggregation
- Vector-raster interactions
- Feature filtering and manipulation
- Creating custom geometries

Prerequisites:
- Understanding of vector data concepts
- Basic knowledge of spatial analysis
- Familiarity with Earth Engine data structures
"""

import ee
import json
import pandas as pd

class VectorOperations:
    """Class for Earth Engine vector operations and spatial analysis."""
    
    def __init__(self, project_id):
        """Initialize with Earth Engine project."""
        self.project_id = project_id
        self.initialize_ee()
    
    def initialize_ee(self):
        """Initialize Earth Engine."""
        try:
            ee.Initialize(project=self.project_id)
            print("✓ Earth Engine initialized successfully!")
        except Exception as e:
            print(f"✗ Error initializing Earth Engine: {e}")
            raise
    
    def load_vector_datasets(self):
        """Load various vector datasets from Earth Engine catalog."""
        print("🗺️  Loading Vector Datasets")
        print("-" * 35)
        
        # Administrative boundaries
        countries = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')
        us_states = ee.FeatureCollection('TIGER/2018/States')
        us_counties = ee.FeatureCollection('TIGER/2018/Counties')
        
        print(f"✓ Countries loaded: {countries.size().getInfo()} features")
        print(f"✓ US States loaded: {us_states.size().getInfo()} features")
        print(f"✓ US Counties loaded: {us_counties.size().getInfo()} features")
        
        # Protected areas
        protected_areas = ee.FeatureCollection('WCMC/WDPA/current/polygons')
        print(f"✓ Protected areas loaded: {protected_areas.size().getInfo()} features")
        
        # Ecoregions
        ecoregions = ee.FeatureCollection('RESOLVE/ECOREGIONS/2017')
        print(f"✓ Ecoregions loaded: {ecoregions.size().getInfo()} features")
        
        return {
            'countries': countries,
            'states': us_states,
            'counties': us_counties,
            'protected_areas': protected_areas,
            'ecoregions': ecoregions
        }
    
    def basic_feature_operations(self, datasets):
        """Demonstrate basic feature operations."""
        print("\n🔧 Basic Feature Operations")
        print("-" * 35)
        
        # Filter features by attribute
        print("1. Attribute Filtering:")
        california = datasets['states'].filter(ee.Filter.eq('NAME', 'California'))
        print(f"   California feature: {california.size().getInfo()} feature(s)")
        
        # Filter by multiple attributes
        western_states = datasets['states'].filter(
            ee.Filter.inList('NAME', ['California', 'Oregon', 'Washington'])
        )
        print(f"   Western states: {western_states.size().getInfo()} features")
        
        # Filter by numeric property
        large_counties = datasets['counties'].filter(
            ee.Filter.gt('ALAND', 1e10)  # > 10,000 km²
        )
        print(f"   Large counties: {large_counties.size().getInfo()} features")
        
        # Spatial filtering
        print("\n2. Spatial Filtering:")
        
        # Features intersecting California
        ca_counties = datasets['counties'].filterBounds(california)
        print(f"   Counties in California: {ca_counties.size().getInfo()} features")
        
        # Point in polygon
        point = ee.Geometry.Point([-122.4, 37.8])  # San Francisco
        point_county = datasets['counties'].filterBounds(point)
        county_name = point_county.first().get('NAME').getInfo()
        print(f"   County containing SF: {county_name}")
        
        return {
            'california': california,
            'western_states': western_states,
            'ca_counties': ca_counties
        }
    
    def geometric_operations(self, features):
        """Demonstrate geometric operations on features."""
        print("\n📐 Geometric Operations")
        print("-" * 30)
        
        california = features['california']
        ca_counties = features['ca_counties']
        
        # Area calculations
        print("1. Area Calculations:")
        
        def add_area_km2(feature):
            """Add area in km² to feature."""
            area_m2 = feature.geometry().area()
            area_km2 = area_m2.divide(1e6)
            return feature.set('area_km2', area_km2)
        
        ca_counties_with_area = ca_counties.map(add_area_km2)
        
        # Get largest county
        largest_county = ca_counties_with_area.sort('area_km2', False).first()
        largest_name = largest_county.get('NAME').getInfo()
        largest_area = largest_county.get('area_km2').getInfo()
        print(f"   Largest CA county: {largest_name} ({largest_area:.0f} km²)")
        
        # Centroid calculation
        print("\n2. Centroid Operations:")
        
        def add_centroid(feature):
            """Add centroid coordinates to feature."""
            centroid = feature.geometry().centroid()
            coords = centroid.coordinates()
            return feature.set({
                'centroid_lon': coords.get(0),
                'centroid_lat': coords.get(1)
            })
        
        counties_with_centroids = ca_counties.map(add_centroid)
        
        # Buffer operations
        print("3. Buffer Operations:")
        
        # Create buffer around California
        ca_buffer_50km = california.geometry().buffer(50000)  # 50 km buffer
        ca_buffer_100km = california.geometry().buffer(100000)  # 100 km buffer
        
        print("   ✓ Created 50km and 100km buffers around California")
        
        # Simplification
        print("\n4. Geometry Simplification:")
        
        def simplify_geometry(feature):
            """Simplify feature geometry."""
            simplified = feature.geometry().simplify(maxError=1000)  # 1km tolerance
            return feature.setGeometry(simplified)
        
        simplified_counties = ca_counties.map(simplify_geometry)
        print("   ✓ Simplified county geometries (1km tolerance)")
        
        return {
            'counties_with_area': ca_counties_with_area,
            'counties_with_centroids': counties_with_centroids,
            'ca_buffer_50km': ca_buffer_50km,
            'simplified_counties': simplified_counties
        }
    
    def spatial_relationships(self, datasets, processed_features):
        """Demonstrate spatial relationship operations."""
        print("\n🌐 Spatial Relationships")
        print("-" * 30)
        
        california = processed_features['counties_with_area'].first().geometry()
        ca_counties = processed_features['counties_with_area']
        
        # Intersection operations
        print("1. Intersection Operations:")
        
        # Protected areas in California
        ca_protected = datasets['protected_areas'].filterBounds(california)
        print(f"   Protected areas in CA: {ca_protected.size().getInfo()} areas")
        
        # Ecoregions intersecting California
        ca_ecoregions = datasets['ecoregions'].filterBounds(california)
        print(f"   Ecoregions in CA: {ca_ecoregions.size().getInfo()} regions")
        
        # Union operations
        print("\n2. Union Operations:")
        
        # Create union of all California counties
        ca_union = ca_counties.geometry().dissolve()
        print("   ✓ Created union of all CA counties")
        
        # Difference operations
        print("\n3. Difference Operations:")
        
        # Land area (counties minus protected areas)
        def calculate_unprotected_area(county):
            """Calculate unprotected area within county."""
            county_geom = county.geometry()
            
            # Get protected areas in this county
            county_protected = ca_protected.filterBounds(county_geom)
            
            if county_protected.size().gt(0):
                protected_union = county_protected.geometry().dissolve()
                unprotected = county_geom.difference(protected_union)
                unprotected_area = unprotected.area().divide(1e6)  # km²
            else:
                unprotected_area = county_geom.area().divide(1e6)
            
            return county.set('unprotected_area_km2', unprotected_area)
        
        # Apply to a subset for demonstration
        sample_counties = ca_counties.limit(5)
        counties_with_unprotected = sample_counties.map(calculate_unprotected_area)
        
        print("   ✓ Calculated unprotected areas for sample counties")
        
        # Distance operations
        print("\n4. Distance Operations:")
        
        # Create point features from county centroids
        def create_centroid_feature(county):
            """Create point feature from county centroid."""
            centroid = county.geometry().centroid()
            return ee.Feature(centroid, county.toDictionary())
        
        county_centroids = ca_counties.map(create_centroid_feature)
        
        # Distance to coast (using a coastal point)
        coast_point = ee.Geometry.Point([-122.5, 37.5])  # Pacific coast
        
        def add_distance_to_coast(feature):
            """Add distance to coast."""
            distance = feature.geometry().distance(coast_point)
            return feature.set('distance_to_coast_m', distance)
        
        centroids_with_distance = county_centroids.map(add_distance_to_coast)
        
        print("   ✓ Calculated distances to coast for county centroids")
        
        return {
            'ca_protected': ca_protected,
            'ca_ecoregions': ca_ecoregions,
            'ca_union': ca_union,
            'counties_with_unprotected': counties_with_unprotected,
            'centroids_with_distance': centroids_with_distance
        }
    
    def zonal_statistics(self, vector_features):
        """Demonstrate zonal statistics using raster data."""
        print("\n📊 Zonal Statistics")
        print("-" * 25)
        
        # Load raster datasets
        elevation = ee.Image('USGS/SRTMGL1_003')
        population = ee.Image('CIESIN/GPWv411/GPW_Population_Density/gpw_v4_population_density_rev11_2020_30_sec')
        
        print("Loaded datasets:")
        print("   ✓ SRTM elevation data")
        print("   ✓ Population density data")
        
        # Get California counties for analysis
        ca_counties = vector_features['counties_with_area']
        
        # Calculate zonal statistics for elevation
        print("\n1. Elevation Statistics:")
        
        def calculate_elevation_stats(feature):
            """Calculate elevation statistics for a feature."""
            stats = elevation.reduceRegion(
                reducer=ee.Reducer.minMax().combine(
                    reducer2=ee.Reducer.mean(),
                    sharedInputs=True
                ).combine(
                    reducer2=ee.Reducer.stdDev(),
                    sharedInputs=True
                ),
                geometry=feature.geometry(),
                scale=90,  # SRTM resolution
                maxPixels=1e9
            )
            
            return feature.set({
                'elevation_min': stats.get('elevation_min'),
                'elevation_max': stats.get('elevation_max'),
                'elevation_mean': stats.get('elevation_mean'),
                'elevation_stdDev': stats.get('elevation_stdDev')
            })
        
        # Apply to sample counties
        sample_counties = ca_counties.limit(10)
        counties_with_elevation = sample_counties.map(calculate_elevation_stats)
        
        print("   ✓ Calculated elevation statistics for sample counties")
        
        # Calculate population statistics
        print("\n2. Population Statistics:")
        
        def calculate_population_stats(feature):
            """Calculate population statistics for a feature."""
            # Population density (people per km²)
            pop_stats = population.select('population_density').reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    reducer2=ee.Reducer.sum(),
                    sharedInputs=True
                ),
                geometry=feature.geometry(),
                scale=1000,
                maxPixels=1e9
            )
            
            area_km2 = feature.geometry().area().divide(1e6)
            total_population = pop_stats.get('population_density_sum')
            
            return feature.set({
                'pop_density_mean': pop_stats.get('population_density_mean'),
                'total_population_est': total_population,
                'area_km2': area_km2
            })
        
        counties_with_population = sample_counties.map(calculate_population_stats)
        
        print("   ✓ Calculated population statistics for sample counties")
        
        # Vegetation statistics using NDVI
        print("\n3. Vegetation Statistics (NDVI):")
        
        # Get recent Landsat image
        landsat = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                  .filterDate('2023-06-01', '2023-09-01')
                  .filterBounds(ca_counties.geometry())
                  .sort('CLOUD_COVER')
                  .first())
        
        # Calculate NDVI
        ndvi = landsat.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
        
        def calculate_ndvi_stats(feature):
            """Calculate NDVI statistics for a feature."""
            ndvi_stats = ndvi.reduceRegion(
                reducer=ee.Reducer.mean().combine(
                    reducer2=ee.Reducer.stdDev(),
                    sharedInputs=True
                ).combine(
                    reducer2=ee.Reducer.percentile([25, 75]),
                    sharedInputs=True
                ),
                geometry=feature.geometry(),
                scale=30,
                maxPixels=1e9
            )
            
            return feature.set({
                'ndvi_mean': ndvi_stats.get('NDVI_mean'),
                'ndvi_stdDev': ndvi_stats.get('NDVI_stdDev'),
                'ndvi_p25': ndvi_stats.get('NDVI_p25'),
                'ndvi_p75': ndvi_stats.get('NDVI_p75')
            })
        
        counties_with_ndvi = sample_counties.map(calculate_ndvi_stats)
        
        print("   ✓ Calculated NDVI statistics for sample counties")
        
        return {
            'elevation_stats': counties_with_elevation,
            'population_stats': counties_with_population,
            'ndvi_stats': counties_with_ndvi
        }
    
    def create_custom_geometries(self):
        """Demonstrate creating custom geometries and features."""
        print("\n🎨 Custom Geometry Creation")
        print("-" * 35)
        
        # Create points
        print("1. Creating Points:")
        points = [
            ee.Geometry.Point([-122.4, 37.8]),  # San Francisco
            ee.Geometry.Point([-118.2, 34.1]),  # Los Angeles
            ee.Geometry.Point([-121.5, 38.6])   # Sacramento
        ]
        
        point_features = ee.FeatureCollection([
            ee.Feature(points[0], {'city': 'San Francisco', 'population': 884000}),
            ee.Feature(points[1], {'city': 'Los Angeles', 'population': 3980000}),
            ee.Feature(points[2], {'city': 'Sacramento', 'population': 525000})
        ])
        
        print(f"   ✓ Created {point_features.size().getInfo()} city points")
        
        # Create lines
        print("\n2. Creating Lines:")
        
        # Highway route (simplified)
        highway_coords = [
            [-122.4, 37.8],  # San Francisco
            [-121.9, 37.3],  # San Jose
            [-120.7, 36.7],  # Fresno
            [-118.2, 34.1]   # Los Angeles
        ]
        
        highway = ee.Geometry.LineString(highway_coords)
        highway_feature = ee.Feature(highway, {
            'name': 'California Highway Route',
            'length_km': highway.length().divide(1000)
        })
        
        print("   ✓ Created highway route line")
        
        # Create polygons
        print("\n3. Creating Polygons:")
        
        # Study area polygon
        study_area_coords = [[
            [-123.0, 37.0],
            [-122.0, 37.0],
            [-122.0, 38.0],
            [-123.0, 38.0],
            [-123.0, 37.0]
        ]]
        
        study_area = ee.Geometry.Polygon(study_area_coords)
        study_area_feature = ee.Feature(study_area, {
            'name': 'San Francisco Bay Study Area',
            'area_km2': study_area.area().divide(1e6)
        })
        
        print("   ✓ Created study area polygon")
        
        # Create buffer polygons around points
        print("\n4. Creating Buffers:")
        
        def create_city_buffer(feature):
            """Create buffer around city based on population."""
            population = ee.Number(feature.get('population'))
            # Buffer radius based on population (scaled)
            radius = population.sqrt().multiply(10)
            buffered_geom = feature.geometry().buffer(radius)
            return feature.setGeometry(buffered_geom).set('buffer_radius', radius)
        
        city_buffers = point_features.map(create_city_buffer)
        
        print("   ✓ Created population-based buffers around cities")
        
        # Create regular grid
        print("\n5. Creating Regular Grid:")
        
        def create_grid(bounds, cell_size):
            """Create a regular grid over the bounds."""
            # Get bounding box
            coords = ee.List(bounds.coordinates().get(0))
            
            # Extract min/max coordinates
            xs = coords.map(lambda item: ee.List(item).get(0))
            ys = coords.map(lambda item: ee.List(item).get(1))
            
            min_x = xs.reduce(ee.Reducer.min())
            max_x = xs.reduce(ee.Reducer.max())
            min_y = ys.reduce(ee.Reducer.min())
            max_y = ys.reduce(ee.Reducer.max())
            
            # Create grid
            x_range = ee.List.sequence(min_x, max_x, cell_size)
            y_range = ee.List.sequence(min_y, max_y, cell_size)
            
            def create_cell(x):
                def create_row(y):
                    x_coord = ee.Number(x)
                    y_coord = ee.Number(y)
                    
                    cell = ee.Geometry.Rectangle([
                        x_coord, y_coord,
                        x_coord.add(cell_size), y_coord.add(cell_size)
                    ])
                    
                    return ee.Feature(cell, {
                        'grid_x': x_coord,
                        'grid_y': y_coord,
                        'cell_id': x_coord.format('%.2f').cat('_').cat(y_coord.format('%.2f'))
                    })
                
                return y_range.map(create_row)
            
            grid_features = x_range.map(create_cell).flatten()
            return ee.FeatureCollection(grid_features)
        
        # Create 0.1 degree grid over study area
        grid = create_grid(study_area, 0.1)
        grid_count = grid.size().getInfo()
        print(f"   ✓ Created regular grid with {grid_count} cells")
        
        return {
            'cities': point_features,
            'highway': highway_feature,
            'study_area': study_area_feature,
            'city_buffers': city_buffers,
            'grid': grid
        }
    
    def export_vector_data(self, feature_collection, description):
        """Demonstrate vector data export."""
        print(f"\n📤 Exporting Vector Data: {description}")
        print("-" * 40)
        
        # Export to Google Drive
        export_task = ee.batch.Export.table.toDrive(
            collection=feature_collection,
            description=description,
            folder='EarthEngine_Exports',
            fileFormat='SHP'  # Shapefile format
        )
        
        print(f"✓ Export task created: {description}")
        print(f"  Task ID: {export_task.id}")
        print(f"  Status: Ready to start")
        print(f"  Format: Shapefile")
        print(f"  Destination: Google Drive/EarthEngine_Exports/")
        
        # Note: To actually start the export, uncomment the line below
        # export_task.start()
        
        return export_task

def main():
    """Main function demonstrating vector operations."""
    
    # Initialize vector operations system
    vector_ops = VectorOperations('your-project-id')
    
    print("="*70)
    print("🗺️  EARTH ENGINE VECTOR OPERATIONS GUIDE")
    print("="*70)
    
    # Step 1: Load vector datasets
    datasets = vector_ops.load_vector_datasets()
    
    # Step 2: Basic feature operations
    basic_features = vector_ops.basic_feature_operations(datasets)
    
    # Step 3: Geometric operations
    geometric_results = vector_ops.geometric_operations(basic_features)
    
    # Step 4: Spatial relationships
    spatial_results = vector_ops.spatial_relationships(datasets, geometric_results)
    
    # Step 5: Zonal statistics
    zonal_results = vector_ops.zonal_statistics(geometric_results)
    
    # Step 6: Create custom geometries
    custom_geometries = vector_ops.create_custom_geometries()
    
    # Step 7: Export examples
    print("\n📤 Export Examples")
    print("-" * 25)
    
    # Export California counties with statistics
    counties_export = vector_ops.export_vector_data(
        geometric_results['counties_with_area'].limit(5),
        'california_counties_with_area'
    )
    
    # Export custom city features
    cities_export = vector_ops.export_vector_data(
        custom_geometries['cities'],
        'california_cities'
    )
    
    # Summary
    print("\n" + "="*70)
    print("📊 VECTOR OPERATIONS SUMMARY")
    print("="*70)
    
    print("\n🎯 Operations Demonstrated:")
    print("• Loading Earth Engine vector datasets")
    print("• Attribute and spatial filtering")
    print("• Geometric calculations (area, centroid, buffer)")
    print("• Spatial relationship analysis")
    print("• Zonal statistics with raster data")
    print("• Custom geometry creation")
    print("• Vector data export")
    
    print("\n📈 Key Results:")
    print(f"• California counties analyzed: {basic_features['ca_counties'].size().getInfo()}")
    print(f"• Protected areas in CA: {spatial_results['ca_protected'].size().getInfo()}")
    print(f"• Custom grid cells created: {custom_geometries['grid'].size().getInfo()}")
    
    print("\n🏆 Best Practices Applied:")
    print("• Efficient spatial filtering")
    print("• Appropriate scale selection for analysis")
    print("• Combining vector and raster operations")
    print("• Proper error handling and validation")
    
    print("\n✅ Vector Operations Guide Complete!")

if __name__ == "__main__":
    main()
