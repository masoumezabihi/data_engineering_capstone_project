import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from Logger import Logger  

class Loader:
    def __init__(self, username, password, host, port, database):
        """
        Initializes the Loader class with PostgreSQL connection details.
        
        Parameters:
            username (str): PostgreSQL username
            password (str): PostgreSQL password
            host (str): Host where PostgreSQL is running
            port (int): Port PostgreSQL is listening on
            database (str): Database name
        """
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.engine = self.get_engine()

    def get_engine(self):
        """
        Creates and returns a SQLAlchemy engine for PostgreSQL.
        
        Returns:
            sqlalchemy.Engine: SQLAlchemy engine object
        """
        connection_string = f"postgresql+psycopg2://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        try:
            engine = create_engine(connection_string)
            Logger.log(f"Successfully created SQLAlchemy engine for database: {self.database}")
            return engine
        except SQLAlchemyError as e:
            Logger.log(f"Error creating engine: {e}")
            return None

    def write_table(self, df, table_name, dtype=None):
        """
        Writes a pandas DataFrame to a PostgreSQL table using SQLAlchemy engine.

        Parameters:
            df (pd.DataFrame): Data to write
            table_name (str): Target table name
            dtype (dict, optional): Column-specific types, e.g., {"openfda": JSONB}
            
        Behavior:
            - Replaces the table if it already exists
            - Logs success/failure message
        """
        if self.engine is None:
            Logger.log("No engine found. Cannot write to the database.")
            return
        
        try:
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists='replace', 
                index=False,
                dtype=dtype
            )
            Logger.log(f"Successfully wrote table '{table_name}' with {len(df)} rows.")
        except Exception as e:
            Logger.log(f"Failed to write table '{table_name}': {e}")
