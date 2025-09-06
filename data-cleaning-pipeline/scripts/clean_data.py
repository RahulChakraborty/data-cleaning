import pandas as pd
import re

df = pd.read_csv('../data/Dish.csv')
df['name'] = df['name'].str.lower().str.replace(r'[^a-z\s]', '', regex=True)
df.to_csv('../data/Dish_cleaned.csv', index=False)

print("Dish names cleaned using RegEx.")
