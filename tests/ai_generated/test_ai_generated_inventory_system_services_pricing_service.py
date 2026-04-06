from inventory_system.services.pricing_service import PricingService, InvalidDiscountError
from unittest.mock import MagicMock, patch
from unittest.mock import patch
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
        self.total = 0.0
        self.discount_applied = None

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_single_item(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.return_value = DummyProduct(price=10.0)
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=3)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    assert total == 30.0
    inventory_mock.get_product.assert_called_once_with(1)
    mock_format_currency.assert_called_once_with(30.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_multiple_items(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.side_effect = [DummyProduct(price=5.0), DummyProduct(price=2.5)]
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=2), DummyItem(product_id=2, quantity=4)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    expected_total = 2 * 5.0 + 4 * 2.5
    assert total == expected_total
    assert inventory_mock.get_product.call_count == 2
    inventory_mock.get_product.assert_any_call(1)
    inventory_mock.get_product.assert_any_call(2)
    mock_format_currency.assert_called_with(expected_total)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_empty_items_list(mock_format_currency):
    inventory_mock = MagicMock()
    order = DummyOrder(items=[])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    assert total == 0.0
    inventory_mock.get_product.assert_not_called()
    mock_format_currency.assert_called_once_with(0.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_zero_quantity_item(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.return_value = DummyProduct(price=100.0)
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=0)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    assert total == 0.0
    inventory_mock.get_product.assert_called_once_with(1)
    mock_format_currency.assert_called_once_with(0.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_negative_quantity_item(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.return_value = DummyProduct(price=50.0)
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=-2)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    assert total == -100.0
    inventory_mock.get_product.assert_called_once_with(1)
    mock_format_currency.assert_called_once_with(-100.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_product_price_zero(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.return_value = DummyProduct(price=0.0)
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=10)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    assert total == 0.0
    inventory_mock.get_product.assert_called_once_with(1)
    mock_format_currency.assert_called_once_with(0.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_product_price_negative(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.return_value = DummyProduct(price=-20.0)
    order = DummyOrder(items=[DummyItem(product_id=1, quantity=3)])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    assert total == -60.0
    inventory_mock.get_product.assert_called_once_with(1)
    mock_format_currency.assert_called_once_with(-60.0)

@patch('inventory_system.services.pricing_service.format_currency', side_effect=lambda x: round(x, 2))
def test_calculate_total_multiple_items_with_zero_and_negative(mock_format_currency):
    inventory_mock = MagicMock()
    inventory_mock.get_product.side_effect = [DummyProduct(price=10.0), DummyProduct(price=0.0), DummyProduct(price=-5.0)]
    order = DummyOrder(items=[
        DummyItem(product_id=1, quantity=1),
        DummyItem(product_id=2, quantity=5),
        DummyItem(product_id=3, quantity=2)
    ])
    service = PricingService(inventory_mock)

    total = service.calculate_total(order)

    expected_total = 1 * 10.0 + 5 * 0.0 + 2 * -5.0
    assert total == expected_total
    assert inventory_mock.get_product.call_count == 3
    inventory_mock.get_product.assert_any_call(1)
    inventory_mock.get_product.assert_any_call(2)
    inventory_mock.get_product.assert_any_call(3)
    mock_format_currency.assert_called_with(expected_total)

def test_calculate_total_invalid_item_missing_product_id():
    inventory_mock = MagicMock()
    order = DummyOrder(items=[DummyItem(product_id=None, quantity=1)])
    service = PricingService(inventory_mock)

    with pytest.raises(TypeError):
        service.calculate_total(order)
    inventory_mock.get_product.assert_called_once_with(None)
# AI_TEST_AGENT_END function=PricingService.calculate_total

# AI_TEST_AGENT_START function=PricingService.apply_discount
class DummyOrder:
    def __init__(self, total):
        self.total = total
        self.discount_applied = None

def test_apply_discount_invalid_code_raises():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=100.0)
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {}):
        with pytest.raises(InvalidDiscountError, match="Invalid discount code: 'INVALID'"):
            service.apply_discount(order, 'INVALID')

def test_apply_discount_order_total_below_minimum_raises():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=50.0)
    discount_code = 'DISC10'
    discount_data = {
        discount_code: {
            "type": "percentage",
            "value": 10,
            "min_order": 100.0
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        with pytest.raises(InvalidDiscountError, match="does not meet minimum requirement"):
            service.apply_discount(order, discount_code)

def test_apply_discount_percentage_discount_applies_correctly():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=200.0)
    discount_code = 'PERC20'
    discount_data = {
        discount_code: {
            "type": "percentage",
            "value": 20,
            "min_order": 100.0
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        result = service.apply_discount(order, discount_code)
        expected_discount = round(200.0 * 0.20, 2)
        expected_total = round(200.0 - expected_discount, 2)
        assert isinstance(result, DummyOrder)
        assert pytest.approx(float(result.discount_applied), 0.01) == expected_discount
        assert pytest.approx(float(result.total), 0.01) == expected_total

def test_apply_discount_fixed_discount_less_than_total_applies_correctly():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=150.0)
    discount_code = 'FIXED30'
    discount_data = {
        discount_code: {
            "type": "fixed",
            "value": 30.0,
            "min_order": 100.0
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        result = service.apply_discount(order, discount_code)
        assert isinstance(result, DummyOrder)
        assert pytest.approx(float(result.discount_applied), 0.01) == 30.0
        assert pytest.approx(float(result.total), 0.01) == 120.0

def test_apply_discount_fixed_discount_more_than_total_caps_at_total():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=25.0)
    discount_code = 'FIXED50'
    discount_data = {
        discount_code: {
            "type": "fixed",
            "value": 50.0,
            "min_order": 10.0
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        result = service.apply_discount(order, discount_code)
        assert isinstance(result, DummyOrder)
        assert pytest.approx(float(result.discount_applied), 0.01) == 25.0
        assert pytest.approx(float(result.total), 0.01) == 0.0

def test_apply_discount_order_total_exactly_minimum_raises():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=100.0)
    discount_code = 'MIN100'
    discount_data = {
        discount_code: {
            "type": "percentage",
            "value": 10,
            "min_order": 100.0
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        with pytest.raises(InvalidDiscountError, match="does not meet minimum requirement"):
            service.apply_discount(order, discount_code)

def test_apply_discount_order_total_just_above_minimum_applies():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=100.01)
    discount_code = 'MIN100'
    discount_data = {
        discount_code: {
            "type": "percentage",
            "value": 10,
            "min_order": 100.0
        }
    }
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', discount_data):
        result = service.apply_discount(order, discount_code)
        expected_discount = round(100.01 * 0.10, 2)
        expected_total = round(100.01 - expected_discount, 2)
        assert isinstance(result, DummyOrder)
        assert pytest.approx(float(result.discount_applied), 0.01) == expected_discount
        assert pytest.approx(float(result.total), 0.01) == expected_total

def test_apply_discount_with_none_discount_code_raises():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=200.0)
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {}):
        with pytest.raises(InvalidDiscountError, match="Invalid discount code: None"):
            service.apply_discount(order, None)

def test_apply_discount_with_empty_string_discount_code_raises():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=200.0)
    with patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {}):
        with pytest.raises(InvalidDiscountError, match="Invalid discount code: ''"):
            service.apply_discount(order, '')
# AI_TEST_AGENT_END function=PricingService.apply_discount

# AI_TEST_AGENT_START function=PricingService.get_discount_info
class DummyOrder:
    def __init__(self, total):
        self.total = total
        self.discount_applied = None

@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', new={})
def test_get_discount_info_invalid_code_raises():
    pricing_service = PricingService(inventory_service=None)
    with pytest.raises(InvalidDiscountError) as excinfo:
        pricing_service.get_discount_info('NONEXISTENT')
    assert "Invalid discount code: 'NONEXISTENT'" in str(excinfo.value)

@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', new={'SAVE10': {'type': 'percentage', 'value': 10, 'min_order': 0}})
def test_get_discount_info_valid_percentage_discount():
    pricing_service = PricingService(inventory_service=None)
    result = pricing_service.get_discount_info('SAVE10')
    assert isinstance(result, dict)
    assert result['type'] == 'percentage'
    assert result['value'] == 10
    assert result['min_order'] == 0

@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', new={'FIXED5': {'type': 'fixed', 'value': 5, 'min_order': 10}})
def test_get_discount_info_valid_fixed_discount():
    pricing_service = PricingService(inventory_service=None)
    result = pricing_service.get_discount_info('FIXED5')
    assert isinstance(result, dict)
    assert result['type'] == 'fixed'
    assert result['value'] == 5
    assert result['min_order'] == 10

@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', new={'EMPTY': {}})
def test_get_discount_info_discount_code_with_empty_dict():
    pricing_service = PricingService(inventory_service=None)
    result = pricing_service.get_discount_info('EMPTY')
    assert isinstance(result, dict)
    assert result == {}

@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', new={'NONE_VALUE': {'type': None, 'value': None, 'min_order': None}})
def test_get_discount_info_discount_code_with_none_values():
    pricing_service = PricingService(inventory_service=None)
    result = pricing_service.get_discount_info('NONE_VALUE')
    assert result['type'] is None
    assert result['value'] is None
    assert result['min_order'] is None

@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', new={'NEGATIVE_MIN': {'type': 'fixed', 'value': 5, 'min_order': -10}})
def test_get_discount_info_discount_code_with_negative_min_order():
    pricing_service = PricingService(inventory_service=None)
    result = pricing_service.get_discount_info('NEGATIVE_MIN')
    assert result['min_order'] == -10

@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', new={'ZERO_MIN': {'type': 'percentage', 'value': 0, 'min_order': 0}})
def test_get_discount_info_discount_code_with_zero_percentage_value():
    pricing_service = PricingService(inventory_service=None)
    result = pricing_service.get_discount_info('ZERO_MIN')
    assert result['value'] == 0
    assert result['min_order'] == 0

@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', new={'STR_VALUE': {'type': 'percentage', 'value': '10', 'min_order': 0}})
def test_get_discount_info_discount_code_with_string_value():
    pricing_service = PricingService(inventory_service=None)
    result = pricing_service.get_discount_info('STR_VALUE')
    assert result['value'] == '10'

@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', new={'MISSING_TYPE': {'value': 10, 'min_order': 0}})
def test_get_discount_info_discount_code_missing_type_key():
    pricing_service = PricingService(inventory_service=None)
    result = pricing_service.get_discount_info('MISSING_TYPE')
    assert 'type' not in result
    assert result['value'] == 10
    assert result['min_order'] == 0
# AI_TEST_AGENT_END function=PricingService.get_discount_info

# AI_TEST_AGENT_START function=PricingService.estimate_discounted_total
class DummyOrderItem:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity


class DummyOrder:
    def __init__(self, total):
        self.total = total
        self.discount_applied = None


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'PERC10': {'type': 'percentage', 'value': 10, 'min_order': 50.0},
    'FIXED5': {'type': 'fixed', 'value': 5.0, 'min_order': 20.0},
})
def test_estimate_discounted_total_percentage_discount_applied():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=100.0)
    discounted_total = service.estimate_discounted_total(order, 'PERC10')
    assert discounted_total == pytest.approx(90.0, rel=1e-2)


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'PERC10': {'type': 'percentage', 'value': 10, 'min_order': 50.0},
    'FIXED5': {'type': 'fixed', 'value': 5.0, 'min_order': 20.0},
})
def test_estimate_discounted_total_fixed_discount_applied():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=30.0)
    discounted_total = service.estimate_discounted_total(order, 'FIXED5')
    assert discounted_total == pytest.approx(25.0, rel=1e-2)


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'PERC10': {'type': 'percentage', 'value': 10, 'min_order': 50.0},
    'FIXED5': {'type': 'fixed', 'value': 5.0, 'min_order': 20.0},
})
def test_estimate_discounted_total_total_below_min_order_returns_original():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=20.0)
    discounted_total = service.estimate_discounted_total(order, 'PERC10')
    assert discounted_total == 20.0


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'PERC10': {'type': 'percentage', 'value': 10, 'min_order': 50.0},
    'FIXED5': {'type': 'fixed', 'value': 5.0, 'min_order': 20.0},
})
def test_estimate_discounted_total_invalid_discount_code_raises():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=100.0)
    with pytest.raises(InvalidDiscountError) as excinfo:
        service.estimate_discounted_total(order, 'INVALID')
    assert "Invalid discount code" in str(excinfo.value)


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'FIXED10': {'type': 'fixed', 'value': 10.0, 'min_order': 0.0},
})
def test_estimate_discounted_total_fixed_discount_exceeds_total_returns_zero():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=5.0)
    discounted_total = service.estimate_discounted_total(order, 'FIXED10')
    assert discounted_total == 0.0


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'PERC0': {'type': 'percentage', 'value': 0, 'min_order': 0.0},
})
def test_estimate_discounted_total_zero_percentage_discount_returns_same_total():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=100.0)
    discounted_total = service.estimate_discounted_total(order, 'PERC0')
    assert discounted_total == pytest.approx(100.0, rel=1e-2)


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'FIXED0': {'type': 'fixed', 'value': 0.0, 'min_order': 0.0},
})
def test_estimate_discounted_total_zero_fixed_discount_returns_same_total():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=50.0)
    discounted_total = service.estimate_discounted_total(order, 'FIXED0')
    assert discounted_total == pytest.approx(50.0, rel=1e-2)


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'PERC100': {'type': 'percentage', 'value': 100, 'min_order': 0.0},
})
def test_estimate_discounted_total_100_percent_discount_returns_zero():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=200.0)
    discounted_total = service.estimate_discounted_total(order, 'PERC100')
    assert discounted_total == 0.0


@patch('inventory_system.services.pricing_service.DISCOUNT_CODES', {
    'FIXED_NEG': {'type': 'fixed', 'value': -10.0, 'min_order': 0.0},
})
def test_estimate_discounted_total_negative_fixed_discount_increases_total():
    inventory_mock = MagicMock()
    service = PricingService(inventory_mock)
    order = DummyOrder(total=50.0)
    discounted_total = service.estimate_discounted_total(order, 'FIXED_NEG')
    assert discounted_total == pytest.approx(60.0, rel=1e-2)
# AI_TEST_AGENT_END function=PricingService.estimate_discounted_total
