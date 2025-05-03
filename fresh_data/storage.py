# -*- coding: utf-8 -*- #
"""
Module containing the storage class for companies.
"""

from __future__ import annotations

import csv
import codecs
import pickle
import sqlite3
import logging
from pathlib import Path
from typing import Iterator

from fresh_data.company import Company
from rules.rules import Rules

# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# ===========================================================================
# Company Class
# ===========================================================================

class CompanyStorage:
    """Class to store and retrieve companies info from a sqlite database."""

    def __init__(self, source: str | Path) -> None:
        self.conn = sqlite3.connect(source)
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

class RulesStorage:
    """Class to store and retrieve rules info from a sqlite database."""

    def __init__(self, source: str | Path) -> None:
        self.conn = sqlite3.connect(source)
        self.cursor = self.conn.cursor()

        self.__initialize_db()
    # End def __init__

    # ---------------------------------------------------------------------------------------------
    # Magic Methods 
    # ---------------------------------------------------------------------------------------------
    
    def __len__(self) -> int:
        self.cursor.execute("SELECT COUNT(*) FROM rules")
        return self.cursor.fetchone()[0]
    # End def __len__

    # ---------------------------------------------------------------------------------------------
    # Accessors 
    # ---------------------------------------------------------------------------------------------
    
    def add_company(self, cursor: sqlite3.Cursor, rule: Rules) -> None:
        
        name          = rule.name
        share_p       = rule.actual_share_price
        sales         = rule.sales
        nb_shares     = rule.nb_shares_issued
        curr_assets   = rule.current_assets
        curr_liab     = rule.current_liabilities
        l_term_debts  = rule.financial_debts
        equity        = rule.equity
        intang_assets = rule.intangible_assets
        net_income    = rule.net_income
        dividends     = rule.dividends
        nt_ernng_shr  = rule.net_earning_per_share

        cursor.execute(f"""
            INSERT INTO companies (
            name,
            actual_share_price,
            sales,
            nb_shares_issued,
            current_assets,
            current_liabilities,
            financial_debts,
            equity,
            intangible_assets,  
            net_income,
            dividends,  
            net_earning_per_share)
            VALUES(
            '{name}',
            '{share_p}',
            '{sales}',
            '{nb_shares}',
            '{curr_assets}',
            '{curr_liab}',
            '{l_term_debts}',
            '{equity}',
            '{intang_assets}',
            '{codecs.encode(pickle.dumps(net_income), "base64").decode()}',
            '{codecs.encode(pickle.dumps(dividends), "base64").decode()}',
            '{codecs.encode(pickle.dumps(nt_ernng_shr), "base64").decode()}')                    
        """)
    # End def add_company

    def update_company(self, cursor: sqlite3.Cursor, company: Company) -> None:
        name          = company.name
        share_p       = company.actual_share_price
        sales         = company.sales
        nb_shares     = company.nb_shares_issued
        curr_assets   = company.current_assets
        curr_liab     = company.current_liabilities
        l_term_debts  = company.financial_debts
        equity        = company.equity
        intang_assets = company.intangible_assets
        net_income    = company.net_income
        dividends     = company.dividends
        nt_ernng_shr  = company.net_earning_per_share

        cursor.execute(f"""
            UPDATE companies
            SET 
                actual_share_price = ?,
                sales = ?,
                nb_shares_issued = ?,
                current_assets = ?,
                current_liabilities = ?,
                financial_debts = ?,
                equity = ?,
                intangible_assets = ?,
                net_income = ?,
                dividends = ?,
                net_earning_per_share = ?
            WHERE name = ?
            """, (
                share_p, 
                sales, 
                nb_shares, 
                curr_assets, 
                curr_liab, 
                l_term_debts, 
                equity, 
                intang_assets, 
                codecs.encode(pickle.dumps(net_income), "base64").decode(),
                codecs.encode(pickle.dumps(dividends), "base64").decode(),
                codecs.encode(pickle.dumps(nt_ernng_shr), "base64").decode(),
                name  # The company you want to update
        ))
    # End def update_company

    def is_rule(self, cursor: sqlite3.Cursor, rule: Rules) -> bool:
        cursor.execute("SELECT COUNT(*) FROM companies WHERE name = ?", (rule.name,))
        return cursor.fetchone()[0]
    # End def is_company

    def get_companies(self) -> Iterator[Rules]:
        for c in self.cursor.execute("SELECT * FROM rules").fetchall():
            try:
                rule = Rules(
                    name = c[1],
                    last_update = c[3],
                    actual_share_price = c[4],
                    sales = c[5],
                    nb_shares_issued = c[6],
                    current_assets = c[7],
                    current_liabilities = c[8],
                    financial_debts = c[9],
                    equity = c[10],
                    intangible_assets = c[11],
                    net_income = pickle.loads(codecs.decode(c[12].encode(), "base64")),
                    dividends = pickle.loads(codecs.decode(c[13].encode(), "base64")),
                    net_earning_per_share = pickle.loads(codecs.decode(c[14].encode(), "base64")),
                )
                yield rule
            except Exception as e:
                print(f"Error: {e}")
        # End for c
    # End def get_companies

    # ---------------------------------------------------------------------------------------------
    # Public Methods 
    # ---------------------------------------------------------------------------------------------

    def clear(self, rules: bool = True) -> None:
        if rules is True:
            self.cursor.execute("DELETE FROM rules")
        self.conn.commit()
    # End def clear

    # ---------------------------------------------------------------------------------------------
    # Private Methods 
    # ---------------------------------------------------------------------------------------------
    
    def __initialize_db(self) -> None:
        # Create if not exists the companies table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                created DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_update DATETIME DEFAULT CURRENT_TIMESTAMP,
                actual_share_price DOUBLE(10,4),
                sales DOUBLE(20,2),
                nb_shares_issued INT(255),
                current_assets DOUBLE(20,2),
                current_liabilities DOUBLE(20,2),
                financial_debts DOUBLE(20,2),
                equity DOUBLE(20,2),
                intangible_assets DOUBLE(20,2),  
                net_income TEXT,
                dividends TEXT,  
                net_earning_per_share TEXT
            )
        """)

        self.cursor.execute(f"""
            CREATE TRIGGER IF NOT EXISTS update_last_update
            AFTER UPDATE ON rules
            FOR EACH ROW
            BEGIN
                UPDATE rules
                SET last_update = CURRENT_TIMESTAMP
                WHERE name = OLD.name;
            END;
        """)

        self.conn.commit()
    # End def __initialize_db
# End class RulesStorage


if __name__ == '__main__':
    s = CompanyStorage(source="./test.db")
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