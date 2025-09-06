#!/usr/bin/env python3
"""
SQL-based integrity validation for NYPL Menu Dataset
Direct SQL implementation of the integrity constraints originally designed for Logica
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

class SQLIntegrityValidator:
    """SQL-based integrity validation for NYPL Menu Dataset"""
    
    def __init__(self, db_path="data/menus.db", output_dir="data/integrity_reports"):
        self.db_path = db_path
        self.output_dir = output_dir
        self.results = {}
        self.start_time = None
        
        # Ensure output directory exists
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def check_prerequisites(self):
        """Check if all prerequisites are met"""
        print("🔍 Checking Prerequisites...")
        
        # Check database
        if not os.path.exists(self.db_path):
            print(f"❌ Database not found: {self.db_path}")
            return False
        
        # Verify database tables
        try:
            conn = self.get_connection()
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
    
    def run_integrity_checks(self):
        """Run all integrity constraint checks"""
        print("\n🔍 Running SQL-based Integrity Checks...")
        
        conn = self.get_connection()
        
        # Define all integrity constraint queries
        constraints = {
            'missing_dish_references': {
                'query': """
                    SELECT mi.id as menu_item_id, mi.dish_id
                    FROM MenuItem mi
                    LEFT JOIN Dish d ON mi.dish_id = d.id
                    WHERE d.id IS NULL AND mi.dish_id IS NOT NULL
                """,
                'description': 'Menu items referencing non-existent dishes'
            },
            
            'missing_menu_references': {
                'query': """
                    SELECT mp.id as page_id, mp.menu_id
                    FROM MenuPage mp
                    LEFT JOIN Menu m ON mp.menu_id = m.id
                    WHERE m.id IS NULL AND mp.menu_id IS NOT NULL
                """,
                'description': 'Menu pages referencing non-existent menus'
            },
            
            'missing_page_references': {
                'query': """
                    SELECT mi.id as item_id, mi.menu_page_id as page_id
                    FROM MenuItem mi
                    LEFT JOIN MenuPage mp ON mi.menu_page_id = mp.id
                    WHERE mp.id IS NULL AND mi.menu_page_id IS NOT NULL
                """,
                'description': 'Menu items referencing non-existent menu pages'
            },
            
            'invalid_negative_prices': {
                'query': """
                    SELECT id as item_id, price
                    FROM MenuItem
                    WHERE price < 0
                """,
                'description': 'Menu items with negative prices'
            },
            
            'inconsistent_price_ranges': {
                'query': """
                    SELECT id as item_id, price, high_price
                    FROM MenuItem
                    WHERE high_price IS NOT NULL 
                    AND high_price < price
                """,
                'description': 'Menu items where high_price < price'
            },
            
            'extreme_price_outliers': {
                'query': """
                    SELECT id as item_id, price
                    FROM MenuItem
                    WHERE price > 100.0
                """,
                'description': 'Menu items with extremely high prices (>$100)'
            },
            
            'empty_dish_names': {
                'query': """
                    SELECT id as dish_id, name
                    FROM Dish
                    WHERE name IS NULL OR TRIM(name) = ''
                """,
                'description': 'Dishes with empty or null names'
            },
            
            'duplicate_dish_names': {
                'query': """
                    SELECT d1.id as dish_id1, d2.id as dish_id2, d1.name
                    FROM Dish d1
                    JOIN Dish d2 ON d1.name = d2.name AND d1.id < d2.id
                    WHERE d1.name IS NOT NULL AND TRIM(d1.name) != ''
                """,
                'description': 'Dishes with duplicate names'
            },
            
            'empty_menu_pages': {
                'query': """
                    SELECT mp.id as page_id, mp.menu_id
                    FROM MenuPage mp
                    LEFT JOIN MenuItem mi ON mp.id = mi.menu_page_id
                    WHERE mi.menu_page_id IS NULL
                """,
                'description': 'Menu pages with no menu items'
            },
            
            'inconsistent_page_counts': {
                'query': """
                    SELECT m.id as menu_id, m.page_count as declared_count, 
                           COUNT(mp.id) as actual_count
                    FROM Menu m
                    LEFT JOIN MenuPage mp ON m.id = mp.menu_id
                    GROUP BY m.id, m.page_count
                    HAVING m.page_count != COUNT(mp.id)
                """,
                'description': 'Menus with inconsistent page counts'
            },
            
            'inconsistent_dish_counts': {
                'query': """
                    SELECT m.id as menu_id, m.dish_count as declared_count,
                           COUNT(mi.id) as actual_count
                    FROM Menu m
                    LEFT JOIN MenuPage mp ON m.id = mp.menu_id
                    LEFT JOIN MenuItem mi ON mp.id = mi.menu_page_id
                    GROUP BY m.id, m.dish_count
                    HAVING m.dish_count != COUNT(mi.id)
                """,
                'description': 'Menus with inconsistent dish counts'
            },
            
            'anachronistic_dates': {
                'query': """
                    SELECT id as menu_id, date
                    FROM Menu
                    WHERE date > '1930-01-01'
                """,
                'description': 'Menus with dates after 1930 (anachronistic for historical dataset)'
            }
        }
        
        # Add cleaned data validation if cleaned tables exist
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%_cleaned';")
        cleaned_tables = [row[0] for row in cursor.fetchall()]
        
        if 'MenuItem_cleaned' in cleaned_tables and 'Dish_cleaned' in cleaned_tables:
            constraints.update({
                'cleaning_broke_references': {
                    'query': """
                        SELECT mic.id as item_id, mic.dish_id
                        FROM MenuItem_cleaned mic
                        LEFT JOIN Dish_cleaned dc ON mic.dish_id = dc.id
                        WHERE dc.id IS NULL AND mic.dish_id IS NOT NULL
                    """,
                    'description': 'Cleaned data broke referential integrity'
                },
                
                'uncapped_outliers_remain': {
                    'query': """
                        SELECT id as item_id, price
                        FROM MenuItem_cleaned
                        WHERE price > 60.0
                    """,
                    'description': 'Price outliers remain uncapped after cleaning'
                },
                
                'uncleaned_dish_names': {
                    'query': """
                        SELECT id as dish_id, name
                        FROM Dish_cleaned
                        WHERE (name IS NULL OR TRIM(name) = '' OR
                               name != TRIM(name) OR
                               SUBSTR(name, 1, 1) != UPPER(SUBSTR(name, 1, 1)) OR
                               name LIKE '%  %')
                        AND name IS NOT NULL
                    """,
                    'description': 'Dish names with formatting issues (null, empty, untrimmed, not starting with capital, or double spaces)'
                }
            })
        
        # Execute all constraints
        violation_summary = {}
        total_violations = 0
        
        print("\nConstraint Validation Results:")
        print("=" * 60)
        
        for constraint_name, constraint_info in constraints.items():
            try:
                df = pd.read_sql_query(constraint_info['query'], conn)
                violation_count = len(df)
                violation_summary[constraint_name] = violation_count
                total_violations += violation_count
                
                # Save results to CSV
                csv_path = os.path.join(self.output_dir, f"{constraint_name}.csv")
                df.to_csv(csv_path, index=False)
                
                # Display results
                constraint_display = constraint_name.replace('_', ' ').title()
                status = "✅ PASS" if violation_count == 0 else f"❌ FAIL ({violation_count} violations)"
                print(f"{constraint_display:<35}: {status}")
                
                # Store detailed results for reporting
                if violation_count > 0:
                    self.results[constraint_display] = {
                        'violations': violation_count,
                        'description': constraint_info['description'],
                        'details': df.to_dict('records')[:5]  # First 5 violations
                    }
                
            except Exception as e:
                print(f"{constraint_name:<35}: ❌ Error executing query ({e})")
        
        conn.close()
        
        print("=" * 60)
        print(f"Total violations found: {total_violations}")
        
        # Generate reports
        self.generate_summary_report(violation_summary, total_violations)
        self.generate_detailed_report(violation_summary, total_violations)
        
        return total_violations
    
    def generate_summary_report(self, violation_summary, total_violations):
        """Generate summary CSV report"""
        summary_df = pd.DataFrame([
            {'Constraint': k.replace('_', ' ').title(), 'Violations': v}
            for k, v in violation_summary.items()
        ])
        
        summary_path = os.path.join(self.output_dir, 'integrity_validation_summary.csv')
        summary_df.to_csv(summary_path, index=False)
        print(f"📊 Summary report saved: {summary_path}")
    
    def generate_detailed_report(self, violation_summary, total_violations):
        """Generate detailed markdown report"""
        report_path = os.path.join(self.output_dir, 'integrity_validation_report.md')
        
        with open(report_path, 'w') as f:
            f.write("# SQL Integrity Validation Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Database:** {self.db_path}\n")
            f.write(f"**Total Violations:** {total_violations}\n\n")
            
            f.write("## Summary\n\n")
            if total_violations == 0:
                f.write("🎉 **All integrity constraints passed!** The dataset maintains excellent data quality.\n\n")
            else:
                f.write(f"⚠️ **{total_violations} integrity violations found** across multiple constraints.\n\n")
            
            f.write("## Detailed Results\n\n")
            f.write("| Constraint | Status | Violations | Description |\n")
            f.write("|------------|--------|------------|-------------|\n")
            
            for constraint, violations in violation_summary.items():
                status = "✅ PASS" if violations == 0 else "❌ FAIL"
                constraint_display = constraint.replace('_', ' ').title()
                description = self.results.get(constraint_display, {}).get('description', '')
                f.write(f"| {constraint_display} | {status} | {violations} | {description} |\n")
            
            f.write("\n## Violation Details\n\n")
            for constraint_name, details in self.results.items():
                f.write(f"### {constraint_name}\n")
                f.write(f"**Description:** {details['description']}\n")
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
        
        print("🚀 Starting SQL Integrity Validation")
        print("=" * 60)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            print("❌ Prerequisites not met. Exiting.")
            return False
        
        # Step 2: Run integrity checks
        total_violations = self.run_integrity_checks()
        
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
    validator = SQLIntegrityValidator()
    success = validator.run_full_validation()
    
    if success:
        print("\n🎉 All integrity constraints passed!")
        return 0
    else:
        print("\n⚠️ Some integrity violations found. Check reports for details.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())