SELECT c.country_name, SUM(m.penalty_score) AS total_penalty_score
FROM match_details m
JOIN soccer_country c ON m.team_id = c.country_id
GROUP BY c.country_name
ORDER BY total_penalty_score DESC
LIMIT 1;
