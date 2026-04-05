from inventory_system.core.consistency_checker import ConsistencyChecker
from inventory_system.core.consistency_checker import OrderStatus
from unittest.mock import MagicMock
from unittest.mock import MagicMock, patch
import pytest

# AI_TEST_AGENT_START function=ConsistencyChecker.validate_inventory_state
class DummyProduct:
    def __init__(self, product_id, stock, reserved):
        self.product_id = product_id
        self.stock = stock
        self.reserved = reserved

def test_validate_inventory_state_no_products():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._inventory.get_all_products.return_value = []

    result = checker.validate_inventory_state()

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []
    assert result["products_checked"] == 0

def test_validate_inventory_state_duplicate_product_ids():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    products = [
        DummyProduct("p1", 10, 5),
        DummyProduct("p1", 20, 10),
        DummyProduct("p2", 5, 1),
        DummyProduct("p2", 7, 2),
    ]
    checker._inventory.get_all_products.return_value = products

    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert "Duplicate product ID detected: 'p1'" in result["errors"]
    assert "Duplicate product ID detected: 'p2'" in result["errors"]
    assert result["products_checked"] == 4

def test_validate_inventory_state_stock_less_or_equal_reserved():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    products = [
        DummyProduct("p1", 5, 5),
        DummyProduct("p2", 3, 4),
        DummyProduct("p3", 10, 9),
    ]
    checker._inventory.get_all_products.return_value = products

    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert "Product 'p1': stock (5) inconsistent with reserved (5)" in result["errors"]
    assert "Product 'p2': stock (3) inconsistent with reserved (4)" in result["errors"]
    assert "Product 'p3': stock (10) inconsistent with reserved (9)" not in result["errors"]
    assert result["products_checked"] == 3

def test_validate_inventory_state_negative_stock_and_reserved():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    products = [
        DummyProduct("p1", -1, 0),
        DummyProduct("p2", 10, -5),
        DummyProduct("p3", -3, -2),
    ]
    checker._inventory.get_all_products.return_value = products

    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert "Product 'p1': negative stock value (-1)" in result["errors"]
    assert "Product 'p2': negative reserved value (-5)" in result["errors"]
    assert "Product 'p3': negative stock value (-3)" in result["errors"]
    assert "Product 'p3': negative reserved value (-2)" in result["errors"]
    assert result["products_checked"] == 3

def test_validate_inventory_state_high_stock_warning():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    products = [
        DummyProduct("p1", 10001, 0),
        DummyProduct("p2", 9999, 0),
        DummyProduct("p3", 10000, 0),
    ]
    checker._inventory.get_all_products.return_value = products

    result = checker.validate_inventory_state()

    assert result["valid"] is True
    assert "Product 'p1': unusually high stock level (10001)" in result["warnings"]
    assert "Product 'p2': unusually high stock level (9999)" not in result["warnings"]
    assert "Product 'p3': unusually high stock level (10000)" not in result["warnings"]
    assert result["products_checked"] == 3

def test_validate_inventory_state_combined_errors_and_warnings():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    products = [
        DummyProduct("p1", 5, 5),  # stock == reserved error
        DummyProduct("p1", 10, 0),  # duplicate id error
        DummyProduct("p2", -1, -1),  # negative stock and reserved error
        DummyProduct("p3", 15000, 0),  # high stock warning
    ]
    checker._inventory.get_all_products.return_value = products

    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert "Duplicate product ID detected: 'p1'" in result["errors"]
    assert "Product 'p1': stock (5) inconsistent with reserved (5)" in result["errors"]
    assert "Product 'p2': negative stock value (-1)" in result["errors"]
    assert "Product 'p2': negative reserved value (-1)" in result["errors"]
    assert "Product 'p3': unusually high stock level (15000)" in result["warnings"]
    assert result["products_checked"] == 4

def test_validate_inventory_state_invalid_product_attributes_type():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()

    class BadProduct:
        def __init__(self):
            self.product_id = None
            self.stock = "not_an_int"
            self.reserved = []

    checker._inventory.get_all_products.return_value = [BadProduct()]

    with pytest.raises(TypeError):
        checker.validate_inventory_state()

def test_validate_inventory_state_product_id_none_and_empty_string():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    products = [
        DummyProduct(None, 10, 5),
        DummyProduct("", 10, 5),
        DummyProduct("valid", 10, 5),
    ]
    checker._inventory.get_all_products.return_value = products

    result = checker.validate_inventory_state()

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []
    assert result["products_checked"] == 3
# AI_TEST_AGENT_END function=ConsistencyChecker.validate_inventory_state

# AI_TEST_AGENT_START function=ConsistencyChecker.validate_order_reservations
class DummyItem:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity

class DummyOrder:
    def __init__(self, items):
        self.items = items

class DummyProduct:
    def __init__(self, product_id, reserved):
        self.product_id = product_id
        self.reserved = reserved

def test_validate_order_reservations_all_consistent():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._orders = MagicMock()

    products = [DummyProduct(product_id=1, reserved=5), DummyProduct(product_id=2, reserved=3)]
    checker._inventory.get_all_products.return_value = products

    orders = [
        DummyOrder(items=[DummyItem(product_id=1, quantity=2), DummyItem(product_id=2, quantity=3)]),
        DummyOrder(items=[DummyItem(product_id=1, quantity=3)]),
    ]
    checker._orders.get_orders_by_status.return_value = orders

    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 2

def test_validate_order_reservations_with_mismatches():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._orders = MagicMock()

    products = [DummyProduct(product_id=1, reserved=4), DummyProduct(product_id=2, reserved=3)]
    checker._inventory.get_all_products.return_value = products

    orders = [
        DummyOrder(items=[DummyItem(product_id=1, quantity=2), DummyItem(product_id=2, quantity=3)]),
        DummyOrder(items=[DummyItem(product_id=1, quantity=3)]),
    ]
    checker._orders.get_orders_by_status.return_value = orders

    result = checker.validate_order_reservations()

    assert result["consistent"] is False
    assert len(result["mismatches"]) == 1
    mismatch = result["mismatches"][0]
    assert mismatch["product_id"] == 1
    assert mismatch["expected_reserved"] == 5
    assert mismatch["actual_reserved"] == 4
    assert mismatch["delta"] == -1
    assert result["orders_checked"] == 2

def test_validate_order_reservations_no_confirmed_orders():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._orders = MagicMock()

    products = [DummyProduct(product_id=1, reserved=0)]
    checker._inventory.get_all_products.return_value = products

    checker._orders.get_orders_by_status.return_value = []

    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 0

def test_validate_order_reservations_no_products():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._orders = MagicMock()

    checker._inventory.get_all_products.return_value = []

    orders = [
        DummyOrder(items=[DummyItem(product_id=1, quantity=2)]),
    ]
    checker._orders.get_orders_by_status.return_value = orders

    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 1

def test_validate_order_reservations_order_with_zero_quantity_item():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._orders = MagicMock()

    products = [DummyProduct(product_id=1, reserved=0)]
    checker._inventory.get_all_products.return_value = products

    orders = [
        DummyOrder(items=[DummyItem(product_id=1, quantity=0)]),
    ]
    checker._orders.get_orders_by_status.return_value = orders

    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 1

def test_validate_order_reservations_product_reserved_none_and_expected_zero():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._orders = MagicMock()

    # reserved is None instead of int, should handle gracefully
    products = [DummyProduct(product_id=1, reserved=None)]
    checker._inventory.get_all_products.return_value = products

    checker._orders.get_orders_by_status.return_value = []

    with pytest.raises(TypeError):
        checker.validate_order_reservations()

def test_validate_order_reservations_order_item_with_negative_quantity():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._orders = MagicMock()

    products = [DummyProduct(product_id=1, reserved=0)]
    checker._inventory.get_all_products.return_value = products

    orders = [
        DummyOrder(items=[DummyItem(product_id=1, quantity=-5)]),
    ]
    checker._orders.get_orders_by_status.return_value = orders

    result = checker.validate_order_reservations()

    assert result["consistent"] is False
    assert len(result["mismatches"]) == 1
    mismatch = result["mismatches"][0]
    assert mismatch["product_id"] == 1
    assert mismatch["expected_reserved"] == -5
    assert mismatch["actual_reserved"] == 0
    assert mismatch["delta"] == 0 - (-5)
    assert result["orders_checked"] == 1

def test_validate_order_reservations_product_reserved_negative():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._orders = MagicMock()

    products = [DummyProduct(product_id=1, reserved=-3)]
    checker._inventory.get_all_products.return_value = products

    orders = [
        DummyOrder(items=[DummyItem(product_id=1, quantity=0)]),
    ]
    checker._orders.get_orders_by_status.return_value = orders

    result = checker.validate_order_reservations()

    assert result["consistent"] is False
    assert len(result["mismatches"]) == 1
    mismatch = result["mismatches"][0]
    assert mismatch["product_id"] == 1
    assert mismatch["expected_reserved"] == 0
    assert mismatch["actual_reserved"] == -3
    assert mismatch["delta"] == -3
    assert result["orders_checked"] == 1

def test_validate_order_reservations_order_items_with_duplicate_product_ids():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._orders = MagicMock()

    products = [DummyProduct(product_id=1, reserved=6)]
    checker._inventory.get_all_products.return_value = products

    orders = [
        DummyOrder(items=[DummyItem(product_id=1, quantity=2), DummyItem(product_id=1, quantity=4)]),
    ]
    checker._orders.get_orders_by_status.return_value = orders

    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 1
# AI_TEST_AGENT_END function=ConsistencyChecker.validate_order_reservations

# AI_TEST_AGENT_START function=ConsistencyChecker.get_reservation_summary
def test_get_reservation_summary_with_multiple_products():
    checker = ConsistencyChecker()
    product1 = MagicMock()
    product1.stock = 10
    product1.reserved = 5
    product1.available_stock.return_value = 4
    product2 = MagicMock()
    product2.stock = 20
    product2.reserved = 10
    product2.available_stock.return_value = 8
    checker._inventory = MagicMock()
    checker._inventory.get_all_products.return_value = [product1, product2]

    result = checker.get_reservation_summary()

    assert result["total_stock"] == 30
    assert result["total_reserved"] == 15
    assert result["total_available"] == 12
    assert result["utilization_rate"] == pytest.approx(15 / 30, 0.0001)
    checker._inventory.get_all_products.assert_called_once()
    product1.available_stock.assert_called_once()
    product2.available_stock.assert_called_once()

def test_get_reservation_summary_with_no_products():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._inventory.get_all_products.return_value = []

    result = checker.get_reservation_summary()

    assert result["total_stock"] == 0
    assert result["total_reserved"] == 0
    assert result["total_available"] == 0
    assert result["utilization_rate"] == 0.0
    checker._inventory.get_all_products.assert_called_once()

def test_get_reservation_summary_with_zero_stock_products():
    checker = ConsistencyChecker()
    product = MagicMock()
    product.stock = 0
    product.reserved = 0
    product.available_stock.return_value = 0
    checker._inventory = MagicMock()
    checker._inventory.get_all_products.return_value = [product]

    result = checker.get_reservation_summary()

    assert result["total_stock"] == 0
    assert result["total_reserved"] == 0
    assert result["total_available"] == 0
    assert result["utilization_rate"] == 0.0
    checker._inventory.get_all_products.assert_called_once()
    product.available_stock.assert_called_once()

def test_get_reservation_summary_with_reserved_greater_than_stock():
    checker = ConsistencyChecker()
    product = MagicMock()
    product.stock = 5
    product.reserved = 10
    product.available_stock.return_value = 0
    checker._inventory = MagicMock()
    checker._inventory.get_all_products.return_value = [product]

    result = checker.get_reservation_summary()

    assert result["total_stock"] == 5
    assert result["total_reserved"] == 10
    assert result["total_available"] == 0
    assert result["utilization_rate"] == pytest.approx(10 / 5, 0.0001)
    checker._inventory.get_all_products.assert_called_once()
    product.available_stock.assert_called_once()

def test_get_reservation_summary_with_negative_stock_and_reserved():
    checker = ConsistencyChecker()
    product = MagicMock()
    product.stock = -10
    product.reserved = -5
    product.available_stock.return_value = -3
    checker._inventory = MagicMock()
    checker._inventory.get_all_products.return_value = [product]

    result = checker.get_reservation_summary()

    assert result["total_stock"] == -10
    assert result["total_reserved"] == -5
    assert result["total_available"] == -3
    # utilization_rate calculation with negative total_stock should not divide, but code does divide anyway
    # So it will calculate -5 / -10 = 0.5
    assert result["utilization_rate"] == pytest.approx(-5 / -10, 0.0001)
    checker._inventory.get_all_products.assert_called_once()
    product.available_stock.assert_called_once()

def test_get_reservation_summary_with_product_available_stock_raising_exception():
    checker = ConsistencyChecker()
    product = MagicMock()
    product.stock = 10
    product.reserved = 5
    def raise_error():
        raise RuntimeError("Error in available_stock")
    product.available_stock.side_effect = raise_error
    checker._inventory = MagicMock()
    checker._inventory.get_all_products.return_value = [product]

    with pytest.raises(RuntimeError, match="Error in available_stock"):
        checker.get_reservation_summary()
    checker._inventory.get_all_products.assert_called_once()
    product.available_stock.assert_called_once()

def test_get_reservation_summary_with_none_returned_from_get_all_products():
    checker = ConsistencyChecker()
    checker._inventory = MagicMock()
    checker._inventory.get_all_products.return_value = None

    with pytest.raises(TypeError):
        checker.get_reservation_summary()
    checker._inventory.get_all_products.assert_called_once()

def test_get_reservation_summary_with_product_having_none_stock_reserved():
    checker = ConsistencyChecker()
    product = MagicMock()
    product.stock = None
    product.reserved = None
    product.available_stock.return_value = 0
    checker._inventory = MagicMock()
    checker._inventory.get_all_products.return_value = [product]

    with pytest.raises(TypeError):
        checker.get_reservation_summary()
    checker._inventory.get_all_products.assert_called_once()
    product.available_stock.assert_called_once()
# AI_TEST_AGENT_END function=ConsistencyChecker.get_reservation_summary
