import os
from signalrcore.hub_connection_builder import HubConnectionBuilder
from dotenv import load_dotenv
import logging
import requests
import json
import time
import psycopg2
from urllib.parse import urlparse

load_dotenv()

class App:
    def __init__(self):
        self._hub_connection = None
        self.TICKS = 10
        self.numberTicks = 0
        self.idealTemp = False
        self.idealTempChange = False

        # To be configured by your team
        self.HOST = os.getenv("HOST")  # Utilize environment variable for HOST
        self.TOKEN = os.getenv("TOKEN")  # Utilize environment variable for TOKEN
        self.T_MAX = float(os.getenv("T_MAX"))  # Utilize environment variable for T_MAX
        self.T_MIN = float(os.getenv("T_MIN"))  # Utilize environment variable for T_MIN
        self.DATABASE_URL = os.getenv("DATABASE_URL")  # Utilize environment variable for DATABASE_URL

    def __del__(self):
        if self._hub_connection != None:
            self.cursor.close()
            self.conn.close()
            self._hub_connection.stop()


    def start(self):
        """Start Oxygen CS."""
        self.setup_sensor_hub()
        self._hub_connection.start()
        db_url = urlparse(self.DATABASE_URL)
        self.conn = self.connect_to_BD(db_url)
        self.cursor = self.conn.cursor()
        self.createDB_OxygenCS()

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
        print(data[0]["date"] + " --> " + data[0]["data"], flush=True)
        timestamp = data[0]["date"]
        temperature = float(data[0]["data"])
        try:
            self.take_action(temperature, timestamp)
        except Exception as err:
            print(err)
        try:
            self.save_sensor_to_database(timestamp, temperature)
        except Exception as err:
            print(err)

    def take_action(self, temperature, timestamp):
        """Take action to HVAC depending on current temperature."""
        action = self.determine_hvac_action(temperature)
        if self.idealTemp == False and self.numberTicks == 0:
            self.send_action_to_hvac(action)
            self.idealTempChange = True
            try:
                self.save_event_to_database(timestamp, action)
            except Exception as err:
                print(err)       
        elif self.idealTemp == True and self.idealTempChange == True:
            self.idealTempChange = False
            self.send_action_to_hvac(action)
            try:
                self.save_event_to_database(timestamp, action)
            except Exception as err:
                print(err)    
            
        
        if self.numberTicks == self.TICKS or self.idealTemp == True:
            self.numberTicks = 0
        else:
            self.numberTicks +=1

    def send_action_to_hvac(self, action):
        """Send action query to the HVAC service."""
        if action == "TurnOnAc" or action == "TurnOnHeater":
            r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}/{self.TICKS}")
            details = json.loads(r.text)
            print(details, flush=True)
        elif action == "TurnOffHvac":
            r = requests.get(f"{self.HOST}/api/hvac/{self.TOKEN}/{action}")
            details = json.loads(r.text)
            print(details, flush=True)
    
    def determine_hvac_action(self, temperature):
        if float(temperature) > float(self.T_MAX):
            self.idealTemp = False
            return "TurnOnAc"
        elif float(temperature) < float(self.T_MIN):
            self.idealTemp = False
            return "TurnOnHeater"
        else:
            self.idealTemp = True
            return "TurnOffHvac"
    
    def connect_to_BD(self, db_url):
        try:
            connectionDB = psycopg2.connect(
                user=db_url.username,
                password=db_url.password,
                host=db_url.hostname,
                port=db_url.port,
                database=db_url.path[1:]
            )
            return connectionDB
        except requests.exceptions.RequestException as e:
            print(f"Error saving to database: {e}")

    def createDB_OxygenCS(self):
        """Create the tables for storing sensor and event data"""
        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP,
                    temperature DOUBLE PRECISION
                )
            """)

            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS hvac_events (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP,
                    action VARCHAR(255)
                )
            """)
            self.conn.commit()
            print("Tables created")
        except Exception as e:
            print(f"Error saving to database: {e}")
            

    def save_sensor_to_database(self, timestamp, temperature):
        """Save sensor data into database."""
        try:
            sensor_data_query = "INSERT INTO sensor_data (timestamp, temperature) VALUES (%s, %s);"
            self.cursor.execute(sensor_data_query, (timestamp, temperature))
            self.conn.commit()
        except psycopg2.Error as e:
            print(f"Error saving sensor data to database: {e}")
        

    def save_event_to_database(self, timestamp, hvac_action):
        """Save event data into database."""
        try:
            hvac_event_query = "INSERT INTO hvac_events (timestamp, action) VALUES (%s, %s);"
            self.cursor.execute(hvac_event_query, (timestamp, hvac_action))
            self.conn.commit()
        except psycopg2.Error as e:
            print(f"Error saving HVAC event to database: {e}")
        
            

if __name__ == "__main__":

    app = App()
    app.start()
