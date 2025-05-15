import unittest
from unittest.mock import MagicMock
import pandas as pd

from financial_pipeline.ml.financial_clusterer import FinancialClusterer


class TestFinancialClusterer(unittest.TestCase):
    def setUp(self):
        self.clusterer = FinancialClusterer()
        self.mock_df = self._get_mock_data()

        # Mock database access
        self.clusterer.db.list_companies = MagicMock(return_value=[("1", "A"), ("2", "B"), ("3", "C")])
        self.clusterer.db.get_financials = MagicMock(side_effect=self._mock_get_financials)
    # End def setUp

    def _get_mock_data(self):
        return pd.DataFrame({
            "name": ["A", "B", "C"],
            "share_price": [10, 15, 14],
            "sales": [100, 150, 140],
            "shares_issued": [1e6, 1.2e6, 1.1e6],
            "current_assets": [30, 35, 32],
            "current_liabilities": [10, 12, 11],
            "financial_debts": [5, 6, 5.5],
            "equity": [50, 60, 55],
            "intangible_assets": [10, 15, 12],
            "net_income": [5, 6, 5.5],
            "dividends": [1, 1.2, 1.1],
            "eps": [2, 2.2, 2.1],
        })
    # End def _get_mock_data

    def _mock_get_financials(self, name):
        row = self.mock_df[self.mock_df["name"] == name].iloc[0]
        return [(None, None, None, 2023) + tuple(row[col] for col in self.mock_df.columns if col != "name")]
    # End def _mock_get_financials

    def test_load_financial_data(self):
        df = self.clusterer.load_financial_data()
        self.assertEqual(df.shape[0], 3)
        self.assertIn("eps", df.columns)
    # End def test_load_financial_data

    def test_find_optimal_k(self):
        df = self.mock_df.copy()
        best_k = self.clusterer.find_optimal_k(df, k_min=2, k_max=3)
        self.assertTrue(2 <= best_k <= 3)
    # End def test_find_optimal_k

    def test_cluster_companies(self):
        df = self.mock_df.copy()
        df_clustered = self.clusterer.cluster_companies(df, k=2)
        self.assertIn("cluster", df_clustered.columns)
        self.assertEqual(df_clustered["cluster"].nunique(), 2)
    # End def test_cluster_companies

    def test_summarize_clusters(self):
        df = self.mock_df.copy()
        df = self.clusterer.cluster_companies(df, k=2)
        summary = self.clusterer.summarize_clusters(df)
        self.assertEqual(len(summary), 2)
        self.assertIn("sales", summary.columns)
    # End def test_summarize_clusters

    def test_no_companies(self):
        self.clusterer.db.list_companies.return_value = []
        df = self.clusterer.load_financial_data()
        self.assertTrue(df.empty)
    # End def test_no_companies

    def test_company_with_no_financials(self):
        self.clusterer.db.list_companies.return_value = [("1", "EmptyCo")]
        self.clusterer.db.get_financials.return_value = []
        df = self.clusterer.load_financial_data()
        self.assertTrue(df.empty)
    # End def test_company_with_no_financials

    def test_only_one_company(self):
        self.clusterer.db.list_companies.return_value = [("1", "SoloCo")]
        self.clusterer.db.get_financials.return_value = self._mock_get_financials("A")
        df = self.clusterer.load_financial_data()

        # Should still work, but clustering won't be valid
        self.assertEqual(len(df), 1)
        with self.assertRaises(ValueError):
            self.clusterer.find_optimal_k(df)
    # End def test_only_one_company

    def test_all_nan_rows(self):
        df = self.mock_df.copy()
        df.loc[:, df.columns != "name"] = float("nan")
        df = df.dropna()
        self.assertTrue(df.empty)
    # End def test_all_nan_rows

    def test_more_clusters_than_companies(self):
        df = self.mock_df.copy().iloc[:3]
        clustered = self.clusterer.cluster_companies(df, k=5)
        self.assertEqual(len(clustered), 3)
        self.assertIn("cluster", clustered.columns)
    # End def test_more_clusters_than_companies
# End class TestFinancialClusterer

if __name__ == "__main__":
    unittest.main()
