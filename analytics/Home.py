
import streamlit as st



st.set_page_config(page_title="Tech Challenge", page_icon=":bar_chart:",layout="wide")


st.title("TimescaleDB for Financial Time Series Analysis and Database Management")


st.write("""
This web application serves as a demonstrative platform for the TimescaleDB extension of PostgreSQL, focusing on interactive and transparent data exploration. Developed using Streamlit, it offers dynamic updates to charts based on user selections and includes a dedicated section to view the SQL queries employed for data retrieval.

### Candlestick Chart
The section features an interactive candlestick chart for cryptocurrency price analysis. It contains a sidebar to select a cryptocurrency symbol, define date ranges, and choose time intervals such as month, week, day, or hour. The chart displays individual price candlesticks, volume information, and Simple Moving Average (SMA) lines. 

### Volume Comparison
A bar chart is presented to show traded volumes for all pairs within user-defined date ranges and time intervals. It also enables users to explore pairs with the highest and lowest trading volumes during the specified period. 

### Price Comparison
This section allows users to investigate percentage price changes over specified intervals, providing insights into cryptocurrency trends. Dynamic chart lines visually represent price changes over selected time intervals, offering an intuitive representation of trends in cryptocurrency prices.
""")