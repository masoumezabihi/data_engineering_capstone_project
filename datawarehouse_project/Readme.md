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
  nation        revenue
0 MIDDLE EAST  359,205.16
1 AFRICA       350,053.73
2 MIDDLE EAST  339,713.20
3 ASIA         335,867.31
4 AFRICA       321,142.63
