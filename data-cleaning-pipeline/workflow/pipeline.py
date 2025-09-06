# @begin Workflow_W1
# @in Menu.csv
# @in MenuPage.csv
# @in MenuItem.csv
# @in Dish.csv
# @out Dish_cleaned.csv
# @out menus.db
# @out price_distribution.png

# @begin Load_CSVs
# @in Menu.csv
# @in MenuPage.csv
# @in MenuItem.csv
# @in Dish.csv
# @out menus.db
# @end Load_CSVs

# @begin Clean_Dishes
# @in Dish.csv
# @out Dish_cleaned.csv
# @end Clean_Dishes

# @begin Validate_Prices
# @in Dish_cleaned.csv
# @out price_distribution.png
# @end Validate_Prices

# @end Workflow_W1
