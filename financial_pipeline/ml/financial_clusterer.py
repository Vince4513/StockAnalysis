import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from financial_pipeline.storage.company_storage import CompanyStorage


class FinancialClusterer:
    def __init__(self, db_path="financials.db"):
        self.db = CompanyStorage(db_path)
    # End def __init__

    def load_financial_data(self) -> pd.DataFrame:
        """Loads the latest financial data per company."""
        companies = self.db.list_companies()
        rows = []

        for _, name, _, _ in companies:
            financials = self.db.get_financials(name)
            if financials:
                latest = sorted(financials, key=lambda x: x[3])[-1]  # latest year
                rows.append((name,) + latest[4:])  # skip id, company_id, last_update, year

        columns = [
            "name", "share_price", "sales", "shares_issued", "current_assets",
            "current_liabilities", "financial_debts", "equity", "intangible_assets",
            "net_income", "dividends", "eps"
        ]
        return pd.DataFrame(rows, columns=columns).dropna()
    # End def load_financial_data

    def find_optimal_k(self, data: pd.DataFrame, k_min=2, k_max=10) -> int:
        features = data.drop(columns=["name"])
        scaled = StandardScaler().fit_transform(features)
        
        if scaled.shape[0] < 2:
            raise ValueError("Need at least 2 samples to compute silhouette score")

        best_k = k_min
        best_score = -1

        for k in range(k_min, min(k_max, len(data)), 1):
            model = KMeans(n_clusters=k, random_state=42)
            labels = model.fit_predict(scaled)
            score = silhouette_score(scaled, labels)
            if score > best_score:
                best_k = k
                best_score = score

        return best_k
    # End def find_optimal_k

    def cluster_companies(self, df: pd.DataFrame, k: int = None) -> pd.DataFrame:
        """Performs clustering and returns the DataFrame with cluster labels."""
        features = df.drop(columns=["name"])
        scaler = StandardScaler()
        scaled = scaler.fit_transform(features)
        
        if k is None:
            k = self.find_optimal_k(df)

        kmeans = KMeans(n_clusters=k, random_state=42)
        df["cluster"] = kmeans.fit_predict(scaled)
        return df
    # End def cluster_companies

    def summarize_clusters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Returns a summary of each cluster's average profile."""
        return df.groupby("cluster").mean(numeric_only=True)
    # End def summarize_clusters
# End class FinancialClusterer