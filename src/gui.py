import numpy as np
import matplotlib.pyplot as plt
import json
from scipy import ndimage
from skimage.feature import peak_local_max
from matplotlib.patches import Circle
import os
import warnings

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
    
    # Check if data is not empty or all NaN
    if scan_counts.size == 0 or np.all(np.isnan(scan_counts)):
        # Return empty results with valid structure
        return {
            'coordinates': np.array([]).reshape(0, 2),
            'x_positions': np.array([]),
            'y_positions': np.array([]),
            'intensities': np.array([]),
            'processed_image': scan_counts,
            'threshold': 0
        }
    
    # Safely calculate mean and std
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Mean of empty slice')
        warnings.filterwarnings('ignore', message='invalid value encountered in scalar divide')
        warnings.filterwarnings('ignore', message='invalid value encountered in true_divide')
        mean_count = np.nanmean(scan_counts)
        std_count = np.nanstd(scan_counts)
    
    # Fallback if mean or std are NaN
    if np.isnan(mean_count) or np.isnan(std_count):
        mean_count = 0
        std_count = 0
    
    if min_peak_height is None:
        threshold = mean_count + threshold_factor * std_count
    else:
        threshold = min_peak_height
    
    # Apply Gaussian blur to reduce noise
    smoothed = ndimage.gaussian_filter(scan_counts, sigma=1)
    
    # Find local peaks (with checks for empty data)
    if threshold <= 0 or not np.any(smoothed > threshold):
        # No peaks found
        coordinates = np.array([]).reshape(0, 2)
    else:
        coordinates = peak_local_max(smoothed, min_distance=min_distance, threshold_abs=threshold)
    
    # Handle empty coordinates case
    if len(coordinates) == 0:
        return {
            'coordinates': np.array([]).reshape(0, 2),
            'x_positions': np.array([]),
            'y_positions': np.array([]),
            'intensities': np.array([]),
            'processed_image': smoothed,
            'threshold': threshold
        }
    
    # Map coordinates to actual positions
    y_indices = coordinates[:, 0]
    x_indices = coordinates[:, 1]
    
    # Calculate actual positions in microns
    x_positions = np.interp(x_indices, np.arange(len(x_steps)), x_steps)
    y_positions = np.interp(y_indices, np.arange(len(y_steps)), y_steps)
    
    # Get intensity values at the peaks
    intensities = [scan_counts[y, x] for y, x in coordinates]
    
    return {
        'coordinates': coordinates,
        'x_positions': x_positions,
        'y_positions': y_positions,
        'intensities': intensities,
        'processed_image': smoothed,
        'threshold': threshold
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
    if len(results["coordinates"]) > 0:
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
    
    # Suppress the specific NumPy warnings globally
    warnings.filterwarnings('ignore', message='Mean of empty slice')
    warnings.filterwarnings('ignore', message='invalid value encountered in scalar divide')
    warnings.filterwarnings('ignore', message='invalid value encountered in true_divide')
    
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

# GUI Application
if __name__ == "__main__":
    import tkinter as tk
    from tkinter import filedialog, ttk
    
    def select_files():
        file_paths = filedialog.askopenfilenames(
            title="Select FSM JSON Files",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_paths:
            file_listbox.delete(0, tk.END)
            for path in file_paths:
                file_listbox.insert(tk.END, path)
            
    def select_output_dir():
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if output_dir:
            output_dir_var.set(output_dir)
    
    def run_analysis():
        file_paths = list(file_listbox.get(0, tk.END))
        output_dir = output_dir_var.get()
        
        if not file_paths:
            status_var.set("Error: No files selected")
            return
        
        # Update UI
        status_var.set("Processing...")
        root.update_idletasks()
        
        # Get parameters
        threshold_factor = float(threshold_factor_var.get())
        min_distance = int(min_distance_var.get())
        
        try:
            # Run processing
            results = process_fsm_files(
                file_paths,
                output_dir=output_dir if output_dir else None,
                threshold_factor=threshold_factor,
                min_distance=min_distance
            )
            
            # Create comparison plots if output directory is provided
            if len(file_paths) > 0 and output_dir:
                create_comparison_plot(file_paths, results, 
                                     os.path.join(output_dir, "comparison_plot.png"))
                create_overlay_plot(file_paths, results, 
                                   os.path.join(output_dir, "overlay_plot.png"))
                create_intensity_analysis(file_paths, results, 
                                         os.path.join(output_dir, "intensity_analysis.png"))
            
            status_var.set(f"Processing complete. Detected centers in {len(file_paths)} files.")
        except Exception as e:
            status_var.set(f"Error: {str(e)}")
    
    # Create the main window
    root = tk.Tk()
    root.title("NV Center Detection Tool")
    root.geometry("700x600")
    
    # Set variables
    output_dir_var = tk.StringVar()
    status_var = tk.StringVar(value="Ready")
    threshold_factor_var = tk.StringVar(value="2.5")
    min_distance_var = tk.StringVar(value="10")
    
    # Create main frame
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create file selection section
    file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="5")
    file_frame.pack(fill=tk.X, pady=5)
    
    select_button = ttk.Button(file_frame, text="Select Files", command=select_files)
    select_button.pack(side=tk.LEFT, padx=5)
    
    file_scroll = ttk.Scrollbar(file_frame)
    file_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    file_listbox = tk.Listbox(file_frame, height=5, width=50, yscrollcommand=file_scroll.set)
    file_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    file_scroll.config(command=file_listbox.yview)
    
    # Create output directory section
    output_frame = ttk.LabelFrame(main_frame, text="Output Directory", padding="5")
    output_frame.pack(fill=tk.X, pady=5)
    
    output_entry = ttk.Entry(output_frame, textvariable=output_dir_var, width=50)
    output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    output_button = ttk.Button(output_frame, text="Browse", command=select_output_dir)
    output_button.pack(side=tk.RIGHT, padx=5)
    
    # Create parameters section
    param_frame = ttk.LabelFrame(main_frame, text="Parameters", padding="5")
    param_frame.pack(fill=tk.X, pady=5)
    
    # Threshold factor
    ttk.Label(param_frame, text="Threshold Factor:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(param_frame, textvariable=threshold_factor_var, width=10).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
    
    # Min distance
    ttk.Label(param_frame, text="Minimum Distance:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
    ttk.Entry(param_frame, textvariable=min_distance_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
    
    # Create run section
    run_frame = ttk.Frame(main_frame)
    run_frame.pack(fill=tk.X, pady=10)
    
    run_button = ttk.Button(run_frame, text="Run Analysis", command=run_analysis)
    run_button.pack(padx=5, pady=5)
    
    # Status bar
    status_bar = ttk.Label(main_frame, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Start the application
    root.mainloop()
