-- Предаставление статусов автомобиля
CREATE OR REPLACE VIEW car_status_view AS
SELECT 
    c.id AS car_id,
    
    -- Статус автомобиля
    CASE 
        -- Автомобиль продан и доставлен
        WHEN d.id IS NOT NULL THEN 'delivered'
        -- Автомобиль продан, но не доставлен
        WHEN s.id IS NOT NULL AND p.status = 'success' THEN 'paid'
        -- Заказ на автомобиль есть, но оплата ожидается
        WHEN s.id IS NOT NULL AND (p.status = 'pending' OR p.status IS NULL) THEN 'payment_pending'
        -- Автомобиль доступен для продажи
        ELSE 'available'
    END AS status

FROM car c
INNER JOIN model m ON c.model_id = m.id
INNER JOIN brand b ON m.brand_id = b.id
INNER JOIN color col ON c.color_id = col.id
LEFT JOIN sale s ON c.id = s.car_id
LEFT JOIN payment p ON s.payment_id = p.id
LEFT JOIN delivery d ON s.id = d.sale_id
LEFT JOIN client cl ON s.client_id = cl.id;

-- Статистика продаж по маркам
CREATE OR REPLACE VIEW brand_sales_view AS
SELECT
    b.name AS brand,
    COUNT(CASE WHEN cs.status IN ('paid', 'delivered') THEN cs.car_id END) AS count
FROM brand b
LEFT JOIN model m ON m.brand_id = b.id
LEFT JOIN car c ON c.model_id = m.id
LEFT JOIN car_status_view cs ON cs.car_id = c.id
GROUP BY b.name;

SELECT * FROM brand_sales_view;

-- Статистика продаж по цветам
CREATE OR REPLACE VIEW color_sales_view AS
SELECT
    COUNT(CASE WHEN cs.status IN ('paid', 'delivered') THEN cs.car_id END) AS count,
    col.name AS color
FROM color col
LEFT JOIN car c ON c.color_id = col.id
LEFT JOIN car_status_view cs ON cs.car_id = c.id
GROUP BY col.name;

-- Статистика продаж по типам кузовов
CREATE OR REPLACE VIEW body_type_sales_view AS
SELECT
    COUNT(CASE WHEN cs.status IN ('paid', 'delivered') THEN cs.car_id END) AS count,
    bt.name AS body_type
FROM body_type bt
LEFT JOIN model m ON m.body_type = bt.id
LEFT JOIN car c ON c.model_id = m.id
LEFT JOIN car_status_view cs ON cs.car_id = c.id
GROUP BY bt.name;

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
