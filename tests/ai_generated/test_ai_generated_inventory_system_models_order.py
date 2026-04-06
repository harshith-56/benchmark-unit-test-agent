from inventory_system.models.order import Order
from inventory_system.models.order import Order, OrderStatus
from inventory_system.models.order import OrderStatus
from unittest.mock import Mock
import pytest

# AI_TEST_AGENT_START function=Order.__init__
def test_order_init_with_valid_inputs():
    mock_item = Mock()
    mock_item.to_dict.return_value = {"product_id": "p1", "quantity": 2}
    items = [mock_item]
    order = Order(order_id="order123", user_id="user456", items=items)
    assert order.order_id == "order123"
    assert order.user_id == "user456"
    assert order.items == items
    assert order.status == OrderStatus.PENDING
    assert order.total == 0.0
    assert order.discount_applied == 0.0
    assert order.created_at is None

def test_order_to_dict_calls_to_dict_on_all_items():
    mock_item1 = Mock()
    mock_item1.to_dict.return_value = {"product_id": "p1", "quantity": 1}
    mock_item2 = Mock()
    mock_item2.to_dict.return_value = {"product_id": "p2", "quantity": 3}
    items = [mock_item1, mock_item2]
    order = Order(order_id="o1", user_id="u1", items=items)
    result = order.to_dict()
    assert result["order_id"] == "o1"
    assert result["user_id"] == "u1"
    assert result["status"] == OrderStatus.PENDING.value
    assert result["total"] == 0.0
    assert result["discount_applied"] == 0.0
    assert result["items"] == [{"product_id": "p1", "quantity": 1}, {"product_id": "p2", "quantity": 3}]
    mock_item1.to_dict.assert_called_once()
    mock_item2.to_dict.assert_called_once()

def test_order_repr_returns_expected_string():
    mock_item = Mock()
    items = [mock_item]
    order = Order(order_id="id123", user_id="user789", items=items)
    order.status = OrderStatus.PENDING
    order.total = 123.45
    repr_str = repr(order)
    assert repr_str == "Order(id='id123', user='user789', status='PENDING', total=123.45)"

def test_order_init_with_empty_items_list():
    items = []
    order = Order(order_id="emptyitems", user_id="user0", items=items)
    assert order.items == []
    assert order.status == OrderStatus.PENDING
    assert order.total == 0.0
    assert order.discount_applied == 0.0

def test_order_init_with_none_order_id_raises_type_error():
    mock_item = Mock()
    with pytest.raises(TypeError):
        Order(order_id=None, user_id="user1", items=[mock_item])

def test_order_init_with_none_user_id_raises_type_error():
    mock_item = Mock()
    with pytest.raises(TypeError):
        Order(order_id="order1", user_id=None, items=[mock_item])

def test_order_init_with_items_containing_none_raises_attribute_error():
    items = [None]
    with pytest.raises(AttributeError):
        Order(order_id="order2", user_id="user2", items=items)

def test_order_to_dict_with_items_to_dict_raising_exception_propagates():
    mock_item = Mock()
    mock_item.to_dict.side_effect = RuntimeError("to_dict failure")
    order = Order(order_id="order3", user_id="user3", items=[mock_item])
    with pytest.raises(RuntimeError, match="to_dict failure"):
        order.to_dict()
# AI_TEST_AGENT_END function=Order.__init__

# AI_TEST_AGENT_START function=Order.to_dict
def test_to_dict_with_single_item_called_to_dict_once():
    mock_item = Mock()
    mock_item.to_dict.return_value = {'product_id': 'p1', 'quantity': 2}
    order = Order(order_id='o1', user_id='u1', items=[mock_item])
    order.status = OrderStatus.PENDING
    order.total = 100.0
    order.discount_applied = 10.0
    result = order.to_dict()
    assert result['order_id'] == 'o1'
    assert result['user_id'] == 'u1'
    assert result['items'] == [{'product_id': 'p1', 'quantity': 2}]
    assert result['status'] == OrderStatus.PENDING.value
    assert result['total'] == 100.0
    assert result['discount_applied'] == 10.0
    mock_item.to_dict.assert_called_once()

def test_to_dict_with_multiple_items_all_to_dict_called():
    mock_item1 = Mock()
    mock_item1.to_dict.return_value = {'product_id': 'p1', 'quantity': 1}
    mock_item2 = Mock()
    mock_item2.to_dict.return_value = {'product_id': 'p2', 'quantity': 3}
    order = Order(order_id='o2', user_id='u2', items=[mock_item1, mock_item2])
    order.status = OrderStatus.COMPLETED
    order.total = 250.0
    order.discount_applied = 25.0
    result = order.to_dict()
    assert result['order_id'] == 'o2'
    assert result['user_id'] == 'u2'
    assert result['items'] == [{'product_id': 'p1', 'quantity': 1}, {'product_id': 'p2', 'quantity': 3}]
    assert result['status'] == OrderStatus.COMPLETED.value
    assert result['total'] == 250.0
    assert result['discount_applied'] == 25.0
    assert mock_item1.to_dict.call_count == 1
    assert mock_item2.to_dict.call_count == 1

def test_to_dict_with_empty_items_list_returns_empty_items_array():
    order = Order(order_id='o3', user_id='u3', items=[])
    order.status = OrderStatus.CANCELLED
    order.total = 0.0
    order.discount_applied = 0.0
    result = order.to_dict()
    assert result['order_id'] == 'o3'
    assert result['user_id'] == 'u3'
    assert result['items'] == []
    assert result['status'] == OrderStatus.CANCELLED.value
    assert result['total'] == 0.0
    assert result['discount_applied'] == 0.0

def test_to_dict_with_none_items_raises_attribute_error():
    order = Order(order_id='o4', user_id='u4', items=None)
    order.status = OrderStatus.PENDING
    order.total = 50.0
    order.discount_applied = 5.0
    with pytest.raises(TypeError):
        order.to_dict()

def test_to_dict_with_item_to_dict_raising_exception_propagates():
    mock_item = Mock()
    mock_item.to_dict.side_effect = RuntimeError("to_dict failure")
    order = Order(order_id='o5', user_id='u5', items=[mock_item])
    order.status = OrderStatus.PENDING
    order.total = 10.0
    order.discount_applied = 1.0
    with pytest.raises(RuntimeError, match="to_dict failure"):
        order.to_dict()

def test_to_dict_with_status_default_value_is_pending():
    mock_item = Mock()
    mock_item.to_dict.return_value = {'product_id': 'p6', 'quantity': 4}
    order = Order(order_id='o6', user_id='u6', items=[mock_item])
    # status not changed, should be PENDING by default
    result = order.to_dict()
    assert result['status'] == OrderStatus.PENDING.value

def test_to_dict_with_zero_total_and_discount():
    mock_item = Mock()
    mock_item.to_dict.return_value = {'product_id': 'p7', 'quantity': 0}
    order = Order(order_id='o7', user_id='u7', items=[mock_item])
    order.status = OrderStatus.PENDING
    order.total = 0.0
    order.discount_applied = 0.0
    result = order.to_dict()
    assert result['total'] == 0.0
    assert result['discount_applied'] == 0.0

def test_to_dict_with_negative_total_and_discount():
    mock_item = Mock()
    mock_item.to_dict.return_value = {'product_id': 'p8', 'quantity': 1}
    order = Order(order_id='o8', user_id='u8', items=[mock_item])
    order.status = OrderStatus.PENDING
    order.total = -100.0
    order.discount_applied = -10.0
    result = order.to_dict()
    assert result['total'] == -100.0
    assert result['discount_applied'] == -10.0

def test_repr_returns_expected_string_format():
    order = Order(order_id='o9', user_id='u9', items=[])
    order.status = OrderStatus.PENDING
    order.total = 123.45
    repr_str = repr(order)
    assert repr_str == f"Order(id='o9', user='u9', status='{OrderStatus.PENDING.value}', total=123.45)"
# AI_TEST_AGENT_END function=Order.to_dict

# AI_TEST_AGENT_START function=Order.__repr__
def test_order_repr_with_normal_values():
    order = Order(order_id="123", user_id="user1", items=[])
    order.status = OrderStatus.PENDING
    order.total = 100.50
    result = repr(order)
    assert result == "Order(id='123', user='user1', status='PENDING', total=100.5)"

def test_order_repr_with_empty_strings_and_zero_total():
    order = Order(order_id="", user_id="", items=[])
    order.status = OrderStatus.PENDING
    order.total = 0.0
    result = repr(order)
    assert result == "Order(id='', user='', status='PENDING', total=0.0)"

def test_order_repr_with_none_order_id_and_user_id():
    order = Order(order_id=None, user_id=None, items=[])
    order.status = OrderStatus.PENDING
    order.total = 10.0
    result = repr(order)
    assert result == "Order(id=None, user=None, status='PENDING', total=10.0)"

def test_order_repr_with_negative_total():
    order = Order(order_id="id_neg", user_id="user_neg", items=[])
    order.status = OrderStatus.PENDING
    order.total = -50.75
    result = repr(order)
    assert result == "Order(id='id_neg', user='user_neg', status='PENDING', total=-50.75)"

def test_order_repr_with_different_status():
    order = Order(order_id="id2", user_id="user2", items=[])
    order.status = OrderStatus.COMPLETED
    order.total = 20.0
    result = repr(order)
    assert result == "Order(id='id2', user='user2', status='COMPLETED', total=20.0)"

def test_order_repr_with_large_total_value():
    order = Order(order_id="id_large", user_id="user_large", items=[])
    order.status = OrderStatus.PENDING
    order.total = 1e10
    result = repr(order)
    assert result == "Order(id='id_large', user='user_large', status='PENDING', total=10000000000.0)"

def test_order_repr_with_status_value_edge_case():
    order = Order(order_id="id_edge", user_id="user_edge", items=[])
    class FakeStatus:
        value = ""
    order.status = FakeStatus()
    order.total = 5.0
    result = repr(order)
    assert result == "Order(id='id_edge', user='user_edge', status='', total=5.0)"

def test_order_repr_with_non_string_order_id_and_user_id():
    order = Order(order_id=123, user_id=456, items=[])
    order.status = OrderStatus.PENDING
    order.total = 15.0
    result = repr(order)
    assert result == "Order(id=123, user=456, status='PENDING', total=15.0)"
# AI_TEST_AGENT_END function=Order.__repr__
