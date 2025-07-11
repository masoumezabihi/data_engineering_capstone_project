SELECT 
    s.country_name, 
    p.posi_to_play, 
    COUNT(*) AS goals
FROM 
    goal_details g
JOIN 
    soccer_country s ON g.team_id = s.country_id
JOIN 
    player_mast p ON g.player_id = p.player_id
GROUP BY 
    s.country_name, p.posi_to_play
HAVING 
    COUNT(*) > 0
ORDER BY 
    s.country_name, p.posi_to_play;
