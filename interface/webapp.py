# -*- coding: utf-8 -*- #
"""
Interface class
"""

import os
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
from ml.models import Models
from interface.reports import PDF

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

        raw_data_tab, plots, rules_tab, regression_tab, report_tab = st.tabs(
            ["Upload", "Plots", "7 Rules", "Regression", "Reports"])

        df = self.show_raw_data_tab(raw_data_tab)
        # self.show_graphs(plots, df)
        # self.show_kpi_tab(kpi_tab)
        # self.show_rules_tab(rules_tab, df)
        # self.show_regres_tab(regression_tab, df)
        # self.show_report_tab(report_tab, df)
    # End def show_tabs

    def load_data(self) -> None:

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
            
            # Step 1: Check structure
            st.header("Check structure")
            st.dataframe(df.head())
            st.write(f"Shape: {df.shape}")
            st.write(f"Info: {df.info()}")

            # Step 2: Statistical summary
            st.header("Statistical summary")
            st.write(df.describe())

            # Step 3: Missing values
            st.header("Missing values")
            st.dataframe(df.isnull().sum())

            # Step 4: Check duplicates
            st.header("Check duplicates")
            st.write("Number of duplicates:", df.duplicated().sum())

            return df
    # End def show_kpi_tab

    def show_graphs(self, tab, df: pd.DataFrame) -> None:
        with tab:
            st.header("Graphs")
            
            # Step 5: Visualizations
            fig, ax = plt.subplots()
            sns.histplot(df['sales'], bins=40, ax=ax)
            st.pyplot(fig)
            
            # fig, ax = plt.subplots()
            # sns.heatmap(df.corr(), annot=True, ax=ax)
            # st.pyplot(fig)
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

    def show_regres_tab(self, tab, df: pd.DataFrame) -> None:
        with tab:
            st.header("Regression")
            ml = Models(df, 'sales')
            ml.get_score(estimators = 100)
            ml.plot_errors()     
    # End def show_regres_tab

    def show_report_tab(self, tab, df: pd.DataFrame) -> None:
        with tab:
            st.header("Report")

            @st.cache_data
            def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv().encode("utf-8")

            csv = convert_df(df)

            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name="large_df.csv",
                mime="text/csv",
            )

            # Adapt the function with the code below
            date = datetime.now()
            title = f'Report_{date.month}_{date.year}'
            os.chdir(r".\interface")

            # Create PDF object
            pdf = PDF("P","mm", "A4")
            
            pdf.header(title)
            pdf.alias_nb_pages() # Get total page numbers 
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font('helvetica', '', 16)

            # Print from txt 
            pdf.print_chapter(1, 'Total Energies', r'.\TTE.txt')
            pdf.print_chapter(2, 'Orange', r'.\ORA.txt')

            # Create pdf
            pdf.output(f'{title}.pdf')
    # End def show_report_tab

# End class StockAnalysisApp

def chrono(message: str = "") -> None:
    now = datetime.now()
    # now_str = now.strftime("%d-%m-%Y %H:%M:%s")
    st.write(f"{now} - {message}\n")
# End def chrono