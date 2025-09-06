#!/usr/bin/env python3
"""
Integrated Data Cleaning Pipeline with SQL-based Integrity Validation
Combines the existing data cleaning workflow with comprehensive integrity checks
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add the scripts directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sql_integrity_validator import SQLIntegrityValidator

def run_integrated_pipeline():
    """Run the complete integrated data cleaning and validation pipeline"""
    
    print("🚀 Starting Integrated Data Cleaning Pipeline with Integrity Validation")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    pipeline_start = datetime.now()
    
    # Step 1: Load data to SQL (if needed)
    print("\n📊 Step 1: Loading Data to SQL Database")
    try:
        if os.path.exists('scripts/load_to_sql.py'):
            import subprocess
            result = subprocess.run([sys.executable, 'scripts/load_to_sql.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Data loaded successfully")
            else:
                print(f"⚠️ Data loading completed with warnings: {result.stderr}")
        else:
            print("ℹ️ Data loading script not found, assuming data is already loaded")
    except Exception as e:
        print(f"⚠️ Data loading step encountered issues: {e}")
    
    # Step 2: Run data cleaning
    print("\n🧹 Step 2: Running Enhanced Data Cleaning")
    try:
        if os.path.exists('scripts/enhanced_clean_data.py'):
            import subprocess
            result = subprocess.run([sys.executable, 'scripts/enhanced_clean_data.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Data cleaning completed successfully")
            else:
                print(f"⚠️ Data cleaning completed with warnings: {result.stderr}")
        else:
            print("ℹ️ Enhanced cleaning script not found, skipping cleaning step")
    except Exception as e:
        print(f"⚠️ Data cleaning step encountered issues: {e}")
    
    # Step 3: Run SQL-based integrity validation (our main contribution)
    print("\n🔍 Step 3: Running SQL-based Integrity Validation")
    validator = SQLIntegrityValidator()
    validation_success = validator.run_full_validation()
    
    # Step 4: Run additional validation demos (if available)
    print("\n📈 Step 4: Running Additional Validation Demos")
    try:
        if os.path.exists('scripts/data_validation_demo.py'):
            import subprocess
            result = subprocess.run([sys.executable, 'scripts/data_validation_demo.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Validation demos completed successfully")
            else:
                print(f"⚠️ Validation demos completed with warnings: {result.stderr}")
        else:
            print("ℹ️ Validation demo script not found, skipping demo step")
    except Exception as e:
        print(f"⚠️ Validation demo step encountered issues: {e}")
    
    # Step 5: Generate final documentation
    print("\n📄 Step 5: Generating Final Documentation")
    try:
        if os.path.exists('scripts/final_documentation.py'):
            import subprocess
            result = subprocess.run([sys.executable, 'scripts/final_documentation.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Final documentation generated successfully")
            else:
                print(f"⚠️ Documentation generation completed with warnings: {result.stderr}")
        else:
            print("ℹ️ Final documentation script not found, skipping documentation step")
    except Exception as e:
        print(f"⚠️ Documentation generation step encountered issues: {e}")
    
    # Pipeline Summary
    pipeline_end = datetime.now()
    duration = pipeline_end - pipeline_start
    
    print("\n" + "=" * 80)
    print("🏁 Integrated Pipeline Complete")
    print("=" * 80)
    print(f"Total Duration: {duration}")
    print(f"Integrity Validation: {'✅ PASSED' if validation_success else '⚠️ VIOLATIONS FOUND'}")
    print("\n📊 Generated Reports:")
    print("  • data/integrity_reports/integrity_validation_summary.csv")
    print("  • data/integrity_reports/integrity_validation_report.md")
    print("  • Individual constraint violation CSV files")
    
    if not validation_success:
        print("\n⚠️ Data quality issues detected. Review the integrity reports for details.")
        print("   Consider addressing violations before proceeding with data analysis.")
    else:
        print("\n🎉 All integrity constraints passed! Data quality is excellent.")
    
    return validation_success

def main():
    """Main execution function"""
    try:
        success = run_integrated_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()