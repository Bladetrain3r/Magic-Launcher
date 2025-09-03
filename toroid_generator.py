import numpy as np
from math import sin, cos, pi

def generate_4d_toroid_points(point_count, major_radius=2.0, minor_radius=1.0, distribution='fibonacci'):
    """Generate points on a 4D toroid (4-torus)
    
    Args:
        point_count (int): Number of points to generate
        major_radius (float): Major radius of the toroid
        minor_radius (float): Minor radius of the toroid
        distribution (str): Distribution type ('fibonacci', 'grid', 'random')
        
    Returns:
        numpy.ndarray: 4D points array of shape (point_count, 4)
    """
    if distribution == 'fibonacci':
        return _generate_fibonacci_toroid(point_count, major_radius, minor_radius)
    elif distribution == 'grid':
        return _generate_grid_toroid(point_count, major_radius, minor_radius)
    else:  # Default to random
        return _generate_random_toroid(point_count, major_radius, minor_radius)

def _generate_fibonacci_toroid(point_count, major_radius, minor_radius):
    """Generate a 4D toroid using Fibonacci spiral distribution"""
    # Use golden ratio for optimal point distribution
    golden_ratio = (1 + np.sqrt(5)) * 2
    
    # Create indices array
    indices = np.arange(point_count)
    
    # Generate 4 angles using Fibonacci spiral
    # These will be evenly distributed
    theta1 = 2 * np.pi * (indices / golden_ratio % 1)
    theta2 = 2 * np.pi * ((indices * golden_ratio) / golden_ratio % 1)
    theta3 = 2 * np.pi * ((indices * golden_ratio**2) / golden_ratio % 1)
    theta4 = 2 * np.pi * ((indices * golden_ratio**3) / golden_ratio % 1)
    
    # Parameterize based on the 4-torus equations
    # First create the two circular components
    circle1_x = (major_radius + minor_radius * np.cos(theta3)) * np.cos(theta1)
    circle1_y = (major_radius + minor_radius * np.cos(theta3)) * np.sin(theta1)
    circle2_x = (major_radius + minor_radius * np.sin(theta3)) * np.cos(theta2)
    circle2_y = (major_radius + minor_radius * np.sin(theta3)) * np.sin(theta2)
    
    # Create the 4D points array
    points_4d = np.column_stack([
        circle1_x,
        circle1_y,
        circle2_x,
        circle2_y
    ]).astype(np.float32)
    
    # Normalize to unit scale (important for consistent w-coordinate mapping)
    max_val = np.max(np.abs(points_4d))
    points_4d = points_4d / max_val
    
    return points_4d

def _generate_grid_toroid(point_count, major_radius, minor_radius):
    """Generate a 4D toroid using a grid distribution"""
    # Calculate how many points per dimension to get close to point_count
    points_per_dim = int(np.power(point_count, 1/4)) + 1
    
    # Create evenly spaced grid for 4 angles
    theta_values = np.linspace(0, 2*np.pi, points_per_dim, endpoint=False)
    
    # Initialize array for points
    points_4d = []
    
    # Generate points using nested loops
    for theta1 in theta_values:
        for theta2 in theta_values:
            for theta3 in theta_values:
                for theta4 in theta_values:
                    # Parameterize based on the 4-torus equations
                    # Change multipliers for different grid patterns
                    x = (major_radius + minor_radius * np.cos(theta3)) * np.cos(theta1)
                    y = (major_radius + minor_radius * np.cos(theta3)) * np.sin(theta1)
                    z = (major_radius + minor_radius * np.sin(theta3)) * np.cos(theta2)
                    w = (major_radius + minor_radius * np.sin(theta3)) * 2 * np.sin(theta2)
                    
                    # Add point to array
                    points_4d.append([x, y, z, w])
                    
                    # Break if we've reached target point count
                    if len(points_4d) >= point_count:
                        break
                if len(points_4d) >= point_count:
                    break
            if len(points_4d) >= point_count:
                break
        if len(points_4d) >= point_count:
            break
    
    # Convert to numpy array
    points_4d = np.array(points_4d, dtype=np.float32)
    
    # Normalize to unit scale
    max_val = np.max(np.abs(points_4d))
    points_4d = points_4d / max_val
    
    return points_4d[:point_count]

def _generate_random_toroid(point_count, major_radius, minor_radius):
    """Generate a 4D toroid using random distribution"""
    # Generate 4 random angles
    theta1 = np.random.random(point_count) * 2 * np.pi
    theta2 = np.random.random(point_count) * 2 * np.pi
    theta3 = np.random.random(point_count) * 2 * np.pi
    theta4 = np.random.random(point_count) * 2 * np.pi
    
    # Parameterize based on the 4-torus equations
    x = (major_radius + minor_radius * np.cos(theta3)) * np.cos(theta1)
    y = (major_radius + minor_radius * np.cos(theta3)) * np.sin(theta1)
    z = (major_radius + minor_radius * np.sin(theta3)) * np.cos(theta2)
    w = (major_radius + minor_radius * np.sin(theta3)) * np.sin(theta2)
    
    # Create points array
    points_4d = np.column_stack([x, y, z, w]).astype(np.float32)
    
    # Normalize to unit scale
    max_val = np.max(np.abs(points_4d))
    points_4d = points_4d / max_val
    
    return points_4d

def project_4d_toroid(points_4d, w_angle, color_depth=8, color_gradient=None, zoom_factor=2.0):
    """Project 4D toroid points to 3D with colors
    
    Args:
        points_4d (numpy.ndarray): 4D points to project
        w_angle (float): Rotation angle in w dimension
        color_depth (int): Color bit depth
        color_gradient (dict): Color gradient configuration
        zoom_factor (float): Zoom factor
        
    Returns:
        tuple: (points_3d, colors) arrays
    """
    # Extract components
    x4, y4, z4, w4 = points_4d[:, 0], points_4d[:, 1], points_4d[:, 2], points_4d[:, 3]
    
    # 4D rotation matrices for multiple planes
    # Rotate in the x-w plane
    cos_w, sin_w = np.cos(w_angle), np.sin(w_angle)
    rotated_w4 = w4 * cos_w - x4 * sin_w
    rotated_x4 = w4 * sin_w + x4 * cos_w
    
    # Rotate in the y-z plane for interesting effects
    cos_yz, sin_yz = np.cos(w_angle/2), np.sin(w_angle/2)
    rotated_y4 = y4 * cos_yz - z4 * sin_yz
    rotated_z4 = y4 * sin_yz + z4 * cos_yz
    
    # Apply projection factor
    factor = 1.25
    
    # Apply projection
    points_3d = np.column_stack([
        rotated_x4 * factor,
        rotated_y4 * factor,
        rotated_z4 * factor
    ])
    
    # Default color gradient if none provided
    if color_gradient is None:
        color_gradient = {
            'low': [0, 0, 255],  # Blue
            'high': [255, 0, 0]  # Red
        }
    
    # Color interpolation
    max_color_value = 2**color_depth - 1
    t = (rotated_w4 + 1) / 2  # Normalize to [0,1]
    
    # Apply zoom influence
    zoom_influence = (zoom_factor - 2.0) / 3.0
    zoom_influence = np.clip(zoom_influence, 0, 1)
    t_modified = t * (1 + zoom_influence)
    t_modified = np.clip(t_modified, 0, 1)
    
    # Create color arrays
    low = np.array(color_gradient['low']) / max_color_value
    high = np.array(color_gradient['high']) / max_color_value
    
    # Calculate colors
    colors = np.outer(1-t_modified, low) + np.outer(t_modified, high)
    
    return points_3d, colors

# Integration with HyperspherePipeline
def integrate_4d_toroid(hypersphere_pipeline, major_radius=2.0, minor_radius=1.0, distribution='fibonacci'):
    """Replace hypersphere points with toroid points in the pipeline
    
    Args:
        hypersphere_pipeline: The HyperspherePipeline instance
        major_radius (float): Major radius of the toroid
        minor_radius (float): Minor radius of the toroid
        distribution (str): Distribution type
        
    Returns:
        The modified pipeline
    """
    # Generate toroid points
    toroid_points = generate_4d_toroid_points(
        hypersphere_pipeline.point_count, 
        major_radius, 
        minor_radius, 
        distribution
    )
    
    # Replace the points in shared memory
    shared_points = np.ndarray(
        hypersphere_pipeline.points_4d.shape, 
        dtype=hypersphere_pipeline.points_4d.dtype, 
        buffer=hypersphere_pipeline.points_shm.buf
    )
    
    # Copy new points to shared memory
    np.copyto(shared_points, toroid_points)
    
    # Replace the projection function
    original_projection = hypersphere_pipeline.project_4d_to_3d_optimized
    
    @staticmethod
    def toroid_projection(points_4d, w_angle, color_depth, color_gradient, zoom_factor):
        return project_4d_toroid(points_4d, w_angle, color_depth, color_gradient, zoom_factor)
    
    # Update the projection method
    hypersphere_pipeline.project_4d_to_3d_optimized = toroid_projection
    
    return hypersphere_pipeline