# TreeSeg-Analysis
Automated TLS/LiDAR pipeline for segmenting individually tagged trees and extracting structural (QSM, voxelization), growth (height, DBH, crown metrics), and power-line clearance metrics across multi-year scans

# Test data
A sample block from the Saint-Bruno-de-Montarville plantation is provided to test the pipeline end-to-end.

# Pipeline
1. PreProcessing / Alignement: Metashape Pro
2. Tree Block Processing / Segmentation: Ground removal, noise filtering, per-tree isolation [segmentation.ipynb]
3. Intra-year Alignment: ICP co-registration for growth detection between years [alignement.py]
4. Structural analysis & Report: Per-tree HTML report (voxelization, growth, clearance, crown metrics, etc) [tree_analysis_template.Rmd]
5. Batch Report Generation: Runs the analysis template across all trees [Generate_All_Reports.R]
6. Report Index: Builds an HTML index linking all individual tree reports [create_index.Rmd]
7. Excel Export: Converts the CSV/HTML outputs into Excel format [ExcelGeneration.py]

# Requirements

- Python 3.10 (laspy, Open3D, scikit-learn, scipy)

- R 
    - lidR (https://r-lidar.github.io/lidRbook/)
    - VoxR (https://github.com/Blecigne/VoxR)
    - ITSMe (https://lmterryn.github.io/ITSMe/)
    - ArchiQSM (https://github.com/umr-amap/aRchi)

- For QSM generation - AdTree executable (https://github.com/tudelft3d/AdTree)
  
- If Raw TLS scan Alignement is required for your usecase, Agisoft Metashape Pro 2.3.1 (https://www.agisoft.com/downloads/installer/)
  
- CloudCompare for visualisation (https://www.cloudcompare.org/release/)

# Full instructions
See InstructionsEnglish.docx for detailed setup and usage steps.

# Authors
- Loïc Charlebois (loiccv123@gmail.com)
- Annick St-Denis (st-denis.annick@uqam.ca)

# Project License
- MIT license

