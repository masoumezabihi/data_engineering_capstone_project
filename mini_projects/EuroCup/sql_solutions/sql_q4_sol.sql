SELECT play_schedule , COUNT(*) AS num_substitutions
FROM player_in_out
GROUP BY play_schedule 
ORDER BY num_substitutions DESC