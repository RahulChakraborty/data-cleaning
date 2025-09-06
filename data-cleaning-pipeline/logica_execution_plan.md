# Logica Execution Plan and Implementation

## Overview
This document outlines the comprehensive plan for running Logica commands on the NYPL Menu Dataset, including a Python wrapper script for automated execution and result analysis.

## Current Status Assessment

### Environment Check
- ✅ Logica is listed in [`requirements.txt`](requirements.txt:5)
- ✅ Database file exists at [`data/menus.db`](data/menus.db)
- ✅ Logic files are ready:
  - [`scripts/integrity_checks.logic`](scripts/integrity_checks.logic) - Basic checks
  - [`scripts/enhanced_integrity_checks.logic`](scripts/enhanced_integrity_checks.logic) - 15 comprehensive rules
- ✅ Output directory exists: [`data/integrity_reports/`](data/integrity_reports/)

## Implementation Plan

### Phase 1: Environment Setup and Verification
1. **Check Logica Installation**
   ```bash
   pip install logica
   logica --version
   ```

2. **Verify Database Structure**
   ```bash
   sqlite3 data/menus.db ".tables"
   sqlite3 data/menus.db ".schema"
   ```

3. **Test Database Connectivity**
   ```bash
   sqlite3 data/menus.db "SELECT COUNT(*) FROM Menu;"
   sqlite3 data/menus.db "SELECT COUNT(*) FROM MenuItem;"
   sqlite3 data/menus.db "SELECT COUNT(*) FROM Dish;"
   sqlite3 data/menus.db "SELECT COUNT(*) FROM MenuPage;"
   ```

### Phase 2: Python Wrapper Script Implementation

#### Script: `scripts/run_logica_validation.py`

```python
#!/usr/bin/env python3
"""
Python wrapper for running Logica integrity validation on NYPL Menu Dataset
Provides automated execution, result analysis, and comprehensive reporting.
"""

import subprocess
import os
import pandas as pd
import sqlite3
import json
from datetime import datetime
from pathlib import Path
import sys

class LogicaValidator:
    """Comprehensive Logica validation wrapper for NYPL Menu Dataset"""
    
    def __init__(self, db_path="data/menus.db", output_dir="data/integrity_reports"):
        self.db_path = db_path
        self.output_dir = output_dir
        self.results = {}
        self.start_time = None
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 Checking Prerequisites...")
        
        # Check Logica installation
        try:
            result = subprocess.run(['logica', '--version'], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Logica installed: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Logica not found. Installing...")
            self.install_logica()
        
        # Check database
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return False
        
        # Verify database tables
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            required_tables = ['Menu', 'MenuItem', 'Dish', 'MenuPage']
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = [t for t in required_tables if t not in existing_tables]
            if missing_tables:
                print(f"❌ Missing tables: {missing_tables}")
                return False
            
            # Check table counts
            for table in required_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count:,} records")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return False
    
    def install_logica(self):
        """Install Logica if not present"""
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'logica'], 
                         check=True)
            print("✅ Logica installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Logica: {e}")
            sys.exit(1)
    
    def run_basic_checks(self):
        """Run basic integrity checks"""
        print("\n🔍 Running Basic Integrity Checks...")
        
        cmd = [
            'logica', 
            'scripts/integrity_checks.logic',
            '--db_engine=sqlite',
            f'--db_file={self.db_path}',
            f'--output_dir={self.output_dir}/'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Basic checks completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Basic checks failed: {e}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False
    
    def run_enhanced_checks(self):
        """Run enhanced integrity checks (15 comprehensive rules)"""
        print("\n🔍 Running Enhanced Integrity Checks...")
        
        cmd = [
            'logica', 
            'scripts/enhanced_integrity_checks.logic',
            '--db_engine=sqlite',
            f'--db_file={self.db_path}',
            f'--output_dir={self.output_dir}/',
            '--verbose'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Enhanced checks completed successfully")
            if result.stdout:
                print(f"Output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Enhanced checks failed: {e}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False
    
    def analyze_results(self):
        """Analyze and summarize validation results"""
        print("\n📊 Analyzing Validation Results...")
        
        # Define all expected constraint files
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
        
        violation_summary = {}
        total_violations = 0
        
        print("\nConstraint Validation Results:")
        print("=" * 60)
        
        for filename in constraint_files:
            filepath = os.path.join(self.output_dir, filename)
            constraint_name = filename.replace('.csv', '').replace('_', ' ').title()
            
            if os.path.exists(filepath):
                try:
                    df = pd.read_csv(filepath)
                    violation_count = len(df)
                    violation_summary[constraint_name] = violation_count
                    total_violations += violation_count
                    
                    status = "✅ PASS" if violation_count == 0 else f"❌ FAIL ({violation_count} violations)"
                    print(f"{constraint_name:<35}: {status}")
                    
                    # Store detailed results
                    if violation_count > 0:
                        self.results[constraint_name] = {
                            'violations': violation_count,
                            'details': df.to_dict('records')[:5]  # First 5 violations
                        }
                    
                except Exception as e:
                    print(f"{constraint_name:<35}: ❌ Error reading file ({e})")
            else:
                print(f"{constraint_name:<35}: ⚠️  File not found")
        
        print("=" * 60)
        print(f"Total violations found: {total_violations}")
        
        # Save summary
        summary_df = pd.DataFrame(list(violation_summary.items()), 
                                columns=['Constraint', 'Violations'])
        summary_path = os.path.join(self.output_dir, 'logica_validation_summary.csv')
        summary_df.to_csv(summary_path, index=False)
        
        # Generate detailed report
        self.generate_detailed_report(violation_summary, total_violations)
        
        return total_violations
    
    def generate_detailed_report(self, violation_summary, total_violations):
        """Generate comprehensive validation report"""
        report_path = os.path.join(self.output_dir, 'logica_validation_report.md')
        
        with open(report_path, 'w') as f:
            f.write("# Logica Integrity Validation Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Database:** {self.db_path}\n")
            f.write(f"**Total Violations:** {total_violations}\n\n")
            
            f.write("## Summary\n\n")
            if total_violations == 0:
                f.write("🎉 **All integrity constraints passed!** The dataset maintains excellent data quality.\n\n")
            else:
                f.write(f"⚠️ **{total_violations} integrity violations found** across multiple constraints.\n\n")
            
            f.write("## Detailed Results\n\n")
            f.write("| Constraint | Status | Violations |\n")
            f.write("|------------|--------|------------|\n")
            
            for constraint, violations in violation_summary.items():
                status = "✅ PASS" if violations == 0 else "❌ FAIL"
                f.write(f"| {constraint} | {status} | {violations} |\n")
            
            f.write("\n## Violation Details\n\n")
            for constraint_name, details in self.results.items():
                f.write(f"### {constraint_name}\n")
                f.write(f"**Violations:** {details['violations']}\n\n")
                f.write("**Sample violations:**\n")
                for i, violation in enumerate(details['details'], 1):
                    f.write(f"{i}. {violation}\n")
                f.write("\n")
            
            f.write("## Recommendations\n\n")
            if total_violations > 0:
                f.write("1. Review and address the identified violations\n")
                f.write("2. Update data cleaning procedures to prevent similar issues\n")
                f.write("3. Re-run validation after corrections\n")
            else:
                f.write("1. Data quality is excellent - no immediate action required\n")
                f.write("2. Continue regular validation as part of data pipeline\n")
        
        print(f"📄 Detailed report saved: {report_path}")
    
    def run_full_validation(self):
        """Run complete validation workflow"""
        self.start_time = datetime.now()
        
        print("🚀 Starting Logica Integrity Validation")
        print("=" * 60)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Exiting.")
            return False
        
        # Step 2: Run basic checks
        if not self.run_basic_checks():
            print("❌ Basic checks failed. Continuing with enhanced checks...")
        
        # Step 3: Run enhanced checks
        if not self.run_enhanced_checks():
            print("❌ Enhanced checks failed. Exiting.")
            return False
        
        # Step 4: Analyze results
        total_violations = self.analyze_results()
        
        # Summary
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n" + "=" * 60)
        print("🏁 Validation Complete")
        print("=" * 60)
        print(f"Duration: {duration}")
        print(f"Total violations: {total_violations}")
        print(f"Reports saved to: {self.output_dir}/")
        
        return total_violations == 0

def main():
    """Main execution function"""
    validator = LogicaValidator()
    success = validator.run_full_validation()
    
    if success:
        print("\n🎉 All integrity constraints passed!")
        sys.exit(0)
    else:
        print("\n⚠️ Some integrity violations found. Check reports for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Phase 3: Execution Commands

#### Manual Logica Commands
```bash
# Basic integrity checks
logica scripts/integrity_checks.logic \
    --db_engine=sqlite \
    --db_file=data/menus.db \
    --output_dir=data/integrity_reports/

# Enhanced integrity checks  
logica scripts/enhanced_integrity_checks.logic \
    --db_engine=sqlite \
    --db_file=data/menus.db \
    --output_dir=data/integrity_reports/ \
    --verbose
```

#### Python Wrapper Execution
```bash
# Run comprehensive validation
python scripts/run_logica_validation.py

# Or with specific parameters
python -c "
from scripts.run_logica_validation import LogicaValidator
validator = LogicaValidator('data/menus.db', 'data/integrity_reports')
validator.run_full_validation()
"
```

### Phase 4: Expected Outputs

#### Generated Files
- `data/integrity_reports/missing_dish_references.csv`
- `data/integrity_reports/missing_menu_references.csv`
- `data/integrity_reports/missing_page_references.csv`
- `data/integrity_reports/invalid_negative_prices.csv`
- `data/integrity_reports/inconsistent_price_ranges.csv`
- `data/integrity_reports/extreme_price_outliers.csv`
- `data/integrity_reports/empty_dish_names.csv`
- `data/integrity_reports/duplicate_dish_names.csv`
- `data/integrity_reports/empty_menu_pages.csv`
- `data/integrity_reports/inconsistent_page_counts.csv`
- `data/integrity_reports/inconsistent_dish_counts.csv`
- `data/integrity_reports/anachronistic_dates.csv`
- `data/integrity_reports/cleaning_broke_references.csv`
- `data/integrity_reports/uncapped_outliers_remain.csv`
- `data/integrity_reports/uncleaned_dish_names.csv`
- `data/integrity_reports/logica_validation_summary.csv`
- `data/integrity_reports/logica_validation_report.md`

#### Success Criteria
- All 15 constraint rules execute successfully
- Violation reports are generated (empty files indicate no violations)
- Summary report shows comprehensive analysis
- Integration with existing pipeline workflow

### Phase 5: Integration with Pipeline

#### Add to Enhanced Pipeline
```python
# Add to workflow/enhanced_pipeline.py
from scripts.run_logica_validation import LogicaValidator

def run_logica_validation():
    """Run Logica integrity validation"""
    validator = LogicaValidator()
    return validator.run_full_validation()
```

#### Automated Workflow Script
```bash
#!/bin/bash
# complete_pipeline_with_logica.sh

echo "🚀 Starting Complete Data Pipeline with Logica Validation"

# Step 1: Data loading
python scripts/load_to_sql.py

# Step 2: Data cleaning  
python scripts/enhanced_clean_data.py

# Step 3: Logica integrity validation
python scripts/run_logica_validation.py

# Step 4: Additional validation
python scripts/data_validation_demo.py

echo "✅ Complete pipeline finished successfully!"
```

## Next Steps

1. **Switch to Code Mode** to implement the Python wrapper script
2. **Test Logica installation** and database connectivity
3. **Execute basic integrity checks** to verify setup
4. **Run enhanced validation** with all 15 constraint rules
5. **Analyze results** and generate comprehensive reports
6. **Integrate with existing pipeline** workflow

## Risk Mitigation

- **Logica Installation Issues**: Fallback to pip install with error handling
- **Database Connectivity**: Verify table structure and data availability
- **Permission Issues**: Ensure output directory is writable
- **Large Result Sets**: Implement pagination for violation details
- **Performance**: Add timing and progress indicators

This plan provides a comprehensive approach to running Logica commands with proper error handling, result analysis, and integration with the existing data cleaning pipeline.