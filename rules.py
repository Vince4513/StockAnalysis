import os as os
import numpy as np
import pandas as pd

share_actual_price = [25, 25, 20]

# Define sample data for multiple companies
data = {
    'Company': ['Orange', 'Total', 'Nexity'],
    'Sales': [1000000, 1500000, 800000],
    'Current assets': [500000, 700000, 400000],
    'Current liabilities': [200000, 300000, 250000],
    'Financial debts': [300000, 200000, 150000],
    'Number of shares issued': [10000, 1500000, 800000],
    'Shareholders\' equity': [1000000, 1500000, 800000],
    'Intangible assets': [10000, 1500, 8000],
    'Net income 1 year': [150000, 200000, 100000],
    'Net income 2 year': [120000, 180000, 90000],
    'Net income 3 year': [130000, 190000, 95000],
    'Net income 4 year': [150000, 200000, 100000],
    'Net income 5 year': [120000, 180000, 90000],
    'Net income 6 year': [130000, -190000, 95000],
    'Net income 7 year': [150000, 200000, 100000],
    'Net income 8 year': [120000, 180000, 90000],
    'Net income 9 year': [130000, 190000, 95000],
    'Net income 10 year': [130000, 190000, 95000],
    'Dividends 1 year': [1.5, 2, 1],
    'Dividends 2 year': [1.2, 1.8, 0.9],
    'Dividends 3 year': [1.3, 1.9, 0.95],
    'Dividends 4 year': [1.5, 2, 1],
    'Dividends 5 year': [1.2, 1.8, 0.9],
    'Dividends 6 year': [1.3, 1.9, 0.95],
    'Dividends 7 year': [1.5, 2, 1],
    'Dividends 8 year': [1.2, 1.8, 0.9],
    'Dividends 9 year': [1.3, 1.9, np.nan],
    'Dividends 10 year': [1.3, 1.9, 0.95],
    'Net earnings per share 1 year': [1.5, 2.0, 1.0],
    'Net earnings per share 2 year': [1.5, 2.1, 1.1],
    'Net earnings per share 3 year': [1.5, 2.2, 1.2],
    'Net earnings per share 4 year': [1.0, 1.0, 1.0],
    'Net earnings per share 5 year': [1.0, 1.0, 1.0],
    'Net earnings per share 6 year': [1.0, 1.0, 1.0],
    'Net earnings per share 7 year': [1.0, 1.0, 1.0],
    'Net earnings per share 8 year': [1.7, 1.5, 1.8],
    'Net earnings per share 9 year': [1.8, 1.4, 1.9],
    'Net earnings per share 10 year': [1.9, 1.3, 1.9]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Display the DataFrame
print(df.shape, df.info(verbose=False, memory_usage=True))

# 1st Rule ---------------------------------------------------------------
# Check if Sales (CA) > 1000 for each company
sales_greater_100M = df['Sales'] > 1000000

# Create a new DataFrame with True/False values based on the condition
df_rules = pd.DataFrame({
    'Company': df['Company'],
    'first_rule': sales_greater_100M
})

# Display the new DataFrame
# print(df_rules)

# 2nd Rule ----------------------------------------------------------------
asset_2times_liabilities = df['Current assets'] >= 2 * df['Current liabilities']
debt_lower_BFR = df['Financial debts'] <= df['Current assets'] - df['Current liabilities']

second = np.logical_and(asset_2times_liabilities, debt_lower_BFR)

# Display the result array
# print(asset_2times_liabilities, "\n", debt_lower_BFR, "\n", second)

df_rules['second_rule'] = second
# print(df_rules)

# 3rd Rule ----------------------------------------------------------------
net_income_all_positive = df.filter(like='Net income').gt(0).all(axis=1)
# print(net_income_all_positive)

df_rules['third_rule'] = net_income_all_positive 
# print(df_rules)

# 4th Rule -----------------------------------------------------------------
dividends_not_interrupted = df.filter(like='Dividends').gt(0).all(axis=1)
# print(dividends_not_interrupted)

df_rules['fourth_rule'] = dividends_not_interrupted 
# print(df_rules)

# 5th Rule -----------------------------------------------------------------
first_3_years = df.filter(like='Net earnings per share').iloc[:, :3]
last_3_years = df.filter(like='Net earnings per share').iloc[:, -3:]

# Calculate the mean for each row
mean_first_3_years = first_3_years.mean(axis=1)
mean_last_3_years = last_3_years.mean(axis=1)

_33_percent_growth = mean_first_3_years * 4/3 < mean_last_3_years 

# Display the results
df_rules['fifth_rule'] = _33_percent_growth 
# print(df_rules)

# 6th Rule -----------------------------------------------------------------
PER = share_actual_price / mean_last_3_years
print(PER)

condition = PER <= 15
df_rules['sixth_rule'] = condition 
# print(df_rules)

# 7th Rule -----------------------------------------------------------------
market_cap = df['Number of shares issued'] * share_actual_price 
net_book_value = df['Shareholders\' equity'] - df['Intangible assets']
PBR = market_cap / net_book_value
print(PBR)

condition = PBR < 1.5
df_rules['seventh_rule'] = condition 
# print(df_rules)

# Bonus ---------------------------------------------------------------------
bonus = PER * PBR
print(bonus)

condition = bonus <= 22.5
df_rules['bonus'] = condition 
print(df_rules)