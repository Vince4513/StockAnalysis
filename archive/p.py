import pandas as pd
import numpy as np

# Create a list of 5 different dates
dates = pd.date_range('2023-10-10', periods=5, freq='M')

# Create a list of random float values
float_values = np.random.random(5)

# Create the DataFrame with datetime index and float column
df = pd.DataFrame(float_values, index=dates, columns=['Value'])

# Display the DataFrame
print(df)

# Sum the values per year
df_yearly_sum = df.resample('Y').sum()

# Display the result
print(df_yearly_sum)
