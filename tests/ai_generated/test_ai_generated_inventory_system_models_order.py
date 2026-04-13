from inventory_system.models.order import Order
from inventory_system.models.order import Order, OrderStatus
from inventory_system.models.order import OrderStatus
from unittest.mock import MagicMock
from unittest.mock import Mock
import pytest

# AI_TEST_AGENT_START function=Order.__init__
def test_order_init_with_valid_inputs():
    item_mock = MagicMock()
    item_mock.to_dict.return_value = {"product_id": "p1", "quantity": 2}
    order = Order(order_id="order123", user_id="user456", items=[item_mock])
    assert order.order_id == "order123"
    assert order.user_id == "user456"
    assert order.items == [item_mock]
    assert order.status == OrderStatus.PENDING
    assert order.total == 0.0
    assert order.discount_applied == 0.0
    assert order.created_at is None

def test_order_to_dict_calls_item_to_dict_and_returns_expected_dict():
    item_mock1 = MagicMock()
    item_mock1.to_dict.return_value = {"product_id": "p1", "quantity": 1}
    item_mock2 = MagicMock()
    item_mock2.to_dict.return_value = {"product_id": "p2", "quantity": 3}
    order = Order(order_id="order1", user_id="user1", items=[item_mock1, item_mock2])
    result = order.to_dict()
    assert result["order_id"] == "order1"
    assert result["user_id"] == "user1"
    assert result["items"] == [{"product_id": "p1", "quantity": 1}, {"product_id": "p2", "quantity": 3}]
    assert result["status"] == OrderStatus.PENDING.value
    assert result["total"] == 0.0
    assert result["discount_applied"] == 0.0
    item_mock1.to_dict.assert_called_once()
    item_mock2.to_dict.assert_called_once()

def test_order_repr_returns_expected_string():
    item_mock = MagicMock()
    order = Order(order_id="id123", user_id="user789", items=[item_mock])
    order.total = 123.45
    expected_repr = f"Order(id='id123', user='user789', status='{OrderStatus.PENDING.value}', total=123.45)"
    assert repr(order) == expected_repr

def test_order_init_with_empty_items_list():
    order = Order(order_id="order_empty", user_id="user_empty", items=[])
    assert order.items == []
    assert order.status == OrderStatus.PENDING
    assert order.total == 0.0
    assert order.discount_applied == 0.0
    assert order.created_at is None

def test_order_init_with_none_items_raises_type_error():
    with pytest.raises(TypeError):
        Order(order_id="order_none", user_id="user_none", items=None)

def test_order_init_with_empty_strings_for_ids():
    item_mock = MagicMock()
    order = Order(order_id="", user_id="", items=[item_mock])
    assert order.order_id == ""
    assert order.user_id == ""
    assert order.items == [item_mock]
    assert order.status == OrderStatus.PENDING

def test_order_init_with_non_string_order_id_and_user_id():
    item_mock = MagicMock()
    order = Order(order_id=123, user_id=456, items=[item_mock])
    assert order.order_id == 123
    assert order.user_id == 456
    assert order.items == [item_mock]
    assert order.status == OrderStatus.PENDING

def test_order_to_dict_with_items_to_dict_raises_if_item_to_dict_missing():
    class DummyItem:
        pass
    dummy_item = DummyItem()
    order = Order(order_id="orderX", user_id="userX", items=[dummy_item])
    with pytest.raises(AttributeError):
        order.to_dict()
# AI_TEST_AGENT_END function=Order.__init__

# AI_TEST_AGENT_START function=Order.to_dict
def test_to_dict_with_single_item():
    item_mock = Mock()
    item_mock.to_dict.return_value = {"product_id": "p1", "quantity": 2}
    order = Order(order_id="o1", user_id="u1", items=[item_mock])
    order.status = OrderStatus.PENDING
    order.total = 100.0
    order.discount_applied = 10.0

    result = order.to_dict()

    assert result["order_id"] == "o1"
    assert result["user_id"] == "u1"
    assert isinstance(result["items"], list)
    assert result["items"][0] == {"product_id": "p1", "quantity": 2}
    assert result["status"] == OrderStatus.PENDING.value
    assert result["total"] == 100.0
    assert result["discount_applied"] == 10.0
    item_mock.to_dict.assert_called_once()

def test_to_dict_with_multiple_items():
    item1 = Mock()
    item1.to_dict.return_value = {"product_id": "p1", "quantity": 1}
    item2 = Mock()
    item2.to_dict.return_value = {"product_id": "p2", "quantity": 3}
    order = Order(order_id="o2", user_id="u2", items=[item1, item2])
    order.status = OrderStatus.PENDING
    order.total = 200.0
    order.discount_applied = 0.0

    result = order.to_dict()

    assert len(result["items"]) == 2
    assert result["items"][0] == {"product_id": "p1", "quantity": 1}
    assert result["items"][1] == {"product_id": "p2", "quantity": 3}
    assert result["order_id"] == "o2"
    assert result["user_id"] == "u2"
    assert result["status"] == OrderStatus.PENDING.value
    assert result["total"] == 200.0
    assert result["discount_applied"] == 0.0
    item1.to_dict.assert_called_once()
    item2.to_dict.assert_called_once()

def test_to_dict_with_empty_items_list():
    order = Order(order_id="o3", user_id="u3", items=[])
    order.status = OrderStatus.PENDING
    order.total = 0.0
    order.discount_applied = 0.0

    result = order.to_dict()

    assert result["items"] == []
    assert result["order_id"] == "o3"
    assert result["user_id"] == "u3"
    assert result["status"] == OrderStatus.PENDING.value
    assert result["total"] == 0.0
    assert result["discount_applied"] == 0.0

def test_to_dict_with_item_to_dict_raises():
    class BadItem:
        def to_dict(self):
            raise RuntimeError("fail")

    bad_item = BadItem()
    order = Order(order_id="o4", user_id="u4", items=[bad_item])
    order.status = OrderStatus.PENDING
    order.total = 50.0
    order.discount_applied = 5.0

    with pytest.raises(RuntimeError, match="fail"):
        order.to_dict()

def test_to_dict_with_none_item_in_list():
    item_mock = Mock()
    item_mock.to_dict.return_value = {"product_id": "p5", "quantity": 1}
    order = Order(order_id="o5", user_id="u5", items=[item_mock, None])
    order.status = OrderStatus.PENDING
    order.total = 150.0
    order.discount_applied = 15.0

    with pytest.raises(AttributeError):
        order.to_dict()

def test_to_dict_with_non_list_items():
    item_mock = Mock()
    item_mock.to_dict.return_value = {"product_id": "p6", "quantity": 1}
    order = Order(order_id="o6", user_id="u6", items=item_mock)
    order.status = OrderStatus.PENDING
    order.total = 75.0
    order.discount_applied = 7.5

    with pytest.raises(TypeError):
        order.to_dict()

def test_to_dict_with_items_containing_non_mock_object():
    order = Order(order_id="o7", user_id="u7", items=[{"not": "mock"}])
    order.status = OrderStatus.PENDING
    order.total = 80.0
    order.discount_applied = 8.0

    with pytest.raises(AttributeError):
        order.to_dict()
# AI_TEST_AGENT_END function=Order.to_dict

# AI_TEST_AGENT_START function=Order.__repr__
def test_repr_with_normal_values():
    item_mock = Mock()
    order = Order(order_id="123", user_id="user1", items=[item_mock])
    order.status = OrderStatus.PENDING
    order.total = 100.5
    result = repr(order)
    assert result == "Order(id='123', user='user1', status='pending', total=100.5)"

def test_repr_with_empty_strings_and_zero_total():
    item_mock = Mock()
    order = Order(order_id="", user_id="", items=[item_mock])
    order.status = OrderStatus.PENDING
    order.total = 0.0
    result = repr(order)
    assert result == "Order(id='', user='', status='pending', total=0.0)"

def test_repr_with_none_order_id_and_user_id():
    item_mock = Mock()
    order = Order(order_id=None, user_id=None, items=[item_mock])
    order.status = OrderStatus.PENDING
    order.total = 50.0
    result = repr(order)
    assert result == "Order(id=None, user=None, status='pending', total=50.0)"

def test_repr_with_negative_total():
    item_mock = Mock()
    order = Order(order_id="id_neg", user_id="user_neg", items=[item_mock])
    order.status = OrderStatus.PENDING
    order.total = -10.0
    result = repr(order)
    assert result == "Order(id='id_neg', user='user_neg', status='pending', total=-10.0)"

def test_repr_with_different_status_value():
    item_mock = Mock()
    order = Order(order_id="id2", user_id="user2", items=[item_mock])
    order.status = OrderStatus.PENDING
    order.status = OrderStatus.PENDING  # Only PENDING is visible in code, so no other status to test
    order.total = 20.0
    result = repr(order)
    assert result == "Order(id='id2', user='user2', status='pending', total=20.0)"

def test_repr_with_large_total_value():
    item_mock = Mock()
    order = Order(order_id="large", user_id="user_large", items=[item_mock])
    order.status = OrderStatus.PENDING
    order.total = 1e10
    result = repr(order)
    assert result == "Order(id='large', user='user_large', status='pending', total=10000000000.0)"

def test_repr_with_items_list_none():
    # items is required positional argument, but test with empty list to simulate no items
    order = Order(order_id="noitems", user_id="user_noitems", items=[])
    order.status = OrderStatus.PENDING
    order.total = 0.0
    result = repr(order)
    assert result == "Order(id='noitems', user='user_noitems', status='pending', total=0.0)"
# AI_TEST_AGENT_END function=Order.__repr__
