# TimescaleDB for Financial Time Series Analysis and Database Management

### Initialization of TimescaleDB database

1. Install and configure PostgreSQL and TimescaleDB on your server.
2. Create a virtual environment and install required Python packages from `requirements.txt`:
   ```
   virtualenv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Write your database connection details in the file `database/config.py`
4. Create Table, Hypertable, and Indexing by running the Python script `init_timescaledb.py` in the `database` directory:
   ```
   python database/init_timescaledb.py
   ```
5. Ingest Dataset into the server by running the Python script `data_ingestion.py` in the `database` directory:
   ```
   python database/data_ingestion.py
   ```
   The dataset is expected to be in `database/raw/trades.csv`

### Data analysis

1. Streamlit expects the database connection details to be located in `.streamlit/secrets.toml`

2. To lunch the web application, execute the following line:

   ```
   streamlit run analytics/Home.py
   ```
