# -*- coding: utf-8 -*- #
"""
Module containing the rules 
"""

import os as os
import numpy as np
import pandas as pd

# ==================================================================================================================================================
# Rules Class
# ==================================================================================================================================================

class Rules:
    """Determine the results of each company following the rules of fondamental analysis"""

    def __init__(self, share_actual_price: list[float] | None) -> None:
        """Initialize the class

        Args:
            share_actual_price (list[float] | None): Actual price of the shares.
        """
        self.share_price = share_actual_price
        self.df_rules = None
        
        # Measures 
        self.bonus = None
        self.sales_greater_100M = None
        self.asset_2times_liabilities = None
        self.debt_lower_BFR = None
        self.net_income_all_positive = None
        self.dividends_not_interrupted = None

        # Internal members
        self.__PER = None
        self.__PBR = None

    # End def __init__

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Properties
    # ----------------------------------------------------------------------------------------------------------------------------------------------
    
    @property
    def PER(self) -> np.ndarray:
        return self.__PER
    # End def PER
    
    @property
    def PBR(self) -> np.ndarray:
        return self.__PBR
    # End def PBR

    # @PER.setter
    # def PER(self, PER: np.ndarray) -> None:
    #     self.__PER = PER
    # # End def PER

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Magic Methods
    # ----------------------------------------------------------------------------------------------------------------------------------------------
    
    def __str__(self) -> str:
        return f"Rules:\n{self.df_rules}"

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ----------------------------------------------------------------------------------------------------------------------------------------------

    def determine_rules(self, df: pd.DataFrame):
        """Determine the results of each rule based on measures.

        Args:
            df (pd.DataFrame): Balance sheet of the company in a dataframe format.
        """
        # Calculus of measures
        self.__determine_measures(df)

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
        condition = self.__PER <= 15
        self.df_rules['sixth_rule'] = condition 
    
        # 7th Rule -----------------------------------------------------------------
        condition = self.__PBR < 1.5
        self.df_rules['seventh_rule'] = condition 
        
        # Bonus ---------------------------------------------------------------------
        self.bonus = self.__PER * self.__PBR
        condition = self.bonus <= 22.5
        self.df_rules['bonus'] = condition 
        self.df_rules.columns = ['company', 'rule_1', 'rule_2', 'rule_3', 'rule_4', 'rule_5', 'rule_6', 'rule_7', 'bonus']
    # End def determine_rules

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ----------------------------------------------------------------------------------------------------------------------------------------------
    
    def __determine_measures(self, df: pd.DataFrame):
        """Calculate the measures of fondamental analysis based on the data in df.

        Args:
            df (pd.DataFrame): Balance sheet of the company in a dataframe format.
        """
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
        self.__PER = self.share_price / mean_last_3_years

        market_cap = df['Number of shares issued'] * self.share_price 
        net_book_value = df['Shareholders\' equity'] - df['Intangible assets']
        self.__PBR = market_cap / net_book_value
    # End def __determine_measures

# End class Rules
