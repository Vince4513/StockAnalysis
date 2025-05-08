# -*- coding: utf-8 -*- #
"""
Module containing the storage class for companies.
"""

from __future__ import annotations

import os
import csv
import sqlite3
import logging

# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# ===========================================================================
# CompanyStorage Class
# ===========================================================================

class CompanyStorage:
    """Class to store and retrieve companies info from a sqlite database."""

    def __init__(self, source=None) -> None:
        db_source = source or "data/processed/test.db"
        self.conn = sqlite3.connect(db_source)
        self.cursor = self.conn.cursor()

        self.__initialize_db()
    # End def __init__

    # ---------------------------------------------------------------------------------------------
    # Magic Methods 
    # ---------------------------------------------------------------------------------------------
    
    def __len__(self) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM companies")
        return self.cursor.fetchone()[0]
    # End def __len__

    # ---------------------------------------------------------------------------------------------
    # Accessors 
    # ---------------------------------------------------------------------------------------------

    def get_company_id(self, name):
        self.cursor.execute("SELECT id FROM companies WHERE name = ?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None
    # End def get_company_id

    def get_company(self, name):
        self.cursor.execute("SELECT * FROM companies WHERE name = ?", (name,))
        return self.cursor.fetchone()
    # End def get_company

    def get_financials(self, name, year=None):
        company_id = self.get_company_id(name)
        if not company_id:
            return None
        if year:
            self.cursor.execute("""
                SELECT * FROM financials
                WHERE company_id = ? AND year = ?
            """, (company_id, year))
        else:
            self.cursor.execute("""
                SELECT * FROM financials
                WHERE company_id = ?
                ORDER BY year
            """, (company_id,))
        return self.cursor.fetchall()
    # End def get_financials

    # ---------------------------------------------------------------------------------------------
    # Public Methods 
    # ---------------------------------------------------------------------------------------------

    def add_company(self, name, industry=None, country=None):
        try:
            # name     = company.name
            # industry = None
            # country  = None

            self.cursor.execute("""
                INSERT INTO companies (name, industry, country)
                VALUES (?, ?, ?)
            """, (name, industry, country))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"Company '{name}' already exists.")
    # End def add_company

    def update_financials(self, name, year, **kwargs):
        company_id = self.get_company_id(name)
        if not company_id:
            raise ValueError(f"Company '{name}' not found.")

        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?'] * len(kwargs))
        values = list(kwargs.values())

        # Try insert; if it fails, update
        try:
            self.cursor.execute(f"""
                INSERT INTO financials (company_id, year, {columns})
                VALUES (?, ?, {placeholders})
            """, [company_id, year] + values)
        except sqlite3.IntegrityError:
            # Update existing
            update_stmt = ', '.join([f"{k} = ?" for k in kwargs.keys()])
            self.cursor.execute(f"""
                UPDATE financials
                SET {update_stmt}
                WHERE company_id = ? AND year = ?
            """, values + [company_id, year])
        except sqlite3.OperationalError:
            raise ValueError(f"At least one parameter is mispelled.")
        self.conn.commit()
    # End def update_financials
    
    def list_companies(self):
        self.cursor.execute("SELECT id, name, industry, country FROM companies ORDER BY name;")
        return self.cursor.fetchall()
    # End def list_companies
    
    def delete_company(self, name):
        company_id = self.get_company_id(name)
        if not company_id:
            print(f"No such company: {name}")
            return
        self.cursor.execute("DELETE FROM financials WHERE company_id = ?", (company_id,))
        self.cursor.execute("DELETE FROM companies WHERE id = ?", (company_id,))
        self.conn.commit()
        print(f"Deleted company '{name}' and associated financials.")
    # End def delete_company

    def export_company_financials_to_csv(self, name, file_path):
        company_id = self.get_company_id(name)
        if not company_id:
            print(f"No such company: {name}")
            return

        self.cursor.execute("""
            SELECT year, share_price, sales, shares_issued, current_assets,
                   current_liabilities, financial_debts, equity, intangible_assets,
                   net_income, dividends, eps
            FROM financials
            WHERE company_id = ?
            ORDER BY year
        """, (company_id,))
        rows = self.cursor.fetchall()

        headers = [
            "year", "share_price", "sales", "shares_issued", "current_assets",
            "current_liabilities", "financial_debts", "equity", "intangible_assets",
            "net_income", "dividends", "eps"
        ]
        
        os.chdir("data/processed/")
        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"Exported financials for '{name}' to {file_path}")
    # End def export_company_financials_to_csv

    def close(self):
        self.conn.close()
    # End def close

    # ---------------------------------------------------------------------------------------------
    # Private Methods 
    # ---------------------------------------------------------------------------------------------
    
    def __initialize_db(self) -> None:
        # Create if not exists the static companies table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                industry TEXT,
                country TEXT
            );
        """)

        # Create if not exists the time-series financials table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS financials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
                year INTEGER NOT NULL,
                share_price REAL,
                sales REAL,
                shares_issued INTEGER,
                current_assets REAL,
                current_liabilities REAL,
                financial_debts REAL,
                equity REAL,
                intangible_assets REAL,
                net_income REAL,
                dividends REAL,
                eps REAL,
                FOREIGN KEY (company_id) REFERENCES companies(id),
                UNIQUE(company_id, year) -- Prevents duplicate yearly entries per company
            );
        """)

        self.cursor.execute(f"""
            CREATE TRIGGER IF NOT EXISTS update_last_update
            AFTER UPDATE ON financials
            FOR EACH ROW
            BEGIN
                UPDATE financials
                SET last_update = CURRENT_TIMESTAMP
                WHERE company_id = OLD.company_id;
            END;
        """)

        self.conn.commit()
    # End def __initialize_db
# End class CompanyStorage


if __name__ == '__main__':
    s = CompanyStorage()
    s.add_company(name="BBC")
    logger.debug(s.get_company_id(name="BBA"))
    logger.debug(s.get_company_id(name="BBC"))
    
    # s.update_financials(
    #     name='BBC', 
    #     year=2023
    # )
    s.update_financials(
        name='BBC', 
        year=2021,
        share_price=10.9,
        sales=200000,
        dividends=2.3
    )

    logger.debug(s.get_company(name="B"))
    logger.debug(s.get_company(name="BBC"))
    
    logger.debug(s.get_financials(name="B"))
    logger.debug(s.get_financials(name="BBC"))
    logger.debug(s.get_financials(name="BBC", year=2021))

    s.export_company_financials_to_csv("BBC", "BBC_export.csv")

    # s.delete_company("B")
    # s.delete_company("BBC")

    s.close()