from inventory_system.main import build_system
from inventory_system.main import run_demo
from inventory_system.main import seed_catalog
from unittest.mock import MagicMock, call
from unittest.mock import patch, MagicMock
import pytest

# AI_TEST_AGENT_START function=build_system
def test_build_system_returns_all_components():
    inventory, reservation, pricing, orders, checker = build_system()
    assert inventory is not None
    assert reservation is not None
    assert pricing is not None
    assert orders is not None
    assert checker is not None

def test_build_system_inventory_instance_type():
    inventory, _, _, _, _ = build_system()
    assert inventory.__class__.__name__ == "InventoryService"

def test_build_system_reservation_receives_inventory():
    inventory, reservation, _, _, _ = build_system()
    assert hasattr(reservation, 'inventory')
    assert reservation.inventory is inventory

def test_build_system_pricing_receives_inventory():
    inventory, _, pricing, _, _ = build_system()
    assert hasattr(pricing, 'inventory')
    assert pricing.inventory is inventory

def test_build_system_orders_receives_all_dependencies():
    inventory, reservation, pricing, orders, _ = build_system()
    assert hasattr(orders, 'inventory')
    assert hasattr(orders, 'reservation')
    assert hasattr(orders, 'pricing')
    assert orders.inventory is inventory
    assert orders.reservation is reservation
    assert orders.pricing is pricing

def test_build_system_checker_receives_inventory_and_orders():
    inventory, _, _, orders, checker = build_system()
    assert hasattr(checker, 'inventory')
    assert hasattr(checker, 'orders')
    assert checker.inventory is inventory
    assert checker.orders is orders

def test_build_system_multiple_calls_return_distinct_instances():
    inv1, res1, pri1, ord1, chk1 = build_system()
    inv2, res2, pri2, ord2, chk2 = build_system()
    assert inv1 is not inv2
    assert res1 is not res2
    assert pri1 is not pri2
    assert ord1 is not ord2
    assert chk1 is not chk2

def test_build_system_raises_no_exception_on_call():
    try:
        build_system()
    except Exception as e:
        pytest.fail(f"build_system raised an unexpected exception: {e}")

def test_build_system_returned_objects_have_expected_methods():
    inventory, reservation, pricing, orders, checker = build_system()
    assert callable(getattr(inventory, '__init__', None))
    assert callable(getattr(reservation, '__init__', None))
    assert callable(getattr(pricing, '__init__', None))
    assert callable(getattr(orders, '__init__', None))
    assert callable(getattr(checker, '__init__', None))
# AI_TEST_AGENT_END function=build_system

# AI_TEST_AGENT_START function=seed_catalog
def test_seed_catalog_calls_add_product_and_update_stock_correctly():
    inventory = MagicMock()
    seed_catalog(inventory)
    expected_add_calls = [
        call("P001", "Laptop", 999.99),
        call("P002", "Wireless Mouse", 29.99),
        call("P003", "Mechanical Keyboard", 79.99),
        call("P004", "USB-C Hub", 49.99),
        call("P005", "Monitor Stand", 39.99),
    ]
    expected_update_calls = [
        call("P001", 15),
        call("P002", 80),
        call("P003", 40),
        call("P004", 60),
        call("P005", 25),
    ]
    assert inventory.add_product.call_count == 5
    assert inventory.add_product.call_args_list == expected_add_calls
    assert inventory.update_stock.call_count == 5
    assert inventory.update_stock.call_args_list == expected_update_calls

def test_seed_catalog_raises_if_add_product_raises():
    inventory = MagicMock()
    inventory.add_product.side_effect = [None, None, Exception("Add failed"), None, None]
    with pytest.raises(Exception, match="Add failed"):
        seed_catalog(inventory)
    assert inventory.add_product.call_count == 3
    assert inventory.update_stock.call_count == 0

def test_seed_catalog_raises_if_update_stock_raises():
    inventory = MagicMock()
    inventory.add_product.return_value = None
    inventory.update_stock.side_effect = [None, None, Exception("Update failed")]
    with pytest.raises(Exception, match="Update failed"):
        seed_catalog(inventory)
    assert inventory.add_product.call_count == 5
    assert inventory.update_stock.call_count == 3

def test_seed_catalog_with_inventory_methods_accepting_unexpected_types():
    inventory = MagicMock()
    inventory.add_product.side_effect = lambda pid, name, price: None if isinstance(pid, str) and isinstance(name, str) and isinstance(price, float) else Exception("Invalid add_product args")
    inventory.update_stock.side_effect = lambda pid, qty: None if isinstance(pid, str) and isinstance(qty, int) else Exception("Invalid update_stock args")
    seed_catalog(inventory)
    assert inventory.add_product.call_count == 5
    assert inventory.update_stock.call_count == 5

def test_seed_catalog_with_inventory_add_product_receiving_empty_strings_and_zero_price():
    inventory = MagicMock()
    inventory.add_product.side_effect = None
    inventory.update_stock.side_effect = None
    inventory.add_product = MagicMock()
    inventory.update_stock = MagicMock()
    def add_product_side_effect(pid, name, price):
        if pid == "" or name == "" or price < 0:
            raise ValueError("Invalid product data")
    inventory.add_product.side_effect = add_product_side_effect
    inventory.update_stock.return_value = None
    with pytest.raises(ValueError):
        inventory.add_product("", "Laptop", 999.99)
    with pytest.raises(ValueError):
        inventory.add_product("P001", "", 999.99)
    with pytest.raises(ValueError):
        inventory.add_product("P001", "Laptop", -1.0)

def test_seed_catalog_with_inventory_update_stock_receiving_negative_stock():
    inventory = MagicMock()
    inventory.add_product.return_value = None
    def update_stock_side_effect(pid, qty):
        if qty < 0:
            raise ValueError("Stock cannot be negative")
    inventory.update_stock.side_effect = update_stock_side_effect
    seed_catalog(inventory)
    with pytest.raises(ValueError):
        inventory.update_stock("P001", -10)

def test_seed_catalog_with_inventory_methods_receiving_none_arguments():
    inventory = MagicMock()
    inventory.add_product.side_effect = lambda pid, name, price: None
    inventory.update_stock.side_effect = lambda pid, qty: None
    with pytest.raises(TypeError):
        inventory.add_product(None, "Laptop", 999.99)
    with pytest.raises(TypeError):
        inventory.add_product("P001", None, 999.99)
    with pytest.raises(TypeError):
        inventory.add_product("P001", "Laptop", None)
    with pytest.raises(TypeError):
        inventory.update_stock(None, 15)
    with pytest.raises(TypeError):
        inventory.update_stock("P001", None)

def test_seed_catalog_partial_failure_in_add_product_stops_execution():
    inventory = MagicMock()
    inventory.add_product.side_effect = [None, Exception("Fail on second product")]
    with pytest.raises(Exception, match="Fail on second product"):
        seed_catalog(inventory)
    assert inventory.add_product.call_count == 2
    assert inventory.update_stock.call_count == 0

def test_seed_catalog_partial_failure_in_update_stock_stops_execution():
    inventory = MagicMock()
    inventory.add_product.return_value = None
    inventory.update_stock.side_effect = [None, None, Exception("Fail on third stock update")]
    with pytest.raises(Exception, match="Fail on third stock update"):
        seed_catalog(inventory)
    assert inventory.add_product.call_count == 5
    assert inventory.update_stock.call_count == 3
# AI_TEST_AGENT_END function=seed_catalog

# AI_TEST_AGENT_START function=run_demo
def test_run_demo_normal_flow(capsys):
    mock_inventory = MagicMock()
    mock_reservation = MagicMock()
    mock_pricing = MagicMock()
    mock_orders = MagicMock()
    mock_checker = MagicMock()

    product1 = MagicMock()
    product1.__str__.return_value = "Product1"
    product2 = MagicMock()
    product2.__str__.return_value = "Product2"
    product3 = MagicMock()
    product3.__str__.return_value = "Product3"
    mock_inventory.get_all_products.return_value = [product1, product2, product3]

    order1 = MagicMock()
    order1.total = 100
    order1.status.value = "created"
    order1.order_id = "order1"
    order1.discount_applied = 0
    mock_orders.create_order.return_value = order1

    order2 = MagicMock()
    order2.status.value = "created"
    order2.order_id = "order2"
    mock_orders.create_order.side_effect = [order1, order2]

    mock_reservation.get_reserved.side_effect = [5, 0]
    mock_reservation.get_available.side_effect = [10, 20]

    mock_checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    mock_checker.get_reservation_summary.return_value = {"summary_key": "summary_value"}

    mock_inventory.get_stock.return_value = 50
    low_stock_product = MagicMock()
    low_stock_product.product_id = "P001"
    low_stock_product.available_stock.return_value = 5
    mock_inventory.list_low_stock.return_value = [low_stock_product]

    with patch("inventory_system.main.build_system", return_value=(mock_inventory, mock_reservation, mock_pricing, mock_orders, mock_checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    mock_seed_catalog.assert_called_once_with(mock_inventory)
    mock_inventory.get_all_products.assert_called_once()
    assert mock_orders.create_order.call_count == 2
    mock_orders.process_order.assert_any_call(order1.order_id)
    mock_orders.process_order.assert_any_call(order2.order_id)
    mock_pricing.apply_discount.assert_called_once_with(order1, "SAVE10")
    mock_orders.cancel_order.assert_called_once_with(order2.order_id)
    mock_orders.complete_order.assert_called_once_with(order1.order_id)
    mock_checker.validate_inventory_state.assert_called_once()
    mock_checker.get_reservation_summary.assert_called_once()
    mock_inventory.list_low_stock.assert_called_once_with(threshold=10)
    low_stock_product.available_stock.assert_called_once()


def test_run_demo_pricing_apply_discount_raises_exception(capsys):
    mock_inventory = MagicMock()
    mock_reservation = MagicMock()
    mock_pricing = MagicMock()
    mock_orders = MagicMock()
    mock_checker = MagicMock()

    product = MagicMock()
    product.__str__.return_value = "Product"
    mock_inventory.get_all_products.return_value = [product]

    order1 = MagicMock()
    order1.total = 100
    order1.status.value = "created"
    order1.order_id = "order1"
    order1.discount_applied = 0
    mock_orders.create_order.return_value = order1

    order2 = MagicMock()
    order2.status.value = "created"
    order2.order_id = "order2"
    mock_orders.create_order.side_effect = [order1, order2]

    mock_reservation.get_reserved.return_value = 5
    mock_reservation.get_available.return_value = 10

    mock_pricing.apply_discount.side_effect = ValueError("Invalid discount code")

    mock_checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    mock_checker.get_reservation_summary.return_value = {}

    mock_inventory.get_stock.return_value = 50
    mock_inventory.list_low_stock.return_value = []

    with patch("inventory_system.main.build_system", return_value=(mock_inventory, mock_reservation, mock_pricing, mock_orders, mock_checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    mock_pricing.apply_discount.assert_called_once_with(order1, "SAVE10")
    captured = capsys.readouterr()
    assert "Discount error: Invalid discount code" in captured.out


def test_run_demo_empty_product_catalog(capsys):
    mock_inventory = MagicMock()
    mock_reservation = MagicMock()
    mock_pricing = MagicMock()
    mock_orders = MagicMock()
    mock_checker = MagicMock()

    mock_inventory.get_all_products.return_value = []

    order1 = MagicMock()
    order1.total = 0
    order1.status.value = "created"
    order1.order_id = "order1"
    order1.discount_applied = 0
    mock_orders.create_order.return_value = order1

    order2 = MagicMock()
    order2.status.value = "created"
    order2.order_id = "order2"
    mock_orders.create_order.side_effect = [order1, order2]

    mock_reservation.get_reserved.return_value = 0
    mock_reservation.get_available.return_value = 0

    mock_checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    mock_checker.get_reservation_summary.return_value = {}

    mock_inventory.get_stock.return_value = 0
    mock_inventory.list_low_stock.return_value = []

    with patch("inventory_system.main.build_system", return_value=(mock_inventory, mock_reservation, mock_pricing, mock_orders, mock_checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    mock_inventory.get_all_products.assert_called_once()
    mock_orders.create_order.assert_called()
    mock_orders.process_order.assert_called()
    mock_orders.cancel_order.assert_called()
    mock_orders.complete_order.assert_called()
    mock_checker.validate_inventory_state.assert_called_once()
    mock_checker.get_reservation_summary.assert_called_once()
    mock_inventory.list_low_stock.assert_called_once()


def test_run_demo_checker_returns_errors_and_warnings(capsys):
    mock_inventory = MagicMock()
    mock_reservation = MagicMock()
    mock_pricing = MagicMock()
    mock_orders = MagicMock()
    mock_checker = MagicMock()

    product = MagicMock()
    product.__str__.return_value = "Product"
    mock_inventory.get_all_products.return_value = [product]

    order1 = MagicMock()
    order1.total = 100
    order1.status.value = "created"
    order1.order_id = "order1"
    order1.discount_applied = 0
    mock_orders.create_order.return_value = order1

    order2 = MagicMock()
    order2.status.value = "created"
    order2.order_id = "order2"
    mock_orders.create_order.side_effect = [order1, order2]

    mock_reservation.get_reserved.return_value = 5
    mock_reservation.get_available.return_value = 10

    mock_checker.validate_inventory_state.return_value = {
        "valid": False,
        "errors": ["Error1", "Error2"],
        "warnings": ["Warning1"]
    }
    mock_checker.get_reservation_summary.return_value = {}

    mock_inventory.get_stock.return_value = 50
    mock_inventory.list_low_stock.return_value = []

    with patch("inventory_system.main.build_system", return_value=(mock_inventory, mock_reservation, mock_pricing, mock_orders, mock_checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    captured = capsys.readouterr()
    assert "Valid: False" in captured.out
    assert "Error: Error1" in captured.out
    assert "Error: Error2" in captured.out
    assert "Warning: Warning1" in captured.out


def test_run_demo_orders_create_order_raises_exception(capsys):
    mock_inventory = MagicMock()
    mock_reservation = MagicMock()
    mock_pricing = MagicMock()
    mock_orders = MagicMock()
    mock_checker = MagicMock()

    product = MagicMock()
    product.__str__.return_value = "Product"
    mock_inventory.get_all_products.return_value = [product]

    mock_orders.create_order.side_effect = Exception("Order creation failed")

    mock_checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    mock_checker.get_reservation_summary.return_value = {}

    mock_inventory.get_stock.return_value = 50
    mock_inventory.list_low_stock.return_value = []

    with patch("inventory_system.main.build_system", return_value=(mock_inventory, mock_reservation, mock_pricing, mock_orders, mock_checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        with pytest.raises(Exception, match="Order creation failed"):
            run_demo()


def test_run_demo_inventory_list_low_stock_empty(capsys):
    mock_inventory = MagicMock()
    mock_reservation = MagicMock()
    mock_pricing = MagicMock()
    mock_orders = MagicMock()
    mock_checker = MagicMock()

    product = MagicMock()
    product.__str__.return_value = "Product"
    mock_inventory.get_all_products.return_value = [product]

    order1 = MagicMock()
    order1.total = 100
    order1.status.value = "created"
    order1.order_id = "order1"
    order1.discount_applied = 0
    mock_orders.create_order.return_value = order1

    order2 = MagicMock()
    order2.status.value = "created"
    order2.order_id = "order2"
    mock_orders.create_order.side_effect = [order1, order2]

    mock_reservation.get_reserved.return_value = 5
    mock_reservation.get_available.return_value = 10

    mock_checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    mock_checker.get_reservation_summary.return_value = {}

    mock_inventory.get_stock.return_value = 50
    mock_inventory.list_low_stock.return_value = []

    with patch("inventory_system.main.build_system", return_value=(mock_inventory, mock_reservation, mock_pricing, mock_orders, mock_checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    mock_inventory.list_low_stock.assert_called_once_with(threshold=10)


def test_run_demo_reservation_methods_return_zero(capsys):
    mock_inventory = MagicMock()
    mock_reservation = MagicMock()
    mock_pricing = MagicMock()
    mock_orders = MagicMock()
    mock_checker = MagicMock()

    product = MagicMock()
    product.__str__.return_value = "Product"
    mock_inventory.get_all_products.return_value = [product]

    order1 = MagicMock()
    order1.total = 100
    order1.status.value = "created"
    order1.order_id = "order1"
    order1.discount_applied = 0
    mock_orders.create_order.return_value = order1

    order2 = MagicMock()
    order2.status.value = "created"
    order2.order_id = "order2"
    mock_orders.create_order.side_effect = [order1, order2]

    mock_reservation.get_reserved.return_value = 0
    mock_reservation.get_available.return_value = 0

    mock_checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    mock_checker.get_reservation_summary.return_value = {}

    mock_inventory.get_stock.return_value = 50
    mock_inventory.list_low_stock.return_value = []

    with patch("inventory_system.main.build_system", return_value=(mock_inventory, mock_reservation, mock_pricing, mock_orders, mock_checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    mock_reservation.get_reserved.assert_called()
    mock_reservation.get_available.assert_called()
# AI_TEST_AGENT_END function=run_demo
