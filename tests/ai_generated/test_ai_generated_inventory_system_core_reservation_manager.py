from inventory_system.core.reservation_manager import InsufficientStockError
from inventory_system.core.reservation_manager import ReservationManager
from inventory_system.core.reservation_manager import ReservationManager, InsufficientStockError
from unittest.mock import MagicMock
import pytest

# AI_TEST_AGENT_START function=ReservationManager.reserve_stock
def test_reserve_stock_positive_quantity_sufficient_stock():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.stock = 10
    product_mock.reserved = 2
    product_mock.available_stock.return_value = 8
    inventory_mock.get_product.return_value = product_mock

    manager = ReservationManager(inventory_mock)
    manager.reserve_stock("prod1", 5)

    inventory_mock.get_product.assert_called_once_with("prod1")
    assert product_mock.reserved == 7

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
        manager.reserve_stock("prod1", -3)

    inventory_mock.get_product.assert_not_called()

def test_reserve_stock_insufficient_stock_raises_insufficient_stock_error():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.stock = 5
    product_mock.reserved = 1
    product_mock.available_stock.return_value = 4
    inventory_mock.get_product.return_value = product_mock

    manager = ReservationManager(inventory_mock)

    with pytest.raises(InsufficientStockError, match="Insufficient stock for 'prod1': requested 6, available 4"):
        manager.reserve_stock("prod1", 6)

    inventory_mock.get_product.assert_called_once_with("prod1")
    assert product_mock.reserved == 1

def test_reserve_stock_quantity_equals_stock_allows_reservation():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.stock = 5
    product_mock.reserved = 0
    product_mock.available_stock.return_value = 5
    inventory_mock.get_product.return_value = product_mock

    manager = ReservationManager(inventory_mock)
    manager.reserve_stock("prod1", 5)

    inventory_mock.get_product.assert_called_once_with("prod1")
    assert product_mock.reserved == 5

def test_reserve_stock_quantity_equals_available_stock_allows_reservation():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.stock = 10
    product_mock.reserved = 3
    product_mock.available_stock.return_value = 7
    inventory_mock.get_product.return_value = product_mock

    manager = ReservationManager(inventory_mock)
    manager.reserve_stock("prod1", 7)

    inventory_mock.get_product.assert_called_once_with("prod1")
    assert product_mock.reserved == 10

def test_reserve_stock_quantity_greater_than_available_stock_raises_error():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.stock = 10
    product_mock.reserved = 5
    product_mock.available_stock.return_value = 5
    inventory_mock.get_product.return_value = product_mock

    manager = ReservationManager(inventory_mock)

    with pytest.raises(InsufficientStockError, match="Insufficient stock for 'prod1': requested 6, available 5"):
        manager.reserve_stock("prod1", 6)

    inventory_mock.get_product.assert_called_once_with("prod1")
    assert product_mock.reserved == 5

def test_reserve_stock_non_integer_quantity_raises_type_error():
    inventory_mock = MagicMock()
    manager = ReservationManager(inventory_mock)

    with pytest.raises(TypeError):
        manager.reserve_stock("prod1", "five")

def test_reserve_stock_none_quantity_raises_type_error():
    inventory_mock = MagicMock()
    manager = ReservationManager(inventory_mock)

    with pytest.raises(TypeError):
        manager.reserve_stock("prod1", None)
# AI_TEST_AGENT_END function=ReservationManager.reserve_stock

# AI_TEST_AGENT_START function=ReservationManager.release_stock
def test_release_stock_valid_quantity_less_than_reserved():
    mock_inventory = MagicMock()
    product = MagicMock()
    product.reserved = 10
    mock_inventory.get_product.return_value = product
    rm = ReservationManager(mock_inventory)

    rm.release_stock("prod1", 5)

    assert product.reserved == 5
    mock_inventory.get_product.assert_called_once_with("prod1")

def test_release_stock_valid_quantity_equal_to_reserved():
    mock_inventory = MagicMock()
    product = MagicMock()
    product.reserved = 7
    mock_inventory.get_product.return_value = product
    rm = ReservationManager(mock_inventory)

    rm.release_stock("prod2", 7)

    assert product.reserved == 0
    mock_inventory.get_product.assert_called_once_with("prod2")

def test_release_stock_valid_quantity_greater_than_reserved():
    mock_inventory = MagicMock()
    product = MagicMock()
    product.reserved = 3
    mock_inventory.get_product.return_value = product
    rm = ReservationManager(mock_inventory)

    rm.release_stock("prod3", 10)

    assert product.reserved == 0
    mock_inventory.get_product.assert_called_once_with("prod3")

def test_release_stock_zero_quantity_raises_value_error():
    mock_inventory = MagicMock()
    rm = ReservationManager(mock_inventory)

    with pytest.raises(ValueError, match="Release quantity must be positive"):
        rm.release_stock("prod4", 0)

def test_release_stock_negative_quantity_raises_value_error():
    mock_inventory = MagicMock()
    rm = ReservationManager(mock_inventory)

    with pytest.raises(ValueError, match="Release quantity must be positive"):
        rm.release_stock("prod5", -1)

def test_release_stock_calls_get_product_once():
    mock_inventory = MagicMock()
    product = MagicMock()
    product.reserved = 4
    mock_inventory.get_product.return_value = product
    rm = ReservationManager(mock_inventory)

    rm.release_stock("prod6", 2)

    mock_inventory.get_product.assert_called_once_with("prod6")

def test_release_stock_reserved_does_not_go_negative():
    mock_inventory = MagicMock()
    product = MagicMock()
    product.reserved = 1
    mock_inventory.get_product.return_value = product
    rm = ReservationManager(mock_inventory)

    rm.release_stock("prod7", 5)

    assert product.reserved == 0
    mock_inventory.get_product.assert_called_once_with("prod7")
# AI_TEST_AGENT_END function=ReservationManager.release_stock

# AI_TEST_AGENT_START function=ReservationManager.transfer_reservation
def test_transfer_reservation_success_decrease_reserved():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.reserved = 10
    product_mock.available_stock.return_value = 5
    inventory_mock.get_product.return_value = product_mock

    rm = ReservationManager(inventory_mock)
    rm.transfer_reservation("prod1", from_quantity=10, to_quantity=5)

    assert product_mock.reserved == 5
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_success_increase_reserved_with_sufficient_stock():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.reserved = 5
    product_mock.available_stock.return_value = 10
    inventory_mock.get_product.return_value = product_mock

    rm = ReservationManager(inventory_mock)
    rm.transfer_reservation("prod1", from_quantity=5, to_quantity=8)

    assert product_mock.reserved == 8
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_raises_insufficient_stock_error_when_reserved_less_than_from_quantity():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.reserved = 3
    product_mock.available_stock.return_value = 10
    inventory_mock.get_product.return_value = product_mock

    rm = ReservationManager(inventory_mock)
    with pytest.raises(InsufficientStockError) as excinfo:
        rm.transfer_reservation("prod1", from_quantity=5, to_quantity=7)
    assert "only 3 units reserved for 'prod1'" in str(excinfo.value)
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_raises_insufficient_stock_error_when_increasing_reservation_but_insufficient_available_stock():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.reserved = 5
    product_mock.available_stock.return_value = 2
    inventory_mock.get_product.return_value = product_mock

    rm = ReservationManager(inventory_mock)
    with pytest.raises(InsufficientStockError) as excinfo:
        rm.transfer_reservation("prod1", from_quantity=5, to_quantity=10)
    assert "insufficient available stock for 'prod1'" in str(excinfo.value)
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_no_change_when_from_quantity_equals_to_quantity():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.reserved = 7
    product_mock.available_stock.return_value = 5
    inventory_mock.get_product.return_value = product_mock

    rm = ReservationManager(inventory_mock)
    rm.transfer_reservation("prod1", from_quantity=7, to_quantity=7)

    assert product_mock.reserved == 7
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_with_zero_from_quantity_raises_insufficient_stock_error():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.reserved = 0
    product_mock.available_stock.return_value = 10
    inventory_mock.get_product.return_value = product_mock

    rm = ReservationManager(inventory_mock)
    with pytest.raises(InsufficientStockError) as excinfo:
        rm.transfer_reservation("prod1", from_quantity=1, to_quantity=2)
    assert "only 0 units reserved for 'prod1'" in str(excinfo.value)
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_with_negative_from_quantity_raises_insufficient_stock_error():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.reserved = 5
    product_mock.available_stock.return_value = 10
    inventory_mock.get_product.return_value = product_mock

    rm = ReservationManager(inventory_mock)
    with pytest.raises(InsufficientStockError) as excinfo:
        rm.transfer_reservation("prod1", from_quantity=-1, to_quantity=2)
    assert "only 5 units reserved for 'prod1'" in str(excinfo.value)
    inventory_mock.get_product.assert_called_once_with("prod1")


def test_transfer_reservation_with_negative_to_quantity_decreases_reserved():
    inventory_mock = MagicMock()
    product_mock = MagicMock()
    product_mock.reserved = 10
    product_mock.available_stock.return_value = 5
    inventory_mock.get_product.return_value = product_mock

    rm = ReservationManager(inventory_mock)
    rm.transfer_reservation("prod1", from_quantity=10, to_quantity=5)

    assert product_mock.reserved == 5
    inventory_mock.get_product.assert_called_once_with("prod1")
# AI_TEST_AGENT_END function=ReservationManager.transfer_reservation
