#   Pune Weather Pipeline
This is project is build to engireed an end to end weather analytics ETL pipeline using python, Pandas and SQLite targeting real time meteorological metrics for Pune district.
The core goal was to build a reliable data ingestion and transformation workflow that extracts live metrics like temperature, humidity, wind speed, and rain from the Open-Meteo REST API. 
I designed the transformation layer using Pandas to handle schema enforcement, data type validation, and missing value handling before loading the records into a relational database and implemented an indexed time-series schema in SQLite to optimize analytical range queries.

## Key Technical Features

* **Zero-Key REST Ingestion:** Fetches live weather metrics (`temperature`, `relative_humidity`, `wind_speed`, `rain`) for Pune District (`18.5204° N, 73.8567° E`).
* **Environment Isolation & Security:** Utilizes `python-dotenv` and `.env` files to keep local environment parameters separated from source control.
* **Data Cleansing & Normalization:** Converts nested API JSON responses into strongly-typed Pandas DataFrames with standardized schema naming.
* **Reliable Connection Management:** Leverages Python context managers (`with sqlite3.connect()`) to guarantee database transaction safety and connection handling.
* **Time-Series Query Optimization:** Creates automated database indices on timestamp attributes (`idx_timestamp`) to optimize fast range queries.
* **Structured Execution Logging:** Captures pipeline runs, row insertion counts, and connection exceptions to `pipeline.log`.

---

# Tech Stack & Tools

* **Language:** Python 3.10+
* **Data Processing & Transformation:** Pandas, NumPy
* **Storage Engine:** SQLite3 (SQL)
* **Configuration & Security:** `python-dotenv`
* **API Ingestion:** Requests Library
* **Developer Environment:** VS Code (SQLite Viewer Extension), Virtual Environment (`venv`), Git

---

# Database Schema & DDL

The database automatically initializes the following relational table and index structure upon the first run:


```sql
CREATE TABLE IF NOT EXISTS weather_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    temperature_c REAL,
    humidity_percent REAL,
    wind_speed_kmh REAL,
    rain_mm REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

```
-- Index created to speed up time-series range queries
CREATE INDEX IF NOT EXISTS idx_timestamp ON weather_logs(timestamp);

## Clone repository
git clone [clone](https://github.com/capibara-codes/Weather-Pipeline-for-Pune.git)
cd pune-weather-pipeline

## To install required tech and libraries
pip install -r requirements.txt

## Run the Pipeline
python weather_pipeline.py

## Roadmap and Future Upgrades
*[ ] Add Air Quality Index (AQI) and UV Index tracking metrics from Open-Meteo.
*[ ] Migrate storage backend from local SQLite to PostgreSQL.
*[ ] Implement unit testing suite using pytest for data transformation routines.
*[ ] Schedule automated hourly runs using Linux cron / Windows Task Scheduler.
