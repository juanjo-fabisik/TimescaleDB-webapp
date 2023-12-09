import streamlit as st


st.set_page_config(page_title="Price summary", page_icon=":bar_chart:",layout="wide")
# Initialize connection.
conn = st.connection("postgresql", type="sql")

table_name = "crypto_database4"
def query_price_change(table_name,price_change_option):
    query_p1 = """
      -- Common Table Expression (CTE) to calculate the maximum timestamp in the dataset
      WITH max_time AS (
          SELECT MAX(time) AS max_timestamp
          FROM {table_name}
      )
      -- Main query: calculate price change percentages for for each symbold and different time intervals
      SELECT
          symbol,
          LAST(price_close, time) AS price,
           """.format(table_name=table_name)
    query_p2 = ""
    for price_change in price_change_option:
        query_p2 = query_p2 + """
        ((LAST(price_close, time) / FIRST(price_open, time) FILTER (WHERE time >= max_timestamp - INTERVAL '{time_bucket}'))-1) * 100 AS _{column_id},
        """.format(time_bucket=price_change, column_id=price_change.replace(" ","_"))
    query_p3 = """
      FROM
          {table_name}, max_time
      GROUP BY
          symbol;
    """.format(table_name=table_name)

    query = query_p1 + query_p2[:-10]+"\n" + query_p3

    df = conn.query(query, ttl="10m")
    df.rename(columns=lambda c: c.replace('_',' ').strip(), inplace=True)
    return df, query

def query_price_chart(table_name,chart_option):
    if chart_option=='Last 24 hours':
       time_interval = "24 hours"
       time_bucket = "1 hours"
    elif chart_option=='Last 7 days':
       time_interval = "7 days"
       time_bucket = "2 hours"
    elif chart_option=='Last month':
       time_interval = "1 month"
       time_bucket = "8 hours"
    elif chart_option=='Last quarter':
       time_interval = "3 month"
       time_bucket = "1 day"
    elif chart_option=='Last year':
       time_interval = "1 year"
       time_bucket = "4 day"

    query = """
    -- Common Table Expression (CTE) to calculate the maximum timestamp in the dataset
    WITH max_time AS (
        SELECT MAX(time) AS max_timestamp
        FROM {table_name}
    )
    -- Main query to retrieve symbol, bucket start time, and last close price
    SELECT
        symbol,
        TIME_BUCKET('{time_bucket}'::interval, time) AS bucket_start_time,
        LAST(price_close, time) AS last_close_price
    FROM
        {table_name}, max_time
    WHERE
        -- Filter data for the last {time_interval} from the maximum timestamp
        time >= max_timestamp - INTERVAL '{time_interval}'
    GROUP BY
        symbol,
        bucket_start_time
    ORDER BY
        symbol,
        bucket_start_time;
        """.format(table_name=table_name,time_bucket=time_bucket, time_interval=time_interval); 
    # Perform query.
    df = conn.query(query, ttl="10m")
    return df, query



# Choose table options
st.sidebar.title("Customize table")
price_change_option = st.sidebar.multiselect(
    'Price change',
    ['1 hour', '24 hour', '7 days', '30 days', '90 days', '1 year'],
    ['1 hour', '24 hour', '7 days'])
chart_option = st.sidebar.selectbox(
    'Chart',
    ('Last 7 days', 'Last month', 'Last quarter', 'Last year'))


# query the database
df1, query1 = query_price_change(table_name,price_change_option)
# choose columns to apply color scheme
colored_columns = df1.columns.values[2:]
df2, query2 = query_price_chart(table_name,chart_option)

#New column for chart line
df1[chart_option] = None
# Define a function to create a new column with the list of values
def create_new_column(row, symbol, price_list):
    if row["symbol"] == symbol:
        return price_list
    else:
      return row[chart_option] 
# add char line data to main table
for symbol in df2["symbol"].unique():

    price_lastweek = df2[df2["symbol"]==symbol]["last_close_price"].values
    # normalize prices to 100 to better chart line
    price_ini = price_lastweek[0]
    normalized_price_lastweek = [(x / price_ini) * 100 for x in price_lastweek]
    # Apply the function to create the new column
    df1[chart_option] = df1.apply(lambda row: create_new_column(row, symbol, normalized_price_lastweek), axis=1)
    

st.write("## Price change [%]")
# set red or green background depending on price change
def color_cell(val):
    color = '#751010' if float(val)<=0.00 else '#135518'
    return f'background-color: {color}'


st.dataframe(df1.style.applymap(color_cell, subset=colored_columns), hide_index=True,
    column_config={chart_option: st.column_config.LineChartColumn(width="medium"),}, use_container_width=False )

with st.expander("See query used to get the price changes"):
  st.code(query1, language='sql')

with st.expander("See query used to make the "+chart_option.lower()+" chart"):
  st.code(query2, language='sql')