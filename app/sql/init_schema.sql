-- Postgresql 18
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
        CREATE TYPE user_role AS ENUM ('admin', 'manager', 'user');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'engine_type') THEN
        CREATE TYPE engine_type AS ENUM ('petrol', 'diesel', 'electric', 'hybrid');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'transmission') THEN
        CREATE TYPE transmission AS ENUM ('manual', 'automatic', 'variator', 'robotic');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'body_type') THEN
        CREATE TYPE body_type AS ENUM ('sedan', 'hatchback', 'universal', 'coupe', 'SUV', 'cabrio', 'pickup', 'minivan', 'van');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'car_status') THEN
        CREATE TYPE car_status AS ENUM ('available', 'sold', 'reserved');
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'payment_type') THEN
        CREATE TYPE payment_type AS ENUM ('cash', 'credit', 'bank_transfer');
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    surname VARCHAR(255) NOT NULL,
    patronymic VARCHAR(255),
    email VARCHAR(255) NOT NULL UNIQUE,
    phone CHAR(12) NOT NULL UNIQUE CHECK (phone ~ '^\+7\d{10}$'),
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'user'
);


CREATE TABLE IF NOT EXISTS brand (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);


CREATE TABLE IF NOT EXISTS model (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    image_path VARCHAR(255) NOT NULL, -- В формате 'audi_a4.png'
    brand_id INTEGER NOT NULL,
    year INTEGER NOT NULL CHECK (year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE)),
    engine_type engine_type NOT NULL,
    engine_volume NUMERIC(3, 1), -- В литрах, может быть NULL для электрических двигателей
    engine_power INTEGER NOT NULL, -- В л.с.
    transmission transmission NOT NULL,
    body_type body_type NOT NULL,

    FOREIGN KEY (brand_id) REFERENCES brand(id)
);


CREATE TABLE IF NOT EXISTS color (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    hex_code CHAR(6) NOT NULL CHECK (hex_code ~ '^([A-Fa-f0-9]{6})$') -- HEX код цвета в формате #RRGGBB
);


CREATE TABLE IF NOT EXISTS model_configuration (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(4096) NOT NULL,
    model_id INTEGER NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price > 0), -- Цена в рублях

    FOREIGN KEY (model_id) REFERENCES model(id)
);


CREATE TABLE IF NOT EXISTS car (
    id SERIAL PRIMARY KEY,
    model_configuration_id INTEGER NOT NULL,
    vin CHAR(17) NOT NULL UNIQUE,
    color_id INTEGER NOT NULL,
    status car_status NOT NULL DEFAULT 'available',

    FOREIGN KEY (model_configuration_id) REFERENCES model_configuration(id),
    FOREIGN KEY (color_id) REFERENCES color(id)
);


CREATE TABLE IF NOT EXISTS car_sale (
    id SERIAL PRIMARY KEY,
    car_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    sale_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    payment_type payment_type NOT NULL,

    FOREIGN KEY (car_id) REFERENCES car(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);