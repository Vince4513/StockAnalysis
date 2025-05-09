# -*- coding: utf-8 -*- #
"""
Interface class
"""

import os
import logging
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

# from financial_pipeline.ml.models import Models
# from financial_pipeline.rules.rules import Rules
# from financial_pipeline.interface.reports import PDF

from financial_pipeline.storage.company_storage import CompanyStorage

# ===========================================================================
# Constant and global variables
# ===========================================================================

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ==================================================================================================================================================
# FinancialDataInterface Class
# ==================================================================================================================================================

class FinancialDataInterface :
    """App displaying financial info from companies"""

    def __init__(self, db_path: str | None=None) -> None:
        
        st.set_page_config(
            page_title="Stock Analysis",
            page_icon=":bar_chart:",
            layout="wide"
        )

        # Store the paths database
        self.db_path = db_path or "data/processed/test.db"
        self.db = CompanyStorage(db_path)
    # End def __init__

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Public Methods
    # ----------------------------------------------------------------------------------------------------------------------------------------------

    def run(self):
        st.title("📊 Company Financial Explorer")

        tab1, tab2 = st.tabs(["📈 Single Company View", "📊 Compare Companies"])

        with tab1:
            self.display_single_company_view()

        with tab2:
            self.display_comparison_view()
    # End def run

    # ----------------------------------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ----------------------------------------------------------------------------------------------------------------------------------------------
    
    # Tab 1: Single Company ----------------------------------
    
    def display_single_company_view(self) -> None:
        companies = self.db.list_companies()
        if not companies:
            st.warning("No companies found in database.")
            return

        company_names = [c[1] for c in companies]
        selected_name = st.selectbox("Select a company", company_names)

        self.display_company_info(selected_name)
        df = self.display_financial_charts(selected_name)

        # Export as CSV
        if df is not None:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Financials as CSV",
                data=csv,
                file_name=f"{selected_name}_financials.csv",
                mime="text/csv"
            )
    # End def display_single_company_view

    def display_company_info(self, name: str) -> None:
        company = self.db.get_company(name)
        if not company:
            st.error("Company not found.")
            return

        # Map to column names manually
        columns = [
            "id", "name", "country", "phone", "website", "industry", "sector",
            "region", "full_exchange_name", "exchange_timezone", "isin", "full_time_employees"
        ]
        info = dict(zip(columns, company))

        st.subheader("📄 Company Information")
            
        # Group definitions
        group_1 = {
            "Company Name": info.get("name"),
            "ISIN": info.get("isin"),
            "Sector": info.get("sector"),
            "Industry": info.get("industry"),
        }

        group_2 = {
            "Country": info.get("country"),
            "Region": info.get("region"),
            "Exchange": info.get("full_exchange_name"),
            "Timezone": info.get("exchange_timezone"),
        }

        group_3 = {
            "Phone": info.get("phone"),
            "Website": info.get("website"),
            "Employees": info.get("full_time_employees"),
        }

        # Display in 3 columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### 🏢 Company Profile")
            for label, value in group_1.items():
                if value:
                    st.markdown(f"**{label}:** {value}")

        with col2:
            st.markdown("#### 🌍 Market Info")
            for label, value in group_2.items():
                if value:
                    st.markdown(f"**{label}:** {value}")

        with col3:
            st.markdown("#### 📞 Contact")
            for label, value in group_3.items():
                if value:
                    st.markdown(f"**{label}:** {value}")
    # End def display_company_info

    def display_financial_charts(self, name: str) -> pd.DataFrame:
        rows = self.db.get_financials(name)
        if not rows:
            st.warning("No financial data available.")
            return

        columns = [
            "id", "company_id", "last_update", "year", "share_price", "sales", "shares_issued", "current_assets",
            "current_liabilities", "financial_debts", "equity", "intangible_assets", "net_income",
            "dividends", "eps"
        ]
        df = pd.DataFrame(rows, columns=columns).sort_values("year")

        st.subheader("📈 Financial Trends")

        metrics = ["sales", "net_income", "dividends", "eps", "share_price", "equity"]

        selected_metrics = st.multiselect(
            "Select metrics to visualize:", metrics, default=["sales", "net_income"]
        )

        for metric in selected_metrics:
            st.line_chart(df.set_index("year")[metric])

        return df
    # End def display_financial_charts

    # Tab 2: Compare Companies -------------------------------
    
    def display_comparison_view(self) -> None:
        companies = self.db.list_companies()
        if len(companies) < 2:
            st.warning("You need at least two companies in the database to compare.")
            return

        company_names = [c[1] for c in companies]

        col1, col2 = st.columns(2)
        with col1:
            company1 = st.selectbox("Company 1", company_names, key="cmp1")
        with col2:
            company2 = st.selectbox("Company 2", company_names, index=1, key="cmp2")

        if company1 == company2:
            st.warning("Please select two different companies.")
            return

        df1 = self._get_financial_df(company1)
        df2 = self._get_financial_df(company2)

        if df1 is None or df2 is None:
            return

        st.subheader("📊 Metric Comparison Over Time")
        metrics = ["sales", "net_income", "dividends", "eps", "share_price", "equity"]

        selected_metrics = st.multiselect("Metrics to compare:", metrics, default=["sales", "net_income"])

        for metric in selected_metrics:
            fig = self._plot_grouped_bar(df1, df2, metric, company1, company2)
            st.plotly_chart(fig, use_container_width=True)
    # End def display_comparison_view

    def _get_financial_df(self, company_name: str) -> pd.DataFrame:
        rows = self.db.get_financials(company_name)
        if not rows:
            st.warning(f"No financial data for {company_name}")
            return None

        columns = [
            "id", "company_id", "last_update", "year", "share_price", "sales", "shares_issued", "current_assets",
            "current_liabilities", "financial_debts", "equity", "intangible_assets", "net_income",
            "dividends", "eps"
        ]
        return pd.DataFrame(rows, columns=columns).sort_values("year")
    # End def _get_financial_df

    def _plot_grouped_bar(self, df1: pd.DataFrame, df2: pd.DataFrame, metric: str, company1: str, company2: str):
        df1_plot = df1[["year", metric]].copy()
        df1_plot["company"] = company1

        df2_plot = df2[["year", metric]].copy()
        df2_plot["company"] = company2

        combined = pd.concat([df1_plot, df2_plot])
        
        fig = px.bar(
            combined,
            x="year",
            y=metric,
            color="company",
            barmode="group",
            title=f"{metric.title()} Comparison",
        )

        return fig
    # End def plot_grouped_bar

    # Old functions
    # def show_tabs(self) -> None:
    #     """Display the tabs of the streamlit app"""

    #     st.title("Stock Analysis Dashboard")
    #     st.markdown("_Prototype v0.1.0_")

    #     raw_data_tab, plots, rules_tab, regression_tab, report_tab = st.tabs(
    #         ["Upload", "Plots", "7 Rules", "Regression", "Reports"])

    #     df = self.show_raw_data_tab(raw_data_tab)
    #     # self.show_graphs(plots, df)
    #     # self.show_kpi_tab(kpi_tab)
    #     self.show_rules_tab(rules_tab, df)
    #     # self.show_regres_tab(regression_tab, df)
    #     # self.show_report_tab(report_tab, df)
    # # End def show_tabs

    # def show_raw_data_tab(self, tab) -> pd.DataFrame:
    #     with tab:
    #         st.header("Raw data")

    #         # Dataframe of all companies from the database
    #         df = self.imprt.as_rule_dataframe()
    #         chrono("Data transformed in dataframe !")
            
    #         # Step 1: Check structure
    #         st.header("Check structure")
    #         st.dataframe(df.head())
    #         st.write(f"Shape: {df.shape}")
    #         st.write(f"Info: {df.info()}")

    #         # Step 2: Statistical summary
    #         st.header("Statistical summary")
    #         st.write(df.describe())

    #         # Step 3: Missing values
    #         st.header("Missing values")
    #         st.dataframe(df.isnull().sum())

    #         # Step 4: Check duplicates
    #         st.header("Check duplicates")
    #         st.write("Number of duplicates:", df.duplicated().sum())

    #         return df
    # # End def show_kpi_tab

    # def show_graphs(self, tab, df: pd.DataFrame) -> None:
    #     with tab:
    #         st.header("Graphs")
            
    #         # Step 5: Visualizations
    #         fig, ax = plt.subplots()
    #         sns.histplot(df['sales'], bins=40, ax=ax)
    #         st.pyplot(fig)
            
    #         # fig, ax = plt.subplots()
    #         # sns.heatmap(df.corr(), annot=True, ax=ax)
    #         # st.pyplot(fig)
    # # End def show_graphs

    # def show_rules_tab(self, tab, df: pd.DataFrame) -> None:
    #     with tab:
    #         st.header("7 Rules")
            
    #         try:
    #             # Connect to Rules module ----------------------------------
    #             Rule = Rules()
    #             Rule.determine_rules(df)
    #             chrono("Rules determined !")

    #             st.dataframe(Rule.df_rules)
    #             st.write(Rule.PER, Rule.PBR)
                
    #         except Exception as e:
    #             st.write(f"Error: {e}")
    # # End def show_rules_tab

    # def show_regres_tab(self, tab, df: pd.DataFrame) -> None:
    #     with tab:
    #         st.header("Regression")
    #         ml = Models(df, 'sales')
    #         ml.get_score(estimators = 100)
    #         ml.plot_errors()     
    # # End def show_regres_tab

    # def show_report_tab(self, tab, df: pd.DataFrame) -> None:
    #     with tab:
    #         st.header("Report")

    #         @st.cache_data
    #         def convert_df(df):
    #             # IMPORTANT: Cache the conversion to prevent computation on every rerun
    #             return df.to_csv().encode("utf-8")

    #         csv = convert_df(df)

    #         st.download_button(
    #             label="Download data as CSV",
    #             data=csv,
    #             file_name="large_df.csv",
    #             mime="text/csv",
    #         )

    #         # Adapt the function with the code below
    #         date = datetime.now()
    #         title = f'Report_{date.month}_{date.year}'
    #         os.chdir(r".\interface")

    #         # Create PDF object
    #         pdf = PDF("P","mm", "A4")
            
    #         pdf.header(title)
    #         pdf.alias_nb_pages() # Get total page numbers 
    #         pdf.set_auto_page_break(auto=True, margin=15)
    #         pdf.set_font('helvetica', '', 16)

    #         # Print from txt 
    #         pdf.print_chapter(1, 'Total Energies', r'.\TTE.txt')
    #         pdf.print_chapter(2, 'Orange', r'.\ORA.txt')

    #         # Create pdf
    #         pdf.output(f'{title}.pdf')
    # # End def show_report_tab
# End class FinancialDataInterface


def run_streamlit_app():
    interface = FinancialDataInterface()
    interface.run()