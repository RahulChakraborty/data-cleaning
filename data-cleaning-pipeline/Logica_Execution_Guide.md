# Logica Execution Guide
## Running Logica for Data Integrity Validation on NYPL Menu Dataset

### Overview
Logica is a logic programming language that compiles to SQL for data analysis and integrity checking. This guide explains how to install, configure, and run Logica on the NYPL Menu Dataset integrity constraints.

### What is Logica?
Logica is a declarative logic programming language developed by Google that:
- Compiles logic programs to SQL
- Enables complex data analysis with simple syntax
- Provides powerful constraint checking capabilities
- Integrates with databases like SQLite, PostgreSQL, and BigQuery

## Installation and Setup

### Method 1: Install via pip (Recommended)
```bash
# Install Logica
pip install logica

# Verify installation
logica --help
```

### Method 2: Install from Source
```bash
# Clone the repository
git clone https://github.com/EvgSkv/logica.git
cd logica

# Install dependencies
pip install -r requirements.txt

# Install Logica
python setup.py install
```

### Method 3: Using Docker
```bash
# Pull Logica Docker image
docker pull logica/logica

# Run Logica in container
docker run -it -v $(pwd):/workspace logica/logica
```

### Prerequisites
- **Python 3.7+**
- **SQLite3** (for database operations)
- **pandas** (for data manipulation)

```bash
# Install required dependencies
pip install logica pandas sqlite3
```

## Project Logica Files

The project contains two Logica constraint files:

### 1. Basic Integrity Checks (`scripts/integrity_checks.logic`)
```logica
read Menu, MenuPage, MenuItem, Dish

result missing_dish_reference(dish_id) :-
    MenuItem(dish_id: dish_id),
    not Dish(id: dish_id).

write missing_dish_reference to "missing_dish_references.csv"
```

### 2. Enhanced Integrity Checks (`scripts/enhanced_integrity_checks.logic`)
- **15 comprehensive constraint rules**
- **122 lines of Logica code**
- **Covers referential integrity, data quality, and business logic**

## Running Logica

### Step 1: Prepare the Database
Ensure your SQLite database is ready with data:

```bash
# Navigate to project directory
cd /path/to/data-cleaning-pipeline

# Verify database exists and has data
sqlite3 data/menus.db ".tables"
sqlite3 data/menus.db "SELECT COUNT(*) FROM Menu;"
```

### Step 2: Run Basic Integrity Checks

#### Command Line Execution
```bash
# Run basic integrity checks
logica scripts/integrity_checks.logic \
    --db_engine=sqlite \
    --db_file=data/menus.db \
    --output_dir=data/integrity_reports/

# Alternative syntax
logica run scripts/integrity_checks.logic \
    sqlite:///data/menus.db \
    --output=data/integrity_reports/
```

#### Expected Output
```
Processing integrity_checks.logic...
Compiling Logica to SQL...
Executing SQL queries...
Writing results to missing_dish_references.csv
Execution completed successfully.
```

### Step 3: Run Enhanced Integrity Checks

#### Full Enhanced Validation
```bash
# Run comprehensive integrity validation
logica scripts/enhanced_integrity_checks.logic \
    --db_engine=sqlite \
    --db_file=data/menus.db \
    --output_dir=data/integrity_reports/

# With verbose output
logica scripts/enhanced_integrity_checks.logic \
    --db_engine=sqlite \
    --db_file=data/menus.db \
    --output_dir=data/integrity_reports/ \
    --verbose
```

#### Expected Output Files
The enhanced script generates 15 CSV files:
- `missing_dish_references.csv`
- `missing_menu_references.csv`
- `missing_page_references.csv`
- `invalid_negative_prices.csv`
- `inconsistent_price_ranges.csv`
- `extreme_price_outliers.csv`
- `empty_dish_names.csv`
- `duplicate_dish_names.csv`
- `empty_menu_pages.csv`
- `inconsistent_page_counts.csv`
- `inconsistent_dish_counts.csv`
- `anachronistic_dates.csv`
- `cleaning_broke_references.csv`
- `uncapped_outliers_remain.csv`
- `uncleaned_dish_names.csv`

### Step 4: Verify Results

#### Check Generated Files
```bash
# List generated integrity reports
ls -la data/integrity_reports/

# Check file sizes (empty files indicate no violations)
du -h data/integrity_reports/*.csv

# View sample violations
head -5 data/integrity_reports/missing_dish_references.csv
```

#### Analyze Results
```bash
# Count violations by type
wc -l data/integrity_reports/*.csv

# View non-empty reports (actual violations)
find data/integrity_reports/ -name "*.csv" -size +1c -exec echo "=== {} ===" \; -exec cat {} \;
```

## Advanced Logica Usage

### Custom Configuration

#### Create Logica Configuration File
Create `logica_config.json`:
```json
{
    "db_engine": "sqlite",
    "db_file": "data/menus.db",
    "output_dir": "data/integrity_reports/",
    "verbose": true,
    "parallel": false
}
```

#### Use Configuration File
```bash
logica scripts/enhanced_integrity_checks.logic --config=logica_config.json
```

### Interactive Logica Session

#### Start Interactive Mode
```bash
# Start Logica REPL
logica --interactive --db_engine=sqlite --db_file=data/menus.db
```

#### Interactive Commands
```logica
# Load tables
read Menu, MenuItem, Dish;

# Test simple query
result test_query(menu_id, name) :- Menu(id: menu_id, name: name);

# Execute query
run test_query;

# Exit interactive mode
exit;
```

### Debugging Logica Programs

#### View Generated SQL
```bash
# Compile to SQL without execution
logica scripts/enhanced_integrity_checks.logic \
    --compile_only \
    --output_sql=generated_queries.sql

# View generated SQL
cat generated_queries.sql
```

#### Step-by-Step Execution
```bash
# Run specific rules only
logica scripts/enhanced_integrity_checks.logic \
    --db_engine=sqlite \
    --db_file=data/menus.db \
    --rule=missing_dish_reference \
    --output_dir=data/integrity_reports/
```

## Integration with Python

### Python Wrapper Script

Create `run_logica_validation.py`:
```python
#!/usr/bin/env python3
"""
Python wrapper for running Logica integrity validation
"""

import subprocess
import os
import pandas as pd
from datetime import datetime

def run_logica_validation():
    """Run Logica integrity validation and summarize results"""
    
    print("=" * 60)
    print("LOGICA INTEGRITY VALIDATION")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Ensure output directory exists
    os.makedirs('data/integrity_reports', exist_ok=True)
    
    # Run Logica validation
    cmd = [
        'logica', 
        'scripts/enhanced_integrity_checks.logic',
        '--db_engine=sqlite',
        '--db_file=data/menus.db',
        '--output_dir=data/integrity_reports/'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Logica execution completed successfully")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Logica execution failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    # Analyze results
    analyze_integrity_results()
    return True

def analyze_integrity_results():
    """Analyze and summarize integrity validation results"""
    
    report_dir = 'data/integrity_reports'
    violation_summary = {}
    
    # Check each constraint file
    constraint_files = [
        'missing_dish_references.csv',
        'missing_menu_references.csv',
        'missing_page_references.csv',
        'invalid_negative_prices.csv',
        'inconsistent_price_ranges.csv',
        'extreme_price_outliers.csv',
        'empty_dish_names.csv',
        'duplicate_dish_names.csv',
        'empty_menu_pages.csv',
        'inconsistent_page_counts.csv',
        'inconsistent_dish_counts.csv',
        'anachronistic_dates.csv',
        'cleaning_broke_references.csv',
        'uncapped_outliers_remain.csv',
        'uncleaned_dish_names.csv'
    ]
    
    print("\nIntegrity Validation Results:")
    print("-" * 40)
    
    total_violations = 0
    
    for filename in constraint_files:
        filepath = os.path.join(report_dir, filename)
        
        if os.path.exists(filepath):
            try:
                df = pd.read_csv(filepath)
                violation_count = len(df)
                violation_summary[filename] = violation_count
                total_violations += violation_count
                
                status = "✓ PASS" if violation_count == 0 else f"✗ FAIL ({violation_count} violations)"
                constraint_name = filename.replace('.csv', '').replace('_', ' ').title()
                print(f"{constraint_name:<30}: {status}")
                
            except Exception as e:
                print(f"{filename:<30}: Error reading file ({e})")
        else:
            print(f"{filename:<30}: File not found")
    
    print(f"\nTotal violations found: {total_violations}")
    
    # Create summary report
    summary_df = pd.DataFrame(list(violation_summary.items()), 
                             columns=['Constraint', 'Violations'])
    summary_df.to_csv(f'{report_dir}/logica_validation_summary.csv', index=False)
    
    print(f"Summary saved to: {report_dir}/logica_validation_summary.csv")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    run_logica_validation()
```

#### Run Python Wrapper
```bash
python run_logica_validation.py
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Logica Not Found
```bash
# Error: logica: command not found
# Solution: Install Logica
pip install logica

# Verify installation
which logica
logica --version
```

#### 2. Database Connection Issues
```bash
# Error: Cannot connect to database
# Solution: Check database file path and permissions
ls -la data/menus.db
sqlite3 data/menus.db ".tables"
```

#### 3. Table Not Found Errors
```bash
# Error: Table 'Menu' doesn't exist
# Solution: Ensure data is loaded into database
python scripts/load_to_sql.py
sqlite3 data/menus.db "SELECT name FROM sqlite_master WHERE type='table';"
```

#### 4. Syntax Errors in Logica Files
```bash
# Error: Syntax error in .logic file
# Solution: Validate Logica syntax
logica scripts/enhanced_integrity_checks.logic --compile_only --check_syntax
```

#### 5. Permission Denied for Output Directory
```bash
# Error: Permission denied writing to output directory
# Solution: Create directory and set permissions
mkdir -p data/integrity_reports
chmod 755 data/integrity_reports
```

### Debugging Tips

#### Enable Verbose Output
```bash
logica scripts/enhanced_integrity_checks.logic \
    --db_engine=sqlite \
    --db_file=data/menus.db \
    --output_dir=data/integrity_reports/ \
    --verbose \
    --debug
```

#### Test Individual Rules
```bash
# Test single constraint rule
logica scripts/enhanced_integrity_checks.logic \
    --db_engine=sqlite \
    --db_file=data/menus.db \
    --rule=missing_dish_reference \
    --output_dir=data/integrity_reports/
```

#### Validate Generated SQL
```bash
# Generate SQL without execution
logica scripts/enhanced_integrity_checks.logic \
    --compile_only \
    --output_sql=debug_queries.sql

# Test SQL manually
sqlite3 data/menus.db < debug_queries.sql
```

## Expected Results

### Successful Execution Output
```
Processing enhanced_integrity_checks.logic...
Compiling 15 constraint rules to SQL...
Executing constraint validation queries...
Writing results to data/integrity_reports/...

Constraint Validation Results:
Missing Dish References        : ✗ FAIL (1 violations)
Missing Menu References        : ✓ PASS
Missing Page References        : ✓ PASS
Invalid Negative Prices        : ✓ PASS
Inconsistent Price Ranges      : ✓ PASS
Extreme Price Outliers         : ✗ FAIL (2 violations)
Empty Dish Names              : ✓ PASS
Duplicate Dish Names          : ✓ PASS
Empty Menu Pages              : ✗ FAIL (3 violations)
Inconsistent Page Counts      : ✗ FAIL (1 violations)
Inconsistent Dish Counts      : ✗ FAIL (5 violations)
Anachronistic Dates           : ✓ PASS
Cleaning Broke References     : ✓ PASS
Uncapped Outliers Remain      : ✓ PASS
Uncleaned Dish Names          : ✗ FAIL (5 violations)

Total violations found: 17
Execution completed successfully.
```

### Generated Files Structure
```
data/integrity_reports/
├── missing_dish_references.csv      (1 row - actual violation)
├── missing_menu_references.csv      (0 rows - no violations)
├── missing_page_references.csv      (0 rows - no violations)
├── invalid_negative_prices.csv      (0 rows - no violations)
├── inconsistent_price_ranges.csv    (0 rows - no violations)
├── extreme_price_outliers.csv       (2 rows - actual violations)
├── empty_dish_names.csv             (0 rows - no violations)
├── duplicate_dish_names.csv         (0 rows - no violations)
├── empty_menu_pages.csv             (3 rows - actual violations)
├── inconsistent_page_counts.csv     (1 row - actual violation)
├── inconsistent_dish_counts.csv     (5 rows - actual violations)
├── anachronistic_dates.csv          (0 rows - no violations)
├── cleaning_broke_references.csv    (0 rows - no violations)
├── uncapped_outliers_remain.csv     (0 rows - no violations)
├── uncleaned_dish_names.csv         (5 rows - actual violations)
└── logica_validation_summary.csv    (summary report)
```

## Integration with Data Cleaning Pipeline

### Automated Validation Workflow
```bash
#!/bin/bash
# Complete data cleaning and validation workflow

echo "Starting NYPL Menu Dataset Processing Pipeline..."

# Step 1: Load data
python scripts/load_to_sql.py

# Step 2: Run data cleaning
python scripts/enhanced_clean_data.py

# Step 3: Run Logica integrity validation
logica scripts/enhanced_integrity_checks.logic \
    --db_engine=sqlite \
    --db_file=data/menus.db \
    --output_dir=data/integrity_reports/

# Step 4: Run validation demo
python scripts/data_validation_demo.py

echo "Pipeline completed successfully!"
```

This comprehensive guide provides everything needed to install, configure, and run Logica for data integrity validation on the NYPL Menu Dataset, ensuring robust constraint checking and quality assurance.