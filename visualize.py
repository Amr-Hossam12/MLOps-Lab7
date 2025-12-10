
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

data = """
Platform,Sales (Millions),Release Year,Genre
PC,100,2019,Action
PS5,150,2020,RPG
Xbox,200,2021,Sports
PC,250,2022,Action
PS5,300,2023,RPG
Xbox,350,2023,Sports
PC,400,2023,Action
PS5,450,2023,RPG
Xbox,500,2023,Sports
PC,550,2023,Action
"""

df = pd.read_csv(StringIO(data), sep=',')

# Aggregate sales by platform
agg_sales = df.groupby('Platform')['Sales (Millions)'].sum().reset_index()

# Create bar chart
plt.figure(figsize=(10, 6))
plt.bar(agg_sales['Platform'], agg_sales['Sales (Millions)'], color='skyblue')

plt.title('Total Sales by Platform')
plt.xlabel('Platform')
plt.ylabel('Sales (Millions)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('chart_output.png')
plt.close()
