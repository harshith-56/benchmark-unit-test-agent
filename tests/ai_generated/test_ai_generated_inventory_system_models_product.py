from inventory_system.models.product import Product
import pytest

# AI_TEST_AGENT_START function=Product.__init__
def test_product_init_with_valid_values():
    p = Product(product_id="p1", name="Test Product", price=10.5)
    assert p.product_id == "p1"
    assert p.name == "Test Product"
    assert p.price == 10.5
    assert p.stock == 0
    assert p.reserved == 0

def test_product_init_with_empty_strings():
    p = Product(product_id="", name="", price=0.0)
    assert p.product_id == ""
    assert p.name == ""
    assert p.price == 0.0
    assert p.stock == 0
    assert p.reserved == 0

def test_product_init_with_zero_price():
    p = Product(product_id="p2", name="Zero Price", price=0)
    assert p.price == 0
    assert isinstance(p.price, (int, float))

def test_product_init_with_negative_price():
    p = Product(product_id="p3", name="Negative Price", price=-5.0)
    assert p.price == -5.0

def test_product_init_with_none_product_id():
    with pytest.raises(TypeError):
        Product(product_id=None, name="Name", price=1.0)

def test_product_init_with_none_name():
    with pytest.raises(TypeError):
        Product(product_id="p4", name=None, price=1.0)

def test_product_init_with_non_string_product_id():
    p = Product(product_id=123, name="Name", price=1.0)
    assert p.product_id == 123

def test_product_init_with_non_string_name():
    p = Product(product_id="p5", name=456, price=1.0)
    assert p.name == 456

def test_product_init_with_non_numeric_price():
    with pytest.raises(TypeError):
        Product(product_id="p6", name="Name", price="not a number")
# AI_TEST_AGENT_END function=Product.__init__

# AI_TEST_AGENT_START function=Product.to_dict
def test_to_dict_with_zero_stock_and_reserved():
    p = Product(product_id="p1", name="Test Product", price=10.0)
    p.stock = 0
    p.reserved = 0
    result = p.to_dict()
    assert result["product_id"] == "p1"
    assert result["name"] == "Test Product"
    assert result["price"] == 10.0
    assert result["stock"] == 0
    assert result["reserved"] == 0
    assert result["available"] == 0

def test_to_dict_with_positive_stock_and_reserved_less_than_stock():
    p = Product(product_id="p2", name="Another Product", price=20.5)
    p.stock = 100
    p.reserved = 30
    result = p.to_dict()
    assert result["stock"] == 100
    assert result["reserved"] == 30
    assert result["available"] == 70

def test_to_dict_with_reserved_equal_to_stock():
    p = Product(product_id="p3", name="Reserved Equals Stock", price=5.5)
    p.stock = 50
    p.reserved = 50
    result = p.to_dict()
    assert result["stock"] == 50
    assert result["reserved"] == 50
    assert result["available"] == 0

def test_to_dict_with_reserved_greater_than_stock_negative_available():
    p = Product(product_id="p4", name="Over Reserved", price=15.0)
    p.stock = 20
    p.reserved = 25
    result = p.to_dict()
    assert result["stock"] == 20
    assert result["reserved"] == 25
    assert result["available"] == -5

def test_to_dict_with_negative_stock_and_reserved():
    p = Product(product_id="p5", name="Negative Stock", price=7.5)
    p.stock = -10
    p.reserved = -3
    result = p.to_dict()
    assert result["stock"] == -10
    assert result["reserved"] == -3
    assert result["available"] == -7

def test_to_dict_with_zero_price_and_empty_name():
    p = Product(product_id="p6", name="", price=0.0)
    p.stock = 10
    p.reserved = 2
    result = p.to_dict()
    assert result["product_id"] == "p6"
    assert result["name"] == ""
    assert result["price"] == 0.0
    assert result["stock"] == 10
    assert result["reserved"] == 2
    assert result["available"] == 8

def test_to_dict_with_non_string_product_id_and_name():
    p = Product(product_id=123, name=456, price=12.0)
    p.stock = 5
    p.reserved = 1
    result = p.to_dict()
    assert result["product_id"] == 123
    assert result["name"] == 456
    assert result["price"] == 12.0
    assert result["stock"] == 5
    assert result["reserved"] == 1
    assert result["available"] == 4

def test_to_dict_with_float_stock_and_reserved_cast_to_int_behavior():
    p = Product(product_id="p7", name="Float Stock", price=9.99)
    p.stock = 10.7
    p.reserved = 3.2
    result = p.to_dict()
    assert result["stock"] == 10.7
    assert result["reserved"] == 3.2
    assert result["available"] == pytest.approx(7.5, rel=1e-9)

def test_to_dict_with_none_values_for_stock_and_reserved():
    p = Product(product_id="p8", name="None Values", price=1.0)
    p.stock = None
    p.reserved = None
    with pytest.raises(TypeError):
        _ = p.to_dict()
# AI_TEST_AGENT_END function=Product.to_dict

# AI_TEST_AGENT_START function=Product.__repr__
def test_repr_with_zero_stock_and_reserved():
    p = Product("p1", "Test Product", 10.0)
    p.stock = 0
    p.reserved = 0
    expected = "Product(id='p1', name='Test Product', price=10.0, stock=0, reserved=0)"
    assert repr(p) == expected

def test_repr_with_positive_stock_and_reserved():
    p = Product("p2", "Another Product", 25.5)
    p.stock = 100
    p.reserved = 20
    expected = "Product(id='p2', name='Another Product', price=25.5, stock=100, reserved=20)"
    assert repr(p) == expected

def test_repr_with_reserved_greater_than_stock():
    p = Product("p3", "Edge Case Product", 5.0)
    p.stock = 10
    p.reserved = 15
    expected = "Product(id='p3', name='Edge Case Product', price=5.0, stock=10, reserved=15)"
    assert repr(p) == expected

def test_repr_with_negative_stock_and_reserved():
    p = Product("p4", "Negative Stock Product", 7.5)
    p.stock = -5
    p.reserved = -3
    expected = "Product(id='p4', name='Negative Stock Product', price=7.5, stock=-5, reserved=-3)"
    assert repr(p) == expected

def test_repr_with_empty_string_fields():
    p = Product("", "", 0.0)
    p.stock = 0
    p.reserved = 0
    expected = "Product(id='', name='', price=0.0, stock=0, reserved=0)"
    assert repr(p) == expected

def test_repr_with_none_as_price_raises_type_error():
    with pytest.raises(TypeError):
        Product("p5", "None Price Product", None)

def test_repr_with_non_string_product_id_and_name():
    p = Product(123, 456, 12.0)
    p.stock = 5
    p.reserved = 2
    expected = "Product(id=123, name=456, price=12.0, stock=5, reserved=2)"
    assert repr(p) == expected

def test_repr_with_float_stock_and_reserved_cast_to_int_behavior():
    p = Product("p6", "Float Stock Product", 9.99)
    p.stock = 10.5
    p.reserved = 3.2
    expected = "Product(id='p6', name='Float Stock Product', price=9.99, stock=10.5, reserved=3.2)"
    assert repr(p) == expected

def test_repr_with_large_values():
    p = Product("p7", "Large Values Product", 9999999.99)
    p.stock = 10**9
    p.reserved = 10**8
    expected = f"Product(id='p7', name='Large Values Product', price=9999999.99, stock={10**9}, reserved={10**8})"
    assert repr(p) == expected
# AI_TEST_AGENT_END function=Product.__repr__
