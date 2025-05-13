# -*- coding: utf-8 -*- #
"""
Module containing the rules 
"""

import logging
import pandas as pd
from typing import Dict, Any

from financial_pipeline.utils.helpers import get_safe_values
from financial_pipeline.storage.company_storage import CompanyStorage

# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)

# ==================================================================================================================================================
# GrahamEvaluator Class
# ==================================================================================================================================================

class GrahamEvaluator:
    """Determine the results of each company following the rules of fondamental analysis"""

    def __init__(self, db_path=None):
        self.db_path = db_path or "data/processed/test.db"
        self.db = CompanyStorage(db_path)
    # End def __init__

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Properties
    # ----------------------------------------------------------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Magic Methods
    # ----------------------------------------------------------------------------------------------------------------------------------------------
    
    def __repr__(self) -> str:
        return f"<GrahamEvaluator>"
    # End def __repr__

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ----------------------------------------------------------------------------------------------------------------------------------------------
    
    def evaluate(self, company_name: str) -> Dict[str, Dict[str, Any]]:
        """Evaluate a company against Graham’s rules."""
        rows = self.db.get_financials(company_name)
        if not rows:
            raise ValueError(f"No financials found for {company_name}")

        columns = [
            "id", "company_id", "last_update", "year", "share_price", "sales", "shares_issued", "current_assets",
            "current_liabilities", "financial_debts", "equity", "intangible_assets", "net_income",
            "dividends", "eps"
        ]
        df = pd.DataFrame(rows, columns=columns).sort_values("year")

        results = {}

        # Run each rule
        results["Rule 1"] = self._check_sales(df)
        results["Rule 2"] = self._check_current_ratio(df)
        results["Rule 3"] = self._check_positive_income(df)
        results["Rule 4"] = self._check_dividend_history(df)
        results["Rule 5"] = self._check_eps_growth(df)
        results["Rule 6"] = self._check_eps_price_ratio(df)
        results["Rule 7"] = self._check_valuation_ratio(df)
        results["Bonus Rule"] = self._check_bonus_rule(df)

        return results
    # End def evaluate

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ----------------------------------------------------------------------------------------------------------------------------------------------
    
    # Rule 1: Sales > 100M (50M for utilities — not handled yet)
    def _check_sales(self, df: pd.DataFrame) -> Dict:
        latest = df[df["year"] == df["year"].max()].iloc[0]
        passed = latest["sales"] >= 100_000_000
        return {
            "passed": passed,
            "description": "Sales in the most recent year > 100M",
            "value": round(latest["sales"], 2)
        }
    # End def _check_sales

    # Rule 2: Current Ratio = 2x (current assets - financial debts) >= current liabilities
    def _check_current_ratio(self, df: pd.DataFrame) -> Dict:
        latest = df.iloc[-1]
        keys = ["current_assets", "current_liabilities", "financial_debts"]
        has_data, values = get_safe_values(latest, keys)

        if not has_data:
            return {
                "passed": False,
                "description": "Current assets ≥ 2 × current liabilities and financial debt ≤ (CA - CL)",
                "value": "Some data is missing (CA, CL, or FD is null)"
            }
        
        # Perform calculus
        ca = values["current_assets"]
        cl = values["current_liabilities"]
        fd = values["financial_debts"]

        wc = ca - cl
        passed = ca >= 2 * cl and fd <= wc
        return {
            "passed": passed,
            "description": "Current assets ≥ 2 × current liabilities and financial debt ≤ (CA - CL)",
            "value": f"CA={ca}, CL={cl}, FD={fd}"
        }
    # End def _check_current_ratio

    # Rule 3: Net income > 0 for 10 years
    def _check_positive_income(self, df: pd.DataFrame) -> Dict:
        recent = df[df["year"] >= df["year"].max() - 9]

        # Check we have 10 years of data
        if len(recent) < 10:
            return {
                "passed": False,
                "description": "Requires uninterrupted net_income for 10 years",
                "value": f"Only {len(recent)} years of data available"
            }
    
        passed = (recent["net_income"] > 0).all()
        return {
            "passed": passed,
            "description": "Positive net income for 10 consecutive years",
            "value": recent["net_income"].tolist()
        }
    # End def _check_positive_income

    # Rule 4: Dividends paid every year for 20 years
    def _check_dividend_history(self, df: pd.DataFrame) -> Dict:
        recent = df[df["year"] >= df["year"].max() - 19]

        # Check we have 20 years of data
        if len(recent) < 20:
            return {
                "passed": False,
                "description": "Requires uninterrupted dividends for 20 years",
                "value": f"Only {len(recent)} years of data available"
            }

        passed = (recent["dividends"] > 0).all()
        return {
            "passed": passed,
            "description": "Uninterrupted dividends for 20 years",
            "value": recent["dividends"].tolist()
        }
    # End def _check_dividend_history

    # Rule 5: EPS growth: Avg last 3 > Avg first 3 by +33%
    def _check_eps_growth(self, df: pd.DataFrame) -> Dict:
        if len(df) < 10:
            return {
                "passed": False, 
                "description": "Requires 10 years of eps data", 
                "value": f"Only {len(df)} years of data available"
            }

        # Select last 10 years
        recent = df.tail(10)

        eps_first_3 = recent.head(3)["eps"].mean()
        eps_last_3 = recent.tail(3)["eps"].mean()
        passed = eps_last_3 >= eps_first_3 * 1.33
        return {
            "passed": passed,
            "description": "EPS increased by at least 33% over 10 years",
            "value": f"{eps_first_3:.2f} → {eps_last_3:.2f}"
        }
    # End def _check_eps_growth

    # Rule 6: Current price / Avg EPS (last 3) ≤ 15
    def _check_eps_price_ratio(self, df: pd.DataFrame) -> Dict:
        eps = df.tail(3)["eps"].mean()
        latest = df.iloc[-1]
        keys = ["share_price"]
        has_data, values = get_safe_values(latest, keys)

        if not has_data:
            return {
                "passed": False,
                "description": "P/E ratio (3-year avg) ≤ 15",
                "value": "Some required financial data is missing."
            }
        price = values["share_price"]
        ratio = price / eps if eps and eps > 0 else float("inf")
        passed = ratio <= 15
        return {
            "passed": passed,
            "description": "P/E ratio (3-year avg) ≤ 15",
            "value": f"{price:.2f} / {eps:.2f} = {ratio:.2f}"
        }
    # End def _check_eps_price_ratio

    # Rule 7: Market Cap / Net Book Value (less intangibles) < 1.5
    def _check_valuation_ratio(self, df: pd.DataFrame) -> Dict:
        latest = df.iloc[-1]
        keys = ["shares_issued", "share_price", "equity", "intangible_assets"]
        has_data, values = get_safe_values(latest, keys)

        if not has_data:
            return {
                "passed": False,
                "description": "Market cap / tangible equity ≤ 1.5",
                "value": "Some required financial data is missing."
            }

        market_cap = values["shares_issued"] * values["share_price"]
        tangible_equity = values["equity"] - values["intangible_assets"]
        ratio = market_cap / tangible_equity if tangible_equity and tangible_equity > 0 else float("inf")
        passed = ratio <= 1.5

        return {
            "passed": passed,
            "description": "Market cap / tangible equity ≤ 1.5",
            "value": f"{market_cap:.2f} / {tangible_equity:.2f} = {ratio:.2f}"
        }
    # End def _check_valuation_ratio

    # Bonus Rule: PER × PBR ≤ 22.5
    def _check_bonus_rule(self, df: pd.DataFrame) -> Dict:
        eps = df.tail(3)["eps"].mean()
        latest = df.iloc[-1]
        keys = ["share_price", "equity", "intangible_assets", "shares_issued"]
        has_data, values = get_safe_values(latest, keys)

        if not has_data:
            return {
                "passed": False,
                "description": "PER × PBR ≤ 22.5",
                "value": "Some required financial data is missing."
            }
        
        price = values["share_price"]
        equity = values["equity"]
        intangibles = values["intangible_assets"]
        shares = values["shares_issued"]
        tangible_equity = equity - intangibles

        per = price / eps if eps and eps > 0 else float("inf")
        pbr = (price * shares) / tangible_equity if tangible_equity and tangible_equity > 0 else float("inf")
        value = per * pbr
        passed = value <= 22.5
        return {
            "passed": passed,
            "description": "PER × PBR ≤ 22.5",
            "value": f"{per:.2f} × {pbr:.2f} = {value:.2f}"
        }
    # End def _check_bonus_rule
# End class GrahamEvaluator

if __name__ == '__main__':
    g = GrahamEvaluator()