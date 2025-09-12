# PySpark Query Optimization (Local Execution)
## Project overview

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
| Pushed filter (default 200 partitions) | 3.69s          | 3.60s            | Minor improvement                             |
| Pushed filter (with 4 partitions)      | 2.96s          | 2.78s            | Minor improvement                            |
| Repartitioning both DataFrames (200)   | 3.72s          | 2.86s            | Repartitioning improve performance       |
| Repartitioning both DataFrames (4)     | 2.74s          | 2.94s            | Small overhead            |
| Broadcast `answers_month`              | 2.92s          | 2.87s            | Small improvement                        |
| Broadcast `questionsDF`                | 2.81s          | 2.97s            | Small overhead                              |


## Notes
- With smaller datasets, pushed filters show only minor improvements. The performance gain becomes more noticeable with larger datasets where I/O and scan time dominate
- By default, Spark uses **200 shuffle partitions**, which is excessive for small datasets and local development. Applying  **.repartition(4, "column_id")** can reduce shuffle overhead when the default (200) is active — this was noticeable in our run. However, if **spark.sql.shuffle.partitions** is already set to 4, explicit repartitioning offers little to no benefit, and may even introduce    minor overhead due to the extra shuffle step.
- As we can see, the broadcast join did not have a significant impact on performance. The main benefit of a broadcast join is that it avoids moving a lot of data around by copying a small dataset to all parts of the cluster. But if both datasets are already small, this doesn’t really help. Also, In this project, Spark is running in local mode (on a single machine), not in a cluster. As a result, broadcast joins did not significantly improve performance, since there's no network communication to avoid. 
