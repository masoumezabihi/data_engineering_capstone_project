# Data Pipeline Mini Project

In this project, a Python program reads sales data from a file named **third_party_sales_1.csv**, formats the data, and loads it into a MySQL database table called **ticket_sales**. After that, it performs some analysis and displays the results on the screen.


### Prerequisites

1. python 3 needs to be installed  

2. Mysql server needs to be installed and a database credtional need to be set up. 


### Installing


#### Step 1. Download source code
Create a work folder on your computer. Then download only the ticket_system_pipeline folder from the repository at:
https://github.com/masoumezabihi/data_engineering_capstone_project/tree/main/mini_projects/ticket_system_pipeline


#### Step 2. Install MySQL Python connector
mysql-connector-python is a MySQL database adapter in Python. It provides convenient APIs to load and query the tables. It also has a nice tool to load CSV files into the tables. In this step, we will need to install this Python module with following command:

pip3 install mysql-connector-python

#### Step 3: Setup database connection
To run the ETL pipeline and generate reports, the application needs to connect to a MySQL database. Instead of hardcoding credentials, the application reads them from an environment file (.env) located in the root folder of this project.

1. **Create your own `.env` file** in the project root, and include your MySQL connection details:

<pre> DB_USER=your_mysql_username DB_PASSWORD=your_mysql_password DB_HOST=127.0.0.1 DB_NAME=ticket_system DB_PORT=3306 </pre>

2. **Create the database** using the following MySQL command (from terminal or a client like MySQL Workbench):
   ```sql
    CREATE DATABASE ticket_system;

3. **Note**: You do not need to create any tables manually. The application will automatically create a table named **ticket_sales** when you run it.

#### Step 4: Run python script

On Windows 10 Command Prompt, navigate to the work folder you created in Step 1.  
Then run the following command to execute the pipeline script located in the `scripts` folder:

 python scripts/main.py
