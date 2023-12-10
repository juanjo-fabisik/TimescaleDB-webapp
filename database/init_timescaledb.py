import psycopg2
import config 


connection = psycopg2.connect(database=config.DB_NAME, 
                            host=config.DB_HOST, 
                            user=config.DB_USER, 
                            password=config.DB_PASS, 
                            port=config.DB_PORT)

table_name = "dataset_by_hour"

# SQL script
sql_script = """
BEGIN;

CREATE TABLE public.{table_name} (
    "time_hour" timestamp(0) NOT NULL,
    symbol varchar NULL,
    price_open float8 NULL,
    price_close float8 NULL,
    price_low float8 NULL,
    price_high float8 NULL,
    trading_volume float8 NULL
);

/* Enable the TimscaleDB extension */
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Time-based index
CREATE INDEX ON {table_name} (time_hour DESC);

-- symbol-based index
CREATE INDEX ON {table_name} (symbol, time_hour DESC);

/* 
Turn the  table into a hypertable.
This is important to be able to make use of TimescaleDB features later on.
*/

SELECT create_hypertable('{table_name}', 'time_hour');

COMMIT;
""".format(table_name=table_name)


try:
    # Create a cursor object
    cursor = connection.cursor()

    # Execute the SQL script
    cursor.execute(sql_script)

    # Commit the changes
    connection.commit()

finally:
    # Close the cursor and connection
    cursor.close()
    connection.close()
