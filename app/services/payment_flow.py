import re
import time
from dataclasses import dataclass
from psycopg2.extras import RealDictCursor
from app.db.connection import db


class PaymentProcessingError(Exception):
    def __init__(self, message, public_message=None, status_code=400):
        super().__init__(message)
        self.message = message
        self.public_message = public_message or message
        self.status_code = status_code


@dataclass
class BankCardData:
    card_number: str
    card_holder: str
    expiry: str
    cvv: str


@dataclass
class BankPaymentResult:
    success: bool
    transaction_id: str
    message: str
    bank_account_last4: str


class MockBankGateway:
    CARD_RESPONSES = {
        "0": (True, "Платеж успешно подтвержден."),
        "1": (False, "Недостаточно средств на карте."),
        "2": (True, "Платеж успешно подтвержден."),
        "3": (False, "Карта заблокирована банком."),
        "4": (True, "Платеж успешно подтвержден."),
        "5": (False, "Операция отклонена банком-эмитентом."),
        "6": (True, "Платеж успешно подтвержден."),
        "7": (False, "Требуется дополнительная проверка карты."),
        "8": (True, "Платеж успешно подтвержден."),
        "9": (False, "Недостаточно средств на карте."),
    }

    def process(self, card_data):
        time.sleep(1.2)

        digits = PaymentService.normalize_card_number(card_data.card_number)
        last_digit = digits[-1]
        is_success, message = self.CARD_RESPONSES.get(
            last_digit, (False, "Не удалось обработать карту.")
        )

        return BankPaymentResult(
            success=is_success,
            transaction_id=f"MOCK-{int(time.time() * 1000)}-{last_digit}",
            message=message,
            bank_account_last4=digits[-4:],
        )


class PaymentMethod:
    payment_type = None

    def process(self, order_context, payment_context):
        raise NotImplementedError


class OnlineBankCardPaymentMethod(PaymentMethod):
    payment_type = "bank_online"

    def __init__(self, bank_gateway=None):
        self.bank_gateway = bank_gateway or MockBankGateway()

    def process(self, order_context, payment_context):
        return self.bank_gateway.process(payment_context["card_data"])


class PaymentMethodFactory:
    _methods = {
        "bank_online": OnlineBankCardPaymentMethod,
    }

    @classmethod
    def create(cls, payment_type):
        method_class = cls._methods.get(payment_type)
        if not method_class:
            raise PaymentProcessingError(
                f"unsupported payment type: {payment_type}",
                public_message="Выбранный способ оплаты пока не поддерживается.",
                status_code=400,
            )

        return method_class()


class PaymentService:
    PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")
    EXPIRY_PATTERN = re.compile(r"^(0[1-9]|1[0-2])\/\d{2}$")

    @staticmethod
    def normalize_card_number(card_number):
        return re.sub(r"\D", "", (card_number or ""))

    @staticmethod
    def normalize_phone(phone_number):
        return re.sub(r"[^\d+]", "", (phone_number or ""))

    @classmethod
    def validate_card_data(cls, raw_card_data):
        card_number = cls.normalize_card_number(raw_card_data.get("cardNumber"))
        card_holder = (raw_card_data.get("cardHolder") or "").strip()
        expiry = (raw_card_data.get("expiry") or "").strip()
        cvv = re.sub(r"\D", "", (raw_card_data.get("cvv") or ""))

        if len(card_number) != 16:
            raise PaymentProcessingError(
                "invalid card number",
                public_message="Введите корректный номер карты из 16 цифр.",
            )

        if len(card_holder) < 3:
            raise PaymentProcessingError(
                "invalid card holder",
                public_message="Укажите имя держателя карты.",
            )

        if not cls.EXPIRY_PATTERN.match(expiry):
            raise PaymentProcessingError(
                "invalid expiry",
                public_message="Укажите срок действия карты в формате MM/YY.",
            )

        if len(cvv) != 3:
            raise PaymentProcessingError(
                "invalid cvv",
                public_message="CVV должен содержать 3 цифры.",
            )

        return BankCardData(
            card_number=card_number,
            card_holder=card_holder,
            expiry=expiry,
            cvv=cvv,
        )

    @classmethod
    def validate_phone_number(cls, phone_number):
        normalized_phone = cls.normalize_phone(phone_number)

        if not cls.PHONE_PATTERN.match(normalized_phone):
            raise PaymentProcessingError(
                "invalid phone number",
                public_message="Укажите корректный номер телефона для связи.",
            )

        return normalized_phone

    @staticmethod
    def _reserve_order(user_id, model_id, color_id, phone_number, payment_type):
        with db.get_connection() as connection:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            try:
                cursor.execute(
                    """
                    SELECT
                        c.id AS car_id,
                        m.price AS amount,
                        b.name AS brand,
                        m.name AS model,
                        clr.name AS color
                    FROM car c
                    JOIN model m ON m.id = c.model_id
                    JOIN brand b ON b.id = m.brand_id
                    JOIN color clr ON clr.id = c.color_id
                    WHERE c.model_id = %s
                    AND c.color_id = %s
                    AND is_car_available_for_sale(c.id)
                    ORDER BY c.id
                    FOR UPDATE SKIP LOCKED
                    LIMIT 1;
                    """,
                    (model_id, color_id),
                )
                car_row = cursor.fetchone()

                if not car_row:
                    raise PaymentProcessingError(
                        "car not available",
                        public_message="Свободный автомобиль в выбранной комплектации не найден.",
                        status_code=409,
                    )

                cursor.execute(
                    """
                    INSERT INTO car_order (car_id, client_id, contact_number, status)
                    VALUES (%s, %s, %s, 'awaiting_payment')
                    RETURNING id;
                    """,
                    (car_row["car_id"], user_id, phone_number),
                )
                order_id = cursor.fetchone()["id"]

                cursor.execute(
                    """
                    INSERT INTO payment (order_id, type, status, amount, bank_account)
                    VALUES (%s, %s, 'pending', %s, NULL)
                    RETURNING id;
                    """,
                    (order_id, payment_type, car_row["amount"]),
                )
                payment_id = cursor.fetchone()["id"]

                connection.commit()

                return {
                    "order_id": order_id,
                    "payment_id": payment_id,
                    "car_id": car_row["car_id"],
                    "amount": car_row["amount"],
                    "brand": car_row["brand"],
                    "model": car_row["model"],
                    "color": car_row["color"],
                }
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()

    @classmethod
    def _finalize_payment(cls, reservation, bank_result):
        with db.get_connection() as connection:
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            try:
                payment_status = "success" if bank_result.success else "fail"
                order_status = "completed" if bank_result.success else "cancelled"

                cursor.execute(
                    """
                    UPDATE payment
                    SET
                        status = %s,
                        transaction_id = %s,
                        bank_account = %s,
                        datetime = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (
                        payment_status,
                        bank_result.transaction_id,
                        bank_result.bank_account_last4,
                        reservation["payment_id"],
                    ),
                )

                cursor.execute(
                    """
                    UPDATE car_order
                    SET status = %s
                    WHERE id = %s;
                    """,
                    (order_status, reservation["order_id"]),
                )

                if bank_result.success:
                    cursor.execute(
                        """
                        INSERT INTO sale (order_id, personal_id)
                        VALUES (%s, %s)
                        ON CONFLICT (order_id) DO NOTHING;
                        """,
                        (reservation["order_id"], None),
                    )

                connection.commit()
            except Exception:
                connection.rollback()
                raise
            finally:
                cursor.close()

    @classmethod
    def process_order(
        cls,
        user_id,
        model_id,
        color_id,
        phone_number,
        payment_type,
        payment_payload,
    ):
        normalized_phone = cls.validate_phone_number(phone_number)
        payment_method = PaymentMethodFactory.create(payment_type)

        payment_context = {}
        if payment_type == "bank_online":
            payment_context["card_data"] = cls.validate_card_data(payment_payload)

        reservation = cls._reserve_order(
            user_id=user_id,
            model_id=model_id,
            color_id=color_id,
            phone_number=normalized_phone,
            payment_type=payment_type,
        )

        try:
            bank_result = payment_method.process(reservation, payment_context)
        except PaymentProcessingError as exc:
            bank_result = BankPaymentResult(
                success=False,
                transaction_id=f"MOCK-FAIL-{reservation['payment_id']}",
                message=exc.public_message,
                bank_account_last4="",
            )
        except Exception:
            bank_result = BankPaymentResult(
                success=False,
                transaction_id=f"MOCK-FAIL-{reservation['payment_id']}",
                message="Не удалось получить ответ от платежного сервиса.",
                bank_account_last4="",
            )

        cls._finalize_payment(reservation, bank_result)

        is_success = bank_result.success
        result_title = "Оплата прошла успешно" if is_success else "Оплата не выполнена"
        result_message = (
            f"Заказ на {reservation['brand']} {reservation['model']} оформлен. "
            f"Мы свяжемся с вами по номеру {normalized_phone}."
            if is_success
            else bank_result.message
        )

        return {
            "success": is_success,
            "order_id": reservation["order_id"],
            "payment_id": reservation["payment_id"],
            "status": "success" if is_success else "error",
            "title": result_title,
            "message": result_message,
            "transaction_id": bank_result.transaction_id,
        }
