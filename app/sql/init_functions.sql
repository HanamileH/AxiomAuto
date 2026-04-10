-- Postgresql 18
-- Получение фамилии и инициалов клиента
CREATE OR REPLACE FUNCTION get_client_full_name(p_client_id INTEGER)
RETURNS VARCHAR
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_full_name VARCHAR;
BEGIN
    SELECT 
        CASE 
            WHEN patronymic IS NOT NULL AND patronymic != '' THEN
                surname || ' ' || LEFT(name, 1) || '.' || LEFT(patronymic, 1) || '.'
            ELSE
                surname || ' ' || LEFT(name, 1) || '.'
        END
    INTO v_full_name
    FROM client
    WHERE id = p_client_id;

    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    RETURN v_full_name;
END;
$$;

-- Проверка доступности автомобиля для продажи
CREATE OR REPLACE FUNCTION is_car_available_for_sale(p_car_id INTEGER)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_is_sold BOOLEAN;
BEGIN
    -- Проверяем, существует ли автомобиль
    IF NOT EXISTS (SELECT 1 FROM car WHERE id = p_car_id) THEN
        RETURN FALSE;
    END IF;

    -- Проверяем, есть ли запись в sale
    SELECT EXISTS(
        SELECT 1 FROM sale WHERE car_id = p_car_id
    ) INTO v_is_sold;

    RETURN NOT v_is_sold;
END;
$$;
