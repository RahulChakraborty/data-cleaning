# SQL Integrity Validation Report

**Generated:** 2025-08-02 20:33:53
**Database:** data/menus.db
**Total Violations:** 30

## Summary

⚠️ **30 integrity violations found** across multiple constraints.

## Detailed Results

| Constraint | Status | Violations | Description |
|------------|--------|------------|-------------|
| Missing Dish References | ❌ FAIL | 1 | Menu items referencing non-existent dishes |
| Missing Menu References | ✅ PASS | 0 |  |
| Missing Page References | ✅ PASS | 0 |  |
| Invalid Negative Prices | ✅ PASS | 0 |  |
| Inconsistent Price Ranges | ✅ PASS | 0 |  |
| Extreme Price Outliers | ✅ PASS | 0 |  |
| Empty Dish Names | ✅ PASS | 0 |  |
| Duplicate Dish Names | ✅ PASS | 0 |  |
| Empty Menu Pages | ❌ FAIL | 3 | Menu pages with no menu items |
| Inconsistent Page Counts | ❌ FAIL | 1 | Menus with inconsistent page counts |
| Inconsistent Dish Counts | ❌ FAIL | 5 | Menus with inconsistent dish counts |
| Anachronistic Dates | ✅ PASS | 0 |  |
| Cleaning Broke References | ✅ PASS | 0 |  |
| Uncapped Outliers Remain | ✅ PASS | 0 |  |
| Uncleaned Dish Names | ❌ FAIL | 20 | Dish names not properly title-cased after cleaning |

## Violation Details

### Missing Dish References
**Description:** Menu items referencing non-existent dishes
**Violations:** 1

**Sample violations:**
1. {'menu_item_id': 36, 'dish_id': 99}

### Empty Menu Pages
**Description:** Menu pages with no menu items
**Violations:** 3

**Sample violations:**
1. {'page_id': 3, 'menu_id': 1}
2. {'page_id': 4, 'menu_id': 1}
3. {'page_id': 9, 'menu_id': 3}

### Inconsistent Page Counts
**Description:** Menus with inconsistent page counts
**Violations:** 1

**Sample violations:**
1. {'menu_id': 5, 'declared_count': 5, 'actual_count': 1}

### Inconsistent Dish Counts
**Description:** Menus with inconsistent dish counts
**Violations:** 5

**Sample violations:**
1. {'menu_id': 1, 'declared_count': 25, 'actual_count': 9}
2. {'menu_id': 2, 'declared_count': 18, 'actual_count': 7}
3. {'menu_id': 3, 'declared_count': 22, 'actual_count': 7}
4. {'menu_id': 4, 'declared_count': 15, 'actual_count': 5}
5. {'menu_id': 5, 'declared_count': 35, 'actual_count': 8}

### Uncleaned Dish Names
**Description:** Dish names not properly title-cased after cleaning
**Violations:** 20

**Sample violations:**
1. {'dish_id': 1, 'name': 'Oysters Rockefeller'}
2. {'dish_id': 2, 'name': 'Lobster Thermidor'}
3. {'dish_id': 3, 'name': 'Beef Wellington'}
4. {'dish_id': 4, 'name': 'Consommé Célestine'}
5. {'dish_id': 5, 'name': 'Canvasback Duck'}

## Recommendations

1. Review and address the identified violations
2. Update data cleaning procedures to prevent similar issues
3. Re-run validation after corrections
