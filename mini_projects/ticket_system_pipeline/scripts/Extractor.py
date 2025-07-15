import csv

class Extractor:
    def read_csv(self, file_path_csv):
        data = []

        # Define headers in the correct order
        fieldnames = [
            'ticket_id', 'trans_date', 'event_id', 'event_name',
            'event_date', 'event_type', 'event_city',
            'customer_id', 'price', 'num_tickets'
        ]

        with open(file_path_csv, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=fieldnames)
            for row in reader:
                data.append(row)

        print(f"✅ Extracted {len(data)} rows from {file_path_csv}")
        return data
