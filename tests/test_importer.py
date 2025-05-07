import os
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from financial_pipeline.importer.financial_data_importer import FinancialDataImporter


class TestFinancialDataImporter(unittest.TestCase):
    
    def setUp(self):
        self.importer = FinancialDataImporter(ticker_source="mock_tickers.json", data_path="test_data/")
    # End def setUp

    @patch("os.path.exists", return_value=False)
    def test_retrieve_tickers_returns_default_if_file_missing(self, mock_exists):
        tickers = self.importer.retrieve_tickers()
        self.assertIn("TTE.PA", tickers)
        self.assertGreater(len(tickers), 0)
    # End def test_retrieve_tickers_returns_default_if_file_missing

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=mock_open, read_data='{"TTE.PA": "TotalEnergies"}')
    @patch("chardet.detect", return_value={"encoding": "utf-8"})
    def test_retrieve_tickers_from_file(self, mock_chardet, mock_open_func, mock_exists):
        tickers = self.importer.retrieve_tickers()
        self.assertEqual(tickers, ["TTE.PA"])
    # End def test_retrieve_tickers_from_file

    @patch("financial_pipeline.importer.financial_data_importer.yf.Ticker")
    @patch("builtins.open", new_callable=mock_open)
    def test_fetch_ticker_data_success(self, mock_file, mock_yf):
        mock_ticker = MagicMock()
        mock_ticker.info = {"some": "data"}
        mock_ticker.isin = "ISIN123"
        mock_ticker.incomestmt.to_dict.return_value = {}
        mock_ticker.balancesheet.to_dict.return_value = {}
        mock_ticker.dividends.items.return_value = []

        mock_yf.return_value = mock_ticker

        self.importer._fetch_ticker_data("TTE.PA")
        mock_file.assert_called_with(os.path.join("test_data/", "TTE.PA.json"), "w", encoding="utf-8")
        mock_file().write.assert_called()
    # End def test_fetch_ticker_data_success

    @patch("financial_pipeline.importer.financial_data_importer.yf.Ticker", side_effect=Exception("fetch error"))
    @patch("builtins.open", new_callable=mock_open)
    @patch("financial_pipeline.importer.financial_data_importer.logger")
    def test_fetch_ticker_data_handles_error(self, mock_logger, mock_file, mock_yf):
        self.importer._fetch_ticker_data("INVALID")
        mock_logger.error.assert_called()
    # End def test_fetch_ticker_data_handles_error

    def test_convert_timestamp(self):
        input_data = {
            "2020": {
                Path("2020-01-01"): 100,
                Path("2021-01-01"): 150,
            }
        }
        # Simulate datetime keys
        from datetime import datetime
        input_data = {
            "A": {
                datetime(2020, 1, 1): 100,
                datetime(2021, 1, 1): 200,
            }
        }
        result = self.importer._convert_timestamp(input_data)
        self.assertEqual(list(result["A"].keys()), ["2020-01-01", "2021-01-01"])
    # End def test_convert_timestamp
# End class TestFinancialDataImporter

if __name__ == "__main__":
    unittest.main()
