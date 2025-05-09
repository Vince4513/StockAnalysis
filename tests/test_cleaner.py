import unittest

from financial_pipeline.cleaner.financial_data_cleaner import FinancialDataCleaner


class TestFinancialDataCleaner(unittest.TestCase):

    def setUp(self):
        self.cleaner = FinancialDataCleaner()

        # Simulate raw JSON data similar to what's returned by the importer
        self.raw_data = {
            "country": "France", 
            "phone": "33 7 85 44 11 22", 
            "website": ".com", 
            "industry": "Retail", 
            "sector": "Consulting", 
            "region": "US", 
            "fullExchangeName": "Paris",
            "exchangeTimezoneShortName": "CEST", 
            "isin": "-", 
            "fullTimeEmployees": "2990",
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
    # End def setUp

    def test_extract_all(self):
        rows = self.cleaner.extract_all(self.raw_data, "TestCorp")

        self.assertEqual(len(rows), 1)

        row = rows[0]
        self.assertEqual(row["name"], "TestCorp")
        self.assertEqual(row["year"], 2023)
        self.assertEqual(row["share_price"], 52.5)
        self.assertEqual(row["sales"], 100000000.0)
        self.assertEqual(row["shares_issued"], 1000000000)
        self.assertEqual(row["current_assets"], 6000000.0)  # 5M + 1M
        self.assertEqual(row["current_liabilities"], 3200000.0)  # 3M + 200k
        self.assertEqual(row["financial_debts"], 1500000.0)  # 800k + 700k
        self.assertEqual(row["equity"], 15000000.0)
        self.assertEqual(row["intangible_assets"], 250000.0)
        self.assertEqual(row["net_income"], 9000000.0)
        self.assertEqual(row["eps"], 1.2)
        self.assertAlmostEqual(row["dividends"], 1.1)  # 0.5 + 0.6 (2023 only)
    # End def test_extract_all

    def test_missing_data(self):
        # Test partial or missing fields
        minimal_data = {
            "regularMarketPrice": 40,
            "incomestmt": {
                "Operating Revenue": {"2023-12-31": 5000}
            },
            "balancesheet": {},
            "dividends": {}
        }
        rows = self.cleaner.extract_all(minimal_data, "MiniCorp")
        row = rows[0]
        self.assertEqual(row["share_price"], 40)
        self.assertEqual(row["sales"], 5000)
        self.assertIsNone(row["net_income"])
        self.assertIsNone(row["financial_debts"])
        self.assertIsNone(row["dividends"])
    # End def test_missing_data

    def test_nan_values(self):
        pass
    # End def test_nan_values
# End class TestFinancialDataCleaner

if __name__ == '__main__':
    unittest.main()