# Data Pipeline Mini Project

In this project, a Python program reads sales data from a file named 'third_party_sales_1.csv', formats the data, and loads it into a MySQL database table called 'ticket_sales'. After that, it performs some analysis and displays the results on the screen.


### Prerequisites

1. python 3 needs to be installed  

2. Mysql server needs to be installed and a database credtional need to be set up. 


### Installing


#### Step 1. Download source code
Create a work folder on your compulter and downlad files in following github folder to it
https://github.com/huangc11/Springboard/tree/main/proj_15_data_pipelines 

#### Step 2. Install MySQL Python connector using pip
Run following  pip command to install the pyhton module:

pip install mysql-connector-python

#### Step 3: Create database and table in mysql database

 1) At dos prompt,  launch mysql shell to connect to mysql server using following command (assume you have set up a credential,  'dbuser1' as username and a password):
 
     mysql -u dbuser1 -p
 
 2) After  connecting to mysql serer, run follow command to create database if it is not existing:
 
  create database ticket_system
  
 3) Type command 'use ticket_system' to connect to the database.
 
 4) Run the DDL statement in  of one of the downloaded file, 'cr_table_sales.sql',  to create table 'sales'
 

#### Step 4: Run python script

At Windows 10 Dos prompty, navigate to the work folder created at step 1, enter following command to run the python script
python main_pipeline.py

#### Note:
1. The program needa some information to connectd to mysql database. So at the beginning  you will be asked 5 questions (if your answer is the same as the default value, you can hit enter to skip it):
Please enter the databse username:
Please enter the databse password:
please enter the port(default=3306):
Please enter the localhost(default="localhost"):
Please enter the databse(default='ticket_system'):


2. After 5 questions get answered,  the program will try to conenct to database. If it was not able to connect the database, it will display an error message and abort.    Otherwise, it will read the sales data from file  'third_party_sales_1.csv', format the data and load the formatted data into mysql table 'sales'. Then it will do some analysis and display the  result  'the top 2 most popular tickets', on the screen.
