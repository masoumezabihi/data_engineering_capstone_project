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

  ## Goal
  For each question, get the number of answers per month, then join this with the question metadata.
