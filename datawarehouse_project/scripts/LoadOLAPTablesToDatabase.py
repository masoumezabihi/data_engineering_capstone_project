import sqlite3


class LoadOLAPTablesToDatabase():
    
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path) 

    def save_tables(self, dimensions, fact):
        for name, df in dimensions.items():
            df.to_sql(name, self.conn, if_exists="replace", index=False)
        fact.to_sql("fact_lineitem", self.conn, if_exists="replace", index=False)
        self.conn.close()