# -*- coding: utf-8 -*- #
"""
Main file calling classes 
"""
import numpy as np
import pandas as pd

from rules.rules import Rules

def main():
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
    # print(df.shape, df.info(verbose=False, memory_usage=True))

    Rule = Rules(share_actual_price)
    Rule.determine_rules(df)
    print(Rule)

if __name__ == "__main__":
    main()