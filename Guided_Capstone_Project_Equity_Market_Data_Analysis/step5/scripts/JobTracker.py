import datetime
import psycopg2


class JobTracker(object):
    def __init__(self, jobname, dbconfig):
        self.jobname = jobname
        self.dbconfig = dbconfig


    def assign_job_id(self):
        today = datetime.date.today().isoformat()  
        job_id = f"{self.jobname}_{today}" 
        return job_id


    def update_job_status(self, status):
        job_id = self.assign_job_id()
        print("Job ID Assigned: {}".format(job_id))

        update_time = datetime.datetime.now()
        table_name = self.dbconfig['postgres']['job_tracker_table_name']
        connection = self.get_db_connection()
        try:
            cursor = connection.cursor()
            insert_query = f"""
            INSERT INTO {table_name} (job_id, status, updated_time)
            VALUES (%s, %s, %s)
            ON CONFLICT (job_id) DO UPDATE
            SET status = EXCLUDED.status,
                updated_time = EXCLUDED.updated_time;
            """
            cursor.execute(insert_query, (job_id, status, update_time))
            connection.commit()
            cursor.close()
            print(f"Job status updated for {job_id} with status '{status}' at {update_time}")
        except (Exception, psycopg2.Error) as error:
            print("error executing db statement for job tracker.")
        return


    def get_job_status(self, job_id):
        # connect db and send sql query
        table_name = self.dbconfig['postgres']['job_tracker_table_name']
        connection = self.get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} WHERE job_id = %s", (job_id,))
            record = cursor.fetchone() 
            cursor.close()
            return record
        except (Exception, psycopg2.Error) as error:
            print("error executing db statement for job tracker.")
            return


    def get_db_connection(self):
        connection = None
        print("Connecting to the PostgreSQL database...")
        try:
            pg_conf = self.dbconfig["postgres"]
            connection = psycopg2.connect(
                dbname = pg_conf["database"],
                user = pg_conf["user"],
                password = pg_conf["password"],
                host = pg_conf["host"],
                port = pg_conf["port"]
            )

            print("Successfully connected to the PostgreSQL database.")
        except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
        return connection