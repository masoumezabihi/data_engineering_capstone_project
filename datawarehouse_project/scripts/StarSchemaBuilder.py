import pandas as pd
class StarSchemaBuilder():
    def __init__(self, data_frames):
        self.dataframes = data_frames
        self.dimensions = {}
        self.fact_lineitem = None


    def build_dim_customer(self):
        df_customer = self.dataframes["customer.tbl"].copy()
        df_customer["customer_key"] = range(1, len(df_customer)+1)
    

        def classify_balance(balance):
            min_acct_bal = df_customer['c_acctbal'].min()
            max_acct_bal = df_customer['c_acctbal'].max()
            interval = (max_acct_bal-min_acct_bal)/3
            if balance < min_acct_bal + interval:
                return "Low"
            elif balance < min_acct_bal + 2*interval:
                return "Medium"
            else:
                return "High"

        # merge nation and region
        df_nation = self.dataframes["nation.tbl"]
        df_region = self.dataframes["region.tbl"]

        df_customer = df_customer.merge(df_nation[['n_id','n_name','n_regionkey']],
                                        left_on='c_nationkey', right_on='n_id', how='left')
        df_customer = df_customer.merge(df_region[['r_id','r_name']],
                                        left_on='n_regionkey', right_on='r_id', how='left')

        dim_customer = df_customer[[
            "customer_key","c_custKey","c_name","c_address","c_phone",
            "c_acctbal","c_mktsegment","n_name","r_name"
        ]].copy()

        dim_customer['acctbal_class'] = dim_customer["c_acctbal"].apply(classify_balance)
        dim_customer.columns = ["customer_key","c_custKey","c_name","c_address",
                                "c_phone","c_acctbal","acctbal_class","c_mktsegment","c_nation_name","c_region_name"]
        self.dimensions["dim_customer"] = dim_customer
        return dim_customer

    def build_dim_part(self):
        df_part= self.dataframes["part.tbl"].copy()
        df_part["part_key"]=range(1, len(df_part)+1)

        dim_part = df_part[["part_key","p_id","p_name","p_mfgr","p_brand","p_type",
                            "p_size","p_container","p_retailprice"]].copy()
        dim_part.columns = ["part_key","p_partkey","p_name","p_mfgr","p_brand","p_type",
                            "p_size","p_container","p_retailprice"]

        self.dimensions["dim_part"] = dim_part
        return dim_part

    def build_dim_supplier(self):
        df_supplier = self.dataframes["supplier.tbl"].copy()
        df_supplier["supplier_key"]=range(1, len(df_supplier)+1)

        df_nation = self.dataframes["nation.tbl"]

        df_supplier = df_supplier.merge(df_nation[['n_id','n_name','n_regionkey']], 
                                        left_on = "s_nationkey", right_on = "n_id", 
                                        how = "left")

        dim_supplier = df_supplier[[
            "supplier_key","s_id","s_name","s_address","s_phone",
            "s_acctbal","n_name"
        ]].copy()
        dim_supplier.columns = ["supplier_key","s_suppkey","s_name","s_address",
                                "s_phone","s_acctbal","s_nation_name"]
        self.dimensions["dim_supplier"] = dim_supplier
        return dim_supplier

    def build_dim_date(self):
        dates = pd.concat([
            pd.to_datetime(self.dataframes['orders.tbl']['o_orderdate']),
            pd.to_datetime(self.dataframes['lineitem.tbl']['l_shipdate']),
            pd.to_datetime(self.dataframes['lineitem.tbl']['l_commitdate']),
            pd.to_datetime(self.dataframes['lineitem.tbl']['l_receiptdate'])
        ]).dropna().unique()

        dim_date = pd.DataFrame({'full_date': pd.to_datetime(dates)})
        dim_date['date_key'] = dim_date['full_date'].dt.strftime('%Y%m%d').astype(int)
        dim_date['day_of_week'] = dim_date['full_date'].dt.day_name()
        dim_date['day_of_month'] = dim_date['full_date'].dt.day
        dim_date['day_of_year'] = dim_date['full_date'].dt.dayofyear
        dim_date['week_of_year'] = dim_date['full_date'].dt.isocalendar().week
        dim_date['month'] = dim_date['full_date'].dt.month
        dim_date['month_name'] = dim_date['full_date'].dt.month_name()
        dim_date['quarter'] = dim_date['full_date'].dt.quarter
        dim_date['year'] = dim_date['full_date'].dt.year
        dim_date['is_weekend'] = dim_date['full_date'].dt.weekday >= 5

        self.dimensions["dim_date"] = dim_date
        return dim_date  
    
    def build_dim_order(self):
        df_orders = self.dataframes["orders.tbl"].copy()
        df_orders["order_key"] = range(1, len(df_orders)+1)

        dim_order = df_orders[["order_key","o_orderKey","o_status","o_orderdate",
                               "o_orderpriority","o_clerk","o_shippriority"]].copy()
        dim_order.columns = ["order_key","o_orderkey","o_order_status","o_order_date",
                             "o_order_priority","o_clerk","o_ship_priority"]
        self.dimensions["dim_order"] = dim_order
        return dim_order

    def build_fact_lineitem(self):
        df_lineitem = self.dataframes["lineitem.tbl"].copy()
        dim_order = self.dimensions["dim_order"]
        dim_customer = self.dimensions["dim_customer"]
        dim_part = self.dimensions["dim_part"]
        dim_supplier = self.dimensions["dim_supplier"]
        dim_date = self.dimensions["dim_date"]
        
        df_lineitem['l_shipdate'] = pd.to_datetime(df_lineitem['l_shipdate'])
        df_lineitem['l_commitdate'] = pd.to_datetime(df_lineitem['l_commitdate'])
        df_lineitem['l_receiptdate'] = pd.to_datetime(df_lineitem['l_receiptdate'])

        # merge surrogate keys
        df_lineitem = df_lineitem.merge(dim_order[['o_orderkey','order_key']],
                                        left_on='l_orderkey', right_on='o_orderkey', how='left')
        df_lineitem = df_lineitem.merge(dim_customer[['c_custKey','customer_key']],
                                        left_on='l_orderkey', right_on='c_custKey', how='left')
        df_lineitem = df_lineitem.merge(dim_part[['p_partkey','part_key']],
                                        left_on='l_partkey', right_on='p_partkey', how='left')
        df_lineitem = df_lineitem.merge(dim_supplier[['s_suppkey','supplier_key']],
                                        left_on='l_suppkey', right_on='s_suppkey', how='left')
        df_lineitem = df_lineitem.merge(dim_date[['date_key','full_date']],
                                        left_on='l_shipdate', right_on='full_date', how='left')
        df_lineitem.rename(columns={'date_key':'ship_date_key'}, inplace=True)

        df_lineitem = df_lineitem.merge(dim_date[['date_key','full_date']],
                                        left_on='l_commitdate', right_on='full_date', how='left')
        df_lineitem.rename(columns={'date_key':'commit_date_key'}, inplace=True)

        df_lineitem = df_lineitem.merge(dim_date[['date_key','full_date']],
                                        left_on='l_receiptdate', right_on='full_date', how='left')
        df_lineitem.rename(columns={'date_key':'receipt_date_key'}, inplace=True)



        fact_lineitem = df_lineitem[['order_key','customer_key','part_key','supplier_key',
                                     'ship_date_key','commit_date_key','receipt_date_key',
                                     'l_quantity','l_extendedprice','l_discount','l_tax','l_shipmode']].copy()
        fact_lineitem['lineitem_key'] = range(1,len(fact_lineitem)+1)

        fact_lineitem['l_revenue'] = df_lineitem['l_extendedprice'] * (1-df_lineitem['l_discount'])

        fact_lineitem = fact_lineitem[['lineitem_key','order_key','customer_key','part_key','supplier_key',
                                       'ship_date_key','commit_date_key','receipt_date_key',
                                       'l_quantity','l_extendedprice','l_discount','l_tax','l_shipmode','l_revenue']]
        self.fact_lineitem = fact_lineitem
        return fact_lineitem
