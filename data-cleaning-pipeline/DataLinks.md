# NYPL Menu Dataset - Data Cleaning Pipeline Project
## Phase-II Supplementary Materials

**Box Folder Link:** [To be provided upon submission]

## Contents Overview

### Source Code and Scripts
- `scripts/enhanced_clean_data.py` - Main cleaning script (290 lines)
- `scripts/data_profiling.py` - Quality assessment script (217 lines)
- `scripts/integrity_validator.py` - Constraint validation script (280 lines)
- `scripts/data_validation_demo.py` - Comparative analysis script (399 lines)
- `scripts/clean_data.py` - Basic cleaning script for comparison
- `scripts/load_to_sql.py` - Database loading script
- `scripts/validate_output.py` - Output validation script
- `scripts/final_documentation.py` - Documentation generation script

### Workflow Documentation
- `Workflow_W1_Overall.md` - Complete YesWorkflow specification for overall pipeline (189 lines)
- `Workflow_W2_Inner_Cleaning.md` - Detailed inner workflow with OpenRefine-style operations (334 lines)
- `YesWorkflow_Execution_Guide.md` - Complete guide for running YesWorkflow tool (227 lines)
- `YesWorkflow_Comment_Solution.md` - Solution for YW comment errors with ready-to-use commands (298 lines)
- `YesWorkflow_Python_Conversion_Guide.md` - Convert YW files to executable Python scripts (442 lines)
- `workflow/enhanced_pipeline.yw` - Original YesWorkflow documentation (219 lines)
- `workflow/pipeline.yw` - Basic workflow model for comparison
- `yesworkflow-0.2.1.1-jar-with-dependencies.jar` - YesWorkflow executable JAR file
- `data/final_documentation/pipeline_workflow_diagram.png` - Visual workflow representation
- `data/final_documentation/data_lineage_diagram.png` - Data provenance diagram

### Constraint Specifications
- `scripts/enhanced_integrity_checks.logic` - Logica constraint definitions (122 lines)
- `scripts/integrity_checks.logic` - Basic constraint definitions
- `Logica_Execution_Guide.md` - Complete guide for running Logica integrity validation (394 lines)

### Original ("Dirty") Datasets
- `data/Menu.csv` - Original menu metadata (5 records)
- `data/MenuPage.csv` - Original menu page data (12 records)
- `data/MenuItem.csv` - Original menu item data (36 records)
- `data/Dish.csv` - Original dish information (20 records)

### Cleaned Datasets
- `data/Menu_cleaned.csv` - Cleaned menu metadata (5 records)
- `data/MenuItem_cleaned.csv` - Cleaned menu item data (35 records)
- `data/Dish_cleaned.csv` - Cleaned dish information (20 records)
- `data/menus.db` - Complete SQLite database with all tables

### Analysis Reports and Visualizations
- `data/profiling_charts/` - Data quality assessment visualizations
  - `price_distribution_raw.png`
  - `dish_frequency.png`
  - `menu_timeline.png`
- `data/integrity_reports/` - Constraint violation reports (15 files)
  - `integrity_summary.csv`
  - `missing_dish_references.csv`
  - `empty_menu_pages.csv`
  - `inconsistent_page_counts.csv`
  - `inconsistent_dish_counts.csv`
  - `uncleaned_dish_names.csv`
- `data/validation_results/` - Before/after comparison analysis
  - `validation_summary.csv`
  - `price_distribution_comparison.png`
  - `comprehensive_validation_dashboard.png`
- `data/final_documentation/` - Comprehensive project documentation
  - `final_pipeline_report.md`

### Configuration and Dependencies
- `requirements.txt` - Python package dependencies
- `README.md` - Project overview and execution instructions
- `PIPELINE_EXPLANATION.md` - Detailed pipeline documentation

## Access Instructions

1. **Download**: Download the complete ZIP file from the Box folder link above
2. **Extract**: Extract all files maintaining the directory structure
3. **Dependencies**: Install required dependencies using:
   ```bash
   pip install -r requirements.txt
   ```
4. **Execution**: Run the complete pipeline using:
   ```bash
   python scripts/load_to_sql.py
   python scripts/enhanced_clean_data.py
   python scripts/integrity_validator.py
   python scripts/data_validation_demo.py
   ```
5. **Results**: View results in the respective `data/` subdirectories

## File Structure
```
data-cleaning-pipeline/
├── data/
│   ├── *.csv (original and cleaned datasets)
│   ├── menus.db (SQLite database)
│   ├── profiling_charts/
│   ├── integrity_reports/
│   ├── validation_results/
│   └── final_documentation/
├── scripts/
│   ├── *.py (all processing scripts)
│   └── *.logic (Logica constraint files)
├── workflow/
│   └── *.yw (YesWorkflow documentation)
├── requirements.txt
├── README.md
├── PIPELINE_EXPLANATION.md
└── Phase_II_Data_Cleaning_Report.md
```

## Contact Information
- **Student:** [To be filled in]
- **Course:** [To be filled in]
- **Date:** January 2025
- **Project:** NYPL Menu Dataset Data Cleaning Pipeline

## Notes
- All scripts are fully documented with inline comments
- The pipeline is designed to be reproducible and scalable
- Original data is preserved alongside cleaned versions
- Complete provenance tracking is maintained throughout the process
- All visualizations are generated programmatically and saved as high-resolution images

**Note:** This file should be renamed to `DataLinks.txt` for final submission as specified in the requirements.