import pandas as pd
import sqlite3

conn = sqlite3.connect('../data/menus.db')
data_files = ['Menu', 'MenuPage', 'MenuItem', 'Dish']

for file in data_files:
    df = pd.read_csv(f'../data/{file}.csv')
    df.to_sql(file, conn, if_exists='replace', index=False)

print("All CSVs loaded into SQLite database.")
