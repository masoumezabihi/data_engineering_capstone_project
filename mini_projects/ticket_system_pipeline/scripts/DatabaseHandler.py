import mysql.connector
from Logger import Logger

class DatabaseHandler:
    def __init__(self, config):
        self._config = config
        self._connection = None

    def connect(self):
        if self._connection is None:
            try:
                self._connection = mysql.connector.connect(**self._config)
                Logger.log("Successfully connected to the database.", 'info')
            except mysql.connector.Error as err:
               Logger.log(f"Database connection failed: {err}", 'error')
               raise
        else:
            Logger.log("Connection already open. Close it before reconnecting.", 'warning')
            raise Exception("Connection already open. Close it before reconnecting.")

    def get_connection(self):
        if self._connection is None:
            try:
                self.connect()
            except Exception as e:
                Logger.log(f"Failed to get database connection: {e}", 'error')
                raise
        return self._connection


    def create_third_party_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS ticket_sales (
            ticket_id INT PRIMARY KEY,
            trans_date INT,
            event_id INT,
            event_name VARCHAR(50),
            event_date DATE,
            event_type VARCHAR(10),
            event_city VARCHAR(20),
            customer_id INT,
            price DECIMAL(10, 2),
            num_tickets INT
        );
        """
        try:
            cursor = self._connection.cursor()
            cursor.execute(query)
            self._connection.commit()
            cursor.close()
            Logger.log("Table 'ticket_sales' created or already exists.", 'info')
        except mysql.connector.Error as err:
            Logger.log(f"Failed to create table: {err}", 'error')
            raise

    def close(self):
        if self._connection:
            try:
                self._connection.close()
                Logger.log("Database connection closed.", 'info')
            except mysql.connector.Error as err:
                Logger.log(f"Error closing the connection: {err}", 'error')
                raise
