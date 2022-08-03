import pandas as pd
import yfinance as yf
import streamlit as st
import datetime as dt
import plotly.graph_objects as go

# import numpy as np

st.title('S Phase BioFund Portfolio Performance')

# update portfolio manually here
portfolio = {'TXG': 9, 'ALLO': 36, 'GBIO': 78, 'IBB': 5, 'NKTR': 61, 'XBI': 3, 'SPY': 4}
securities = list(portfolio.keys())
shares = list(portfolio.values())

# Create all accounts df

selected_period = '6mo'
portfolio_dfs = list()

for security in list(portfolio.keys()):
    security_ticker = yf.Ticker(security)
    security_df = security_ticker.history(period=selected_period)
    portfolio_dfs.append(security_df)

# scale each of the stock dfs based on how many shares we hold
scaled_dfs = list()
for i in range(len(shares)):
    scaled_df = portfolio_dfs[i] * shares[i]
    scaled_dfs.append(scaled_df)

# finally create an aggregate df
all_accounts_df = scaled_dfs[0].add(scaled_dfs[1])

for scaled_df in scaled_dfs[2:]:
    all_accounts_df = all_accounts_df.add(scaled_df)

# display current portfolio value
st.info('Total portfolio value on {} : $ {}'.format(dt.date.today(), round(all_accounts_df['Close'][-1], 2)))

# Display all accounts candlestick

dateStr1 = all_accounts_df.index.strftime("%m-%d-%Y")

fig1 = go.Figure(data=[go.Candlestick(x=dateStr1,
                                      open=all_accounts_df['Open'],
                                      high=all_accounts_df['High'],
                                      low=all_accounts_df['Low'],
                                      close=all_accounts_df['Close'])])

fig1.update_layout(
    title={
        'text': "S Phase (Total Portfolio)",
        'y': .82,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    width=900, height=350)
fig1.update_layout(xaxis_rangeslider_visible=False)

st.plotly_chart(fig1)

# Plot reference index

spy_ticker = yf.Ticker('SPY')  # SP500
ibb_ticker = yf.Ticker('IBB')  # iShares NASDAQ Biotechnology ETF

spy = spy_ticker.history(period=selected_period)
ibb = ibb_ticker.history(period=selected_period)

dateStr2 = spy.index.strftime("%m-%d-%Y")

fig2 = go.Figure(data=[go.Candlestick(x=dateStr2,
                                      open=spy['Open'],
                                      high=spy['High'],
                                      low=spy['Low'],
                                      close=spy['Close'])])

fig2.update_layout(
    title={
        'text': "S&P 500 (SPY)",
        'y': .82,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
    width=900, height=350)
fig2.update_layout(xaxis_rangeslider_visible=False)

st.plotly_chart(fig2)

# display table of reference stock returns
reference_stocks = [spy, ibb]
reference_stock_names = ['SPY', 'IBB']
references_returns = [round(((stock['Close'][-1] - stock['Close'][0]) / stock['Close'][0]) * 100, 1) for stock in
                      reference_stocks]
references_returns_df = pd.DataFrame(references_returns, index=reference_stock_names,
                                     columns=['% Return'])

# display table of portfolio returns
portfolio_stocks = [all_accounts_df] + portfolio_dfs.copy()
portfolio_stock_names = ['All Accounts', 'TXG', 'ALLO', 'GBIO', 'IBB', 'NKTR', 'XBI', 'SPY']

portfolio_returns = [round(((stock['Close'][-1] - stock['Close'][0]) / stock['Close'][0]) * 100, 1) for stock in
                     portfolio_stocks]
portfolio_returns_df = pd.DataFrame(portfolio_returns, index=portfolio_stock_names,
                                    columns=['% Return'])

st.markdown("<h3 style='text-align: center; color: black;'>{} Return (Portfolio)</h3>".format(selected_period),
            unsafe_allow_html=True)
st.dataframe(portfolio_returns_df)

st.markdown("<h3 style='text-align: center; color: black;'>{} Return (Reference indices)</h3>".format(selected_period),
            unsafe_allow_html=True)
st.dataframe(references_returns_df)

# plot portfolio composition pie chart
current_share_prices = list()

for ticker in portfolio.keys():
    tickerData = yf.Ticker(ticker)
    todayData = tickerData.history(period='1d')
    current_share_prices.append(round(todayData['Close'][0], 2))

market_values = [shares[i] * current_share_prices[i] for i in range(len(current_share_prices))]

colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen', 'cornflower blue']
info = ['percent+label', 'value+label']

fig3 = go.Figure(data=[go.Pie(labels=list(portfolio.keys()),
                              values=list(market_values))])
fig3.update_traces(hoverinfo='label+percent', textinfo=info[1], textfont_size=15,
                   marker=dict(colors=colors, line=dict(color='#000000', width=2)))

st.markdown("<h2 style='text-align: center; color: black;'>Portfolio Composition </h2>", unsafe_allow_html=True)

st.plotly_chart(fig3)
