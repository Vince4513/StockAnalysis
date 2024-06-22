# -*- coding: utf-8 -*- #
"""
Module containing the storage class for companies.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Iterator

from fresh_data.company import Company

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
    
    def add_company(self, company: Company) -> None:
        
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

        self.cursor.execute(f"""
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
            '{net_income}',
            '{dividends}',
            '{nt_ernng_shr}')                    
        """)
        self.conn.commit()
    # End def add_company

    def get_companies(self) -> Iterator[Company]:
        for c in self.cursor.execute("SELECT * FROM companies").fetchall():
            try:
                company = Company(
                    name = c[1],
                    last_update = datetime.isoformat(c[2]),
                    actual_share_price = c[3],
                    sales = c[4],
                    nb_shares_issued = c[5],
                    current_assets = c[6],
                    current_liabilities = c[7],
                    financial_debts = c[8],
                    equity = c[9],
                    intangible_assets = c[10],
                    net_income = c[11],
                    dividends = c[12],
                    net_earning_per_share = c[13],
                )
                yield company
            except Exception as e:
                print(f"Error: {e}")
        # End for c
    # End def get_companies

    # ---------------------------------------------------------------------------------------------
    # Public Methods 
    # ---------------------------------------------------------------------------------------------
    
    def clear(self, companies: bool = True) -> None:
        if companies is True:
            self.cursor.execute("DELETE FROM companies")
        self.conn.commit()
    # End def clear

    # ---------------------------------------------------------------------------------------------
    # Private Methods 
    # ---------------------------------------------------------------------------------------------
    
    def __initialize_db(self) -> None:
        # Create if not exists the companies table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
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

        self.conn.commit()
    # End def __initialize_db