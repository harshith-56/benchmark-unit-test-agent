from inventory_system.services.inventory_service import InventoryService
from inventory_system.services.inventory_service import InventoryService, ProductNotFoundError
from inventory_system.services.inventory_service import Product
from unittest.mock import MagicMock
from unittest.mock import MagicMock, patch
from unittest.mock import patch, MagicMock
import pytest

# AI_TEST_AGENT_START function=InventoryService.add_product
def test_add_product_valid_input_adds_product_and_returns_product():
    service = InventoryService()
    product_id = "p123"
    name = "Test Product"
    price = 10.5

    with patch.object(name, 'strip', return_value=name):
        with patch.object(service, '_products', new_callable=dict) as mock_products:
            result = service.add_product(product_id, name, price)
            assert isinstance(result, Product)
            assert result.product_id == product_id
            assert result.name == name
            assert result.price == price
            assert product_id in mock_products
            assert mock_products[product_id] == result

def test_add_product_price_negative_raises_value_error():
    service = InventoryService()
    product_id = "p124"
    name = "Valid Name"
    price = -0.01

    with patch.object(name, 'strip', return_value=name):
        with patch.object(service, '_products', new_callable=dict):
            with pytest.raises(ValueError, match="Price cannot be negative"):
                service.add_product(product_id, name, price)

def test_add_product_name_empty_string_raises_value_error():
    service = InventoryService()
    product_id = "p125"
    name = ""
    price = 5.0

    with patch.object(name, 'strip', return_value=""):
        with patch.object(service, '_products', new_callable=dict):
            with pytest.raises(ValueError, match="Product name cannot be empty"):
                service.add_product(product_id, name, price)

def test_add_product_name_whitespace_only_raises_value_error():
    service = InventoryService()
    product_id = "p126"
    name = "   "
    price = 5.0

    with patch.object(name, 'strip', return_value=""):
        with patch.object(service, '_products', new_callable=dict):
            with pytest.raises(ValueError, match="Product name cannot be empty"):
                service.add_product(product_id, name, price)

def test_add_product_name_strip_called_and_product_added():
    service = InventoryService()
    product_id = "p127"
    name = "  Valid Name  "
    price = 20.0

    mock_name = MagicMock()
    mock_name.strip.return_value = "Valid Name"

    with patch.object(service, '_products', new_callable=dict) as mock_products:
        result = service.add_product(product_id, mock_name, price)
        mock_name.strip.assert_called_once()
        assert isinstance(result, Product)
        assert result.name == mock_name.strip.return_value
        assert product_id in mock_products
        assert mock_products[product_id] == result

def test_add_product_price_zero_is_valid():
    service = InventoryService()
    product_id = "p128"
    name = "Free Product"
    price = 0.0

    with patch.object(name, 'strip', return_value=name):
        with patch.object(service, '_products', new_callable=dict) as mock_products:
            result = service.add_product(product_id, name, price)
            assert isinstance(result, Product)
            assert result.price == 0.0
            assert product_id in mock_products
            assert mock_products[product_id] == result

def test_add_product_name_none_raises_attribute_error_on_strip():
    service = InventoryService()
    product_id = "p129"
    name = None
    price = 10.0

    with patch.object(service, '_products', new_callable=dict):
        with pytest.raises(AttributeError):
            service.add_product(product_id, name, price)
# AI_TEST_AGENT_END function=InventoryService.add_product

# AI_TEST_AGENT_START function=InventoryService.get_product
class DummyProduct:
    def __init__(self, id):
        self.id = id

def test_get_product_returns_product_when_exists():
    service = InventoryService()
    dummy_product = DummyProduct('123')
    with patch.object(service, '_products', {'123': dummy_product}):
        result = service.get_product('123')
    assert result is dummy_product

def test_get_product_raises_ProductNotFoundError_when_product_missing():
    service = InventoryService()
    with patch.object(service, '_products', {}):
        with pytest.raises(ProductNotFoundError, match="'abc' not found"):
            service.get_product('abc')

def test_get_product_raises_ProductNotFoundError_with_empty_string_id():
    service = InventoryService()
    with patch.object(service, '_products', {}):
        with pytest.raises(ProductNotFoundError, match="'' not found"):
            service.get_product('')

def test_get_product_raises_ProductNotFoundError_with_none_id():
    service = InventoryService()
    with patch.object(service, '_products', {}):
        with pytest.raises(ProductNotFoundError, match="'None' not found"):
            service.get_product(None)

def test_get_product_raises_ProductNotFoundError_with_numeric_string_id():
    service = InventoryService()
    with patch.object(service, '_products', {}):
        with pytest.raises(ProductNotFoundError, match="'0' not found"):
            service.get_product('0')

def test_get_product_returns_correct_product_among_multiple():
    service = InventoryService()
    product_a = DummyProduct('a')
    product_b = DummyProduct('b')
    product_c = DummyProduct('c')
    with patch.object(service, '_products', {'a': product_a, 'b': product_b, 'c': product_c}):
        result = service.get_product('b')
    assert result is product_b

def test_get_product_raises_ProductNotFoundError_with_whitespace_id():
    service = InventoryService()
    with patch.object(service, '_products', {}):
        with pytest.raises(ProductNotFoundError, match="' ' not found"):
            service.get_product(' ')

def test_get_product_raises_ProductNotFoundError_with_special_characters_id():
    service = InventoryService()
    with patch.object(service, '_products', {}):
        with pytest.raises(ProductNotFoundError, match="'!@#$' not found"):
            service.get_product('!@#$')
# AI_TEST_AGENT_END function=InventoryService.get_product

# AI_TEST_AGENT_START function=InventoryService.update_stock
def test_update_stock_valid_quantity_updates_stock():
    service = InventoryService()
    product_mock = MagicMock()
    product_mock.stock = 10
    service.get_product = MagicMock(return_value=product_mock)

    service.update_stock("prod123", 5)

    service.get_product.assert_called_once_with("prod123")
    assert product_mock.stock == 5

def test_update_stock_zero_quantity_updates_stock_to_zero():
    service = InventoryService()
    product_mock = MagicMock()
    product_mock.stock = 10
    service.get_product = MagicMock(return_value=product_mock)

    service.update_stock("prod123", 0)

    service.get_product.assert_called_once_with("prod123")
    assert product_mock.stock == 0

def test_update_stock_negative_quantity_raises_value_error():
    service = InventoryService()
    product_mock = MagicMock()
    service.get_product = MagicMock(return_value=product_mock)

    with pytest.raises(ValueError, match="Stock quantity cannot be negative"):
        service.update_stock("prod123", -1)

    service.get_product.assert_called_once_with("prod123")

def test_update_stock_product_not_found_raises_product_not_found_error():
    service = InventoryService()
    service.get_product = MagicMock(side_effect=KeyError("Product 'prod123' not found"))

    with pytest.raises(KeyError, match="Product 'prod123' not found"):
        service.update_stock("prod123", 5)

    service.get_product.assert_called_once_with("prod123")

def test_update_stock_quantity_as_large_number_updates_stock():
    service = InventoryService()
    product_mock = MagicMock()
    product_mock.stock = 0
    service.get_product = MagicMock(return_value=product_mock)

    large_quantity = 10**9
    service.update_stock("prod123", large_quantity)

    service.get_product.assert_called_once_with("prod123")
    assert product_mock.stock == large_quantity

def test_update_stock_quantity_as_non_integer_raises_type_error():
    service = InventoryService()
    product_mock = MagicMock()
    service.get_product = MagicMock(return_value=product_mock)

    with pytest.raises(TypeError):
        service.update_stock("prod123", "not_an_int")

    service.get_product.assert_called_once_with("prod123")

def test_update_stock_product_id_empty_string_raises_key_error():
    service = InventoryService()
    service.get_product = MagicMock(side_effect=KeyError("Product '' not found"))

    with pytest.raises(KeyError, match="Product '' not found"):
        service.update_stock("", 5)

    service.get_product.assert_called_once_with("")

def test_update_stock_product_id_none_raises_type_error():
    service = InventoryService()
    with pytest.raises(TypeError):
        service.update_stock(None, 5)

def test_update_stock_quantity_none_raises_type_error():
    service = InventoryService()
    product_mock = MagicMock()
    service.get_product = MagicMock(return_value=product_mock)

    with pytest.raises(TypeError):
        service.update_stock("prod123", None)

    service.get_product.assert_called_once_with("prod123")
# AI_TEST_AGENT_END function=InventoryService.update_stock

# AI_TEST_AGENT_START function=InventoryService.remove_product
class DummyProduct:
    def __init__(self, reserved):
        self.reserved = reserved

def test_remove_product_success_removes_product():
    service = InventoryService()
    product_id = "prod123"
    dummy_product = DummyProduct(reserved=0)

    with patch.object(service, "get_product", return_value=dummy_product) as mock_get_product, \
         patch.object(service, "_products", {product_id: dummy_product}) as mock_products:
        service.remove_product(product_id)
        mock_get_product.assert_called_once_with(product_id)
        assert product_id not in mock_products

def test_remove_product_raises_value_error_if_reserved_greater_than_zero():
    service = InventoryService()
    product_id = "prod456"
    dummy_product = DummyProduct(reserved=5)

    with patch.object(service, "get_product", return_value=dummy_product) as mock_get_product, \
         patch.object(service, "_products", {product_id: dummy_product}):
        with pytest.raises(ValueError, match=f"Cannot remove product '{product_id}' with active reservations"):
            service.remove_product(product_id)
        mock_get_product.assert_called_once_with(product_id)

def test_remove_product_raises_key_error_if_product_not_in_products_dict():
    service = InventoryService()
    product_id = "prod789"
    dummy_product = DummyProduct(reserved=0)

    with patch.object(service, "get_product", return_value=dummy_product) as mock_get_product, \
         patch.object(service, "_products", {}) as mock_products:
        with pytest.raises(KeyError):
            service.remove_product(product_id)
        mock_get_product.assert_called_once_with(product_id)

def test_remove_product_raises_type_error_if_product_id_is_none():
    service = InventoryService()
    product_id = None
    dummy_product = DummyProduct(reserved=0)

    with patch.object(service, "get_product", return_value=dummy_product) as mock_get_product, \
         patch.object(service, "_products", {"None": dummy_product}):
        with pytest.raises(TypeError):
            service.remove_product(product_id)
        mock_get_product.assert_called_once_with(product_id)

def test_remove_product_raises_type_error_if_product_id_is_empty_string():
    service = InventoryService()
    product_id = ""
    dummy_product = DummyProduct(reserved=0)

    with patch.object(service, "get_product", return_value=dummy_product) as mock_get_product, \
         patch.object(service, "_products", {product_id: dummy_product}):
        with pytest.raises(KeyError):
            service.remove_product(product_id)
        mock_get_product.assert_called_once_with(product_id)

def test_remove_product_raises_value_error_with_reserved_boundary_one():
    service = InventoryService()
    product_id = "prod_boundary"
    dummy_product = DummyProduct(reserved=1)

    with patch.object(service, "get_product", return_value=dummy_product) as mock_get_product, \
         patch.object(service, "_products", {product_id: dummy_product}):
        with pytest.raises(ValueError, match=f"Cannot remove product '{product_id}' with active reservations"):
            service.remove_product(product_id)
        mock_get_product.assert_called_once_with(product_id)

def test_remove_product_removes_product_when_reserved_is_zero_boundary():
    service = InventoryService()
    product_id = "prod_zero"
    dummy_product = DummyProduct(reserved=0)

    with patch.object(service, "get_product", return_value=dummy_product) as mock_get_product, \
         patch.object(service, "_products", {product_id: dummy_product}) as mock_products:
        service.remove_product(product_id)
        mock_get_product.assert_called_once_with(product_id)
        assert product_id not in mock_products

def test_remove_product_raises_value_error_when_reserved_negative():
    service = InventoryService()
    product_id = "prod_negative"
    dummy_product = DummyProduct(reserved=-1)

    with patch.object(service, "get_product", return_value=dummy_product) as mock_get_product, \
         patch.object(service, "_products", {product_id: dummy_product}):
        with pytest.raises(ValueError, match=f"Cannot remove product '{product_id}' with active reservations"):
            service.remove_product(product_id)
        mock_get_product.assert_called_once_with(product_id)
# AI_TEST_AGENT_END function=InventoryService.remove_product

# AI_TEST_AGENT_START function=InventoryService.list_low_stock
def test_list_low_stock_all_below_threshold_included():
    service = InventoryService()
    product1 = MagicMock()
    product2 = MagicMock()
    product1.available_stock.return_value = 2
    product2.available_stock.return_value = 4
    service._products = {'p1': product1, 'p2': product2}
    result = service.list_low_stock(threshold=5)
    assert product1 in result
    assert product2 in result
    assert len(result) == 2
    product1.available_stock.assert_called()
    product2.available_stock.assert_called()

def test_list_low_stock_some_above_threshold_excluded():
    service = InventoryService()
    product1 = MagicMock()
    product2 = MagicMock()
    product3 = MagicMock()
    product1.available_stock.return_value = 1
    product2.available_stock.return_value = 5
    product3.available_stock.return_value = 10
    service._products = {'p1': product1, 'p2': product2, 'p3': product3}
    result = service.list_low_stock(threshold=5)
    assert product1 in result
    assert product2 not in result
    assert product3 not in result
    assert len(result) == 1

def test_list_low_stock_negative_stock_excluded():
    service = InventoryService()
    product1 = MagicMock()
    product2 = MagicMock()
    product1.available_stock.return_value = -1
    product2.available_stock.return_value = 3
    service._products = {'p1': product1, 'p2': product2}
    result = service.list_low_stock(threshold=5)
    assert product1 not in result
    assert product2 in result
    assert len(result) == 1

def test_list_low_stock_empty_products_returns_empty_list():
    service = InventoryService()
    service._products = {}
    result = service.list_low_stock(threshold=5)
    assert result == []

def test_list_low_stock_threshold_zero_includes_all_non_negative():
    service = InventoryService()
    product1 = MagicMock()
    product2 = MagicMock()
    product3 = MagicMock()
    product1.available_stock.return_value = 0
    product2.available_stock.return_value = 1
    product3.available_stock.return_value = -1
    service._products = {'p1': product1, 'p2': product2, 'p3': product3}
    result = service.list_low_stock(threshold=0)
    assert product1 not in result
    assert product2 not in result
    assert product3 not in result
    assert result == []

def test_list_low_stock_threshold_negative_includes_all_non_negative():
    service = InventoryService()
    product1 = MagicMock()
    product2 = MagicMock()
    product1.available_stock.return_value = 0
    product2.available_stock.return_value = 3
    service._products = {'p1': product1, 'p2': product2}
    result = service.list_low_stock(threshold=-1)
    assert product1 not in result
    assert product2 not in result
    assert result == []

def test_list_low_stock_product_available_stock_raises_propagates():
    service = InventoryService()
    product1 = MagicMock()
    product1.available_stock.side_effect = RuntimeError("fail")
    service._products = {'p1': product1}
    with pytest.raises(RuntimeError, match="fail"):
        service.list_low_stock(threshold=5)

def test_list_low_stock_threshold_non_integer_raises_typeerror():
    service = InventoryService()
    product1 = MagicMock()
    product1.available_stock.return_value = 1
    service._products = {'p1': product1}
    with pytest.raises(TypeError):
        service.list_low_stock(threshold="five")

def test_list_low_stock_products_values_not_iterable_raises_attributeerror():
    service = InventoryService()
    service._products = None
    with pytest.raises(AttributeError):
        service.list_low_stock(threshold=5)
# AI_TEST_AGENT_END function=InventoryService.list_low_stock
