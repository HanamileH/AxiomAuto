-- PostgreSQL 18

-- Триггер для проверки формата VIN
CREATE OR REPLACE FUNCTION check_vin_format()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Проверка длины
    IF LENGTH(NEW.vin) != 17 THEN
        RAISE EXCEPTION 'VIN должен содержать ровно 17 символов. Передано: % символов', LENGTH(NEW.vin);
    END IF;

    -- Проверка на заглавные буквы (приведение к верхнему регистру)
    NEW.vin := UPPER(NEW.vin);

    -- Проверка на запрещённые символы (I, O, Q запрещены в VIN)
    IF NEW.vin ~ '[IOQ]' THEN
        RAISE EXCEPTION 'VIN содержит запрещённые символы: I, O или Q';
    END IF;

    -- Проверка на допустимые символы (только латиница и цифры)
    IF NEW.vin !~ '^[A-HJ-NPR-Z0-9]{17}$' THEN
        RAISE EXCEPTION 'VIN содержит недопустимые символы. Разрешены только латинские буквы (кроме I,O,Q) и цифры';
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_check_vin
    BEFORE INSERT OR UPDATE OF vin ON car
    FOR EACH ROW
    EXECUTE FUNCTION check_vin_format();


-- Триггер для предотвращения изменения проданного автомобиля
CREATE OR REPLACE FUNCTION prevent_sold_car_edit()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Для UPDATE
    IF TG_OP = 'UPDATE' THEN
        -- Проверяем, продан ли автомобиль
        IF EXISTS (SELECT 1 FROM sale WHERE car_id = OLD.id) THEN
            -- Запрещаем изменение VIN
            IF NEW.vin IS DISTINCT FROM OLD.vin THEN
                RAISE EXCEPTION 'Невозможно изменить VIN проданного автомобиля (id: %)', OLD.id;
            END IF;
            
            -- Запрещаем изменение цвета
            IF NEW.color_id IS DISTINCT FROM OLD.color_id THEN
                RAISE EXCEPTION 'Невозможно изменить цвет проданного автомобиля (id: %)', OLD.id;
            END IF;

            -- Запрещаем изменение модели
            IF NEW.model_id IS DISTINCT FROM OLD.model_id THEN
                RAISE EXCEPTION 'Невозможно изменить модель проданного автомобиля (id: %)', OLD.id;
            END IF;
        END IF;
        
        RETURN NEW;
    
    -- Для DELETE
    ELSIF TG_OP = 'DELETE' THEN
        IF EXISTS (SELECT 1 FROM sale WHERE car_id = OLD.id) THEN
            RAISE EXCEPTION 'Невозможно удалить проданный автомобиль (id: %)', OLD.id;
        END IF;
        
        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$;

CREATE OR REPLACE TRIGGER trg_prevent_sold_car_edit
    BEFORE UPDATE OR DELETE ON car
    FOR EACH ROW
    EXECUTE FUNCTION prevent_sold_car_edit();


-- Триггер для проверки объёма двигателя в зависимости от типа
CREATE OR REPLACE FUNCTION validate_engine_volume()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    -- Для электромобилей объём двигателя должен быть NULL
    IF NEW.engine_type = 'electric' THEN
        IF NEW.engine_volume IS NOT NULL THEN
            RAISE EXCEPTION 'Для электромобиля объём двигателя должен быть NULL';
        END IF;
    
    -- Для остальных типов объём двигателя обязателен
    ELSE
        IF NEW.engine_volume IS NULL THEN
            RAISE EXCEPTION 'Для типа двигателя % объём двигателя обязателен', NEW.engine_type;
        END IF;

        -- Проверка диапазона объёма двигателя
        IF NEW.engine_volume <= 0 OR NEW.engine_volume > 10.0 THEN
            RAISE EXCEPTION 'Объём двигателя должен быть от 0.1 до 10.0 литров. Указано: %', NEW.engine_volume;
        END IF;
    END IF;

    RETURN NEW;
END;
$$;

CREATE OR REPLACE TRIGGER trg_validate_engine_volume
    BEFORE INSERT OR UPDATE OF engine_type, engine_volume ON model
    FOR EACH ROW
    EXECUTE FUNCTION validate_engine_volume();