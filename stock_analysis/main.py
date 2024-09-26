# -*- coding: utf-8 -*- #
"""
Main file calling classes 
"""
import sys
import logging 
import numpy as np
import pandas as pd

from rules.rules import Rules
from fresh_data.importer import StockDataImporter
from extraction.extraction import Extraction

def chrono(message: str = "") -> None:
    from datetime import datetime
    now = datetime.now()
    # now_str = now.strftime("%d-%m-%Y %H:%M:%s")
    print(f"{now} - {message}\n")
    
def main():
    db_path=r'C:\diskD\6 - CODE\stock_analysis\stock_analysis\company.db'
    tickers_path=r'C:\diskD\6 - CODE\stock_analysis\stock_analysis\yh_tickers.json' 
    # logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    
    data = StockDataImporter(db_path)
    chrono("Config")

    # Retrieve tickers from json file --------------------------
    data.retrieve_tickers(tickers_path, dev=True)
    chrono("Tickers retrieved !")

    # Retrieve data with yfinance ------------------------------
    data.parallel_retrieve_data()
    chrono("Data retrieved !")
    
    # Save all balance sheets to a database --------------------
    data.parallel_to_database(db_path, max_workers=0)    
    chrono("Data stored !")
    
    # Dataframe of all companies from the database
    df = data.as_rule_dataframe()
    chrono("Data transformed in dataframe !")

    # Connect to Rules module ----------------------------------
    Rule = Rules()
    Rule.determine_rules(df)
    chrono("Rules determined !")
    print(Rule)

if __name__ == "__main__":
    main()