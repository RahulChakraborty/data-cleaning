#!/usr/bin/env python3
"""
Validate Cleaned Data and Compare Results
Run integrity validation on cleaned data and compare with original results
"""

import os
import pandas as pd
from datetime import datetime
from sql_integrity_validator import SQLIntegrityValidator

class CleanedDataValidator:
    """Validate cleaned data and compare with original results"""
    
    def __init__(self):
        self.original_db = "data/menus.db"
        self.cleaned_db = "cleaned_data/menus_cleaned.db"
        self.original_reports_dir = "data/integrity_reports"
        self.cleaned_reports_dir = "cleaned_data/integrity_reports"
        
        # Ensure cleaned reports directory exists
        os.makedirs(self.cleaned_reports_dir, exist_ok=True)
    
    def validate_cleaned_data(self):
        """Run integrity validation on cleaned data"""
        print("🔍 Running Integrity Validation on Cleaned Data")
        print("=" * 60)
        
        # Create validator for cleaned data
        validator = SQLIntegrityValidator(
            db_path=self.cleaned_db,
            output_dir=self.cleaned_reports_dir
        )
        
        # Run validation
        success = validator.run_full_validation()
        return success
    
    def compare_validation_results(self):
        """Compare original vs cleaned validation results"""
        print("\n📊 Comparing Original vs Cleaned Data Results")
        print("=" * 60)
        
        # Load original results
        original_summary_path = f"{self.original_reports_dir}/integrity_validation_summary.csv"
        cleaned_summary_path = f"{self.cleaned_reports_dir}/integrity_validation_summary.csv"
        
        if not os.path.exists(original_summary_path):
            print("❌ Original validation results not found")
            return False
        
        if not os.path.exists(cleaned_summary_path):
            print("❌ Cleaned validation results not found")
            return False
        
        # Load data
        original_df = pd.read_csv(original_summary_path)
        cleaned_df = pd.read_csv(cleaned_summary_path)
        
        # Merge for comparison
        comparison_df = original_df.merge(
            cleaned_df, 
            on='Constraint', 
            suffixes=('_Original', '_Cleaned')
        )
        
        # Calculate improvements
        comparison_df['Improvement'] = comparison_df['Violations_Original'] - comparison_df['Violations_Cleaned']
        comparison_df['Status'] = comparison_df.apply(
            lambda row: '✅ FIXED' if row['Improvement'] > 0 
            else '✅ CLEAN' if row['Violations_Cleaned'] == 0 
            else '⚠️ REMAINING', axis=1
        )
        
        # Display results
        print("\nConstraint Comparison Results:")
        print("-" * 80)
        print(f"{'Constraint':<35} {'Original':<10} {'Cleaned':<10} {'Improved':<10} {'Status'}")
        print("-" * 80)
        
        total_original = 0
        total_cleaned = 0
        total_fixed = 0
        
        for _, row in comparison_df.iterrows():
            constraint = row['Constraint']
            original = row['Violations_Original']
            cleaned = row['Violations_Cleaned']
            improvement = row['Improvement']
            status = row['Status']
            
            total_original += original
            total_cleaned += cleaned
            if improvement > 0:
                total_fixed += improvement
            
            print(f"{constraint:<35} {original:<10} {cleaned:<10} {improvement:<10} {status}")
        
        print("-" * 80)
        print(f"{'TOTALS':<35} {total_original:<10} {total_cleaned:<10} {total_fixed:<10}")
        print("-" * 80)
        
        # Save comparison report
        comparison_path = f"{self.cleaned_reports_dir}/validation_comparison.csv"
        comparison_df.to_csv(comparison_path, index=False)
        print(f"\n📄 Comparison report saved: {comparison_path}")
        
        # Generate summary
        self.generate_comparison_report(comparison_df, total_original, total_cleaned, total_fixed)
        
        return total_cleaned == 0
    
    def generate_comparison_report(self, comparison_df, total_original, total_cleaned, total_fixed):
        """Generate detailed comparison report"""
        report_path = f"{self.cleaned_reports_dir}/validation_comparison_report.md"
        
        with open(report_path, 'w') as f:
            f.write("# Data Cleaning Validation Comparison Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Original Database:** {self.original_db}\n")
            f.write(f"**Cleaned Database:** {self.cleaned_db}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Original Violations:** {total_original}\n")
            f.write(f"- **Cleaned Violations:** {total_cleaned}\n")
            f.write(f"- **Violations Fixed:** {total_fixed}\n")
            f.write(f"- **Improvement Rate:** {(total_fixed/total_original*100):.1f}%\n\n")
            
            if total_cleaned == 0:
                f.write("🎉 **Perfect!** All integrity violations have been resolved!\n\n")
            else:
                f.write(f"⚠️ **{total_cleaned} violations remain** after cleaning.\n\n")
            
            f.write("## Detailed Comparison\n\n")
            f.write("| Constraint | Original | Cleaned | Improvement | Status |\n")
            f.write("|------------|----------|---------|-------------|--------|\n")
            
            for _, row in comparison_df.iterrows():
                f.write(f"| {row['Constraint']} | {row['Violations_Original']} | {row['Violations_Cleaned']} | {row['Improvement']} | {row['Status']} |\n")
            
            f.write("\n## Cleaning Actions Performed\n\n")
            f.write("1. **Missing Dish References:** Created placeholder dishes for orphaned references\n")
            f.write("2. **Empty Menu Pages:** Removed menu pages with no menu items\n")
            f.write("3. **Inconsistent Page Counts:** Updated menu page counts to match actual pages\n")
            f.write("4. **Inconsistent Dish Counts:** Updated menu dish counts to match actual items\n")
            f.write("5. **Dish Name Cleaning:** Applied proper title case formatting\n\n")
            
            f.write("## Data Quality Assessment\n\n")
            if total_cleaned == 0:
                f.write("✅ **Excellent Data Quality:** All integrity constraints are satisfied.\n")
                f.write("✅ **Ready for Analysis:** The cleaned dataset is ready for downstream analysis.\n")
            else:
                f.write("⚠️ **Remaining Issues:** Some violations persist and may need manual review.\n")
                f.write("📋 **Recommendation:** Review remaining violations for additional cleaning opportunities.\n")
        
        print(f"📄 Detailed comparison report saved: {report_path}")
    
    def run_complete_validation(self):
        """Run complete validation and comparison workflow"""
        start_time = datetime.now()
        
        print("🚀 Starting Cleaned Data Validation and Comparison")
        print("=" * 70)
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Step 1: Validate cleaned data
        cleaned_success = self.validate_cleaned_data()
        
        # Step 2: Compare results
        comparison_success = self.compare_validation_results()
        
        # Summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 70)
        print("🏁 Validation and Comparison Complete")
        print("=" * 70)
        print(f"Duration: {duration}")
        print(f"Cleaned Data Validation: {'✅ PASSED' if cleaned_success else '⚠️ VIOLATIONS FOUND'}")
        print(f"Comparison Analysis: {'✅ COMPLETE' if comparison_success else '⚠️ ISSUES REMAIN'}")
        
        return cleaned_success and comparison_success

def main():
    """Main execution function"""
    validator = CleanedDataValidator()
    success = validator.run_complete_validation()
    
    if success:
        print("\n🎉 All validation checks passed! Data cleaning was successful!")
        return 0
    else:
        print("\n⚠️ Some issues remain. Check reports for details.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())