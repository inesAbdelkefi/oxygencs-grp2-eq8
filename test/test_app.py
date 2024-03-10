"""
This file tests the functionnalities of the app in main.py (found in src/main.py)
"""
import json
import unittest
from unittest.mock import MagicMock, patch
from src.main import App

class TestApp(unittest.TestCase):
    """
    Test cases for the App class.
    """

    @patch("signalrcore.hub_connection_builder.HubConnectionBuilder.build")
    def test_setup_sensor_hub(self, mock_build):
        """
        Test that makes sure the environment the connection to the hvac app works
        This method tests the setup_sensor_hub method in main
        """
        app = App()
        app.setup_sensor_hub()

        mock_build.assert_called_once()
        self.assertIsNotNone(app._hub_connection.on)
        self.assertIsNotNone(app._hub_connection.on_open)
        self.assertIsNotNone(app._hub_connection.on_close)
        self.assertIsNotNone(app._hub_connection.on_error)

    def test_on_sensor_data_received(self):
        """
        This method tests what the program does on temperature data received from
        the app

        This method tests the function on_sensor_data_received
        """
        app = App()
        app.setup_sensor_hub()

        data = [{"date": "2024-02-25", "data": "25.5"}]

        with patch.object(app, "take_action") as mock_take_action, \
             patch.object(app, "save_sensor_to_database") as mock_save_event:
            app.on_sensor_data_received(data)

        mock_take_action.assert_called_once_with(25.5,"2024-02-25")
        mock_save_event.assert_called_once_with("2024-02-25", 25.5)

    @patch("requests.get")
    def test_send_turn_on_ac_to_hvac(self, mock_get):
        """
        This test makes sure that the turn on ac action is called when the temp
        too high

        this method tests send_action_to_hvac method
        """
        response_mock = MagicMock()
        response_mock.text = '{"Response": "Activating AC for 10 ticks"}'

        mock_get.return_value = response_mock

        app = App()
        app.send_action_to_hvac("TurnOnAc")

        mock_get.assert_called_once()

        expected_url = "http://159.203.50.162/api/hvac/d6e33ac9ad141a18af77/TurnOnAc/10"
        mock_get.assert_called_once_with(expected_url)

        # Additional assertion: Check if json.loads is called with the correct argument
        details = json.loads(response_mock.text)
        self.assertEqual(details, {"Response": "Activating AC for 10 ticks"})

    @patch("requests.get")
    def test_send_turn_on_heater_to_hvac(self, mock_get):
        """
        This test makes sure that the turn on heater action is called when the temp
        too low

        this method tests send_action_to_hvac method
        """
        response_mock = MagicMock()
        response_mock.text = '{"Response": "Activating Heater for 10 ticks"}'

        mock_get.return_value = response_mock

        app = App()
        app.send_action_to_hvac("TurnOnHeater")

        mock_get.assert_called_once()

        expected_url = "http://159.203.50.162/api/hvac/d6e33ac9ad141a18af77/TurnOnHeater/10"
        mock_get.assert_called_once_with(expected_url)

        details = json.loads(response_mock.text)
        self.assertEqual(details, {"Response": "Activating Heater for 10 ticks"})

    @patch("requests.get")
    def test_send_turn_off_hvac_to_hvac(self, mock_get):
        """
        This test makes sure that the turn off hvac action is called when the temp
        is ideal.

        this method tests send_action_to_hvac method
        """
        response_mock = MagicMock()
        response_mock.text = '{"Response": "Turning off Hvac"}'

        mock_get.return_value = response_mock

        app = App()
        app.send_action_to_hvac("TurnOffHvac")

        mock_get.assert_called_once()

        expected_url = "http://159.203.50.162/api/hvac/d6e33ac9ad141a18af77/TurnOffHvac"
        mock_get.assert_called_once_with(expected_url)

        # Additional assertion: Check if json.loads is called with the correct argument
        details = json.loads(response_mock.text)
        self.assertEqual(details, {"Response": "Turning off Hvac"})

    def test_determine_hvac_action(self):
        """
        This method tests if the right action is chosen under the given temperature

        this method tests determine_hvac_action
        """
        app = App()

        action = app.determine_hvac_action(35)
        self.assertEqual(action, "TurnOnAc")
        action = app.determine_hvac_action(9)
        self.assertEqual(action, "TurnOnHeater")
        action = app.determine_hvac_action(15)
        self.assertEqual(action, "TurnOffHvac")

    @patch("psycopg2.connect")
    def test_connect_to_bd(self, mock_connect):
        """
        Test the connect_to_bd method.

        This method tests the functionality of the connect_to_bd method in the App class.
        It verifies that the method properly connects to the database.
        """
        mock_connection = MagicMock()
        mock_connect.return_value = mock_connection

        app = App()

        mock_db_url = MagicMock()
        mock_db_url.username = 'user'
        mock_db_url.password = 'password'
        mock_db_url.hostname = 'hostname'
        mock_db_url.port = '5432'
        mock_db_url.path = '/database'

        conn = app.connect_to_BD(mock_db_url)

        mock_connect.assert_called_once_with(
            user='user',
            password='password',
            host='hostname',
            port='5432',
            database='database'
        )
        self.assertEqual(conn, mock_connection)

    def test_create_db_tables(self):
        """
        Test the create tables in database.

        This method tests the functionality of createDB_OxygenCS() method in the App class.
        It verifies that it properly creates tables
        """
        # Mock the connection and cursor
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor


        # Initialize an instance of App
        app = App()
        app.conn = mock_conn
        app.cursor = mock_cursor

        # Call the method
        app.createDB_OxygenCS()

        # Define the expected SQL commands
        expected_sql_commands = [
            'CREATE TABLE IF NOT EXISTS sensor_data (id SERIAL PRIMARY KEY,'+
            'timestamp TIMESTAMP,temperature DOUBLE PRECISION)',
            'CREATE TABLE IF NOT EXISTS hvac_events (id SERIAL PRIMARY KEY,'+
            'timestamp TIMESTAMP,action VARCHAR(255))'
        ]

        normalized_actual_calls = []
        # Iterate through each call argument in the call_args_list
        for call_args in mock_cursor.execute.call_args_list:
            # Extract the SQL command from the call arguments
            sql_command = call_args[0][0]

            # Strip leading and trailing whitespaces
            sql_command = sql_command.strip()

            # Remove newline characters
            sql_command = sql_command.replace('\n', '')

            # Replace multiple spaces with a single space
            sql_command = sql_command.replace('  ', ' ')

            # Replace sequences of spaces with a single space
            sql_command = sql_command.replace('          ', '')
            sql_command = sql_command.replace('        ', '')

            # Add the normalized SQL command to the list
            normalized_actual_calls.append(sql_command)

        # Assert that the cursor's execute method was called with expected SQL commands
        self.assertCountEqual(normalized_actual_calls, expected_sql_commands)

        # Assert that commit was called on the connection
        mock_conn.commit.assert_called_once()

    def test_save_sensor_to_database(self):
        """
        Test recording sensor data in db.

        This method tests the functionality of save_sensor_to_database method in the App class.
        It verifies that it properly sends the right sql argument ro record sensor data in the
        database.
        """
        # Mock the connection and cursor
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor


        # Initialize an instance of App
        app = App()
        app.conn = mock_conn
        app.cursor = mock_cursor

        # Call the method
        timestamp = '2024-03-09'
        temperature = 25.5
        app.save_sensor_to_database(timestamp, temperature)

        # Define the expected SQL command
        expected_sql_command = "INSERT INTO sensor_data (timestamp, temperature) VALUES (%s, %s);"
        expected_call_args = (timestamp, temperature)

        # Assert that the cursor's execute method was called with expected SQL command and arguments
        mock_cursor.execute.assert_called_once_with(expected_sql_command, expected_call_args)

        # Assert that commit was called on the connection
        mock_conn.commit.assert_called_once()

    def test_save_event_to_database(self):
        """
        Test recording event data in db.

        This method tests the functionality of save_event_to_database method in the App class.
        It verifies that it properly sends the right sql argument ro record sensor data in the
        database.
        """
        # Mock the connection and cursor
        mock_cursor = MagicMock()
        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor


        # Initialize an instance of App
        app = App()
        app.conn = mock_conn
        app.cursor = mock_cursor

        # Call the method
        timestamp = '2024-03-09'
        action = "TurnOnHeater"
        app.save_event_to_database(timestamp, action)

        # Define the expected SQL command
        expected_sql_command = "INSERT INTO hvac_events (timestamp, action) VALUES (%s, %s);"
        expected_call_args = (timestamp, action)

        # Assert that the cursor's execute method was called with expected SQL command and arguments
        mock_cursor.execute.assert_called_once_with(expected_sql_command, expected_call_args)

        # Assert that commit was called on the connection
        mock_conn.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
