import pandas as pd
import unittest
from unittest.mock import MagicMock

from financial_pipeline.evaluator.graham_evaluator import GrahamEvaluator


class TestGrahamEvaluator(unittest.TestCase):
    def setUp(self):
        self.company_name = "TestCorp" # <-- Need the name to be in database and pass all rules
        self.evaluator = GrahamEvaluator()
        self.df = self._get_base_dataframe()
    # End def setUp

    def _get_base_dataframe(self):
        # Builds a 20-year valid dataset with increasing EPS and stable data
        data = {
            "year": list(range(2004, 2024)),
            "share_price": [100.0] * 20,
            "sales": [200_000_000] * 20,
            "shares_issued": [10_000_000] * 20,
            "current_assets": [80_000_000] * 20,
            "current_liabilities": [30_000_000] * 20,
            "financial_debts": [20_000_000] * 20,
            "equity": [150_000_000] * 20,
            "intangible_assets": [10_000_000] * 20,
            "net_income": [10_000_000] * 20,
            "dividends": [1.0] * 20,
            "eps": [5 + 0.5 * i for i in range(20)],  # EPS growing
        }
        return pd.DataFrame(data)
    # End def _get_base_dataframe

    def test_evaluate_rules(self):
        results = self.evaluator.evaluate(self.company_name)

        # All rules should pass with the mock data
        for rule, result in results.items():
            with self.subTest(rule=rule):
                self.assertTrue(result.get("passed"), f"{rule} should pass but failed.")
    # End def test_evaluate_rules

    def test_rule_1_sales_over_100m(self):
        result = self.evaluator._check_sales(self.df)
        self.assertTrue(result["passed"])
        self.assertIn("Average sales", result["description"])

        # Force fail
        self.df["sales"] = [50_000_000] * 20
        result = self.evaluator._check_sales(self.df)
        self.assertFalse(result["passed"])
    # End def test_rule_1_sales_over_100m

    def test_rule_2_current_ratio_and_debt(self):
        result = self.evaluator._check_current_ratio(self.df)
        self.assertTrue(result["passed"])

        # Fail CA < 2×CL
        self.df.at[19, "current_assets"] = 40_000_000
        result = self.evaluator._check_current_ratio(self.df)
        self.assertFalse(result["passed"])
    # End def test_rule_2_current_ratio_and_debt
    
    def test_rule_3_net_income_positive_10y(self):
        result = self.evaluator._check_positive_income(self.df)
        self.assertTrue(result["passed"])

        # Force a loss in one year
        self.df.at[15, "net_income"] = -1
        result = self.evaluator._check_positive_income(self.df)
        self.assertFalse(result["passed"])
    # End def test_rule_3_net_income_positive_10y
    
    def test_rule_4_dividends_20_years(self):
        result = self.evaluator._check_dividend_history(self.df)
        self.assertTrue(result["passed"])

        # Zero dividend in one year
        self.df.at[10, "dividends"] = 0.0
        result = self.evaluator._check_dividend_history(self.df)
        self.assertFalse(result["passed"])
    # End def test_rule_4_dividends_20_years
    
    def test_rule_5_eps_growth_over_10y(self):
        result = self.evaluator._check_eps_growth(self.df)
        self.assertTrue(result["passed"])

        # Flat EPS
        self.df["eps"] = [5.0] * 20
        result = self.evaluator._check_eps_growth(self.df)
        self.assertFalse(result["passed"])
    # End def test_rule_5_eps_growth_over_10y
    
    def test_rule_6_avg_eps_price_ratio(self):
        result = self.evaluator._check_eps_price_ratio(self.df)
        self.assertTrue(result["passed"])

        # EPS drops → ratio > 15
        self.df["eps"] = [1.0] * 20
        result = self.evaluator._check_eps_price_ratio(self.df)
        self.assertFalse(result["passed"])
    # End def test_rule_6_avg_eps_price_ratio
    
    def test_rule_7_valuation_ratio(self):
        result = self.evaluator._check_valuation_ratio(self.df)
        self.assertTrue(result["passed"])

        # Equity drops → ratio > 1.5
        self.df["equity"] = [20_000_000] * 20
        result = self.evaluator._check_valuation_ratio(self.df)
        self.assertFalse(result["passed"])
    # End def test_rule_7_valuation_ratio

    def test_bonus_rule_per_times_pbr(self):
        result = self.evaluator._check_bonus_rule(self.df)
        self.assertTrue(result["passed"])

        # Inflate price → high PER and PBR
        self.df["share_price"] = [1000.0] * 20
        result = self.evaluator._check_bonus_rule(self.df)
        self.assertFalse(result["passed"])
    # End def test_bonus_rule_per_times_pbr
# End class TestGrahamEvaluator

if __name__ == "__main__":
    unittest.main()
