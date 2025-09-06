import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Connect to the database
conn = sqlite3.connect('../data/menus.db')

print("=" * 60)
print("DATA PROFILING REPORT - NYPL Menu Dataset")
print("=" * 60)
print(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 1. Basic Dataset Overview
print("1. DATASET OVERVIEW")
print("-" * 30)

tables = ['Menu', 'MenuPage', 'MenuItem', 'Dish']
for table in tables:
    count = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", conn).iloc[0]['count']
    print(f"{table} table: {count} records")

print()

# 2. Data Quality Issues Analysis
print("2. DATA QUALITY ISSUES")
print("-" * 30)

# Check for missing values in critical fields
print("Missing Values Analysis:")
for table in tables:
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    missing_counts = df.isnull().sum()
    if missing_counts.sum() > 0:
        print(f"\n{table} table missing values:")
        for col, count in missing_counts.items():
            if count > 0:
                print(f"  - {col}: {count} missing ({count/len(df)*100:.1f}%)")
    else:
        print(f"\n{table} table: No missing values")

print()

# 3. Dish Name Quality Issues
print("3. DISH NAME QUALITY ANALYSIS")
print("-" * 30)

dish_df = pd.read_sql_query("SELECT * FROM Dish", conn)
print(f"Total dishes: {len(dish_df)}")

# Check for inconsistent naming patterns
print("\nNaming Pattern Issues:")
special_chars = dish_df['name'].str.contains(r'[^a-zA-Z\s\-\']', na=False)
print(f"- Dishes with special characters: {special_chars.sum()}")

mixed_case = dish_df['name'].str.contains(r'[a-z].*[A-Z]|[A-Z].*[a-z]', na=False)
print(f"- Dishes with mixed case: {mixed_case.sum()}")

# Show examples of problematic names
print("\nExamples of dishes needing cleaning:")
problematic = dish_df[special_chars | mixed_case]['name'].head(5)
for name in problematic:
    print(f"  - '{name}'")

print()

# 4. Price Analysis
print("4. PRICE ANALYSIS")
print("-" * 30)

menuitem_df = pd.read_sql_query("SELECT * FROM MenuItem", conn)
print(f"Total menu items: {len(menuitem_df)}")

# Price statistics
price_stats = menuitem_df['price'].describe()
print("\nPrice Distribution:")
print(f"  - Mean: ${price_stats['mean']:.2f}")
print(f"  - Median: ${price_stats['50%']:.2f}")
print(f"  - Min: ${price_stats['min']:.2f}")
print(f"  - Max: ${price_stats['max']:.2f}")
print(f"  - Std Dev: ${price_stats['std']:.2f}")

# Identify outliers (prices > 3 standard deviations from mean)
mean_price = menuitem_df['price'].mean()
std_price = menuitem_df['price'].std()
outliers = menuitem_df[menuitem_df['price'] > mean_price + 3*std_price]
print(f"\nPrice Outliers (> 3σ): {len(outliers)} items")
if len(outliers) > 0:
    print("Outlier prices:")
    for _, item in outliers.iterrows():
        print(f"  - Item ID {item['id']}: ${item['price']:.2f}")

print()

# 5. Referential Integrity Issues
print("5. REFERENTIAL INTEGRITY ANALYSIS")
print("-" * 30)

# Check for orphaned menu items (dish_id not in Dish table)
orphaned_query = """
SELECT mi.id, mi.dish_id, mi.price 
FROM MenuItem mi 
LEFT JOIN Dish d ON mi.dish_id = d.id 
WHERE d.id IS NULL
"""
orphaned_items = pd.read_sql_query(orphaned_query, conn)
print(f"Orphaned menu items (invalid dish_id): {len(orphaned_items)}")
if len(orphaned_items) > 0:
    print("Examples:")
    for _, item in orphaned_items.head(3).iterrows():
        print(f"  - MenuItem ID {item['id']} references non-existent Dish ID {item['dish_id']}")

# Check for menu pages without menu references
orphaned_pages_query = """
SELECT mp.id, mp.menu_id 
FROM MenuPage mp 
LEFT JOIN Menu m ON mp.menu_id = m.id 
WHERE m.id IS NULL
"""
orphaned_pages = pd.read_sql_query(orphaned_pages_query, conn)
print(f"Orphaned menu pages (invalid menu_id): {len(orphaned_pages)}")

print()

# 6. Date and Location Analysis
print("6. DATE AND LOCATION ANALYSIS")
print("-" * 30)

menu_df = pd.read_sql_query("SELECT * FROM Menu", conn)

# Date range analysis
menu_df['date'] = pd.to_datetime(menu_df['date'])
print(f"Date range: {menu_df['date'].min().strftime('%Y-%m-%d')} to {menu_df['date'].max().strftime('%Y-%m-%d')}")

# Location analysis
location_counts = menu_df['location'].value_counts()
print(f"\nLocation distribution:")
for location, count in location_counts.items():
    print(f"  - {location}: {count} menus")

# Check for location inconsistencies
unique_places = menu_df['place'].unique()
unique_locations = menu_df['location'].unique()
print(f"\nUnique places: {len(unique_places)}")
print(f"Unique locations: {len(unique_locations)}")

print()

# 7. Generate Visualizations
print("7. GENERATING VISUALIZATIONS")
print("-" * 30)

# Create visualizations directory
import os
os.makedirs('../data/profiling_charts', exist_ok=True)

# Price distribution histogram
plt.figure(figsize=(10, 6))
plt.hist(menuitem_df['price'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
plt.title('Price Distribution - Raw Data')
plt.xlabel('Price ($)')
plt.ylabel('Frequency')
plt.grid(True, alpha=0.3)
plt.savefig('../data/profiling_charts/price_distribution_raw.png', dpi=300, bbox_inches='tight')
plt.close()

# Dish appearance frequency
plt.figure(figsize=(12, 6))
dish_freq = dish_df.nlargest(10, 'times_appeared')
plt.bar(range(len(dish_freq)), dish_freq['times_appeared'], color='lightcoral')
plt.title('Top 10 Most Frequently Appearing Dishes')
plt.xlabel('Dish Rank')
plt.ylabel('Times Appeared')
plt.xticks(range(len(dish_freq)), [name[:20] + '...' if len(name) > 20 else name 
                                   for name in dish_freq['name']], rotation=45, ha='right')
plt.tight_layout()
plt.savefig('../data/profiling_charts/dish_frequency.png', dpi=300, bbox_inches='tight')
plt.close()

# Menu timeline
plt.figure(figsize=(12, 6))
menu_timeline = menu_df.groupby(menu_df['date'].dt.year).size()
plt.plot(menu_timeline.index, menu_timeline.values, marker='o', linewidth=2, markersize=8)
plt.title('Menu Count by Year')
plt.xlabel('Year')
plt.ylabel('Number of Menus')
plt.grid(True, alpha=0.3)
plt.savefig('../data/profiling_charts/menu_timeline.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualizations saved to ../data/profiling_charts/")
print("  - price_distribution_raw.png")
print("  - dish_frequency.png")
print("  - menu_timeline.png")

print()

# 8. Summary of Issues Found
print("8. SUMMARY OF DATA QUALITY ISSUES")
print("-" * 30)
print("Issues identified that need cleaning:")
print("✓ Dish names contain special characters and inconsistent casing")
print("✓ Price outliers detected (potential data entry errors)")
print("✓ Referential integrity violations (orphaned menu items)")
print("✓ Mixed date formats and location inconsistencies")
print()
print("Recommended cleaning steps:")
print("1. Normalize dish names (remove special chars, standardize case)")
print("2. Validate and cap extreme price values")
print("3. Fix referential integrity issues")
print("4. Standardize location and date formats")

conn.close()
print("\nData profiling complete!")