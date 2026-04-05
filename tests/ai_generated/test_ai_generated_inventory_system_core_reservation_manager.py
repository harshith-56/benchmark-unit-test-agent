from inventory_system.core.reservation_manager import InsufficientStockError
from inventory_system.core.reservation_manager import ReservationManager
from unittest.mock import MagicMock
import pytest

# AI_TEST_AGENT_START function=ReservationManager.reserve_stock
class InsufficientStockError(Exception):
    pass

def test_reserve_stock_raises_value_error_for_zero_quantity():
    rm = ReservationManager()
    rm._inventory = MagicMock()
    with pytest.raises(ValueError, match="Reservation quantity must be positive"):
        rm.reserve_stock("prod1", 0)
    rm._inventory.get_product.assert_not_called()

def test_reserve_stock_raises_value_error_for_negative_quantity():
    rm = ReservationManager()
    rm._inventory = MagicMock()
    with pytest.raises(ValueError, match="Reservation quantity must be positive"):
        rm.reserve_stock("prod1", -5)
    rm._inventory.get_product.assert_not_called()

def test_reserve_stock_raises_insufficient_stock_error_when_stock_less_than_quantity():
    rm = ReservationManager()
    product_mock = MagicMock()
    product_mock.stock = 3
    product_mock.available_stock.return_value = 3
    rm._inventory = MagicMock()
    rm._inventory.get_product.return_value = product_mock

    with pytest.raises(InsufficientStockError) as excinfo:
        rm.reserve_stock("prod1", 5)
    assert "Insufficient stock for 'prod1': requested 5, available 3" in str(excinfo.value)
    rm._inventory.get_product.assert_called_once_with("prod1")
    product_mock.available_stock.assert_called_once()
    assert product_mock.reserved == 0

def test_reserve_stock_increments_reserved_when_stock_sufficient():
    rm = ReservationManager()
    product_mock = MagicMock()
    product_mock.stock = 10
    product_mock.available_stock.return_value = 10
    product_mock.reserved = 2
    rm._inventory = MagicMock()
    rm._inventory.get_product.return_value = product_mock

    rm.reserve_stock("prod1", 5)

    rm._inventory.get_product.assert_called_once_with("prod1")
    product_mock.available_stock.assert_not_called()  # Not called if stock >= quantity
    assert product_mock.reserved == 7

def test_reserve_stock_raises_type_error_for_non_int_quantity():
    rm = ReservationManager()
    rm._inventory = MagicMock()
    with pytest.raises(TypeError):
        rm.reserve_stock("prod1", "five")
    rm._inventory.get_product.assert_not_called()

def test_reserve_stock_raises_type_error_for_none_quantity():
    rm = ReservationManager()
    rm._inventory = MagicMock()
    with pytest.raises(TypeError):
        rm.reserve_stock("prod1", None)
    rm._inventory.get_product.assert_not_called()

def test_reserve_stock_raises_attribute_error_if_product_has_no_stock():
    rm = ReservationManager()
    product_mock = MagicMock()
    del product_mock.stock
    rm._inventory = MagicMock()
    rm._inventory.get_product.return_value = product_mock

    with pytest.raises(AttributeError):
        rm.reserve_stock("prod1", 1)
    rm._inventory.get_product.assert_called_once_with("prod1")

def test_reserve_stock_raises_attribute_error_if_product_has_no_reserved():
    rm = ReservationManager()
    product_mock = MagicMock()
    product_mock.stock = 10
    product_mock.available_stock.return_value = 10
    del product_mock.reserved
    rm._inventory = MagicMock()
    rm._inventory.get_product.return_value = product_mock

    with pytest.raises(AttributeError):
        rm.reserve_stock("prod1", 1)
    rm._inventory.get_product.assert_called_once_with("prod1")

def test_reserve_stock_raises_attribute_error_if_product_has_no_available_stock_method():
    rm = ReservationManager()
    product_mock = MagicMock()
    product_mock.stock = 10
    product_mock.reserved = 0
    del product_mock.available_stock
    rm._inventory = MagicMock()
    rm._inventory.get_product.return_value = product_mock

    with pytest.raises(AttributeError):
        rm.reserve_stock("prod1", 1)
    rm._inventory.get_product.assert_called_once_with("prod1")
# AI_TEST_AGENT_END function=ReservationManager.reserve_stock

# AI_TEST_AGENT_START function=ReservationManager.release_stock
def test_release_stock_quantity_zero_raises_value_error():
    rm = ReservationManager()
    with pytest.raises(ValueError, match="Release quantity must be positive"):
        rm.release_stock("prod1", 0)

def test_release_stock_quantity_negative_raises_value_error():
    rm = ReservationManager()
    with pytest.raises(ValueError, match="Release quantity must be positive"):
        rm.release_stock("prod1", -5)

def test_release_stock_releases_exact_reserved_quantity():
    rm = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 10
    rm._inventory = MagicMock()
    rm._inventory.get_product.return_value = product_mock

    rm.release_stock("prod1", 10)

    assert product_mock.reserved == 0
    rm._inventory.get_product.assert_called_once_with("prod1")

def test_release_stock_releases_less_than_reserved_quantity():
    rm = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 10
    rm._inventory = MagicMock()
    rm._inventory.get_product.return_value = product_mock

    rm.release_stock("prod1", 5)

    assert product_mock.reserved == 5
    rm._inventory.get_product.assert_called_once_with("prod1")

def test_release_stock_releases_more_than_reserved_quantity_only_reserved_released():
    rm = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 7
    rm._inventory = MagicMock()
    rm._inventory.get_product.return_value = product_mock

    rm.release_stock("prod1", 10)

    assert product_mock.reserved == 0
    rm._inventory.get_product.assert_called_once_with("prod1")

def test_release_stock_product_reserved_zero_no_change():
    rm = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 0
    rm._inventory = MagicMock()
    rm._inventory.get_product.return_value = product_mock

    rm.release_stock("prod1", 5)

    assert product_mock.reserved == 0
    rm._inventory.get_product.assert_called_once_with("prod1")

def test_release_stock_product_reserved_none_type_raises_attribute_error():
    rm = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = None
    rm._inventory = MagicMock()
    rm._inventory.get_product.return_value = product_mock

    with pytest.raises(TypeError):
        rm.release_stock("prod1", 5)

def test_release_stock_product_none_raises_attribute_error():
    rm = ReservationManager()
    rm._inventory = MagicMock()
    rm._inventory.get_product.return_value = None

    with pytest.raises(AttributeError):
        rm.release_stock("prod1", 5)
# AI_TEST_AGENT_END function=ReservationManager.release_stock

# AI_TEST_AGENT_START function=ReservationManager.transfer_reservation
def test_transfer_reservation_raises_if_reserved_less_than_from_quantity():
    manager = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 2
    manager._inventory = MagicMock()
    manager._inventory.get_product.return_value = product_mock

    with pytest.raises(InsufficientStockError, match="Cannot transfer: only 2 units reserved for 'prod1'"):
        manager.transfer_reservation("prod1", from_quantity=3, to_quantity=1)

    manager._inventory.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_increases_reserved_when_delta_positive_and_available_stock_sufficient():
    manager = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 5
    product_mock.available_stock.return_value = 10
    manager._inventory = MagicMock()
    manager._inventory.get_product.return_value = product_mock

    manager.transfer_reservation("prod2", from_quantity=3, to_quantity=6)

    assert product_mock.reserved == 8
    manager._inventory.get_product.assert_called_once_with("prod2")
    product_mock.available_stock.assert_called_once()


def test_transfer_reservation_raises_if_delta_positive_and_available_stock_insufficient():
    manager = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 4
    product_mock.available_stock.return_value = 1
    manager._inventory = MagicMock()
    manager._inventory.get_product.return_value = product_mock

    with pytest.raises(InsufficientStockError, match="Cannot increase reservation: insufficient available stock for 'prod3'"):
        manager.transfer_reservation("prod3", from_quantity=2, to_quantity=5)

    manager._inventory.get_product.assert_called_once_with("prod3")
    product_mock.available_stock.assert_called_once()


def test_transfer_reservation_decreases_reserved_when_delta_negative():
    manager = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 7
    manager._inventory = MagicMock()
    manager._inventory.get_product.return_value = product_mock

    manager.transfer_reservation("prod4", from_quantity=5, to_quantity=3)

    assert product_mock.reserved == 5
    manager._inventory.get_product.assert_called_once_with("prod4")


def test_transfer_reservation_no_change_when_delta_zero():
    manager = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 10
    manager._inventory = MagicMock()
    manager._inventory.get_product.return_value = product_mock

    manager.transfer_reservation("prod5", from_quantity=4, to_quantity=4)

    assert product_mock.reserved == 10
    manager._inventory.get_product.assert_called_once_with("prod5")


def test_transfer_reservation_raises_if_product_reserved_is_zero_and_from_quantity_positive():
    manager = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 0
    manager._inventory = MagicMock()
    manager._inventory.get_product.return_value = product_mock

    with pytest.raises(InsufficientStockError, match="Cannot transfer: only 0 units reserved for 'prod6'"):
        manager.transfer_reservation("prod6", from_quantity=1, to_quantity=0)

    manager._inventory.get_product.assert_called_once_with("prod6")


def test_transfer_reservation_raises_if_product_reserved_is_negative_and_from_quantity_positive():
    manager = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = -1
    manager._inventory = MagicMock()
    manager._inventory.get_product.return_value = product_mock

    with pytest.raises(InsufficientStockError, match="Cannot transfer: only -1 units reserved for 'prod7'"):
        manager.transfer_reservation("prod7", from_quantity=1, to_quantity=0)

    manager._inventory.get_product.assert_called_once_with("prod7")


def test_transfer_reservation_handles_zero_from_and_to_quantity():
    manager = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 0
    product_mock.available_stock.return_value = 5
    manager._inventory = MagicMock()
    manager._inventory.get_product.return_value = product_mock

    manager.transfer_reservation("prod8", from_quantity=0, to_quantity=0)

    assert product_mock.reserved == 0
    manager._inventory.get_product.assert_called_once_with("prod8")
    product_mock.available_stock.assert_not_called()


def test_transfer_reservation_raises_type_error_on_invalid_input_types():
    manager = ReservationManager()
    product_mock = MagicMock()
    product_mock.reserved = 5
    product_mock.available_stock.return_value = 5
    manager._inventory = MagicMock()
    manager._inventory.get_product.return_value = product_mock

    with pytest.raises(TypeError):
        manager.transfer_reservation("prod9", from_quantity="3", to_quantity=5)

    with pytest.raises(TypeError):
        manager.transfer_reservation("prod9", from_quantity=3, to_quantity="5")
# AI_TEST_AGENT_END function=ReservationManager.transfer_reservation
