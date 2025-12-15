-- Postgresql 18
DO $$
BEGIN
    -- Роль пользователя
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('admin', 'manager', 'user');
    END IF;

    -- Тип двигателя
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'engine_type') THEN
        CREATE TYPE engine_type AS ENUM ('petrol', 'diesel', 'electric', 'hybrid');
    END IF;

    -- Тип коробки передач
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transmission') THEN
        CREATE TYPE transmission AS ENUM ('manual', 'automatic', 'variator', 'robotic');
    END IF;

    -- Тип оплаты
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_type') THEN
        CREATE TYPE payment_type AS ENUM ('cash', 'bank_online', 'bank_terminal');
    END IF;

    -- Статус оплаты
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_status') THEN
        CREATE TYPE payment_status AS ENUM ('success', 'fail', 'pending');
    END IF;
END
$$;

-- Клиенты
CREATE TABLE IF NOT EXISTS client (
    id SERIAL PRIMARY KEY,
    -- ФИО клиента
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    patronymic VARCHAR(255)
);

-- Пользователи системы (декорптация от клиентов)
CREATE TABLE IF NOT EXISTS user (
    client_id INTEGER NOT NULL PRIMARY KEY,
    role user_role NOT NULL DEFAULT 'user',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,

    FOREIGN KEY (client_id) REFERENCES client(id) ON DELETE CASCADE
);


-- Производители автомобилей
CREATE TABLE IF NOT EXISTS brand (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Типы кузова
CREATE TABLE IF NOT EXISTS body_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Модели автомобиля
CREATE TABLE IF NOT EXISTS model (
    id SERIAL PRIMARY KEY,
    -- Общие данные
    name VARCHAR(255) NOT NULL,
    description VARCHAR(4096) NOT NULL,
    image_path VARCHAR(255) NOT NULL, -- В формате 'audi_a4.png'
    brand_id INTEGER NOT NULL,
    price INTEGER NOT NULL CHECK (price > 0), -- Цена в рублях без копеек
    -- Характеристики
    year INTEGER NOT NULL CHECK (year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE)),
    engine_type engine_type NOT NULL,
    engine_volume NUMERIC(3, 1), -- В литрах, NULL для электромобилей
    engine_power INTEGER NOT NULL, -- В л.с.
    transmission transmission NOT NULL,
    body_type INTEGER NOT NULL,

    FOREIGN KEY (brand_id) REFERENCES brand(id),
    FOREIGN KEY (body_type) REFERENCES body_type(id)

);


-- Цвета автомобилей
CREATE TABLE IF NOT EXISTS color (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    hex_code CHAR(6) NOT NULL CHECK (hex_code ~ '^([A-Fa-f0-9]{6})$') -- HEX код цвета в формате #RRGGBB
);


-- Экземпляр автомобиля
CREATE TABLE IF NOT EXISTS car (
    id SERIAL PRIMARY KEY,
    model_id INTEGER NOT NULL,
    vin CHAR(17) NOT NULL UNIQUE,
    color_id INTEGER NOT NULL,

    FOREIGN KEY (model_id) REFERENCES model(id),
    FOREIGN KEY (color_id) REFERENCES color(id)
);


-- Транзакция оплаты
CREATE TABLE IF NOT EXISTS payment (
    id SERIAL PRIMARY KEY,
    type payment_type NOT NULL, -- Тип оплаты (наличные, онлайн, терминал)
    status payment_status NOT NULL, -- Статус оплаты (успешно, неуспешно, ожидание)
    amount INTEGER NOT NULL CHECK (amount > 0), -- Сумма в рублях на момент оплаты
    datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    transaction_id VARCHAR(64) UNIQUE, -- ID транзакции (NULL если оплата наличными)
    bank_account CHAR(4) -- Последние 4 цифры банковского счёта (NULL если оплата наличными)
);

-- Акт купли-продажи
CREATE TABLE IF NOT EXISTS sale (
    id SERIAL PRIMARY KEY,
    car_id INTEGER NOT NULL, -- Экземпляр купленного автомобиля
    client_id INTEGER NOT NULL, -- Клиент, заказавший автомобиль
    personal_id INTEGER, -- Ответственный менеджер (NULL если заказ онлайн)
    payment_id INTEGER NOT NULL UNIQUE, -- Чек оплаты
    contact_number VARCHAR(20) NOT NULL, -- Номер телефона клиента

    FOREIGN KEY (car_id) REFERENCES car(id),
    FOREIGN KEY (client_id) REFERENCES client(id),
    FOREIGN KEY (personal_id) REFERENCES user(id),
    FOREIGN KEY (payment_id) REFERENCES payment(id)
);

-- Акт выдачи автомобиля
CREATE TABLE IF NOT EXISTS delivery (
    id SERIAL PRIMARY KEY,
    sale_id INTEGER NOT NULL UNIQUE,
    personal_id INTEGER NOT NULL, -- Ответственный менеджер
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    FOREIGN KEY (sale_id) REFERENCES sale(id),

    FOREIGN KEY (personal_id) REFERENCES user(id)
);