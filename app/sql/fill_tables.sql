-- Postgresql 18

-- ===== Код для заполнения таблиц тестовыми данными ===== --
-- Заполнение таблицы типов кузова
INSERT INTO body_type (name) VALUES
('sedan'),
('SUV'),
('hatchback'),
('coupe'),
('convertible'),
('wagon');

-- Заполнение таблицы брендов (5 марок)
INSERT INTO brand (name) VALUES
('Audi'),
('BMW'),
('Mercedes-Benz'),
('Toyota'),
('Volkswagen');

-- Заполнение таблицы цветов (5 цветов)
INSERT INTO color (name, hex_code) VALUES
('Черный', '000000'),
('Белый', 'FFFFFF'),
('Серебристый', 'C0C0C0'),
('Красный', 'FF0000'),
('Синий', '0000FF');

-- Заполнение таблицы моделей автомобилей (10 моделей)
INSERT INTO model (
   name, 
   description, 
   image_path, 
   brand_id, 
   price, 
   year, 
   engine_type, 
   engine_volume, 
   engine_power, 
   transmission, 
   body_type
) VALUES
-- Audi (id: 1)
('A4', 'Современный седан премиум-класса с передовыми технологиями', 'audi_a4.png', 1, 3500000, 2023, 'petrol', 2.0, 190, 'automatic', 1),
('Q5', 'Вместительный кроссовер с полным приводом и комфортным салоном', 'audi_q5.png', 1, 4500000, 2023, 'diesel', 3.0, 286, 'automatic', 2),

-- BMW (id: 2)
('3 Series', 'Легендарный спортивный седан с отличной управляемостью', 'bmw_3series.png', 2, 3800000, 2023, 'petrol', 2.0, 184, 'automatic', 1),
('X5', 'Люксовый внедорожник с гибридной силовой установкой', 'bmw_x5.png', 2, 5500000, 2023, 'hybrid', 3.0, 394, 'automatic', 2),

-- Mercedes-Benz (id: 3)
('C-Class', 'Элегантный бизнес-седан с премиальным интерьером', 'mercedes_cclass.png', 3, 4100000, 2023, 'petrol', 2.0, 258, 'automatic', 1),
('GLE', 'Роскошный внедорожник для города и бездорожья', 'mercedes_gle.png', 3, 5200000, 2023, 'diesel', 2.0, 245, 'automatic', 2),

-- Toyota (id: 4)
('Camry', 'Надежный семейный седан с гибридной установкой', 'toyota_camry.png', 4, 2500000, 2023, 'hybrid', 2.5, 218, 'automatic', 1),
('RAV4', 'Популярный кроссовер с отличной проходимостью', 'toyota_rav4.png', 4, 3200000, 2023, 'petrol', 2.0, 150, 'manual', 2),

-- Volkswagen (id: 5)
('Passat', 'Практичный бизнес-седан немецкого качества', 'vw_passat.png', 5, 2200000, 2023, 'petrol', 1.5, 150, 'automatic', 1),
('Tiguan', 'Стильный городской кроссовер для всей семьи', 'vw_tiguan.png', 5, 2800000, 2023, 'diesel', 2.0, 150, 'automatic', 2);

-- Заполнение таблицы автомобилей (20 автомобилей)
INSERT INTO car (model_id, vin, color_id) VALUES
-- Audi A4 (model_id: 1)
(1, 'WAUZZZ8KZFA123456', 1),
(1, 'WAUZZZ8KZFA123457', 2),
(1, 'WAUZZZ8KZFA123458', 3),

-- Audi Q5 (model_id: 2)
(2, 'WA1VAAF75HD123459', 4),
(2, 'WA1VAAF75HD123460', 1),

-- BMW 3 Series (model_id: 3)
(3, 'WBA8E9C58JEU12361', 2),
(3, 'WBA8E9C58JEU12362', 5),

-- BMW X5 (model_id: 4)
(4, '5UXCR6C56KUL12363', 3),
(4, '5UXCR6C56KUL12364', 4),

-- Mercedes C-Class (model_id: 5)
(5, 'WDDWF4EB3FN123465', 1),
(5, 'WDDWF4EB3FN123466', 2),

-- Toyota Camry (model_id: 7)
(7, 'JTNK4JEC0M2123467', 3),
(7, 'JTNK4JEC0M2123468', 5),

-- Volkswagen Passat (model_id: 9)
(9, 'WVWZZZ3CZJE123469', 1),
(9, 'WVWZZZ3CZJE123470', 2),
(9, 'WVWZZZ3CZJE123471', 4),
(9, 'WVWZZZ3CZJE123472', 3),
(9, 'WVWZZZ3CZJE123473', 5),
(9, 'WVWZZZ3CZJE123474', 1),
(9, 'WVWZZZ3CZJE123475', 2);