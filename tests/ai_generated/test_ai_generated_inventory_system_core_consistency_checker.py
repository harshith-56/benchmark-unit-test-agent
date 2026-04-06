from inventory_system.core.consistency_checker import ConsistencyChecker
from inventory_system.core.consistency_checker import OrderStatus
from unittest.mock import MagicMock
import pytest

# AI_TEST_AGENT_START function=ConsistencyChecker.validate_inventory_state
class DummyProduct:
    def __init__(self, product_id, stock, reserved):
        self.product_id = product_id
        self.stock = stock
        self.reserved = reserved

def test_validate_inventory_state_no_products():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    inventory_mock.get_all_products.return_value = []

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_inventory_state()

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []
    assert result["products_checked"] == 0
    inventory_mock.get_all_products.assert_called_once()

def test_validate_inventory_state_duplicate_product_ids():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p1 = DummyProduct("p1", 10, 5)
    p2 = DummyProduct("p1", 20, 10)
    inventory_mock.get_all_products.return_value = [p1, p2]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert any("Duplicate product ID detected" in e for e in result["errors"])
    assert result["products_checked"] == 2

def test_validate_inventory_state_stock_less_or_equal_reserved():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p = DummyProduct("p2", 5, 5)
    inventory_mock.get_all_products.return_value = [p]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert any("stock (5) inconsistent with reserved (5)" in e for e in result["errors"])
    assert result["products_checked"] == 1

def test_validate_inventory_state_negative_stock_and_reserved():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p = DummyProduct("p3", -1, -2)
    inventory_mock.get_all_products.return_value = [p]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert any("negative stock value (-1)" in e for e in result["errors"])
    assert any("negative reserved value (-2)" in e for e in result["errors"])
    assert result["products_checked"] == 1

def test_validate_inventory_state_high_stock_warning():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p = DummyProduct("p4", 10001, 0)
    inventory_mock.get_all_products.return_value = [p]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_inventory_state()

    assert result["valid"] is True
    assert result["errors"] == []
    assert any("unusually high stock level (10001)" in w for w in result["warnings"])
    assert result["products_checked"] == 1

def test_validate_inventory_state_multiple_issues():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p1 = DummyProduct("dup", 10, 11)
    p2 = DummyProduct("dup", -5, 0)
    p3 = DummyProduct("p5", 10002, 0)
    inventory_mock.get_all_products.return_value = [p1, p2, p3]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert any("Duplicate product ID detected" in e for e in result["errors"])
    assert any("stock (10) inconsistent with reserved (11)" in e for e in result["errors"])
    assert any("negative stock value (-5)" in e for e in result["errors"])
    assert any("unusually high stock level (10002)" in w for w in result["warnings"])
    assert result["products_checked"] == 3

def test_validate_inventory_state_empty_product_id_and_zero_values():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p = DummyProduct("", 0, 0)
    inventory_mock.get_all_products.return_value = [p]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert any("stock (0) inconsistent with reserved (0)" in e for e in result["errors"])
    assert result["products_checked"] == 1

def test_validate_inventory_state_non_string_product_id():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p = DummyProduct(123, 10, 5)
    inventory_mock.get_all_products.return_value = [p]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_inventory_state()

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["products_checked"] == 1

def test_validate_inventory_state_product_id_none():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p = DummyProduct(None, 10, 5)
    inventory_mock.get_all_products.return_value = [p]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_inventory_state()

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["products_checked"] == 1
# AI_TEST_AGENT_END function=ConsistencyChecker.validate_inventory_state

# AI_TEST_AGENT_START function=ConsistencyChecker.validate_order_reservations
def test_validate_order_reservations_all_match():
    inventory_mock = MagicMock()
    order_service_mock = MagicMock()

    product1 = MagicMock()
    product1.product_id = "p1"
    product1.reserved = 5

    product2 = MagicMock()
    product2.product_id = "p2"
    product2.reserved = 3

    inventory_mock.get_all_products.return_value = [product1, product2]

    order_item1 = MagicMock()
    order_item1.product_id = "p1"
    order_item1.quantity = 5

    order_item2 = MagicMock()
    order_item2.product_id = "p2"
    order_item2.quantity = 3

    order_mock = MagicMock()
    order_mock.items = [order_item1, order_item2]

    order_service_mock.get_orders_by_status.return_value = [order_mock]

    checker = ConsistencyChecker(inventory_mock, order_service_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 1
    inventory_mock.get_all_products.assert_called_once()
    order_service_mock.get_orders_by_status.assert_called_once_with(OrderStatus.CONFIRMED)

def test_validate_order_reservations_mismatch_detected():
    inventory_mock = MagicMock()
    order_service_mock = MagicMock()

    product1 = MagicMock()
    product1.product_id = "p1"
    product1.reserved = 4  # actual reserved less than expected

    product2 = MagicMock()
    product2.product_id = "p2"
    product2.reserved = 3

    inventory_mock.get_all_products.return_value = [product1, product2]

    order_item1 = MagicMock()
    order_item1.product_id = "p1"
    order_item1.quantity = 5  # expected reserved is 5

    order_item2 = MagicMock()
    order_item2.product_id = "p2"
    order_item2.quantity = 3

    order_mock = MagicMock()
    order_mock.items = [order_item1, order_item2]

    order_service_mock.get_orders_by_status.return_value = [order_mock]

    checker = ConsistencyChecker(inventory_mock, order_service_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is False
    assert len(result["mismatches"]) == 1
    mismatch = result["mismatches"][0]
    assert mismatch["product_id"] == "p1"
    assert mismatch["expected_reserved"] == 5
    assert mismatch["actual_reserved"] == 4
    assert mismatch["delta"] == -1
    assert result["orders_checked"] == 1

def test_validate_order_reservations_no_confirmed_orders():
    inventory_mock = MagicMock()
    order_service_mock = MagicMock()

    product1 = MagicMock()
    product1.product_id = "p1"
    product1.reserved = 0

    inventory_mock.get_all_products.return_value = [product1]
    order_service_mock.get_orders_by_status.return_value = []

    checker = ConsistencyChecker(inventory_mock, order_service_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 0

def test_validate_order_reservations_multiple_orders_accumulate_quantities():
    inventory_mock = MagicMock()
    order_service_mock = MagicMock()

    product1 = MagicMock()
    product1.product_id = "p1"
    product1.reserved = 7

    inventory_mock.get_all_products.return_value = [product1]

    order_item1 = MagicMock()
    order_item1.product_id = "p1"
    order_item1.quantity = 3

    order_item2 = MagicMock()
    order_item2.product_id = "p1"
    order_item2.quantity = 4

    order_mock1 = MagicMock()
    order_mock1.items = [order_item1]

    order_mock2 = MagicMock()
    order_mock2.items = [order_item2]

    order_service_mock.get_orders_by_status.return_value = [order_mock1, order_mock2]

    checker = ConsistencyChecker(inventory_mock, order_service_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 2

def test_validate_order_reservations_product_with_no_reservations_but_reserved_stock():
    inventory_mock = MagicMock()
    order_service_mock = MagicMock()

    product1 = MagicMock()
    product1.product_id = "p1"
    product1.reserved = 2

    inventory_mock.get_all_products.return_value = [product1]
    order_service_mock.get_orders_by_status.return_value = []

    checker = ConsistencyChecker(inventory_mock, order_service_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is False
    assert len(result["mismatches"]) == 1
    mismatch = result["mismatches"][0]
    assert mismatch["product_id"] == "p1"
    assert mismatch["expected_reserved"] == 0
    assert mismatch["actual_reserved"] == 2
    assert mismatch["delta"] == 2
    assert result["orders_checked"] == 0

def test_validate_order_reservations_order_with_zero_quantity_items():
    inventory_mock = MagicMock()
    order_service_mock = MagicMock()

    product1 = MagicMock()
    product1.product_id = "p1"
    product1.reserved = 0

    inventory_mock.get_all_products.return_value = [product1]

    order_item1 = MagicMock()
    order_item1.product_id = "p1"
    order_item1.quantity = 0

    order_mock = MagicMock()
    order_mock.items = [order_item1]

    order_service_mock.get_orders_by_status.return_value = [order_mock]

    checker = ConsistencyChecker(inventory_mock, order_service_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 1

def test_validate_order_reservations_product_with_none_reserved_value():
    inventory_mock = MagicMock()
    order_service_mock = MagicMock()

    product1 = MagicMock()
    product1.product_id = "p1"
    product1.reserved = None  # invalid reserved value

    inventory_mock.get_all_products.return_value = [product1]

    order_item1 = MagicMock()
    order_item1.product_id = "p1"
    order_item1.quantity = 0

    order_mock = MagicMock()
    order_mock.items = [order_item1]

    order_service_mock.get_orders_by_status.return_value = [order_mock]

    checker = ConsistencyChecker(inventory_mock, order_service_mock)
    with pytest.raises(TypeError):
        checker.validate_order_reservations()

def test_validate_order_reservations_product_with_none_product_id():
    inventory_mock = MagicMock()
    order_service_mock = MagicMock()

    product1 = MagicMock()
    product1.product_id = None
    product1.reserved = 0

    inventory_mock.get_all_products.return_value = [product1]

    order_item1 = MagicMock()
    order_item1.product_id = None
    order_item1.quantity = 0

    order_mock = MagicMock()
    order_mock.items = [order_item1]

    order_service_mock.get_orders_by_status.return_value = [order_mock]

    checker = ConsistencyChecker(inventory_mock, order_service_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 1

def test_validate_order_reservations_order_with_none_items():
    inventory_mock = MagicMock()
    order_service_mock = MagicMock()

    product1 = MagicMock()
    product1.product_id = "p1"
    product1.reserved = 0

    inventory_mock.get_all_products.return_value = [product1]

    order_mock = MagicMock()
    order_mock.items = None  # invalid items list

    order_service_mock.get_orders_by_status.return_value = [order_mock]

    checker = ConsistencyChecker(inventory_mock, order_service_mock)
    with pytest.raises(TypeError):
        checker.validate_order_reservations()
# AI_TEST_AGENT_END function=ConsistencyChecker.validate_order_reservations

# AI_TEST_AGENT_START function=ConsistencyChecker.get_reservation_summary
def test_get_reservation_summary_with_no_products():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    inventory_mock.get_all_products.return_value = []

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == 0
    assert result["total_reserved"] == 0
    assert result["total_available"] == 0
    assert result["utilization_rate"] == 0.0
    inventory_mock.get_all_products.assert_called_once()


def test_get_reservation_summary_with_normal_values():
    product1 = MagicMock()
    product1.stock = 100
    product1.reserved = 20
    product1.available_stock.return_value = 80
    product1.product_id = "p1"

    product2 = MagicMock()
    product2.stock = 200
    product2.reserved = 50
    product2.available_stock.return_value = 150
    product2.product_id = "p2"

    inventory_mock = MagicMock()
    order_mock = MagicMock()
    inventory_mock.get_all_products.return_value = [product1, product2]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == 300
    assert result["total_reserved"] == 70
    assert result["total_available"] == 230
    assert result["utilization_rate"] == pytest.approx(70 / 300, 0.0001)
    inventory_mock.get_all_products.assert_called_once()


def test_get_reservation_summary_with_zero_total_stock():
    product1 = MagicMock()
    product1.stock = 0
    product1.reserved = 0
    product1.available_stock.return_value = 0
    product1.product_id = "p1"

    inventory_mock = MagicMock()
    order_mock = MagicMock()
    inventory_mock.get_all_products.return_value = [product1]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == 0
    assert result["total_reserved"] == 0
    assert result["total_available"] == 0
    assert result["utilization_rate"] == 0.0
    inventory_mock.get_all_products.assert_called_once()


def test_get_reservation_summary_with_negative_stock_and_reserved():
    product1 = MagicMock()
    product1.stock = -10
    product1.reserved = -5
    product1.available_stock.return_value = -15
    product1.product_id = "p1"

    inventory_mock = MagicMock()
    order_mock = MagicMock()
    inventory_mock.get_all_products.return_value = [product1]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == -10
    assert result["total_reserved"] == -5
    assert result["total_available"] == -15
    # utilization_rate is negative reserved / negative stock = -5 / -10 = 0.5
    assert result["utilization_rate"] == pytest.approx(0.5, 0.0001)
    inventory_mock.get_all_products.assert_called_once()


def test_get_reservation_summary_with_large_stock_and_reserved():
    product1 = MagicMock()
    product1.stock = 1000000
    product1.reserved = 500000
    product1.available_stock.return_value = 500000
    product1.product_id = "p1"

    product2 = MagicMock()
    product2.stock = 500000
    product2.reserved = 250000
    product2.available_stock.return_value = 250000
    product2.product_id = "p2"

    inventory_mock = MagicMock()
    order_mock = MagicMock()
    inventory_mock.get_all_products.return_value = [product1, product2]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == 1500000
    assert result["total_reserved"] == 750000
    assert result["total_available"] == 750000
    assert result["utilization_rate"] == pytest.approx(750000 / 1500000, 0.0001)
    inventory_mock.get_all_products.assert_called_once()


def test_get_reservation_summary_with_available_stock_method_raises():
    product1 = MagicMock()
    product1.stock = 100
    product1.reserved = 20
    product1.product_id = "p1"

    def raise_error():
        raise RuntimeError("available_stock error")

    product1.available_stock.side_effect = raise_error

    inventory_mock = MagicMock()
    order_mock = MagicMock()
    inventory_mock.get_all_products.return_value = [product1]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    with pytest.raises(RuntimeError, match="available_stock error"):
        checker.get_reservation_summary()
    inventory_mock.get_all_products.assert_called_once()


def test_get_reservation_summary_with_non_integer_stock_and_reserved():
    product1 = MagicMock()
    product1.stock = 100.5
    product1.reserved = 20.25
    product1.available_stock.return_value = 80.25
    product1.product_id = "p1"

    inventory_mock = MagicMock()
    order_mock = MagicMock()
    inventory_mock.get_all_products.return_value = [product1]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == 100.5
    assert result["total_reserved"] == 20.25
    assert result["total_available"] == 80.25
    assert result["utilization_rate"] == pytest.approx(20.25 / 100.5, 0.0001)
    inventory_mock.get_all_products.assert_called_once()
# AI_TEST_AGENT_END function=ConsistencyChecker.get_reservation_summary
