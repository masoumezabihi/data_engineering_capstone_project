SELECT r.referee_name, s.venue_name, COUNT(*) AS match_count
FROM match_mast m
JOIN soccer_venue s ON s.venue_id = m.venue_id
JOIN referee_mast r ON r.referee_id = m.referee_id
GROUP BY s.venue_name, r.referee_name
ORDER BY match_count DESC