import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

print("=" * 60)
print("DATA VALIDATION & DEMO QUERIES - NYPL Menu Dataset")
print("=" * 60)
print(f"Started on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Connect to the database
conn = sqlite3.connect('../data/menus.db')

# Create output directory for validation results
os.makedirs('../data/validation_results', exist_ok=True)

# ============================================================================
# LOAD ORIGINAL AND CLEANED DATA
# ============================================================================
print("LOADING ORIGINAL AND CLEANED DATASETS")
print("-" * 50)

# Original data
menu_orig = pd.read_sql_query("SELECT * FROM Menu", conn)
menuitem_orig = pd.read_sql_query("SELECT * FROM MenuItem", conn)
dish_orig = pd.read_sql_query("SELECT * FROM Dish", conn)

# Cleaned data
menu_clean = pd.read_sql_query("SELECT * FROM Menu_cleaned", conn)
menuitem_clean = pd.read_sql_query("SELECT * FROM MenuItem_cleaned", conn)
dish_clean = pd.read_sql_query("SELECT * FROM Dish_cleaned", conn)

print(f"Original dataset: {len(menu_orig)} menus, {len(menuitem_orig)} items, {len(dish_orig)} dishes")
print(f"Cleaned dataset:  {len(menu_clean)} menus, {len(menuitem_clean)} items, {len(dish_clean)} dishes")
print()

# ============================================================================
# DEMO QUERY 1: DISH PRICE ANALYSIS
# ============================================================================
print("DEMO QUERY 1: DISH PRICE ANALYSIS")
print("-" * 50)

print("Comparing price statistics before and after cleaning:")

# Original price stats
orig_price_stats = menuitem_orig['price'].describe()
clean_price_stats = menuitem_clean['price'].describe()

comparison_df = pd.DataFrame({
    'Original': orig_price_stats,
    'Cleaned': clean_price_stats,
    'Change': clean_price_stats - orig_price_stats
})

print(comparison_df.round(2))
print()

# Price distribution comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

ax1.hist(menuitem_orig['price'], bins=20, alpha=0.7, color='red', label='Original')
ax1.set_title('Original Price Distribution')
ax1.set_xlabel('Price ($)')
ax1.set_ylabel('Frequency')
ax1.grid(True, alpha=0.3)

ax2.hist(menuitem_clean['price'], bins=20, alpha=0.7, color='green', label='Cleaned')
ax2.set_title('Cleaned Price Distribution')
ax2.set_xlabel('Price ($)')
ax2.set_ylabel('Frequency')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('../data/validation_results/price_distribution_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

print("Price distribution comparison saved to: price_distribution_comparison.png")
print()

# ============================================================================
# DEMO QUERY 2: SEAFOOD FREQUENCY ANALYSIS
# ============================================================================
print("DEMO QUERY 2: SEAFOOD FREQUENCY ANALYSIS")
print("-" * 50)

# Define seafood keywords
seafood_keywords = ['oyster', 'lobster', 'fish', 'salmon', 'cod', 'sole', 'shrimp', 'crab', 'turtle', 'terrapin']

def count_seafood_dishes(dish_df, name_col='name'):
    """Count dishes containing seafood keywords"""
    seafood_count = 0
    seafood_dishes = []
    
    for _, dish in dish_df.iterrows():
        dish_name = str(dish[name_col]).lower()
        for keyword in seafood_keywords:
            if keyword in dish_name:
                seafood_count += 1
                seafood_dishes.append(dish[name_col])
                break
    
    return seafood_count, seafood_dishes

# Count seafood dishes in original and cleaned data
orig_seafood_count, orig_seafood_dishes = count_seafood_dishes(dish_orig)
clean_seafood_count, clean_seafood_dishes = count_seafood_dishes(dish_clean)

print(f"Seafood dishes in original dataset: {orig_seafood_count}")
print("Original seafood dishes:")
for dish in orig_seafood_dishes:
    print(f"  - {dish}")

print(f"\nSeafood dishes in cleaned dataset: {clean_seafood_count}")
print("Cleaned seafood dishes:")
for dish in clean_seafood_dishes:
    print(f"  - {dish}")

print(f"\nSeafood dish preservation rate: {clean_seafood_count/orig_seafood_count*100:.1f}%")
print()

# ============================================================================
# DEMO QUERY 3: MENU TIMELINE ANALYSIS
# ============================================================================
print("DEMO QUERY 3: MENU TIMELINE ANALYSIS")
print("-" * 50)

# Convert dates and analyze timeline
menu_orig['date'] = pd.to_datetime(menu_orig['date'])
menu_clean['date'] = pd.to_datetime(menu_clean['date'])

# Group by year
orig_timeline = menu_orig.groupby(menu_orig['date'].dt.year).agg({
    'id': 'count',
    'dish_count': 'sum'
}).rename(columns={'id': 'menu_count', 'dish_count': 'total_dishes'})

clean_timeline = menu_clean.groupby(menu_clean['date'].dt.year).agg({
    'id': 'count',
    'dish_count': 'sum'
}).rename(columns={'id': 'menu_count', 'dish_count': 'total_dishes'})

print("Menu timeline comparison:")
timeline_comparison = pd.DataFrame({
    'Original_Menus': orig_timeline['menu_count'],
    'Cleaned_Menus': clean_timeline['menu_count'],
    'Original_Dishes': orig_timeline['total_dishes'],
    'Cleaned_Dishes': clean_timeline['total_dishes']
})

print(timeline_comparison)
print()

# ============================================================================
# DEMO QUERY 4: LOCATION STANDARDIZATION IMPACT
# ============================================================================
print("DEMO QUERY 4: LOCATION STANDARDIZATION IMPACT")
print("-" * 50)

print("Location distribution before cleaning:")
orig_locations = menu_orig['location'].value_counts()
print(orig_locations)

print("\nLocation distribution after cleaning:")
clean_locations = menu_clean['location'].value_counts()
print(clean_locations)

print(f"\nUnique locations before: {len(orig_locations)}")
print(f"Unique locations after: {len(clean_locations)}")
print(f"Location consolidation: {len(orig_locations) - len(clean_locations)} locations merged")
print()

# ============================================================================
# DEMO QUERY 5: DISH NAME CLEANING EFFECTIVENESS
# ============================================================================
print("DEMO QUERY 5: DISH NAME CLEANING EFFECTIVENESS")
print("-" * 50)

# Analyze character patterns in dish names
def analyze_name_patterns(dish_df, name_col='name'):
    """Analyze character patterns in dish names"""
    names = dish_df[name_col].dropna()
    
    special_chars = sum(1 for name in names if any(c for c in str(name) if not c.isalnum() and c not in [' ', '-', "'"]))
    mixed_case = sum(1 for name in names if str(name) != str(name).title() and str(name) != str(name).lower())
    
    return {
        'total_names': len(names),
        'with_special_chars': special_chars,
        'mixed_case': mixed_case,
        'special_char_rate': special_chars / len(names) * 100,
        'mixed_case_rate': mixed_case / len(names) * 100
    }

orig_patterns = analyze_name_patterns(dish_orig)
clean_patterns = analyze_name_patterns(dish_clean)

print("Dish name pattern analysis:")
pattern_comparison = pd.DataFrame({
    'Original': [orig_patterns['with_special_chars'], orig_patterns['mixed_case'], 
                orig_patterns['special_char_rate'], orig_patterns['mixed_case_rate']],
    'Cleaned': [clean_patterns['with_special_chars'], clean_patterns['mixed_case'],
               clean_patterns['special_char_rate'], clean_patterns['mixed_case_rate']]
}, index=['Special Characters', 'Mixed Case', 'Special Char Rate (%)', 'Mixed Case Rate (%)'])

print(pattern_comparison.round(2))
print()

# Show examples of name transformations
print("Examples of dish name transformations:")
for i, (orig_row, clean_row) in enumerate(zip(dish_orig.itertuples(), dish_clean.itertuples())):
    if orig_row.name != clean_row.name:
        print(f"  '{orig_row.name}' → '{clean_row.name}'")

print()

# ============================================================================
# DEMO QUERY 6: PRICE OUTLIER HANDLING
# ============================================================================
print("DEMO QUERY 6: PRICE OUTLIER HANDLING")
print("-" * 50)

# Identify outliers using IQR method
def identify_outliers(prices):
    Q1 = prices.quantile(0.25)
    Q3 = prices.quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    return prices[(prices < lower_bound) | (prices > upper_bound)]

orig_outliers = identify_outliers(menuitem_orig['price'])
clean_outliers = identify_outliers(menuitem_clean['price'])

print(f"Price outliers in original data: {len(orig_outliers)}")
if len(orig_outliers) > 0:
    print("Original outliers:")
    for price in orig_outliers:
        print(f"  ${price:.2f}")

print(f"\nPrice outliers in cleaned data: {len(clean_outliers)}")
if len(clean_outliers) > 0:
    print("Cleaned outliers:")
    for price in clean_outliers:
        print(f"  ${price:.2f}")

print(f"\nOutlier reduction: {len(orig_outliers) - len(clean_outliers)} outliers handled")
print()

# ============================================================================
# DEMO QUERY 7: DATA COMPLETENESS ANALYSIS
# ============================================================================
print("DEMO QUERY 7: DATA COMPLETENESS ANALYSIS")
print("-" * 50)

def calculate_completeness(df):
    """Calculate data completeness metrics"""
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    completeness = (total_cells - missing_cells) / total_cells * 100
    return completeness, missing_cells, total_cells

orig_completeness, orig_missing, orig_total = calculate_completeness(menuitem_orig)
clean_completeness, clean_missing, clean_total = calculate_completeness(menuitem_clean)

print("Data completeness analysis:")
completeness_df = pd.DataFrame({
    'Original': [orig_total, orig_missing, orig_completeness],
    'Cleaned': [clean_total, clean_missing, clean_completeness]
}, index=['Total Cells', 'Missing Cells', 'Completeness (%)'])

print(completeness_df.round(2))
print()

# ============================================================================
# DEMO QUERY 8: REFERENTIAL INTEGRITY IMPROVEMENT
# ============================================================================
print("DEMO QUERY 8: REFERENTIAL INTEGRITY IMPROVEMENT")
print("-" * 50)

# Check referential integrity
orig_orphans = menuitem_orig[~menuitem_orig['dish_id'].isin(dish_orig['id'])]
clean_orphans = menuitem_clean[~menuitem_clean['dish_id'].isin(dish_clean['id'])]

print(f"Orphaned menu items in original data: {len(orig_orphans)}")
print(f"Orphaned menu items in cleaned data: {len(clean_orphans)}")
print(f"Referential integrity improvement: {len(orig_orphans) - len(clean_orphans)} orphans resolved")
print()

# ============================================================================
# COMPREHENSIVE VALIDATION SUMMARY
# ============================================================================
print("COMPREHENSIVE VALIDATION SUMMARY")
print("-" * 50)

# Create comprehensive summary
validation_summary = {
    'Dataset Size': {
        'Original Menus': len(menu_orig),
        'Cleaned Menus': len(menu_clean),
        'Original Items': len(menuitem_orig),
        'Cleaned Items': len(menuitem_clean),
        'Original Dishes': len(dish_orig),
        'Cleaned Dishes': len(dish_clean)
    },
    'Data Quality Improvements': {
        'Price Outliers Handled': len(orig_outliers) - len(clean_outliers),
        'Orphaned Items Removed': len(orig_orphans) - len(clean_orphans),
        'Locations Standardized': len(orig_locations) - len(clean_locations),
        'Dish Names Cleaned': sum(1 for i, (o, c) in enumerate(zip(dish_orig['name'], dish_clean['name'])) if o != c)
    },
    'Data Preservation': {
        'Seafood Dishes Preserved': f"{clean_seafood_count}/{orig_seafood_count} ({clean_seafood_count/orig_seafood_count*100:.1f}%)",
        'Menu Timeline Preserved': 'Yes' if len(orig_timeline) == len(clean_timeline) else 'No',
        'Data Completeness': f"{clean_completeness:.1f}%"
    }
}

print("VALIDATION RESULTS:")
for category, metrics in validation_summary.items():
    print(f"\n{category}:")
    for metric, value in metrics.items():
        print(f"  {metric}: {value}")

# Save validation summary to CSV
summary_rows = []
for category, metrics in validation_summary.items():
    for metric, value in metrics.items():
        summary_rows.append({'Category': category, 'Metric': metric, 'Value': value})

summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv('../data/validation_results/validation_summary.csv', index=False)

print(f"\nValidation summary saved to: validation_summary.csv")

# ============================================================================
# GENERATE FINAL COMPARISON VISUALIZATIONS
# ============================================================================
print("\nGENERATING FINAL COMPARISON VISUALIZATIONS")
print("-" * 50)

# Create a comprehensive comparison dashboard
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

# 1. Price distribution comparison
ax1.hist(menuitem_orig['price'], bins=15, alpha=0.6, color='red', label='Original', density=True)
ax1.hist(menuitem_clean['price'], bins=15, alpha=0.6, color='green', label='Cleaned', density=True)
ax1.set_title('Price Distribution Comparison')
ax1.set_xlabel('Price ($)')
ax1.set_ylabel('Density')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Data completeness comparison
categories = ['Original', 'Cleaned']
completeness_values = [orig_completeness, clean_completeness]
ax2.bar(categories, completeness_values, color=['red', 'green'], alpha=0.7)
ax2.set_title('Data Completeness Comparison')
ax2.set_ylabel('Completeness (%)')
ax2.set_ylim(0, 100)
for i, v in enumerate(completeness_values):
    ax2.text(i, v + 1, f'{v:.1f}%', ha='center', va='bottom')

# 3. Seafood dish preservation
seafood_data = [orig_seafood_count, clean_seafood_count]
ax3.bar(categories, seafood_data, color=['red', 'green'], alpha=0.7)
ax3.set_title('Seafood Dishes Preservation')
ax3.set_ylabel('Number of Seafood Dishes')
for i, v in enumerate(seafood_data):
    ax3.text(i, v + 0.1, str(v), ha='center', va='bottom')

# 4. Data quality metrics
metrics = ['Outliers', 'Orphans', 'Locations']
orig_values = [len(orig_outliers), len(orig_orphans), len(orig_locations)]
clean_values = [len(clean_outliers), len(clean_orphans), len(clean_locations)]

x = np.arange(len(metrics))
width = 0.35

ax4.bar(x - width/2, orig_values, width, label='Original', color='red', alpha=0.7)
ax4.bar(x + width/2, clean_values, width, label='Cleaned', color='green', alpha=0.7)
ax4.set_title('Data Quality Metrics Comparison')
ax4.set_ylabel('Count')
ax4.set_xticks(x)
ax4.set_xticklabels(metrics)
ax4.legend()

plt.tight_layout()
plt.savefig('../data/validation_results/comprehensive_validation_dashboard.png', dpi=300, bbox_inches='tight')
plt.close()

print("Comprehensive validation dashboard saved to: comprehensive_validation_dashboard.png")

conn.close()
print(f"\nData validation and demo queries completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\nAll validation results saved to: ../data/validation_results/")