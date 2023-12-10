import psycopg2
import config 
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


connection = psycopg2.connect(database=config.DB_NAME, 
                            host=config.DB_HOST, 
                            user=config.DB_USER, 
                            password=config.DB_PASS, 
                            port=config.DB_PORT)

# Don't create a transaction by setting isolation level to ISOLATION_LEVEL_AUTOCOMMIT
# required to run continuous aggregation with psycopg2
connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

# create continuous aggregates for day, week and month time intervals.
sql_script_day = """
create materialized view dataset_by_day
with (timescaledb.continuous) as
select
	symbol,
	time_bucket('1 day', "time_hour") AS time_day,
	sum(trading_volume) AS trading_volume, 
	FIRST(price_open, time_hour) AS price_open, 
    LAST(price_close, time_hour) AS price_close,
    MAX(price_high) AS price_high,
    MIN(price_low) AS price_low
 FROM dataset_by_hour
 group by time_day, symbol;
"""
sql_script_week = """
create materialized view dataset_by_week
with (timescaledb.continuous) as
select
	symbol,
	time_bucket('1 week', "time_day") AS time_week,
	sum(trading_volume) AS trading_volume, 
	FIRST(price_open, time_day) AS price_open, 
    LAST(price_close, time_day) AS price_close,
    MAX(price_high) AS price_high,
    MIN(price_low) AS price_low
 FROM dataset_by_day
 group by time_week, symbol;
"""
sql_script_month = """
create materialized view dataset_by_month
with (timescaledb.continuous) as
select
	symbol,
	time_bucket('1 month', "time_day") AS time_month,
	sum(trading_volume) AS trading_volume, 
	FIRST(price_open, time_day) AS price_open, 
    LAST(price_close, time_day) AS price_close,
    MAX(price_high) AS price_high,
    MIN(price_low) AS price_low
 FROM dataset_by_day
 group by time_month, symbol;

"""


try:
    # Create a cursor object
    cursor = connection.cursor()

    # Execute the SQL script
    cursor.execute(sql_script_day)
    cursor.execute(sql_script_week)
    cursor.execute(sql_script_month)
    # Commit the changes
    connection.commit()

finally:
    # Close the cursor and connection
    cursor.close()
    connection.close()
