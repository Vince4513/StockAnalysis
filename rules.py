import os as os
import numpy as np
import pandas as pd


class Rules:
    def __init__(self, share_actual_price) -> None:
        self.share_price = share_actual_price
        self.df_rules = None
        self.PER = None
        self.PBR = None
        self.bonus = None
        self.sales_greater_100M = None
        self.asset_2times_liabilities = None
        self.debt_lower_BFR = None
        self.net_income_all_positive = None
        self.dividends_not_interrupted = None


    def determine_measures(self, df: pd.DataFrame):
        # Check if Sales (CA) > 1000 for each company
        self.sales_greater_100M = df['Sales'] > 1000000
        self.asset_2times_liabilities = df['Current assets'] >= 2 * df['Current liabilities']
        self.debt_lower_BFR = df['Financial debts'] <= df['Current assets'] - df['Current liabilities']
        self.net_income_all_positive = df.filter(like='Net income').gt(0).all(axis=1)
        self.dividends_not_interrupted = df.filter(like='Dividends').gt(0).all(axis=1)
        
        first_3_years = df.filter(like='Net earnings per share').iloc[:, :3]
        last_3_years = df.filter(like='Net earnings per share').iloc[:, -3:]
        mean_first_3_years = first_3_years.mean(axis=1)
        mean_last_3_years = last_3_years.mean(axis=1)

        self._33_percent_growth = mean_first_3_years * 4/3 < mean_last_3_years 
        self.PER = self.share_price / mean_last_3_years

        market_cap = df['Number of shares issued'] * self.share_price 
        net_book_value = df['Shareholders\' equity'] - df['Intangible assets']
        self.PBR = market_cap / net_book_value

    def determine_rules(self, df: pd.DataFrame):
        # Display the DataFrame
        print(df.shape, df.info(verbose=False, memory_usage=True))

        # 1st Rule ---------------------------------------------------------------
        # Create a new DataFrame with True/False values based on the condition
        self.df_rules = pd.DataFrame({
            'Company': df['Company'],
            'first_rule': self.sales_greater_100M
        })

        # 2nd Rule ----------------------------------------------------------------
        second = np.logical_and(self.asset_2times_liabilities, self.debt_lower_BFR)
        self.df_rules['second_rule'] = second

        # 3rd Rule ----------------------------------------------------------------
        self.df_rules['third_rule'] = self.net_income_all_positive 
        
        # 4th Rule -----------------------------------------------------------------
        self.df_rules['fourth_rule'] = self.dividends_not_interrupted 

        # 5th Rule -----------------------------------------------------------------
        self.df_rules['fifth_rule'] = self._33_percent_growth 

        # 6th Rule -----------------------------------------------------------------
        condition = self.PER <= 15
        self.df_rules['sixth_rule'] = condition 
    
        # 7th Rule -----------------------------------------------------------------
        condition = self.PBR < 1.5
        self.df_rules['seventh_rule'] = condition 
        
        # Bonus ---------------------------------------------------------------------
        self.bonus = self.PER * self.PBR
        condition = self.bonus <= 22.5
        self.df_rules['bonus'] = condition 
        self.df_rules.columns = ['company', 'rule_1', 'rule_2', 'rule_3', 'rule_4', 'rule_5', 'rule_6', 'rule_7', 'bonus']

    def show_rules(self) -> None:
        print(self.df_rules)
        print(self.PBR,"\n", self.PER)

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
    Rule = Rules(share_actual_price)
    Rule.determine_measures(df)
    Rule.determine_rules(df)
    Rule.show_rules()

if __name__ == "__main__":
    main()