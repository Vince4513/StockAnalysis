# 🧠 Graham-Based Financial Analysis Tool

This project is a full-stack financial data pipeline that imports, cleans, stores, analyzes, and visualizes company financials based on **Benjamin Graham’s investment principles** (from *The Intelligent Investor*).

It provides a **Streamlit dashboard** to explore financials, compare companies, and evaluate them against 7 key Graham rules (+1 bonus rule).

You can test for yourself here : [Web application](https://stockanalysis-dd27.onrender.com/)

---

## 📊 Features

- 🔄 **Automated data importer** from Yahoo Finance using `yfinance`
- 🧹 **Financial data cleaner** to structure and normalize key metrics
- 🗃️ **SQLite storage** with normalized schema
- 🧠 **Graham Evaluator** for applying value investing rules:
  - Sales threshold
  - Debt ratios
  - Earnings stability
  - Dividend history
  - EPS growth and valuation metrics
- 🖥️ **Streamlit dashboard**:
  - View company info & financial charts
  - Compare 2 companies side-by-side
  - Evaluate Graham rules + heatmap across all companies
  - Export to CSV



## 📁 Project Structure

financial_pipeline/  
├── cleaner/ # Cleans raw data into structured format   
├── evaluator/ # GrahamEvaluator logic (investment rules)  
├── importer/ # FinancialDataImporter using yfinance  
├── interface/ # Streamlit UI logic  
├── ml/ # In working progress (Clustering)  
├── storage/ # CompanyStorage class (SQLite backend)  
├── utils/ # Helpers: parsing, insertion, formatting  
scripts/  
└── run_pipeline.py # Entrypoint for launching database ingestion 
└── run_streamlit.py # Entrypoint for launching Streamlit app  
tests/  
└── test_* # Unit tests for core modules  
LICENSE  
poetry.lock  
pyproject.toml # Package setup  
README.md  



## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Vince4513/StockAnalysis.git
cd stock_analysis
```
### 2. Install dependencies

```bash
poetry install
```

### 3. Launch Streamlit dashboard

```bash
streamlit run scripts/run_streamlit.py
```

### 🧪 Running Tests

```bash
python -m unittest discover -s tests
```


## 📦 Core Technologies
| Area         | Tools                                                      |
|--------------|------------------------------------------------------------|
| Data Import  | [yfinance](https://pypi.org/project/yfinance/)             |
| Storage      | SQLite + custom schema                                     |
| Cleaning     | Custom parsing logic                                       |
| Interface    | [Streamlit](https://streamlit.io/), [Plotly](https://plotly.com/) |
| Evaluation   | Benjamin Graham's "The Intelligent Investor"               |


## 📘 Graham’s 7 (+1) Investment Rules

Each company is evaluated against these rules:

1. Sales > $100M (or $50M for utilities)

2. Current ratio + low financial debt

3. 10 years of positive net income

4. 20 years of uninterrupted dividends

5. EPS growth of 33% over last 10 years

6. P/E ratio ≤ 15

7. P/B ratio × shares ≤ 1.5

8. Bonus Rule: P/E × P/B ≤ 22.5

## 🧠 Why This Project?

This tool is ideal for:

- Value investors and finance students

- Data scientists exploring financial data pipelines

- Anyone building an integrated dashboard from raw financial data to actionable insights


## 📃 License

This project is licensed under the MIT License.  


## 🙋‍♂️ Acknowledgments  

- Benjamin Graham's The Intelligent Investor

- Yahoo Finance for data APIs

- yfinance, streamlit, plotly, sqlite3


## 📄 Disclaimer

This project uses financial data obtained through the open-source [`yfinance`](https://pypi.org/project/yfinance/) library, which accesses publicly available Yahoo Finance APIs.

- Yahoo!, Y!Finance, and Yahoo! finance are registered trademarks of Yahoo, Inc.
- `yfinance` is not affiliated, endorsed, or vetted by Yahoo, Inc.
- This project is intended **strictly for educational and research purposes**.

Please review Yahoo’s [Terms of Use](https://legal.yahoo.com/us/en/yahoo/terms/product-atos/index.html) for details on your rights to use the data.

📌 **The Yahoo Finance API is intended for personal use only.**