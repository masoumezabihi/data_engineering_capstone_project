SELECT p.player_name, COUNT(*) AS golas_count
FROM goal_details g
JOIN player_mast p USING (player_id)
JOIN playing_position pl ON p.posi_to_play = pl.position_id
WHERE pl.position_desc = 'Defenders'
GROUP BY p.player_name
ORDER BY golas_count DESC;