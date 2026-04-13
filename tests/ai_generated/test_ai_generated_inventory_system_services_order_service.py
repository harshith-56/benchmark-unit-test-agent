from inventory_system.services.order_service import Order
from inventory_system.services.order_service import OrderNotFoundError
from inventory_system.services.order_service import OrderService
from inventory_system.services.order_service import OrderService, OrderItem, Order
from inventory_system.services.order_service import OrderService, OrderNotFoundError
from inventory_system.services.order_service import OrderStatus, OrderStateError
from inventory_system.services.order_service import OrderStatus, OrderStateError, InsufficientStockError
from unittest.mock import MagicMock
from unittest.mock import MagicMock, patch
from unittest.mock import patch, MagicMock
import pytest

# AI_TEST_AGENT_START function=OrderService.__init__
def test_init_with_valid_services():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    service = OrderService(inventory_mock, reservation_mock, pricing_mock)
    assert service._inventory is inventory_mock
    assert service._reservation is reservation_mock
    assert service._pricing is pricing_mock
    assert isinstance(service._orders, dict)
    assert service._orders == {}

def test_init_with_none_inventory_service():
    reservation_mock = MagicMock()
    pricing_mock = MagicMock()
    with pytest.raises(AttributeError):
        OrderService(None, reservation_mock, pricing_mock)

def test_init_with_none_reservation_manager():
    inventory_mock = MagicMock()
    pricing_mock = MagicMock()
    with pytest.raises(AttributeError):
        OrderService(inventory_mock, None, pricing_mock)

def test_init_with_none_pricing_service():
    inventory_mock = MagicMock()
    reservation_mock = MagicMock()
    with pytest.raises(AttributeError):
        OrderService(inventory_mock, reservation_mock, None)

def test_init_with_all_none_services():
    with pytest.raises(AttributeError):
        OrderService(None, None, None)

def test_init_with_non_mocked_objects():
    class DummyInventory:
        pass
    class DummyReservation:
        pass
    class DummyPricing:
        pass
    inventory = DummyInventory()
    reservation = DummyReservation()
    pricing = DummyPricing()
    service = OrderService(inventory, reservation, pricing)
    assert service._inventory is inventory
    assert service._reservation is reservation
    assert service._pricing is pricing
    assert service._orders == {}

def test_init_with_empty_string_services():
    with pytest.raises(AttributeError):
        OrderService("", "", "")

def test_init_with_integer_services():
    with pytest.raises(AttributeError):
        OrderService(1, 2, 3)
# AI_TEST_AGENT_END function=OrderService.__init__

# AI_TEST_AGENT_START function=OrderService.create_order
def test_create_order_raises_value_error_on_empty_items():
    service = OrderService()
    with pytest.raises(ValueError, match="Order must contain at least one item"):
        service.create_order("user1", [])

def test_create_order_calls_get_product_for_each_item_and_returns_order():
    service = OrderService()
    service._inventory = MagicMock()
    service._pricing = MagicMock()
    service._orders = {}

    items = [{"product_id": "p1", "quantity": 2}, {"product_id": "p2", "quantity": 3}]

    service._inventory.get_product.side_effect = [None, None]
    service._pricing.calculate_total.return_value = 100
    with patch("inventory_system.services.order_service.generate_id", return_value="ORD-123"):
        with patch("inventory_system.services.order_service.get_timestamp", return_value=1234567890):
            order = service.create_order("user1", items)

    assert order.order_id == "ORD-123"
    assert order.user_id == "user1"
    assert len(order.items) == 2
    assert order.items[0].product_id == "p1"
    assert order.items[0].quantity == 2
    assert order.items[1].product_id == "p2"
    assert order.items[1].quantity == 3
    assert order.created_at == 1234567890
    assert order.total == 100
    assert service._orders["ORD-123"] == order
    assert service._inventory.get_product.call_count == 2
    service._inventory.get_product.assert_any_call("p1")
    service._inventory.get_product.assert_any_call("p2")
    service._pricing.calculate_total.assert_called_once_with(order)

def test_create_order_raises_key_error_if_product_id_missing():
    service = OrderService()
    service._inventory = MagicMock()
    service._pricing = MagicMock()
    service._orders = {}

    items = [{"quantity": 2}]

    with pytest.raises(KeyError):
        service.create_order("user1", items)

def test_create_order_raises_key_error_if_quantity_missing():
    service = OrderService()
    service._inventory = MagicMock()
    service._pricing = MagicMock()
    service._orders = {}

    items = [{"product_id": "p1"}]

    with pytest.raises(KeyError):
        service.create_order("user1", items)

def test_create_order_inventory_get_product_raises_exception_propagates():
    service = OrderService()
    service._inventory = MagicMock()
    service._pricing = MagicMock()
    service._orders = {}

    items = [{"product_id": "p1", "quantity": 1}]
    service._inventory.get_product.side_effect = RuntimeError("Inventory failure")

    with pytest.raises(RuntimeError, match="Inventory failure"):
        service.create_order("user1", items)
    service._inventory.get_product.assert_called_once_with("p1")

def test_create_order_pricing_calculate_total_raises_exception_propagates():
    service = OrderService()
    service._inventory = MagicMock()
    service._pricing = MagicMock()
    service._orders = {}

    items = [{"product_id": "p1", "quantity": 1}]
    service._inventory.get_product.return_value = None
    service._pricing.calculate_total.side_effect = RuntimeError("Pricing failure")

    with patch("inventory_system.services.order_service.generate_id", return_value="ORD-999"):
        with patch("inventory_system.services.order_service.get_timestamp", return_value=123):
            with pytest.raises(RuntimeError, match="Pricing failure"):
                service.create_order("user1", items)
    service._inventory.get_product.assert_called_once_with("p1")
    service._pricing.calculate_total.assert_called_once()

def test_create_order_with_zero_quantity_still_calls_get_product_and_creates_order():
    service = OrderService()
    service._inventory = MagicMock()
    service._pricing = MagicMock()
    service._orders = {}

    items = [{"product_id": "p1", "quantity": 0}]
    service._inventory.get_product.return_value = None
    service._pricing.calculate_total.return_value = 0

    with patch("inventory_system.services.order_service.generate_id", return_value="ORD-000"):
        with patch("inventory_system.services.order_service.get_timestamp", return_value=0):
            order = service.create_order("user1", items)

    assert order.items[0].quantity == 0
    assert order.total == 0
    assert service._orders["ORD-000"] == order

def test_create_order_with_none_user_id_creates_order():
    service = OrderService()
    service._inventory = MagicMock()
    service._pricing = MagicMock()
    service._orders = {}

    items = [{"product_id": "p1", "quantity": 1}]
    service._inventory.get_product.return_value = None
    service._pricing.calculate_total.return_value = 50

    with patch("inventory_system.services.order_service.generate_id", return_value="ORD-321"):
        with patch("inventory_system.services.order_service.get_timestamp", return_value=111):
            order = service.create_order(None, items)

    assert order.user_id is None
    assert order.total == 50
    assert service._orders["ORD-321"] == order

def test_create_order_with_malformed_item_raises_type_error():
    service = OrderService()
    service._inventory = MagicMock()
    service._pricing = MagicMock()
    service._orders = {}

    items = [None]

    with pytest.raises(TypeError):
        service.create_order("user1", items)
# AI_TEST_AGENT_END function=OrderService.create_order

# AI_TEST_AGENT_START function=OrderService.process_order
def make_order(status, items):
    order = MagicMock(spec=Order)
    order.status = status
    order.items = items
    return order

def make_item(product_id, quantity):
    item = MagicMock()
    item.product_id = product_id
    item.quantity = quantity
    return item

def test_process_order_successful_reservation(monkeypatch):
    service = OrderService()
    item1 = make_item("prod1", 5)
    item2 = make_item("prod2", 3)
    order = make_order(OrderStatus.PENDING, [item1, item2])
    monkeypatch.setattr(service, "get_order", lambda order_id: order)
    reservation_mock = MagicMock()
    reservation_mock.get_available.side_effect = [10, 5]
    reservation_mock.reserve_stock.return_value = None
    reservation_mock.release_stock.return_value = None
    service._reservation = reservation_mock

    result = service.process_order("order123")

    assert result is order
    assert order.status == OrderStatus.CONFIRMED
    assert reservation_mock.get_available.call_count == 2
    reservation_mock.get_available.assert_any_call("prod1")
    reservation_mock.get_available.assert_any_call("prod2")
    assert reservation_mock.reserve_stock.call_count == 2
    reservation_mock.reserve_stock.assert_any_call("prod1", 5)
    reservation_mock.reserve_stock.assert_any_call("prod2", 3)
    reservation_mock.release_stock.assert_not_called()

def test_process_order_raises_order_state_error_if_not_pending(monkeypatch):
    service = OrderService()
    order = make_order(OrderStatus.CONFIRMED, [])
    monkeypatch.setattr(service, "get_order", lambda order_id: order)
    service._reservation = MagicMock()

    with pytest.raises(OrderStateError) as excinfo:
        service.process_order("order123")
    assert "not in PENDING state" in str(excinfo.value)
    service._reservation.get_available.assert_not_called()
    service._reservation.reserve_stock.assert_not_called()
    service._reservation.release_stock.assert_not_called()

def test_process_order_raises_insufficient_stock_error_when_stock_not_enough(monkeypatch):
    service = OrderService()
    item1 = make_item("prod1", 5)
    order = make_order(OrderStatus.PENDING, [item1])
    monkeypatch.setattr(service, "get_order", lambda order_id: order)
    reservation_mock = MagicMock()
    reservation_mock.get_available.return_value = 3
    service._reservation = reservation_mock

    with pytest.raises(InsufficientStockError) as excinfo:
        service.process_order("order123")
    assert "insufficient stock" in str(excinfo.value)
    reservation_mock.get_available.assert_called_once_with("prod1")
    reservation_mock.reserve_stock.assert_not_called()
    reservation_mock.release_stock.assert_not_called()

def test_process_order_reserve_stock_raises_and_releases_already_reserved(monkeypatch):
    service = OrderService()
    item1 = make_item("prod1", 2)
    item2 = make_item("prod2", 3)
    order = make_order(OrderStatus.PENDING, [item1, item2])
    monkeypatch.setattr(service, "get_order", lambda order_id: order)
    reservation_mock = MagicMock()
    reservation_mock.get_available.side_effect = [5, 5]
    def reserve_side_effect(product_id, quantity):
        if product_id == "prod2":
            raise InsufficientStockError("No stock")
    reservation_mock.reserve_stock.side_effect = reserve_side_effect
    reservation_mock.release_stock.return_value = None
    service._reservation = reservation_mock

    with pytest.raises(InsufficientStockError) as excinfo:
        service.process_order("order123")
    assert "No stock" in str(excinfo.value)
    reservation_mock.get_available.assert_any_call("prod1")
    reservation_mock.get_available.assert_any_call("prod2")
    reservation_mock.reserve_stock.assert_any_call("prod1", 2)
    reservation_mock.reserve_stock.assert_any_call("prod2", 3)
    reservation_mock.release_stock.assert_called_once_with("prod1", 2)
    assert order.status == OrderStatus.PENDING

def test_process_order_with_empty_items_list(monkeypatch):
    service = OrderService()
    order = make_order(OrderStatus.PENDING, [])
    monkeypatch.setattr(service, "get_order", lambda order_id: order)
    reservation_mock = MagicMock()
    service._reservation = reservation_mock

    result = service.process_order("order123")

    assert result is order
    assert order.status == OrderStatus.CONFIRMED
    reservation_mock.get_available.assert_not_called()
    reservation_mock.reserve_stock.assert_not_called()
    reservation_mock.release_stock.assert_not_called()

def test_process_order_get_order_raises_order_not_found(monkeypatch):
    service = OrderService()
    def raise_not_found(order_id):
        raise OrderNotFoundError(f"Order {order_id!r} not found")
    monkeypatch.setattr(service, "get_order", raise_not_found)
    service._reservation = MagicMock()

    with pytest.raises(Exception) as excinfo:
        service.process_order("nonexistent")
    assert "not found" in str(excinfo.value)
    service._reservation.get_available.assert_not_called()
    service._reservation.reserve_stock.assert_not_called()
    service._reservation.release_stock.assert_not_called()

def test_process_order_invalid_order_id_type(monkeypatch):
    service = OrderService()
    monkeypatch.setattr(service, "get_order", lambda order_id: make_order(OrderStatus.PENDING, []))
    service._reservation = MagicMock()

    with pytest.raises(TypeError):
        service.process_order(None)

def test_process_order_item_quantity_zero(monkeypatch):
    service = OrderService()
    item = make_item("prod1", 0)
    order = make_order(OrderStatus.PENDING, [item])
    monkeypatch.setattr(service, "get_order", lambda order_id: order)
    reservation_mock = MagicMock()
    reservation_mock.get_available.return_value = 0
    reservation_mock.reserve_stock.return_value = None
    reservation_mock.release_stock.return_value = None
    service._reservation = reservation_mock

    result = service.process_order("order123")

    assert result is order
    assert order.status == OrderStatus.CONFIRMED
    reservation_mock.get_available.assert_called_once_with("prod1")
    reservation_mock.reserve_stock.assert_called_once_with("prod1", 0)
    reservation_mock.release_stock.assert_not_called()

def test_process_order_item_quantity_negative(monkeypatch):
    service = OrderService()
    item = make_item("prod1", -1)
    order = make_order(OrderStatus.PENDING, [item])
    monkeypatch.setattr(service, "get_order", lambda order_id: order)
    reservation_mock = MagicMock()
    reservation_mock.get_available.return_value = 10
    reservation_mock.reserve_stock.return_value = None
    reservation_mock.release_stock.return_value = None
    service._reservation = reservation_mock

    result = service.process_order("order123")

    assert result is order
    assert order.status == OrderStatus.CONFIRMED
    reservation_mock.get_available.assert_called_once_with("prod1")
    reservation_mock.reserve_stock.assert_called_once_with("prod1", -1)
    reservation_mock.release_stock.assert_not_called()
# AI_TEST_AGENT_END function=OrderService.process_order

# AI_TEST_AGENT_START function=OrderService.cancel_order
def make_order(status, items=None):
    order = MagicMock(spec=Order)
    order.status = status
    order.items = items or []
    return order

def make_item(product_id, quantity):
    item = MagicMock()
    item.product_id = product_id
    item.quantity = quantity
    return item

def test_cancel_order_pending_releases_stock_and_cancels(monkeypatch):
    service = OrderService()
    item1 = make_item('prod1', 3)
    item2 = make_item('prod2', 5)
    order = make_order(OrderStatus.PENDING, [item1, item2])
    service._reservation = MagicMock()
    service.get_order = MagicMock(return_value=order)

    result = service.cancel_order('order123')

    service.get_order.assert_called_once_with('order123')
    assert order.status == OrderStatus.CANCELLED
    service._reservation.release_stock.assert_any_call('prod1', 3)
    service._reservation.release_stock.assert_any_call('prod2', 5)
    assert service._reservation.release_stock.call_count == 2
    assert result is order

def test_cancel_order_confirmed_does_not_release_stock_but_cancels(monkeypatch):
    service = OrderService()
    order = make_order(OrderStatus.CONFIRMED, [make_item('prod1', 1)])
    service._reservation = MagicMock()
    service.get_order = MagicMock(return_value=order)

    result = service.cancel_order('order456')

    service.get_order.assert_called_once_with('order456')
    service._reservation.release_stock.assert_not_called()
    assert order.status == OrderStatus.CANCELLED
    assert result is order

@pytest.mark.parametrize("status", [
    OrderStatus.SHIPPED,
    OrderStatus.DELIVERED,
    OrderStatus.CANCELLED,
    OrderStatus.RETURNED,
])
def test_cancel_order_raises_for_invalid_status(status):
    service = OrderService()
    order = make_order(status)
    service.get_order = MagicMock(return_value=order)
    service._reservation = MagicMock()

    with pytest.raises(OrderStateError) as excinfo:
        service.cancel_order('order789')

    assert f"Order 'order789' cannot be cancelled" in str(excinfo.value)
    service._reservation.release_stock.assert_not_called()

def test_cancel_order_raises_when_order_not_found(monkeypatch):
    service = OrderService()
    service.get_order = MagicMock(side_effect=KeyError("not found"))
    service._reservation = MagicMock()

    with pytest.raises(KeyError, match="not found"):
        service.cancel_order('missing_order')

    service._reservation.release_stock.assert_not_called()

def test_cancel_order_with_empty_items_list(monkeypatch):
    service = OrderService()
    order = make_order(OrderStatus.PENDING, [])
    service.get_order = MagicMock(return_value=order)
    service._reservation = MagicMock()

    result = service.cancel_order('order_empty')

    service.get_order.assert_called_once_with('order_empty')
    service._reservation.release_stock.assert_not_called()
    assert order.status == OrderStatus.CANCELLED
    assert result is order

def test_cancel_order_with_none_order_id_raises(monkeypatch):
    service = OrderService()
    service.get_order = MagicMock(side_effect=KeyError("None not found"))
    service._reservation = MagicMock()

    with pytest.raises(KeyError, match="None not found"):
        service.cancel_order(None)

    service._reservation.release_stock.assert_not_called()

def test_cancel_order_with_empty_string_order_id_raises(monkeypatch):
    service = OrderService()
    service.get_order = MagicMock(side_effect=KeyError("'' not found"))
    service._reservation = MagicMock()

    with pytest.raises(KeyError, match="'' not found"):
        service.cancel_order('')

    service._reservation.release_stock.assert_not_called()
# AI_TEST_AGENT_END function=OrderService.cancel_order

# AI_TEST_AGENT_START function=OrderService.complete_order
def test_complete_order_success_single_item():
    service = OrderService()
    order_id = "order123"
    product_id = "prod1"
    item_quantity = 2

    product_mock = MagicMock()
    product_mock.stock = 10
    product_mock.reserved = 5

    item_mock = MagicMock()
    item_mock.product_id = product_id
    item_mock.quantity = item_quantity

    order_mock = MagicMock(spec=Order)
    order_mock.status = OrderStatus.CONFIRMED
    order_mock.items = [item_mock]

    service.get_order = MagicMock(return_value=order_mock)
    service._inventory = MagicMock()
    service._inventory.get_product = MagicMock(return_value=product_mock)

    result = service.complete_order(order_id)

    service.get_order.assert_called_once_with(order_id)
    service._inventory.get_product.assert_called_once_with(product_id)
    assert product_mock.stock == 10 - item_quantity
    assert product_mock.reserved == 5 - item_quantity
    assert result.status == OrderStatus.COMPLETED

def test_complete_order_raises_if_order_not_confirmed():
    service = OrderService()
    order_id = "order456"

    order_mock = MagicMock(spec=Order)
    order_mock.status = OrderStatus.COMPLETED
    order_mock.items = []

    service.get_order = MagicMock(return_value=order_mock)
    service._inventory = MagicMock()

    with pytest.raises(OrderStateError) as excinfo:
        service.complete_order(order_id)
    assert f"Order {order_id!r} must be CONFIRMED to complete" in str(excinfo.value)
    service.get_order.assert_called_once_with(order_id)
    service._inventory.get_product.assert_not_called()

def test_complete_order_multiple_items_stock_and_reserved_decremented():
    service = OrderService()
    order_id = "order789"

    product1 = MagicMock()
    product1.stock = 20
    product1.reserved = 10
    product2 = MagicMock()
    product2.stock = 15
    product2.reserved = 5

    item1 = MagicMock()
    item1.product_id = "prod1"
    item1.quantity = 3
    item2 = MagicMock()
    item2.product_id = "prod2"
    item2.quantity = 4

    order_mock = MagicMock(spec=Order)
    order_mock.status = OrderStatus.CONFIRMED
    order_mock.items = [item1, item2]

    service.get_order = MagicMock(return_value=order_mock)
    service._inventory = MagicMock()
    service._inventory.get_product = MagicMock(side_effect=[product1, product2])

    result = service.complete_order(order_id)

    service.get_order.assert_called_once_with(order_id)
    assert service._inventory.get_product.call_count == 2
    service._inventory.get_product.assert_any_call("prod1")
    service._inventory.get_product.assert_any_call("prod2")

    assert product1.stock == 17
    assert product1.reserved == 7
    assert product2.stock == 11
    assert product2.reserved == 1
    assert result.status == OrderStatus.COMPLETED

def test_complete_order_raises_order_not_found():
    service = OrderService()
    order_id = "nonexistent"

    def raise_not_found(oid):
        raise KeyError("Order not found")

    service.get_order = MagicMock(side_effect=KeyError("Order not found"))
    service._inventory = MagicMock()

    with pytest.raises(KeyError) as excinfo:
        service.complete_order(order_id)
    assert "Order not found" in str(excinfo.value)
    service.get_order.assert_called_once_with(order_id)
    service._inventory.get_product.assert_not_called()

def test_complete_order_with_zero_quantity_item():
    service = OrderService()
    order_id = "order_zero_qty"
    product_id = "prod_zero"

    product_mock = MagicMock()
    product_mock.stock = 5
    product_mock.reserved = 3

    item_mock = MagicMock()
    item_mock.product_id = product_id
    item_mock.quantity = 0

    order_mock = MagicMock(spec=Order)
    order_mock.status = OrderStatus.CONFIRMED
    order_mock.items = [item_mock]

    service.get_order = MagicMock(return_value=order_mock)
    service._inventory = MagicMock()
    service._inventory.get_product = MagicMock(return_value=product_mock)

    result = service.complete_order(order_id)

    service.get_order.assert_called_once_with(order_id)
    service._inventory.get_product.assert_called_once_with(product_id)
    assert product_mock.stock == 5
    assert product_mock.reserved == 3
    assert result.status == OrderStatus.COMPLETED

def test_complete_order_with_empty_items_list():
    service = OrderService()
    order_id = "order_empty_items"

    order_mock = MagicMock(spec=Order)
    order_mock.status = OrderStatus.CONFIRMED
    order_mock.items = []

    service.get_order = MagicMock(return_value=order_mock)
    service._inventory = MagicMock()

    result = service.complete_order(order_id)

    service.get_order.assert_called_once_with(order_id)
    service._inventory.get_product.assert_not_called()
    assert result.status == OrderStatus.COMPLETED

def test_complete_order_with_none_order_id_raises():
    service = OrderService()
    order_id = None

    service.get_order = MagicMock(side_effect=TypeError("order_id must be str"))
    service._inventory = MagicMock()

    with pytest.raises(TypeError) as excinfo:
        service.complete_order(order_id)
    assert "order_id must be str" in str(excinfo.value)
    service.get_order.assert_called_once_with(order_id)
    service._inventory.get_product.assert_not_called()

def test_complete_order_with_negative_quantity_item():
    service = OrderService()
    order_id = "order_neg_qty"
    product_id = "prod_neg"

    product_mock = MagicMock()
    product_mock.stock = 10
    product_mock.reserved = 5

    item_mock = MagicMock()
    item_mock.product_id = product_id
    item_mock.quantity = -3

    order_mock = MagicMock(spec=Order)
    order_mock.status = OrderStatus.CONFIRMED
    order_mock.items = [item_mock]

    service.get_order = MagicMock(return_value=order_mock)
    service._inventory = MagicMock()
    service._inventory.get_product = MagicMock(return_value=product_mock)

    result = service.complete_order(order_id)

    service.get_order.assert_called_once_with(order_id)
    service._inventory.get_product.assert_called_once_with(product_id)
    assert product_mock.stock == 10 - (-3)
    assert product_mock.reserved == 5 - (-3)
    assert result.status == OrderStatus.COMPLETED
# AI_TEST_AGENT_END function=OrderService.complete_order

# AI_TEST_AGENT_START function=OrderService.get_order
def test_get_order_returns_order_when_order_exists():
    service = OrderService()
    mock_order = MagicMock()
    with patch.object(service, '_orders', {'order123': mock_order}):
        result = service.get_order('order123')
    assert result is mock_order

def test_get_order_raises_order_not_found_error_when_order_missing():
    service = OrderService()
    with patch.object(service, '_orders', {}):
        with pytest.raises(OrderNotFoundError, match=r"Order 'missing_order' not found"):
            service.get_order('missing_order')

def test_get_order_raises_order_not_found_error_with_empty_string_order_id():
    service = OrderService()
    with patch.object(service, '_orders', {}):
        with pytest.raises(OrderNotFoundError, match=r"Order '' not found"):
            service.get_order('')

def test_get_order_raises_order_not_found_error_with_none_order_id():
    service = OrderService()
    with patch.object(service, '_orders', {}):
        with pytest.raises(OrderNotFoundError, match=r"Order None not found"):
            service.get_order(None)

def test_get_order_raises_order_not_found_error_with_numeric_order_id():
    service = OrderService()
    with patch.object(service, '_orders', {}):
        with pytest.raises(OrderNotFoundError, match=r"Order 123 not found"):
            service.get_order(123)

def test_get_order_returns_order_when_order_id_is_numeric_string():
    service = OrderService()
    mock_order = MagicMock()
    with patch.object(service, '_orders', {'123': mock_order}):
        result = service.get_order('123')
    assert result is mock_order

def test_get_order_returns_order_when_order_id_is_special_characters():
    service = OrderService()
    special_id = '!@#$%^&*()'
    mock_order = MagicMock()
    with patch.object(service, '_orders', {special_id: mock_order}):
        result = service.get_order(special_id)
    assert result is mock_order

def test_get_order_raises_order_not_found_error_when_order_id_is_whitespace():
    service = OrderService()
    whitespace_id = '   '
    with patch.object(service, '_orders', {}):
        with pytest.raises(OrderNotFoundError, match=r"Order '   ' not found"):
            service.get_order(whitespace_id)
# AI_TEST_AGENT_END function=OrderService.get_order

# AI_TEST_AGENT_START function=OrderService.get_order_summary
class DummyStatus:
    def __init__(self, value):
        self.value = value


class DummyOrder:
    def __init__(self, order_id, user_id, status, items, total, discount_applied):
        self.order_id = order_id
        self.user_id = user_id
        self.status = status
        self.items = items
        self.total = total
        self.discount_applied = discount_applied


def test_get_order_summary_returns_correct_summary(monkeypatch):
    service = OrderService()
    dummy_order = DummyOrder(
        order_id="order123",
        user_id="user456",
        status=DummyStatus("shipped"),
        items=[1, 2, 3],
        total=99.99,
        discount_applied=True,
    )
    monkeypatch.setattr(service, "get_order", lambda order_id: dummy_order)
    result = service.get_order_summary("order123")
    assert result["order_id"] == "order123"
    assert result["user_id"] == "user456"
    assert result["status"] == "shipped"
    assert result["item_count"] == 3
    assert result["total"] == 99.99
    assert result["discount_applied"] is True


def test_get_order_summary_with_empty_items_list(monkeypatch):
    service = OrderService()
    dummy_order = DummyOrder(
        order_id="order_empty",
        user_id="user_empty",
        status=DummyStatus("pending"),
        items=[],
        total=0.0,
        discount_applied=False,
    )
    monkeypatch.setattr(service, "get_order", lambda order_id: dummy_order)
    result = service.get_order_summary("order_empty")
    assert result["order_id"] == "order_empty"
    assert result["user_id"] == "user_empty"
    assert result["status"] == "pending"
    assert result["item_count"] == 0
    assert result["total"] == 0.0
    assert result["discount_applied"] is False


def test_get_order_summary_raises_order_not_found(monkeypatch):
    service = OrderService()
    def raise_not_found(order_id):
        raise OrderNotFoundError(f"Order {order_id!r} not found")
    monkeypatch.setattr(service, "get_order", raise_not_found)
    with pytest.raises(OrderNotFoundError, match="Order 'missing_order' not found"):
        service.get_order_summary("missing_order")


def test_get_order_summary_with_discount_false(monkeypatch):
    service = OrderService()
    dummy_order = DummyOrder(
        order_id="order_no_discount",
        user_id="user789",
        status=DummyStatus("delivered"),
        items=[1],
        total=50.0,
        discount_applied=False,
    )
    monkeypatch.setattr(service, "get_order", lambda order_id: dummy_order)
    result = service.get_order_summary("order_no_discount")
    assert result["discount_applied"] is False
    assert result["item_count"] == 1
    assert result["total"] == 50.0


def test_get_order_summary_with_zero_total(monkeypatch):
    service = OrderService()
    dummy_order = DummyOrder(
        order_id="order_zero_total",
        user_id="user_zero",
        status=DummyStatus("cancelled"),
        items=[1, 2],
        total=0.0,
        discount_applied=True,
    )
    monkeypatch.setattr(service, "get_order", lambda order_id: dummy_order)
    result = service.get_order_summary("order_zero_total")
    assert result["total"] == 0.0
    assert result["item_count"] == 2
    assert result["discount_applied"] is True


def test_get_order_summary_with_none_order_id(monkeypatch):
    service = OrderService()
    dummy_order = DummyOrder(
        order_id=None,
        user_id="user_none",
        status=DummyStatus("processing"),
        items=[1],
        total=10.0,
        discount_applied=False,
    )
    monkeypatch.setattr(service, "get_order", lambda order_id: dummy_order)
    result = service.get_order_summary(None)
    assert result["order_id"] is None
    assert result["user_id"] == "user_none"
    assert result["status"] == "processing"
    assert result["item_count"] == 1
    assert result["total"] == 10.0
    assert result["discount_applied"] is False


def test_get_order_summary_with_non_string_order_id(monkeypatch):
    service = OrderService()
    dummy_order = DummyOrder(
        order_id=123,
        user_id="user_int",
        status=DummyStatus("new"),
        items=[1, 2, 3, 4],
        total=200.0,
        discount_applied=True,
    )
    monkeypatch.setattr(service, "get_order", lambda order_id: dummy_order)
    result = service.get_order_summary(123)
    assert result["order_id"] == 123
    assert result["user_id"] == "user_int"
    assert result["status"] == "new"
    assert result["item_count"] == 4
    assert result["total"] == 200.0
    assert result["discount_applied"] is True


def test_get_order_summary_with_status_value_none(monkeypatch):
    service = OrderService()
    dummy_order = DummyOrder(
        order_id="order_none_status",
        user_id="user_none_status",
        status=DummyStatus(None),
        items=[1],
        total=15.0,
        discount_applied=False,
    )
    monkeypatch.setattr(service, "get_order", lambda order_id: dummy_order)
    result = service.get_order_summary("order_none_status")
    assert result["status"] is None
    assert result["order_id"] == "order_none_status"
    assert result["user_id"] == "user_none_status"
    assert result["item_count"] == 1
    assert result["total"] == 15.0
    assert result["discount_applied"] is False
# AI_TEST_AGENT_END function=OrderService.get_order_summary
