from signalrcore.hub_connection_builder import HubConnectionBuilder
import logging
import requests
import json
import time
import os
import psycopg2
from urllib.parse import urlparse

class App:
    def __init__(self):
        self._hub_connection = None
        self.TICKS = 10

        # To be configured by your team
        self.HOST = os.getenv("HOST")  # Utilize environment variable for HOST
        self.TOKEN = os.getenv("TOKEN")  # Utilize environment variable for TOKEN
        self.T_MAX = float(os.getenv("T_MAX"))  # Utilize environment variable for T_MAX
        self.T_MIN = float(os.getenv("T_MIN"))  # Utilize environment variable for T_MIN
        self.DATABASE_URL = os.getenv("DATABASE_URL")  # Utilize environment variable for DATABASE_URL

    def __del__(self):
        if self._hub_connection != None:
            self._hub_connection.stop()

    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        print("Press CTRL+C to exit.")
        while True:
            time.sleep(2)

    def setup_sensor_hub(self):
        """Configure hub connection and subscribe to sensor data events."""
        self._hub_connection = (
            HubConnectionBuilder()
            .with_url(f"{self.HOST}/SensorHub?token={self.TOKEN}")
            .configure_logging(logging.INFO)
            .with_automatic_reconnect(
                {
                    "type": "raw",
                    "keep_alive_interval": 10,
                    "reconnect_interval": 5,
                    "max_attempts": 999,
                }
            )
            .build()
        )
        self._hub_connection.on("ReceiveSensorData", self.on_sensor_data_received)
        self._hub_connection.on_open(lambda: print("||| Connection opened."))
        self._hub_connection.on_close(lambda: print("||| Connection closed."))
        self._hub_connection.on_error(
            lambda data: print(f"||| An exception was thrown closed: {data.error}")
        )

    def on_sensor_data_received(self, data):
        """Callback method to handle sensor data on reception."""
        try:
            print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
            timestamp = data[0]["date"]
            temperature = float(data[0]["data"])
            self.take_action(temperature)
            self.save_event_to_database(timestamp, temperature)
        except Exception as err:
            print(err)

    def take_action(self, temperature):
        """Take action to HVAC depending on current temperature."""
        if float(temperature) >= float(self.T_MAX):
            self.send_action_to_hvac("TurnOnAc")
        elif float(temperature) <= float(self.T_MIN):
            self.send_action_to_hvac("TurnOnHeater")

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{self.TICKS}")
        details = json.loads(r.text)
        print(details, flush=True)

    def save_event_to_database(self, timestamp, temperature):
        """Save sensor data into database."""
        try:
            # Parse the database URL
            db_url = urlparse(self.DATABASE_URL)

            conn = psycopg2.connect(
                user=db_url.username,
                password=db_url.password,
                host=db_url.hostname,
                port=db_url.port,
                database=db_url.path[1:]
            )

            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP,
                    temperature DOUBLE PRECISION
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hvac_events (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP,
                    action VARCHAR(255)
                )
            """)

            conn.commit()

            # Save sensor data
            sensor_data_query = "INSERT INTO sensor_data (timestamp, temperature) VALUES (%s, %s);"
            cursor.execute(sensor_data_query, (timestamp, temperature))

            # Save HVAC event
            hvac_action = self.determine_hvac_action(temperature)
            hvac_event_query = "INSERT INTO hvac_events (timestamp, action) VALUES (%s, %s);"
            cursor.execute(hvac_event_query, (timestamp, hvac_action))

            conn.commit()
        except Exception as e:
            print(f"Error saving to database: {e}")
        finally:
            cursor.close()
            conn.close()

    def determine_hvac_action(self, temperature):
        if float(temperature) >= float(self.T_MAX):
            return "TurnOnAc"
        elif float(temperature) <= float(self.T_MIN):
            return "TurnOnHeater"


if __name__ == "__main__":
    app = App()
    app.start()
