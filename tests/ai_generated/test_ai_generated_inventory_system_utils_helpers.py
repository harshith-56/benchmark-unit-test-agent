from inventory_system.utils.helpers import batch_lookup
from inventory_system.utils.helpers import compute_order_weight
from inventory_system.utils.helpers import validate_quantity
from unittest.mock import MagicMock
import pytest

# AI_TEST_AGENT_START function=validate_quantity
def test_validate_quantity_with_valid_positive_integer():
    result = validate_quantity(10)
    assert result is True

def test_validate_quantity_with_zero():
    result = validate_quantity(0)
    assert result is True

def test_validate_quantity_with_negative_integer_raises_value_error():
    with pytest.raises(ValueError, match="Quantity cannot be negative"):
        validate_quantity(-1)

def test_validate_quantity_with_float_raises_type_error():
    with pytest.raises(TypeError, match="Quantity must be an integer"):
        validate_quantity(3.14)

def test_validate_quantity_with_string_raises_type_error():
    with pytest.raises(TypeError, match="Quantity must be an integer"):
        validate_quantity("5")

def test_validate_quantity_with_none_raises_type_error():
    with pytest.raises(TypeError, match="Quantity must be an integer"):
        validate_quantity(None)

def test_validate_quantity_with_boolean_true_raises_type_error():
    with pytest.raises(TypeError, match="Quantity must be an integer"):
        validate_quantity(True)

def test_validate_quantity_with_boolean_false_raises_type_error():
    with pytest.raises(TypeError, match="Quantity must be an integer"):
        validate_quantity(False)
# AI_TEST_AGENT_END function=validate_quantity

# AI_TEST_AGENT_START function=compute_order_weight
class DummyItem:
    def __init__(self, quantity):
        self.quantity = quantity

def test_compute_order_weight_empty_list():
    result = compute_order_weight([])
    assert result == 0

def test_compute_order_weight_single_item_positive_quantity():
    item = DummyItem(quantity=5)
    result = compute_order_weight([item])
    assert result == 5

def test_compute_order_weight_multiple_items_positive_quantities():
    items = [DummyItem(quantity=1), DummyItem(quantity=2), DummyItem(quantity=3)]
    result = compute_order_weight(items)
    assert result == 6

def test_compute_order_weight_items_with_zero_quantity():
    items = [DummyItem(quantity=0), DummyItem(quantity=0)]
    result = compute_order_weight(items)
    assert result == 0

def test_compute_order_weight_items_with_negative_quantity():
    items = [DummyItem(quantity=3), DummyItem(quantity=-1)]
    result = compute_order_weight(items)
    assert result == 2

def test_compute_order_weight_items_with_mixed_types_quantity():
    items = [DummyItem(quantity=2), DummyItem(quantity=3.5)]
    result = compute_order_weight(items)
    assert result == 5.5

def test_compute_order_weight_items_with_quantity_none():
    items = [DummyItem(quantity=1), DummyItem(quantity=None)]
    with pytest.raises(TypeError):
        compute_order_weight(items)

def test_compute_order_weight_items_with_missing_quantity_attribute():
    class IncompleteItem:
        pass
    items = [DummyItem(quantity=1), IncompleteItem()]
    with pytest.raises(AttributeError):
        compute_order_weight(items)

def test_compute_order_weight_items_with_non_numeric_quantity():
    items = [DummyItem(quantity=1), DummyItem(quantity="two")]
    with pytest.raises(TypeError):
        compute_order_weight(items)
# AI_TEST_AGENT_END function=compute_order_weight

# AI_TEST_AGENT_START function=batch_lookup
def test_batch_lookup_all_ids_found():
    product_ids = ['p1', 'p2', 'p3']
    product_map = MagicMock()
    product_map.keys.return_value = ['p1', 'p2', 'p3', 'p4']
    product_map.__getitem__.side_effect = lambda k: f'product_{k}'
    result = batch_lookup(product_ids, product_map)
    assert result == ['product_p1', 'product_p2', 'product_p3']
    product_map.keys.assert_called_once()

def test_batch_lookup_some_ids_not_found():
    product_ids = ['p1', 'p5', 'p3']
    product_map = MagicMock()
    product_map.keys.return_value = ['p1', 'p2', 'p3']
    product_map.__getitem__.side_effect = lambda k: f'product_{k}'
    result = batch_lookup(product_ids, product_map)
    assert result == ['product_p1', 'product_p3']
    product_map.keys.assert_called_once()

def test_batch_lookup_empty_product_ids():
    product_ids = []
    product_map = MagicMock()
    product_map.keys.return_value = ['p1', 'p2']
    result = batch_lookup(product_ids, product_map)
    assert result == []
    product_map.keys.assert_called_once()

def test_batch_lookup_empty_product_map():
    product_ids = ['p1', 'p2']
    product_map = MagicMock()
    product_map.keys.return_value = []
    result = batch_lookup(product_ids, product_map)
    assert result == []
    product_map.keys.assert_called_once()

def test_batch_lookup_duplicate_product_ids():
    product_ids = ['p1', 'p1', 'p2']
    product_map = MagicMock()
    product_map.keys.return_value = ['p1', 'p2']
    product_map.__getitem__.side_effect = lambda k: f'product_{k}'
    result = batch_lookup(product_ids, product_map)
    assert result == ['product_p1', 'product_p1', 'product_p2']
    product_map.keys.assert_called_once()

def test_batch_lookup_product_ids_with_none_and_empty_string():
    product_ids = [None, '', 'p1']
    product_map = MagicMock()
    product_map.keys.return_value = ['p1', '']
    product_map.__getitem__.side_effect = lambda k: f'product_{k}'
    result = batch_lookup(product_ids, product_map)
    assert result == ['product_', 'product_p1']
    product_map.keys.assert_called_once()

def test_batch_lookup_product_map_keys_called_once_even_with_duplicates():
    product_ids = ['p1', 'p2', 'p3', 'p2']
    product_map = MagicMock()
    product_map.keys.return_value = ['p1', 'p2', 'p3']
    product_map.__getitem__.side_effect = lambda k: f'product_{k}'
    result = batch_lookup(product_ids, product_map)
    assert result == ['product_p1', 'product_p2', 'product_p3', 'product_p2']
    product_map.keys.assert_called_once()

def test_batch_lookup_product_map_keys_returns_non_list_iterable():
    product_ids = ['p1', 'p2']
    product_map = MagicMock()
    product_map.keys.return_value = ('p1', 'p2', 'p3')
    product_map.__getitem__.side_effect = lambda k: f'product_{k}'
    result = batch_lookup(product_ids, product_map)
    assert result == ['product_p1', 'product_p2']
    product_map.keys.assert_called_once()

def test_batch_lookup_product_map_keys_returns_empty_list_and_product_ids_nonempty():
    product_ids = ['p1']
    product_map = MagicMock()
    product_map.keys.return_value = []
    result = batch_lookup(product_ids, product_map)
    assert result == []
    product_map.keys.assert_called_once()
# AI_TEST_AGENT_END function=batch_lookup
