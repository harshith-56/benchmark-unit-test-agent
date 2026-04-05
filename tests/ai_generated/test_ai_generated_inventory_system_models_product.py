from inventory_system.models.product import Product
import pytest

# AI_TEST_AGENT_START function=Product.__init__
def test_init_with_valid_inputs():
    product = Product(product_id="123", name="Widget", price=19.99)
    assert product.product_id == "123"
    assert product.name == "Widget"
    assert product.price == 19.99
    assert product.stock == 0
    assert product.reserved == 0

def test_init_with_empty_product_id_and_name():
    product = Product(product_id="", name="", price=0.0)
    assert product.product_id == ""
    assert product.name == ""
    assert product.price == 0.0
    assert product.stock == 0
    assert product.reserved == 0

def test_init_with_zero_price():
    product = Product(product_id="001", name="Freebie", price=0.0)
    assert product.product_id == "001"
    assert product.name == "Freebie"
    assert product.price == 0.0
    assert product.stock == 0
    assert product.reserved == 0

def test_init_with_negative_price():
    product = Product(product_id="neg", name="NegativePrice", price=-10.5)
    assert product.product_id == "neg"
    assert product.name == "NegativePrice"
    assert product.price == -10.5
    assert product.stock == 0
    assert product.reserved == 0

def test_init_with_none_product_id():
    with pytest.raises(TypeError):
        Product(product_id=None, name="Name", price=10.0)

def test_init_with_none_name():
    with pytest.raises(TypeError):
        Product(product_id="id", name=None, price=10.0)

def test_init_with_none_price():
    with pytest.raises(TypeError):
        Product(product_id="id", name="Name", price=None)

def test_init_with_non_string_product_id():
    product = Product(product_id=123, name="Name", price=10.0)
    assert product.product_id == 123
    assert product.name == "Name"
    assert product.price == 10.0
    assert product.stock == 0
    assert product.reserved == 0

def test_init_with_non_string_name():
    product = Product(product_id="id", name=456, price=10.0)
    assert product.product_id == "id"
    assert product.name == 456
    assert product.price == 10.0
    assert product.stock == 0
    assert product.reserved == 0
# AI_TEST_AGENT_END function=Product.__init__

# AI_TEST_AGENT_START function=Product.to_dict
def test_to_dict_with_positive_stock_and_reserved():
    product = Product(product_id=1, name="Widget", price=9.99, stock=100, reserved=20)
    expected_available = product.stock - product.reserved
    result = product.to_dict()
    assert result["product_id"] == 1
    assert result["name"] == "Widget"
    assert result["price"] == 9.99
    assert result["stock"] == 100
    assert result["reserved"] == 20
    assert result["available"] == expected_available

def test_to_dict_with_zero_stock_and_zero_reserved():
    product = Product(product_id=2, name="Gadget", price=0.0, stock=0, reserved=0)
    expected_available = 0
    result = product.to_dict()
    assert result["product_id"] == 2
    assert result["name"] == "Gadget"
    assert result["price"] == 0.0
    assert result["stock"] == 0
    assert result["reserved"] == 0
    assert result["available"] == expected_available

def test_to_dict_with_reserved_greater_than_stock():
    product = Product(product_id=3, name="Thingamajig", price=15.5, stock=10, reserved=15)
    expected_available = product.stock - product.reserved  # negative value
    result = product.to_dict()
    assert result["product_id"] == 3
    assert result["name"] == "Thingamajig"
    assert result["price"] == 15.5
    assert result["stock"] == 10
    assert result["reserved"] == 15
    assert result["available"] == expected_available
    assert result["available"] < 0

def test_to_dict_with_negative_price_and_stock():
    product = Product(product_id=4, name="Faulty", price=-5.0, stock=-10, reserved=0)
    expected_available = product.stock - product.reserved
    result = product.to_dict()
    assert result["product_id"] == 4
    assert result["name"] == "Faulty"
    assert result["price"] == -5.0
    assert result["stock"] == -10
    assert result["reserved"] == 0
    assert result["available"] == expected_available

def test_to_dict_with_none_name_and_zero_reserved():
    product = Product(product_id=5, name=None, price=20.0, stock=50, reserved=0)
    expected_available = product.stock - product.reserved
    result = product.to_dict()
    assert result["product_id"] == 5
    assert result["name"] is None
    assert result["price"] == 20.0
    assert result["stock"] == 50
    assert result["reserved"] == 0
    assert result["available"] == expected_available

def test_to_dict_with_reserved_equal_to_stock():
    product = Product(product_id=6, name="Exact", price=30.0, stock=25, reserved=25)
    expected_available = 0
    result = product.to_dict()
    assert result["product_id"] == 6
    assert result["name"] == "Exact"
    assert result["price"] == 30.0
    assert result["stock"] == 25
    assert result["reserved"] == 25
    assert result["available"] == expected_available

def test_to_dict_with_non_integer_stock_and_reserved():
    product = Product(product_id=7, name="FloatStock", price=12.5, stock=10.5, reserved=2.5)
    expected_available = product.stock - product.reserved
    result = product.to_dict()
    assert result["product_id"] == 7
    assert result["name"] == "FloatStock"
    assert result["price"] == 12.5
    assert result["stock"] == 10.5
    assert result["reserved"] == 2.5
    assert result["available"] == expected_available

def test_to_dict_with_string_price_and_stock_should_fail():
    product = Product(product_id=8, name="StringPrice", price="free", stock="many", reserved=0)
    with pytest.raises(TypeError):
        _ = product.to_dict()

def test_to_dict_with_missing_product_id_should_fail():
    with pytest.raises(TypeError):
        Product(name="NoID", price=10.0, stock=5, reserved=1).to_dict()
# AI_TEST_AGENT_END function=Product.to_dict

# AI_TEST_AGENT_START function=Product.__repr__
def test_repr_with_typical_values():
    product = Product(product_id=1, name="Widget", price=19.99, stock=100, reserved=10)
    expected = "Product(id=1, name='Widget', price=19.99, stock=100, reserved=10)"
    assert repr(product) == expected

def test_repr_with_empty_string_name():
    product = Product(product_id=2, name="", price=0.0, stock=0, reserved=0)
    expected = "Product(id=2, name='', price=0.0, stock=0, reserved=0)"
    assert repr(product) == expected

def test_repr_with_none_name_and_zero_values():
    product = Product(product_id=3, name=None, price=0, stock=0, reserved=0)
    expected = "Product(id=3, name=None, price=0, stock=0, reserved=0)"
    assert repr(product) == expected

def test_repr_with_negative_numbers():
    product = Product(product_id=-1, name="Negative", price=-10.5, stock=-5, reserved=-2)
    expected = "Product(id=-1, name='Negative', price=-10.5, stock=-5, reserved=-2)"
    assert repr(product) == expected

def test_repr_with_large_numbers():
    product = Product(product_id=999999999999, name="Big", price=1e10, stock=1_000_000, reserved=500_000)
    expected = "Product(id=999999999999, name='Big', price=10000000000.0, stock=1000000, reserved=500000)"
    assert repr(product) == expected

def test_repr_with_non_string_name_type():
    product = Product(product_id=4, name=12345, price=10, stock=1, reserved=0)
    expected = "Product(id=4, name=12345, price=10, stock=1, reserved=0)"
    assert repr(product) == expected

def test_repr_with_float_product_id_and_reserved():
    product = Product(product_id=5.5, name="FloatID", price=20, stock=10, reserved=2.2)
    expected = "Product(id=5.5, name='FloatID', price=20, stock=10, reserved=2.2)"
    assert repr(product) == expected

def test_repr_with_boolean_values_for_stock_and_reserved():
    product = Product(product_id=6, name="BoolStock", price=15, stock=True, reserved=False)
    expected = "Product(id=6, name='BoolStock', price=15, stock=True, reserved=False)"
    assert repr(product) == expected

def test_repr_with_all_none_values():
    product = Product(product_id=None, name=None, price=None, stock=None, reserved=None)
    expected = "Product(id=None, name=None, price=None, stock=None, reserved=None)"
    assert repr(product) == expected
# AI_TEST_AGENT_END function=Product.__repr__
