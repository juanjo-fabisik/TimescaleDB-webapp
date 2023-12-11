This project employs a static dataset of cryptocurrency prices, and to enhance scalability for real-time processing, two key functionalities of TimescaleDB prove instrumental: continuous aggregates and data compression.

### Continuous Aggregates in Real-Time Price Analysis

Real-time price data is commonly acquired on a second-by-second basis, necessitating the efficient aggregation into various time intervals such as minutes, hours, and days. Continuous aggregates, as a form of hypertable, prove invaluable in this context, automatically refreshing in the background as new data is added.

Unlike traditional PostgreSQL materialized views, the maintenance of continuous aggregates imposes a significantly lower burden. This is attributed to the incremental and continuous updates that occur in the background, eliminating the need for manual intervention in refreshing the aggregates.
Given their foundation on hypertables, querying continuous aggregates mirrors the process of querying other tables.

### Hierarchical Continuous Aggregates for Granular Data Summarization

Introducing the concept of hierarchical continuous aggregates allows for the creation of aggregations at varying levels of granularity. For instance, one may establish an hourly continuous aggregate to summarize minute-by-minute data. Then, a new continuous aggregate can be created on top of the hourly aggregate to obtain a daily summary. This approach is more efficient than creating a daily aggregate directly on the original hypertable, as it leverages the calculations already performed in the hourly aggregate.

### Compression for Efficient Storage and Query Speed

When working with real time financial data, the storage requirements grows continuously. Data storage considerations become important.
Timescale has the ability to compress time-series data, minimizing storage requirements and accelerating certain queries. As new uncompressed data is added to the database, Timescale utilizes a built-in job scheduler to convert this data into compressed columns. This compression process is executed across chunks of Timescale hypertables, ensuring a streamlined and resource-efficient management of time-series data.
