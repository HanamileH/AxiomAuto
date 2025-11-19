-- Postgresql 18

-- ===== Код для заполнения таблиц тестовыми данными ===== --

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

-- Заполнение таблицы моделей (10 моделей)
INSERT INTO model (name, image_path, brand_id, year, engine_type, engine_volume, engine_power, transmission, body_type) VALUES
-- Audi
('A4', 'audi_a4.png', 1, 2023, 'petrol', 2.0, 190, 'automatic', 'sedan'),
('Q5', 'audi_q5.png', 1, 2023, 'diesel', 3.0, 286, 'automatic', 'SUV'),
-- BMW
('3 Series', 'bmw_3series.png', 2, 2023, 'petrol', 2.0, 184, 'automatic', 'sedan'),
('X5', 'bmw_x5.png', 2, 2023, 'hybrid', 3.0, 394, 'automatic', 'SUV'),
-- Mercedes-Benz
('C-Class', 'mercedes_cclass.png', 3, 2023, 'petrol', 2.0, 258, 'automatic', 'sedan'),
('GLE', 'mercedes_gle.png', 3, 2023, 'diesel', 2.0, 245, 'automatic', 'SUV'),
-- Toyota
('Camry', 'toyota_camry.png', 4, 2023, 'hybrid', 2.5, 218, 'automatic', 'sedan'),
('RAV4', 'toyota_rav4.png', 4, 2023, 'petrol', 2.0, 150, 'manual', 'SUV'),
-- Volkswagen
('Passat', 'vw_passat.png', 5, 2023, 'petrol', 1.5, 150, 'automatic', 'sedan'),
('Tiguan', 'vw_tiguan.png', 5, 2023, 'diesel', 2.0, 150, 'automatic', 'SUV');

-- Заполнение таблицы конфигураций моделей (15 конфигураций)
INSERT INTO model_configuration (name, description, model_id, price) VALUES
-- Audi A4 конфигурации
('Standard', 'Базовая комплектация с кожаным салоном и мультимедиа', 1, 3500000.00),
('Premium', 'Премиум комплектация с панорамной крышей и ксеноном', 1, 4200000.00),
('Sport', 'Спортивная комплектация с улучшенной подвеской', 1, 3900000.00),

-- Audi Q5 конфигурации
('Comfort', 'Комфортная комплектация для городской езды', 2, 4500000.00),
('Luxury', 'Люксовая комплектация с массой опций', 2, 5200000.00),

-- BMW 3 Series конфигурации
('Modern', 'Современная комплектация с цифровыми приборами', 3, 3800000.00),
('M Sport', 'Спортивный пакет M с аэродинамическим обвесом', 3, 4300000.00),

-- BMW X5 конфигурации
('xLine', 'Комфортная комплектация для семьи', 4, 5500000.00),
('M Package', 'Спортивный пакет с улучшенными характеристиками', 4, 6200000.00),

-- Mercedes C-Class конфигурации
('Avantgarde', 'Стильная комплектация с премиум опциями', 5, 4100000.00),
('AMG Line', 'Спортивный пакет AMG с уникальным дизайном', 5, 4700000.00),

-- Toyota Camry конфигурации
('Comfort', 'Комфортная комплектация для ежедневных поездок', 7, 2500000.00),
('Premium', 'Премиум комплектация с кожаным салоном', 7, 2900000.00),

-- Volkswagen Passat конфигурации
('Trendline', 'Базовая комплектация с необходимыми опциями', 9, 2200000.00),
('Highline', 'Топовая комплектация с полным набором опций', 9, 2800000.00),
('R-Line', 'Спортивная комплектация с элементами R-Line', 9, 2600000.00);

-- Заполнение таблицы автомобилей (20 автомобилей)
INSERT INTO car (model_configuration_id, vin, color_id, status) VALUES
-- Audi A4
(1, 'WAUZZZ8KZFA123456', 1, 'available'),
(2, 'WAUZZZ8KZFA123457', 2, 'sold'),
(3, 'WAUZZZ8KZFA123458', 3, 'available'),

-- Audi Q5
(4, 'WA1VAAF75HD123459', 4, 'reserved'),
(5, 'WA1VAAF75HD123460', 1, 'available'),

-- BMW 3 Series
(6, 'WBA8E9C58JEU12361', 2, 'available'),
(7, 'WBA8E9C58JEU12362', 5, 'sold'),

-- BMW X5
(8, '5UXCR6C56KUL12363', 3, 'available'),
(9, '5UXCR6C56KUL12364', 4, 'available'),

-- Mercedes C-Class
(10, 'WDDWF4EB3FN123465', 1, 'reserved'),
(11, 'WDDWF4EB3FN123466', 2, 'available'),

-- Toyota Camry
(12, 'JTNK4JEC0M2123467', 3, 'available'),
(13, 'JTNK4JEC0M2123468', 5, 'sold'),

-- Volkswagen Passat
(14, 'WVWZZZ3CZJE123469', 1, 'available'),
(15, 'WVWZZZ3CZJE123470', 2, 'available'),
(14, 'WVWZZZ3CZJE123471', 4, 'reserved'),
(15, 'WVWZZZ3CZJE123472', 3, 'available'),
(14, 'WVWZZZ3CZJE123473', 5, 'sold'),
(15, 'WVWZZZ3CZJE123474', 1, 'available'),
(14, 'WVWZZZ3CZJE123475', 2, 'available');