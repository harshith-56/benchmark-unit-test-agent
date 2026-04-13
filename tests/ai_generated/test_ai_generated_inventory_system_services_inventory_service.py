from inventory_system.services.inventory_service import InventoryService
from inventory_system.services.inventory_service import InventoryService, ProductNotFoundError
from inventory_system.services.inventory_service import Product
from inventory_system.services.inventory_service import ProductNotFoundError
from unittest.mock import MagicMock
from unittest.mock import MagicMock, patch
import pytest

# AI_TEST_AGENT_START function=InventoryService.add_product
def test_add_product_valid():
    service = InventoryService()
    product = service.add_product("p1", "Product 1", 10.0)
    assert isinstance(product, Product)
    assert product.product_id == "p1"
    assert product.name == "Product 1"
    assert product.price == 10.0
    assert service._products["p1"] is product

def test_add_product_negative_price_raises_value_error():
    service = InventoryService()
    with pytest.raises(ValueError) as excinfo:
        service.add_product("p2", "Product 2", -1.0)
    assert str(excinfo.value) == "Price cannot be negative"

def test_add_product_empty_name_raises_value_error():
    service = InventoryService()
    with pytest.raises(ValueError) as excinfo:
        service.add_product("p3", "   ", 5.0)
    assert str(excinfo.value) == "Product name cannot be empty"

def test_add_product_name_with_only_spaces_raises_value_error():
    service = InventoryService()
    with pytest.raises(ValueError) as excinfo:
        service.add_product("p4", "", 5.0)
    assert str(excinfo.value) == "Product name cannot be empty"

def test_add_product_name_with_leading_and_trailing_spaces():
    service = InventoryService()
    product = service.add_product("p5", "  Valid Name  ", 15.0)
    assert product.name == "  Valid Name  "
    assert service._products["p5"] is product

def test_add_product_zero_price_is_allowed():
    service = InventoryService()
    product = service.add_product("p6", "Free Product", 0.0)
    assert product.price == 0.0
    assert service._products["p6"] is product

def test_add_product_duplicate_product_id_overwrites():
    service = InventoryService()
    product1 = service.add_product("p7", "Product 7", 10.0)
    product2 = service.add_product("p7", "Product 7 New", 20.0)
    assert product2 is not product1
    assert service._products["p7"] is product2
    assert product2.name == "Product 7 New"
    assert product2.price == 20.0

def test_add_product_name_is_not_str_but_has_strip_method():
    class NameLike:
        def __init__(self, s):
            self.s = s
        def strip(self):
            return self.s.strip()
        def __str__(self):
            return self.s

    service = InventoryService()
    name_obj = NameLike("  ValidName  ")
    product = service.add_product("p8", name_obj, 12.0)
    assert product.name == name_obj
    assert service._products["p8"] is product

def test_add_product_name_is_none_raises_attribute_error():
    service = InventoryService()
    with pytest.raises(AttributeError):
        service.add_product("p9", None, 10.0)
# AI_TEST_AGENT_END function=InventoryService.add_product

# AI_TEST_AGENT_START function=InventoryService.get_product
def test_get_product_returns_product_when_exists():
    service = InventoryService()
    product_mock = MagicMock()
    with patch.object(service, '_products', {'p1': product_mock}):
        result = service.get_product('p1')
    assert result is product_mock

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
    product1 = MagicMock()
    product2 = MagicMock()
    with patch.object(service, '_products', {'p1': product1, 'p2': product2}):
        result = service.get_product('p2')
    assert result is product2

def test_get_product_with_numeric_string_id():
    service = InventoryService()
    product_mock = MagicMock()
    with patch.object(service, '_products', {'123': product_mock}):
        result = service.get_product('123')
    assert result is product_mock

def test_get_product_with_whitespace_id_raises_ProductNotFoundError():
    service = InventoryService()
    with patch.object(service, '_products', {}):
        with pytest.raises(ProductNotFoundError) as excinfo:
            service.get_product('   ')
    assert "Product '   ' not found" in str(excinfo.value)
# AI_TEST_AGENT_END function=InventoryService.get_product

# AI_TEST_AGENT_START function=InventoryService.update_stock
class DummyProduct:
    def __init__(self):
        self.stock = None

def test_update_stock_valid_quantity_updates_stock():
    service = InventoryService()
    dummy_product = DummyProduct()
    dummy_product.stock = 0
    with patch.object(service, 'get_product', return_value=dummy_product) as mock_get_product:
        service.update_stock('prod1', 10)
        mock_get_product.assert_called_once_with('prod1')
        assert dummy_product.stock == 10

def test_update_stock_negative_quantity_raises_value_error():
    service = InventoryService()
    dummy_product = DummyProduct()
    with patch.object(service, 'get_product', return_value=dummy_product):
        with pytest.raises(ValueError) as excinfo:
            service.update_stock('prod1', -1)
        assert str(excinfo.value) == "Stock quantity cannot be negative"

def test_update_stock_product_not_found_raises_product_not_found_error():
    service = InventoryService()
    with patch.object(service, 'get_product', side_effect=ProductNotFoundError("Product 'prod1' not found")):
        with pytest.raises(ProductNotFoundError) as excinfo:
            service.update_stock('prod1', 5)
        assert str(excinfo.value) == "Product 'prod1' not found"

def test_update_stock_zero_quantity_sets_stock_to_zero():
    service = InventoryService()
    dummy_product = DummyProduct()
    dummy_product.stock = 5
    with patch.object(service, 'get_product', return_value=dummy_product):
        service.update_stock('prod1', 0)
        assert dummy_product.stock == 0

def test_update_stock_large_quantity_updates_stock_correctly():
    service = InventoryService()
    dummy_product = DummyProduct()
    dummy_product.stock = 1
    large_quantity = 10**6
    with patch.object(service, 'get_product', return_value=dummy_product):
        service.update_stock('prod1', large_quantity)
        assert dummy_product.stock == large_quantity

def test_update_stock_non_integer_quantity_type_raises_type_error():
    service = InventoryService()
    dummy_product = DummyProduct()
    with patch.object(service, 'get_product', return_value=dummy_product):
        with pytest.raises(TypeError):
            service.update_stock('prod1', 'not-an-int')

def test_update_stock_none_quantity_raises_type_error():
    service = InventoryService()
    dummy_product = DummyProduct()
    with patch.object(service, 'get_product', return_value=dummy_product):
        with pytest.raises(TypeError):
            service.update_stock('prod1', None)
# AI_TEST_AGENT_END function=InventoryService.update_stock

# AI_TEST_AGENT_START function=InventoryService.remove_product
def test_remove_product_success_removes_product():
    service = InventoryService()
    product_mock = MagicMock()
    product_mock.reserved = 0
    with patch.object(service, 'get_product', return_value=product_mock) as get_product_mock:
        service._products = {'p1': product_mock}
        service.remove_product('p1')
        assert 'p1' not in service._products
        get_product_mock.assert_called_once_with('p1')

def test_remove_product_raises_value_error_when_reserved_gt_zero():
    service = InventoryService()
    product_mock = MagicMock()
    product_mock.reserved = 3
    with patch.object(service, 'get_product', return_value=product_mock):
        service._products = {'p1': product_mock}
        with pytest.raises(ValueError) as excinfo:
            service.remove_product('p1')
        assert "Cannot remove product 'p1' with active reservations" in str(excinfo.value)

def test_remove_product_raises_product_not_found_error_when_product_missing():
    service = InventoryService()
    service._products = {}
    with pytest.raises(ProductNotFoundError) as excinfo:
        service.remove_product('missing_id')
    assert "Product 'missing_id' not found" in str(excinfo.value)

def test_remove_product_removes_only_specified_product():
    service = InventoryService()
    product1 = MagicMock()
    product1.reserved = 0
    product2 = MagicMock()
    product2.reserved = 0
    service._products = {'p1': product1, 'p2': product2}
    with patch.object(service, 'get_product', side_effect=lambda pid: service._products[pid]):
        service.remove_product('p1')
        assert 'p1' not in service._products
        assert 'p2' in service._products

def test_remove_product_with_reserved_zero_removes_product():
    service = InventoryService()
    product_mock = MagicMock()
    product_mock.reserved = 0
    service._products = {'p1': product_mock}
    with patch.object(service, 'get_product', return_value=product_mock):
        service.remove_product('p1')
        assert 'p1' not in service._products

def test_remove_product_with_reserved_none_raises_attribute_error():
    service = InventoryService()
    product_mock = MagicMock()
    del product_mock.reserved
    service._products = {'p1': product_mock}
    with patch.object(service, 'get_product', return_value=product_mock):
        with pytest.raises(AttributeError):
            service.remove_product('p1')

def test_remove_product_with_reserved_negative_removes_product():
    service = InventoryService()
    product_mock = MagicMock()
    product_mock.reserved = -1
    service._products = {'p1': product_mock}
    with patch.object(service, 'get_product', return_value=product_mock):
        service.remove_product('p1')
        assert 'p1' not in service._products
# AI_TEST_AGENT_END function=InventoryService.remove_product

# AI_TEST_AGENT_START function=InventoryService.list_low_stock
class DummyProduct:
    def __init__(self, available_stock_value):
        self._available_stock_value = available_stock_value

    def available_stock(self):
        return self._available_stock_value


def test_list_low_stock_empty_products(monkeypatch):
    service = InventoryService()
    monkeypatch.setattr(service, "_products", {})
    result = service.list_low_stock()
    assert result == []


def test_list_low_stock_with_products_below_threshold(monkeypatch):
    service = InventoryService()
    product1 = DummyProduct(3)
    product2 = DummyProduct(4)
    product3 = DummyProduct(10)
    products = {"p1": product1, "p2": product2, "p3": product3}
    monkeypatch.setattr(service, "_products", products)
    result = service.list_low_stock(threshold=5)
    assert product1 in result
    assert product2 in result
    assert product3 not in result
    assert len(result) == 2


def test_list_low_stock_with_products_at_threshold(monkeypatch):
    service = InventoryService()
    product1 = DummyProduct(5)
    product2 = DummyProduct(6)
    products = {"p1": product1, "p2": product2}
    monkeypatch.setattr(service, "_products", products)
    result = service.list_low_stock(threshold=5)
    assert product1 not in result
    assert product2 not in result
    assert result == []


def test_list_low_stock_with_negative_available_stock(monkeypatch):
    service = InventoryService()
    product1 = DummyProduct(-1)
    product2 = DummyProduct(2)
    products = {"p1": product1, "p2": product2}
    monkeypatch.setattr(service, "_products", products)
    result = service.list_low_stock(threshold=5)
    assert product1 not in result
    assert product2 in result
    assert len(result) == 1


def test_list_low_stock_with_zero_threshold(monkeypatch):
    service = InventoryService()
    product1 = DummyProduct(0)
    product2 = DummyProduct(1)
    products = {"p1": product1, "p2": product2}
    monkeypatch.setattr(service, "_products", products)
    result = service.list_low_stock(threshold=0)
    assert result == []


def test_list_low_stock_with_threshold_negative(monkeypatch):
    service = InventoryService()
    product1 = DummyProduct(0)
    product2 = DummyProduct(-1)
    products = {"p1": product1, "p2": product2}
    monkeypatch.setattr(service, "_products", products)
    result = service.list_low_stock(threshold=-1)
    assert result == []


def test_list_low_stock_with_non_integer_threshold(monkeypatch):
    service = InventoryService()
    product1 = DummyProduct(2)
    products = {"p1": product1}
    monkeypatch.setattr(service, "_products", products)
    with pytest.raises(TypeError):
        service.list_low_stock(threshold="5")


def test_list_low_stock_with_large_threshold(monkeypatch):
    service = InventoryService()
    product1 = DummyProduct(100)
    product2 = DummyProduct(50)
    products = {"p1": product1, "p2": product2}
    monkeypatch.setattr(service, "_products", products)
    result = service.list_low_stock(threshold=200)
    assert product1 in result
    assert product2 in result
    assert len(result) == 2


def test_list_low_stock_with_all_products_above_threshold(monkeypatch):
    service = InventoryService()
    product1 = DummyProduct(10)
    product2 = DummyProduct(20)
    products = {"p1": product1, "p2": product2}
    monkeypatch.setattr(service, "_products", products)
    result = service.list_low_stock(threshold=5)
    assert result == []
# AI_TEST_AGENT_END function=InventoryService.list_low_stock
