SELECT p.*, pos.position_desc
FROM player_mast p
JOIN playing_position pos ON p.posi_to_play = pos.position_id
JOIN soccer_country s ON p.team_id = s.country_id
WHERE s.country_name = 'England'
  AND p.playing_club = 'Liverpool'
