# -*- coding: utf-8 -*- #
"""
Interface class
"""

import logging
import pandas as pd
import streamlit as st
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# from financial_pipeline.ml.models import Models
# from financial_pipeline.interface.reports import PDF

from financial_pipeline.storage.company_storage import CompanyStorage
from financial_pipeline.evaluator.graham_evaluator import GrahamEvaluator
from financial_pipeline.ml.financial_clusterer import FinancialClusterer

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

        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Single Company View", 
            "📊 Compare Companies",
            "🧠 Graham Evaluation",
            "🔍 Clustering Explorer"
        ])

        with tab1:
            self.display_single_company_view()

        with tab2:
            self.display_comparison_view()
        
        with tab3:
            self.display_graham_analysis()

        with tab4:
            self.display_clustering_analysis()
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

    # Tab 3: Graham Evaluator --------------------------------

    def display_graham_analysis(self) -> None:
        st.header("🧠 Graham Value Investing Criteria")

        evaluator = GrahamEvaluator(self.db_path)
        companies = self.db.list_companies()
        company_names = [c[1] for c in companies]

        selected = st.selectbox("Select a company to evaluate", company_names)
        results = evaluator.evaluate(selected)

        st.subheader(f"📄 Results for {selected}")
        passed_count = 0

        for rule, outcome in results.items():
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown("✅" if outcome["passed"] else "❌")
            with col2:
                st.markdown(f"**{rule}** — {outcome['description']}")
                st.caption(f"Result: {outcome['value']}")
            passed_count += int(outcome["passed"])

        st.success(f"✅ {passed_count} / 8 rules passed")

        st.markdown("---")

        self._top10_graham_score(evaluator, company_names)

        st.markdown("---")
        
        self._heatmap_graham_score(evaluator, company_names)
    # End def display_graham_analysis

    def _top10_graham_score(self, evaluator: GrahamEvaluator, company_names: list):
        # TOP 10 Companies by score
        st.subheader("🏅 Top 10 Companies by Graham Score")

        company_scores = []
        for name in company_names:
            res = evaluator.evaluate(name)
            score = sum(1 for r in res.values() if isinstance(r, dict) and r.get("passed"))
            company_scores.append((name, score))

        top_companies = sorted(company_scores, key=lambda x: x[1], reverse=True)[:10]
        st.table(pd.DataFrame(top_companies, columns=["Company", "Rules Passed"]))
    # End def _top10_graham_score

    def _heatmap_graham_score(self, evaluator: GrahamEvaluator, company_names: list):
        st.subheader("🔍 Graham Rule Heatmap")

        heatmap_data = {}
        for name in company_names:
            res = evaluator.evaluate(name)
            heatmap_data[name] = {
                rule: int(outcome.get("passed", False)) for rule, outcome in res.items() if isinstance(outcome, dict)
            }

        df_heatmap = pd.DataFrame(heatmap_data).T  # rows=companies, cols=rules

        start = st.slider("Start index", 0, len(df_heatmap) - 5, 0)
        end = st.slider("End index", start + 1, len(df_heatmap), start + 10)
        
        df_subset = df_heatmap.iloc[start:end]

        # Flip axes so companies are on Y, rules on X
        fig = px.imshow(
            df_subset.values,
            labels=dict(x="Rules", y="Companies", color="Pass"),
            x=df_subset.columns,
            y=df_subset.index,
            color_continuous_scale=["#cd3232", "#32cd32"],  # red (fail) → green (pass)
            text_auto=True,
            aspect="auto"
        )

        fig.update_layout(
            title="Graham Rule Pass/Fail Heatmap",
            xaxis_side="top",
            margin=dict(l=10, r=10, t=40, b=10)
        )

        st.plotly_chart(fig, use_container_width=True)
    # End def _heatmap_graham_score

   # Tab 4: Graham Evaluator --------------------------------

    def display_clustering_analysis(self) -> None:
        st.header("🔍 Company Clustering Explorer")

        clusterer = FinancialClusterer(self.db_path)
        df_raw = clusterer.load_financial_data()

        if df_raw.empty:
            st.warning("No financial data available to perform clustering.")
            return

        # Choose range for K
        k_range = st.slider("Choose range of clusters to evaluate", 2, 10, (2, 6))

        # Silhouette scores
        silhouette_scores = {}
        for k in range(k_range[0], k_range[1] + 1):
            try:
                df_temp = clusterer.cluster_companies(df_raw.copy(), k)
                features = df_temp.drop(columns=["name", "cluster"])
                scaled = StandardScaler().fit_transform(features)
                labels = df_temp["cluster"]
                score = silhouette_score(scaled, labels)
                silhouette_scores[k] = score
            except Exception:
                silhouette_scores[k] = None

        st.subheader("📈 Silhouette Scores")
        df_scores = pd.DataFrame(list(silhouette_scores.items()), columns=["k", "score"])
        fig = px.line(df_scores, x="k", y="score", markers=True, title="Silhouette Score by Cluster Count")
        st.plotly_chart(fig)

        # Select number of clusters to use
        default_k = max(silhouette_scores, key=lambda x: silhouette_scores[x] if silhouette_scores[x] is not None else -1)
        selected_k = st.selectbox("Choose number of clusters for visualization", df_scores["k"], index=df_scores["k"].tolist().index(default_k))

        # Perform clustering
        df_clustered = clusterer.cluster_companies(df_raw.copy(), k=selected_k)

        st.subheader("📊 2D Clustering Visualization (PCA)")
        features = df_clustered.drop(columns=["name", "cluster"])
        scaled = StandardScaler().fit_transform(features)
        pca = PCA(n_components=2)
        reduced = pca.fit_transform(scaled)

        df_clustered["PC1"] = reduced[:, 0]
        df_clustered["PC2"] = reduced[:, 1]

        fig = px.scatter(
            df_clustered,
            x="PC1",
            y="PC2",
            color=df_clustered["cluster"].astype(str),
            hover_data=["name"],
            title=f"{selected_k}-Cluster PCA Projection"
        )
        st.plotly_chart(fig)

        st.subheader("📋 Cluster Summary")
        st.dataframe(clusterer.summarize_clusters(df_clustered).round(2))
    # End def 


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
