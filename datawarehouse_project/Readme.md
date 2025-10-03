# ETL Star Schema Project – Prospa Data Engineering Challenge  

## Overview  
This project solves the [Prospa Data Engineer interview challenge](https://github.com/prospa-group-oss/interview-test-data-engineer).  

The pipeline:  
1. **Extract** OLTP data from `.tbl` text files.  
2. **Transform** into a **star schema** for OLAP.  
3. **Load** into a SQLite database.  
4. **Query** with analytical SQL queries.  

Built in **Python (pandas + sqlite3)**.  

---

## 📂 Project Structure  


---

## ⚙️ How It Works  

### **1. Extract**  
- `OLTPLoader` reads `.tbl` files into Pandas DataFrames.  
- Schema applied per table.  
- Includes a `describe_tables()` function for data exploration.  

### **2. Transform**  
- `StarSchemaBuilder` builds dimensions and fact:  
  - `dim_customer` (with account balance classification + nation/region merge)  
  - `dim_part`  
  - `dim_supplier` (nation join)  
  - `dim_order`  
  - `dim_date` (calendar dimension)  
  - `fact_lineitem` (joins surrogate keys, calculates revenue)  

### **3. Load**  
- `LoadOLAPTablesToDatabase` writes dimensions + fact into SQLite (`olap_star_schema.db`).  

### **4. Query**  
- `OLAPQuery` implements analytical queries:  
  - Top 5 nations by revenue  
  - Most common ship mode for top nations  
  - Top 3 selling months  
  - Top customers (by revenue/quantity)  
  - Financial year revenue comparison  

---

## 🖼️ Star Schema Design  

![Star Schema](star_schema.png)  

- **Fact Table:** `fact_lineitem`  
- **Dimensions:** Customer, Supplier, Part, Order, Date  

---

## Running the Project  

### 1. Clone this repository
```bash
git clone https://github.com/your-username/prospa-etl-challenge.git
cd prospa-etl-challenge
```
### 2. Run the ETL script
The script automatically reads data from the raw_data/ folder and creates a SQLite database:
- python scripts/run_etl.py

### 3. Inspect the generated database
After running the ETL, a database file olap_star_schema.db will be created in the project root.
You can explore the tables using the SQLite command-line interface:
- Open the database: sqlite3 olap_star_schema.db
- List all tables in the database:.tables <br>
You should see the OLAP tables:
- dim_customer, dim_part, dim_supplier, dim_order, dim_date, fact_lineitem

### 4. Example Query Outputs  

After execution, the script prints analytical results directly to the console.  
All query statements are implemented in the `OLAPQuery` class (`scripts/OLAPQuery.py`).  

**Top 5 nations by revenue** 
```
   nation       revenue
0 MIDDLE EAST  359,205.16
1 AFRICA       350,053.73
2 MIDDLE EAST  339,713.20
3 ASIA         335,867.31
4 AFRICA       321,142.63
```
**Most common ship mode for top 5 nations** 
```
most_common_ship_mode
0     TRUCK
```

**Top 3 selling months (by order count)** 
```
  year month_name orders_count
0 1994 March         930
1 1996 October       862
2 1993 December       846
```
**Top customers (by revenue or quantity)** 
```customer_key customer_name
   0 1121      Customer#000001121
   1 645       Customer#000000645
```
**Revenue comparison by financial year**
```
financial_year revenue
0 1991       1.065957e+08
1 1992       1.447356e+08
2 1993       1.651534e+08
3 1994       1.450829e+08
4 1995       1.570654e+08
5 1996       1.610370e+08
6 1997       1.510506e+08
7 1992       1.565555e+08
8 1993       1.609816e+08
9 1994       1.580713e+08
10 1995      1.526817e+08
11 1996      1.566896e+08
12 1997      1.511401e+08
13 1998      7.829449e+07
```
