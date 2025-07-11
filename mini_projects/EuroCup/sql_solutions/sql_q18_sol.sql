SELECT MAX(count) AS max_count
FROM (
    SELECT match_no, COUNT(*) AS count
    FROM player_booked
    GROUP BY match_no
) p1;
