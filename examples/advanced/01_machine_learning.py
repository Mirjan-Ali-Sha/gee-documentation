"""
Advanced Example 1: Machine Learning Classification
===================================================

This example demonstrates:
- Land cover classification using machine learning
- Training data collection and preparation
- Random Forest classifier implementation
- Accuracy assessment and validation
- Large-scale prediction and export

Use case: Mapping land cover types using Sentinel-2 imagery
"""

import ee
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

class LandCoverClassifier:
    """
    Advanced land cover classification using Google Earth Engine and Machine Learning.
    """
    
    def __init__(self, project_id):
        """
        Initialize the classifier with Earth Engine project.
        """
        self.project_id = project_id
        self.classifier = None
        self.trained_classifier = None
        self.class_names = ['Water', 'Forest', 'Urban', 'Agriculture', 'Bare_Soil']
        self.class_values = [0, 1, 2, 3, 4]
        
        # Initialize Earth Engine
        try:
            ee.Initialize(project=project_id)
            print("✓ Earth Engine initialized successfully!")
        except Exception as e:
            print(f"✗ Error initializing Earth Engine: {e}")
            raise
    
    def create_composite(self, geometry, start_date, end_date, cloud_threshold=10):
        """
        Create a cloud-free Sentinel-2 composite.
        
        Args:
            geometry: Area of interest
            start_date: Start date for image collection
            end_date: End date for image collection
            cloud_threshold: Maximum cloud cover percentage
        
        Returns:
            ee.Image: Cloud-free composite image
        """
        print(f"Creating Sentinel-2 composite from {start_date} to {end_date}")
        
        # Load Sentinel-2 Surface Reflectance collection
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                     .filterDate(start_date, end_date)
                     .filterBounds(geometry)
                     .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_threshold)))
        
        print(f"Found {collection.size().getInfo()} images")
        
        # Cloud masking function
        def mask_clouds(image):
            qa = image.select('QA60')
            cloud_bit_mask = 1 << 10
            cirrus_bit_mask = 1 << 11
            mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
                   qa.bitwiseAnd(cirrus_bit_mask).eq(0))
            return image.updateMask(mask).divide(10000)
        
        # Apply cloud masking and create median composite
        composite = collection.map(mask_clouds).median()
        
        # Add spectral indices
        composite = self.add_spectral_indices(composite)
        
        return composite
    
    def add_spectral_indices(self, image):
        """
        Add spectral indices to improve classification accuracy.
        
        Args:
            image: Sentinel-2 image
        
        Returns:
            ee.Image: Image with additional spectral indices
        """
        # NDVI (Normalized Difference Vegetation Index)
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        
        # NDWI (Normalized Difference Water Index)
        ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
        
        # NDBI (Normalized Difference Built-up Index)
        ndbi = image.normalizedDifference(['B11', 'B8']).rename('NDBI')
        
        # EVI (Enhanced Vegetation Index)
        evi = image.expression(
            '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))',
            {
                'NIR': image.select('B8'),
                'RED': image.select('B4'),
                'BLUE': image.select('B2')
            }
        ).rename('EVI')
        
        # SAVI (Soil Adjusted Vegetation Index)
        savi = image.expression(
            '((NIR - RED) / (NIR + RED + 0.5)) * (1.5)',
            {
                'NIR': image.select('B8'),
                'RED': image.select('B4')
            }
        ).rename('SAVI')
        
        return image.addBands([ndvi, ndwi, ndbi, evi, savi])
    
    def create_training_data(self, image, training_points):
        """
        Create training dataset from labeled points.
        
        Args:
            image: Composite image for training
            training_points: ee.FeatureCollection with training points
        
        Returns:
            ee.FeatureCollection: Training features with spectral values
        """
        print("Creating training dataset...")
        
        # Select bands for training
        bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12',
                'NDVI', 'NDWI', 'NDBI', 'EVI', 'SAVI']
        
        # Sample the image at training points
        training = image.select(bands).sampleRegions(
            collection=training_points,
            properties=['landcover'],
            scale=10
        )
        
        print(f"Training samples: {training.size().getInfo()}")
        
        return training
    
    def train_classifier(self, training_data, n_trees=100):
        """
        Train Random Forest classifier.
        
        Args:
            training_data: Training feature collection
            n_trees: Number of trees in Random Forest
        
        Returns:
            ee.Classifier: Trained classifier
        """
        print(f"Training Random Forest classifier with {n_trees} trees...")
        
        # Select features for training
        bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12',
                'NDVI', 'NDWI', 'NDBI', 'EVI', 'SAVI']
        
        # Create and train classifier
        classifier = ee.Classifier.smileRandomForest(n_trees).train(
            features=training_data,
            classProperty='landcover',
            inputProperties=bands
        )
        
        self.trained_classifier = classifier
        print("✓ Classifier training completed!")
        
        return classifier
    
    def classify_image(self, image, classifier=None):
        """
        Classify the input image using trained classifier.
        
        Args:
            image: Image to classify
            classifier: Trained classifier (optional)
        
        Returns:
            ee.Image: Classified image
        """
        if classifier is None:
            classifier = self.trained_classifier
        
        if classifier is None:
            raise ValueError("No trained classifier available")
        
        print("Classifying image...")
        
        # Select the same bands used for training
        bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A', 'B11', 'B12',
                'NDVI', 'NDWI', 'NDBI', 'EVI', 'SAVI']
        
        classified = image.select(bands).classify(classifier)
        
        return classified
    
    def assess_accuracy(self, training_data, classifier=None):
        """
        Assess classifier accuracy using confusion matrix.
        
        Args:
            training_data: Validation dataset
            classifier: Trained classifier
        
        Returns:
            dict: Accuracy metrics
        """
        if classifier is None:
            classifier = self.trained_classifier
        
        print("Assessing accuracy...")
        
        # Get confusion matrix
        confusion_matrix = classifier.confusionMatrix()
        
        # Calculate accuracy metrics
        overall_accuracy = confusion_matrix.accuracy()
        kappa = confusion_matrix.kappa()
        
        print(f"Overall Accuracy: {overall_accuracy.getInfo():.3f}")
        print(f"Kappa Coefficient: {kappa.getInfo():.3f}")
        
        # Get confusion matrix as array
        cm_array = confusion_matrix.getInfo()
        
        return {
            'overall_accuracy': overall_accuracy.getInfo(),
            'kappa': kappa.getInfo(),
            'confusion_matrix': cm_array
        }
    
    def create_training_points(self, geometry):
        """
        Create sample training points for different land cover classes.
        This is a simplified example - in practice, use field data or 
        careful visual interpretation.
        
        Args:
            geometry: Area of interest
        
        Returns:
            ee.FeatureCollection: Training points
        """
        print("Creating sample training points...")
        
        # Example training points (replace with actual training data)
        water_points = ee.FeatureCollection([
            ee.Feature(ee.Geometry.Point([-122.0, 37.4]), {'landcover': 0}),
            ee.Feature(ee.Geometry.Point([-122.1, 37.3]), {'landcover': 0}),
        ])
        
        forest_points = ee.FeatureCollection([
            ee.Feature(ee.Geometry.Point([-122.2, 37.5]), {'landcover': 1}),
            ee.Feature(ee.Geometry.Point([-122.3, 37.6]), {'landcover': 1}),
        ])
        
        urban_points = ee.FeatureCollection([
            ee.Feature(ee.Geometry.Point([-122.4, 37.7]), {'landcover': 2}),
            ee.Feature(ee.Geometry.Point([-122.5, 37.8]), {'landcover': 2}),
        ])
        
        agriculture_points = ee.FeatureCollection([
            ee.Feature(ee.Geometry.Point([-122.6, 37.2]), {'landcover': 3}),
            ee.Feature(ee.Geometry.Point([-122.7, 37.1]), {'landcover': 3}),
        ])
        
        bare_soil_points = ee.FeatureCollection([
            ee.Feature(ee.Geometry.Point([-122.8, 37.0]), {'landcover': 4}),
            ee.Feature(ee.Geometry.Point([-122.9, 36.9]), {'landcover': 4}),
        ])
        
        # Merge all training points
        training_points = water_points.merge(forest_points)\
                                   .merge(urban_points)\
                                   .merge(agriculture_points)\
                                   .merge(bare_soil_points)
        
        return training_points
    
    def export_classification(self, classified_image, geometry, filename, scale=10):
        """
        Export classified image to Google Drive.
        
        Args:
            classified_image: Classified image
            geometry: Export region
            filename: Output filename
            scale: Export scale in meters
        """
        print(f"Exporting classification to Google Drive: {filename}")
        
        task = ee.batch.Export.image.toDrive(
            image=classified_image,
            description=filename,
            folder='EarthEngine_Exports',
            fileNamePrefix=filename,
            region=geometry,
            scale=scale,
            maxPixels=1e13
        )
        
        task.start()
        print(f"Export task started. Check Google Drive folder 'EarthEngine_Exports'")
        print(f"Task ID: {task.id}")
        
        return task

def main():
    """
    Main function demonstrating advanced machine learning classification.
    """
    # Initialize classifier
    classifier_system = LandCoverClassifier('your-project-id')
    
    # Define area of interest (San Francisco Bay Area example)
    geometry = ee.Geometry.Rectangle([-122.5, 37.0, -121.5, 38.0])
    
    # Create composite image
    composite = classifier_system.create_composite(
        geometry=geometry,
        start_date='2023-06-01',
        end_date='2023-08-31',
        cloud_threshold=10
    )
    
    # Create training points (replace with actual training data)
    training_points = classifier_system.create_training_points(geometry)
    
    # Create training dataset
    training_data = classifier_system.create_training_data(
        image=composite,
        training_points=training_points
    )
    
    # Train classifier
    classifier = classifier_system.train_classifier(
        training_data=training_data,
        n_trees=100
    )
    
    # Classify the image
    classified = classifier_system.classify_image(
        image=composite,
        classifier=classifier
    )
    
    # Assess accuracy
    accuracy_metrics = classifier_system.assess_accuracy(
        training_data=training_data,
        classifier=classifier
    )
    
    print("\n📊 Classification Results:")
    print(f"Overall Accuracy: {accuracy_metrics['overall_accuracy']:.1%}")
    print(f"Kappa Coefficient: {accuracy_metrics['kappa']:.3f}")
    
    # Export results
    export_task = classifier_system.export_classification(
        classified_image=classified,
        geometry=geometry,
        filename='land_cover_classification_2023',
        scale=10
    )
    
    print("\n🎯 Advanced Classification Analysis Complete!")
    print("Key Features Demonstrated:")
    print("• Multi-spectral index calculation")
    print("• Random Forest classification")
    print("• Accuracy assessment")
    print("• Large-scale processing and export")
    print("• Object-oriented programming approach")

if __name__ == "__main__":
    main()
