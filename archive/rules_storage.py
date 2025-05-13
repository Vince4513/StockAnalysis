# -*- coding: utf-8 -*- #
"""
Module containing the storage class for companies.
"""

from __future__ import annotations

import codecs
import pickle
import sqlite3
import logging
from pathlib import Path
from typing import Iterator

from archive.company import Company
from financial_pipeline.evaluator.graham_evaluator import GrahamEvaluator

# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# ===========================================================================
# RulesStorage Class
# ===========================================================================

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
    
    def add_company(self, cursor: sqlite3.Cursor, rule: GrahamEvaluator) -> None:
        
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

    def is_rule(self, cursor: sqlite3.Cursor, rule: GrahamEvaluator) -> bool:
        cursor.execute("SELECT COUNT(*) FROM companies WHERE name = ?", (rule.name,))
        return cursor.fetchone()[0]
    # End def is_company

    def get_companies(self) -> Iterator[GrahamEvaluator]:
        for c in self.cursor.execute("SELECT * FROM rules").fetchall():
            try:
                rule = GrahamEvaluator(
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