import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import date

# ─── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="Market Trend Dashboard",
    page_icon="📈",
    layout="wide"
)

# ─── TITLE ─────────────────────────────────────────────────
st.title("📈 Market Trend Dashboard")
st.markdown("Analyse any asset — stocks, indices, commodities, ETFs")
st.divider()

# ─── HELPER FUNCTIONS ──────────────────────────────────────
def download_data(ticker, start, end):
    data = yf.download(ticker, start=start, end=end,
                      auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.droplevel(1)
    df = data[['Close', 'Volume']].copy()
    df.dropna(inplace=True)
    return df

def add_indicators(df):
    df['MA20']         = df['Close'].rolling(20).mean()
    df['MA50']         = df['Close'].rolling(50).mean()
    df['MA200']        = df['Close'].rolling(200).mean()
    df['Daily_Return'] = df['Close'].pct_change()
    df['Volatility']   = df['Daily_Return'].rolling(30).std() * 100
    df['Regime']       = df.apply(
        lambda r: 'Bull' if r['Close'] > r['MA200'] else 'Bear', axis=1
    )
    df['Normalised']   = (df['Close'] / df['Close'].iloc[0]) * 100
    return df

def get_summary(df, portfolio_value=100_000):
    total_return = (df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0] * 100
    sharpe       = (df['Daily_Return'].mean() / df['Daily_Return'].std()) * np.sqrt(252)
    bull_days    = (df['Regime'] == 'Bull').sum()
    bear_days    = (df['Regime'] == 'Bear').sum()
    return {
        'total_return' : total_return,
        'sharpe'       : sharpe,
        'best_day'     : df['Daily_Return'].max() * 100,
        'worst_day'    : df['Daily_Return'].min() * 100,
        'avg_vol'      : df['Volatility'].mean(),
        'max_vol'      : df['Volatility'].max(),
        'bull_days'    : bull_days,
        'bear_days'    : bear_days,
    }

# ─── SIDEBAR ───────────────────────────────────────────────
st.sidebar.header("Settings")

mode = st.sidebar.radio("Mode", ["Single Asset", "Compare Two Assets"])

ticker1 = st.sidebar.text_input("Ticker 1", value="^DJI",
    help="Examples: AAPL, TSLA, GC=F, ^GSPC, BTC-USD")

ticker2 = None
if mode == "Compare Two Assets":
    ticker2 = st.sidebar.text_input("Ticker 2", value="AAPL")

start_date = st.sidebar.date_input("Start Date",
    value=date(2018, 1, 1),
    min_value=date(2000, 1, 1),
    max_value=date.today()
)
end_date = st.sidebar.date_input("End Date",
    value=date(2023, 12, 31),
    min_value=date(2000, 1, 1),
    max_value=date.today()
)

show_ma20  = st.sidebar.checkbox("20-day MA",  value=True)
show_ma50  = st.sidebar.checkbox("50-day MA",  value=True)
show_ma200 = st.sidebar.checkbox("200-day MA", value=True)

run = st.sidebar.button("Run Analysis", type="primary")

# ─── SINGLE ASSET MODE ─────────────────────────────────────
if run and mode == "Single Asset":
    with st.spinner(f'Downloading {ticker1} data...'):
        df = download_data(ticker1, start_date, end_date)
        df = add_indicators(df)

    if df.empty:
        st.error("No data found. Please check the ticker symbol.")
    else:
        s = get_summary(df)

        # metrics row
        st.subheader(f"Summary — {ticker1.upper()}")
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Total Return",   f"{s['total_return']:.1f}%")
        c2.metric("Sharpe Ratio",   f"{s['sharpe']:.2f}")
        c3.metric("Best Day",       f"{s['best_day']:.2f}%")
        c4.metric("Worst Day",      f"{s['worst_day']:.2f}%")
        c5.metric("Avg Volatility", f"{s['avg_vol']:.2f}%")
        c6.metric("Max Volatility", f"{s['max_vol']:.2f}%")
        st.divider()

        # price + MA chart
        st.subheader("Price & Moving Averages")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df.index, y=df['Close'],
            name='Close Price', line=dict(color='steelblue', width=1), opacity=0.8))
        if show_ma20:
            fig1.add_trace(go.Scatter(x=df.index, y=df['MA20'],
                name='20-day MA', line=dict(color='orange', width=1.5)))
        if show_ma50:
            fig1.add_trace(go.Scatter(x=df.index, y=df['MA50'],
                name='50-day MA', line=dict(color='green', width=1.5)))
        if show_ma200:
            fig1.add_trace(go.Scatter(x=df.index, y=df['MA200'],
                name='200-day MA', line=dict(color='red', width=2)))
        fig1.update_layout(height=450, xaxis_title='Date',
                          yaxis_title='Price', hovermode='x unified')
        st.plotly_chart(fig1, use_container_width=True)

        # returns + volatility
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Daily Returns")
            colors = ['green' if r > 0 else 'red'
                     for r in df['Daily_Return'].fillna(0)]
            fig2 = go.Figure(go.Bar(x=df.index,
                y=df['Daily_Return']*100, marker_color=colors))
            fig2.update_layout(height=350, xaxis_title='Date',
                              yaxis_title='Return (%)')
            st.plotly_chart(fig2, use_container_width=True)

        with col2:
            st.subheader("30-Day Rolling Volatility")
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=df.index, y=df['Volatility'],
                fill='tozeroy', fillcolor='rgba(147,112,219,0.3)',
                line=dict(color='purple', width=1.5), name='Volatility'))
            fig3.add_hline(y=s['avg_vol'], line_dash='dash',
                          line_color='red',
                          annotation_text=f"Avg: {s['avg_vol']:.2f}%")
            fig3.update_layout(height=350, xaxis_title='Date',
                              yaxis_title='Volatility (%)')
            st.plotly_chart(fig3, use_container_width=True)

        # bull/bear + best/worst
        col3, col4 = st.columns(2)
        with col3:
            st.subheader("Bull vs Bear Market Days")
            fig4 = go.Figure(go.Pie(
                labels=['Bull Market', 'Bear Market'],
                values=[s['bull_days'], s['bear_days']],
                marker_colors=['steelblue', 'tomato'], hole=0.4))
            fig4.update_layout(height=350)
            st.plotly_chart(fig4, use_container_width=True)

        with col4:
            st.subheader("Top 5 Best & Worst Days")
            best5  = df.nlargest(5, 'Daily_Return')[['Close', 'Daily_Return']].copy()
            worst5 = df.nsmallest(5, 'Daily_Return')[['Close', 'Daily_Return']].copy()
            best5['Daily_Return']  = (best5['Daily_Return']*100).round(2).astype(str) + '%'
            worst5['Daily_Return'] = (worst5['Daily_Return']*100).round(2).astype(str) + '%'
            best5.columns  = ['Close Price', 'Return']
            worst5.columns = ['Close Price', 'Return']
            st.markdown("**Best Days 🟢**")
            st.dataframe(best5, use_container_width=True)
            st.markdown("**Worst Days 🔴**")
            st.dataframe(worst5, use_container_width=True)

        # download button
        st.divider()
        st.subheader("Download Data")
        csv = df.to_csv().encode('utf-8')
        st.download_button(
            label     = "Download as CSV",
            data      = csv,
            file_name = f"{ticker1}_{start_date}_{end_date}.csv",
            mime      = "text/csv"
        )

# ─── COMPARE TWO ASSETS MODE ───────────────────────────────
elif run and mode == "Compare Two Assets":
    with st.spinner(f'Downloading {ticker1} and {ticker2} data...'):
        df1 = download_data(ticker1, start_date, end_date)
        df2 = download_data(ticker2, start_date, end_date)
        df1 = add_indicators(df1)
        df2 = add_indicators(df2)

    if df1.empty or df2.empty:
        st.error("Could not find data for one or both tickers.")
    else:
        s1 = get_summary(df1)
        s2 = get_summary(df2)

        # comparison metrics
        st.subheader(f"Comparison — {ticker1.upper()} vs {ticker2.upper()}")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### {ticker1.upper()}")
            a, b, c = st.columns(3)
            a.metric("Total Return",  f"{s1['total_return']:.1f}%")
            b.metric("Sharpe Ratio",  f"{s1['sharpe']:.2f}")
            c.metric("Avg Volatility",f"{s1['avg_vol']:.2f}%")

        with col2:
            st.markdown(f"### {ticker2.upper()}")
            a, b, c = st.columns(3)
            a.metric("Total Return",  f"{s2['total_return']:.1f}%")
            b.metric("Sharpe Ratio",  f"{s2['sharpe']:.2f}")
            c.metric("Avg Volatility",f"{s2['avg_vol']:.2f}%")

        st.divider()

        # normalised price comparison
        st.subheader("Normalised Price (Both Start at 100)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df1.index, y=df1['Normalised'],
            name=ticker1.upper(), line=dict(color='steelblue', width=2)))
        fig.add_trace(go.Scatter(x=df2.index, y=df2['Normalised'],
            name=ticker2.upper(), line=dict(color='orange', width=2)))
        fig.add_hline(y=100, line_dash='dash', line_color='gray',
                     annotation_text='Starting Point')
        fig.update_layout(height=450, xaxis_title='Date',
                         yaxis_title='Normalised Price (Base 100)',
                         hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

        # volatility comparison
        st.subheader("Volatility Comparison")
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df1.index, y=df1['Volatility'],
            name=ticker1.upper(), line=dict(color='steelblue', width=1.5)))
        fig2.add_trace(go.Scatter(x=df2.index, y=df2['Volatility'],
            name=ticker2.upper(), line=dict(color='orange', width=1.5)))
        fig2.update_layout(height=350, xaxis_title='Date',
                          yaxis_title='Volatility (%)', hovermode='x unified')
        st.plotly_chart(fig2, use_container_width=True)

        # bull/bear comparison
        col3, col4 = st.columns(2)
        with col3:
            st.subheader(f"{ticker1.upper()} — Bull vs Bear")
            fig3 = go.Figure(go.Pie(
                labels=['Bull', 'Bear'],
                values=[s1['bull_days'], s1['bear_days']],
                marker_colors=['steelblue', 'tomato'], hole=0.4))
            fig3.update_layout(height=300)
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.subheader(f"{ticker2.upper()} — Bull vs Bear")
            fig4 = go.Figure(go.Pie(
                labels=['Bull', 'Bear'],
                values=[s2['bull_days'], s2['bear_days']],
                marker_colors=['steelblue', 'tomato'], hole=0.4))
            fig4.update_layout(height=300)
            st.plotly_chart(fig4, use_container_width=True)

        # download both
        st.divider()
        st.subheader("Download Data")
        col5, col6 = st.columns(2)
        with col5:
            csv1 = df1.to_csv().encode('utf-8')
            st.download_button(
                label     = f"Download {ticker1.upper()} CSV",
                data      = csv1,
                file_name = f"{ticker1}_{start_date}_{end_date}.csv",
                mime      = "text/csv"
            )
        with col6:
            csv2 = df2.to_csv().encode('utf-8')
            st.download_button(
                label     = f"Download {ticker2.upper()} CSV",
                data      = csv2,
                file_name = f"{ticker2}_{start_date}_{end_date}.csv",
                mime      = "text/csv"
            )

else:
    st.info("Enter a ticker symbol in the sidebar and click Run Analysis.")
    st.markdown("""
    **Example tickers to try:**
    - `^GSPC` — S&P 500
    - `^DJI` — Dow Jones
    - `AAPL` — Apple
    - `TSLA` — Tesla
    - `GC=F` — Gold
    - `BTC-USD` — Bitcoin
    """)