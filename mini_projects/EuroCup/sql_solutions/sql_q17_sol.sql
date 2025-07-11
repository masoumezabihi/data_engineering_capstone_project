SELECT s.country_name, COUNT(*) AS referees_count
FROM asst_referee_mast a
JOIN soccer_country s ON s.country_id = a.country_id
GROUP BY s.country_name 
ORDER BY referees_count DESC
LIMIT 1