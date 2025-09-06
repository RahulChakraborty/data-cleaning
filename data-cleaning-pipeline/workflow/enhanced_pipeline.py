
# @begin Enhanced_Data_Cleaning_Pipeline_W1
# @desc Comprehensive data cleaning pipeline with profiling, cleaning, validation, and integrity checking
# @in Menu.csv @desc Original menu metadata
# @in MenuPage.csv @desc Original menu page information  
# @in MenuItem.csv @desc Original menu item data
# @in Dish.csv @desc Original dish information
# @out Menu_cleaned.csv @desc Cleaned menu metadata
# @out MenuItem_cleaned.csv @desc Cleaned menu item data
# @out Dish_cleaned.csv @desc Cleaned dish information
# @out menus.db @desc SQLite database with all tables
# @out profiling_charts/ @desc Data quality profiling visualizations
# @out integrity_reports/ @desc Constraint violation reports
# @out validation_results/ @desc Pre/post cleaning comparison results

    # @begin Step1_Data_Loading
    # @desc Load CSV files into pandas DataFrames and import to SQLite database
    # @in Menu.csv
    # @in MenuPage.csv
    # @in MenuItem.csv
    # @in Dish.csv
    # @out menus.db
    # @out Menu_table @desc Menu table in database
    # @out MenuPage_table @desc MenuPage table in database
    # @out MenuItem_table @desc MenuItem table in database
    # @out Dish_table @desc Dish table in database
    # @end Step1_Data_Loading

    # @begin Step2_Data_Profiling
    # @desc Analyze data quality issues using SQL queries and pandas profiling
    # @in Menu_table
    # @in MenuPage_table
    # @in MenuItem_table
    # @in Dish_table
    # @out profiling_report.txt @desc Comprehensive data quality report
    # @out price_distribution_raw.png @desc Raw price distribution histogram
    # @out dish_frequency.png @desc Most frequently appearing dishes
    # @out menu_timeline.png @desc Menu count by year timeline
    # @end Step2_Data_Profiling

    # @begin Step3_Data_Cleaning
    # @desc Apply RegEx transformations, normalization, and OpenRefine-style clustering
    # @in Menu_table
    # @in MenuItem_table
    # @in Dish_table
    # @out Menu_cleaned.csv
    # @out MenuItem_cleaned.csv
    # @out Dish_cleaned.csv
    # @out Menu_cleaned_table @desc Cleaned menu table in database
    # @out MenuItem_cleaned_table @desc Cleaned menu item table in database
    # @out Dish_cleaned_table @desc Cleaned dish table in database

        # @begin Clean_Dish_Names
        # @desc Normalize dish names using RegEx (remove special chars, standardize case)
        # @in Dish_table
        # @out Dish_cleaned_table
        # @end Clean_Dish_Names

        # @begin Standardize_Locations
        # @desc Standardize menu location names for consistency
        # @in Menu_table
        # @out Menu_cleaned_table
        # @end Standardize_Locations

        # @begin Handle_Price_Outliers
        # @desc Cap extreme price outliers using statistical methods
        # @in MenuItem_table
        # @out MenuItem_cleaned_table
        # @end Handle_Price_Outliers

        # @begin Fix_Referential_Integrity
        # @desc Remove orphaned menu items with invalid dish references
        # @in MenuItem_table
        # @in Dish_table
        # @out MenuItem_cleaned_table
        # @end Fix_Referential_Integrity

    # @end Step3_Data_Cleaning

    # @begin Step4_Integrity_Checking
    # @desc Use Logica-style constraints to validate data integrity
    # @in Menu_table
    # @in MenuPage_table
    # @in MenuItem_table
    # @in Dish_table
    # @in Menu_cleaned_table
    # @in MenuItem_cleaned_table
    # @in Dish_cleaned_table
    # @out missing_dish_references.csv @desc Menu items with invalid dish IDs
    # @out missing_menu_references.csv @desc Pages with invalid menu IDs
    # @out missing_page_references.csv @desc Items with invalid page IDs
    # @out invalid_negative_prices.csv @desc Items with negative prices
    # @out inconsistent_price_ranges.csv @desc Items with high_price < price
    # @out extreme_price_outliers.csv @desc Items with prices > $100
    # @out empty_dish_names.csv @desc Dishes with empty names
    # @out duplicate_dish_names.csv @desc Dishes with duplicate names
    # @out empty_menu_pages.csv @desc Pages without menu items
    # @out inconsistent_page_counts.csv @desc Menus with wrong page counts
    # @out inconsistent_dish_counts.csv @desc Menus with wrong dish counts
    # @out anachronistic_dates.csv @desc Menus with dates after 1930
    # @out cleaning_broke_references.csv @desc Cleaning-induced integrity violations
    # @out uncapped_outliers_remain.csv @desc Remaining outliers in cleaned data
    # @out uncleaned_dish_names.csv @desc Inconsistent name formatting
    # @out integrity_summary.csv @desc Summary of all constraint violations
    # @end Step4_Integrity_Checking

    # @begin Step5_Data_Validation
    # @desc Compare pre- and post-cleaning results with comprehensive demo queries
    # @in Menu_table
    # @in MenuItem_table
    # @in Dish_table
    # @in Menu_cleaned_table
    # @in MenuItem_cleaned_table
    # @in Dish_cleaned_table
    # @out price_distribution_comparison.png @desc Before/after price distributions
    # @out comprehensive_validation_dashboard.png @desc Multi-panel comparison dashboard
    # @out validation_summary.csv @desc Comprehensive validation metrics

        # @begin Price_Analysis
        # @desc Compare price statistics and distributions before/after cleaning
        # @in MenuItem_table
        # @in MenuItem_cleaned_table
        # @out price_distribution_comparison.png
        # @end Price_Analysis

        # @begin Seafood_Frequency_Analysis
        # @desc Analyze preservation of seafood dishes through cleaning process
        # @in Dish_table
        # @in Dish_cleaned_table
        # @out seafood_preservation_report.txt
        # @end Seafood_Frequency_Analysis

        # @begin Timeline_Analysis
        # @desc Verify menu timeline preservation across cleaning
        # @in Menu_table
        # @in Menu_cleaned_table
        # @out timeline_comparison.txt
        # @end Timeline_Analysis

        # @begin Location_Standardization_Impact
        # @desc Measure impact of location standardization
        # @in Menu_table
        # @in Menu_cleaned_table
        # @out location_consolidation_report.txt
        # @end Location_Standardization_Impact

        # @begin Name_Cleaning_Effectiveness
        # @desc Analyze effectiveness of dish name cleaning
        # @in Dish_table
        # @in Dish_cleaned_table
        # @out name_cleaning_report.txt
        # @end Name_Cleaning_Effectiveness

        # @begin Outlier_Handling_Validation
        # @desc Validate price outlier handling effectiveness
        # @in MenuItem_table
        # @in MenuItem_cleaned_table
        # @out outlier_handling_report.txt
        # @end Outlier_Handling_Validation

        # @begin Completeness_Analysis
        # @desc Analyze data completeness before/after cleaning
        # @in MenuItem_table
        # @in MenuItem_cleaned_table
        # @out completeness_report.txt
        # @end Completeness_Analysis

        # @begin Referential_Integrity_Improvement
        # @desc Measure referential integrity improvements
        # @in MenuItem_table
        # @in MenuItem_cleaned_table
        # @in Dish_table
        # @in Dish_cleaned_table
        # @out integrity_improvement_report.txt
        # @end Referential_Integrity_Improvement

    # @end Step5_Data_Validation

    # @begin Step6_Documentation_Visualization
    # @desc Generate comprehensive documentation and workflow visualizations
    # @in profiling_charts/
    # @in integrity_reports/
    # @in validation_results/
    # @out enhanced_pipeline.yw @desc This comprehensive YesWorkflow documentation
    # @out pipeline_workflow_diagram.png @desc Visual workflow diagram
    # @out data_lineage_diagram.png @desc Data lineage and provenance diagram
    # @out final_pipeline_report.md @desc Complete pipeline execution report
    # @end Step6_Documentation_Visualization

# @end Enhanced_Data_Cleaning_Pipeline_W1

