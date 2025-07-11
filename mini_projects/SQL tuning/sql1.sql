
************* Write a SQL Query to find all the conferences held in 2018 that have published at least 200 papers in a single decade.*************


EXPLAIN ANALYZE
WITH decade_counts AS ( 
    SELECT  
        booktitle, 
        FLOOR(year::int / 10) * 10 AS decade, 
        COUNT(*) AS paper_count 
    FROM public.inproceedings 
    GROUP BY booktitle, FLOOR(year::int / 10) * 10 
    HAVING COUNT(*) >= 200 
), 
conferences_2018 AS ( 
    SELECT title, booktitle 
    FROM public.proceedings 
    WHERE year = '2018' 
) 
SELECT c.title 
FROM conferences_2018 c 
JOIN decade_counts d ON c.booktitle = d.booktitle;


********* EXPLAIN before creating index ***************

"Merge Join  (cost=281276.66..374608.17 rows=29007 width=140) (actual time=422.093..452.097 rows=2832 loops=1)"
"  Merge Cond: (inproceedings.booktitle = proceedings.booktitle)"
"  ->  Finalize GroupAggregate  (cost=278221.39..369684.29 rows=114680 width=24) (actual time=404.118..431.493 rows=3898 loops=1)"
"        Group Key: inproceedings.booktitle, ((floor((((inproceedings.year)::integer / 10))::double precision) * '10'::double precision))"
"        Filter: (count(*) >= 200)"
"        Rows Removed by Filter: 17276"
"        ->  Gather Merge  (cost=278221.39..358502.99 rows=688080 width=24) (actual time=404.081..424.326 rows=34609 loops=1)"
"              Workers Planned: 2"
"              Workers Launched: 2"
"              ->  Sort  (cost=277221.36..278081.46 rows=344040 width=24) (actual time=382.332..383.231 rows=11536 loops=3)"
"                    Sort Key: inproceedings.booktitle, ((floor((((inproceedings.year)::integer / 10))::double precision) * '10'::double precision))"
"                    Sort Method: quicksort  Memory: 900kB"
"                    Worker 0:  Sort Method: quicksort  Memory: 957kB"
"                    Worker 1:  Sort Method: quicksort  Memory: 956kB"
"                    ->  Partial HashAggregate  (cost=215927.03..238527.07 rows=344040 width=24) (actual time=358.060..359.392 rows=11536 loops=3)"
"                          Group Key: inproceedings.booktitle, (floor((((inproceedings.year)::integer / 10))::double precision) * '10'::double precision)"
"                          Planned Partitions: 8  Batches: 1  Memory Usage: 2577kB"
"                          Worker 0:  Batches: 1  Memory Usage: 2577kB"
"                          Worker 1:  Batches: 1  Memory Usage: 2577kB"
"                          ->  Parallel Seq Scan on inproceedings  (cost=0.00..120509.55 rows=1433502 width=16) (actual time=0.215..215.678 rows=1146802 loops=3)"
"  ->  Sort  (cost=3055.27..3062.53 rows=2904 width=150) (actual time=17.953..18.264 rows=4330 loops=1)"
"        Sort Key: proceedings.booktitle"
"        Sort Method: quicksort  Memory: 603kB"
"        ->  Seq Scan on proceedings  (cost=0.00..2888.24 rows=2904 width=150) (actual time=0.082..13.423 rows=2979 loops=1)"
"              Filter: (year = '2018'::text)"
"              Rows Removed by Filter: 59120"
"Planning Time: 0.730 ms"
"Execution Time: 452.646 ms"



****** Create Index on Year column in proceedings table ********

	CREATE INDEX idx_proceedings_year ON public.proceedings(year);



********* EXPLAIN After creating index ***************

"QUERY PLAN"
"Merge Join  (cost=280682.88..374014.39 rows=29007 width=140) (actual time=380.493..406.714 rows=2832 loops=1)"
"  Merge Cond: (inproceedings.booktitle = proceedings.booktitle)"
"  ->  Finalize GroupAggregate  (cost=278221.39..369684.29 rows=114680 width=24) (actual time=373.007..396.762 rows=3898 loops=1)"
"        Group Key: inproceedings.booktitle, ((floor((((inproceedings.year)::integer / 10))::double precision) * '10'::double precision))"
"        Filter: (count(*) >= 200)"
"        Rows Removed by Filter: 17276"
"        ->  Gather Merge  (cost=278221.39..358502.99 rows=688080 width=24) (actual time=372.980..390.304 rows=34857 loops=1)"
"              Workers Planned: 2"
"              Workers Launched: 2"
"              ->  Sort  (cost=277221.36..278081.46 rows=344040 width=24) (actual time=352.281..353.385 rows=11619 loops=3)"
"                    Sort Key: inproceedings.booktitle, ((floor((((inproceedings.year)::integer / 10))::double precision) * '10'::double precision))"
"                    Sort Method: quicksort  Memory: 883kB"
"                    Worker 0:  Sort Method: quicksort  Memory: 980kB"
"                    Worker 1:  Sort Method: quicksort  Memory: 961kB"
"                    ->  Partial HashAggregate  (cost=215927.03..238527.07 rows=344040 width=24) (actual time=327.147..328.554 rows=11619 loops=3)"
"                          Group Key: inproceedings.booktitle, (floor((((inproceedings.year)::integer / 10))::double precision) * '10'::double precision)"
"                          Planned Partitions: 8  Batches: 1  Memory Usage: 2577kB"
"                          Worker 0:  Batches: 1  Memory Usage: 2833kB"
"                          Worker 1:  Batches: 1  Memory Usage: 2577kB"
"                          ->  Parallel Seq Scan on inproceedings  (cost=0.00..120509.55 rows=1433502 width=16) (actual time=0.168..193.176 rows=1146802 loops=3)"
"  ->  Sort  (cost=2461.49..2468.75 rows=2904 width=150) (actual time=7.458..7.799 rows=4330 loops=1)"
"        Sort Key: proceedings.booktitle"
"        Sort Method: quicksort  Memory: 603kB"
"        ->  Bitmap Heap Scan on proceedings  (cost=34.80..2294.46 rows=2904 width=150) (actual time=0.266..1.406 rows=2979 loops=1)"
"              Recheck Cond: (year = '2018'::text)"
"              Heap Blocks: exact=1746"
"              ->  Bitmap Index Scan on idx_proceedings_year  (cost=0.00..34.07 rows=2904 width=0) (actual time=0.148..0.148 rows=2979 loops=1)"
"                    Index Cond: (year = '2018'::text)"
"Planning Time: 1.612 ms"
"Execution Time: 407.322 ms"


******************************************
As we can see, the actual time for scanning the proceedings table before indexing the year column was 13.341 ms (13.423 − 0.082). After creating the index, 
the scan time dropped to 1.140 ms (1.406 − 0.266), which is significantly lower. Therefore, indexing clearly improved performance.
******************************************