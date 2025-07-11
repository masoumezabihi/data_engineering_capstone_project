SELECT DISTINCT p.player_name, p.jersey_no , p.playing_club 
FROM match_details m
JOIN soccer_country s ON m.team_id = s.country_id
JOIN player_mast p ON m.player_gk = p.player_id 
WHERE s.country_name = 'England'
