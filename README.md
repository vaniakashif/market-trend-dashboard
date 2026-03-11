# Market Trend Dashboard

An interactive web application for analysing financial asset trends. Built with Python and Streamlit, the dashboard allows users to analyse any stock, index, commodity or ETF using real-time data from Yahoo Finance.

---

## Live Demo

> 🔗https://market-trend-dashboard-app.streamlit.app/ 

---

## Features

**Single Asset Mode**
- Interactive price chart with toggleable 20, 50 and 200-day moving averages
- Daily returns bar chart (green/red)
- 30-day rolling volatility chart
- Bull vs bear market breakdown (pie chart)
- Top 5 best and worst trading days
- Summary metrics total return, Sharpe ratio, avg/max volatility
- Download full dataset as CSV

**Compare Two Assets Mode**
- Normalised price chart (both assets start at 100 for fair comparison)
- Side by side summary metrics of total return, Sharpe ratio, volatility
- Volatility comparison chart
- Bull vs bear breakdown for both assets
- Download CSV for both assets

**Flexible Settings**
- Any ticker supported(stocks, indices, commodities, crypto, ETFs)
- Custom date range from 2000 to today
- Toggle moving averages on/off

---

## Example Tickers to Try

| Ticker | Asset |
|---|---|
| `^DJI` | Dow Jones Industrial Average |
| `^GSPC` | S&P 500 |
| `AAPL` | Apple |
| `TSLA` | Tesla |
| `MSFT` | Microsoft |
| `GC=F` | Gold Futures |
| `BTC-USD` | Bitcoin |
| `^TNX` | 10-Year Treasury Yield |

---

## How to Run Locally

**Step 1 — Clone the repository:**
```bash
git clone https://github.com/vaniakashif/market-trend-dashboard
cd market-trend-dashboard
```

**Step 2 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**Step 3 — Run the dashboard:**
```bash
streamlit run dashboard.py
```

**Step 4 — Open in browser:**
```
http://localhost:8501
```

---

## Key Concepts Used

**Moving Averages**
```
20 day  → short term trend (1 month)
50 day  → medium term trend (2.5 months)
200 day → long term bull/bear regime
```

**Normalised Price**
```
Both assets scaled to start at 100
→ allows fair comparison regardless of price difference
→ shows % growth from starting point
```

**Sharpe Ratio**
```
Measures return per unit of risk taken
Higher Sharpe = more efficient investment
Sharpe = (mean daily return / std) × sqrt(252)
```

**Rolling Volatility**
```
30-day standard deviation of daily returns
Shows how wildly prices jumped around recently
Spikes during market crises (COVID 2020, rate hikes 2022)
```

**Bull vs Bear Market**
```
Price above 200-day MA → Bull market day
Price below 200-day MA → Bear market day
```

---

## Tech Stack

```
Language   : Python 3
Framework  : Streamlit
Charts     : Plotly
Data       : Yahoo Finance via yfinance
Libraries  : pandas, numpy, scipy
```

---

## Project Structure
```
market-trend-dashboard/
│
├── dashboard.py        ← main application
├── requirements.txt    ← dependencies
├── runtime.txt         ← Python version for deployment
└── README.md
```



