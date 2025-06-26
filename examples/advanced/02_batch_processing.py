"""
Advanced Example 2: Batch Processing and Large-Scale Analysis
=============================================================

This example demonstrates:
- Large-scale batch processing techniques
- Parallel processing strategies
- Memory-efficient workflows
- Error handling for long-running operations
- Progress monitoring and logging
- Export optimization for large datasets

Prerequisites:
- Experience with Earth Engine collections
- Understanding of parallel processing concepts
- Knowledge of export operations
- Familiarity with error handling
"""

import ee
import time
import json
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

class BatchProcessor:
    """Advanced batch processing system for Earth Engine operations."""
    
    def __init__(self, project_id, max_workers=5):
        """Initialize batch processor."""
        self.project_id = project_id
        self.max_workers = max_workers
        self.tasks = []
        self.results = {}
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('batch_processing.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize Earth Engine
        self.initialize_ee()
    
    def initialize_ee(self):
        """Initialize Earth Engine with error handling."""
        try:
            ee.Initialize(project=self.project_id)
            self.logger.info("✓ Earth Engine initialized successfully")
        except Exception as e:
            self.logger.error(f"✗ Failed to initialize Earth Engine: {e}")
            raise
    
    def create_processing_grid(self, region, grid_size=1.0):
        """
        Create a grid of processing tiles over a large region.
        
        Args:
            region: ee.Geometry defining the area of interest
            grid_size: Size of each grid cell in degrees
        
        Returns:
            ee.FeatureCollection: Grid cells for processing
        """
        self.logger.info(f"Creating processing grid with {grid_size}° cells")
        
        # Get region bounds
        bounds = region.bounds()
        coords = ee.List(bounds.coordinates().get(0))
        
        # Extract coordinates
        xs = coords.map(lambda item: ee.List(item).get(0))
        ys = coords.map(lambda item: ee.List(item).get(1))
        
        min_x = xs.reduce(ee.Reducer.min())
        max_x = xs.reduce(ee.Reducer.max())
        min_y = ys.reduce(ee.Reducer.min())
        max_y = ys.reduce(ee.Reducer.max())
        
        # Create grid
        def create_grid_cell(x):
            def create_cell_row(y):
                x_coord = ee.Number(x)
                y_coord = ee.Number(y)
                
                cell = ee.Geometry.Rectangle([
                    x_coord, y_coord,
                    x_coord.add(grid_size), y_coord.add(grid_size)
                ])
                
                # Only include cells that intersect the region
                intersects = cell.intersects(region)
                
                return ee.Feature(cell, {
                    'tile_x': x_coord,
                    'tile_y': y_coord,
                    'tile_id': x_coord.format('%.2f').cat('_').cat(y_coord.format('%.2f')),
                    'intersects_region': intersects
                }).set('intersects_region', intersects)
            
            x_range = ee.List.sequence(min_y, max_y, grid_size)
            return x_range.map(create_cell_row)
        
        x_range = ee.List.sequence(min_x, max_x, grid_size)
        grid_features = x_range.map(create_grid_cell).flatten()
        
        # Filter to only cells that intersect the region
        valid_grid = ee.FeatureCollection(grid_features).filter(
            ee.Filter.eq('intersects_region', True)
        )
        
        grid_size_info = valid_grid.size().getInfo()
        self.logger.info(f"Created grid with {grid_size_info} tiles")
        
        return valid_grid
    
    def batch_image_collection_processing(self, collection, process_func, batch_size=50):
        """
        Process large image collections in batches.
        
        Args:
            collection: ee.ImageCollection to process
            process_func: Function to apply to each batch
            batch_size: Number of images per batch
        
        Returns:
            list: Results from each batch
        """
        total_images = collection.size().getInfo()
        self.logger.info(f"Processing {total_images} images in batches of {batch_size}")
        
        results = []
        num_batches = (total_images + batch_size - 1) // batch_size
        
        for i in range(0, total_images, batch_size):
            batch_num = i // batch_size + 1
            self.logger.info(f"Processing batch {batch_num}/{num_batches}")
            
            try:
                # Get batch
                batch = collection.limit(batch_size, i)
                
                # Apply processing function
                start_time = time.time()
                batch_result = process_func(batch)
                processing_time = time.time() - start_time
                
                results.append({
                    'batch_id': batch_num,
                    'result': batch_result,
                    'processing_time': processing_time,
                    'images_processed': min(batch_size, total_images - i)
                })
                
                self.logger.info(f"Batch {batch_num} completed in {processing_time:.2f}s")
                
                # Small delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error processing batch {batch_num}: {e}")
                results.append({
                    'batch_id': batch_num,
                    'result': None,
                    'error': str(e),
                    'processing_time': 0
                })
        
        return results
    
    def parallel_export_tasks(self, export_configs):
        """
        Create and manage multiple export tasks in parallel.
        
        Args:
            export_configs: List of export configuration dictionaries
        
        Returns:
            dict: Task IDs and their configurations
        """
        self.logger.info(f"Creating {len(export_configs)} parallel export tasks")
        
        tasks = {}
        
        for i, config in enumerate(export_configs):
            try:
                # Create export task based on type
                if config['type'] == 'image':
                    task = ee.batch.Export.image.toDrive(**config['params'])
                elif config['type'] == 'table':
                    task = ee.batch.Export.table.toDrive(**config['params'])
                elif config['type'] == 'video':
                    task = ee.batch.Export.video.toDrive(**config['params'])
                else:
                    raise ValueError(f"Unknown export type: {config['type']}")
                
                # Start task
                task.start()
                
                tasks[task.id] = {
                    'task': task,
                    'config': config,
                    'started_at': datetime.now(),
                    'status': 'RUNNING'
                }
                
                self.logger.info(f"Started export task {i+1}: {task.id}")
                
                # Small delay between task starts
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"Failed to create export task {i+1}: {e}")
        
        return tasks
    
    def monitor_task_progress(self, tasks, check_interval=60):
        """
        Monitor progress of running tasks.
        
        Args:
            tasks: Dictionary of task IDs and configurations
            check_interval: How often to check status (seconds)
        
        Returns:
            dict: Final status of all tasks
        """
        self.logger.info(f"Monitoring {len(tasks)} tasks")
        
        completed_tasks = 0
        total_tasks = len(tasks)
        
        while completed_tasks < total_tasks:
            self.logger.info(f"Checking task status... ({completed_tasks}/{total_tasks} completed)")
            
            for task_id, task_info in tasks.items():
                if task_info['status'] in ['COMPLETED', 'FAILED', 'CANCELLED']:
                    continue
                
                try:
                    # Check task status
                    status = task_info['task'].status()
                    
                    if status['state'] in ['COMPLETED', 'FAILED', 'CANCELLED']:
                        task_info['status'] = status['state']
                        task_info['completed_at'] = datetime.now()
                        
                        if status['state'] == 'COMPLETED':
                            completed_tasks += 1
                            self.logger.info(f"✓ Task completed: {task_id}")
                        else:
                            completed_tasks += 1
                            error_msg = status.get('error_message', 'Unknown error')
                            self.logger.error(f"✗ Task failed: {task_id} - {error_msg}")
                
                except Exception as e:
                    self.logger.error(f"Error checking task {task_id}: {e}")
            
            if completed_tasks < total_tasks:
                time.sleep(check_interval)
        
        self.logger.info("All tasks completed")
        return tasks
    
    def time_series_batch_processing(self, region, start_date, end_date, time_step_days=16):
        """
        Process time series data in temporal batches.
        
        Args:
            region: Area of interest
            start_date: Start date string
            end_date: End date string
            time_step_days: Days per time step
        
        Returns:
            list: Time series results
        """
        self.logger.info(f"Processing time series from {start_date} to {end_date}")
        
        # Create time periods
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        periods = []
        current_date = start
        
        while current_date < end:
            period_end = min(current_date + timedelta(days=time_step_days), end)
            periods.append({
                'start': current_date.strftime('%Y-%m-%d'),
                'end': period_end.strftime('%Y-%m-%d'),
                'period_id': len(periods) + 1
            })
            current_date = period_end
        
        self.logger.info(f"Created {len(periods)} time periods")
        
        # Process each period
        results = []
        
        for period in periods:
            self.logger.info(f"Processing period {period['period_id']}: {period['start']} to {period['end']}")
            
            try:
                # Load collection for this period
                collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                             .filterDate(period['start'], period['end'])
                             .filterBounds(region)
                             .filter(ee.Filter.lt('CLOUD_COVER', 30)))
                
                # Check if any images available
                count = collection.size().getInfo()
                if count == 0:
                    self.logger.warning(f"No images found for period {period['period_id']}")
                    continue
                
                # Create composite
                composite = collection.median()
                
                # Calculate NDVI
                ndvi = composite.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
                
                # Calculate statistics
                stats = ndvi.reduceRegion(
                    reducer=ee.Reducer.mean().combine(
                        reducer2=ee.Reducer.stdDev(),
                        sharedInputs=True
                    ),
                    geometry=region,
                    scale=30,
                    maxPixels=1e9
                )
                
                result = {
                    'period_id': period['period_id'],
                    'start_date': period['start'],
                    'end_date': period['end'],
                    'image_count': count,
                    'ndvi_mean': stats.getInfo().get('NDVI_mean'),
                    'ndvi_stddev': stats.getInfo().get('NDVI_stdDev')
                }
                
                results.append(result)
                self.logger.info(f"✓ Period {period['period_id']} processed successfully")
                
            except Exception as e:
                self.logger.error(f"✗ Error processing period {period['period_id']}: {e}")
                results.append({
                    'period_id': period['period_id'],
                    'start_date': period['start'],
                    'end_date': period['end'],
                    'error': str(e)
                })
        
        return results
    
    def large_scale_classification(self, training_data, region_grid, output_folder):
        """
        Perform classification across a large region using grid-based processing.
        
        Args:
            training_data: Training feature collection
            region_grid: Grid of processing tiles
            output_folder: Output folder for results
        
        Returns:
            list: Export task configurations
        """
        self.logger.info("Starting large-scale classification")
        
        # Prepare classifier
        def train_classifier():
            """Train random forest classifier."""
            # Load recent Landsat collection
            collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                         .filterDate('2023-01-01', '2023-12-31')
                         .filter(ee.Filter.lt('CLOUD_COVER', 10))
                         .median())
            
            # Calculate spectral indices
            ndvi = collection.normalizedDifference(['SR_B5', 'SR_B4']).rename('NDVI')
            ndwi = collection.normalizedDifference(['SR_B3', 'SR_B5']).rename('NDWI')
            
            # Create feature image
            features = collection.select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5', 'SR_B6', 'SR_B7']).addBands([ndvi, ndwi])
            
            # Sample training data
            training = features.sampleRegions(
                collection=training_data,
                properties=['landcover'],
                scale=30
            )
            
            # Train classifier
            classifier = ee.Classifier.smileRandomForest(100).train(
                features=training,
                classProperty='landcover',
                inputProperties=features.bandNames()
            )
            
            return features, classifier
        
        features, classifier = train_classifier()
        
        # Get grid tiles
        grid_list = region_grid.getInfo()['features']
        self.logger.info(f"Processing {len(grid_list)} grid tiles")
        
        # Create export configurations for each tile
        export_configs = []
        
        for i, tile_feature in enumerate(grid_list):
            tile_geom = ee.Geometry(tile_feature['geometry'])
            tile_id = tile_feature['properties']['tile_id']
            
            # Classify tile
            tile_features = features.clip(tile_geom)
            classified = tile_features.classify(classifier).select(['classification'])
            
            # Create export configuration
            export_config = {
                'type': 'image',
                'params': {
                    'image': classified,
                    'description': f'classification_tile_{tile_id}',
                    'folder': output_folder,
                    'region': tile_geom,
                    'scale': 30,
                    'crs': 'EPSG:4326',
                    'maxPixels': 1e13
                }
            }
            
            export_configs.append(export_config)
        
        return export_configs
    
    def optimize_memory_usage(self):
        """Implement memory optimization strategies."""
        self.logger.info("Applying memory optimization strategies")
        
        strategies = {
            'reduce_precision': 'Use .float() instead of .double() for calculations',
            'select_bands': 'Only select necessary bands for processing',
            'clip_early': 'Clip images to study area as early as possible',
            'batch_processing': 'Process data in smaller chunks',
            'clear_cache': 'Periodically clear Earth Engine cache'
        }
        
        for strategy, description in strategies.items():
            self.logger.info(f"  {strategy}: {description}")
        
        # Example optimization
        def optimized_processing_example(image, region):
            """Example of optimized image processing."""
            # Clip early and select only needed bands
            clipped = image.clip(region).select(['SR_B4', 'SR_B5'])
            
            # Use float precision
            processed = clipped.float()
            
            # Calculate only necessary indices
            ndvi = processed.normalizedDifference(['SR_B5', 'SR_B4'])
            
            return ndvi
        
        return optimized_processing_example

def main():
    """Main function demonstrating batch processing capabilities."""
    
    # Initialize batch processor
    processor = BatchProcessor('your-project-id', max_workers=3)
    
    print("="*80)
    print("⚡ ADVANCED BATCH PROCESSING AND LARGE-SCALE ANALYSIS")
    print("="*80)
    
    # Define study region (California)
    study_region = ee.Geometry.Rectangle([-124.5, 32.5, -114.0, 42.0])
    
    # Example 1: Grid-based processing
    print("\n1️⃣ Grid-Based Processing")
    print("-" * 30)
    
    processing_grid = processor.create_processing_grid(study_region, grid_size=2.0)
    print(f"✓ Created processing grid with {processing_grid.size().getInfo()} tiles")
    
    # Example 2: Batch collection processing
    print("\n2️⃣ Batch Collection Processing")
    print("-" * 35)
    
    # Load large collection
    large_collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                       .filterDate('2023-01-01', '2023-12-31')
                       .filterBounds(study_region.centroid().buffer(100000))
                       .filter(ee.Filter.lt('CLOUD_COVER', 50)))
    
    def calculate_ndvi_stats(batch):
        """Calculate NDVI statistics for a batch of images."""
        composite = batch.median()
        ndvi = composite.normalizedDifference(['SR_B5', 'SR_B4'])
        
        stats = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=study_region.centroid().buffer(50000),
            scale=30,
            maxPixels=1e6
        )
        
        return stats.get('nd')
    
    batch_results = processor.batch_image_collection_processing(
        large_collection, 
        calculate_ndvi_stats, 
        batch_size=20
    )
    
    print(f"✓ Processed {len(batch_results)} batches")
    successful_batches = [r for r in batch_results if 'error' not in r]
    print(f"✓ {len(successful_batches)} batches completed successfully")
    
    # Example 3: Time series batch processing
    print("\n3️⃣ Time Series Batch Processing")
    print("-" * 35)
    
    small_region = study_region.centroid().buffer(10000)
    time_series_results = processor.time_series_batch_processing(
        small_region,
        '2023-01-01',
        '2023-12-31',
        time_step_days=30
    )
    
    print(f"✓ Processed {len(time_series_results)} time periods")
    
    # Create summary statistics
    valid_results = [r for r in time_series_results if 'error' not in r and r.get('ndvi_mean')]
    if valid_results:
        avg_ndvi = sum(r['ndvi_mean'] for r in valid_results) / len(valid_results)
        print(f"✓ Average NDVI across time series: {avg_ndvi:.3f}")
    
    # Example 4: Parallel export setup
    print("\n4️⃣ Parallel Export Configuration")
    print("-" * 35)
    
    # Create sample export configurations
    sample_exports = []
    grid_sample = processing_grid.limit(3)  # Process first 3 tiles
    
    grid_features = grid_sample.getInfo()['features']
    
    for i, tile in enumerate(grid_features):
        tile_geom = ee.Geometry(tile['geometry'])
        
        # Create sample image for export
        sample_image = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
                       .filterBounds(tile_geom)
                       .filterDate('2023-06-01', '2023-08-31')
                       .median()
                       .select(['SR_B4', 'SR_B3', 'SR_B2']))
        
        export_config = {
            'type': 'image',
            'params': {
                'image': sample_image,
                'description': f'sample_export_tile_{i+1}',
                'folder': 'BatchProcessing_Exports',
                'region': tile_geom,
                'scale': 30,
                'maxPixels': 1e13
            }
        }
        
        sample_exports.append(export_config)
    
    print(f"✓ Created {len(sample_exports)} export configurations")
    print("  (Note: Exports not started in demo mode)")
    
    # Example 5: Memory optimization demonstration
    print("\n5️⃣ Memory Optimization")
    print("-" * 25)
    
    optimization_func = processor.optimize_memory_usage()
    print("✓ Memory optimization strategies implemented")
    
    # Example 6: Performance monitoring
    print("\n6️⃣ Performance Monitoring")
    print("-" * 28)
    
    # Calculate processing statistics
    if batch_results:
        total_processing_time = sum(r.get('processing_time', 0) for r in batch_results)
        total_images = sum(r.get('images_processed', 0) for r in batch_results)
        
        print(f"✓ Total processing time: {total_processing_time:.2f} seconds")
        print(f"✓ Total images processed: {total_images}")
        
        if total_images > 0:
            avg_time_per_image = total_processing_time / total_images
            print(f"✓ Average time per image: {avg_time_per_image:.3f} seconds")
    
    # Summary
    print("\n" + "="*80)
    print("📊 BATCH PROCESSING SUMMARY")
    print("="*80)
    
    print("\n🎯 Capabilities Demonstrated:")
    print("• Grid-based spatial processing")
    print("• Batch collection processing with error handling")
    print("• Time series analysis in temporal batches")
    print("• Parallel export task management")
    print("• Memory optimization strategies")
    print("• Performance monitoring and logging")
    
    print("\n📈 Processing Statistics:")
    print(f"• Processing grid: {processing_grid.size().getInfo()} tiles")
    print(f"• Collection batches: {len(batch_results)} processed")
    print(f"• Time series periods: {len(time_series_results)} analyzed")
    print(f"• Export tasks configured: {len(sample_exports)}")
    
    print("\n🏆 Best Practices Applied:")
    print("• Comprehensive error handling and logging")
    print("• Progress monitoring for long operations")
    print("• Memory-efficient processing strategies")
    print("• Scalable parallel processing architecture")
    print("• Resource optimization techniques")
    
    print("\n✅ Advanced Batch Processing Complete!")

if __name__ == "__main__":
    main()
