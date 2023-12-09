import streamlit as st
import plotly.express as px
import datetime

st.set_page_config(page_title="Volume Comparison", page_icon=":bar_chart:",layout="wide")
# Initialize connection.
conn = st.connection("postgresql", type="sql")

table_name = "crypto_database4"
# Define functions to make the queries and plot the results
def query_and_plot_vol(table_name,startDate,endDate, time_bucket):
    import plotly.graph_objects as go
    query = """
    -- Selects and aggregates data into {bucket} buckets for a specific time range
      SELECT
        -- Compute {bucket} time bucket for each row's timestamp
        time_bucket('{bucket}', time) AS bucket,
        symbol,
        -- Sum the trading volume within each {bucket} bucket for each symbol
        sum(trading_volume) AS volume
      FROM
        {table_name}
      WHERE
        time BETWEEN '{start_date}' AND '{end_date}'
      GROUP BY
        -- Group the result by both time bucket and symbol
        bucket, symbol;
    """.format(table_name=table_name,bucket=time_bucket, start_date=startDate, end_date=endDate,); 
 
    # Perform query.
    df = conn.query(query, ttl="10m")

    fig = px.bar(df, x="bucket", y="volume", color="symbol",
            hover_data=['volume'], barmode = 'stack',  ).update_layout(xaxis_title="Date", yaxis_title="Total Volume")
    st.plotly_chart(fig, use_container_width=True)
    return query

def query_and_plot_max_min_vol(table_name,startDate,endDate, order):
    query = """
      SELECT
        symbol,
        SUM(trading_volume) AS total_volume
      FROM
        {table_name}
      WHERE
        time BETWEEN '{start_date}' AND '{end_date}'
      GROUP BY
        symbol
      ORDER BY
        total_volume {order}
      LIMIT 10;
    """.format(table_name=table_name,start_date=startDate, end_date=endDate,order=order); 
 
    # Perform query.
    df = conn.query(query, ttl="10m")

    fig = px.bar(df, x="symbol", y="total_volume").update_layout(xaxis_title="Date", yaxis_title="Total Volume")
    st.plotly_chart(fig, use_container_width=True)

    return query


# Choose chart options
st.sidebar.title("Choose chart options")
st.sidebar.write('### Define date range')
startDate = st.sidebar.date_input("Start date:", datetime.date(2019, 9, 8))
endDate   = st.sidebar.date_input("End date:",   datetime.date(2023, 10, 6))

st.sidebar.write('### Define time interval')
time_unit  = st.sidebar.selectbox('Time unit:',('month','week','day','hour'))
time_value = st.sidebar.number_input('Number of '+time_unit+"s:", min_value=1, max_value=12, value=3, step=1)

time_bucket =  str(time_value) +" "+ time_unit
if time_value > 1:
    time_bucket = time_bucket + "s"


# write page contents
st.write("## Traded volume for all pairs between {start_date} and {end_date}".format(start_date=startDate, end_date=endDate))
st.write('## ', time_bucket,"intervals")

query1 = query_and_plot_vol(table_name,startDate,endDate, time_bucket)
with st.expander("See query used to get the data for the plot above"):
  st.code(query1, language='sql')

st.write("## Pairs with the most trading volume between {start_date} and {end_date}".format(start_date=startDate, end_date=endDate))
query2 = query_and_plot_max_min_vol(table_name,startDate,endDate,"DESC")
with st.expander("See query used to get the data for the plot above"):
  st.code(query2, language='sql')

st.write("## Pairs with the least trading volume between {start_date} and {end_date}".format(start_date=startDate, end_date=endDate))
query3 = query_and_plot_max_min_vol(table_name,startDate,endDate,"ASC")
with st.expander("See query used to get the data for the plot above"):
  st.code(query3, language='sql')



