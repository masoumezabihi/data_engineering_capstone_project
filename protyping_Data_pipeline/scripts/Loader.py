import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from Logger import Logger 
from sqlalchemy import text 
from sqlalchemy import inspect

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


    def has_primary_key(self, table_name):
        inspector = inspect(self.engine)
        pk = inspector.get_pk_constraint(table_name)
        return bool(pk and pk.get('constrained_columns'))

    def has_foreign_key(self, table_name, fk_column):
        inspector = inspect(self.engine)
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            if fk_column in fk.get('constrained_columns', []):
                return True
        return False
    
    def ensure_columns_exist(self, table_name, df):
        inspector = inspect(self.engine)

        if table_name not in inspector.get_table_names():
            return

        existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
        missing_cols = [col for col in df.columns if col not in existing_columns]

        with self.engine.connect() as conn:
            for col in missing_cols:
                alter_sql = f'ALTER TABLE {table_name} ADD COLUMN "{col}" TEXT;'
                conn.execute(text(alter_sql))
                conn.commit()
                Logger.log(f"Added missing column '{col}' to table '{table_name}'.")

    def write_table(self, df, table_name, dtype=None, primary_key=None, foreign_key=None):
        """
        Writes a pandas DataFrame to a PostgreSQL table using SQLAlchemy engine.

        Parameters:
            df (pd.DataFrame): Data to write
            table_name (str): Target table name
            dtype (dict, optional): Column-specific types, e.g., {"openfda": JSONB}
            primary_key (str, optional): Column name to set as PRIMARY KEY
            foreign_key (dict, optional): Dictionary with keys:
                - "column": name of the column in this table
                - "ref_table": the table to reference
                - "ref_column": the column in the referenced table

        Behavior:
            - Replaces the table if it already exists
            - Adds PRIMARY KEY if specified
            - Adds FOREIGN KEY constraint if specified
            - Logs success/failure messages
        """
        if self.engine is None:
            Logger.log("No engine found. Cannot write to the database.")
            return

        try:
            self.ensure_columns_exist(table_name, df)
            df.to_sql(
                name=table_name,
                con=self.engine,
                if_exists='replace',
                index=False,
                dtype=dtype
            )
            Logger.log(f"Successfully wrote table '{table_name}' with {len(df)} rows.")

            with self.engine.connect() as conn:
                if primary_key and not self.has_primary_key(table_name):
                    try:
                        sql = f"ALTER TABLE {table_name} ADD PRIMARY KEY ({primary_key});"
                        conn.execute(text(sql))
                        conn.commit()
                        Logger.log(f"Set '{primary_key}' as PRIMARY KEY for table '{table_name}'.")
                    except Exception as e:
                        Logger.log(f"Failed to set PRIMARY KEY on '{table_name}': {e}", level='error')

                if foreign_key:
                    fk_column = foreign_key.get("column")
                    if not self.has_foreign_key(table_name, fk_column):
                        try:
                            ref_table = foreign_key.get("ref_table")
                            ref_column = foreign_key.get("ref_column")
                            constraint_name = f"fk_{table_name}_{fk_column}"

                            sql = f"""
                                ALTER TABLE {table_name}
                                ADD CONSTRAINT {constraint_name}
                                FOREIGN KEY ({fk_column})
                                REFERENCES {ref_table}({ref_column});
                            """
                            conn.execute(text(sql))
                            conn.commit()
                            Logger.log(f"Set FOREIGN KEY on '{table_name}.{fk_column}'-> '{ref_table}.{ref_column}'.")

                        except Exception as e:
                            Logger.log(f"Failed to set FOREIGN KEY on '{table_name}': {e}", level='error')

        except Exception as e:
            Logger.log(f"Failed to write table '{table_name}': {e}", level='error')

