# Airflow Log Analyzer
This Python script analyzes Airflow DAG logs and reports all errors.

---

## How It Works

1. The script recursively scans all `.log` files in a given DAG log folder.
2. It counts the total number of `ERROR` messages.
3. It prints **all error messages** with their timestamps.

---

## Usage
Run the script with:  __python <script_name> <path_to_logs>__
- <script_name> is the Python file (e.g., log_analyzer.py).
- <path_to_logs> is the folder containing your DAG logs.

---
## Sample Output
The images illustrate the script’s output for two cases: logs with errors and logs without errors.

---

> [!NOTE]  
> - This script is **path-agnostic** — you don’t need to hardcode paths.  
> - Works for logs on your **local machine** or inside an **Airflow Docker container**.  
> - To run inside Docker:  
>   ```bash
>   docker exec -it <container_name> python /opt/airflow/scripts/log_analyzer.py <path_to_logs>
>   ```  
> - Replace `<container_name>` with your Airflow container name.  


