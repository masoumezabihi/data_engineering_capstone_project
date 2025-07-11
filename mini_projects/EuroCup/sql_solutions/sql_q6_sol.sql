SELECT COUNT(*)
FROM (
    SELECT DISTINCT t1.match_no
    FROM match_details t1
    JOIN match_details t2
        ON t1.match_no = t2.match_no
       AND t1.team_id <> t2.team_id
    JOIN match_mast mm
        ON t1.match_no = mm.match_no
    WHERE ABS(t1.goal_score - t2.goal_score) = 1
      AND mm.decided_by = 'N'
) AS mch;
