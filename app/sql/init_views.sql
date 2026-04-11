-- PostgreSQL 18
-- Статистика продаж по маркам
CREATE OR REPLACE VIEW brand_sales_view AS
SELECT
    b.name AS brand,
    COUNT(CASE WHEN is_car_sold(c.id) THEN c.id END) AS count
FROM brand b
LEFT JOIN model m ON m.brand_id = b.id
LEFT JOIN car c ON c.model_id = m.id
GROUP BY b.name;

SELECT * FROM brand_sales_view;

-- Статистика продаж по цветам
CREATE OR REPLACE VIEW color_sales_view AS
SELECT
    col.name AS color,
    COUNT(CASE WHEN is_car_sold(c.id) THEN c.id END) AS count
FROM color col
LEFT JOIN car c ON c.color_id = col.id
GROUP BY col.name;

SELECT * FROM color_sales_view;

-- Статистика продаж по типам кузовов
CREATE OR REPLACE VIEW body_type_sales_view AS
SELECT
    bt.name AS body_type,
    COUNT(CASE WHEN is_car_sold(c.id) THEN c.id END) AS count
FROM body_type bt
LEFT JOIN model m ON m.body_type = bt.id
LEFT JOIN car c ON c.model_id = m.id
GROUP BY bt.name;

SELECT * FROM body_type_sales_view;

-- Статистика эффективности менеджеров
CREATE OR REPLACE VIEW manager_perfomance_view AS
SELECT
	c.name AS name,
	c.surname AS surname,
	c.patronymic AS patronymic,
	COUNT(DISTINCT s.id) AS sales,
	COUNT(DISTINCT d.id) AS deliveries
FROM users u
JOIN client c ON u.id = c.id
LEFT JOIN sale s ON s.personal_id = u.id
LEFT JOIN delivery d ON d.personal_id = u.id
WHERE u.role = 'manager'
GROUP BY name, surname, patronymic;

SELECT * FROM manager_perfomance_view;
