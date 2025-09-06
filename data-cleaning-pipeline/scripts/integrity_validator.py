import pandas as pd
import sqlite3
import numpy as np
from datetime import datetime
import os

print("=" * 60)
print("INTEGRITY CONSTRAINT VALIDATION - NYPL Menu Dataset")
print("=" * 60)
print(f"Started on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Connect to the database
conn = sqlite3.connect('../data/menus.db')

# Create output directory for constraint violation reports
os.makedirs('../data/integrity_reports', exist_ok=True)

# Load all tables
print("Loading data tables...")
menu_df = pd.read_sql_query("SELECT * FROM Menu", conn)
menupage_df = pd.read_sql_query("SELECT * FROM MenuPage", conn)
menuitem_df = pd.read_sql_query("SELECT * FROM MenuItem", conn)
dish_df = pd.read_sql_query("SELECT * FROM Dish", conn)

# Load cleaned tables
menu_cleaned_df = pd.read_sql_query("SELECT * FROM Menu_cleaned", conn)
menuitem_cleaned_df = pd.read_sql_query("SELECT * FROM MenuItem_cleaned", conn)
dish_cleaned_df = pd.read_sql_query("SELECT * FROM Dish_cleaned", conn)

print(f"Loaded {len(menu_df)} menus, {len(menupage_df)} pages, {len(menuitem_df)} items, {len(dish_df)} dishes")
print()

# ============================================================================
# REFERENTIAL INTEGRITY CONSTRAINTS
# ============================================================================
print("CHECKING REFERENTIAL INTEGRITY CONSTRAINTS")
print("-" * 50)

# Rule 1: Missing dish references in menu items
print("Rule 1: Checking for missing dish references...")
missing_dish_refs = menuitem_df[~menuitem_df['dish_id'].isin(dish_df['id'])]
print(f"Found {len(missing_dish_refs)} menu items with invalid dish references")

if len(missing_dish_refs) > 0:
    missing_dish_refs[['id', 'dish_id', 'price']].to_csv(
        '../data/integrity_reports/missing_dish_references.csv', index=False)
    print("  Saved to: missing_dish_references.csv")

# Rule 2: Missing menu references in menu pages
print("Rule 2: Checking for missing menu references...")
missing_menu_refs = menupage_df[~menupage_df['menu_id'].isin(menu_df['id'])]
print(f"Found {len(missing_menu_refs)} menu pages with invalid menu references")

if len(missing_menu_refs) > 0:
    missing_menu_refs[['id', 'menu_id']].to_csv(
        '../data/integrity_reports/missing_menu_references.csv', index=False)
    print("  Saved to: missing_menu_references.csv")

# Rule 3: Missing menu page references in menu items
print("Rule 3: Checking for missing menu page references...")
missing_page_refs = menuitem_df[~menuitem_df['menu_page_id'].isin(menupage_df['id'])]
print(f"Found {len(missing_page_refs)} menu items with invalid page references")

if len(missing_page_refs) > 0:
    missing_page_refs[['id', 'menu_page_id']].to_csv(
        '../data/integrity_reports/missing_page_references.csv', index=False)
    print("  Saved to: missing_page_references.csv")

print()

# ============================================================================
# DATA QUALITY CONSTRAINTS
# ============================================================================
print("CHECKING DATA QUALITY CONSTRAINTS")
print("-" * 50)

# Rule 4: Invalid price ranges (negative prices)
print("Rule 4: Checking for negative prices...")
negative_prices = menuitem_df[menuitem_df['price'] < 0]
print(f"Found {len(negative_prices)} menu items with negative prices")

if len(negative_prices) > 0:
    negative_prices[['id', 'price']].to_csv(
        '../data/integrity_reports/invalid_negative_prices.csv', index=False)
    print("  Saved to: invalid_negative_prices.csv")

# Rule 5: Inconsistent price ranges (high_price < price)
print("Rule 5: Checking for inconsistent price ranges...")
inconsistent_prices = menuitem_df[
    (menuitem_df['high_price'].notna()) & 
    (menuitem_df['high_price'] < menuitem_df['price'])
]
print(f"Found {len(inconsistent_prices)} menu items with inconsistent price ranges")

if len(inconsistent_prices) > 0:
    inconsistent_prices[['id', 'price', 'high_price']].to_csv(
        '../data/integrity_reports/inconsistent_price_ranges.csv', index=False)
    print("  Saved to: inconsistent_price_ranges.csv")

# Rule 6: Extreme price outliers (> $100 in historical context)
print("Rule 6: Checking for extreme price outliers...")
extreme_outliers = menuitem_df[menuitem_df['price'] > 100.0]
print(f"Found {len(extreme_outliers)} menu items with extreme prices (>$100)")

if len(extreme_outliers) > 0:
    extreme_outliers[['id', 'price']].to_csv(
        '../data/integrity_reports/extreme_price_outliers.csv', index=False)
    print("  Saved to: extreme_price_outliers.csv")

# Rule 7: Empty or null dish names
print("Rule 7: Checking for empty dish names...")
empty_names = dish_df[(dish_df['name'].isna()) | (dish_df['name'] == '')]
print(f"Found {len(empty_names)} dishes with empty names")

if len(empty_names) > 0:
    empty_names[['id', 'name']].to_csv(
        '../data/integrity_reports/empty_dish_names.csv', index=False)
    print("  Saved to: empty_dish_names.csv")

# Rule 8: Duplicate dish names
print("Rule 8: Checking for duplicate dish names...")
duplicate_names = dish_df[dish_df.duplicated(subset=['name'], keep=False)]
print(f"Found {len(duplicate_names)} dishes with duplicate names")

if len(duplicate_names) > 0:
    duplicate_names[['id', 'name']].to_csv(
        '../data/integrity_reports/duplicate_dish_names.csv', index=False)
    print("  Saved to: duplicate_dish_names.csv")

print()

# ============================================================================
# BUSINESS LOGIC CONSTRAINTS
# ============================================================================
print("CHECKING BUSINESS LOGIC CONSTRAINTS")
print("-" * 50)

# Rule 9: Menu pages without menu items
print("Rule 9: Checking for empty menu pages...")
page_item_counts = menuitem_df.groupby('menu_page_id').size()
empty_pages = menupage_df[~menupage_df['id'].isin(page_item_counts.index)]
print(f"Found {len(empty_pages)} menu pages without items")

if len(empty_pages) > 0:
    empty_pages[['id', 'menu_id']].to_csv(
        '../data/integrity_reports/empty_menu_pages.csv', index=False)
    print("  Saved to: empty_menu_pages.csv")

# Rule 10: Menus with inconsistent page counts
print("Rule 10: Checking for inconsistent page counts...")
actual_page_counts = menupage_df.groupby('menu_id').size().reset_index(name='actual_count')
page_count_check = menu_df.merge(actual_page_counts, left_on='id', right_on='menu_id', how='left')
page_count_check['actual_count'] = page_count_check['actual_count'].fillna(0)
inconsistent_page_counts = page_count_check[
    page_count_check['page_count'] != page_count_check['actual_count']
]
print(f"Found {len(inconsistent_page_counts)} menus with inconsistent page counts")

if len(inconsistent_page_counts) > 0:
    inconsistent_page_counts[['id', 'page_count', 'actual_count']].to_csv(
        '../data/integrity_reports/inconsistent_page_counts.csv', index=False)
    print("  Saved to: inconsistent_page_counts.csv")

# Rule 11: Menus with inconsistent dish counts
print("Rule 11: Checking for inconsistent dish counts...")
# Get actual dish counts per menu
menu_dish_counts = menuitem_df.merge(menupage_df, left_on='menu_page_id', right_on='id')
actual_dish_counts = menu_dish_counts.groupby('menu_id').size().reset_index(name='actual_count')
dish_count_check = menu_df.merge(actual_dish_counts, left_on='id', right_on='menu_id', how='left')
dish_count_check['actual_count'] = dish_count_check['actual_count'].fillna(0)
inconsistent_dish_counts = dish_count_check[
    dish_count_check['dish_count'] != dish_count_check['actual_count']
]
print(f"Found {len(inconsistent_dish_counts)} menus with inconsistent dish counts")

if len(inconsistent_dish_counts) > 0:
    inconsistent_dish_counts[['id', 'dish_count', 'actual_count']].to_csv(
        '../data/integrity_reports/inconsistent_dish_counts.csv', index=False)
    print("  Saved to: inconsistent_dish_counts.csv")

# Rule 12: Historical date inconsistencies
print("Rule 12: Checking for anachronistic dates...")
menu_df['date'] = pd.to_datetime(menu_df['date'])
anachronistic_dates = menu_df[menu_df['date'] > '1930-01-01']
print(f"Found {len(anachronistic_dates)} menus with dates after 1930")

if len(anachronistic_dates) > 0:
    anachronistic_dates[['id', 'date']].to_csv(
        '../data/integrity_reports/anachronistic_dates.csv', index=False)
    print("  Saved to: anachronistic_dates.csv")

print()

# ============================================================================
# CLEANED DATA VALIDATION
# ============================================================================
print("VALIDATING CLEANED DATA")
print("-" * 50)

# Rule 13: Verify cleaning preserved referential integrity
print("Rule 13: Checking cleaned data referential integrity...")
cleaned_missing_refs = menuitem_cleaned_df[~menuitem_cleaned_df['dish_id'].isin(dish_cleaned_df['id'])]
print(f"Found {len(cleaned_missing_refs)} referential integrity violations in cleaned data")

if len(cleaned_missing_refs) > 0:
    cleaned_missing_refs[['id', 'dish_id']].to_csv(
        '../data/integrity_reports/cleaning_broke_references.csv', index=False)
    print("  Saved to: cleaning_broke_references.csv")

# Rule 14: Verify price outliers were properly handled
print("Rule 14: Checking for uncapped outliers in cleaned data...")
uncapped_outliers = menuitem_cleaned_df[menuitem_cleaned_df['price'] > 60.0]
print(f"Found {len(uncapped_outliers)} uncapped outliers in cleaned data")

if len(uncapped_outliers) > 0:
    uncapped_outliers[['id', 'price']].to_csv(
        '../data/integrity_reports/uncapped_outliers_remain.csv', index=False)
    print("  Saved to: uncapped_outliers_remain.csv")

# Rule 15: Verify dish name cleaning was applied
print("Rule 15: Checking dish name cleaning consistency...")
def is_title_case(name):
    if pd.isna(name):
        return True
    return str(name) == str(name).title()

uncleaned_names = dish_cleaned_df[~dish_cleaned_df['name'].apply(is_title_case)]
print(f"Found {len(uncleaned_names)} dishes with inconsistent name formatting")

if len(uncleaned_names) > 0:
    uncleaned_names[['id', 'name']].to_csv(
        '../data/integrity_reports/uncleaned_dish_names.csv', index=False)
    print("  Saved to: uncleaned_dish_names.csv")

print()

# ============================================================================
# SUMMARY REPORT
# ============================================================================
print("INTEGRITY VALIDATION SUMMARY")
print("-" * 50)

violations = {
    'Missing dish references': len(missing_dish_refs),
    'Missing menu references': len(missing_menu_refs),
    'Missing page references': len(missing_page_refs),
    'Negative prices': len(negative_prices),
    'Inconsistent price ranges': len(inconsistent_prices),
    'Extreme price outliers': len(extreme_outliers),
    'Empty dish names': len(empty_names),
    'Duplicate dish names': len(duplicate_names),
    'Empty menu pages': len(empty_pages),
    'Inconsistent page counts': len(inconsistent_page_counts),
    'Inconsistent dish counts': len(inconsistent_dish_counts),
    'Anachronistic dates': len(anachronistic_dates),
    'Cleaned data ref violations': len(cleaned_missing_refs),
    'Uncapped outliers in cleaned': len(uncapped_outliers),
    'Uncleaned dish names': len(uncleaned_names)
}

total_violations = sum(violations.values())
print(f"Total constraint violations found: {total_violations}")
print()

print("Breakdown by constraint type:")
for constraint, count in violations.items():
    status = "✓ PASS" if count == 0 else f"✗ FAIL ({count} violations)"
    print(f"  {constraint:<30}: {status}")

print()
print("All integrity reports saved to: ../data/integrity_reports/")

# Create summary report
summary_df = pd.DataFrame(list(violations.items()), columns=['Constraint', 'Violations'])
summary_df.to_csv('../data/integrity_reports/integrity_summary.csv', index=False)
print("Summary report saved to: integrity_summary.csv")

conn.close()
print(f"\nIntegrity validation completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")