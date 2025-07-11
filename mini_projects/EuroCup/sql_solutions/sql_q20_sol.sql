SELECT p.player_name
FROM player_in_out pio
JOIN player_mast p ON pio.player_id = p.player_id
WHERE pio.in_out = 'I' AND pio.play_schedule = 'NT' AND pio.play_half = 1