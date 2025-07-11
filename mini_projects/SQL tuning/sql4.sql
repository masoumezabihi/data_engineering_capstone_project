
*******QUESTION 4  ******
Write a SQL Query to find the top 10 authors publishing in journals and conferences whose titles contain the word data.
*************

EXPLAIN ANALYZE
WITH combined_publications AS (
    SELECT author, title
    FROM public.articles
    WHERE title ILIKE '%data%'

    UNION ALL
	
    SELECT editor AS author, title
    FROM public.proceedings
    WHERE title ILIKE '%data%'
)

SELECT author, COUNT(*) AS publication_count
FROM combined_publications
WHERE author IS NOT NULL
GROUP BY author
ORDER BY publication_count DESC
LIMIT 10;



********* EXPLAIN before creating index ***************

"Limit  (cost=113936.52..113936.54 rows=10 width=63) (actual time=2370.358..2377.240 rows=10 loops=1)"
"  ->  Sort  (cost=113936.52..113937.02 rows=200 width=63) (actual time=2370.358..2377.238 rows=10 loops=1)"
"        Sort Key: (count(*)) DESC"
"        Sort Method: top-N heapsort  Memory: 25kB"
"        ->  Finalize GroupAggregate  (cost=113881.53..113932.20 rows=200 width=63) (actual time=2176.253..2361.687 rows=203956 loops=1)"
"              Group Key: ""*SELECT* 1"".author"
"              ->  Gather Merge  (cost=113881.53..113928.20 rows=400 width=63) (actual time=2176.246..2329.285 rows=213983 loops=1)"
"                    Workers Planned: 2"
"                    Workers Launched: 2"
"                    ->  Sort  (cost=112881.50..112882.00 rows=200 width=63) (actual time=2129.623..2161.292 rows=71328 loops=3)"
"                          Sort Key: ""*SELECT* 1"".author"
"                          Sort Method: external merge  Disk: 5576kB"
"                          Worker 0:  Sort Method: external merge  Disk: 6184kB"
"                          Worker 1:  Sort Method: external merge  Disk: 6112kB"
"                          ->  Partial HashAggregate  (cost=112871.86..112873.86 rows=200 width=63) (actual time=1884.083..1896.480 rows=71328 loops=3)"
"                                Group Key: ""*SELECT* 1"".author"
"                                Batches: 5  Memory Usage: 8257kB  Disk Usage: 2824kB"
"                                Worker 0:  Batches: 5  Memory Usage: 8257kB  Disk Usage: 3472kB"
"                                Worker 1:  Batches: 5  Memory Usage: 8257kB  Disk Usage: 3456kB"
"                                ->  Parallel Append  (cost=0.00..112422.51 rows=89869 width=55) (actual time=0.257..1854.900 rows=74084 loops=3)"
"                                      ->  Subquery Scan on ""*SELECT* 1""  (cost=0.00..109374.45 rows=87736 width=55) (actual time=0.257..1809.902 rows=72939 loops=3)"
"                                            ->  Parallel Seq Scan on articles  (cost=0.00..108497.09 rows=87736 width=87) (actual time=0.257..1806.579 rows=72939 loops=3)"
"                                                  Filter: ((author IS NOT NULL) AND (title ~~* '%data%'::text))"
"                                                  Rows Removed by Filter: 1095515"
"                                      ->  Subquery Scan on ""*SELECT* 2""  (cost=0.00..2598.72 rows=3011 width=56) (actual time=0.243..63.062 rows=1718 loops=2)"
"                                            ->  Parallel Seq Scan on proceedings  (cost=0.00..2568.61 rows=3011 width=88) (actual time=0.243..62.977 rows=1718 loops=2)"
"                                                  Filter: ((editor IS NOT NULL) AND (title ~~* '%data%'::text))"
"                                                  Rows Removed by Filter: 29332"
"Planning Time: 1.066 ms"
"Execution Time: 2381.347 ms"



****** Create Index on title column in both inproceedings and articles tables ********
	CREATE INDEX idx_articles_title_trgm ON public.articles USING gin (title gin_trgm_ops);
	CREATE INDEX idx_proceedings_title_trgm ON public.proceedings USING gin (title gin_trgm_ops);



********* EXPLAIN After creating index ***************

"Limit  (cost=108834.57..108834.60 rows=10 width=63) (actual time=1520.423..1530.565 rows=10 loops=1)"
"  ->  Sort  (cost=108834.57..108835.07 rows=200 width=63) (actual time=1520.422..1530.564 rows=10 loops=1)"
"        Sort Key: (count(*)) DESC"
"        Sort Method: top-N heapsort  Memory: 25kB"
"        ->  Finalize GroupAggregate  (cost=108779.58..108830.25 rows=200 width=63) (actual time=1329.163..1515.498 rows=203956 loops=1)"
"              Group Key: ""*SELECT* 1"".author"
"              ->  Gather Merge  (cost=108779.58..108826.25 rows=400 width=63) (actual time=1329.157..1482.981 rows=214455 loops=1)"
"                    Workers Planned: 2"
"                    Workers Launched: 2"
"                    ->  Sort  (cost=107779.56..107780.06 rows=200 width=63) (actual time=1288.235..1320.375 rows=71485 loops=3)"
"                          Sort Key: ""*SELECT* 1"".author"
"                          Sort Method: external merge  Disk: 5424kB"
"                          Worker 0:  Sort Method: external merge  Disk: 6200kB"
"                          Worker 1:  Sort Method: external merge  Disk: 6272kB"
"                          ->  Partial HashAggregate  (cost=107769.92..107771.92 rows=200 width=63) (actual time=1033.449..1045.019 rows=71485 loops=3)"
"                                Group Key: ""*SELECT* 1"".author"
"                                Batches: 5  Memory Usage: 8257kB  Disk Usage: 1752kB"
"                                Worker 0:  Batches: 5  Memory Usage: 8257kB  Disk Usage: 3496kB"
"                                Worker 1:  Batches: 5  Memory Usage: 8257kB  Disk Usage: 3504kB"
"                                ->  Parallel Append  (cost=74.05..107320.57 rows=89869 width=55) (actual time=15.399..1002.641 rows=74084 loops=3)"
"                                      ->  Subquery Scan on ""*SELECT* 1""  (cost=1458.97..104604.33 rows=87736 width=55) (actual time=28.388..993.970 rows=72939 loops=3)"
"                                            ->  Parallel Bitmap Heap Scan on articles  (cost=1458.97..103726.97 rows=87736 width=87) (actual time=28.387..989.805 rows=72939 loops=3)"
"                                                  Recheck Cond: (title ~~* '%data%'::text)"
"                                                  Rows Removed by Index Recheck: 391847"
"                                                  Filter: (author IS NOT NULL)"
"                                                  Rows Removed by Filter: 424"
"                                                  Heap Blocks: exact=11562 lossy=9547"
"                                                  ->  Bitmap Index Scan on idx_articles_title_trgm  (cost=0.00..1406.33 rows=211731 width=0) (actual time=36.233..36.233 rows=220300 loops=1)"
"                                                        Index Cond: (title ~~* '%data%'::text)"
"                                      ->  Subquery Scan on ""*SELECT* 2""  (cost=74.05..2266.89 rows=3011 width=56) (actual time=0.969..15.488 rows=3435 loops=1)"
"                                            ->  Parallel Bitmap Heap Scan on proceedings  (cost=74.05..2236.78 rows=3011 width=88) (actual time=0.968..15.296 rows=3435 loops=1)"
"                                                  Recheck Cond: (title ~~* '%data%'::text)"
"                                                  Rows Removed by Index Recheck: 8"
"                                                  Filter: (editor IS NOT NULL)"
"                                                  Rows Removed by Filter: 676"
"                                                  Heap Blocks: exact=810"
"                                                  ->  Bitmap Index Scan on idx_proceedings_title_trgm  (cost=0.00..72.77 rows=6900 width=0) (actual time=0.869..0.869 rows=4119 loops=1)"
"                                                        Index Cond: (title ~~* '%data%'::text)"
"Planning Time: 2.244 ms"
"Execution Time: 1532.939 ms"


******************************************
Trigram indexes help speed up searches using ILIKE '%...%' or SIMILAR TO by breaking text into small parts. This allows PostgreSQL to avoid scanning the whole table when searching for words like "data" in the title.

As we can see, the query now uses a Bitmap Index Scan instead of a Parallel Seq Scan, and the execution time is much faster.
******************************************