SELECT DISTINCT venue_name 
FROM match_mast m
JOIN soccer_venue s 
USING(venue_id)
WHERE m.decided_by = 'P'