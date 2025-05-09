# StockAnalysis
Retrieve the current share price and the financial results pdf of companies we want more knowledge on. That way we can select the one that are underrated with KPI based on Benjamin Graham's book "The Intelligent Investor".


## Reality 
1. [x] Find a list of stock tickers  
2. [x] Retrieve data with API Yahoo finance  
 - Lots of info in ticker.info(address, country, website, dividends, ...)  
3. [x] Store Company in a datastore  
4. [ ] Apply the rules

Check the None's in the retrieving data part
Do some plots 
Solve the None <= float problem in Rules
Add a report button to download pdf with a summary and 1 detailled page per company 

## Plan 
1. API Yahoo finance  
How to find all the PARIS tickers ? 
    - [x] Current Share price
    - [x] Number of shares issued (Nombres de titres émis) 
    - [x] Bilan comptable  
    - [x] compte de résultat

2. PDF data Extraction
    - Sales (CA)
    - Current assets (actif circulant)
    - Current liabilities (passif circulant)
    - Financial debts (dettes financières long terme)
    - Net income for the last 10 years (résultat net)
    - Dividends for the last 10 years (dividendes)
    - Net earnings per share (Bénéfice Net Par Action)
    - Number of shares issued (Nombres de titres émis)
    - Shareholders' equity (Capitaux propres)
    - Intangible assets (Immobilisations incorporelles / Goodwill)
Save all that data in a SQL database with date of extraction

3. Determine companies value
    - Calculate with values obtained the 7 rules and give a score.
    
4. Indicate which companies are overrated and which are underrated
    - Django website

## 7 Rules
1. Sales > 100 million (and also 50 million assets for utilities)
2. Current assets = 2 x Current liabilities - Financial debts <= (Current assets - Current liabilities)
3. Net income > 0 for 10 consecutive years
4. Uninterrupted dividends for 20 years
5. Average of first 3 years - Average of last 3 years - Earnings Per Share +33% over 10 years
6. Average of last 3 years EPS / current price <= 15
7. Market capitalization (nb_shares x current price) / Net book value of shareholders' equity (less intangible assets) < 1.5
--> PER x PBR <= 22.5

# 
1. Chiffres d'affaires > 100 millions (et également 50 millions d'actifs pour les services publics)
2. Actif circulant = 2 x Passif circulant - Dettes financières <= (Actif circulant - Passif circulant)
3. Résultat net > 0 sur 10 ans consécutifs
4. Dividendes ininterrompu sur 20 ans
5. Moyenne des 3 premières années - Moyenne des 3 dernières années - Bénéfice Net Par Action +33% sur 10 ans
6. Moyenne des 3 dernières années BNPA / cours actuel <= 15
7. Capitalisation boursière (nb_titres x cours actuel) / Valeur nette comptable  des capitaux propres (déduction faite des immobilisations incorporelles) < 1.5
--> PER x PBR <= 22.5

## 
In google, type:
1. [company name] share price

1. [company name] financial results :pdf
Depends on the company website:
2. on the website, Annual results -> FY [year] 

## Documentation
[Medium Context](https://medium.com/@aguimarneto/python-stock-price-apis-e67d5310f6e3)  
[YAHOO Market Place](https://fr.aide.yahoo.com/kb/SLN2310.html#/)  
[Documentation & Code - yfinance](https://github.com/ranaroussi/yfinance/tree/main)  

### Notes
In the project, when we retrieve the data, there is 2 ways to achieve the same purpose:  
- First, using *yf.Ticker(ticker).incomestmt*  
- Second, using *yf.Ticker(ticker).financials*  

For this project, I will keep *yf.Ticker(ticker).incomestmt* but it's possible to retrieve with *yf.Ticker(ticker).financials* (same data).  

- net income / dividends / net earning per share are all stored under a pandas Dataframe with a datetime64[ns] type index.

python -m scripts.run_pipeline
streamlit run .\scripts\run_streamlit.py