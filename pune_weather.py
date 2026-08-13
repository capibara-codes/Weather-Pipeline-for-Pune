import os
import sqlite3
import datetime
import logging
import requests
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Logging
logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Fetch location coordinates and configs from .env
LATITUDE = float(os.getenv("LATITUDE", 18.5204))
LONGITUDE = float(os.getenv("LONGITUDE", 73.8567))
CITY_NAME = os.getenv("CITY_NAME", "Pune")
DB_NAME = os.getenv("DB_NAME", "pune_weather.db")

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def init_db():
    """Initialize SQLite database table and indices."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
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
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON weather_logs(timestamp);")
        conn.commit()


def extract_weather_data():
    """Fetch current weather metrics from Open-Meteo API for Pune."""
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m",
            "rain"
        ],
        "timezone": "Asia/Kolkata"
    }
    
    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        logging.info("Successfully fetched data from Open-Meteo API.")
        return response.json().get("current", {})
    except requests.RequestException as e:
        logging.error(f"Failed to extract weather data: {e}")
        return None


def transform_data(raw_data):
    """Transform raw JSON response into a structured Pandas DataFrame."""
    if not raw_data:
        return None

    try:
        record = {
            "city": CITY_NAME,
            "timestamp": raw_data.get("time"),
            "temperature_c": raw_data.get("temperature_2m"),
            "humidity_percent": raw_data.get("relative_humidity_2m"),
            "wind_speed_kmh": raw_data.get("wind_speed_10m"),
            "rain_mm": raw_data.get("rain", 0.0),
        }

        df = pd.DataFrame([record])
        return df
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        return None


def load_to_sqlite(df):
    """Load transformed DataFrame into SQLite database."""
    if df is None or df.empty:
        logging.warning("No data to load.")
        return

    try:
        with sqlite3.connect(DB_NAME) as conn:
            df.to_sql("weather_logs", conn, if_exists="append", index=False)
            logging.info(f"Successfully loaded {len(df)} row(s) into database.")
            print(f"✅ Weather data for {CITY_NAME} saved successfully at {df['timestamp'].iloc[0]}")
    except sqlite3.Error as e:
        logging.error(f"Database insertion failed: {e}")


def run_pipeline():
    """Main execution orchestrator."""
    init_db()
    raw_data = extract_weather_data()
    transformed_df = transform_data(raw_data)
    load_to_sqlite(transformed_df)


if __name__ == "__main__":
    run_pipeline()