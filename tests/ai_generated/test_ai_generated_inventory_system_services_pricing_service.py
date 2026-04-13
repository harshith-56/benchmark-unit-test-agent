from inventory_system.services.pricing_service import PricingService, InvalidDiscountError
from unittest.mock import MagicMock, patch
import pytest

# AI_TEST_AGENT_START function=PricingService.calculate_total
class DummyItem:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity

class DummyProduct:
    def __init__(self, price):
        self.price = price

class DummyOrder:
    def __init__(self, items):
        self.items = items

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_single_item(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.return_value = DummyProduct(price=10.0)
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=3)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    inventory_mock.get_product.assert_called_once_with(1)
    assert total == 30.0
    mock_format_currency.assert_called_once_with(30.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_multiple_items(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.side_effect = [DummyProduct(price=5.0), DummyProduct(price=2.5)]
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=2), DummyItem(product_id=2, quantity=4)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    assert inventory_mock.get_product.call_count == 2
    assert total == 20.0
    mock_format_currency.assert_called_with(20.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_zero_quantity(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.return_value = DummyProduct(price=100.0)
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=0)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    inventory_mock.get_product.assert_called_once_with(1)
    assert total == 0.0
    mock_format_currency.assert_called_once_with(0.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_empty_items_list(mock_format_currency):
    inventory_mock = MagicMock()
    order = DummyOrder(items=[])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    inventory_mock.get_product.assert_not_called()
    assert total == 0.0
    mock_format_currency.assert_called_once_with(0.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_negative_quantity(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.return_value = DummyProduct(price=10.0)
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=-3)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    inventory_mock.get_product.assert_called_once_with(1)
    assert total == -30.0
    mock_format_currency.assert_called_once_with(-30.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_product_price_zero(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.return_value = DummyProduct(price=0.0)
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=5)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    inventory_mock.get_product.assert_called_once_with(1)
    assert total == 0.0
    mock_format_currency.assert_called_once_with(0.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_product_price_negative(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.return_value = DummyProduct(price=-10.0)
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=2)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    inventory_mock.get_product.assert_called_once_with(1)
    assert total == -20.0
    mock_format_currency.assert_called_once_with(-20.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_multiple_items_with_zero_and_negative(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.side_effect = [DummyProduct(price=10.0), DummyProduct(price=0.0), DummyProduct(price=-5.0)]
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=1), DummyItem(product_id=2, quantity=3), DummyItem(product_id=3, quantity=2)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    assert inventory_mock.get_product.call_count == 3
    expected_total = 10.0*1 + 0.0*3 + (-5.0)*2
    assert total == round(expected_total, 2)
    mock_format_currency.assert_called_with(round(expected_total, 2))

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_product_id_none(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.return_value = DummyProduct(price=10.0)
    order = DummyOrder(items=[DummyItem(product_id=None, quantity=1)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    inventory_mock.get_product.assert_called_once_with(None)
    assert total == 10.0
    mock_format_currency.assert_called_once_with(10.0)
# AI_TEST_AGENT_END function=PricingService.calculate_total

# AI_TEST_AGENT_START function=PricingService.apply_discount
class DummyOrderItem:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity

class DummyOrder:
    def __init__(self, total):
        self.total = total
        self.discount_applied = None

def test_apply_discount_invalid_code_raises():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=100.0)
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {}):
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.apply_discount(order, "INVALID_CODE")
        assert "Invalid discount code: 'INVALID_CODE'" in str(excinfo.value)

def test_apply_discount_order_total_below_minimum_raises():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=50.0)
    discount_code = "DISC10"
    discount_data = {"min_order": 100.0, "type": "percentage", "value": 10}
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {discount_code: discount_data}):
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.apply_discount(order, discount_code)
        assert f"Order total {order.total} does not meet minimum requirement of {discount_data['min_order']} for code '{discount_code}'" in str(excinfo.value)

def test_apply_discount_percentage_discount_applied_correctly():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=200.0)
    discount_code = "PERC20"
    discount_data = {"min_order": 100.0, "type": "percentage", "value": 20}
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {discount_code: discount_data}):
        result = service.apply_discount(order, discount_code)
        expected_discount = round(200.0 * 0.20, 2)
        expected_total = round(200.0 - expected_discount, 2)
        assert result.discount_applied == expected_discount
        assert result.total == expected_total

def test_apply_discount_fixed_discount_less_than_total():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=150.0)
    discount_code = "FIXED50"
    discount_data = {"min_order": 100.0, "type": "fixed", "value": 50}
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {discount_code: discount_data}):
        result = service.apply_discount(order, discount_code)
        assert result.discount_applied == 50
        assert result.total == 100

def test_apply_discount_fixed_discount_more_than_total_caps_at_total():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=40.0)
    discount_code = "FIXED50"
    discount_data = {"min_order": 10.0, "type": "fixed", "value": 50}
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {discount_code: discount_data}):
        result = service.apply_discount(order, discount_code)
        assert result.discount_applied == 40
        assert result.total == 0

def test_apply_discount_order_total_exactly_minimum_raises():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=100.0)
    discount_code = "PERC10"
    discount_data = {"min_order": 100.0, "type": "percentage", "value": 10}
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {discount_code: discount_data}):
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.apply_discount(order, discount_code)
        assert f"Order total {order.total} does not meet minimum requirement of {discount_data['min_order']} for code '{discount_code}'" in str(excinfo.value)

def test_apply_discount_percentage_discount_with_fractional_result():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=123.45)
    discount_code = "PERC15"
    discount_data = {"min_order": 100.0, "type": "percentage", "value": 15}
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {discount_code: discount_data}):
        result = service.apply_discount(order, discount_code)
        expected_discount = round(123.45 * 0.15, 2)
        expected_total = round(123.45 - expected_discount, 2)
        assert result.discount_applied == expected_discount
        assert result.total == expected_total

def test_apply_discount_fixed_discount_zero_value():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=200.0)
    discount_code = "FIXED0"
    discount_data = {"min_order": 100.0, "type": "fixed", "value": 0}
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {discount_code: discount_data}):
        result = service.apply_discount(order, discount_code)
        assert result.discount_applied == 0
        assert result.total == 200.0
# AI_TEST_AGENT_END function=PricingService.apply_discount

# AI_TEST_AGENT_START function=PricingService.get_discount_info
def test_get_discount_info_valid_code_returns_dict():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    discount_code = "SUMMER21"
    discount_data = {"type": "percentage", "value": 10, "min_order": 50}

    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {discount_code: discount_data}):
        result = service.get_discount_info(discount_code)
        assert isinstance(result, dict)
        assert result == discount_data

def test_get_discount_info_invalid_code_raises_error():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    invalid_code = "INVALID"

    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {}):
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.get_discount_info(invalid_code)
        assert f"Invalid discount code: '{invalid_code}'" in str(excinfo.value)

def test_get_discount_info_empty_string_code_raises_error():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    empty_code = ""

    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {}):
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.get_discount_info(empty_code)
        assert f"Invalid discount code: '{empty_code}'" in str(excinfo.value)

def test_get_discount_info_none_code_raises_error():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    none_code = None

    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {}):
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.get_discount_info(none_code)
        assert "Invalid discount code: 'None'" in str(excinfo.value)

def test_get_discount_info_numeric_code_raises_error():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    numeric_code = 12345

    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {}):
        with pytest.raises(InvalidDiscountError) as excinfo:
            service.get_discount_info(numeric_code)
        assert "Invalid discount code: 12345" in str(excinfo.value)

def test_get_discount_info_code_with_special_chars():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    special_code = "!@#$%"
    discount_data = {"type": "fixed", "value": 20, "min_order": 100}

    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {special_code: discount_data}):
        result = service.get_discount_info(special_code)
        assert isinstance(result, dict)
        assert result == discount_data

def test_get_discount_info_code_case_sensitivity():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    code_upper = "DISCOUNT"
    code_lower = "discount"
    discount_data = {"type": "percentage", "value": 15, "min_order": 30}

    with patch("inventory_system.services.pricing_service.DISCOUNT_CODES", {code_upper: discount_data}):
        with pytest.raises(InvalidDiscountError):
            service.get_discount_info(code_lower)
        result = service.get_discount_info(code_upper)
        assert result == discount_data
# AI_TEST_AGENT_END function=PricingService.get_discount_info

# AI_TEST_AGENT_START function=PricingService.estimate_discounted_total
class DummyOrder:
    def __init__(self, total):
        self.total = total


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'PERC10': {'type': 'percentage', 'value': 10, 'min_order': 50.0},
    'FIXED20': {'type': 'fixed', 'value': 20, 'min_order': 100.0},
})
def test_estimate_discounted_total_percentage_discount_applied():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=200.0)
    result = service.estimate_discounted_total(order, 'PERC10')
    # line: return format_currency(total * (1 - pct / 100))
    assert result == 180.0


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'PERC10': {'type': 'percentage', 'value': 10, 'min_order': 50.0},
    'FIXED20': {'type': 'fixed', 'value': 20, 'min_order': 100.0},
})
def test_estimate_discounted_total_fixed_discount_applied():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=150.0)
    result = service.estimate_discounted_total(order, 'FIXED20')
    # line: return format_currency(max(0.0, total - discount["value"]))
    assert result == 130.0


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'PERC10': {'type': 'percentage', 'value': 10, 'min_order': 50.0},
})
def test_estimate_discounted_total_total_equal_min_order_returns_total():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=50.0)
    result = service.estimate_discounted_total(order, 'PERC10')
    # line: if total <= discount["min_order"]: return total
    assert result == 50.0


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'FIXED20': {'type': 'fixed', 'value': 20, 'min_order': 100.0},
})
def test_estimate_discounted_total_total_less_than_min_order_returns_total():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=80.0)
    result = service.estimate_discounted_total(order, 'FIXED20')
    # line: if total <= discount["min_order"]: return total
    assert result == 80.0


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'FIXED200': {'type': 'fixed', 'value': 200, 'min_order': 100.0},
})
def test_estimate_discounted_total_fixed_discount_cannot_go_below_zero():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=150.0)
    result = service.estimate_discounted_total(order, 'FIXED200')
    # line: return format_currency(max(0.0, total - discount["value"]))
    assert result == 0.0


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {})
def test_estimate_discounted_total_invalid_discount_code_raises():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=100.0)
    with pytest.raises(InvalidDiscountError) as excinfo:
        service.estimate_discounted_total(order, 'INVALID')
    # line: raise InvalidDiscountError(f"Invalid discount code: {discount_code!r}")
    assert "Invalid discount code: 'INVALID'" in str(excinfo.value)


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'UNKNOWN_TYPE': {'type': 'unknown', 'value': 10, 'min_order': 0.0},
})
def test_estimate_discounted_total_unknown_discount_type_returns_total():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=100.0)
    result = service.estimate_discounted_total(order, 'UNKNOWN_TYPE')
    # line: return total (last line of function)
    assert result == 100.0


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'PERC10': {'type': 'percentage', 'value': 10, 'min_order': 50.0},
})
def test_estimate_discounted_total_order_total_zero_percentage_discount():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=0.0)
    result = service.estimate_discounted_total(order, 'PERC10')
    # line: if total <= discount["min_order"]: return total
    assert result == 0.0


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'FIXED20': {'type': 'fixed', 'value': 20, 'min_order': 10.0},
})
def test_estimate_discounted_total_order_total_negative_fixed_discount():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=-5.0)
    result = service.estimate_discounted_total(order, 'FIXED20')
    # line: if total <= discount["min_order"]: return total
    assert result == -5.0
# AI_TEST_AGENT_END function=PricingService.estimate_discounted_total
