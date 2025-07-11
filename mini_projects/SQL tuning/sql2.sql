
*******QUESTION 2  ******
Write a SQL Query to find all the authors who published at least 10 PVLDB papers and at least 10 SIGMOD papers.
You may need to do some legwork here to see how the DBLP spells the names of various conferences and journals.
*************

 EXPLAIN ANALYZE 
 WITH filtered_conferences AS (
  SELECT author, booktitle
  FROM inproceedings
  WHERE booktitle ILIKE '%SIGMOD%' OR booktitle ILIKE '%VLDB%'
),

author_counts AS (
  SELECT 
    author,
    COUNT(CASE WHEN booktitle ILIKE '%SIGMOD%' THEN 1 END) AS sigmod_count,
    COUNT(CASE WHEN booktitle ILIKE '%VLDB%' THEN 1 END) AS pvldb_count
  FROM filtered_conferences
  GROUP BY author
)

SELECT author
FROM author_counts
WHERE sigmod_count >= 10 AND pvldb_count >= 10;


********* EXPLAIN before creating index ***************

"QUERY PLAN"
"Subquery Scan on author_counts  (cost=107282.60..107893.54 rows=526 width=55) (actual time=999.838..1002.874 rows=0 loops=1)"
"  ->  Finalize GroupAggregate  (cost=107282.60..107888.28 rows=526 width=71) (actual time=999.837..1002.873 rows=0 loops=1)"
"        Group Key: inproceedings.author"
"        Filter: ((count(CASE WHEN (inproceedings.booktitle ~~* '%SIGMOD%'::text) THEN 1 ELSE NULL::integer END) >= 10) AND (count(CASE WHEN (inproceedings.booktitle ~~* '%VLDB%'::text) THEN 1 ELSE NULL::integer END) >= 10))"
"        Rows Removed by Filter: 7369"
"        ->  Gather Merge  (cost=107282.60..107787.65 rows=3948 width=71) (actual time=991.532..1001.671 rows=7593 loops=1)"
"              Workers Planned: 2"
"              Workers Launched: 2"
"              ->  Partial GroupAggregate  (cost=106282.58..106331.93 rows=1974 width=71) (actual time=969.325..972.156 rows=2531 loops=3)"
"                    Group Key: inproceedings.author"
"                    ->  Sort  (cost=106282.58..106287.51 rows=1974 width=63) (actual time=969.315..969.445 rows=2655 loops=3)"
"                          Sort Key: inproceedings.author"
"                          Sort Method: quicksort  Memory: 325kB"
"                          Worker 0:  Sort Method: quicksort  Memory: 614kB"
"                          Worker 1:  Sort Method: quicksort  Memory: 68kB"
"                          ->  Parallel Seq Scan on inproceedings  (cost=0.00..106174.53 rows=1974 width=63) (actual time=17.687..963.441 rows=2655 loops=3)"
"                                Filter: ((booktitle ~~* '%SIGMOD%'::text) OR (booktitle ~~* '%VLDB%'::text))"
"                                Rows Removed by Filter: 1144146"
"Planning Time: 4.288 ms"
"Execution Time: 1003.352 ms"



****** Create Index on booktitle column in inproceedings table ********
First we enable trigram index on PostgreSQL with the following command:
	CREATE EXTENSION IF NOT EXISTS pg_trgm;

Then create trigram index:
	CREATE INDEX idx_inproceedings_booktitle_trgm 
	ON inproceedings 
	USING gin (booktitle gin_trgm_ops);




********* EXPLAIN After creating index ***************

"Subquery Scan on author_counts  (cost=15467.61..15543.89 rows=526 width=55) (actual time=17.400..17.402 rows=0 loops=1)"
"  ->  HashAggregate  (cost=15467.61..15538.63 rows=526 width=71) (actual time=17.399..17.400 rows=0 loops=1)"
"        Group Key: inproceedings.author"
"        Filter: ((count(CASE WHEN (inproceedings.booktitle ~~* '%SIGMOD%'::text) THEN 1 ELSE NULL::integer END) >= 10) AND (count(CASE WHEN (inproceedings.booktitle ~~* '%VLDB%'::text) THEN 1 ELSE NULL::integer END) >= 10))"
"        Batches: 1  Memory Usage: 1681kB"
"        Rows Removed by Filter: 7369"
"        ->  Bitmap Heap Scan on inproceedings  (cost=124.34..15408.38 rows=4738 width=63) (actual time=0.539..7.399 rows=7966 loops=1)"
"              Recheck Cond: ((booktitle ~~* '%SIGMOD%'::text) OR (booktitle ~~* '%VLDB%'::text))"
"              Heap Blocks: exact=258"
"              ->  BitmapOr  (cost=124.34..124.34 rows=4738 width=0) (actual time=0.491..0.492 rows=0 loops=1)"
"                    ->  Bitmap Index Scan on idx_inproceedings_booktitle_trgm  (cost=0.00..86.60 rows=4491 width=0) (actual time=0.381..0.381 rows=5062 loops=1)"
"                          Index Cond: (booktitle ~~* '%SIGMOD%'::text)"
"                    ->  Bitmap Index Scan on idx_inproceedings_booktitle_trgm  (cost=0.00..35.37 rows=247 width=0) (actual time=0.110..0.110 rows=2904 loops=1)"
"                          Index Cond: (booktitle ~~* '%VLDB%'::text)"
"Planning Time: 1.432 ms"
"Execution Time: 17.455 ms"


******************************************
Before creating index: PostgreSQL does a sequential scan, checking every row.
After using the trigram index: PostgreSQL uses Bitmap Index Scan to skip many rows 
As we can see, the execution time decreased significantly from 1003.352 ms to 17.455 ms.
******************************************