SELECT COUNT(DISTINCT mc.player_captain) AS goal_keeper_captains
FROM match_captain mc
JOIN match_details md ON mc.player_captain = md.player_gk;
