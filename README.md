# TreeSeg-Analysis
Automated TLS/LiDAR pipeline for segmenting individually tagged trees and extracting structural (QSM, voxelization), growth (height, DBH, crown metrics), and power-line clearance metrics across multi-year scans

# Test data

A sample block from the Saint-Bruno-de-Montarville plantation is provided to test the pipeline end-to-end.

# Pipelin
e
1. Pre-processing / segmentationsegmentation.ipynbGround removal, noise filtering, per-tree isolation
2. Intra-year alignmentalignement.pyICP co-registration for growth detection between years
3. Structural analysis & reporttree_analysis_template.RmdPer-tree HTML report (voxelization, growth, clearance, crown metrics)
4. Batch report generationGenerate_All_Reports.Runs the analysis template across all trees
5. Report indexcreate_index.RmdBuilds an HTML index linking all individual tree reports6. Excel exportExcelGeneration.pyConverts the CSV/HTML outputs into Excel format

# Requirements

Python 3.x (laspy, Open3D, scikit-learn, scipy)
R (lidR, VoxR, ITSMe, AdTree QSM, ArchiQSM)

# Full instructions

See docs/Instructions.docx for detailed setup and usage steps.

# Authors
- Loïc Charlebois
- Annick St-Denis
