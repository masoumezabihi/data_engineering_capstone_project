# PySpark Query Optimization (Local Execution)
## Project overview
  Project Overview

Apache Spark is a powerful tool for processing large datasets — but its speed heavily depends on how it's used.
Poor code layout, unnecessary shuffles, and inefficient operations can significantly slow down your Spark jobs.

This project focuses on optimizing a PySpark query that calculates the number of answers each question received per month. You'll compare the original and optimized queries,
analyze their execution plans, and measure improvements in performance — all on a local machine.

## Problem Statement
 You're given two datasets (in Parquet format):
  - questions: contains metadata about questions (e.g. title, creation date)
  - answers: contains answers linked to each question via question_id
   #### Goal
    For each question, get the number of answers per month, then join this with the question metadata.
    
## Optimizations Applied
This section summarizes the techniques applied to improve query performance, all tested locally on a 2-core CPU using ~500MB of data.

| Optimization Strategy           | What Was Changed                                                                |
| -------------------------------- | ------------------------------------------------------------------------------ |
| ✅ Shuffle partition tuning     | `spark.conf.set("spark.sql.shuffle.partitions", 4)` instead of default `200`   |
| ✅ Broadcast join               | Applied broadcast to the smaller DataFrame for faster joins                    |
| ✅ Pushed filters               | Used `.filter(col("question_id").isNotNull())` early to reduce scanned data    |
| ✅ Repartitioning by key        | Applied `.repartition(4, "question_id")` before `join()` and `groupBy()`       | 
| ✅ Measured execution time      | Used Python’s `time.time()` to track execution performance                     |


## Performance Test Summary
Each row shows the average execution time in seconds across three runs:

| Optimization Applied                   | Original Query | Refactored Query | Notes                                    |
| -------------------------------------- | -------------- | ---------------- | ---------------------------------------- |
| No optimization (default config)       | 3.51s          | -                | Baseline                                 |
| Shuffle partitions = 4                 | 3.41s          | 2.78s            | Yielded strong gain                      |
| Pushed filter (default 200 partitions) | 3.69s          | 3.60s            | Minor impact                             |
| Pushed filter (with 4 partitions)      | 2.96s          | 2.78s            | Minor impact                             |
| Repartitioning both DataFrames (200)   | 3.72s          | 2.86s            | Repartitioning improve performance       |
| Repartitioning both DataFrames (4)     | 2.74s          | 2.94s            | Repartitioning added overhead            |
| Broadcast `answers_month`              | 2.92s          | 2.87s            | Small improvement                        |
| Broadcast `questionsDF`                | 2.81s          | 2.97s            |Add overhead                                    |
