import streamlit as st
from plotly.subplots import make_subplots
import datetime
import plotly.graph_objects as go

st.set_page_config(page_title="Candlestick", page_icon=":bar_chart:",layout="wide")

# Initialize connection.
conn = st.connection("postgresql", type="sql")

# funciton to query the database and plot the results
def query_and_plot_price_vol(selected_symbol,startDate,endDate, time_bucket, sma_n1, sma_n2, sma_n3):
    
    if "hour" in time_bucket:
       table_name = "dataset_by_hour"
       time_col_name = "time_hour"
    elif "day" in time_bucket:
       table_name = "dataset_by_day"
       time_col_name = "time_day"
    elif "week" in time_bucket:
       table_name = "dataset_by_week"
       time_col_name = "time_week"
    elif "month" in time_bucket:
       table_name = "dataset_by_month"
       time_col_name = "time_month"


    query = """
        -- Outer query computes moving averages and selects relevant columns
        SELECT
          bucket,
          volume,
          price_open,
          price_close,
          price_high,
          price_low,
          -- Compute Simple Moving Average (SMA)
          AVG(price_close) OVER (ORDER BY bucket ROWS BETWEEN '{sma_n1_length}' PRECEDING AND CURRENT ROW) AS sma_n1,
          AVG(price_close) OVER (ORDER BY bucket ROWS BETWEEN '{sma_n2_length}' PRECEDING AND CURRENT ROW) AS sma_n2,
          AVG(price_close) OVER (ORDER BY bucket ROWS BETWEEN '{sma_n3_length}' PRECEDING AND CURRENT ROW) AS sma_n3
        FROM (
          -- Inner query aggregates data into {bucket} buckets
          SELECT 
            time_bucket('{bucket}', {time_col_name}) AS bucket,
            sum(trading_volume) AS volume, 
            FIRST(price_open, {time_col_name}) AS price_open, 
            LAST(price_close, {time_col_name}) AS price_close,
            MAX(price_high) AS price_high,
            MIN(price_low) AS price_low
          FROM {table_name}
          -- Filter data for a specific symbol and time range
          WHERE symbol = '{symbol}' 
            AND {time_col_name} BETWEEN '{start_date}' AND '{end_date}'
          GROUP BY bucket
        ) AS custom_interval_data
        -- Order the result set by time bucket
        ORDER BY bucket;
    """.format(table_name=table_name,time_col_name=time_col_name,bucket=time_bucket, symbol=selected_symbol, start_date=startDate, end_date=endDate,
               sma_n1_length =str(int(sma_n1)-1),sma_n2_length =str(int(sma_n2)-1),sma_n3_length =str(int(sma_n3)-1) ); 
 
    # Perform query.
    df = conn.query(query, ttl="10m")

    # Create subplots and define plot grid size
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
               vertical_spacing=0.03, 
               row_width=[0.2, 0.9])

    # Plot OHLC on 1st row
    fig.add_trace(go.Candlestick(x=df['bucket'],
                    open=df['price_open'],
                    high=df['price_high'],
                    low=df['price_low'],
                    close=df['price_close'],showlegend=False, name ="OHLC"), 
                    row=1, col=1)
    
    # Add SMA plots on 1st row
    fig.add_trace(go.Line(x=df['bucket'],y=df['sma_n1'], name = "SMA"+str(sma_n1)),row=1, col=1)
    fig.add_trace(go.Line(x=df['bucket'],y=df['sma_n2'], name = "SMA"+str(sma_n2)),row=1, col=1)
    fig.add_trace(go.Line(x=df['bucket'],y=df['sma_n3'], name = "SMA"+str(sma_n3)),row=1, col=1)
    
    # Bar trace for volumes on 2nd row without legend
    fig.add_trace(go.Bar(x=df['bucket'], y=df['volume'], showlegend=False, name ="Volume"), row=2, col=1)

    fig.update(layout_xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    return query


# Choose the chart options from the sidebar
st.sidebar.title("Choose chart options")
selected_symbol = st.sidebar.selectbox(
  'Select symbol to plot',
  ('BTC_USD','ETH_USD','BCH_USD','XRP_USD','LTC_USD',
  'TRX_USD','ETC_USD','LINK_USD','XLM_USD','ADA_USD',
  'XTZ_USD','ATOM_USD','BNB_USD','VET_USD','THETA_USD',
  'ALGO_USD','DOGE_USD','DOT_USD','EGLD_USD','SOL_USD',
  'UNI_USD','AVAX_USD','MATIC_US','AXS_USD',))

st.sidebar.write('### Define date range')
startDate = st.sidebar.date_input("Start date:", datetime.date(2019, 9, 8))
endDate   = st.sidebar.date_input("End date:",   datetime.date(2023, 10, 6))

st.sidebar.write('### Define time interval')
time_unit  = st.sidebar.selectbox('Time unit:',('month','week','day','hour'))
time_value = st.sidebar.number_input('Number of '+time_unit+"s:", min_value=1, max_value=12, value=1, step=1)

time_bucket =  str(time_value) +" "+ time_unit
if time_value > 1:
    time_bucket = time_bucket + "s"


def get_sma_parameters(time_unit,label, default_days=20):
    sma_days = st.sidebar.number_input(f"Select the number of {time_unit}s for {label} SMA", 1, 100, default_days)
    return sma_days

def get_indicators_choice(time_unit):
    st.sidebar.header("SMA Indicators")
    sma_n1 = get_sma_parameters(time_unit,"1st", 10)
    sma_n2 = get_sma_parameters(time_unit,"2nd", 20)
    sma_n3 = get_sma_parameters(time_unit,"3rd", 100)
    return sma_n1, sma_n2, sma_n3

sma_n1, sma_n2, sma_n3= get_indicators_choice(time_unit)


# Present page results
st.write('## Price and volume of ', selected_symbol)
st.write('### ', time_bucket,"intervals")

query = query_and_plot_price_vol(selected_symbol,startDate,endDate, time_bucket, sma_n1, sma_n2, sma_n3)

with st.expander("See query used to get the data for the plot above"):
    st.code(query, language='sql')
