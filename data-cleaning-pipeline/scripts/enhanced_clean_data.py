import pandas as pd
import sqlite3
import re
import numpy as np
from datetime import datetime
import difflib

print("=" * 60)
print("ENHANCED DATA CLEANING - NYPL Menu Dataset")
print("=" * 60)
print(f"Started on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Connect to the database
conn = sqlite3.connect('../data/menus.db')

# ============================================================================
# STEP 3A: DISH NAME CLEANING AND NORMALIZATION
# ============================================================================
print("STEP 3A: DISH NAME CLEANING AND NORMALIZATION")
print("-" * 50)

# Load dish data
dish_df = pd.read_sql_query("SELECT * FROM Dish", conn)
print(f"Processing {len(dish_df)} dishes...")

# Create a copy for cleaning
dish_cleaned = dish_df.copy()

# Function to clean dish names (similar to OpenRefine clustering)
def clean_dish_name(name):
    if pd.isna(name):
        return name
    
    # Convert to string if not already
    name = str(name)
    
    # Step 1: Remove special characters except apostrophes and hyphens
    name = re.sub(r'[^\w\s\'-]', '', name)
    
    # Step 2: Normalize whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Step 3: Convert to title case for consistency
    name = name.title()
    
    # Step 4: Handle common abbreviations and standardizations
    abbreviations = {
        r'\bA La\b': 'à la',
        r'\bDe\b': 'de',
        r'\bDu\b': 'du',
        r'\bEn\b': 'en',
        r'\bAu\b': 'au',
        r'\bAux\b': 'aux',
        r'\bLe\b': 'le',
        r'\bLa\b': 'la',
        r'\bLes\b': 'les'
    }
    
    for pattern, replacement in abbreviations.items():
        name = re.sub(pattern, replacement, name, flags=re.IGNORECASE)
    
    return name

# Apply cleaning to dish names
print("Cleaning dish names...")
dish_cleaned['name_original'] = dish_cleaned['name']
dish_cleaned['name'] = dish_cleaned['name'].apply(clean_dish_name)

# Show cleaning results
print("\nDish name cleaning results:")
for i, row in dish_cleaned.iterrows():
    if row['name_original'] != row['name']:
        print(f"  '{row['name_original']}' → '{row['name']}'")

# ============================================================================
# STEP 3B: MENU LOCATION STANDARDIZATION
# ============================================================================
print("\nSTEP 3B: MENU LOCATION STANDARDIZATION")
print("-" * 50)

# Load menu data
menu_df = pd.read_sql_query("SELECT * FROM Menu", conn)
print(f"Processing {len(menu_df)} menus...")

# Create a copy for cleaning
menu_cleaned = menu_df.copy()

# Function to standardize locations
def standardize_location(location):
    if pd.isna(location):
        return location
    
    location = str(location).strip()
    
    # Standardize common location patterns
    location_mappings = {
        r'(?i)manhattan': 'Manhattan',
        r'(?i)times\s+square': 'Times Square',
        r'(?i)fifth\s+avenue': 'Fifth Avenue',
        r'(?i)madison\s+avenue': 'Madison Avenue',
        r'(?i)central\s+park\s+south': 'Central Park South',
        r'(?i)broadway': 'Broadway',
        r'(?i)wall\s+street': 'Wall Street'
    }
    
    for pattern, replacement in location_mappings.items():
        location = re.sub(pattern, replacement, location)
    
    return location

# Apply location standardization
print("Standardizing menu locations...")
menu_cleaned['location_original'] = menu_cleaned['location']
menu_cleaned['location'] = menu_cleaned['location'].apply(standardize_location)

# Show location standardization results
print("\nLocation standardization results:")
for i, row in menu_cleaned.iterrows():
    if row['location_original'] != row['location']:
        print(f"  '{row['location_original']}' → '{row['location']}'")

# ============================================================================
# STEP 3C: PRICE VALIDATION AND OUTLIER HANDLING
# ============================================================================
print("\nSTEP 3C: PRICE VALIDATION AND OUTLIER HANDLING")
print("-" * 50)

# Load menu item data
menuitem_df = pd.read_sql_query("SELECT * FROM MenuItem", conn)
print(f"Processing {len(menuitem_df)} menu items...")

# Create a copy for cleaning
menuitem_cleaned = menuitem_df.copy()

# Calculate price statistics for outlier detection
price_stats = menuitem_cleaned['price'].describe()
mean_price = price_stats['mean']
std_price = price_stats['std']
upper_bound = mean_price + 3 * std_price

print(f"Price statistics:")
print(f"  Mean: ${mean_price:.2f}")
print(f"  Std Dev: ${std_price:.2f}")
print(f"  Upper bound (3σ): ${upper_bound:.2f}")

# Identify and handle outliers
outliers = menuitem_cleaned['price'] > upper_bound
outlier_count = outliers.sum()
print(f"\nFound {outlier_count} price outliers")

if outlier_count > 0:
    print("Outlier prices before cleaning:")
    for idx, row in menuitem_cleaned[outliers].iterrows():
        print(f"  Item ID {row['id']}: ${row['price']:.2f}")
    
    # Cap outliers at the upper bound (conservative approach)
    menuitem_cleaned.loc[outliers, 'price_original'] = menuitem_cleaned.loc[outliers, 'price']
    menuitem_cleaned.loc[outliers, 'price'] = upper_bound
    
    print(f"\nCapped {outlier_count} outlier prices to ${upper_bound:.2f}")

# ============================================================================
# STEP 3D: REFERENTIAL INTEGRITY FIXES
# ============================================================================
print("\nSTEP 3D: REFERENTIAL INTEGRITY FIXES")
print("-" * 50)

# Find orphaned menu items
orphaned_query = """
SELECT mi.id, mi.dish_id, mi.price 
FROM MenuItem mi 
LEFT JOIN Dish d ON mi.dish_id = d.id 
WHERE d.id IS NULL
"""
orphaned_items = pd.read_sql_query(orphaned_query, conn)
print(f"Found {len(orphaned_items)} orphaned menu items")

if len(orphaned_items) > 0:
    print("Orphaned menu items:")
    for _, item in orphaned_items.iterrows():
        print(f"  MenuItem ID {item['id']} references non-existent Dish ID {item['dish_id']}")
    
    # Remove orphaned menu items from cleaned dataset
    orphaned_ids = orphaned_items['id'].tolist()
    menuitem_cleaned = menuitem_cleaned[~menuitem_cleaned['id'].isin(orphaned_ids)]
    print(f"Removed {len(orphaned_ids)} orphaned menu items from cleaned dataset")

# ============================================================================
# STEP 3E: STRING CLUSTERING SIMULATION (OpenRefine-style)
# ============================================================================
print("\nSTEP 3E: STRING CLUSTERING ANALYSIS")
print("-" * 50)

def find_similar_strings(strings, threshold=0.8):
    """Find groups of similar strings (simulates OpenRefine clustering)"""
    clusters = []
    processed = set()
    
    for i, string1 in enumerate(strings):
        if string1 in processed:
            continue
            
        cluster = [string1]
        processed.add(string1)
        
        for j, string2 in enumerate(strings[i+1:], i+1):
            if string2 in processed:
                continue
                
            similarity = difflib.SequenceMatcher(None, string1.lower(), string2.lower()).ratio()
            if similarity >= threshold:
                cluster.append(string2)
                processed.add(string2)
        
        if len(cluster) > 1:
            clusters.append(cluster)
    
    return clusters

# Analyze dish name clusters
dish_names = dish_cleaned['name'].dropna().unique()
dish_clusters = find_similar_strings(dish_names, threshold=0.7)

print(f"Found {len(dish_clusters)} potential dish name clusters:")
for i, cluster in enumerate(dish_clusters, 1):
    print(f"  Cluster {i}: {cluster}")

# Analyze location clusters
locations = menu_cleaned['location'].dropna().unique()
location_clusters = find_similar_strings(locations, threshold=0.7)

print(f"\nFound {len(location_clusters)} potential location clusters:")
for i, cluster in enumerate(location_clusters, 1):
    print(f"  Cluster {i}: {cluster}")

# ============================================================================
# STEP 3F: SAVE CLEANED DATA
# ============================================================================
print("\nSTEP 3F: SAVING CLEANED DATA")
print("-" * 50)

# Save cleaned data to new CSV files
dish_cleaned.to_csv('../data/Dish_cleaned.csv', index=False)
menu_cleaned.to_csv('../data/Menu_cleaned.csv', index=False)
menuitem_cleaned.to_csv('../data/MenuItem_cleaned.csv', index=False)

print("Cleaned data saved to:")
print("  - ../data/Dish_cleaned.csv")
print("  - ../data/Menu_cleaned.csv")
print("  - ../data/MenuItem_cleaned.csv")

# Update database with cleaned data
print("\nUpdating database with cleaned data...")
dish_cleaned.to_sql('Dish_cleaned', conn, if_exists='replace', index=False)
menu_cleaned.to_sql('Menu_cleaned', conn, if_exists='replace', index=False)
menuitem_cleaned.to_sql('MenuItem_cleaned', conn, if_exists='replace', index=False)

print("Database updated with cleaned tables:")
print("  - Dish_cleaned")
print("  - Menu_cleaned")
print("  - MenuItem_cleaned")

# ============================================================================
# STEP 3G: CLEANING SUMMARY REPORT
# ============================================================================
print("\nSTEP 3G: CLEANING SUMMARY REPORT")
print("-" * 50)

print("Data cleaning completed successfully!")
print("\nSummary of changes:")
print(f"✓ Cleaned {len(dish_df)} dish names (standardized case, removed special chars)")
print(f"✓ Standardized {len(menu_df)} menu locations")
print(f"✓ Capped {outlier_count} price outliers")
print(f"✓ Removed {len(orphaned_items)} orphaned menu items")
print(f"✓ Identified {len(dish_clusters)} dish name clusters for potential merging")
print(f"✓ Identified {len(location_clusters)} location clusters for standardization")

print(f"\nOriginal dataset sizes:")
print(f"  - Dishes: {len(dish_df)}")
print(f"  - Menus: {len(menu_df)}")
print(f"  - Menu Items: {len(menuitem_df)}")

print(f"\nCleaned dataset sizes:")
print(f"  - Dishes: {len(dish_cleaned)}")
print(f"  - Menus: {len(menu_cleaned)}")
print(f"  - Menu Items: {len(menuitem_cleaned)}")

conn.close()
print(f"\nData cleaning completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")