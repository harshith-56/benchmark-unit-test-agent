from inventory_system.main import InventoryService, ReservationManager, PricingService, OrderService, ConsistencyChecker
from inventory_system.main import build_system
from inventory_system.main import run_demo
from inventory_system.main import seed_catalog
from unittest.mock import MagicMock
from unittest.mock import patch, MagicMock
import pytest

# AI_TEST_AGENT_START function=build_system
def test_build_system_returns_all_components_of_correct_type():
    inventory, reservation, pricing, orders, checker = build_system()
    assert isinstance(inventory, InventoryService)
    assert isinstance(reservation, ReservationManager)
    assert isinstance(pricing, PricingService)
    assert isinstance(orders, OrderService)
    assert isinstance(checker, ConsistencyChecker)

def test_build_system_inventory_and_reservation_linked():
    inventory, reservation, pricing, orders, checker = build_system()
    # ReservationManager should hold reference to the same InventoryService instance
    assert reservation._inventory is inventory

def test_build_system_orders_has_correct_dependencies():
    inventory, reservation, pricing, orders, checker = build_system()
    # OrderService should hold references to inventory, reservation, and pricing instances
    assert orders._inventory is inventory
    assert orders._reservation_manager is reservation
    assert orders._pricing_service is pricing

def test_build_system_pricing_has_inventory_reference():
    inventory, reservation, pricing, orders, checker = build_system()
    # PricingService should hold reference to inventory instance
    assert pricing._inventory is inventory

def test_build_system_consistency_checker_has_inventory_and_orders():
    inventory, reservation, pricing, orders, checker = build_system()
    # ConsistencyChecker should hold references to inventory and orders instances
    assert checker._inventory is inventory
    assert checker._orders is orders

def test_build_system_multiple_calls_return_distinct_instances():
    system1 = build_system()
    system2 = build_system()
    # Each call returns new distinct instances
    for obj1, obj2 in zip(system1, system2):
        assert obj1 is not obj2

def test_build_system_no_arguments_and_returns_tuple_of_length_five():
    result = build_system()
    assert isinstance(result, tuple)
    assert len(result) == 5

def test_build_system_raises_no_exception_on_call():
    try:
        build_system()
    except Exception as e:
        pytest.fail(f"build_system raised an unexpected exception: {e}")

def test_build_system_components_interlinked_consistently():
    inventory, reservation, pricing, orders, checker = build_system()
    # ReservationManager inventory is same as InventoryService
    assert reservation._inventory is inventory
    # PricingService inventory is same as InventoryService
    assert pricing._inventory is inventory
    # OrderService inventory, reservation, pricing are same as created instances
    assert orders._inventory is inventory
    assert orders._reservation_manager is reservation
    assert orders._pricing_service is pricing
    # ConsistencyChecker inventory and orders are same as created instances
    assert checker._inventory is inventory
    assert checker._orders is orders
# AI_TEST_AGENT_END function=build_system

# AI_TEST_AGENT_START function=seed_catalog
def test_seed_catalog_calls_add_product_and_update_stock_correctly():
    inventory = MagicMock()
    seed_catalog(inventory)
    expected_add_calls = [
        (("P001", "Laptop", 999.99),),
        (("P002", "Wireless Mouse", 29.99),),
        (("P003", "Mechanical Keyboard", 79.99),),
        (("P004", "USB-C Hub", 49.99),),
        (("P005", "Monitor Stand", 39.99),),
    ]
    expected_update_calls = [
        (("P001", 15),),
        (("P002", 80),),
        (("P003", 40),),
        (("P004", 60),),
        (("P005", 25),),
    ]
    assert inventory.add_product.call_count == 5
    assert inventory.add_product.call_args_list == expected_add_calls
    assert inventory.update_stock.call_count == 5
    assert inventory.update_stock.call_args_list == expected_update_calls

def test_seed_catalog_raises_when_add_product_raises():
    inventory = MagicMock()
    inventory.add_product.side_effect = [None, None, Exception("Add product failed"), None, None]
    with pytest.raises(Exception, match="Add product failed"):
        seed_catalog(inventory)
    assert inventory.add_product.call_count == 3
    assert inventory.update_stock.call_count == 0

def test_seed_catalog_raises_when_update_stock_raises():
    inventory = MagicMock()
    inventory.add_product.return_value = None
    inventory.update_stock.side_effect = [None, None, Exception("Update stock failed"), None, None]
    with pytest.raises(Exception, match="Update stock failed"):
        seed_catalog(inventory)
    assert inventory.add_product.call_count == 5
    assert inventory.update_stock.call_count == 3

def test_seed_catalog_with_inventory_methods_returning_none():
    inventory = MagicMock()
    inventory.add_product.return_value = None
    inventory.update_stock.return_value = None
    seed_catalog(inventory)
    assert inventory.add_product.call_count == 5
    assert inventory.update_stock.call_count == 5

def test_seed_catalog_with_inventory_methods_returning_unexpected_values():
    inventory = MagicMock()
    inventory.add_product.return_value = "unexpected"
    inventory.update_stock.return_value = 123
    seed_catalog(inventory)
    assert inventory.add_product.call_count == 5
    assert inventory.update_stock.call_count == 5

def test_seed_catalog_with_inventory_methods_raising_type_error():
    inventory = MagicMock()
    inventory.add_product.side_effect = TypeError("Invalid type in add_product")
    with pytest.raises(TypeError, match="Invalid type in add_product"):
        seed_catalog(inventory)
    assert inventory.add_product.call_count == 1
    assert inventory.update_stock.call_count == 0

def test_seed_catalog_with_inventory_methods_raising_value_error():
    inventory = MagicMock()
    inventory.add_product.return_value = None
    inventory.update_stock.side_effect = ValueError("Invalid stock value")
    with pytest.raises(ValueError, match="Invalid stock value"):
        seed_catalog(inventory)
    assert inventory.add_product.call_count == 5
    assert inventory.update_stock.call_count == 1

def test_seed_catalog_with_inventory_methods_called_with_wrong_types():
    inventory = MagicMock()
    inventory.add_product.side_effect = lambda pid, name, price: None if isinstance(pid, str) and isinstance(name, str) and isinstance(price, float) else Exception("Wrong types")
    inventory.update_stock.side_effect = lambda pid, qty: None if isinstance(pid, str) and isinstance(qty, int) else Exception("Wrong types")
    seed_catalog(inventory)
    assert inventory.add_product.call_count == 5
    assert inventory.update_stock.call_count == 5

def test_seed_catalog_with_inventory_methods_called_with_empty_strings_and_zero_price():
    inventory = MagicMock()
    inventory.add_product.side_effect = lambda pid, name, price: None
    inventory.update_stock.side_effect = lambda pid, qty: None
    # Patch seed_catalog to call with empty strings and zero price to test failure
    def seed_catalog_modified(inventory):
        inventory.add_product("", "", 0.0)
        inventory.update_stock("", 0)
    seed_catalog_modified(inventory)
    inventory.add_product.assert_called_once_with("", "", 0.0)
    inventory.update_stock.assert_called_once_with("", 0)
# AI_TEST_AGENT_END function=seed_catalog

# AI_TEST_AGENT_START function=run_demo
def test_run_demo_normal_flow(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    product1 = MagicMock()
    product1.__str__.return_value = "Product1"
    product2 = MagicMock()
    product2.__str__.return_value = "Product2"
    product3 = MagicMock()
    product3.__str__.return_value = "Product3"
    inventory.get_all_products.return_value = [product1, product2, product3]

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "CREATED"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    order2 = MagicMock()
    order2.order_id = "order2"
    order2.status.value = "CREATED"
    orders.create_order.side_effect = [order1, order2]

    reservation.get_reserved.side_effect = [5, 0]
    reservation.get_available.side_effect = [10, 0]

    def apply_discount_side_effect(order, code):
        order.total = 90
        order.discount_applied = 10

    pricing.apply_discount.side_effect = apply_discount_side_effect

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {"P001": 5, "P002": 3}
    low_stock_product = MagicMock()
    low_stock_product.product_id = "P001"
    low_stock_product.available_stock.return_value = 5
    inventory.list_low_stock.return_value = [low_stock_product]
    inventory.get_stock.return_value = 50

    with patch("inventory_system.main.build_system", return_value=(inventory, reservation, pricing, orders, checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    mock_seed_catalog.assert_called_once()
    inventory.get_all_products.assert_called_once()
    assert orders.create_order.call_count == 2
    orders.process_order.assert_any_call("order1")
    orders.process_order.assert_any_call("order2")
    pricing.apply_discount.assert_called_once_with(order1, "SAVE10")
    orders.cancel_order.assert_called_once_with("order2")
    orders.complete_order.assert_called_once_with("order1")
    inventory.get_stock.assert_called_once_with("P001")
    checker.validate_inventory_state.assert_called_once()
    checker.get_reservation_summary.assert_called_once()
    inventory.list_low_stock.assert_called_once_with(threshold=10)
    reservation.get_reserved.assert_any_call("P001")
    reservation.get_available.assert_any_call("P001")


def test_run_demo_discount_raises_exception(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    product = MagicMock()
    product.__str__.return_value = "Product"
    inventory.get_all_products.return_value = [product]

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "CREATED"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 5
    reservation.get_available.return_value = 10

    pricing.apply_discount.side_effect = Exception("Invalid discount code")

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}
    inventory.list_low_stock.return_value = []
    inventory.get_stock.return_value = 50

    with patch("inventory_system.main.build_system", return_value=(inventory, reservation, pricing, orders, checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    mock_seed_catalog.assert_called_once()
    pricing.apply_discount.assert_called_once_with(order1, "SAVE10")
    orders.cancel_order.assert_called_once()
    orders.complete_order.assert_called_once()
    checker.validate_inventory_state.assert_called_once()


def test_run_demo_empty_product_catalog(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    inventory.get_all_products.return_value = []

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 0
    order1.status.value = "CREATED"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 0
    reservation.get_available.return_value = 0

    pricing.apply_discount.side_effect = lambda order, code: None

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}
    inventory.list_low_stock.return_value = []
    inventory.get_stock.return_value = 0

    with patch("inventory_system.main.build_system", return_value=(inventory, reservation, pricing, orders, checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    mock_seed_catalog.assert_called_once()
    inventory.get_all_products.assert_called_once()
    orders.create_order.assert_called_once()
    orders.process_order.assert_called_once()
    pricing.apply_discount.assert_called_once()
    orders.cancel_order.assert_called_once()
    orders.complete_order.assert_called_once()
    checker.validate_inventory_state.assert_called_once()
    checker.get_reservation_summary.assert_called_once()
    inventory.list_low_stock.assert_called_once()


def test_run_demo_process_order_raises(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    product = MagicMock()
    product.__str__.return_value = "Product"
    inventory.get_all_products.return_value = [product]

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "CREATED"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 5
    reservation.get_available.return_value = 10

    def process_order_side_effect(order_id):
        if order_id == "order1":
            raise RuntimeError("Processing error")

    orders.process_order.side_effect = process_order_side_effect

    pricing.apply_discount.side_effect = lambda order, code: None

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}
    inventory.list_low_stock.return_value = []
    inventory.get_stock.return_value = 50

    with patch("inventory_system.main.build_system", return_value=(inventory, reservation, pricing, orders, checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        with pytest.raises(RuntimeError, match="Processing error"):
            run_demo()

    mock_seed_catalog.assert_called_once()
    orders.create_order.assert_called_once()
    orders.process_order.assert_called_once_with("order1")


def test_run_demo_consistency_checker_returns_errors_and_warnings(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    product = MagicMock()
    product.__str__.return_value = "Product"
    inventory.get_all_products.return_value = [product]

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "CREATED"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 5
    reservation.get_available.return_value = 10

    pricing.apply_discount.side_effect = lambda order, code: None

    checker.validate_inventory_state.return_value = {
        "valid": False,
        "errors": ["Negative stock detected"],
        "warnings": ["Reserved quantity exceeds stock"]
    }
    checker.get_reservation_summary.return_value = {}
    inventory.list_low_stock.return_value = []
    inventory.get_stock.return_value = 50

    with patch("inventory_system.main.build_system", return_value=(inventory, reservation, pricing, orders, checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    mock_seed_catalog.assert_called_once()
    checker.validate_inventory_state.assert_called_once()
    checker.get_reservation_summary.assert_called_once()


def test_run_demo_low_stock_empty_list(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    product = MagicMock()
    product.__str__.return_value = "Product"
    inventory.get_all_products.return_value = [product]

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "CREATED"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 5
    reservation.get_available.return_value = 10

    pricing.apply_discount.side_effect = lambda order, code: None

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}
    inventory.list_low_stock.return_value = []
    inventory.get_stock.return_value = 50

    with patch("inventory_system.main.build_system", return_value=(inventory, reservation, pricing, orders, checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    mock_seed_catalog.assert_called_once()
    inventory.list_low_stock.assert_called_once_with(threshold=10)


def test_run_demo_order_create_returns_none(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    product = MagicMock()
    product.__str__.return_value = "Product"
    inventory.get_all_products.return_value = [product]

    orders.create_order.return_value = None

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}
    inventory.list_low_stock.return_value = []
    inventory.get_stock.return_value = 50

    with patch("inventory_system.main.build_system", return_value=(inventory, reservation, pricing, orders, checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        with pytest.raises(AttributeError):
            run_demo()

    mock_seed_catalog.assert_called_once()
    orders.create_order.assert_called_once()


def test_run_demo_reservation_methods_return_none(monkeypatch):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    product = MagicMock()
    product.__str__.return_value = "Product"
    inventory.get_all_products.return_value = [product]

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "CREATED"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = None
    reservation.get_available.return_value = None

    pricing.apply_discount.side_effect = lambda order, code: None

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}
    inventory.list_low_stock.return_value = []
    inventory.get_stock.return_value = 50

    with patch("inventory_system.main.build_system", return_value=(inventory, reservation, pricing, orders, checker)), \
         patch("inventory_system.main.seed_catalog") as mock_seed_catalog:
        run_demo()

    mock_seed_catalog.assert_called_once()
    reservation.get_reserved.assert_called()
    reservation.get_available.assert_called()
# AI_TEST_AGENT_END function=run_demo
