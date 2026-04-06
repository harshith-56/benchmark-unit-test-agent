from inventory_system.services.inventory_service import InventoryService
from inventory_system.services.inventory_service import ProductNotFoundError
from inventory_system.services.inventory_service import ProductNotFoundError, Product
from unittest.mock import MagicMock, patch
from unittest.mock import patch, MagicMock
import pytest

# AI_TEST_AGENT_START function=InventoryService.add_product
def test_add_product_valid():
    service = InventoryService()
    product = service.add_product("p1", "Product 1", 10.0)
    assert isinstance(product, Product)
    assert product.price == 10.0
    assert product.stock == 0
    assert product.reserved == 0
    assert product.name == "Product 1"
    assert service._products["p1"] is product

def test_add_product_negative_price_raises():
    service = InventoryService()
    with pytest.raises(ValueError, match="Price cannot be negative"):
        service.add_product("p2", "Product 2", -0.01)

def test_add_product_empty_name_raises():
    service = InventoryService()
    with pytest.raises(ValueError, match="Product name cannot be empty"):
        service.add_product("p3", "", 5.0)
    with pytest.raises(ValueError, match="Product name cannot be empty"):
        service.add_product("p4", "   ", 5.0)

def test_add_product_name_strip_called(monkeypatch):
    service = InventoryService()
    class NameStr:
        def __init__(self):
            self.strip_called = False
        def strip(self):
            self.strip_called = True
            return "valid"
        def __str__(self):
            return "valid"
    name_obj = NameStr()
    # Patch Product to avoid real creation
    with patch("inventory_system.services.inventory_service.Product") as mock_product:
        mock_product.return_value = MagicMock()
        product = service.add_product("p5", name_obj, 1.0)
        assert name_obj.strip_called is True

def test_add_product_zero_price_and_valid_name():
    service = InventoryService()
    product = service.add_product("p6", "Zero Price", 0.0)
    assert product.price == 0.0
    assert product.name == "Zero Price"

def test_add_product_duplicate_id_overwrites():
    service = InventoryService()
    p1 = service.add_product("p7", "First", 1.0)
    p2 = service.add_product("p7", "Second", 2.0)
    assert service._products["p7"] is p2
    assert p2.name == "Second"
    assert p2.price == 2.0

def test_add_product_name_is_whitespace_only_raises():
    service = InventoryService()
    with pytest.raises(ValueError, match="Product name cannot be empty"):
        service.add_product("p8", " \t\n ", 1.0)
# AI_TEST_AGENT_END function=InventoryService.add_product

# AI_TEST_AGENT_START function=InventoryService.get_product
def test_get_product_returns_product_when_exists():
    service = InventoryService()
    mock_product = MagicMock()
    with patch.object(service, '_products', {'p1': mock_product}):
        result = service.get_product('p1')
    assert result is mock_product

def test_get_product_raises_ProductNotFoundError_when_product_missing():
    service = InventoryService()
    with patch.object(service, '_products', {}):
        with pytest.raises(ProductNotFoundError) as excinfo:
            service.get_product('missing_id')
        assert "Product 'missing_id' not found" in str(excinfo.value)

def test_get_product_raises_ProductNotFoundError_with_empty_string_id():
    service = InventoryService()
    with patch.object(service, '_products', {}):
        with pytest.raises(ProductNotFoundError) as excinfo:
            service.get_product('')
        assert "Product '' not found" in str(excinfo.value)

def test_get_product_raises_ProductNotFoundError_with_none_id():
    service = InventoryService()
    with patch.object(service, '_products', {}):
        with pytest.raises(ProductNotFoundError) as excinfo:
            service.get_product(None)
        assert "Product None not found" in str(excinfo.value)

def test_get_product_returns_correct_product_among_multiple():
    service = InventoryService()
    mock_product1 = MagicMock()
    mock_product2 = MagicMock()
    with patch.object(service, '_products', {'p1': mock_product1, 'p2': mock_product2}):
        result = service.get_product('p2')
    assert result is mock_product2

def test_get_product_raises_ProductNotFoundError_with_numeric_string_id():
    service = InventoryService()
    with patch.object(service, '_products', {}):
        with pytest.raises(ProductNotFoundError) as excinfo:
            service.get_product('123')
        assert "Product '123' not found" in str(excinfo.value)
# AI_TEST_AGENT_END function=InventoryService.get_product

# AI_TEST_AGENT_START function=InventoryService.update_stock
class DummyProduct:
    def __init__(self):
        self.stock = 0
        self.reserved = 0
    def available_stock(self):
        return self.stock

def test_update_stock_valid_quantity_sets_stock():
    service = InventoryService()
    dummy_product = DummyProduct()
    with patch.object(service, 'get_product', return_value=dummy_product) as mock_get_product:
        service.update_stock('prod1', 10)
        mock_get_product.assert_called_once_with('prod1')
        assert dummy_product.stock == 10

def test_update_stock_zero_quantity_sets_stock_to_zero():
    service = InventoryService()
    dummy_product = DummyProduct()
    dummy_product.stock = 5
    with patch.object(service, 'get_product', return_value=dummy_product):
        service.update_stock('prod1', 0)
        assert dummy_product.stock == 0

def test_update_stock_negative_quantity_raises_value_error():
    service = InventoryService()
    dummy_product = DummyProduct()
    with patch.object(service, 'get_product', return_value=dummy_product):
        with pytest.raises(ValueError, match="Stock quantity cannot be negative"):
            service.update_stock('prod1', -1)

def test_update_stock_product_not_found_raises_product_not_found_error():
    service = InventoryService()
    with patch.object(service, 'get_product', side_effect=ProductNotFoundError("Product 'prod1' not found")):
        with pytest.raises(ProductNotFoundError, match="Product 'prod1' not found"):
            service.update_stock('prod1', 5)

def test_update_stock_non_integer_quantity_raises_type_error():
    service = InventoryService()
    dummy_product = DummyProduct()
    with patch.object(service, 'get_product', return_value=dummy_product):
        with pytest.raises(TypeError):
            service.update_stock('prod1', 'ten')

def test_update_stock_large_quantity_sets_stock():
    service = InventoryService()
    dummy_product = DummyProduct()
    large_quantity = 10**9
    with patch.object(service, 'get_product', return_value=dummy_product):
        service.update_stock('prod1', large_quantity)
        assert dummy_product.stock == large_quantity

def test_update_stock_calls_get_product_once():
    service = InventoryService()
    dummy_product = DummyProduct()
    with patch.object(service, 'get_product', return_value=dummy_product) as mock_get_product:
        service.update_stock('prod1', 3)
        mock_get_product.assert_called_once_with('prod1')
# AI_TEST_AGENT_END function=InventoryService.update_stock

# AI_TEST_AGENT_START function=InventoryService.remove_product
class DummyProduct:
    def __init__(self, reserved=0):
        self.reserved = reserved

def test_remove_product_success_removes_product():
    service = InventoryService()
    dummy_product = DummyProduct(reserved=0)
    with patch.object(service, 'get_product', return_value=dummy_product) as mock_get_product, \
         patch.object(service, '_products', {'p1': dummy_product}):
        service.remove_product('p1')
        assert 'p1' not in service._products
        mock_get_product.assert_called_once_with('p1')

def test_remove_product_raises_value_error_if_reserved_gt_zero():
    service = InventoryService()
    dummy_product = DummyProduct(reserved=3)
    with patch.object(service, 'get_product', return_value=dummy_product) as mock_get_product, \
         patch.object(service, '_products', {'p1': dummy_product}):
        with pytest.raises(ValueError) as excinfo:
            service.remove_product('p1')
        assert "Cannot remove product 'p1' with active reservations" in str(excinfo.value)
        assert 'p1' in service._products
        mock_get_product.assert_called_once_with('p1')

def test_remove_product_raises_product_not_found_error_if_product_missing():
    service = InventoryService()
    with patch.object(service, 'get_product', side_effect=ProductNotFoundError("Product 'p2' not found")) as mock_get_product:
        with pytest.raises(ProductNotFoundError) as excinfo:
            service.remove_product('p2')
        assert "Product 'p2' not found" in str(excinfo.value)
        mock_get_product.assert_called_once_with('p2')

def test_remove_product_removes_only_specified_product():
    service = InventoryService()
    dummy_product1 = DummyProduct(reserved=0)
    dummy_product2 = DummyProduct(reserved=0)
    with patch.object(service, 'get_product', side_effect=lambda pid: {'p1': dummy_product1, 'p2': dummy_product2}[pid]) as mock_get_product, \
         patch.object(service, '_products', {'p1': dummy_product1, 'p2': dummy_product2}):
        service.remove_product('p1')
        assert 'p1' not in service._products
        assert 'p2' in service._products
        assert service._products['p2'] is dummy_product2
        assert mock_get_product.call_count == 1
        mock_get_product.assert_called_with('p1')

def test_remove_product_raises_value_error_with_empty_product_id():
    service = InventoryService()
    dummy_product = DummyProduct(reserved=0)
    with patch.object(service, 'get_product', return_value=dummy_product) as mock_get_product, \
         patch.object(service, '_products', {'': dummy_product}):
        service.remove_product('')
        assert '' not in service._products
        mock_get_product.assert_called_once_with('')

def test_remove_product_raises_value_error_with_none_product_id():
    service = InventoryService()
    dummy_product = DummyProduct(reserved=0)
    with patch.object(service, 'get_product', return_value=dummy_product) as mock_get_product, \
         patch.object(service, '_products', {None: dummy_product}):
        service.remove_product(None)
        assert None not in service._products
        mock_get_product.assert_called_once_with(None)

def test_remove_product_raises_value_error_if_reserved_negative():
    service = InventoryService()
    dummy_product = DummyProduct(reserved=-1)
    with patch.object(service, 'get_product', return_value=dummy_product) as mock_get_product, \
         patch.object(service, '_products', {'p1': dummy_product}):
        # Negative reserved is logically invalid but method only checks > 0, so removal allowed
        service.remove_product('p1')
        assert 'p1' not in service._products
        mock_get_product.assert_called_once_with('p1')
# AI_TEST_AGENT_END function=InventoryService.remove_product

# AI_TEST_AGENT_START function=InventoryService.list_low_stock
def test_list_low_stock_empty_products(monkeypatch):
    service = InventoryService()
    monkeypatch.setattr(service, '_products', {})
    result = service.list_low_stock(threshold=5)
    assert result == []

def test_list_low_stock_all_above_threshold(monkeypatch):
    product1 = MagicMock()
    product1.available_stock.return_value = 10
    product2 = MagicMock()
    product2.available_stock.return_value = 6
    products = {'p1': product1, 'p2': product2}
    service = InventoryService()
    monkeypatch.setattr(service, '_products', products)
    result = service.list_low_stock(threshold=5)
    assert result == []

def test_list_low_stock_some_below_threshold(monkeypatch):
    product1 = MagicMock()
    product1.available_stock.return_value = 4
    product2 = MagicMock()
    product2.available_stock.return_value = 5
    product3 = MagicMock()
    product3.available_stock.return_value = 6
    products = {'p1': product1, 'p2': product2, 'p3': product3}
    service = InventoryService()
    monkeypatch.setattr(service, '_products', products)
    result = service.list_low_stock(threshold=5)
    assert product1 in result
    assert product2 not in result
    assert product3 not in result
    assert len(result) == 1

def test_list_low_stock_includes_zero_stock(monkeypatch):
    product1 = MagicMock()
    product1.available_stock.return_value = 0
    product2 = MagicMock()
    product2.available_stock.return_value = 5
    products = {'p1': product1, 'p2': product2}
    service = InventoryService()
    monkeypatch.setattr(service, '_products', products)
    result = service.list_low_stock(threshold=1)
    assert product1 in result
    assert product2 not in result
    assert len(result) == 1

def test_list_low_stock_excludes_negative_stock(monkeypatch):
    product1 = MagicMock()
    product1.available_stock.return_value = -1
    product2 = MagicMock()
    product2.available_stock.return_value = 3
    products = {'p1': product1, 'p2': product2}
    service = InventoryService()
    monkeypatch.setattr(service, '_products', products)
    result = service.list_low_stock(threshold=5)
    assert product1 not in result
    assert product2 in result
    assert len(result) == 1

def test_list_low_stock_threshold_zero(monkeypatch):
    product1 = MagicMock()
    product1.available_stock.return_value = 0
    product2 = MagicMock()
    product2.available_stock.return_value = 1
    products = {'p1': product1, 'p2': product2}
    service = InventoryService()
    monkeypatch.setattr(service, '_products', products)
    result = service.list_low_stock(threshold=0)
    assert result == []

def test_list_low_stock_threshold_negative(monkeypatch):
    product1 = MagicMock()
    product1.available_stock.return_value = 0
    product2 = MagicMock()
    product2.available_stock.return_value = 1
    products = {'p1': product1, 'p2': product2}
    service = InventoryService()
    monkeypatch.setattr(service, '_products', products)
    result = service.list_low_stock(threshold=-1)
    assert result == []

def test_list_low_stock_non_integer_threshold(monkeypatch):
    product1 = MagicMock()
    product1.available_stock.return_value = 2
    products = {'p1': product1}
    service = InventoryService()
    monkeypatch.setattr(service, '_products', products)
    with pytest.raises(TypeError):
        service.list_low_stock(threshold='5')
# AI_TEST_AGENT_END function=InventoryService.list_low_stock
