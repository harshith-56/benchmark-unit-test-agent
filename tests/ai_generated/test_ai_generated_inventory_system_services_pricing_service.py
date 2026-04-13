from inventory_system.services.pricing_service import PricingService
from inventory_system.services.pricing_service import PricingService, InvalidDiscountError
from unittest.mock import MagicMock
from unittest.mock import patch
from unittest.mock import patch, MagicMock
import pytest

# AI_TEST_AGENT_START function=PricingService.calculate_total
class DummyProduct:
    def __init__(self, price):
        self.price = price

class DummyItem:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity

class DummyOrder:
    def __init__(self, items):
        self.items = items

def test_calculate_total_multiple_items_sum_and_format(monkeypatch):
    service = PricingService()
    service._inventory = MagicMock()
    service._inventory.get_product.side_effect = [
        DummyProduct(price=10.0),
        DummyProduct(price=5.5),
        DummyProduct(price=0.0),
    ]

    def fake_format_currency(amount):
        return f"${amount:.2f}"

    monkeypatch.setattr(service, "format_currency", fake_format_currency)

    order = DummyOrder(
        items=[
            DummyItem(product_id=1, quantity=2),
            DummyItem(product_id=2, quantity=3),
            DummyItem(product_id=3, quantity=1),
        ]
    )

    result = service.calculate_total(order)
    expected_total = 10.0 * 2 + 5.5 * 3 + 0.0 * 1
    assert result == f"${expected_total:.2f}"
    assert service._inventory.get_product.call_count == 3
    service._inventory.get_product.assert_any_call(1)
    service._inventory.get_product.assert_any_call(2)
    service._inventory.get_product.assert_any_call(3)

def test_calculate_total_empty_order_returns_zero(monkeypatch):
    service = PricingService()
    service._inventory = MagicMock()

    def fake_format_currency(amount):
        return f"${amount:.2f}"

    monkeypatch.setattr(service, "format_currency", fake_format_currency)

    order = DummyOrder(items=[])
    result = service.calculate_total(order)
    assert result == "$0.00"
    service._inventory.get_product.assert_not_called()

def test_calculate_total_product_price_zero(monkeypatch):
    service = PricingService()
    service._inventory = MagicMock()
    service._inventory.get_product.return_value = DummyProduct(price=0.0)

    def fake_format_currency(amount):
        return f"${amount:.2f}"

    monkeypatch.setattr(service, "format_currency", fake_format_currency)

    order = DummyOrder(items=[DummyItem(product_id=1, quantity=10)])
    result = service.calculate_total(order)
    assert result == "$0.00"
    service._inventory.get_product.assert_called_once_with(1)

def test_calculate_total_negative_quantity(monkeypatch):
    service = PricingService()
    service._inventory = MagicMock()
    service._inventory.get_product.return_value = DummyProduct(price=10.0)

    def fake_format_currency(amount):
        return f"${amount:.2f}"

    monkeypatch.setattr(service, "format_currency", fake_format_currency)

    order = DummyOrder(items=[DummyItem(product_id=1, quantity=-5)])
    result = service.calculate_total(order)
    expected_total = 10.0 * -5
    assert result == f"${expected_total:.2f}"
    service._inventory.get_product.assert_called_once_with(1)

def test_calculate_total_product_price_negative(monkeypatch):
    service = PricingService()
    service._inventory = MagicMock()
    service._inventory.get_product.return_value = DummyProduct(price=-20.0)

    def fake_format_currency(amount):
        return f"${amount:.2f}"

    monkeypatch.setattr(service, "format_currency", fake_format_currency)

    order = DummyOrder(items=[DummyItem(product_id=1, quantity=3)])
    result = service.calculate_total(order)
    expected_total = -20.0 * 3
    assert result == f"${expected_total:.2f}"
    service._inventory.get_product.assert_called_once_with(1)

def test_calculate_total_get_product_raises(monkeypatch):
    service = PricingService()
    service._inventory = MagicMock()
    service._inventory.get_product.side_effect = KeyError("Product not found")

    def fake_format_currency(amount):
        return f"${amount:.2f}"

    monkeypatch.setattr(service, "format_currency", fake_format_currency)

    order = DummyOrder(items=[DummyItem(product_id=999, quantity=1)])

    with pytest.raises(KeyError, match="Product not found"):
        service.calculate_total(order)
    service._inventory.get_product.assert_called_once_with(999)

def test_calculate_total_item_with_none_product_id(monkeypatch):
    service = PricingService()
    service._inventory = MagicMock()
    service._inventory.get_product.return_value = DummyProduct(price=10.0)

    def fake_format_currency(amount):
        return f"${amount:.2f}"

    monkeypatch.setattr(service, "format_currency", fake_format_currency)

    order = DummyOrder(items=[DummyItem(product_id=None, quantity=1)])

    with pytest.raises(TypeError):
        service.calculate_total(order)
    service._inventory.get_product.assert_called_once_with(None)

def test_calculate_total_item_with_zero_quantity(monkeypatch):
    service = PricingService()
    service._inventory = MagicMock()
    service._inventory.get_product.return_value = DummyProduct(price=15.0)

    def fake_format_currency(amount):
        return f"${amount:.2f}"

    monkeypatch.setattr(service, "format_currency", fake_format_currency)

    order = DummyOrder(items=[DummyItem(product_id=1, quantity=0)])
    result = service.calculate_total(order)
    assert result == "$0.00"
    service._inventory.get_product.assert_called_once_with(1)
# AI_TEST_AGENT_END function=PricingService.calculate_total

# AI_TEST_AGENT_START function=PricingService.apply_discount
class DummyOrder:
    def __init__(self, total):
        self.total = total
        self.discount_applied = None

def dummy_format_currency(value):
    return round(value, 2)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=dummy_format_currency)
def test_apply_discount_invalid_code_raises(mock_format):
    service = PricingService()
    order = DummyOrder(total=100)
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {}):
        with pytest.raises(InvalidDiscountError, match="Invalid discount code: 'INVALID'"):
            service.apply_discount(order, 'INVALID')
    mock_format.assert_not_called()

@patch('inventory_system.services.pricing_service.format_currency', side_effect=dummy_format_currency)
def test_apply_discount_order_total_below_minimum_raises(mock_format):
    service = PricingService()
    order = DummyOrder(total=50)
    discount_code = 'CODE1'
    discount_data = {
        discount_code: {
            "min_order": 100,
            "type": "percentage",
            "value": 10
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        with pytest.raises(InvalidDiscountError, match="Order total 50 does not meet minimum requirement of 100 for code 'CODE1'"):
            service.apply_discount(order, discount_code)
    mock_format.assert_not_called()

@patch('inventory_system.services.pricing_service.format_currency', side_effect=dummy_format_currency)
def test_apply_discount_percentage_discount_applied_correctly(mock_format):
    service = PricingService()
    order = DummyOrder(total=200)
    discount_code = 'PERCENT10'
    discount_data = {
        discount_code: {
            "min_order": 100,
            "type": "percentage",
            "value": 10
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        result = service.apply_discount(order, discount_code)
    expected_discount = round(200 * 0.10, 2)
    expected_total = round(200 - expected_discount, 2)
    assert result.discount_applied == expected_discount
    assert result.total == expected_total
    assert result is order
    assert mock_format.call_count == 2

@patch('inventory_system.services.pricing_service.format_currency', side_effect=dummy_format_currency)
def test_apply_discount_fixed_discount_less_than_order_total(mock_format):
    service = PricingService()
    order = DummyOrder(total=150)
    discount_code = 'FIXED50'
    discount_data = {
        discount_code: {
            "min_order": 100,
            "type": "fixed",
            "value": 50
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        result = service.apply_discount(order, discount_code)
    assert result.discount_applied == 50
    assert result.total == 100
    assert result is order
    assert mock_format.call_count == 2

@patch('inventory_system.services.pricing_service.format_currency', side_effect=dummy_format_currency)
def test_apply_discount_fixed_discount_more_than_order_total_caps_discount(mock_format):
    service = PricingService()
    order = DummyOrder(total=40)
    discount_code = 'FIXED50'
    discount_data = {
        discount_code: {
            "min_order": 10,
            "type": "fixed",
            "value": 50
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        result = service.apply_discount(order, discount_code)
    assert result.discount_applied == 40
    assert result.total == 0
    assert result is order
    assert mock_format.call_count == 2

@patch('inventory_system.services.pricing_service.format_currency', side_effect=dummy_format_currency)
def test_apply_discount_min_order_exactly_equal_to_order_total_raises(mock_format):
    service = PricingService()
    order = DummyOrder(total=100)
    discount_code = 'CODEMIN'
    discount_data = {
        discount_code: {
            "min_order": 100,
            "type": "percentage",
            "value": 20
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        with pytest.raises(InvalidDiscountError, match="Order total 100 does not meet minimum requirement of 100 for code 'CODEMIN'"):
            service.apply_discount(order, discount_code)
    mock_format.assert_not_called()

@patch('inventory_system.services.pricing_service.format_currency', side_effect=dummy_format_currency)
def test_apply_discount_discount_type_unknown_no_discount_applied(mock_format):
    service = PricingService()
    order = DummyOrder(total=200)
    discount_code = 'UNKNOWN'
    discount_data = {
        discount_code: {
            "min_order": 100,
            "type": "unknown",
            "value": 30
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        result = service.apply_discount(order, discount_code)
    assert result.discount_applied is None
    assert result.total == 200
    assert result is order
    mock_format.assert_not_called()

@patch('inventory_system.services.pricing_service.format_currency', side_effect=dummy_format_currency)
def test_apply_discount_discount_code_empty_string_raises(mock_format):
    service = PricingService()
    order = DummyOrder(total=200)
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {"": {"min_order": 100, "type": "fixed", "value": 10}}):
        with pytest.raises(InvalidDiscountError, match="Invalid discount code: ''"):
            service.apply_discount(order, '')
    mock_format.assert_not_called()

@patch('inventory_system.services.pricing_service.format_currency', side_effect=dummy_format_currency)
def test_apply_discount_order_total_zero_raises_minimum_not_met(mock_format):
    service = PricingService()
    order = DummyOrder(total=0)
    discount_code = 'FIXED10'
    discount_data = {
        discount_code: {
            "min_order": 1,
            "type": "fixed",
            "value": 10
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        with pytest.raises(InvalidDiscountError, match="Order total 0 does not meet minimum requirement of 1 for code 'FIXED10'"):
            service.apply_discount(order, discount_code)
    mock_format.assert_not_called()
# AI_TEST_AGENT_END function=PricingService.apply_discount

# AI_TEST_AGENT_START function=PricingService.get_discount_info
def test_get_discount_info_valid_code_returns_correct_dict():
    discount_code = "SUMMER21"
    discount_data = {"percent": 15, "description": "Summer sale 15% off"}
    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {discount_code: discount_data}):
        service = PricingService()
        result = service.get_discount_info(discount_code)
        assert result == discount_data
        assert isinstance(result, dict)

def test_get_discount_info_invalid_code_raises_invalid_discount_error():
    invalid_code = "INVALID_CODE"
    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {}):
        service = PricingService()
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.get_discount_info(invalid_code)
        assert f"Invalid discount code: '{invalid_code}'" in str(excinfo.value)

def test_get_discount_info_empty_string_code_raises_invalid_discount_error():
    empty_code = ""
    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {"": {"percent": 0}}):
        service = PricingService()
        result = service.get_discount_info(empty_code)
        assert result == {"percent": 0}
    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {}):
        service = PricingService()
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.get_discount_info(empty_code)
        assert "Invalid discount code: ''" in str(excinfo.value)

def test_get_discount_info_code_with_none_key_raises_invalid_discount_error():
    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {None: {"percent": 10}}):
        service = PricingService()
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.get_discount_info(None)
        assert "Invalid discount code: None" in str(excinfo.value)

def test_get_discount_info_code_with_non_string_key_raises_invalid_discount_error():
    non_string_code = 12345
    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {"12345": {"percent": 20}}):
        service = PricingService()
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.get_discount_info(non_string_code)
        assert f"Invalid discount code: {non_string_code!r}" in str(excinfo.value)

def test_get_discount_info_code_with_similar_key_but_different_case_raises_invalid_discount_error():
    discount_code = "WINTER"
    discount_data = {"percent": 25}
    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {discount_code: discount_data}):
        service = PricingService()
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.get_discount_info("winter")
        assert "Invalid discount code: 'winter'" in str(excinfo.value)

def test_get_discount_info_code_with_complex_dict_value_returns_copy():
    discount_code = "COMPLEX"
    discount_data = {"percent": 30, "description": "Complex discount", "details": {"min_purchase": 100}}
    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {discount_code: discount_data}):
        service = PricingService()
        result = service.get_discount_info(discount_code)
        assert result == discount_data
        assert result is not discount_data
        assert result["details"] == discount_data["details"]

def test_get_discount_info_code_with_empty_dict_value_returns_empty_dict():
    discount_code = "EMPTY"
    discount_data = {}
    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {discount_code: discount_data}):
        service = PricingService()
        result = service.get_discount_info(discount_code)
        assert result == {}
        assert isinstance(result, dict)
# AI_TEST_AGENT_END function=PricingService.get_discount_info

# AI_TEST_AGENT_START function=PricingService.estimate_discounted_total
class DummyOrder:
    def __init__(self, total):
        self.total = total


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES')
@patch('inventory_system.services.pricing_service.format_currency')
def test_estimate_discounted_total_invalid_discount_code(mock_format_currency, mock_discount_codes):
    service = PricingService()
    order = DummyOrder(total=100.0)
    mock_discount_codes.__contains__.return_value = False
    mock_discount_codes.__getitem__.side_effect = KeyError

    with pytest.raises(InvalidDiscountError) as excinfo:
        service.estimate_discounted_total(order, 'INVALID_CODE')
    assert "Invalid discount code: 'INVALID_CODE'" in str(excinfo.value)
    mock_discount_codes.__contains__.assert_called_once_with('INVALID_CODE')
    mock_discount_codes.__getitem__.assert_not_called()
    mock_format_currency.assert_not_called()


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES')
@patch('inventory_system.services.pricing_service.format_currency')
def test_estimate_discounted_total_total_less_equal_min_order_returns_total(mock_format_currency, mock_discount_codes):
    service = PricingService()
    order = DummyOrder(total=50.0)
    discount_code = 'DISC10'
    discount = {"type": "percentage", "value": 10, "min_order": 50.0}
    mock_discount_codes.__contains__.return_value = True
    mock_discount_codes.__getitem__.return_value = discount

    result = service.estimate_discounted_total(order, discount_code)

    assert result == 50.0
    mock_discount_codes.__contains__.assert_called_once_with(discount_code)
    mock_discount_codes.__getitem__.assert_called_once_with(discount_code)
    mock_format_currency.assert_not_called()


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES')
@patch('inventory_system.services.pricing_service.format_currency')
def test_estimate_discounted_total_percentage_discount_applied(mock_format_currency, mock_discount_codes):
    service = PricingService()
    order = DummyOrder(total=200.0)
    discount_code = 'PERC20'
    discount = {"type": "percentage", "value": 20, "min_order": 100.0}
    mock_discount_codes.__contains__.return_value = True
    mock_discount_codes.__getitem__.return_value = discount
    mock_format_currency.side_effect = lambda x: round(x, 2)

    result = service.estimate_discounted_total(order, discount_code)

    expected_value = 200.0 * (1 - 20 / 100)
    assert result == round(expected_value, 2)
    mock_discount_codes.__contains__.assert_called_once_with(discount_code)
    mock_discount_codes.__getitem__.assert_called_once_with(discount_code)
    mock_format_currency.assert_called_once_with(expected_value)


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES')
@patch('inventory_system.services.pricing_service.format_currency')
def test_estimate_discounted_total_fixed_discount_applied_positive_result(mock_format_currency, mock_discount_codes):
    service = PricingService()
    order = DummyOrder(total=150.0)
    discount_code = 'FIXED30'
    discount = {"type": "fixed", "value": 30, "min_order": 100.0}
    mock_discount_codes.__contains__.return_value = True
    mock_discount_codes.__getitem__.return_value = discount
    mock_format_currency.side_effect = lambda x: round(x, 2)

    result = service.estimate_discounted_total(order, discount_code)

    expected_value = max(0.0, 150.0 - 30)
    assert result == round(expected_value, 2)
    mock_discount_codes.__contains__.assert_called_once_with(discount_code)
    mock_discount_codes.__getitem__.assert_called_once_with(discount_code)
    mock_format_currency.assert_called_once_with(expected_value)


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES')
@patch('inventory_system.services.pricing_service.format_currency')
def test_estimate_discounted_total_fixed_discount_applied_zero_floor(mock_format_currency, mock_discount_codes):
    service = PricingService()
    order = DummyOrder(total=20.0)
    discount_code = 'FIXED50'
    discount = {"type": "fixed", "value": 50, "min_order": 10.0}
    mock_discount_codes.__contains__.return_value = True
    mock_discount_codes.__getitem__.return_value = discount
    mock_format_currency.side_effect = lambda x: round(x, 2)

    result = service.estimate_discounted_total(order, discount_code)

    expected_value = max(0.0, 20.0 - 50)
    assert result == round(expected_value, 2)
    mock_discount_codes.__contains__.assert_called_once_with(discount_code)
    mock_discount_codes.__getitem__.assert_called_once_with(discount_code)
    mock_format_currency.assert_called_once_with(expected_value)


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES')
@patch('inventory_system.services.pricing_service.format_currency')
def test_estimate_discounted_total_unknown_discount_type_returns_total(mock_format_currency, mock_discount_codes):
    service = PricingService()
    order = DummyOrder(total=120.0)
    discount_code = 'UNKNOWN'
    discount = {"type": "unknown_type", "value": 10, "min_order": 100.0}
    mock_discount_codes.__contains__.return_value = True
    mock_discount_codes.__getitem__.return_value = discount

    result = service.estimate_discounted_total(order, discount_code)

    assert result == 120.0
    mock_discount_codes.__contains__.assert_called_once_with(discount_code)
    mock_discount_codes.__getitem__.assert_called_once_with(discount_code)
    mock_format_currency.assert_not_called()


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES')
@patch('inventory_system.services.pricing_service.format_currency')
def test_estimate_discounted_total_discount_code_empty_string_raises(mock_format_currency, mock_discount_codes):
    service = PricingService()
    order = DummyOrder(total=100.0)
    discount_code = ''
    mock_discount_codes.__contains__.return_value = False
    mock_discount_codes.__getitem__.side_effect = KeyError

    with pytest.raises(InvalidDiscountError) as excinfo:
        service.estimate_discounted_total(order, discount_code)
    assert "Invalid discount code: ''" in str(excinfo.value)
    mock_discount_codes.__contains__.assert_called_once_with('')
    mock_discount_codes.__getitem__.assert_not_called()
    mock_format_currency.assert_not_called()


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES')
@patch('inventory_system.services.pricing_service.format_currency')
def test_estimate_discounted_total_order_total_zero_percentage_discount(mock_format_currency, mock_discount_codes):
    service = PricingService()
    order = DummyOrder(total=0.0)
    discount_code = 'PERC10'
    discount = {"type": "percentage", "value": 10, "min_order": 0.0}
    mock_discount_codes.__contains__.return_value = True
    mock_discount_codes.__getitem__.return_value = discount

    result = service.estimate_discounted_total(order, discount_code)

    assert result == 0.0
    mock_discount_codes.__contains__.assert_called_once_with(discount_code)
    mock_discount_codes.__getitem__.assert_called_once_with(discount_code)
    mock_format_currency.assert_not_called()


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES')
@patch('inventory_system.services.pricing_service.format_currency')
def test_estimate_discounted_total_order_total_none_raises_attribute_error(mock_format_currency, mock_discount_codes):
    service = PricingService()
    order = MagicMock()
    order.total = None
    discount_code = 'PERC10'
    discount = {"type": "percentage", "value": 10, "min_order": 0.0}
    mock_discount_codes.__contains__.return_value = True
    mock_discount_codes.__getitem__.return_value = discount

    with pytest.raises(TypeError):
        service.estimate_discounted_total(order, discount_code)
    mock_discount_codes.__contains__.assert_called_once_with(discount_code)
    mock_discount_codes.__getitem__.assert_called_once_with(discount_code)
    mock_format_currency.assert_not_called()
# AI_TEST_AGENT_END function=PricingService.estimate_discounted_total
