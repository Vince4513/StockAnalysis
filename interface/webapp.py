# -*- coding: utf-8 -*- #
"""
Interface class
"""

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

from rules.rules import Rules
from fresh_data.importer import StockDataImporter

# ==================================================================================================================================================
# StockAnalysisApp Class
# ==================================================================================================================================================

class StockAnalysisApp:
    """Streamlit application to interact with the backend"""

    def __init__(self, 
                 db_path: str | Path, 
                 ticker_path: str | Path) -> None:
        
        st.set_page_config(
            page_title="Stock Analysis",
            page_icon=":bar_chart:",
            layout="wide"
        )
        
        # Store the paths (database & ticker json file)
        self.db_path : str | Path = db_path
        self.ticker_path : str | Path = ticker_path
        
        # Initialize the importer class
        self.imprt = StockDataImporter(self.db_path)
    # End def __init__

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ----------------------------------------------------------------------------------------------------------------------------------------------

    def run(self):
        self.show_tabs()
    # End def run

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ----------------------------------------------------------------------------------------------------------------------------------------------
    
    def show_tabs(self) -> None:
        """Display the tabs of the streamlit app"""

        st.title("Stock Analysis Dashboard")
        st.markdown("_Prototype v0.1.0_")

        raw_data_tab, plots, rules_tab = st.tabs(["Upload", "Plots", "7 Rules"])

        df = self.show_raw_data_tab(raw_data_tab)
        self.show_graphs(plots, df)
        #self.show_kpi_tab(kpi_tab)
        self.show_rules_tab(rules_tab, df)
    # End def show_tabs

    def load_data(self) -> None:
        st.sidebar.header("Load data")

        # Retrieve tickers from json file --------------------------
        self.imprt.retrieve_tickers(self.ticker_path, dev=True)
        chrono("Tickers retrieved !")  

        # Retrieve data with yfinance ------------------------------
        self.imprt.parallel_retrieve_data()
        chrono("Data retrieved !")

        # Save all balance sheets to a database --------------------
        self.imprt.parallel_to_database(self.db_path, max_workers=0)    
        chrono("Data stored !")        
    # End def load_data

    def show_raw_data_tab(self, tab) -> pd.DataFrame:
        with tab:
            st.header("Raw data")
            
            self.load_data()

            # Dataframe of all companies from the database
            df = self.imprt.as_rule_dataframe()
            chrono("Data transformed in dataframe !")
            
            # Plot the dataframe
            st.dataframe(df)
            
            return df
    # End def show_kpi_tab

    def show_graphs(self, tab, df: pd.DataFrame) -> None:
        with tab:
            st.header("Graphs")
            
            # Plot dataframe informations of all companies from the database
            st.sidebar.header("Plot Options")
            x_axis = st.sidebar.selectbox("Select X-axis", df.columns)
            y_axis = st.sidebar.selectbox("Select Y-axis", df.columns)
            hue = st.sidebar.selectbox("Select Hue", [None] + list(df.columns))

            # Create the Seaborn plot
            fig, ax = plt.subplots()
            sns.scatterplot(data=df, x=x_axis, y=y_axis, hue=hue, ax=ax)

            # Display the plot in Streamlit
            st.pyplot(fig)
            # Plot the dataframe
            st.dataframe(df)
            
    # End def show_graphs

    def show_rules_tab(self, tab, df: pd.DataFrame) -> None:
        with tab:
            st.header("7 Rules")
            
            try:
                # Connect to Rules module ----------------------------------
                Rule = Rules()
                Rule.determine_rules(df)
                chrono("Rules determined !")

                st.dataframe(Rule.df_rules)
                st.write(Rule.PER, Rule.PBR)
                
            except Exception as e:
                st.write(f"Error: {e}")
    # End def show_rules_tab
# End class StockAnalysisApp

def chrono(message: str = "") -> None:
    now = datetime.now()
    # now_str = now.strftime("%d-%m-%Y %H:%M:%s")
    st.write(f"{now} - {message}\n")
# End def chrono