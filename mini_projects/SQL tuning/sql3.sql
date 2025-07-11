
*******QUESTION 3  ******
Write a SQL Query to find the total number of conference publications for each decade, starting from 1970 and ending in 2019. For instance,
to find the total papers from the 1970s you would sum the totals from 1970, 1971,1972…1978, up to 1979. Please do this for the decades 1970, 1980, 1990, 2000, and 2010.
*************


EXPLAIN ANALYZE
SELECT 
  FLOOR(year::int / 10) * 10 AS decade,
  COUNT(*) AS total_publications
FROM inproceedings
WHERE year >= '1970' AND year <= '2019'
GROUP BY decade
ORDER BY decade;



********* EXPLAIN before creating index ***************

"QUERY PLAN"
"Finalize GroupAggregate  (cost=128443.42..128461.13 rows=66 width=16) (actual time=532.275..536.672 rows=5 loops=1)"
"  Group Key: ((floor((((year)::integer / 10))::double precision) * '10'::double precision))"
"  ->  Gather Merge  (cost=128443.42..128458.82 rows=132 width=16) (actual time=532.271..536.668 rows=15 loops=1)"
"        Workers Planned: 2"
"        Workers Launched: 2"
"        ->  Sort  (cost=127443.40..127443.56 rows=66 width=16) (actual time=514.273..514.274 rows=5 loops=3)"
"              Sort Key: ((floor((((year)::integer / 10))::double precision) * '10'::double precision))"
"              Sort Method: quicksort  Memory: 25kB"
"              Worker 0:  Sort Method: quicksort  Memory: 25kB"
"              Worker 1:  Sort Method: quicksort  Memory: 25kB"
"              ->  Partial HashAggregate  (cost=127439.75..127441.40 rows=66 width=16) (actual time=514.256..514.257 rows=5 loops=3)"
"                    Group Key: (floor((((year)::integer / 10))::double precision) * '10'::double precision)"
"                    Batches: 1  Memory Usage: 24kB"
"                    Worker 0:  Batches: 1  Memory Usage: 24kB"
"                    Worker 1:  Batches: 1  Memory Usage: 24kB"
"                    ->  Parallel Seq Scan on inproceedings  (cost=0.00..122123.45 rows=1063261 width=8) (actual time=0.214..448.189 rows=852307 loops=3)"
"                          Filter: ((year >= '1970'::text) AND (year <= '2019'::text))"
"                          Rows Removed by Filter: 294495"
"Planning Time: 0.722 ms"
"Execution Time: 536.717 ms"



****** Create Index on year column in inproceedings  table ********
CREATE INDEX idx_inproceedings_year_text ON inproceedings(year);


********* EXPLAIN After creating index ***************

"Finalize GroupAggregate  (cost=128443.42..128461.13 rows=66 width=16) (actual time=574.500..578.311 rows=5 loops=1)"
"  Group Key: ((floor((((year)::integer / 10))::double precision) * '10'::double precision))"
"  ->  Gather Merge  (cost=128443.42..128458.82 rows=132 width=16) (actual time=574.495..578.304 rows=15 loops=1)"
"        Workers Planned: 2"
"        Workers Launched: 2"
"        ->  Sort  (cost=127443.40..127443.56 rows=66 width=16) (actual time=556.765..556.766 rows=5 loops=3)"
"              Sort Key: ((floor((((year)::integer / 10))::double precision) * '10'::double precision))"
"              Sort Method: quicksort  Memory: 25kB"
"              Worker 0:  Sort Method: quicksort  Memory: 25kB"
"              Worker 1:  Sort Method: quicksort  Memory: 25kB"
"              ->  Partial HashAggregate  (cost=127439.75..127441.40 rows=66 width=16) (actual time=556.754..556.755 rows=5 loops=3)"
"                    Group Key: (floor((((year)::integer / 10))::double precision) * '10'::double precision)"
"                    Batches: 1  Memory Usage: 24kB"
"                    Worker 0:  Batches: 1  Memory Usage: 24kB"
"                    Worker 1:  Batches: 1  Memory Usage: 24kB"
"                    ->  Parallel Seq Scan on inproceedings  (cost=0.00..122123.45 rows=1063261 width=8) (actual time=0.116..483.853 rows=852307 loops=3)"
"                          Filter: ((year >= '1970'::text) AND (year <= '2019'::text))"
"                          Rows Removed by Filter: 294495"
"Planning Time: 1.691 ms"
"Execution Time: 578.359 ms"


******************************************
As we can see, the execution time did not change, and the index was not used even after creating it. This is because the condition (1970–2019) matches many rows, 
and PostgreSQL thinks that reading the whole table is faster than using the index. Index scans work better when only a small number of rows need to be selected.
******************************************