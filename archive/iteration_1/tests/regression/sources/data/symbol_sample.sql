-- Sample SQL file for symbol extraction regression tests.

WITH active_users AS (
    SELECT id, name
    FROM users
    WHERE active = 1
),
order_totals AS (
    SELECT user_id, SUM(amount) AS total
    FROM orders
    GROUP BY user_id
)
SELECT u.name, o.total
FROM active_users u
JOIN order_totals o ON u.id = o.user_id;
