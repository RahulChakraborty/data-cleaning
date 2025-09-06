import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('../data/Dish_cleaned.csv')
df['lowest_price'].dropna().hist()
plt.title("Price Distribution After Cleaning")
plt.savefig('../data/price_distribution.png')
print("Validation histogram saved.")
