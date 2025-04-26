# README: NV Center Detection in Diamond FSM Scans

## Overview

This project provides a robust, automated pipeline for detecting and visualizing Nitrogen-Vacancy (NV) centers in diamonds using Fluorescence Scanning Microscopy (FSM) data. It used test data from Argonne National Lab and includes Python scripts and a GUI for:

- Loading FSM scan data (JSON format)
- Detecting NV centers via adaptive image processing
- Visualizing results and detected centers
- Batch processing and graphical comparison of multiple scans

The workflow is designed for researchers working with diamond NV centers, enabling rapid, reproducible analysis of large FSM datasets.

---

## Project Structure

```
.
├── DemoNotebook.ipynb         # Example Jupyter notebook for data exploration
├── nv_center_detection.py     # Main detection and visualization script
├── gui.py                     # User-friendly graphical interface
├── data/
│   ├── fsmScan040725_190307final.json
│   ├── fsmScan040725_194501final.json
│   ├── fsmScan040825_105623final.json
│   └── ... (additional FSM JSON files)
├── results/
│   └── ... (output plots and analysis)
└── README.md                  # This file
```

---

## Data Format

Each FSM scan is stored as a JSON file with the following structure:

- **params**: Scan metadata (center, sweep ranges, resolution, collects per point, laser power)
- **datasets**:
  - `xSteps`, `ySteps`: 1D arrays of scan coordinates (in microns)
  - `ScanCounts`: 2D array of photon count rates (counts/s) for each (x, y) position

Example:
```json
{
  "params": {
    "CenterOfScan": [0.0, 0.0],
    "sweepRanges": [30.0, 30.0],
    "scanPointsPerAxis": [180, 180],
    "collectsPerPt": 100,
    "LaserPower": 0.01
  },
  "datasets": {
    "xSteps": [...],
    "ySteps": [...],
    "ScanCounts": [...]
  }
}
```

---

## NV Center Detection Algorithm

**Type:** Local maxima detection with noise reduction and adaptive thresholding.

**How it works:**
1. **Load Data:** Reads FSM scan JSON, extracts scan grid and photon counts.
2. **Noise Reduction:** Applies Gaussian smoothing to suppress noise while preserving NV center signals.
3. **Adaptive Thresholding:** Sets a dynamic threshold based on image mean and standard deviation.
4. **Peak Detection:** Identifies local maxima (potential NV centers) above the threshold, ensuring spatial separation.
5. **Result Mapping:** Converts detected pixel coordinates to physical positions (microns).

---

## Usage

### Notebook

- Use `DemoNotebook.ipynb` for interactive exploration, loading data, and visualizing scans.

### Command-Line/Script

1. Place your FSM JSON files in the `data/` directory.
2. Run the main script:
   ```bash
   python nv_center_detection.py
   ```
   - Adjust parameters (threshold factor, minimum distance) as needed.

### GUI

- Launch the GUI:
  ```bash
  python gui.py
  ```
- Select FSM scan files and output directory.
- Set detection parameters and run the analysis.
- Visual and numerical results are saved in the `results/` directory.

---

## Visualization

- **Single Scan:** Detected NV centers are overlaid as circles on the fluorescence image.
- **Multi-Scan Comparison:** Side-by-side panels for each scan, each showing detected centers.
- **Overlay Plot:** All detected NV positions from multiple scans plotted together.
- **Intensity Analysis:** Histogram of NV center intensities.

Example output (NV centers marked in cyan):

![FSM Scan Example 1][6]
![FSM Scan Example 2][7]
![FSM Scan Example 3][8]
![FSM Scan Example 4][9]

---

## Parameter Tuning

- **Threshold Factor:** Controls sensitivity (higher = fewer, more confident detections).
- **Min Distance:** Minimum separation (in pixels) between detected NV centers.
- **Gaussian Sigma:** Smoothing strength; adjust if noise or spot size changes.

---

## Requirements

- Python 3.7+
- NumPy
- Matplotlib
- SciPy
- scikit-image
- tkinter (for GUI)
- (Optional) Jupyter Notebook

Install dependencies with:
```bash
pip install numpy matplotlib scipy scikit-image
```

---

## Troubleshooting

- **No NV centers detected:** Lower the threshold factor or check scan quality.
- **Too many false positives:** Increase threshold factor or min distance.
- **GUI not showing:** Ensure `tkinter` is installed and run from a local terminal.

---

## License

MIT License

---

## Acknowledgments

- Data and scan descriptions provided by the research team.
- Algorithm inspired by standard practices in single-molecule localization microscopy.

---

## Contact

For questions or contributions, please open an issue or contact the project maintainer.

---[6]: https://pplx-res.cloudinary.com/image/private/user_uploads/vdxnzXzhBCloOkj/fig_041025_190714.jpg[7]: https://pplx-res.cloudinary.com/image/private/user_uploads/SRymVxtkwDbpMWY/fig_040725_194501.jpg[8]: https://pplx-res.cloudinary.com/image/private/user_uploads/ynJiLTRrOebedil/fig_040825_105623.jpg[9]: https://pplx-res.cloudinary.com/image/private/user_uploads/aUVTyEkcBlykHCj/fig_040725_190307.jpg

Citations:
[1] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/64999561/d7c0d08e-09f9-41a8-8ed6-b9c3b83192a8/DemoNotebook.ipynb
[2] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/64999561/30f62f81-678e-4ec5-9108-dfea51138c32/fsmScan040725_190307final.json
[3] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/64999561/597893f4-18d5-416c-b3b6-4e1831b0df90/fsmScan040825_105623final.json
[4] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/64999561/455ec74b-a98b-40e5-bdec-f861c8712ee5/fsmScan040725_194501final.json
[5] https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/64999561/b0f5cc36-ead0-4cbb-a406-f5fd68cfa0e9/fsmScan041025_190714final.json
[6] https://pplx-res.cloudinary.com/image/private/user_uploads/vdxnzXzhBCloOkj/fig_041025_190714.jpg
[7] https://pplx-res.cloudinary.com/image/private/user_uploads/SRymVxtkwDbpMWY/fig_040725_194501.jpg
[8] https://pplx-res.cloudinary.com/image/private/user_uploads/ynJiLTRrOebedil/fig_040825_105623.jpg
[9] https://pplx-res.cloudinary.com/image/private/user_uploads/aUVTyEkcBlykHCj/fig_040725_190307.jpg

---
Answer from Perplexity: pplx.ai/share
