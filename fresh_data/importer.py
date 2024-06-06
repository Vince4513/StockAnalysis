# -*- coding: utf-8 -*- #
"""
Importer of data
"""
import os
import json
import numpy
from polygon import RESTClient


class StockDataImporter:
    """Import the data from Internet"""

    def __init__(self) -> None:
        self.client = RESTClient()
    # End def __init__

    def retrieve_data(self):
        aggs = []
        for a in self.client.get_grouped_daily_aggs("2024-06-01"):
            print("Ticker:\n", a)
            aggs.append(a)   
        
        print("\nAggregation:\n", aggs)


        # self.client.get_snapshot_all(

        # )

        # self.client.get_snapshot_ticker(

        # )

        # self.client.list_tickers()

        # aggs = []
        # for a in self.client.list_aggs(
        #     "AAPL",
        #     1,
        #     "day",
        #     "2019-01-01",
        #     "2023-02-16",
        #     limit=50000,
        # ):
        #     aggs.append(a)

        # print(aggs)
    # End def retrieve_data

# End class StockDataImporter