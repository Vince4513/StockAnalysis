# -*- coding: utf-8 -*- #
"""
Cleaning of raw data
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Any


# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ===========================================================================
# FinancialDataCleaner Class
# ===========================================================================


class FinancialDataCleaner:
    """
    Cleans raw Yahoo Finance JSON data into structured format
    suitable for inserting into the database.
    """

    # ===========================================================================
    # Magic Methods
    # ===========================================================================

    def __str__(self):
        return f"Extraction({datetime.now()})"
    # End def __str__

    # ===========================================================================
    # Public Methods
    # ===========================================================================

    def extract_all(self, raw_data: Dict[str, Any], company_name: str) -> List[Dict[str, Any]]:
        """
        Convert raw Yahoo data to structured financial rows.
        Each row is a dictionary keyed by your database columns.
        """
        financials = []

        # Handle time-series: use income stmt, balance sheet, and dividend dates
        income = raw_data.get("incomestmt", {})
        balance = raw_data.get("balancesheet", {})
        dividends = raw_data.get("dividends", {})

        # Assume all dicts have the same years; use incomestmt keys as base
        fiscal_years = list(next(iter(income.values())).keys()) if income else []
        fiscal_years = [year.split("-")[0] for year in fiscal_years]

        for year in fiscal_years:
            row = {
                "name": company_name,
                "year": int(year),  # Use only the year part
                "share_price": raw_data.get("regularMarketPrice", None),
                "sales": self._get_nested(income, "Operating Revenue", year),
                "shares_issued": raw_data.get("sharesOutstanding", None),
                "current_assets": self._sum_nested(balance, ["Current Assets", "Other Current Assets"], year),
                "current_liabilities": self._sum_nested(balance, ["Current Liabilities", "Other Current Liabilities"], year),
                "financial_debts": self._sum_nested(balance, [
                    "Derivative Product Liabilities",
                    "Long Term Debt And Capital Lease Obligation"
                ], year),
                "equity": self._get_nested(balance, "Stockholders Equity", year),
                "intangible_assets": self._get_nested(balance, "Goodwill And Other Intangible Assets", year),
                "net_income": self._get_nested(income, "Net Income Continuous Operations", year),
                "dividends": self._sum_dividends(dividends, year),
                "eps": self._get_nested(income, "Basic EPS", year),
            }
            financials.append(row)

        return financials
    # End def extract_all

    # ===========================================================================
    # Private Methods
    # ===========================================================================

    def _get_nested(self, source: Dict, key: str, year: str) -> float:
        try:
            sub_dict = source.get(key, {})
            for date_str, value in sub_dict.items():
                if date_str.startswith(year):
                    return value
        except Exception as e:
            logger.warning(f"Missing key {key} for year {year}: {e}")
            return None
    # End def _get_nested

    def _sum_nested(self, source: Dict, keys: List[str], year: str) -> float:
        total = 0.0
        found = False
        for key in keys:
            sub_dict = source.get(key, {})
            for date_str, value in sub_dict.items():
                if date_str.startswith(year):
                    total += value
                    found = True
        return total if found else None
    # End def _sum_nested
    
    def _sum_dividends(self, dividends: Dict[str, float], year: str) -> float:
        year_total = sum(amount for date, amount in dividends.items() if date.startswith(year))
        return year_total if year_total > 0 else None
    # End def _sum_dividends
# End class FinancialDataCleaner

if __name__ == "__main__":
    raw_data = {
            "regularMarketPrice": 52.5,
            "sharesOutstanding": 1000000000,
            "incomestmt": {
                "Operating Revenue": {
                    "2023-12-31": 100000000.0
                },
                "Net Income Continuous Operations": {
                    "2023-12-31": 9000000.0
                },
                "Basic EPS": {
                    "2023-12-31": 1.2
                }
            },
            "balancesheet": {
                "Current Assets": {
                    "2023-12-31": 5000000.0
                },
                "Other Current Assets": {
                    "2023-12-31": 1000000.0
                },
                "Current Liabilities": {
                    "2023-12-31": 3000000.0
                },
                "Other Current Liabilities": {
                    "2023-12-31": 200000.0
                },
                "Stockholders Equity": {
                    "2023-12-31": 15000000.0
                },
                "Derivative Product Liabilities": {
                    "2023-12-31": 800000.0
                },
                "Long Term Debt And Capital Lease Obligation": {
                    "2023-12-31": 700000.0
                },
                "Goodwill And Other Intangible Assets": {
                    "2023-12-31": 250000.0
                }
            },
            "dividends": {
                "2023-01-10": 0.5,
                "2023-04-15": 0.6,
                "2022-11-10": 0.4
            }
        }
    cleaner = FinancialDataCleaner()

    rows = cleaner.extract_all(raw_data, "Deloitte")
    logger.info(rows)