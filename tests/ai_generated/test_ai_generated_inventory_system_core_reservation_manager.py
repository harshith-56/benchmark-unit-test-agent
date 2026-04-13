from inventory_system.core.reservation_manager import InsufficientStockError
from inventory_system.core.reservation_manager import ReservationManager
from unittest.mock import MagicMock
import pytest

# AI_TEST_AGENT_START function=ReservationManager.reserve_stock
class DummyProduct:
    def __init__(self, stock, reserved):
        self.stock = stock
        self.reserved = reserved

    def available_stock(self):
        return self.stock - self.reserved

def test_reserve_stock_valid_reservation_increases_reserved():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=2)
    inventory_mock.get_product.return_value = product
    manager = ReservationManager(inventory_mock)

    manager.reserve_stock("prod1", 3)

    assert product.reserved == 5
    inventory_mock.get_product.assert_called_once_with("prod1")

def test_reserve_stock_zero_quantity_raises_value_error():
    inventory_mock = MagicMock()
    manager = ReservationManager(inventory_mock)

    with pytest.raises(ValueError, match="Reservation quantity must be positive"):
        manager.reserve_stock("prod1", 0)
    inventory_mock.get_product.assert_not_called()

def test_reserve_stock_negative_quantity_raises_value_error():
    inventory_mock = MagicMock()
    manager = ReservationManager(inventory_mock)

    with pytest.raises(ValueError, match="Reservation quantity must be positive"):
        manager.reserve_stock("prod1", -5)
    inventory_mock.get_product.assert_not_called()

def test_reserve_stock_insufficient_stock_raises_insufficient_stock_error():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=5, reserved=3)  # available_stock = 2
    inventory_mock.get_product.return_value = product
    manager = ReservationManager(inventory_mock)

    with pytest.raises(InsufficientStockError) as exc_info:
        manager.reserve_stock("prod1", 4)
    assert "Insufficient stock for 'prod1'" in str(exc_info.value)
    assert "requested 4" in str(exc_info.value)
    assert "available 2" in str(exc_info.value)
    inventory_mock.get_product.assert_called_once_with("prod1")

def test_reserve_stock_exact_available_stock_reserves_successfully():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=7, reserved=2)  # available_stock = 5
    inventory_mock.get_product.return_value = product
    manager = ReservationManager(inventory_mock)

    manager.reserve_stock("prod1", 5)

    assert product.reserved == 7
    inventory_mock.get_product.assert_called_once_with("prod1")

def test_reserve_stock_large_quantity_raises_insufficient_stock_error():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=100, reserved=90)  # available_stock = 10
    inventory_mock.get_product.return_value = product
    manager = ReservationManager(inventory_mock)

    with pytest.raises(InsufficientStockError):
        manager.reserve_stock("prod1", 11)
    inventory_mock.get_product.assert_called_once_with("prod1")

def test_reserve_stock_non_integer_quantity_raises_type_error():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=0)
    inventory_mock.get_product.return_value = product
    manager = ReservationManager(inventory_mock)

    with pytest.raises(TypeError):
        manager.reserve_stock("prod1", "5")
    inventory_mock.get_product.assert_not_called()

def test_reserve_stock_none_quantity_raises_type_error():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=0)
    inventory_mock.get_product.return_value = product
    manager = ReservationManager(inventory_mock)

    with pytest.raises(TypeError):
        manager.reserve_stock("prod1", None)
    inventory_mock.get_product.assert_not_called()
# AI_TEST_AGENT_END function=ReservationManager.reserve_stock

# AI_TEST_AGENT_START function=ReservationManager.release_stock
class DummyProduct:
    def __init__(self, stock, reserved):
        self.stock = stock
        self.reserved = reserved

    def available_stock(self):
        return self.stock - self.reserved

def test_release_stock_valid_partial_release():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=5)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    rm.release_stock("prod1", 3)

    assert product.reserved == 2
    inventory_mock.get_product.assert_called_once_with("prod1")

def test_release_stock_release_more_than_reserved_releases_all():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=4)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    rm.release_stock("prod1", 10)

    assert product.reserved == 0
    inventory_mock.get_product.assert_called_once_with("prod1")

def test_release_stock_release_exact_reserved_releases_all():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=7)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    rm.release_stock("prod1", 7)

    assert product.reserved == 0
    inventory_mock.get_product.assert_called_once_with("prod1")

def test_release_stock_zero_quantity_raises_value_error():
    inventory_mock = MagicMock()
    rm = ReservationManager(inventory_mock)

    with pytest.raises(ValueError, match="Release quantity must be positive"):
        rm.release_stock("prod1", 0)

def test_release_stock_negative_quantity_raises_value_error():
    inventory_mock = MagicMock()
    rm = ReservationManager(inventory_mock)

    with pytest.raises(ValueError, match="Release quantity must be positive"):
        rm.release_stock("prod1", -5)

def test_release_stock_product_reserved_zero_no_change():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=0)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    rm.release_stock("prod1", 3)

    assert product.reserved == 0
    inventory_mock.get_product.assert_called_once_with("prod1")

def test_release_stock_called_multiple_times_accumulates_correctly():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=20, reserved=10)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    rm.release_stock("prod1", 4)
    assert product.reserved == 6

    rm.release_stock("prod1", 3)
    assert product.reserved == 3

    rm.release_stock("prod1", 5)
    assert product.reserved == 0

def test_release_stock_non_integer_quantity_raises_type_error():
    inventory_mock = MagicMock()
    rm = ReservationManager(inventory_mock)

    with pytest.raises(TypeError):
        rm.release_stock("prod1", "five")

def test_release_stock_none_quantity_raises_type_error():
    inventory_mock = MagicMock()
    rm = ReservationManager(inventory_mock)

    with pytest.raises(TypeError):
        rm.release_stock("prod1", None)
# AI_TEST_AGENT_END function=ReservationManager.release_stock

# AI_TEST_AGENT_START function=ReservationManager.transfer_reservation
class DummyProduct:
    def __init__(self, stock, reserved):
        self.stock = stock
        self.reserved = reserved

    def available_stock(self):
        return self.stock - self.reserved


def test_transfer_reservation_success_no_change():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=5)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    rm.transfer_reservation("prod1", from_quantity=5, to_quantity=5)

    assert product.reserved == 5
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_success_increase_reservation():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=3)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    rm.transfer_reservation("prod1", from_quantity=3, to_quantity=5)

    assert product.reserved == 5
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_success_decrease_reservation():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=7)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    rm.transfer_reservation("prod1", from_quantity=7, to_quantity=4)

    assert product.reserved == 4
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_insufficient_reserved_raises():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=2)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    with pytest.raises(InsufficientStockError) as excinfo:
        rm.transfer_reservation("prod1", from_quantity=3, to_quantity=5)
    assert "only 2 units reserved" in str(excinfo.value)
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_insufficient_available_stock_raises():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=5, reserved=2)  # available_stock = 3
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    with pytest.raises(InsufficientStockError) as excinfo:
        rm.transfer_reservation("prod1", from_quantity=2, to_quantity=6)  # delta=4 > available_stock=3
    assert "insufficient available stock" in str(excinfo.value)
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_zero_from_quantity_raises():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=5)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    with pytest.raises(InsufficientStockError) as excinfo:
        rm.transfer_reservation("prod1", from_quantity=0, to_quantity=3)
    assert "only 5 units reserved" in str(excinfo.value)
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_negative_to_quantity_decreases_reservation():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=6)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    rm.transfer_reservation("prod1", from_quantity=6, to_quantity=2)

    assert product.reserved == 2
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_negative_from_and_to_quantity_raises():
    inventory_mock = MagicMock()
    product = DummyProduct(stock=10, reserved=3)
    inventory_mock.get_product.return_value = product
    rm = ReservationManager(inventory_mock)

    with pytest.raises(InsufficientStockError) as excinfo:
        rm.transfer_reservation("prod1", from_quantity=4, to_quantity=1)
    assert "only 3 units reserved" in str(excinfo.value)
    inventory_mock.get_product.assert_called_once_with("prod1")
# AI_TEST_AGENT_END function=ReservationManager.transfer_reservation
