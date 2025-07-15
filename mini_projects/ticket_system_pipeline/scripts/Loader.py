from datetime import datetime
from Logger import Logger

class Loader:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def insert_to_third_party(self, data):
        Logger.log("Starting data load into ticket_sales table.", 'info')
        try:
            connection = self.db_handler.get_connection()
            cursor = connection.cursor()
        except Exception as e:
            Logger.log(f"Failed to connect to database: {e}", 'error')
            return 

        insert_query = """
        INSERT IGNORE INTO ticket_sales (
            ticket_id, trans_date, event_id, event_name,
            event_date, event_type, event_city,
            customer_id, price, num_tickets
        ) VALUES (
            %(ticket_id)s, %(trans_date)s, %(event_id)s, %(event_name)s,
            %(event_date)s, %(event_type)s, %(event_city)s,
            %(customer_id)s, %(price)s, %(num_tickets)s
        )
        """

        for row in data:
            try:
                converted_row = {
                    'ticket_id': int(row['ticket_id']),
                    'trans_date': int(row['trans_date'].replace('-', '')),
                    'event_id': int(row['event_id']),
                    'event_name': row['event_name'],
                    'event_date': row['event_date'], 
                    'event_type': row['event_type'],
                    'event_city': row['event_city'],
                    'customer_id': int(row['customer_id']),
                    'price': float(row['price']),
                    'num_tickets': int(row['num_tickets']),
                }

                cursor.execute(insert_query, converted_row)
            except Exception as e:
                 Logger.log(f"Error inserting row with ticket_id {row.get('ticket_id', '?')}: {e}", 'error')

        connection.commit()
        cursor.close()
        Logger.log(f"Loaded {len(data)} rows into ticket_sales.", 'info')
