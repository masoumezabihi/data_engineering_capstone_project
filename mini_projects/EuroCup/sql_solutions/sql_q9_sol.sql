SELECT DISTINCT p.player_name AS germany_group_stage_goal_keeper , p.jersey_no 
FROM match_details m
JOIN soccer_country s ON m.team_id = s.country_id
JOIN player_mast p ON m.player_gk = p.player_id
WHERE m.play_stage = 'G' AND s.country_name = 'Germany'