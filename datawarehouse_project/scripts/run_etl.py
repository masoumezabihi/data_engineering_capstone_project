import os
import pandas as pd
from OLTPLoader import OLTPLoader 
from LoadOLAPTablesToDatabase import LoadOLAPTablesToDatabase
from StarSchemaBuilder import StarSchemaBuilder
from OLAPQuery import OLAPQuery
import logging
import sys
import sqlite3


def main():
    logging.basicConfig(level=logging.INFO, 
                        format="%(asctime)s %(levelname)s %(message)s")

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(scripts_dir)
    raw_data_folder = os.path.join(project_root, "raw_data")
    db_path = os.path.join(project_root, "olap_star_schema.db")

    table_columns = {
        "customer.tbl": ["c_custKey", "c_name", "c_address",
                         "c_nationkey", "c_phone", "c_acctbal",
                         "c_mktsegment", "c_comment"],
        "orders.tbl": ["o_orderKey", "o_custkey", "o_status",
                       "o_totalprice", "o_orderdate", "o_orderpriority",
                       "o_clerk", "o_shippriority", "o_comment"],
        "lineitem.tbl": ["l_orderkey", "l_partkey", "l_suppkey",
                         "l_linenumber", "l_quantity", "l_extendedprice",
                         "l_discount", "l_tax", "l_returnflag",
                         "l_linestatus", "l_shipdate", "l_commitdate",
                         "l_receiptdate", "l_shipinstruct", "l_shipmode",
                         "l_comment"],
        "supplier.tbl": ["s_id", "s_name", "s_address",
                         "s_nationkey", "s_phone", "s_acctbal",
                         "s_comment"],
        "nation.tbl": ["n_id", "n_name", "n_regionkey", "n_comment"],
        "region.tbl": ["r_id", "r_name", "r_comment"],
        "part.tbl": ["p_id", "p_name", "p_mfgr", "p_brand",
                     "p_type", "p_size", "p_container", "p_retailprice",
                     "p_comment"],
        "partsupp.tbl": ["ps_partkey", "ps_suppkey", "ps_availqty",
                         "ps_supplycost", "ps_comment"]
    }

    try:
        # Load OLTP tables
        loader = OLTPLoader(raw_data_folder, table_columns)
        oltp_data = loader.load_all_tables()
        loader.describe_tables()

        # Build Start Schema
        builder = StarSchemaBuilder(oltp_data)
        dim_customer = builder.build_dim_customer()
        dim_part = builder.build_dim_part()
        dim_supplier = builder.build_dim_supplier()
        dim_order = builder.build_dim_order()
        dim_date = builder.build_dim_date()
        fact_lineitem = builder.build_fact_lineitem()

        dimensions = {
            "dim_customer": dim_customer,
            "dim_part": dim_part,
            "dim_supplier": dim_supplier,
            "dim_order": dim_order,
            "dim_date": dim_date
        }

        # Save to database
        loader_db = LoadOLAPTablesToDatabase(db_path)
        loader_db.save_tables(dimensions, fact_lineitem)

        logging.info("ETL run succeeded")

        olap_query = OLAPQuery(db_path)
        print(olap_query.top_5_nations())
        print(olap_query.most_common_shipmode_top5())
        print(olap_query.top_3_selling_months())
        print(olap_query.top_customers())
        print(olap_query.compare_sales_revenue())
        olap_query.close()
    except Exception as e:
        logging.exception("ETL run failed")
        sys.exit(1)



if __name__ == "__main__":
    main()
