import pytest


from app.services.payment_flow import PaymentMethodFactory, PaymentProcessingError, PaymentService


def test_validate_card_data_success():
    raw = {
        "cardNumber": "4111 1111-1111 1111",
        "cardHolder": "  IVAN IVANOV  ",
        "expiry": "12/34",
        "cvv": "0a7-9",
    }

    card = PaymentService.validate_card_data(raw)
    assert card.card_number == "4111111111111111"
    assert card.card_holder == "IVAN IVANOV"
    assert card.expiry == "12/34"
    assert card.cvv == "079"  # digits-only normalization


def test_validate_card_data_invalid_card_number_raises():
    raw = {
        "cardNumber": "4111 1111 1111",
        "cardHolder": "IVAN IVANOV",
        "expiry": "12/34",
        "cvv": "123",
    }

    with pytest.raises(PaymentProcessingError) as excinfo:
        PaymentService.validate_card_data(raw)

    assert excinfo.value.status_code == 400
    assert excinfo.value.public_message


def test_validate_phone_number_normalizes_and_validates():
    assert PaymentService.validate_phone_number("+7 (999) 123-45-67") == "+79991234567"

    with pytest.raises(PaymentProcessingError):
        PaymentService.validate_phone_number("not a phone")


def test_payment_method_factory_rejects_unknown_type():
    with pytest.raises(PaymentProcessingError) as excinfo:
        PaymentMethodFactory.create("crypto")

    assert excinfo.value.status_code == 400
    assert excinfo.value.public_message
