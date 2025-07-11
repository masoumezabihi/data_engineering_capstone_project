WITH booking_counts AS (
    SELECT 
        r.referee_name,
        COUNT(*) AS total_bookings
    FROM player_booked pb
    JOIN match_mast m ON pb.match_no = m.match_no
    JOIN referee_mast r ON m.referee_id = r.referee_id
    GROUP BY r.referee_name
),
max_booking AS (
    SELECT MAX(total_bookings) AS max_value FROM booking_counts
)
SELECT b.referee_name, b.total_bookings
FROM booking_counts b
JOIN max_booking m ON b.total_bookings = m.max_value;
