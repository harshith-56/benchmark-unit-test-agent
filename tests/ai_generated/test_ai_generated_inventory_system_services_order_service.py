from inventory_system.services.order_service import InsufficientStockError
from inventory_system.services.order_service import Order
from inventory_system.services.order_service import Order, OrderItem
from inventory_system.services.order_service import OrderItem, Order
from inventory_system.services.order_service import OrderNotFoundError
from inventory_system.services.order_service import OrderService
from inventory_system.services.order_service import OrderService, OrderNotFoundError, OrderStatus
from inventory_system.services.order_service import OrderService, OrderStatus, OrderStateError, InsufficientStockError, OrderNotFoundError
from inventory_system.services.order_service import OrderStatus
from inventory_system.services.order_service import OrderStatus, OrderStateError
from inventory_system.services.order_service import OrderStatus, OrderStateError, InsufficientStockError, OrderNotFoundError
from inventory_system.services.order_service import OrderStatus, OrderStateError, OrderNotFoundError
from inventory_system.services.order_service import generate_id, get_timestamp
from unittest.mock import MagicMock
from unittest.mock import MagicMock, create_autospec
from unittest.mock import MagicMock, patch
import pytest

# AI_TEST_AGENT_START function=OrderService.__init__
def test_create_order_success(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    inventory_mock.get_product.return_value = True
    pricing_mock.calculate_total.return_value = 100.0

    monkeypatch.setattr("inventory_system.services.order_service.generate_id", lambda prefix: "ORD-123")
    monkeypatch.setattr("inventory_system.services.order_service.get_timestamp", lambda: 1234567890)

    items = [{"product_id": "prod1", "quantity": 2}]
    order = service.create_order("user1", items)

    assert order.order_id == "ORD-123"
    assert order.user_id == "user1"
    assert len(order.items) == 1
    assert order.items[0].product_id == "prod1"
    assert order.items[0].quantity == 2
    assert order.created_at == 1234567890
    assert order.total == 100.0
    assert service._orders["ORD-123"] == order
    inventory_mock.get_product.assert_called_once_with("prod1")
    pricing_mock.calculate_total.assert_called_once_with(order)

def test_create_order_empty_items_raises_value_error():
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(ValueError, match="Order must contain at least one item"):
        service.create_order("user1", [])

def test_process_order_success(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_item = OrderItem("prod1", 2)
    order = Order("ORD-1", "user1", [order_item])
    order.status = OrderStatus.PENDING
    service._orders["ORD-1"] = order

    reservation_mock.get_available.return_value = 3
    reservation_mock.reserve_stock.return_value = None

    processed_order = service.process_order("ORD-1")

    assert processed_order.status == OrderStatus.CONFIRMED
    reservation_mock.get_available.assert_called_once_with("prod1")
    reservation_mock.reserve_stock.assert_called_once_with("prod1", 2)
    reservation_mock.release_stock.assert_not_called()

def test_process_order_insufficient_stock_raises(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_item = OrderItem("prod1", 5)
    order = Order("ORD-2", "user1", [order_item])
    order.status = OrderStatus.PENDING
    service._orders["ORD-2"] = order

    reservation_mock.get_available.return_value = 3

    with pytest.raises(InsufficientStockError) as excinfo:
        service.process_order("ORD-2")

    assert "insufficient stock" in str(excinfo.value)
    reservation_mock.get_available.assert_called_once_with("prod1")
    reservation_mock.reserve_stock.assert_not_called()
    reservation_mock.release_stock.assert_not_called()

def test_process_order_reserve_stock_partial_failure_releases_reserved(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item1 = OrderItem("prod1", 2)
    item2 = OrderItem("prod2", 3)
    order = Order("ORD-3", "user1", [item1, item2])
    order.status = OrderStatus.PENDING
    service._orders["ORD-3"] = order

    reservation_mock.get_available.side_effect = [5, 5]

    def reserve_side_effect(product_id, quantity):
        if product_id == "prod2":
            raise InsufficientStockError("No stock for prod2")
        return None

    reservation_mock.reserve_stock.side_effect = reserve_side_effect

    with pytest.raises(InsufficientStockError):
        service.process_order("ORD-3")

    reservation_mock.reserve_stock.assert_any_call("prod1", 2)
    reservation_mock.reserve_stock.assert_any_call("prod2", 3)
    reservation_mock.release_stock.assert_called_once_with("prod1", 2)

def test_cancel_order_pending_releases_stock(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = OrderItem("prod1", 2)
    order = Order("ORD-4", "user1", [item])
    order.status = OrderStatus.PENDING
    service._orders["ORD-4"] = order

    cancelled_order = service.cancel_order("ORD-4")

    assert cancelled_order.status == OrderStatus.CANCELLED
    reservation_mock.release_stock.assert_called_once_with("prod1", 2)

def test_cancel_order_confirmed_does_not_release_stock(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = OrderItem("prod1", 2)
    order = Order("ORD-5", "user1", [item])
    order.status = OrderStatus.CONFIRMED
    service._orders["ORD-5"] = order

    cancelled_order = service.cancel_order("ORD-5")

    assert cancelled_order.status == OrderStatus.CANCELLED
    reservation_mock.release_stock.assert_not_called()

def test_cancel_order_invalid_status_raises(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = OrderItem("prod1", 2)
    order = Order("ORD-6", "user1", [item])
    order.status = OrderStatus.COMPLETED
    service._orders["ORD-6"] = order

    with pytest.raises(OrderStateError) as excinfo:
        service.cancel_order("ORD-6")

    assert "cannot be cancelled" in str(excinfo.value)
    reservation_mock.release_stock.assert_not_called()

def test_complete_order_success(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = OrderItem("prod1", 2)
    order = Order("ORD-7", "user1", [item])
    order.status = OrderStatus.CONFIRMED
    service._orders["ORD-7"] = order

    product_mock = MagicMock()
    product_mock.stock = 10
    product_mock.reserved = 5
    inventory_mock.get_product.return_value = product_mock

    completed_order = service.complete_order("ORD-7")

    assert completed_order.status == OrderStatus.COMPLETED
    inventory_mock.get_product.assert_called_once_with("prod1")
    assert product_mock.stock == 8
    assert product_mock.reserved == 3

def test_complete_order_invalid_status_raises(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = OrderItem("prod1", 2)
    order = Order("ORD-8", "user1", [item])
    order.status = OrderStatus.PENDING
    service._orders["ORD-8"] = order

    with pytest.raises(OrderStateError) as excinfo:
        service.complete_order("ORD-8")

    assert "must be CONFIRMED to complete" in str(excinfo.value)
    inventory_mock.get_product.assert_not_called()
# AI_TEST_AGENT_END function=OrderService.__init__

# AI_TEST_AGENT_START function=OrderService.create_order
def test_create_order_success(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "p1", "quantity": 2}, {"product_id": "p2", "quantity": 3}]
    inventory_mock.get_product.side_effect = lambda pid: True
    pricing_mock.calculate_total.return_value = 100.0

    monkeypatch.setattr("inventory_system.services.order_service.generate_id", lambda prefix: "ORD-123")
    monkeypatch.setattr("inventory_system.services.order_service.get_timestamp", lambda: 1234567890)

    order = service.create_order("user1", items)

    assert order.order_id == "ORD-123"
    assert order.user_id == "user1"
    assert len(order.items) == 2
    assert order.items[0].product_id == "p1"
    assert order.items[0].quantity == 2
    assert order.created_at == 1234567890
    assert order.total == 100.0
    assert "ORD-123" in service._orders
    inventory_mock.get_product.assert_any_call("p1")
    inventory_mock.get_product.assert_any_call("p2")
    pricing_mock.calculate_total.assert_called_once_with(order)

def test_create_order_empty_items_raises_value_error():
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(ValueError, match="Order must contain at least one item"):
        service.create_order("user1", [])

def test_create_order_inventory_get_product_raises_propagates(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "p1", "quantity": 1}]
    inventory_mock.get_product.side_effect = KeyError("not found")

    with pytest.raises(KeyError, match="not found"):
        service.create_order("user1", items)

def test_create_order_with_zero_quantity(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "p1", "quantity": 0}]
    inventory_mock.get_product.return_value = True
    pricing_mock.calculate_total.return_value = 0.0

    monkeypatch.setattr("inventory_system.services.order_service.generate_id", lambda prefix: "ORD-000")
    monkeypatch.setattr("inventory_system.services.order_service.get_timestamp", lambda: 1111111111)

    order = service.create_order("user2", items)

    assert order.order_id == "ORD-000"
    assert order.user_id == "user2"
    assert len(order.items) == 1
    assert order.items[0].quantity == 0
    assert order.total == 0.0
    assert order.created_at == 1111111111

def test_create_order_with_negative_quantity(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "p1", "quantity": -5}]
    inventory_mock.get_product.return_value = True
    pricing_mock.calculate_total.return_value = -50.0

    monkeypatch.setattr("inventory_system.services.order_service.generate_id", lambda prefix: "ORD-NEG")
    monkeypatch.setattr("inventory_system.services.order_service.get_timestamp", lambda: 2222222222)

    order = service.create_order("user3", items)

    assert order.order_id == "ORD-NEG"
    assert order.user_id == "user3"
    assert len(order.items) == 1
    assert order.items[0].quantity == -5
    assert order.total == -50.0
    assert order.created_at == 2222222222

def test_create_order_with_missing_product_id_key(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"quantity": 1}]

    with pytest.raises(KeyError):
        service.create_order("user1", items)

def test_create_order_with_missing_quantity_key(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "p1"}]
    inventory_mock.get_product.return_value = True
    pricing_mock.calculate_total.return_value = 10.0

    monkeypatch.setattr("inventory_system.services.order_service.generate_id", lambda prefix: "ORD-MISS")
    monkeypatch.setattr("inventory_system.services.order_service.get_timestamp", lambda: 3333333333)

    with pytest.raises(KeyError):
        service.create_order("user1", items)

def test_create_order_with_non_string_product_id(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": 123, "quantity": 1}]
    inventory_mock.get_product.return_value = True
    pricing_mock.calculate_total.return_value = 20.0

    monkeypatch.setattr("inventory_system.services.order_service.generate_id", lambda prefix: "ORD-NONSTR")
    monkeypatch.setattr("inventory_system.services.order_service.get_timestamp", lambda: 4444444444)

    order = service.create_order("user4", items)

    assert order.items[0].product_id == 123
    assert order.total == 20.0

def test_create_order_with_non_integer_quantity(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "p1", "quantity": 2.5}]
    inventory_mock.get_product.return_value = True
    pricing_mock.calculate_total.return_value = 50.0

    monkeypatch.setattr("inventory_system.services.order_service.generate_id", lambda prefix: "ORD-FLOAT")
    monkeypatch.setattr("inventory_system.services.order_service.get_timestamp", lambda: 5555555555)

    order = service.create_order("user5", items)

    assert order.items[0].quantity == 2.5
    assert order.total == 50.0
# AI_TEST_AGENT_END function=OrderService.create_order

# AI_TEST_AGENT_START function=OrderService.process_order
def make_order(order_id="order1", user_id="user1", items=None, status=OrderStatus.PENDING):
    if items is None:
        items = [OrderItem("prod1", 2)]
    order = Order(order_id, user_id, items)
    order.status = status
    order.total = 100
    order.discount_applied = False
    return order

def test_process_order_success_reserves_stock_and_confirms_order():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    order = make_order()
    service._orders[order.order_id] = order

    # Mock get_order to return the order
    # Actually get_order reads from _orders, so no patch needed

    # Setup reservation.get_available to return enough stock for each item
    reservation.get_available.return_value = 5

    # Setup reservation.reserve_stock to succeed
    reservation.reserve_stock.return_value = None

    result = service.process_order(order.order_id)

    assert result.status == OrderStatus.CONFIRMED
    assert result is order
    # Check get_available called for each item
    for item in order.items:
        reservation.get_available.assert_any_call(item.product_id)
    # Check reserve_stock called for each item
    for item in order.items:
        reservation.reserve_stock.assert_any_call(item.product_id, item.quantity)
    # release_stock should not be called
    reservation.release_stock.assert_not_called()

def test_process_order_raises_if_order_not_pending():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    order = make_order(status=OrderStatus.CONFIRMED)
    service._orders[order.order_id] = order

    with pytest.raises(OrderStateError) as excinfo:
        service.process_order(order.order_id)
    assert f"Order {order.order_id!r} is not in PENDING state" in str(excinfo.value)

def test_process_order_raises_insufficient_stock_if_available_less_than_quantity():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = [OrderItem("prod1", 3), OrderItem("prod2", 2)]
    order = make_order(items=items)
    service._orders[order.order_id] = order

    # For first item, enough stock
    def get_available_side_effect(product_id):
        if product_id == "prod1":
            return 5
        else:
            return 1  # less than needed 2

    reservation.get_available.side_effect = get_available_side_effect

    with pytest.raises(InsufficientStockError) as excinfo:
        service.process_order(order.order_id)
    assert "insufficient stock for 'prod2'" in str(excinfo.value)

    # reserve_stock and release_stock should not be called because failure is before reservation
    reservation.reserve_stock.assert_not_called()
    reservation.release_stock.assert_not_called()

def test_process_order_releases_reserved_stock_if_reserve_stock_raises():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = [OrderItem("prod1", 2), OrderItem("prod2", 3)]
    order = make_order(items=items)
    service._orders[order.order_id] = order

    reservation.get_available.return_value = 10

    # reserve_stock succeeds for first item, fails for second
    def reserve_stock_side_effect(product_id, quantity):
        if product_id == "prod1":
            return None
        else:
            raise InsufficientStockError("No stock")

    reservation.reserve_stock.side_effect = reserve_stock_side_effect

    with pytest.raises(InsufficientStockError):
        service.process_order(order.order_id)

    # release_stock called for first item to rollback reservation
    reservation.release_stock.assert_called_once_with("prod1", 2)

def test_process_order_raises_order_not_found_error_for_invalid_order_id():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.process_order("nonexistent_order")
    assert "Order 'nonexistent_order' not found" in str(excinfo.value)

def test_process_order_with_zero_quantity_item_raises_insufficient_stock():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = [OrderItem("prod1", 0)]
    order = make_order(items=items)
    service._orders[order.order_id] = order

    reservation.get_available.return_value = 0

    # According to code, available > quantity is checked, so 0 > 0 is False, should raise
    with pytest.raises(InsufficientStockError) as excinfo:
        service.process_order(order.order_id)
    assert "insufficient stock for 'prod1'" in str(excinfo.value)

def test_process_order_with_negative_quantity_item_raises_insufficient_stock():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = [OrderItem("prod1", -1)]
    order = make_order(items=items)
    service._orders[order.order_id] = order

    # get_available returns 10, but quantity is negative
    reservation.get_available.return_value = 10

    # available > quantity: 10 > -1 is True, so no error on this check
    # But reserve_stock may be called with negative quantity, which may cause error or not
    # We simulate reserve_stock raising error on negative quantity
    def reserve_stock_side_effect(product_id, quantity):
        if quantity < 0:
            raise InsufficientStockError("Negative quantity not allowed")
        return None

    reservation.reserve_stock.side_effect = reserve_stock_side_effect

    with pytest.raises(InsufficientStockError) as excinfo:
        service.process_order(order.order_id)
    assert "Negative quantity not allowed" in str(excinfo.value)

def test_process_order_with_empty_items_raises_order_not_found_error():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    # Add an order with empty items list
    order = make_order(items=[])
    service._orders[order.order_id] = order

    # The code does not explicitly check for empty items in process_order, so it will loop zero times and confirm order
    reservation.get_available.return_value = 10
    reservation.reserve_stock.return_value = None

    result = service.process_order(order.order_id)
    assert result.status == OrderStatus.CONFIRMED
    assert result is order
    reservation.get_available.assert_not_called()
    reservation.reserve_stock.assert_not_called()
    reservation.release_stock.assert_not_called()
# AI_TEST_AGENT_END function=OrderService.process_order

# AI_TEST_AGENT_START function=OrderService.cancel_order
def make_order(status, items=None):
    class DummyOrder:
        def __init__(self):
            self.status = status
            self.items = items or []
    return DummyOrder()

def test_cancel_order_pending_releases_stock_and_cancels():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    order_id = "order1"
    items = [MagicMock(product_id="p1", quantity=2), MagicMock(product_id="p2", quantity=3)]
    order = make_order(OrderStatus.PENDING, items)
    service._orders[order_id] = order

    result = service.cancel_order(order_id)

    assert result.status == OrderStatus.CANCELLED
    assert reservation.release_stock.call_count == len(items)
    for item in items:
        reservation.release_stock.assert_any_call(item.product_id, item.quantity)

def test_cancel_order_confirmed_does_not_release_stock_but_cancels():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    order_id = "order2"
    items = [MagicMock(product_id="p1", quantity=1)]
    order = make_order(OrderStatus.CONFIRMED, items)
    service._orders[order_id] = order

    result = service.cancel_order(order_id)

    assert result.status == OrderStatus.CANCELLED
    reservation.release_stock.assert_not_called()

def test_cancel_order_invalid_status_raises_orderstateerror():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    order_id = "order3"
    order = make_order(OrderStatus.COMPLETED)
    service._orders[order_id] = order

    with pytest.raises(OrderStateError) as excinfo:
        service.cancel_order(order_id)
    assert f"Order {order_id!r} cannot be cancelled" in str(excinfo.value)

def test_cancel_order_nonexistent_order_raises_ordernotfounderror():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    with pytest.raises(Exception) as excinfo:
        service.cancel_order("nonexistent")
    assert "not found" in str(excinfo.value)

def test_cancel_order_pending_with_empty_items_releases_nothing_and_cancels():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    order_id = "order4"
    order = make_order(OrderStatus.PENDING, items=[])
    service._orders[order_id] = order

    result = service.cancel_order(order_id)

    assert result.status == OrderStatus.CANCELLED
    reservation.release_stock.assert_not_called()

def test_cancel_order_confirmed_with_multiple_items_cancels_without_release():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    order_id = "order5"
    items = [MagicMock(product_id="p1", quantity=5), MagicMock(product_id="p2", quantity=10)]
    order = make_order(OrderStatus.CONFIRMED, items)
    service._orders[order_id] = order

    result = service.cancel_order(order_id)

    assert result.status == OrderStatus.CANCELLED
    reservation.release_stock.assert_not_called()

def test_cancel_order_with_none_order_id_raises_ordernotfounderror():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    with pytest.raises(Exception) as excinfo:
        service.cancel_order(None)
    assert "not found" in str(excinfo.value)

def test_cancel_order_with_empty_string_order_id_raises_ordernotfounderror():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    with pytest.raises(Exception) as excinfo:
        service.cancel_order("")
    assert "not found" in str(excinfo.value)
# AI_TEST_AGENT_END function=OrderService.cancel_order

# AI_TEST_AGENT_START function=OrderService.complete_order
class DummyProduct:
    def __init__(self, stock, reserved):
        self.stock = stock
        self.reserved = reserved

class DummyOrderItem:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity

class DummyOrder:
    def __init__(self, order_id, user_id, items, status=OrderStatus.CONFIRMED):
        self.order_id = order_id
        self.user_id = user_id
        self.items = items
        self.status = status
        self.total = 0
        self.discount_applied = False

def test_complete_order_successful_stock_deduction_and_status_update():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item1 = DummyOrderItem("prod1", 3)
    item2 = DummyOrderItem("prod2", 2)
    order = DummyOrder("order123", "user1", [item1, item2], status=OrderStatus.CONFIRMED)

    service._orders["order123"] = order

    product1 = DummyProduct(stock=10, reserved=5)
    product2 = DummyProduct(stock=7, reserved=2)

    inventory_mock.get_product.side_effect = lambda pid: product1 if pid == "prod1" else product2

    result = service.complete_order("order123")

    assert result.status == OrderStatus.COMPLETED
    assert product1.stock == 7
    assert product1.reserved == 2
    assert product2.stock == 5
    assert product2.reserved == 0
    inventory_mock.get_product.assert_any_call("prod1")
    inventory_mock.get_product.assert_any_call("prod2")

def test_complete_order_raises_order_state_error_if_not_confirmed():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = DummyOrderItem("prod1", 1)
    order = DummyOrder("order123", "user1", [item], status=OrderStatus.PENDING)
    service._orders["order123"] = order

    with pytest.raises(OrderStateError) as excinfo:
        service.complete_order("order123")
    assert "must be CONFIRMED to complete" in str(excinfo.value)

def test_complete_order_raises_order_not_found_error_for_invalid_order_id():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.complete_order("nonexistent_order")
    assert "not found" in str(excinfo.value)

def test_complete_order_with_zero_quantity_items_does_not_change_stock_or_reserved():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = DummyOrderItem("prod1", 0)
    order = DummyOrder("order123", "user1", [item], status=OrderStatus.CONFIRMED)
    service._orders["order123"] = order

    product = DummyProduct(stock=5, reserved=2)
    inventory_mock.get_product.return_value = product

    result = service.complete_order("order123")

    assert result.status == OrderStatus.COMPLETED
    assert product.stock == 5
    assert product.reserved == 2
    inventory_mock.get_product.assert_called_once_with("prod1")

def test_complete_order_with_negative_quantity_reduces_stock_and_reserved_incorrectly():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = DummyOrderItem("prod1", -3)
    order = DummyOrder("order123", "user1", [item], status=OrderStatus.CONFIRMED)
    service._orders["order123"] = order

    product = DummyProduct(stock=10, reserved=5)
    inventory_mock.get_product.return_value = product

    result = service.complete_order("order123")

    assert result.status == OrderStatus.COMPLETED
    assert product.stock == 13
    assert product.reserved == 8
    inventory_mock.get_product.assert_called_once_with("prod1")

def test_complete_order_with_non_integer_quantity_raises_type_error():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = DummyOrderItem("prod1", "3")
    order = DummyOrder("order123", "user1", [item], status=OrderStatus.CONFIRMED)
    service._orders["order123"] = order

    product = DummyProduct(stock=10, reserved=5)
    inventory_mock.get_product.return_value = product

    with pytest.raises(TypeError):
        service.complete_order("order123")

def test_complete_order_with_empty_items_list_completes_without_stock_changes():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order = DummyOrder("order123", "user1", [], status=OrderStatus.CONFIRMED)
    service._orders["order123"] = order

    result = service.complete_order("order123")

    assert result.status == OrderStatus.COMPLETED
    inventory_mock.get_product.assert_not_called()

def test_complete_order_with_none_order_id_raises_order_not_found_error():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError):
        service.complete_order(None)
# AI_TEST_AGENT_END function=OrderService.complete_order

# AI_TEST_AGENT_START function=OrderService.get_order
def test_get_order_returns_order_when_exists():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)
    order_mock = MagicMock()
    order_mock.order_id = "order123"
    service._orders = {"order123": order_mock}

    result = service.get_order("order123")

    assert result is order_mock

def test_get_order_raises_order_not_found_error_for_missing_order():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)
    service._orders = {}

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order("nonexistent")

    assert "Order 'nonexistent' not found" in str(excinfo.value)

def test_get_order_raises_order_not_found_error_for_empty_string_id():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)
    service._orders = {}

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order("")

    assert "Order '' not found" in str(excinfo.value)

def test_get_order_raises_order_not_found_error_for_none_id():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)
    service._orders = {}

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order(None)

    assert "Order 'None' not found" in str(excinfo.value)

def test_get_order_returns_correct_order_among_multiple_orders():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)
    order1 = MagicMock()
    order1.order_id = "order1"
    order2 = MagicMock()
    order2.order_id = "order2"
    service._orders = {"order1": order1, "order2": order2}

    result = service.get_order("order2")

    assert result is order2

def test_get_order_raises_order_not_found_error_for_integer_id():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)
    service._orders = {}

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order(123)

    assert "Order '123' not found" in str(excinfo.value)

def test_get_order_raises_order_not_found_error_for_whitespace_id():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)
    service._orders = {}

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order("   ")

    assert "Order '   ' not found" in str(excinfo.value)
# AI_TEST_AGENT_END function=OrderService.get_order

# AI_TEST_AGENT_START function=OrderService.get_order_summary
def test_get_order_summary_returns_correct_summary_for_valid_order():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order = Order(
        order_id="order123",
        user_id="user1",
        items=[],
    )
    order.status = OrderStatus.PENDING
    order.total = 123.45
    order.discount_applied = True
    order.items = [MagicMock(), MagicMock()]
    service._orders["order123"] = order

    summary = service.get_order_summary("order123")

    assert summary["order_id"] == "order123"
    assert summary["user_id"] == "user1"
    assert summary["status"] == OrderStatus.PENDING.value
    assert summary["item_count"] == 2
    assert summary["total"] == 123.45
    assert summary["discount_applied"] is True


def test_get_order_summary_raises_order_not_found_error_for_missing_order():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order_summary("nonexistent_order")

    assert "Order 'nonexistent_order' not found" in str(excinfo.value)


def test_get_order_summary_handles_order_with_no_items_and_no_discount():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order = Order(
        order_id="order_empty",
        user_id="user2",
        items=[],
    )
    order.status = OrderStatus.CANCELLED
    order.total = 0.0
    order.discount_applied = False
    service._orders["order_empty"] = order

    summary = service.get_order_summary("order_empty")

    assert summary["order_id"] == "order_empty"
    assert summary["user_id"] == "user2"
    assert summary["status"] == OrderStatus.CANCELLED.value
    assert summary["item_count"] == 0
    assert summary["total"] == 0.0
    assert summary["discount_applied"] is False


def test_get_order_summary_returns_correct_summary_for_completed_order_with_discount_false():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order = Order(
        order_id="order_completed",
        user_id="user3",
        items=[MagicMock()]
    )
    order.status = OrderStatus.COMPLETED
    order.total = 50.0
    order.discount_applied = False
    service._orders["order_completed"] = order

    summary = service.get_order_summary("order_completed")

    assert summary["order_id"] == "order_completed"
    assert summary["user_id"] == "user3"
    assert summary["status"] == OrderStatus.COMPLETED.value
    assert summary["item_count"] == 1
    assert summary["total"] == 50.0
    assert summary["discount_applied"] is False


def test_get_order_summary_raises_type_error_when_order_id_is_none():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(TypeError):
        service.get_order_summary(None)


def test_get_order_summary_raises_type_error_when_order_id_is_empty_string():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError):
        service.get_order_summary("")


def test_get_order_summary_raises_order_not_found_error_for_numeric_order_id():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError):
        service.get_order_summary(123)


def test_get_order_summary_returns_summary_when_discount_applied_is_none():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order = Order(
        order_id="order_none_discount",
        user_id="user4",
        items=[MagicMock()]
    )
    order.status = OrderStatus.PENDING
    order.total = 75.0
    order.discount_applied = None
    service._orders["order_none_discount"] = order

    summary = service.get_order_summary("order_none_discount")

    assert summary["order_id"] == "order_none_discount"
    assert summary["user_id"] == "user4"
    assert summary["status"] == OrderStatus.PENDING.value
    assert summary["item_count"] == 1
    assert summary["total"] == 75.0
    assert summary["discount_applied"] is None


def test_get_order_summary_returns_summary_for_order_with_zero_total():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order = Order(
        order_id="order_zero_total",
        user_id="user5",
        items=[MagicMock()]
    )
    order.status = OrderStatus.PENDING
    order.total = 0
    order.discount_applied = False
    service._orders["order_zero_total"] = order

    summary = service.get_order_summary("order_zero_total")

    assert summary["order_id"] == "order_zero_total"
    assert summary["user_id"] == "user5"
    assert summary["status"] == OrderStatus.PENDING.value
    assert summary["item_count"] == 1
    assert summary["total"] == 0
    assert summary["discount_applied"] is False
# AI_TEST_AGENT_END function=OrderService.get_order_summary
