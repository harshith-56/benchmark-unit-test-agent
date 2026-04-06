from inventory_system.services.order_service import InsufficientStockError
from inventory_system.services.order_service import Order, OrderItem
from inventory_system.services.order_service import OrderItem, Order
from inventory_system.services.order_service import OrderService
from inventory_system.services.order_service import OrderService, OrderNotFoundError, OrderStatus, Order, OrderItem
from inventory_system.services.order_service import OrderService, OrderStatus, OrderNotFoundError
from inventory_system.services.order_service import OrderService, OrderStatus, OrderNotFoundError, OrderStateError
from inventory_system.services.order_service import OrderService, OrderStatus, OrderNotFoundError, OrderStateError, InsufficientStockError
from inventory_system.services.order_service import OrderStateError, InsufficientStockError
from inventory_system.services.order_service import OrderStatus, OrderNotFoundError, OrderStateError
from inventory_system.services.order_service import OrderStatus, OrderStateError, InsufficientStockError, OrderNotFoundError
from inventory_system.utils.helpers import generate_id, get_timestamp
from unittest.mock import MagicMock
from unittest.mock import MagicMock, call
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

    monkeypatch.setattr("inventory_system.services.order_service.generate_id", lambda prefix="": "ORD-12345678")
    monkeypatch.setattr("inventory_system.services.order_service.get_timestamp", lambda: 1234567890.0)

    items = [{"product_id": "prod1", "quantity": 2}]
    order = service.create_order("user1", items)

    assert order.order_id == "ORD-12345678"
    assert order.user_id == "user1"
    assert len(order.items) == 1
    assert order.items[0].product_id == "prod1"
    assert order.items[0].quantity == 2
    assert order.created_at == 1234567890.0
    assert order.total == 100.0
    assert service._orders["ORD-12345678"] == order
    inventory_mock.get_product.assert_called_once_with("prod1")
    pricing_mock.calculate_total.assert_called_once_with(order)

def test_create_order_empty_items_raises_value_error():
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(ValueError) as excinfo:
        service.create_order("user1", [])
    assert str(excinfo.value) == "Order must contain at least one item"

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

    result = service.process_order("ORD-1")

    assert result.status == OrderStatus.CONFIRMED
    reservation_mock.get_available.assert_called_once_with("prod1")
    reservation_mock.reserve_stock.assert_called_once_with("prod1", 2)

def test_process_order_insufficient_stock_raises(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_item = OrderItem("prod1", 5)
    order = Order("ORD-1", "user1", [order_item])
    order.status = OrderStatus.PENDING
    service._orders["ORD-1"] = order

    reservation_mock.get_available.return_value = 3

    with pytest.raises(InsufficientStockError) as excinfo:
        service.process_order("ORD-1")
    assert "insufficient stock for 'prod1'" in str(excinfo.value)
    reservation_mock.get_available.assert_called_once_with("prod1")
    reservation_mock.reserve_stock.assert_not_called()

def test_process_order_reserve_stock_partial_failure_releases(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item1 = OrderItem("prod1", 2)
    item2 = OrderItem("prod2", 1)
    order = Order("ORD-1", "user1", [item1, item2])
    order.status = OrderStatus.PENDING
    service._orders["ORD-1"] = order

    reservation_mock.get_available.side_effect = [3, 3]

    def reserve_side_effect(product_id, quantity):
        if product_id == "prod2":
            raise InsufficientStockError("No stock")
    reservation_mock.reserve_stock.side_effect = reserve_side_effect

    with pytest.raises(InsufficientStockError):
        service.process_order("ORD-1")

    reservation_mock.reserve_stock.assert_any_call("prod1", 2)
    reservation_mock.reserve_stock.assert_any_call("prod2", 1)
    reservation_mock.release_stock.assert_called_once_with("prod1", 2)

def test_cancel_order_pending_releases_stock(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = OrderItem("prod1", 2)
    order = Order("ORD-1", "user1", [item])
    order.status = OrderStatus.PENDING
    service._orders["ORD-1"] = order

    result = service.cancel_order("ORD-1")

    reservation_mock.release_stock.assert_called_once_with("prod1", 2)
    assert result.status == OrderStatus.CANCELLED

def test_cancel_order_confirmed_does_not_release_stock(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = OrderItem("prod1", 2)
    order = Order("ORD-1", "user1", [item])
    order.status = OrderStatus.CONFIRMED
    service._orders["ORD-1"] = order

    result = service.cancel_order("ORD-1")

    reservation_mock.release_stock.assert_not_called()
    assert result.status == OrderStatus.CANCELLED

def test_cancel_order_invalid_status_raises(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = OrderItem("prod1", 2)
    order = Order("ORD-1", "user1", [item])
    order.status = OrderStatus.COMPLETED
    service._orders["ORD-1"] = order

    with pytest.raises(OrderStateError) as excinfo:
        service.cancel_order("ORD-1")
    assert "cannot be cancelled" in str(excinfo.value)

def test_complete_order_success(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    class DummyProduct:
        def __init__(self):
            self.stock = 10
            self.reserved = 5

    item = OrderItem("prod1", 3)
    order = Order("ORD-1", "user1", [item])
    order.status = OrderStatus.CONFIRMED
    service._orders["ORD-1"] = order

    dummy_product = DummyProduct()
    inventory_mock.get_product.return_value = dummy_product

    result = service.complete_order("ORD-1")

    inventory_mock.get_product.assert_called_once_with("prod1")
    assert dummy_product.stock == 7
    assert dummy_product.reserved == 2
    assert result.status == OrderStatus.COMPLETED

def test_complete_order_invalid_status_raises(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    item = OrderItem("prod1", 3)
    order = Order("ORD-1", "user1", [item])
    order.status = OrderStatus.PENDING
    service._orders["ORD-1"] = order

    with pytest.raises(OrderStateError) as excinfo:
        service.complete_order("ORD-1")
    assert "must be CONFIRMED to complete" in str(excinfo.value)
# AI_TEST_AGENT_END function=OrderService.__init__

# AI_TEST_AGENT_START function=OrderService.create_order
def test_create_order_success(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "prod1", "quantity": 2}, {"product_id": "prod2", "quantity": 3}]
    inventory_mock.get_product.side_effect = lambda pid: True
    pricing_mock.calculate_total.return_value = 100.0

    with patch("inventory_system.services.order_service.generate_id", return_value="ORD-1234"):
        with patch("inventory_system.services.order_service.get_timestamp", return_value=1234567890):
            order = service.create_order("user1", items)

    assert order.order_id == "ORD-1234"
    assert order.user_id == "user1"
    assert len(order.items) == 2
    assert order.items[0].product_id == "prod1"
    assert order.items[0].quantity == 2
    assert order.total == 100.0
    assert order.created_at == 1234567890
    assert "ORD-1234" in service._orders
    inventory_mock.get_product.assert_any_call("prod1")
    inventory_mock.get_product.assert_any_call("prod2")
    pricing_mock.calculate_total.assert_called_once_with(order)

def test_create_order_empty_items_raises_value_error():
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(ValueError) as excinfo:
        service.create_order("user1", [])
    assert str(excinfo.value) == "Order must contain at least one item"

def test_create_order_inventory_get_product_called_for_each_item(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "p1", "quantity": 1}, {"product_id": "p2", "quantity": 1}]
    inventory_mock.get_product.side_effect = lambda pid: True
    pricing_mock.calculate_total.return_value = 50.0

    with patch("inventory_system.services.order_service.generate_id", return_value="ORD-5678"):
        with patch("inventory_system.services.order_service.get_timestamp", return_value=1111111111):
            order = service.create_order("user2", items)

    assert len(order.items) == 2
    inventory_mock.get_product.assert_any_call("p1")
    inventory_mock.get_product.assert_any_call("p2")
    assert pricing_mock.calculate_total.call_count == 1

def test_create_order_inventory_get_product_raises_propagates(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "bad_prod", "quantity": 1}]
    inventory_mock.get_product.side_effect = KeyError("Product not found")

    with pytest.raises(KeyError) as excinfo:
        service.create_order("user3", items)
    assert "Product not found" in str(excinfo.value)
    inventory_mock.get_product.assert_called_once_with("bad_prod")
    pricing_mock.calculate_total.assert_not_called()

def test_create_order_with_zero_quantity(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "prod_zero", "quantity": 0}]
    inventory_mock.get_product.return_value = True
    pricing_mock.calculate_total.return_value = 0.0

    with patch("inventory_system.services.order_service.generate_id", return_value="ORD-0000"):
        with patch("inventory_system.services.order_service.get_timestamp", return_value=2222222222):
            order = service.create_order("user_zero", items)

    assert order.items[0].quantity == 0
    assert order.total == 0.0
    inventory_mock.get_product.assert_called_once_with("prod_zero")
    pricing_mock.calculate_total.assert_called_once_with(order)

def test_create_order_with_negative_quantity(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "prod_neg", "quantity": -5}]
    inventory_mock.get_product.return_value = True
    pricing_mock.calculate_total.return_value = -50.0

    with patch("inventory_system.services.order_service.generate_id", return_value="ORD-NEG1"):
        with patch("inventory_system.services.order_service.get_timestamp", return_value=3333333333):
            order = service.create_order("user_neg", items)

    assert order.items[0].quantity == -5
    assert order.total == -50.0
    inventory_mock.get_product.assert_called_once_with("prod_neg")
    pricing_mock.calculate_total.assert_called_once_with(order)

def test_create_order_with_missing_product_id_key(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"quantity": 1}]

    with pytest.raises(KeyError) as excinfo:
        service.create_order("user_missing", items)
    assert "'product_id'" in str(excinfo.value)
    inventory_mock.get_product.assert_not_called()
    pricing_mock.calculate_total.assert_not_called()

def test_create_order_with_missing_quantity_key(monkeypatch):
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    reservation_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    items = [{"product_id": "prod_missing"}]
    inventory_mock.get_product.return_value = True

    with pytest.raises(KeyError) as excinfo:
        service.create_order("user_missing_qty", items)
    assert "'quantity'" in str(excinfo.value)
    inventory_mock.get_product.assert_called_once_with("prod_missing")
    pricing_mock.calculate_total.assert_not_called()
# AI_TEST_AGENT_END function=OrderService.create_order

# AI_TEST_AGENT_START function=OrderService.process_order
def test_process_order_successful_reservation(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order123"
    user_id = "user1"
    items = [OrderItem("prod1", 2), OrderItem("prod2", 3)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.PENDING
    service._orders[order_id] = order

    reservation_mock.get_available.side_effect = [5, 4]
    reservation_mock.reserve_stock.return_value = None

    result = service.process_order(order_id)

    assert result.status == OrderStatus.CONFIRMED
    reservation_mock.get_available.assert_has_calls([call("prod1"), call("prod2")])
    reservation_mock.reserve_stock.assert_has_calls([call("prod1", 2), call("prod2", 3)])

def test_process_order_order_not_pending_raises_orderstateerror(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order456"
    user_id = "user2"
    items = [OrderItem("prod1", 1)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.CONFIRMED
    service._orders[order_id] = order

    with pytest.raises(OrderStateError) as excinfo:
        service.process_order(order_id)
    assert f"Order {order_id!r} is not in PENDING state" in str(excinfo.value)

def test_process_order_insufficient_stock_raises_insufficientstockerror(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order789"
    user_id = "user3"
    items = [OrderItem("prod1", 5)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.PENDING
    service._orders[order_id] = order

    reservation_mock.get_available.return_value = 3

    with pytest.raises(InsufficientStockError) as excinfo:
        service.process_order(order_id)
    assert f"insufficient stock for 'prod1'" in str(excinfo.value)
    reservation_mock.get_available.assert_called_once_with("prod1")
    reservation_mock.reserve_stock.assert_not_called()

def test_process_order_reservation_partial_failure_releases_reserved_stock(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order101"
    user_id = "user4"
    items = [OrderItem("prod1", 2), OrderItem("prod2", 3)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.PENDING
    service._orders[order_id] = order

    reservation_mock.get_available.side_effect = [5, 5]

    def reserve_side_effect(product_id, quantity):
        if product_id == "prod2":
            raise InsufficientStockError("Insufficient stock for prod2")
        return None

    reservation_mock.reserve_stock.side_effect = reserve_side_effect
    reservation_mock.release_stock.return_value = None

    with pytest.raises(InsufficientStockError):
        service.process_order(order_id)

    reservation_mock.reserve_stock.assert_has_calls([call("prod1", 2), call("prod2", 3)])
    reservation_mock.release_stock.assert_called_once_with("prod1", 2)

def test_process_order_available_equal_quantity_raises_insufficientstockerror(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order202"
    user_id = "user5"
    items = [OrderItem("prod1", 3)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.PENDING
    service._orders[order_id] = order

    reservation_mock.get_available.return_value = 3

    with pytest.raises(InsufficientStockError) as excinfo:
        service.process_order(order_id)
    assert f"insufficient stock for 'prod1'" in str(excinfo.value)
    reservation_mock.reserve_stock.assert_not_called()

def test_process_order_order_not_found_raises_ordernotfounderror():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.process_order("nonexistent_order")
    assert "Order 'nonexistent_order' not found" in str(excinfo.value)

def test_process_order_empty_items_order(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order303"
    user_id = "user6"
    order = Order(order_id, user_id, [])
    order.status = OrderStatus.PENDING
    service._orders[order_id] = order

    # process_order should not raise but will not reserve anything
    with pytest.raises(InsufficientStockError):
        service.process_order(order_id)
    reservation_mock.get_available.assert_not_called()
    reservation_mock.reserve_stock.assert_not_called()

def test_process_order_multiple_items_first_insufficient_stock(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order404"
    user_id = "user7"
    items = [OrderItem("prod1", 5), OrderItem("prod2", 2)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.PENDING
    service._orders[order_id] = order

    reservation_mock.get_available.side_effect = [3, 10]

    with pytest.raises(InsufficientStockError) as excinfo:
        service.process_order(order_id)
    assert "insufficient stock for 'prod1'" in str(excinfo.value)
    reservation_mock.reserve_stock.assert_not_called()

def test_process_order_multiple_items_second_insufficient_stock(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order505"
    user_id = "user8"
    items = [OrderItem("prod1", 2), OrderItem("prod2", 5)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.PENDING
    service._orders[order_id] = order

    reservation_mock.get_available.side_effect = [10, 3]

    with pytest.raises(InsufficientStockError) as excinfo:
        service.process_order(order_id)
    assert "insufficient stock for 'prod2'" in str(excinfo.value)
    reservation_mock.reserve_stock.assert_not_called()
# AI_TEST_AGENT_END function=OrderService.process_order

# AI_TEST_AGENT_START function=OrderService.cancel_order
class DummyProduct:
    def __init__(self, stock=0, reserved=0):
        self.stock = stock
        self.reserved = reserved

class DummyOrderItem:
    def __init__(self, product_id, quantity):
        self.product_id = product_id
        self.quantity = quantity

class DummyOrder:
    def __init__(self, order_id, user_id, items, status=OrderStatus.PENDING):
        self.order_id = order_id
        self.user_id = user_id
        self.items = items
        self.status = status
        self.total = 0
        self.discount_applied = False
        self.created_at = None

def test_cancel_order_pending_releases_stock_and_cancels():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    item1 = DummyOrderItem("prod1", 3)
    item2 = DummyOrderItem("prod2", 5)
    order = DummyOrder("order123", "user1", [item1, item2], status=OrderStatus.PENDING)
    service._orders["order123"] = order

    result = service.cancel_order("order123")

    reservation.release_stock.assert_any_call("prod1", 3)
    reservation.release_stock.assert_any_call("prod2", 5)
    assert reservation.release_stock.call_count == 2
    assert result.status == OrderStatus.CANCELLED
    assert result is order

def test_cancel_order_confirmed_does_not_release_stock_but_cancels():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    item1 = DummyOrderItem("prod1", 2)
    order = DummyOrder("order456", "user2", [item1], status=OrderStatus.CONFIRMED)
    service._orders["order456"] = order

    result = service.cancel_order("order456")

    reservation.release_stock.assert_not_called()
    assert result.status == OrderStatus.CANCELLED
    assert result is order

def test_cancel_order_invalid_status_raises_orderstateerror():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    item1 = DummyOrderItem("prod1", 1)
    order = DummyOrder("order789", "user3", [item1], status=OrderStatus.COMPLETED)
    service._orders["order789"] = order

    with pytest.raises(OrderStateError) as excinfo:
        service.cancel_order("order789")
    assert "cannot be cancelled" in str(excinfo.value)
    assert order.status == OrderStatus.COMPLETED

def test_cancel_order_nonexistent_order_raises_ordernotfounderror():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.cancel_order("nonexistent")
    assert "not found" in str(excinfo.value)

def test_cancel_order_pending_with_empty_items_releases_nothing_and_cancels():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    order = DummyOrder("order_empty", "user4", [], status=OrderStatus.PENDING)
    service._orders["order_empty"] = order

    result = service.cancel_order("order_empty")

    reservation.release_stock.assert_not_called()
    assert result.status == OrderStatus.CANCELLED

def test_cancel_order_confirmed_with_multiple_items_cancels_without_releasing():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = [DummyOrderItem("prodA", 1), DummyOrderItem("prodB", 2)]
    order = DummyOrder("order_multi", "user5", items, status=OrderStatus.CONFIRMED)
    service._orders["order_multi"] = order

    result = service.cancel_order("order_multi")

    reservation.release_stock.assert_not_called()
    assert result.status == OrderStatus.CANCELLED

def test_cancel_order_pending_calls_release_stock_for_each_item():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = [DummyOrderItem("prodX", 4), DummyOrderItem("prodY", 7)]
    order = DummyOrder("order_pending", "user6", items, status=OrderStatus.PENDING)
    service._orders["order_pending"] = order

    result = service.cancel_order("order_pending")

    calls = [((item.product_id, item.quantity),) for item in items]
    reservation.release_stock.assert_has_calls(calls, any_order=True)
    assert reservation.release_stock.call_count == len(items)
    assert result.status == OrderStatus.CANCELLED

def test_cancel_order_with_none_order_id_raises_ordernotfounderror():
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    with pytest.raises(OrderNotFoundError):
        service.cancel_order(None)
# AI_TEST_AGENT_END function=OrderService.cancel_order

# AI_TEST_AGENT_START function=OrderService.complete_order
def make_order(order_id, user_id, items, status, total=0, discount_applied=False):
    order = Order(order_id, user_id, items)
    order.status = status
    order.total = total
    order.discount_applied = discount_applied
    return order

def make_product(stock, reserved):
    product = MagicMock()
    product.stock = stock
    product.reserved = reserved
    return product

def test_complete_order_successful_reduces_stock_and_reserved_and_sets_completed(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = [OrderItem("prod1", 3), OrderItem("prod2", 2)]
    order = make_order("order1", "user1", items, OrderStatus.CONFIRMED, total=100)
    service._orders["order1"] = order

    product1 = make_product(stock=10, reserved=5)
    product2 = make_product(stock=7, reserved=2)
    inventory.get_product.side_effect = [product1, product2]

    result = service.complete_order("order1")

    assert result.status == OrderStatus.COMPLETED
    assert product1.stock == 7  # 10 - 3
    assert product1.reserved == 2  # 5 - 3
    assert product2.stock == 5  # 7 - 2
    assert product2.reserved == 0  # 2 - 2
    assert result is order
    assert inventory.get_product.call_count == 2
    inventory.get_product.assert_any_call("prod1")
    inventory.get_product.assert_any_call("prod2")

def test_complete_order_raises_order_not_found(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.complete_order("missing_order")
    assert "Order 'missing_order' not found" in str(excinfo.value)

def test_complete_order_raises_order_state_error_if_not_confirmed(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = [OrderItem("prod1", 1)]
    order = make_order("order2", "user2", items, OrderStatus.PENDING)
    service._orders["order2"] = order

    with pytest.raises(OrderStateError) as excinfo:
        service.complete_order("order2")
    assert "Order 'order2' must be CONFIRMED to complete" in str(excinfo.value)

def test_complete_order_with_zero_quantity_items(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = [OrderItem("prod1", 0)]
    order = make_order("order3", "user3", items, OrderStatus.CONFIRMED, total=0)
    service._orders["order3"] = order

    product = make_product(stock=5, reserved=1)
    inventory.get_product.return_value = product

    result = service.complete_order("order3")

    assert result.status == OrderStatus.COMPLETED
    assert product.stock == 5  # unchanged because quantity is zero
    assert product.reserved == 1  # unchanged because quantity is zero

def test_complete_order_with_negative_quantity_items(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = [OrderItem("prod1", -1)]
    order = make_order("order4", "user4", items, OrderStatus.CONFIRMED, total=0)
    service._orders["order4"] = order

    product = make_product(stock=5, reserved=1)
    inventory.get_product.return_value = product

    result = service.complete_order("order4")

    # Negative quantity reduces stock and reserved by negative number (i.e. increases)
    assert result.status == OrderStatus.COMPLETED
    assert product.stock == 6  # 5 - (-1) = 6
    assert product.reserved == 2  # 1 - (-1) = 2

def test_complete_order_with_non_integer_quantity(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = [OrderItem("prod1", 2.5)]
    order = make_order("order5", "user5", items, OrderStatus.CONFIRMED, total=0)
    service._orders["order5"] = order

    product = make_product(stock=10, reserved=5)
    inventory.get_product.return_value = product

    result = service.complete_order("order5")

    assert result.status == OrderStatus.COMPLETED
    assert product.stock == 7.5  # 10 - 2.5
    assert product.reserved == 2.5  # 5 - 2.5

def test_complete_order_with_empty_items_list(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    items = []
    order = make_order("order6", "user6", items, OrderStatus.CONFIRMED, total=0)
    service._orders["order6"] = order

    result = service.complete_order("order6")

    assert result.status == OrderStatus.COMPLETED
    # No calls to get_product because no items
    inventory.get_product.assert_not_called()

def test_complete_order_with_none_order_id_raises(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    service = OrderService(inventory, reservation, pricing)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.complete_order(None)
    assert "Order None not found" in str(excinfo.value)
# AI_TEST_AGENT_END function=OrderService.complete_order

# AI_TEST_AGENT_START function=OrderService.get_order
def test_get_order_returns_order_when_exists():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order = Order("order123", "user1", [])
    service._orders["order123"] = order

    result = service.get_order("order123")

    assert result is order

def test_get_order_raises_order_not_found_error_for_missing_order():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order("missing_order")

    assert str(excinfo.value) == "Order 'missing_order' not found"

def test_get_order_raises_order_not_found_error_for_empty_string_id():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order("")

    assert str(excinfo.value) == "Order '' not found"

def test_get_order_raises_order_not_found_error_for_none_id():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order(None)

    assert str(excinfo.value) == "Order None not found"

def test_get_order_raises_order_not_found_error_for_numeric_id():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order(123)

    assert str(excinfo.value) == "Order 123 not found"

def test_get_order_returns_correct_order_among_multiple_orders():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order1 = Order("order1", "user1", [])
    order2 = Order("order2", "user2", [])
    service._orders["order1"] = order1
    service._orders["order2"] = order2

    result = service.get_order("order2")

    assert result is order2

def test_get_order_raises_order_not_found_error_for_whitespace_id():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order("   ")

    assert str(excinfo.value) == "Order '   ' not found"
# AI_TEST_AGENT_END function=OrderService.get_order

# AI_TEST_AGENT_START function=OrderService.get_order_summary
def test_get_order_summary_valid_order(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order123"
    user_id = "user1"
    items = [OrderItem("prod1", 2), OrderItem("prod2", 3)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.CONFIRMED
    order.total = 100.0
    order.discount_applied = True

    service._orders[order_id] = order

    summary = service.get_order_summary(order_id)

    assert summary["order_id"] == order_id
    assert summary["user_id"] == user_id
    assert summary["status"] == OrderStatus.CONFIRMED.value
    assert summary["item_count"] == 2
    assert summary["total"] == 100.0
    assert summary["discount_applied"] is True


def test_get_order_summary_order_not_found():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    with pytest.raises(OrderNotFoundError) as excinfo:
        service.get_order_summary("nonexistent_order")

    assert "Order 'nonexistent_order' not found" in str(excinfo.value)


def test_get_order_summary_empty_items_list(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order_empty"
    user_id = "user2"
    items = []
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.PENDING
    order.total = 0.0
    order.discount_applied = False

    service._orders[order_id] = order

    summary = service.get_order_summary(order_id)

    assert summary["order_id"] == order_id
    assert summary["user_id"] == user_id
    assert summary["status"] == OrderStatus.PENDING.value
    assert summary["item_count"] == 0
    assert summary["total"] == 0.0
    assert summary["discount_applied"] is False


def test_get_order_summary_discount_none(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order_no_discount"
    user_id = "user3"
    items = [OrderItem("prod3", 1)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.COMPLETED
    order.total = 50.0
    order.discount_applied = None

    service._orders[order_id] = order

    summary = service.get_order_summary(order_id)

    assert summary["order_id"] == order_id
    assert summary["user_id"] == user_id
    assert summary["status"] == OrderStatus.COMPLETED.value
    assert summary["item_count"] == 1
    assert summary["total"] == 50.0
    assert summary["discount_applied"] is None


def test_get_order_summary_status_pending(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order_pending"
    user_id = "user4"
    items = [OrderItem("prod4", 5)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.PENDING
    order.total = 200.0
    order.discount_applied = False

    service._orders[order_id] = order

    summary = service.get_order_summary(order_id)

    assert summary["order_id"] == order_id
    assert summary["user_id"] == user_id
    assert summary["status"] == OrderStatus.PENDING.value
    assert summary["item_count"] == 1
    assert summary["total"] == 200.0
    assert summary["discount_applied"] is False


def test_get_order_summary_status_cancelled(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order_cancelled"
    user_id = "user5"
    items = [OrderItem("prod5", 10)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.CANCELLED
    order.total = 0.0
    order.discount_applied = False

    service._orders[order_id] = order

    summary = service.get_order_summary(order_id)

    assert summary["order_id"] == order_id
    assert summary["user_id"] == user_id
    assert summary["status"] == OrderStatus.CANCELLED.value
    assert summary["item_count"] == 1
    assert summary["total"] == 0.0
    assert summary["discount_applied"] is False


def test_get_order_summary_status_completed(monkeypatch):
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)

    order_id = "order_completed"
    user_id = "user6"
    items = [OrderItem("prod6", 7)]
    order = Order(order_id, user_id, items)
    order.status = OrderStatus.COMPLETED
    order.total = 350.0
    order.discount_applied = True

    service._orders[order_id] = order

    summary = service.get_order_summary(order_id)

    assert summary["order_id"] == order_id
    assert summary["user_id"] == user_id
    assert summary["status"] == OrderStatus.COMPLETED.value
    assert summary["item_count"] == 1
    assert summary["total"] == 350.0
    assert summary["discount_applied"] is True
# AI_TEST_AGENT_END function=OrderService.get_order_summary
