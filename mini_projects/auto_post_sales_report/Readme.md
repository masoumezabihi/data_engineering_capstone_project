# Automobile Post-Sales Report with Apache Spark

This project processes automobile incident data using Apache Spark. It extracts vehicle make and year from initial sales records, propagates them to related records, and produces a report counting incidents grouped by make and year.

## Project Structure

- `autoinc_spark.py` – Main PySpark script to process data
- `run_autoinc.sh` – Shell script to run the PySpark job and capture log
- `data.csv` - CSV data input file

## Environment & Setup

This project was developed and tested using:

- **Hortonworks Sandbox (HDP_3.0.1_virtualbox_181205.ova)** running in **VirtualBox-7.1.12-169651-Win**
- **Apache Spark 2.x**
- **HDFS**
- **Local mode** execution of Spark job (not on YARN)

## Prerequisites
Make sure the following are available:

- Hortonworks Sandbox is running in VirtualBox
- Terminal access to the VM via http://localhost:4200/
- Input file should be located in HDFS at: /user/root/spark_mini_project1/input/data.csv
- Python script and shell script should be inside VM root directory (/root)

## How to Run
1. Use the terminal inside VirtualBox located in http://localhost:4200/ and sign in as root user
2. Make sure you’re in the directory where both scripts are stored:
3. Run the shell script: bash run_autoinc.sh (This will execute the Spark job in local mode using:  spark-submit --master local /root/autoinc_spark.py > output.log 2>&1 and attach the command line execution log for the successful and failed job run.)
