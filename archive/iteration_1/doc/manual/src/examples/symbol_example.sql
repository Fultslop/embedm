-- Example SQL file for symbol extraction.

WITH active_users AS (
    SELECT id, name, email
    FROM users
    WHERE active = 1
),
monthly_totals AS (
    SELECT user_id, SUM(amount) AS total
    FROM orders
    WHERE order_date >= '2024-01-01'
    GROUP BY user_id
)
SELECT u.name, u.email, m.total
FROM active_users u
JOIN monthly_totals m ON u.id = m.user_id;
