# TreeSeg-Analysis
Automated TLS/LiDAR pipeline for segmenting individually tagged trees and extracting structural (QSM, voxelization), growth (height, DBH, crown metrics), and power-line clearance metrics across multi-year scans

# Test data
A sample block from the Saint-Bruno-de-Montarville plantation is provided to test the pipeline end-to-end.

# Pipeline
1. Pre-processing / Segmentation: Ground removal, noise filtering, per-tree isolation [segmentation.ipynb]
2. Intra-year Alignment: ICP co-registration for growth detection between years [alignement.py]
3. Structural analysis & Report: Per-tree HTML report (voxelization, growth, clearance, crown metrics, etc) [tree_analysis_template.Rmd]
4. Batch Report Generation: Runs the analysis template across all trees [Generate_All_Reports.R]
5. Report Index: Builds an HTML index linking all individual tree reports [create_index.Rmd]
6. Excel Export: Converts the CSV/HTML outputs into Excel format [ExcelGeneration.py]

# Requirements
Python 3.x (laspy, Open3D, scikit-learn, scipy)

R (lidR, VoxR, ITSMe, AdTree QSM, ArchiQSM)

# Full instructions
See InstructionsEnglish.docx for detailed setup and usage steps.

# Authors
- Loïc Charlebois (loiccv123@gmail.com)
- Annick St-Denis (st-denis.annick@uqam.ca)

# Project License
- MIT license

