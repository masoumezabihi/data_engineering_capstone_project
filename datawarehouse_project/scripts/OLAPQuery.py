import sqlite3
import pandas as pd

class OLAPQuery:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def top_5_nations(self):
        query = f"""
        SELECT 
            c.c_nation_name AS nation,
            ROUND(SUM(f.l_extendedprice * (1 - f.l_discount)),2) AS revenue
        FROM fact_lineitem f
        JOIN dim_customer c ON f.customer_key = c.c_custKey
        GROUP BY c.c_name
        ORDER BY revenue DESC
        LIMIT 5;
        """
        return pd.read_sql_query(query, self.conn)

    def most_common_shipmode_top5(self):
        query = """
        WITH top5 AS (
            SELECT c.c_nation_name AS nation
            FROM fact_lineitem f
            JOIN dim_customer c ON f.customer_key = c.c_custKey
            GROUP BY c.c_nation_name
            ORDER BY SUM(f.l_extendedprice * (1 - f.l_discount)) DESC
            LIMIT 5
        )
        SELECT t.most_common_ship_mode
        FROM (
            SELECT f.l_shipmode AS most_common_ship_mode, COUNT(*) AS frequency
            FROM fact_lineitem f
            JOIN dim_customer c ON f.customer_key = c.customer_key
            JOIN top5 t ON c.c_nation_name = t.nation
            GROUP BY f.l_shipmode
            ORDER BY frequency DESC
            LIMIT 1
        ) AS t;
        """
        return pd.read_sql_query(query, self.conn)

    def top_3_selling_months(self):
        query = """
        SELECT d.year, d.month_name, COUNT(*) AS orders_count
        FROM fact_lineitem f
        JOIN dim_date d ON f.commit_date_key = d.date_key
        GROUP BY d.year, d.month_name
        ORDER BY orders_count DESC
        LIMIT 3;
        """
        return pd.read_sql_query(query, self.conn)

    def top_customers(self):
        query = """
        WITH customer_revenue AS (
            SELECT 
                c.c_custKey,
                c.c_name,
                SUM(f.l_extendedprice * (1 - f.l_discount)) AS total_revenue,
                SUM(f.l_quantity) AS total_quantity
            FROM fact_lineitem f
            JOIN dim_customer c ON f.customer_key = c.c_custKey
            GROUP BY c.c_custKey, c.c_name
        )
        SELECT ranked.c_custKey AS customer_key, ranked.c_name AS customer_name
        FROM (
            SELECT *,
                RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
                RANK() OVER (ORDER BY total_quantity DESC) AS quantity_rank
            FROM customer_revenue
        ) AS ranked
        WHERE revenue_rank = 1 OR quantity_rank = 1;
        """
        return pd.read_sql_query(query, self.conn)

    def compare_sales_revenue(self):
        query = """
            SELECT
                (CASE WHEN strftime('%m', d.full_date) >= '07' THEN strftime('%Y', d.full_date)
                ELSE CAST(strftime('%Y', d.full_date) AS INTEGER) - 1
                END) AS financial_year,
                SUM(f.l_extendedprice * (1 - f.l_discount)) AS revenue 
            FROM fact_lineitem f
            INNER JOIN dim_date d 
            ON f.commit_date_key = d.date_key
            GROUP BY 
                CASE WHEN strftime('%m', d.full_date) >= '07' THEN strftime('%Y', d.full_date)
                ELSE CAST(strftime('%Y', d.full_date) AS INTEGER) - 1
                END
            ORDER BY financial_year
        """
        return pd.read_sql_query(query, self.conn)

    def close(self):
        self.conn.close()
