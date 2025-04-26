import numpy as np
import matplotlib.pyplot as plt
import json
from scipy import ndimage
from skimage.feature import peak_local_max
from matplotlib.patches import Circle
import os

def loadJson(filename):
    """Load a JSON file and return the data dictionary"""
    with open(filename) as f:
        dataDict = json.load(f)
    return dataDict

def detect_nv_centers(data, threshold_factor=2.0, min_distance=5, min_peak_height=None):
    """Detect NV centers in FSM scan data"""
    # Extract scan data
    scan_counts = np.array(data['datasets']['ScanCounts'])
    x_steps = np.array(data['datasets']['xSteps'])
    y_steps = np.array(data['datasets']['ySteps'])
    
    # Calculate threshold based on mean and standard deviation
    mean_count = np.mean(scan_counts)
    std_count = np.std(scan_counts)
    if min_peak_height is None:
        threshold = mean_count + threshold_factor * std_count
    else:
        threshold = min_peak_height
    
    # Apply Gaussian blur to reduce noise
    smoothed = ndimage.gaussian_filter(scan_counts, sigma=1)
    
    # Find local peaks
    coordinates = peak_local_max(smoothed, min_distance=min_distance, threshold_abs=threshold)
    
    # Map coordinates to actual positions
    y_indices = coordinates[:, 0]
    x_indices = coordinates[:, 1]
    
    # Calculate actual positions in microns
    x_positions = np.interp(x_indices, np.arange(len(x_steps)), x_steps)
    y_positions = np.interp(y_indices, np.arange(len(y_steps)), y_steps)
    
    # Get intensity values at the peaks
    intensities = [scan_counts[y, x] for y, x in coordinates]
    
    return {
        'coordinates': coordinates,  # Pixel coordinates [y, x]
        'x_positions': x_positions,  # Actual x positions in microns
        'y_positions': y_positions,  # Actual y positions in microns
        'intensities': intensities,  # Intensity values at the peaks
        'processed_image': smoothed,  # Processed image
        'threshold': threshold       # Used threshold value
    }

def visualize_results(data, results, output_path=None):
    """Visualize the detection results"""
    scan_counts = np.array(data['datasets']['ScanCounts'])
    x_steps = np.array(data['datasets']['xSteps'])
    y_steps = np.array(data['datasets']['ySteps'])
    threshold = results['threshold']
    smoothed = results['processed_image']
    
    # Set up the figure
    fig = plt.figure(figsize=(15, 10))
    
    # Plot original scan
    ax1 = fig.add_subplot(231)
    im1 = ax1.imshow(scan_counts, cmap='hot', 
                   extent=[min(x_steps), max(x_steps), min(y_steps), max(y_steps)])
    plt.colorbar(im1, ax=ax1, label='Counts/s')
    ax1.set_title('Original FSM Scan')
    ax1.set_xlabel('X Position (μm)')
    ax1.set_ylabel('Y Position (μm)')
    
    # Plot smoothed scan
    ax2 = fig.add_subplot(232)
    im2 = ax2.imshow(smoothed, cmap='hot', 
                   extent=[min(x_steps), max(x_steps), min(y_steps), max(y_steps)])
    plt.colorbar(im2, ax=ax2, label='Counts/s (smoothed)')
    ax2.set_title('Smoothed Scan')
    ax2.set_xlabel('X Position (μm)')
    ax2.set_ylabel('Y Position (μm)')
    
    # Plot threshold mask
    ax3 = fig.add_subplot(233)
    mask = smoothed > threshold
    im3 = ax3.imshow(mask, cmap='gray', 
                   extent=[min(x_steps), max(x_steps), min(y_steps), max(y_steps)])
    ax3.set_title(f'Threshold Mask (>{threshold:.1f} counts/s)')
    ax3.set_xlabel('X Position (μm)')
    ax3.set_ylabel('Y Position (μm)')
    
    # Plot detected NV centers on original scan
    ax4 = fig.add_subplot(234)
    im4 = ax4.imshow(scan_counts, cmap='hot', 
                   extent=[min(x_steps), max(x_steps), min(y_steps), max(y_steps)])
    plt.colorbar(im4, ax=ax4, label='Counts/s')
    ax4.set_title(f'Detected NV Centers: {len(results["coordinates"])}')
    ax4.set_xlabel('X Position (μm)')
    ax4.set_ylabel('Y Position (μm)')
    
    # Plot markers at NV centers
    ax4.scatter(results['x_positions'], results['y_positions'], 
              s=50, facecolors='none', edgecolors='red')
    
    # Plot 3D surface of the scan
    ax5 = fig.add_subplot(235, projection='3d')
    X, Y = np.meshgrid(x_steps, y_steps)
    ax5.plot_surface(X, Y, scan_counts, cmap='hot', linewidth=0, antialiased=True)
    ax5.set_title('3D Surface Plot')
    ax5.set_xlabel('X Position (μm)')
    ax5.set_ylabel('Y Position (μm)')
    ax5.set_zlabel('Counts/s')
    
    # Plot intensity histogram with threshold
    ax6 = fig.add_subplot(236)
    ax6.hist(scan_counts.flatten(), bins=50, alpha=0.7, color='blue')
    ax6.axvline(x=threshold, color='red', linestyle='--', 
               label=f'Threshold: {threshold:.1f}')
    ax6.set_title('Intensity Histogram')
    ax6.set_xlabel('Counts/s')
    ax6.set_ylabel('Frequency')
    ax6.legend()
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300)
        plt.close()
    else:
        plt.show()

def process_fsm_files(file_paths, output_dir=None, **kwargs):
    """Process multiple FSM JSON files"""
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    all_results = []
    
    for idx, file_path in enumerate(file_paths):
        print(f"Processing file {idx+1}/{len(file_paths)}: {os.path.basename(file_path)}")
        
        try:
            # Load data
            data = loadJson(file_path)
            
            # Extract basic info
            params = data['params']
            print(f"  Scan center: {params.get('CenterOfScan', 'N/A')}")
            print(f"  Sweep ranges: {params.get('sweepRanges', 'N/A')} μm")
            print(f"  Resolution: {params.get('scanPointsPerAxis', 'N/A')} points")
            
            # Detect NV centers
            results = detect_nv_centers(data, **kwargs)
            all_results.append(results)
            
            print(f"  Detected {len(results['coordinates'])} potential NV centers")
            
            # Visualize and save results if output directory is provided
            if output_dir:
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                visualize_results(data, results, 
                                os.path.join(output_dir, f"{base_name}_results.png"))
            else:
                visualize_results(data, results)
            
        except Exception as e:
            print(f"  Error processing file: {e}")
        
        print("-" * 50)
    
    return all_results

# Example usage
if __name__ == "__main__":
    # Replace with actual paths to your JSON files
    file_paths = [
        # Path goes here
    ]
    
    results = process_fsm_files(
        file_paths,
        output_dir="nv_detection_results",
        threshold_factor=2.5,
        min_distance=10
    )
