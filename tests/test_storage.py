import unittest
from financial_pipeline.storage.company_storage import CompanyStorage

class TestCompanyStorage(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite DB to isolate tests
        self.storage = CompanyStorage(":memory:")

    def tearDown(self):
        self.storage.close()

    def test_add_and_get_company(self):
        self.storage.add_company("AlphaCorp", "Finance", "USA")
        company = self.storage.get_company("AlphaCorp")
        self.assertIsNotNone(company)
        self.assertEqual(company[1], "AlphaCorp")
        self.assertEqual(company[2], "Finance")
        self.assertEqual(company[3], "USA")

    def test_add_duplicate_company(self):
        self.storage.add_company("BetaCorp")
        self.storage.add_company("BetaCorp")  # Should not raise error
        companies = self.storage.list_companies()
        self.assertEqual(len(companies), 1)

    def test_update_and_get_financials(self):
        self.storage.add_company("GammaCorp")
        self.storage.update_financials("GammaCorp", 2022, sales=1000.0, eps=2.5)
        financials = self.storage.get_financials("GammaCorp", 2022)
        self.assertEqual(len(financials), 1)
        self.assertEqual(financials[0][5], 1000.0)  # sales
        self.assertEqual(financials[0][-1], 2.5)    # eps

    def test_update_existing_financials(self):
        self.storage.add_company("DeltaCorp")
        self.storage.update_financials("DeltaCorp", 2022, sales=500.0)
        self.storage.update_financials("DeltaCorp", 2022, sales=1500.0, eps=1.0)
        updated = self.storage.get_financials("DeltaCorp", 2022)[0]
        self.assertEqual(updated[5], 1500.0)
        self.assertEqual(updated[-1], 1.0)

    def test_list_companies(self):
        self.storage.add_company("EpsilonCorp", "Energy", "UK")
        self.storage.add_company("ZetaCorp", "Retail", "DE")
        companies = self.storage.list_companies()
        names = [c[1] for c in companies]
        self.assertIn("EpsilonCorp", names)
        self.assertIn("ZetaCorp", names)

    def test_delete_company(self):
        self.storage.add_company("OmegaCorp")
        self.storage.update_financials("OmegaCorp", 2020, sales=2000)
        self.storage.delete_company("OmegaCorp")

        self.assertIsNone(self.storage.get_company("OmegaCorp"))
        self.assertEqual(self.storage.get_financials("OmegaCorp"), None)

if __name__ == '__main__':
    unittest.main()
