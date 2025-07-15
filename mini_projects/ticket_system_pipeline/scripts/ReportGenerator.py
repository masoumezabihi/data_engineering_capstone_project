class ReportGenerator:
    def __init__(self, connection):
        self.connection = connection

    def query_popular_tickets(self):
        sql = """
        SELECT event_name, SUM(num_tickets) AS total_sold
        FROM ticket_sales
        WHERE event_date >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
        GROUP BY event_name
        HAVING total_sold = (
            SELECT MAX(total_sold)
            FROM (
                SELECT event_name, SUM(num_tickets) AS total_sold
                FROM ticket_sales
                WHERE event_date >= DATE_SUB(NOW(), INTERVAL 1 MONTH)
                GROUP BY event_name
            ) AS sub
        )
        ORDER BY event_name;
        """
        cursor = self.connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result

    def format_popular_tickets(self, events):
        if not events:
            return "No ticket sales in the past month."

        lines = ["Here are the most popular tickets in the past month:"]
        for event_name, _ in events:
            lines.append(f"- {event_name}")
        return "\n".join(lines)
