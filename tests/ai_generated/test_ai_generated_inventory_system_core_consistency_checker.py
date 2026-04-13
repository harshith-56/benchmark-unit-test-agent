from inventory_system.core.consistency_checker import ConsistencyChecker
from inventory_system.core.consistency_checker import OrderStatus
from unittest.mock import MagicMock
import pytest

# AI_TEST_AGENT_START function=ConsistencyChecker.validate_inventory_state
class DummyProduct:
    def __init__(self, product_id, stock, reserved, available_stock_return):
        self.product_id = product_id
        self.stock = stock
        self.reserved = reserved
        self._available_stock_return = available_stock_return

    def available_stock(self):
        return self._available_stock_return

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
    p1 = DummyProduct("p1", 10, 5, 5)
    p2 = DummyProduct("p1", 20, 10, 10)
    inventory_mock.get_all_products.return_value = [p1, p2]
    checker = ConsistencyChecker(inventory_mock, order_mock)

    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert "Duplicate product ID detected: 'p1'" in result["errors"]
    assert result["products_checked"] == 2

def test_validate_inventory_state_stock_less_equal_reserved_and_negative_values():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p1 = DummyProduct("p1", 5, 5, 0)
    p2 = DummyProduct("p2", -1, 0, 0)
    p3 = DummyProduct("p3", 10, -2, 0)
    inventory_mock.get_all_products.return_value = [p1, p2, p3]
    checker = ConsistencyChecker(inventory_mock, order_mock)

    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert f"Product 'p1': stock (5) inconsistent with reserved (5)" in result["errors"]
    assert f"Product 'p2': negative stock value (-1)" in result["errors"]
    assert f"Product 'p3': negative reserved value (-2)" in result["errors"]
    assert result["products_checked"] == 3

def test_validate_inventory_state_high_stock_warning():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p1 = DummyProduct("p1", 10001, 0, 10001)
    inventory_mock.get_all_products.return_value = [p1]
    checker = ConsistencyChecker(inventory_mock, order_mock)

    result = checker.validate_inventory_state()

    assert result["valid"] is True
    assert result["errors"] == []
    assert f"Product 'p1': unusually high stock level (10001)" in result["warnings"]
    assert result["products_checked"] == 1

def test_validate_inventory_state_multiple_errors_and_warnings():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p1 = DummyProduct("p1", 0, 1, 0)
    p2 = DummyProduct("p1", -5, -1, 0)
    p3 = DummyProduct("p3", 15000, 0, 15000)
    inventory_mock.get_all_products.return_value = [p1, p2, p3]
    checker = ConsistencyChecker(inventory_mock, order_mock)

    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert f"Duplicate product ID detected: 'p1'" in result["errors"]
    assert f"Product 'p1': stock (0) inconsistent with reserved (1)" in result["errors"]
    assert f"Product 'p1': negative stock value (-5)" in result["errors"]
    assert f"Product 'p1': negative reserved value (-1)" in result["errors"]
    assert f"Product 'p3': unusually high stock level (15000)" in result["warnings"]
    assert result["products_checked"] == 3

def test_validate_inventory_state_single_product_valid():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p1 = DummyProduct("p1", 10, 5, 5)
    inventory_mock.get_all_products.return_value = [p1]
    checker = ConsistencyChecker(inventory_mock, order_mock)

    result = checker.validate_inventory_state()

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["warnings"] == []
    assert result["products_checked"] == 1

def test_validate_inventory_state_product_stock_equals_reserved_edge_case():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p1 = DummyProduct("p1", 5, 5, 0)
    inventory_mock.get_all_products.return_value = [p1]
    checker = ConsistencyChecker(inventory_mock, order_mock)

    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert f"Product 'p1': stock (5) inconsistent with reserved (5)" in result["errors"]
    assert result["products_checked"] == 1

def test_validate_inventory_state_product_stock_less_than_reserved_edge_case():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    p1 = DummyProduct("p1", 4, 5, 0)
    inventory_mock.get_all_products.return_value = [p1]
    checker = ConsistencyChecker(inventory_mock, order_mock)

    result = checker.validate_inventory_state()

    assert result["valid"] is False
    assert f"Product 'p1': stock (4) inconsistent with reserved (5)" in result["errors"]
    assert result["products_checked"] == 1
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

def test_validate_order_reservations_no_confirmed_orders_no_products():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    inventory_mock.get_all_products.return_value = []
    order_mock.get_orders_by_status.return_value = []

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 0
    inventory_mock.get_all_products.assert_called_once()
    order_mock.get_orders_by_status.assert_called_once_with(OrderStatus.CONFIRMED)

def test_validate_order_reservations_confirmed_orders_match_reserved():
    inventory_mock = MagicMock()
    order_mock = MagicMock()

    product1 = DummyProduct("p1", reserved=3)
    product2 = DummyProduct("p2", reserved=5)
    inventory_mock.get_all_products.return_value = [product1, product2]

    order1 = DummyOrder([DummyItem("p1", 3)])
    order2 = DummyOrder([DummyItem("p2", 5)])
    order_mock.get_orders_by_status.return_value = [order1, order2]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 2
    inventory_mock.get_all_products.assert_called_once()
    order_mock.get_orders_by_status.assert_called_once_with(OrderStatus.CONFIRMED)

def test_validate_order_reservations_confirmed_orders_reserved_mismatch():
    inventory_mock = MagicMock()
    order_mock = MagicMock()

    product1 = DummyProduct("p1", reserved=2)
    product2 = DummyProduct("p2", reserved=7)
    inventory_mock.get_all_products.return_value = [product1, product2]

    order1 = DummyOrder([DummyItem("p1", 3)])
    order2 = DummyOrder([DummyItem("p2", 5)])
    order_mock.get_orders_by_status.return_value = [order1, order2]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is False
    assert len(result["mismatches"]) == 2
    mismatch_p1 = next(m for m in result["mismatches"] if m["product_id"] == "p1")
    mismatch_p2 = next(m for m in result["mismatches"] if m["product_id"] == "p2")
    assert mismatch_p1["expected_reserved"] == 3
    assert mismatch_p1["actual_reserved"] == 2
    assert mismatch_p1["delta"] == -1
    assert mismatch_p2["expected_reserved"] == 5
    assert mismatch_p2["actual_reserved"] == 7
    assert mismatch_p2["delta"] == 2
    assert result["orders_checked"] == 2
    inventory_mock.get_all_products.assert_called_once()
    order_mock.get_orders_by_status.assert_called_once_with(OrderStatus.CONFIRMED)

def test_validate_order_reservations_confirmed_orders_some_products_missing_in_inventory():
    inventory_mock = MagicMock()
    order_mock = MagicMock()

    product1 = DummyProduct("p1", reserved=3)
    inventory_mock.get_all_products.return_value = [product1]

    order1 = DummyOrder([DummyItem("p1", 3), DummyItem("p2", 4)])
    order_mock.get_orders_by_status.return_value = [order1]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is False
    assert len(result["mismatches"]) == 1
    mismatch = result["mismatches"][0]
    assert mismatch["product_id"] == "p1"
    assert mismatch["expected_reserved"] == 3
    assert mismatch["actual_reserved"] == 3
    assert mismatch["delta"] == 0
    assert result["orders_checked"] == 1
    inventory_mock.get_all_products.assert_called_once()
    order_mock.get_orders_by_status.assert_called_once_with(OrderStatus.CONFIRMED)

def test_validate_order_reservations_confirmed_orders_empty_items():
    inventory_mock = MagicMock()
    order_mock = MagicMock()

    product1 = DummyProduct("p1", reserved=0)
    inventory_mock.get_all_products.return_value = [product1]

    order1 = DummyOrder([])
    order_mock.get_orders_by_status.return_value = [order1]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 1
    inventory_mock.get_all_products.assert_called_once()
    order_mock.get_orders_by_status.assert_called_once_with(OrderStatus.CONFIRMED)

def test_validate_order_reservations_confirmed_orders_with_zero_quantity_items():
    inventory_mock = MagicMock()
    order_mock = MagicMock()

    product1 = DummyProduct("p1", reserved=0)
    inventory_mock.get_all_products.return_value = [product1]

    order1 = DummyOrder([DummyItem("p1", 0)])
    order_mock.get_orders_by_status.return_value = [order1]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_order_reservations()

    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 1
    inventory_mock.get_all_products.assert_called_once()
    order_mock.get_orders_by_status.assert_called_once_with(OrderStatus.CONFIRMED)

def test_validate_order_reservations_confirmed_orders_with_negative_quantity_items():
    inventory_mock = MagicMock()
    order_mock = MagicMock()

    product1 = DummyProduct("p1", reserved=0)
    inventory_mock.get_all_products.return_value = [product1]

    order1 = DummyOrder([DummyItem("p1", -1)])
    order_mock.get_orders_by_status.return_value = [order1]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_order_reservations()

    # Negative quantity is accepted by code as no validation is shown
    # So expected_reserved will be -1, actual_reserved 0, mismatch present
    assert result["consistent"] is False
    assert len(result["mismatches"]) == 1
    mismatch = result["mismatches"][0]
    assert mismatch["product_id"] == "p1"
    assert mismatch["expected_reserved"] == -1
    assert mismatch["actual_reserved"] == 0
    assert mismatch["delta"] == 0 - (-1)
    assert result["orders_checked"] == 1
    inventory_mock.get_all_products.assert_called_once()
    order_mock.get_orders_by_status.assert_called_once_with(OrderStatus.CONFIRMED)

def test_validate_order_reservations_confirmed_orders_with_duplicate_product_ids_in_items():
    inventory_mock = MagicMock()
    order_mock = MagicMock()

    product1 = DummyProduct("p1", reserved=5)
    inventory_mock.get_all_products.return_value = [product1]

    order1 = DummyOrder([DummyItem("p1", 2), DummyItem("p1", 3)])
    order_mock.get_orders_by_status.return_value = [order1]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.validate_order_reservations()

    # Expected reserved is sum of quantities for product_id p1: 2+3=5, matches reserved 5
    assert result["consistent"] is True
    assert result["mismatches"] == []
    assert result["orders_checked"] == 1
    inventory_mock.get_all_products.assert_called_once()
    order_mock.get_orders_by_status.assert_called_once_with(OrderStatus.CONFIRMED)
# AI_TEST_AGENT_END function=ConsistencyChecker.validate_order_reservations

# AI_TEST_AGENT_START function=ConsistencyChecker.get_reservation_summary
def test_get_reservation_summary_with_multiple_products():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
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
    inventory_mock.get_all_products.return_value = [product1, product2]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == 300  # sum of 100 + 200
    assert result["total_reserved"] == 70  # sum of 20 + 50
    assert result["total_available"] == 230  # sum of 80 + 150
    assert result["utilization_rate"] == pytest.approx(70 / 300, 0.0001)


def test_get_reservation_summary_with_zero_total_stock():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    product = MagicMock()
    product.stock = 0
    product.reserved = 0
    product.available_stock.return_value = 0
    product.product_id = "p1"
    inventory_mock.get_all_products.return_value = [product]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == 0
    assert result["total_reserved"] == 0
    assert result["total_available"] == 0
    assert result["utilization_rate"] == 0.0


def test_get_reservation_summary_with_negative_stock_and_reserved():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    product = MagicMock()
    product.stock = -10
    product.reserved = -5
    product.available_stock.return_value = -15
    product.product_id = "p1"
    inventory_mock.get_all_products.return_value = [product]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == -10
    assert result["total_reserved"] == -5
    assert result["total_available"] == -15
    # utilization_rate = reserved / stock = -5 / -10 = 0.5
    assert result["utilization_rate"] == pytest.approx(0.5, 0.0001)


def test_get_reservation_summary_with_empty_product_list():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    inventory_mock.get_all_products.return_value = []

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == 0
    assert result["total_reserved"] == 0
    assert result["total_available"] == 0
    assert result["utilization_rate"] == 0.0


def test_get_reservation_summary_with_available_stock_method_raising():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    product = MagicMock()
    product.stock = 10
    product.reserved = 5
    product.product_id = "p1"

    def raise_error():
        raise RuntimeError("Error in available_stock")

    product.available_stock.side_effect = raise_error
    inventory_mock.get_all_products.return_value = [product]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    with pytest.raises(RuntimeError, match="Error in available_stock"):
        checker.get_reservation_summary()


def test_get_reservation_summary_with_non_integer_stock_and_reserved():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    product = MagicMock()
    product.stock = 10.5
    product.reserved = 3.2
    product.available_stock.return_value = 7.3
    product.product_id = "p1"
    inventory_mock.get_all_products.return_value = [product]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == 10.5
    assert result["total_reserved"] == 3.2
    assert result["total_available"] == 7.3
    assert result["utilization_rate"] == pytest.approx(3.2 / 10.5, 0.0001)


def test_get_reservation_summary_with_large_stock_and_reserved():
    inventory_mock = MagicMock()
    order_mock = MagicMock()
    product = MagicMock()
    product.stock = 1_000_000
    product.reserved = 500_000
    product.available_stock.return_value = 500_000
    product.product_id = "p1"
    inventory_mock.get_all_products.return_value = [product]

    checker = ConsistencyChecker(inventory_mock, order_mock)
    result = checker.get_reservation_summary()

    assert result["total_stock"] == 1_000_000
    assert result["total_reserved"] == 500_000
    assert result["total_available"] == 500_000
    assert result["utilization_rate"] == pytest.approx(0.5, 0.0001)
# AI_TEST_AGENT_END function=ConsistencyChecker.get_reservation_summary
