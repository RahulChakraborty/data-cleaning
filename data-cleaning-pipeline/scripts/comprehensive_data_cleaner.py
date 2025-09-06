#!/usr/bin/env python3
"""
Comprehensive Data Cleaner for NYPL Menu Dataset
Addresses all integrity violations identified by the SQL-based validation
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import shutil

class ComprehensiveDataCleaner:
    """Clean data based on integrity validation results"""
    
    def __init__(self, source_db="data/menus.db", cleaned_dir="cleaned_data"):
        self.source_db = source_db
        self.cleaned_dir = cleaned_dir
        self.cleaned_db = f"{cleaned_dir}/menus_cleaned.db"
        
        # Create cleaned_data directory
        Path(self.cleaned_dir).mkdir(parents=True, exist_ok=True)
        
        # Copy original database to cleaned location
        if os.path.exists(self.source_db):
            shutil.copy2(self.source_db, self.cleaned_db)
            print(f"✅ Copied database to {self.cleaned_db}")
    
    def get_connection(self, db_path=None):
        """Get database connection"""
        if db_path is None:
            db_path = self.cleaned_db
        return sqlite3.connect(db_path)
    
    def clean_missing_dish_references(self):
        """Fix missing dish references"""
        print("\n🔧 Fixing missing dish references...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Find missing dish references
        cursor.execute("""
            SELECT mi.id, mi.dish_id
            FROM MenuItem mi
            LEFT JOIN Dish d ON mi.dish_id = d.id
            WHERE d.id IS NULL AND mi.dish_id IS NOT NULL
        """)
        
        missing_refs = cursor.fetchall()
        
        for menu_item_id, dish_id in missing_refs:
            print(f"  • MenuItem {menu_item_id} references non-existent Dish {dish_id}")
            
            # Option 1: Create a placeholder dish
            cursor.execute("""
                INSERT OR IGNORE INTO Dish (id, name, menus_appeared, times_appeared, first_appeared, last_appeared)
                VALUES (?, 'Unknown Dish (ID: ' || ? || ')', 1, 1, '1900-01-01', '1900-01-01')
            """, (dish_id, dish_id))
            
            print(f"    → Created placeholder Dish {dish_id}")
        
        conn.commit()
        conn.close()
        print(f"✅ Fixed {len(missing_refs)} missing dish references")
    
    def clean_empty_menu_pages(self):
        """Handle empty menu pages"""
        print("\n🔧 Handling empty menu pages...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Find empty menu pages
        cursor.execute("""
            SELECT mp.id, mp.menu_id
            FROM MenuPage mp
            LEFT JOIN MenuItem mi ON mp.id = mi.menu_page_id
            WHERE mi.menu_page_id IS NULL
        """)
        
        empty_pages = cursor.fetchall()
        
        for page_id, menu_id in empty_pages:
            print(f"  • MenuPage {page_id} (Menu {menu_id}) has no menu items")
            
            # Option: Remove empty menu pages
            cursor.execute("DELETE FROM MenuPage WHERE id = ?", (page_id,))
            print(f"    → Removed empty MenuPage {page_id}")
        
        conn.commit()
        conn.close()
        print(f"✅ Removed {len(empty_pages)} empty menu pages")
    
    def clean_inconsistent_page_counts(self):
        """Fix inconsistent page counts"""
        print("\n🔧 Fixing inconsistent page counts...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Find inconsistent page counts
        cursor.execute("""
            SELECT m.id, m.page_count as declared_count, COUNT(mp.id) as actual_count
            FROM Menu m
            LEFT JOIN MenuPage mp ON m.id = mp.menu_id
            GROUP BY m.id, m.page_count
            HAVING m.page_count != COUNT(mp.id)
        """)
        
        inconsistent_counts = cursor.fetchall()
        
        for menu_id, declared_count, actual_count in inconsistent_counts:
            print(f"  • Menu {menu_id}: declared {declared_count} pages, actual {actual_count} pages")
            
            # Update to actual count
            cursor.execute("UPDATE Menu SET page_count = ? WHERE id = ?", (actual_count, menu_id))
            print(f"    → Updated Menu {menu_id} page_count to {actual_count}")
        
        conn.commit()
        conn.close()
        print(f"✅ Fixed {len(inconsistent_counts)} inconsistent page counts")
    
    def clean_inconsistent_dish_counts(self):
        """Fix inconsistent dish counts"""
        print("\n🔧 Fixing inconsistent dish counts...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Find inconsistent dish counts
        cursor.execute("""
            SELECT m.id, m.dish_count as declared_count, COUNT(mi.id) as actual_count
            FROM Menu m
            LEFT JOIN MenuPage mp ON m.id = mp.menu_id
            LEFT JOIN MenuItem mi ON mp.id = mi.menu_page_id
            GROUP BY m.id, m.dish_count
            HAVING m.dish_count != COUNT(mi.id)
        """)
        
        inconsistent_counts = cursor.fetchall()
        
        for menu_id, declared_count, actual_count in inconsistent_counts:
            print(f"  • Menu {menu_id}: declared {declared_count} dishes, actual {actual_count} dishes")
            
            # Update to actual count
            cursor.execute("UPDATE Menu SET dish_count = ? WHERE id = ?", (actual_count, menu_id))
            print(f"    → Updated Menu {menu_id} dish_count to {actual_count}")
        
        conn.commit()
        conn.close()
        print(f"✅ Fixed {len(inconsistent_counts)} inconsistent dish counts")
    
    def clean_dish_names(self):
        """Clean dish names to proper title case"""
        print("\n🔧 Cleaning dish names to proper title case...")
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Find dishes that need name cleaning
        cursor.execute("""
            SELECT id, name
            FROM Dish
            WHERE name IS NOT NULL AND TRIM(name) != ''
        """)
        
        dishes = cursor.fetchall()
        cleaned_count = 0
        
        for dish_id, name in dishes:
            # Apply title case cleaning
            cleaned_name = self.clean_dish_name(name)
            
            if cleaned_name != name:
                cursor.execute("UPDATE Dish SET name = ? WHERE id = ?", (cleaned_name, dish_id))
                print(f"  • Dish {dish_id}: '{name}' → '{cleaned_name}'")
                cleaned_count += 1
        
        conn.commit()
        conn.close()
        print(f"✅ Cleaned {cleaned_count} dish names")
    
    def clean_dish_name(self, name):
        """Apply proper title case to dish name"""
        if not name:
            return name
        
        # Basic title case with some culinary-specific rules
        words = name.split()
        cleaned_words = []
        
        # Words that should remain lowercase (articles, prepositions, etc.)
        lowercase_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        for i, word in enumerate(words):
            # First word is always capitalized
            if i == 0:
                cleaned_words.append(word.capitalize())
            # Check if word should remain lowercase
            elif word.lower() in lowercase_words:
                cleaned_words.append(word.lower())
            # Regular title case
            else:
                cleaned_words.append(word.capitalize())
        
        return ' '.join(cleaned_words)
    
    def export_cleaned_csv_files(self):
        """Export cleaned data to CSV files"""
        print("\n📄 Exporting cleaned data to CSV files...")
        
        conn = self.get_connection()
        
        tables = ['Menu', 'MenuPage', 'MenuItem', 'Dish']
        
        for table in tables:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            csv_path = f"{self.cleaned_dir}/{table}_cleaned.csv"
            df.to_csv(csv_path, index=False)
            print(f"✅ Exported {table} to {csv_path} ({len(df)} records)")
        
        conn.close()
    
    def run_comprehensive_cleaning(self):
        """Run all cleaning operations"""
        start_time = datetime.now()
        
        print("🧹 Starting Comprehensive Data Cleaning")
        print("=" * 60)
        print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Source DB: {self.source_db}")
        print(f"Cleaned DB: {self.cleaned_db}")
        print("=" * 60)
        
        # Run all cleaning operations
        self.clean_missing_dish_references()
        self.clean_empty_menu_pages()
        self.clean_inconsistent_page_counts()
        self.clean_inconsistent_dish_counts()
        self.clean_dish_names()
        
        # Export cleaned CSV files
        self.export_cleaned_csv_files()
        
        # Summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print("🏁 Data Cleaning Complete")
        print("=" * 60)
        print(f"Duration: {duration}")
        print(f"Cleaned database: {self.cleaned_db}")
        print(f"Cleaned CSV files: {self.cleaned_dir}/")
        
        return True

def main():
    """Main execution function"""
    cleaner = ComprehensiveDataCleaner()
    success = cleaner.run_comprehensive_cleaning()
    
    if success:
        print("\n🎉 Data cleaning completed successfully!")
        return 0
    else:
        print("\n❌ Data cleaning failed!")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())