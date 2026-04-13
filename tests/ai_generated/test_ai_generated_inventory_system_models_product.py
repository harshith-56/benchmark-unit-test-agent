from inventory_system.models.product import Product
import pytest

# AI_TEST_AGENT_START function=Product.__init__
def test_product_init_with_valid_values():
    product = Product(product_id="p1", name="Test Product", price=10.5)
    assert product.product_id == "p1"
    assert product.name == "Test Product"
    assert product.price == 10.5
    assert product.stock == 0
    assert product.reserved == 0

def test_product_init_with_empty_strings():
    product = Product(product_id="", name="", price=0.0)
    assert product.product_id == ""
    assert product.name == ""
    assert product.price == 0.0
    assert product.stock == 0
    assert product.reserved == 0

def test_product_init_with_zero_price():
    product = Product(product_id="p2", name="Zero Price", price=0.0)
    assert product.price == 0.0
    assert product.stock == 0
    assert product.reserved == 0

def test_product_init_with_negative_price():
    product = Product(product_id="p3", name="Negative Price", price=-5.0)
    assert product.price == -5.0
    assert product.stock == 0
    assert product.reserved == 0

def test_product_init_with_none_product_id():
    product = Product(product_id=None, name="None ID", price=1.0)
    assert product.product_id is None
    assert product.name == "None ID"
    assert product.price == 1.0
    assert product.stock == 0
    assert product.reserved == 0

def test_product_init_with_none_name():
    product = Product(product_id="p4", name=None, price=1.0)
    assert product.product_id == "p4"
    assert product.name is None
    assert product.price == 1.0
    assert product.stock == 0
    assert product.reserved == 0

def test_product_init_with_non_string_product_id():
    product = Product(product_id=123, name="Non-string ID", price=2.0)
    assert product.product_id == 123
    assert product.name == "Non-string ID"
    assert product.price == 2.0
    assert product.stock == 0
    assert product.reserved == 0

def test_product_init_with_non_string_name():
    product = Product(product_id="p5", name=456, price=3.0)
    assert product.product_id == "p5"
    assert product.name == 456
    assert product.price == 3.0
    assert product.stock == 0
    assert product.reserved == 0

def test_product_init_with_non_float_price():
    product = Product(product_id="p6", name="Non-float Price", price="100")
    assert product.product_id == "p6"
    assert product.name == "Non-float Price"
    assert product.price == "100"
    assert product.stock == 0
    assert product.reserved == 0
# AI_TEST_AGENT_END function=Product.__init__

# AI_TEST_AGENT_START function=Product.to_dict
def test_to_dict_with_zero_stock_and_reserved():
    product = Product(product_id="p1", name="Test Product", price=10.0)
    product.stock = 0
    product.reserved = 0
    result = product.to_dict()
    assert result["product_id"] == "p1"
    assert result["name"] == "Test Product"
    assert result["price"] == 10.0
    assert result["stock"] == 0
    assert result["reserved"] == 0
    assert result["available"] == 0

def test_to_dict_with_positive_stock_and_reserved_less_than_stock():
    product = Product(product_id="p2", name="Another Product", price=20.5)
    product.stock = 100
    product.reserved = 30
    result = product.to_dict()
    assert result["stock"] == 100
    assert result["reserved"] == 30
    assert result["available"] == 70

def test_to_dict_with_reserved_equal_to_stock():
    product = Product(product_id="p3", name="Reserved Equals Stock", price=5.0)
    product.stock = 50
    product.reserved = 50
    result = product.to_dict()
    assert result["stock"] == 50
    assert result["reserved"] == 50
    assert result["available"] == 0

def test_to_dict_with_reserved_greater_than_stock():
    product = Product(product_id="p4", name="Reserved Greater Than Stock", price=15.0)
    product.stock = 20
    product.reserved = 25
    result = product.to_dict()
    assert result["stock"] == 20
    assert result["reserved"] == 25
    assert result["available"] == -5

def test_to_dict_with_negative_stock_and_reserved():
    product = Product(product_id="p5", name="Negative Stock and Reserved", price=8.0)
    product.stock = -10
    product.reserved = -5
    result = product.to_dict()
    assert result["stock"] == -10
    assert result["reserved"] == -5
    assert result["available"] == -5

def test_to_dict_with_empty_strings_and_zero_price():
    product = Product(product_id="", name="", price=0.0)
    product.stock = 10
    product.reserved = 2
    result = product.to_dict()
    assert result["product_id"] == ""
    assert result["name"] == ""
    assert result["price"] == 0.0
    assert result["stock"] == 10
    assert result["reserved"] == 2
    assert result["available"] == 8

def test_to_dict_with_float_stock_and_reserved_cast_to_int():
    product = Product(product_id="p6", name="Float Stock Reserved", price=12.0)
    product.stock = 10.7
    product.reserved = 3.2
    result = product.to_dict()
    assert result["stock"] == 10.7
    assert result["reserved"] == 3.2
    assert result["available"] == pytest.approx(7.5)

def test_to_dict_with_none_values_for_stock_and_reserved():
    product = Product(product_id="p7", name="None Stock Reserved", price=7.0)
    product.stock = None
    product.reserved = None
    with pytest.raises(TypeError):
        _ = product.to_dict()

def test_to_dict_with_non_string_product_id_and_name():
    product = Product(product_id=123, name=456, price=9.99)
    product.stock = 5
    product.reserved = 1
    result = product.to_dict()
    assert result["product_id"] == 123
    assert result["name"] == 456
    assert result["price"] == 9.99
    assert result["stock"] == 5
    assert result["reserved"] == 1
    assert result["available"] == 4
# AI_TEST_AGENT_END function=Product.to_dict

# AI_TEST_AGENT_START function=Product.__repr__
def test_repr_with_normal_values():
    product = Product(product_id="p1", name="Widget", price=19.99)
    product.stock = 100
    product.reserved = 20
    result = repr(product)
    expected = "Product(id='p1', name='Widget', price=19.99, stock=100, reserved=20)"
    assert result == expected

def test_repr_with_empty_strings_and_zero_price():
    product = Product(product_id="", name="", price=0.0)
    product.stock = 0
    product.reserved = 0
    result = repr(product)
    expected = "Product(id='', name='', price=0.0, stock=0, reserved=0)"
    assert result == expected

def test_repr_with_negative_stock_and_reserved():
    product = Product(product_id="neg", name="NegativeStock", price=10.0)
    product.stock = -5
    product.reserved = -3
    result = repr(product)
    expected = "Product(id='neg', name='NegativeStock', price=10.0, stock=-5, reserved=-3)"
    assert result == expected

def test_repr_with_reserved_greater_than_stock():
    product = Product(product_id="over", name="OverReserved", price=5.5)
    product.stock = 10
    product.reserved = 15
    result = repr(product)
    expected = "Product(id='over', name='OverReserved', price=5.5, stock=10, reserved=15)"
    assert result == expected

def test_repr_with_none_as_strings_and_zero_price():
    product = Product(product_id=None, name=None, price=0.0)
    product.stock = 0
    product.reserved = 0
    result = repr(product)
    expected = "Product(id=None, name=None, price=0.0, stock=0, reserved=0)"
    assert result == expected

def test_repr_with_float_price_precision():
    product = Product(product_id="fp", name="FloatPrice", price=19.9999999)
    product.stock = 1
    product.reserved = 0
    result = repr(product)
    expected = "Product(id='fp', name='FloatPrice', price=19.9999999, stock=1, reserved=0)"
    assert result == expected

def test_repr_with_zero_stock_and_reserved():
    product = Product(product_id="zero", name="ZeroStock", price=1.0)
    product.stock = 0
    product.reserved = 0
    result = repr(product)
    expected = "Product(id='zero', name='ZeroStock', price=1.0, stock=0, reserved=0)"
    assert result == expected

def test_repr_with_large_stock_and_reserved():
    product = Product(product_id="large", name="LargeStock", price=1000.0)
    product.stock = 10**6
    product.reserved = 10**5
    result = repr(product)
    expected = f"Product(id='large', name='LargeStock', price=1000.0, stock={10**6}, reserved={10**5})"
    assert result == expected

def test_repr_with_non_string_product_id_and_name():
    product = Product(product_id=123, name=456, price=9.99)
    product.stock = 10
    product.reserved = 5
    result = repr(product)
    expected = "Product(id=123, name=456, price=9.99, stock=10, reserved=5)"
    assert result == expected
# AI_TEST_AGENT_END function=Product.__repr__
