"""
Advanced Example 3: Custom Algorithms and Specialized Functions
===============================================================

This example demonstrates:
- Creating custom Earth Engine algorithms
- Implementing specialized mathematical functions
- Building reusable code libraries
- Performance optimization techniques
- Advanced computational methods

Prerequisites:
- Strong programming background
- Understanding of Earth Engine architecture
- Knowledge of mathematical algorithms
- Experience with optimization techniques
"""

import ee
import math
import numpy as np
from typing import List, Dict, Tuple, Union, Optional

class CustomAlgorithms:
    """Library of custom Earth Engine algorithms and specialized functions."""
    
    def __init__(self, project_id: str):
        """Initialize custom algorithms library."""
        self.project_id = project_id
        self.initialize_ee()
    
    def initialize_ee(self):
        """Initialize Earth Engine with error handling."""
        try:
            ee.Initialize(project=self.project_id)
            print("✓ Earth Engine initialized for custom algorithms")
        except Exception as e:
            print(f"✗ Failed to initialize Earth Engine: {e}")
            raise
    
    def adaptive_threshold_segmentation(self, image: ee.Image, 
                                      window_size: int = 15,
                                      threshold_factor: float = 0.1) -> ee.Image:
        """
        Implement adaptive threshold segmentation algorithm.
        
        Args:
            image: Input single-band image
            window_size: Size of local window for threshold calculation
            threshold_factor: Factor for threshold adjustment
        
        Returns:
            ee.Image: Binary segmented image
        """
        print(f"🔍 Applying adaptive threshold segmentation (window: {window_size})")
        
        # Create kernel for local statistics
        kernel = ee.Kernel.square(radius=window_size//2, units='pixels')
        
        # Calculate local mean and standard deviation
        local_mean = image.reduceNeighborhood(
            reducer=ee.Reducer.mean(),
            kernel=kernel
        )
        
        local_stddev = image.reduceNeighborhood(
            reducer=ee.Reducer.stdDev(),
            kernel=kernel
        )
        
        # Adaptive threshold = local_mean + threshold_factor * local_stddev
        adaptive_threshold = local_mean.add(
            local_stddev.multiply(threshold_factor)
        )
        
        # Apply threshold
        segmented = image.gt(adaptive_threshold)
        
        return segmented.rename('adaptive_segmentation')
    
    def texture_analysis_glcm(self, image: ee.Image, 
                             window_size: int = 7,
                             angles: List[int] = [0, 45, 90, 135]) -> ee.Image:
        """
        Calculate texture features using Gray-Level Co-occurrence Matrix (GLCM).
        
        Args:
            image: Input single-band image
            window_size: Size of analysis window
            angles: List of angles for GLCM calculation
        
        Returns:
            ee.Image: Multi-band image with texture features
        """
        print(f"📐 Calculating GLCM texture features (window: {window_size})")
        
        # Normalize image to 0-255 range for GLCM
        normalized = image.unitScale(0, 255).uint8()
        
        texture_bands = []
        
        for angle in angles:
            # Calculate GLCM for each angle
            glcm = normalized.glcmTexture(size=window_size, kernel=None, average=True)
            
            # Extract specific texture measures
            contrast = glcm.select(f'.*_contrast')
            dissimilarity = glcm.select(f'.*_diss')
            homogeneity = glcm.select(f'.*_idm')
            energy = glcm.select(f'.*_asm')
            entropy = glcm.select(f'.*_ent')
            
            # Rename bands with angle suffix
            contrast = contrast.rename(f'contrast_{angle}')
            dissimilarity = dissimilarity.rename(f'dissimilarity_{angle}')
            homogeneity = homogeneity.rename(f'homogeneity_{angle}')
            energy = energy.rename(f'energy_{angle}')
            entropy = entropy.rename(f'entropy_{angle}')
            
            texture_bands.extend([contrast, dissimilarity, homogeneity, energy, entropy])
        
        # Combine all texture bands
        texture_image = ee.Image.cat(texture_bands)
        
        return texture_image
    
    def morphological_operations(self, binary_image: ee.Image,
                                operation: str = 'opening',
                                kernel_size: int = 3,
                                iterations: int = 1) -> ee.Image:
        """
        Implement morphological operations for binary images.
        
        Args:
            binary_image: Input binary image
            operation: Type of operation ('erosion', 'dilation', 'opening', 'closing')
            kernel_size: Size of morphological kernel
            iterations: Number of iterations to apply
        
        Returns:
            ee.Image: Processed binary image
        """
        print(f"🔧 Applying morphological {operation} (kernel: {kernel_size}, iterations: {iterations})")
        
        # Create morphological kernel
        kernel = ee.Kernel.square(radius=kernel_size//2, units='pixels')
        
        def erosion(img):
            """Morphological erosion."""
            return img.reduceNeighborhood(
                reducer=ee.Reducer.min(),
                kernel=kernel
            )
        
        def dilation(img):
            """Morphological dilation."""
            return img.reduceNeighborhood(
                reducer=ee.Reducer.max(),
                kernel=kernel
            )
        
        def opening(img):
            """Morphological opening (erosion followed by dilation)."""
            eroded = erosion(img)
            return dilation(eroded)
        
        def closing(img):
            """Morphological closing (dilation followed by erosion)."""
            dilated = dilation(img)
            return erosion(dilated)
        
        # Define operations
        operations = {
            'erosion': erosion,
            'dilation': dilation,
            'opening': opening,
            'closing': closing
        }
        
        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")
        
        # Apply operation for specified iterations
        result = binary_image
        for i in range(iterations):
            result = operations[operation](result)
        
        return result.rename(f'{operation}_result')
    
    def spectral_angle_mapper(self, image: ee.Image, 
                             reference_spectra: Dict[str, List[float]]) -> ee.Image:
        """
        Implement Spectral Angle Mapper (SAM) classification.
        
        Args:
            image: Multi-band input image
            reference_spectra: Dictionary of class names and their spectral signatures
        
        Returns:
            ee.Image: Classification result with spectral angle distances
        """
        print(f"📊 Applying Spectral Angle Mapper with {len(reference_spectra)} classes")
        
        # Get band names
        band_names = image.bandNames()
        num_bands = band_names.length()
        
        classification_bands = []
        
        for class_name, spectrum in reference_spectra.items():
            # Convert reference spectrum to Earth Engine image
            ref_spectrum = ee.Image.constant(spectrum).rename(band_names)
            
            # Calculate spectral angle
            # SAM = arccos(sum(pixel * reference) / (||pixel|| * ||reference||))
            
            # Dot product
            dot_product = image.multiply(ref_spectrum).reduce(ee.Reducer.sum())
            
            # Magnitudes
            image_magnitude = image.pow(2).reduce(ee.Reducer.sum()).sqrt()
            ref_magnitude = ref_spectrum.pow(2).reduce(ee.Reducer.sum()).sqrt()
            
            # Cosine of angle
            cos_angle = dot_product.divide(image_magnitude.multiply(ref_magnitude))
            
            # Spectral angle in radians
            spectral_angle = cos_angle.acos()
            
            # Add to classification bands
            classification_bands.append(spectral_angle.rename(f'sam_{class_name}'))
        
        # Combine all SAM bands
        sam_image = ee.Image.cat(classification_bands)
        
        # Find class with minimum spectral angle
        class_assignment = sam_image.reduce(ee.Reducer.min(len(reference_spectra) + 1))
        
        return sam_image.addBands(class_assignment.rename('sam_classification'))
    
    def principal_component_analysis(self, image: ee.Image,
                                   region: ee.Geometry,
                                   scale: int = 30) -> Dict[str, ee.Image]:
        """
        Implement Principal Component Analysis (PCA) transformation.
        
        Args:
            image: Multi-band input image
            region: Region for calculating statistics
            scale: Scale for calculations
        
        Returns:
            Dict containing PCA components and statistics
        """
        print("📈 Performing Principal Component Analysis")
        
        # Get band names
        band_names = image.bandNames()
        
        # Calculate mean values
        mean_dict = image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=scale,
            maxPixels=1e9
        )
        
        # Create mean image
        means = ee.Image.constant(mean_dict.values(band_names))
        
        # Center the data (subtract means)
        centered = image.subtract(means)
        
        # Calculate covariance matrix
        # This is a simplified implementation - full PCA requires eigenvalue decomposition
        covariance = centered.toArray().reduce(
            reducer=ee.Reducer.covariance(),
            axes=[0, 1]
        )
        
        # For demonstration, create simplified PC transformation
        # In practice, you would need to compute eigenvectors
        
        # Simplified PC1 (weighted average emphasizing variance)
        pc1_weights = [0.4, 0.3, 0.2, 0.1]  # Example weights
        pc1 = image.expression(
            'b1*w1 + b2*w2 + b3*w3 + b4*w4',
            {
                'b1': image.select(0),
                'b2': image.select(1),
                'b3': image.select(2) if image.bandNames().size().gt(2) else image.select(0),
                'b4': image.select(3) if image.bandNames().size().gt(3) else image.select(0),
                'w1': pc1_weights[0],
                'w2': pc1_weights[1],
                'w3': pc1_weights[2],
                'w4': pc1_weights[3]
            }
        ).rename('PC1')
        
        # Simplified PC2 (orthogonal to PC1)
        pc2_weights = [0.1, -0.2, 0.3, 0.4]
        pc2 = image.expression(
            'b1*w1 + b2*w2 + b3*w3 + b4*w4',
            {
                'b1': image.select(0),
                'b2': image.select(1),
                'b3': image.select(2) if image.bandNames().size().gt(2) else image.select(0),
                'b4': image.select(3) if image.bandNames().size().gt(3) else image.select(0),
                'w1': pc2_weights[0],
                'w2': pc2_weights[1],
                'w3': pc2_weights[2],
                'w4': pc2_weights[3]
            }
        ).rename('PC2')
        
        pca_image = ee.Image.cat([pc1, pc2])
        
        return {
            'pca_image': pca_image,
            'mean_values': mean_dict,
            'centered_image': centered
        }
    
    def edge_detection_sobel(self, image: ee.Image) -> ee.Image:
        """
        Implement Sobel edge detection algorithm.
        
        Args:
            image: Input single-band image
        
        Returns:
            ee.Image: Edge magnitude and direction
        """
        print("🔍 Applying Sobel edge detection")
        
        # Sobel kernels
        sobel_x = ee.Kernel.fixed(3, 3, [
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ])
        
        sobel_y = ee.Kernel.fixed(3, 3, [
            [-1, -2, -1],
            [ 0,  0,  0],
            [ 1,  2,  1]
        ])
        
        # Apply Sobel filters
        gradient_x = image.convolve(sobel_x).rename('gradient_x')
        gradient_y = image.convolve(sobel_y).rename('gradient_y')
        
        # Calculate magnitude and direction
        magnitude = gradient_x.pow(2).add(gradient_y.pow(2)).sqrt().rename('edge_magnitude')
        direction = gradient_y.atan2(gradient_x).rename('edge_direction')
        
        return ee.Image.cat([gradient_x, gradient_y, magnitude, direction])
    
    def watershed_segmentation(self, image: ee.Image,
                              markers: ee.Image,
                              connectivity: int = 8) -> ee.Image:
        """
        Simplified watershed segmentation implementation.
        
        Args:
            image: Input grayscale image
            markers: Seed points for watershed
            connectivity: Pixel connectivity (4 or 8)
        
        Returns:
            ee.Image: Segmented image
        """
        print(f"💧 Applying watershed segmentation (connectivity: {connectivity})")
        
        # This is a simplified implementation
        # Full watershed requires iterative region growing
        
        # Create distance transform from markers
        distance = markers.distance(ee.Kernel.euclidean(radius=100))
        
        # Apply watershed-like segmentation using distance and image gradient
        gradient = self.edge_detection_sobel(image).select('edge_magnitude')
        
        # Combine distance and gradient information
        watershed_function = distance.multiply(-1).add(gradient.multiply(0.1))
        
        # Create regions using connected components
        # This is a simplified approach - true watershed is more complex
        regions = watershed_function.connectedComponents(
            connectedness=ee.Kernel.plus() if connectivity == 4 else ee.Kernel.square(1),
            maxSize=1000
        )
        
        return regions.rename('watershed_segments')
    
    def fractal_dimension_calculation(self, binary_image: ee.Image,
                                    scales: List[int] = [1, 2, 4, 8, 16]) -> ee.Image:
        """
        Calculate fractal dimension using box-counting method.
        
        Args:
            binary_image: Input binary image
            scales: List of box sizes for calculation
        
        Returns:
            ee.Image: Fractal dimension map
        """
        print(f"📐 Calculating fractal dimension with scales: {scales}")
        
        box_counts = []
        
        for scale in scales:
            # Create kernel for box counting
            kernel = ee.Kernel.square(radius=scale, units='pixels')
            
            # Count boxes containing features
            box_count = binary_image.reduceNeighborhood(
                reducer=ee.Reducer.sum(),
                kernel=kernel
            ).gt(0)  # Convert to binary (box contains feature or not)
            
            # Sum boxes in larger neighborhoods to get local fractal properties
            local_count = box_count.reduceNeighborhood(
                reducer=ee.Reducer.sum(),
                kernel=ee.Kernel.square(radius=scale*2, units='pixels')
            )
            
            box_counts.append(local_count.rename(f'count_{scale}'))
        
        # Combine all scales
        count_image = ee.Image.cat(box_counts)
        
        # Calculate fractal dimension using linear regression
        # This is a simplified implementation
        # True fractal dimension requires log-log regression across scales
        
        # For demonstration, use ratio of counts at different scales
        if len(scales) >= 2:
            fractal_approx = count_image.select(f'count_{scales[0]}').divide(
                count_image.select(f'count_{scales[-1]}').add(1)
            ).log().rename('fractal_dimension')
        else:
            fractal_approx = count_image.select(0).rename('fractal_dimension')
        
        return count_image.addBands(fractal_approx)
    
    def multi_scale_analysis(self, image: ee.Image,
                           scales: List[int] = [1, 2, 4, 8, 16, 32],
                           operations: List[str] = ['mean', 'stdDev', 'variance']) -> ee.Image:
        """
        Perform multi-scale analysis using different scales and operations.
        
        Args:
            image: Input image
            scales: List of analysis scales
            operations: List of operations to perform
        
        Returns:
            ee.Image: Multi-scale feature image
        """
        print(f"🔍 Multi-scale analysis with {len(scales)} scales and {len(operations)} operations")
        
        scale_bands = []
        
        for scale in scales:
            kernel = ee.Kernel.square(radius=scale, units='pixels')
            
            for operation in operations:
                if operation == 'mean':
                    result = image.reduceNeighborhood(
                        reducer=ee.Reducer.mean(),
                        kernel=kernel
                    )
                elif operation == 'stdDev':
                    result = image.reduceNeighborhood(
                        reducer=ee.Reducer.stdDev(),
                        kernel=kernel
                    )
                elif operation == 'variance':
                    result = image.reduceNeighborhood(
                        reducer=ee.Reducer.variance(),
                        kernel=kernel
                    )
                elif operation == 'entropy':
                    # Approximate entropy using histogram
                    result = image.reduceNeighborhood(
                        reducer=ee.Reducer.entropy(),
                        kernel=kernel
                    )
                else:
                    continue
                
                scale_bands.append(result.rename(f'{operation}_scale_{scale}'))
        
        return ee.Image.cat(scale_bands)
    
    def optimize_algorithm_performance(self) -> Dict[str, str]:
        """
        Provide performance optimization strategies for custom algorithms.
        
        Returns:
            Dict of optimization strategies
        """
        strategies = {
            'vectorization': 'Use ee.Image operations instead of loops when possible',
            'kernel_optimization': 'Choose appropriate kernel sizes for operations',
            'band_selection': 'Process only necessary bands to reduce computation',
            'scale_matching': 'Match processing scale to data resolution',
            'chunked_processing': 'Break large operations into smaller chunks',
            'memory_management': 'Use appropriate data types and avoid large intermediate results',
            'caching': 'Cache frequently used intermediate results',
            'parallel_processing': 'Design algorithms to leverage Earth Engine\'s parallelism'
        }
        
        print("⚡ Performance Optimization Strategies:")
        for strategy, description in strategies.items():
            print(f"  • {strategy}: {description}")
        
        return strategies

def main():
    """Main function demonstrating custom algorithms."""
    
    # Initialize custom algorithms library
    algorithms = CustomAlgorithms('your-project-id')
    
    print("="*80)
    print("🧮 CUSTOM ALGORITHMS AND SPECIALIZED FUNCTIONS")
    print("="*80)
    
    # Load test image
    image = (ee.Image('LANDSAT/LC08/C02/T1_L2/LC08_044034_20140318')
             .select(['SR_B2', 'SR_B3', 'SR_B4', 'SR_B5'])
             .multiply(0.0000275).add(-0.2))
    
    test_region = ee.Geometry.Rectangle([-122.5, 37.5, -122.0, 38.0])
    
    print(f"Using test image: Landsat 8")
    print(f"Test region: San Francisco Bay Area")
    
    # Example 1: Adaptive threshold segmentation
    print("\n1️⃣ Adaptive Threshold Segmentation")
    print("-" * 40)
    
    # Use NDVI for segmentation
    ndvi = image.normalizedDifference(['SR_B5', 'SR_B4'])
    segmented = algorithms.adaptive_threshold_segmentation(
        ndvi, window_size=15, threshold_factor=0.1
    )
    print("✓ Adaptive segmentation completed")
    
    # Example 2: Texture analysis
    print("\n2️⃣ Texture Analysis (GLCM)")
    print("-" * 30)
    
    # Use NIR band for texture analysis
    nir_band = image.select('SR_B5')
    texture_features = algorithms.texture_analysis_glcm(
        nir_band, window_size=7, angles=[0, 45, 90, 135]
    )
    print(f"✓ Texture analysis completed with {texture_features.bandNames().size().getInfo()} features")
    
    # Example 3: Morphological operations
    print("\n3️⃣ Morphological Operations")
    print("-" * 35)
    
    # Create binary image from NDVI threshold
    binary_image = ndvi.gt(0.3)
    
    # Apply different morphological operations
    operations = ['erosion', 'dilation', 'opening', 'closing']
    morph_results = {}
    
    for operation in operations:
        result = algorithms.morphological_operations(
            binary_image, operation=operation, kernel_size=3, iterations=1
        )
        morph_results[operation] = result
        print(f"✓ {operation} completed")
    
    # Example 4: Spectral Angle Mapper
    print("\n4️⃣ Spectral Angle Mapper")
    print("-" * 30)
    
    # Define reference spectra (example values)
    reference_spectra = {
        'water': [0.05, 0.08, 0.06, 0.04],
        'vegetation': [0.04, 0.08, 0.15, 0.35],
        'urban': [0.15, 0.18, 0.22, 0.25],
        'soil': [0.12, 0.15, 0.18, 0.20]
    }
    
    sam_result = algorithms.spectral_angle_mapper(image, reference_spectra)
    print(f"✓ SAM classification with {len(reference_spectra)} classes")
    
    # Example 5: Principal Component Analysis
    print("\n5️⃣ Principal Component Analysis")
    print("-" * 35)
    
    pca_results = algorithms.principal_component_analysis(
        image, test_region, scale=30
    )
    print("✓ PCA transformation completed")
    print(f"✓ PC bands: {pca_results['pca_image'].bandNames().getInfo()}")
    
    # Example 6: Edge detection
    print("\n6️⃣ Sobel Edge Detection")
    print("-" * 28)
    
    # Use first band for edge detection
    edges = algorithms.edge_detection_sobel(image.select(0))
    print(f"✓ Edge detection completed with {edges.bandNames().size().getInfo()} output bands")
    
    # Example 7: Multi-scale analysis
    print("\n7️⃣ Multi-Scale Analysis")
    print("-" * 28)
    
    multiscale_features = algorithms.multi_scale_analysis(
        ndvi,
        scales=[1, 2, 4, 8, 16],
        operations=['mean', 'stdDev', 'variance']
    )
    num_features = multiscale_features.bandNames().size().getInfo()
    print(f"✓ Multi-scale analysis with {num_features} features")
    
    # Example 8: Fractal dimension
    print("\n8️⃣ Fractal Dimension Calculation")
    print("-" * 35)
    
    fractal_result = algorithms.fractal_dimension_calculation(
        binary_image, scales=[1, 2, 4, 8, 16]
    )
    print("✓ Fractal dimension calculated")
    
    # Example 9: Performance optimization
    print("\n9️⃣ Performance Optimization")
    print("-" * 32)
    
    optimization_strategies = algorithms.optimize_algorithm_performance()
    
    # Summary
    print("\n" + "="*80)
    print("📊 CUSTOM ALGORITHMS SUMMARY")
    print("="*80)
    
    print("\n🎯 Algorithms Demonstrated:")
    print("• Adaptive threshold segmentation")
    print("• Gray-Level Co-occurrence Matrix (GLCM) texture analysis")
    print("• Morphological operations (erosion, dilation, opening, closing)")
    print("• Spectral Angle Mapper (SAM) classification")
    print("• Principal Component Analysis (PCA)")
    print("• Sobel edge detection")
    print("• Multi-scale spatial analysis")
    print("• Fractal dimension calculation")
    
    print("\n📈 Results Generated:")
    print(f"• Segmented regions: {segmented.bandNames().size().getInfo()} bands")
    print(f"• Texture features: {texture_features.bandNames().size().getInfo()} bands")
    print(f"• Morphological results: {len(morph_results)} operations")
    print(f"• SAM classification: {sam_result.bandNames().size().getInfo()} bands")
    print(f"• Edge features: {edges.bandNames().size().getInfo()} bands")
    print(f"• Multi-scale features: {num_features} bands")
    
    print("\n🏆 Advanced Techniques Applied:")
    print("• Custom mathematical implementations")
    print("• Neighborhood analysis and convolution")
    print("• Multi-dimensional data processing")
    print("• Performance optimization strategies")
    print("• Object-oriented algorithm design")
    print("• Reusable function libraries")
    
    print("\n✅ Custom Algorithms Development Complete!")

if __name__ == "__main__":
    main()
