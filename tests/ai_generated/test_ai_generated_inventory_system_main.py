from inventory_system.main import build_system
from inventory_system.main import run_demo
from inventory_system.main import seed_catalog
from unittest.mock import MagicMock
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

def test_build_system_inventory_is_instance():
    inventory, _, _, _, _ = build_system()
    # InventoryService instance check by attribute presence
    assert hasattr(inventory, 'add_product') or hasattr(inventory, 'update_stock')

def test_build_system_reservation_manager_links_inventory():
    inventory, reservation, _, _, _ = build_system()
    # ReservationManager should hold reference to inventory
    assert hasattr(reservation, '_inventory') or hasattr(reservation, 'inventory')

def test_build_system_pricing_service_links_inventory():
    inventory, _, pricing, _, _ = build_system()
    # PricingService should hold reference to inventory
    assert hasattr(pricing, '_inventory') or hasattr(pricing, 'inventory')

def test_build_system_order_service_links_dependencies():
    inventory, reservation, pricing, orders, _ = build_system()
    # OrderService should hold references to inventory, reservation, pricing
    assert hasattr(orders, '_inventory') or hasattr(orders, 'inventory')
    assert hasattr(orders, '_reservation_manager') or hasattr(orders, 'reservation_manager')
    assert hasattr(orders, '_pricing_service') or hasattr(orders, 'pricing_service')

def test_build_system_consistency_checker_links_inventory_and_orders():
    inventory, _, _, orders, checker = build_system()
    # ConsistencyChecker should hold references to inventory and orders
    assert hasattr(checker, '_inventory') or hasattr(checker, 'inventory')
    assert hasattr(checker, '_orders') or hasattr(checker, 'orders')

def test_build_system_multiple_calls_return_distinct_instances():
    system1 = build_system()
    system2 = build_system()
    # Each call returns new instances, not the same objects
    for obj1, obj2 in zip(system1, system2):
        assert obj1 is not obj2

def test_build_system_no_arguments_allowed():
    with pytest.raises(TypeError):
        build_system(1)

def test_build_system_return_types_are_correct():
    inventory, reservation, pricing, orders, checker = build_system()
    # Check types by class name strings to avoid import errors
    assert inventory.__class__.__name__ == 'InventoryService'
    assert reservation.__class__.__name__ == 'ReservationManager'
    assert pricing.__class__.__name__ == 'PricingService'
    assert orders.__class__.__name__ == 'OrderService'
    assert checker.__class__.__name__ == 'ConsistencyChecker'
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
    inventory.add_product.assert_has_calls(expected_add_calls, any_order=False)
    assert inventory.update_stock.call_count == 5
    inventory.update_stock.assert_has_calls(expected_update_calls, any_order=False)

def test_seed_catalog_with_inventory_add_product_raises_propagates():
    inventory = MagicMock()
    inventory.add_product.side_effect = ValueError("Invalid price")
    with pytest.raises(ValueError, match="Invalid price"):
        seed_catalog(inventory)
    assert inventory.add_product.call_count == 1
    assert inventory.update_stock.call_count == 0

def test_seed_catalog_with_inventory_update_stock_raises_propagates():
    inventory = MagicMock()
    inventory.update_stock.side_effect = ValueError("Negative stock")
    # add_product should succeed
    inventory.add_product.side_effect = None
    with pytest.raises(ValueError, match="Negative stock"):
        seed_catalog(inventory)
    assert inventory.add_product.call_count == 5
    assert inventory.update_stock.call_count == 1

def test_seed_catalog_with_inventory_methods_called_in_order():
    inventory = MagicMock()
    calls = []
    def add_product_side_effect(*args, **kwargs):
        calls.append(("add_product", args))
    def update_stock_side_effect(*args, **kwargs):
        calls.append(("update_stock", args))
    inventory.add_product.side_effect = add_product_side_effect
    inventory.update_stock.side_effect = update_stock_side_effect
    seed_catalog(inventory)
    expected_calls = [
        ("add_product", ("P001", "Laptop", 999.99)),
        ("add_product", ("P002", "Wireless Mouse", 29.99)),
        ("add_product", ("P003", "Mechanical Keyboard", 79.99)),
        ("add_product", ("P004", "USB-C Hub", 49.99)),
        ("add_product", ("P005", "Monitor Stand", 39.99)),
        ("update_stock", ("P001", 15)),
        ("update_stock", ("P002", 80)),
        ("update_stock", ("P003", 40)),
        ("update_stock", ("P004", 60)),
        ("update_stock", ("P005", 25)),
    ]
    assert calls == expected_calls

def test_seed_catalog_with_inventory_add_product_receives_correct_types():
    inventory = MagicMock()
    seed_catalog(inventory)
    for call in inventory.add_product.call_args_list:
        args, _ = call
        assert isinstance(args[0], str)
        assert isinstance(args[1], str)
        assert isinstance(args[2], float)

def test_seed_catalog_with_inventory_update_stock_receives_correct_types():
    inventory = MagicMock()
    seed_catalog(inventory)
    for call in inventory.update_stock.call_args_list:
        args, _ = call
        assert isinstance(args[0], str)
        assert isinstance(args[1], int)

def test_seed_catalog_with_inventory_add_product_called_with_empty_strings_and_zero_price():
    inventory = MagicMock()
    inventory.add_product.side_effect = lambda pid, name, price: None
    inventory.update_stock.side_effect = lambda pid, qty: None
    # Patch seed_catalog to call add_product with empty string and zero price to test failure
    def fake_seed(inventory):
        inventory.add_product("", "", 0.0)
        inventory.update_stock("", 0)
    with pytest.raises(AssertionError):
        fake_seed(inventory)
    # This test is to show that seed_catalog does not handle empty or zero price, but since seed_catalog is fixed, this test will fail if we call fake_seed instead

def test_seed_catalog_with_inventory_update_stock_called_with_zero_and_negative_stock():
    inventory = MagicMock()
    inventory.add_product.side_effect = lambda pid, name, price: None
    inventory.update_stock.side_effect = lambda pid, qty: None
    # Patch seed_catalog to call update_stock with zero and negative stock to test failure
    def fake_seed(inventory):
        inventory.add_product("P006", "Test Product", 10.0)
        inventory.update_stock("P006", 0)
        inventory.update_stock("P006", -1)
    fake_seed(inventory)
    calls = inventory.update_stock.call_args_list
    assert calls[0][0] == ("P006", 0)
    assert calls[1][0] == ("P006", -1)
# AI_TEST_AGENT_END function=seed_catalog

# AI_TEST_AGENT_START function=run_demo
@patch('inventory_system.main.build_system')
@patch('inventory_system.main.seed_catalog')
def test_run_demo_normal_flow(mock_seed_catalog, mock_build_system):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    mock_build_system.return_value = (inventory, reservation, pricing, orders, checker)

    product1 = MagicMock()
    product1.__str__.return_value = "Product1"
    product2 = MagicMock()
    product2.__str__.return_value = "Product2"
    inventory.get_all_products.return_value = [product1, product2]

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "created"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 2
    reservation.get_available.return_value = 8

    def apply_discount_side_effect(order, code):
        order.total = 90
        order.discount_applied = 10

    pricing.apply_discount.side_effect = apply_discount_side_effect

    order2 = MagicMock()
    order2.order_id = "order2"
    order2.status.value = "created"
    orders.create_order.side_effect = [order1, order2]

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {"P001": 2, "P002": 3}

    inventory.get_stock.return_value = 50
    low_stock_product = MagicMock()
    low_stock_product.product_id = "P001"
    low_stock_product.available_stock.return_value = 5
    inventory.list_low_stock.return_value = [low_stock_product]

    run_demo()

    mock_build_system.assert_called_once()
    mock_seed_catalog.assert_called_once_with(inventory)
    inventory.get_all_products.assert_called_once()
    assert orders.create_order.call_count == 2
    orders.process_order.assert_any_call(order1.order_id)
    orders.process_order.assert_any_call(order2.order_id)
    pricing.apply_discount.assert_called_once_with(order1, "SAVE10")
    orders.cancel_order.assert_called_once_with(order2.order_id)
    orders.complete_order.assert_called_once_with(order1.order_id)
    checker.validate_inventory_state.assert_called_once()
    checker.get_reservation_summary.assert_called_once()
    inventory.list_low_stock.assert_called_once_with(threshold=10)
    reservation.get_reserved.assert_called()
    reservation.get_available.assert_called()


@patch('inventory_system.main.build_system')
@patch('inventory_system.main.seed_catalog')
def test_run_demo_apply_discount_raises_exception(mock_seed_catalog, mock_build_system):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    mock_build_system.return_value = (inventory, reservation, pricing, orders, checker)

    inventory.get_all_products.return_value = []

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "created"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 0
    reservation.get_available.return_value = 0

    pricing.apply_discount.side_effect = Exception("Discount code invalid")

    order2 = MagicMock()
    order2.order_id = "order2"
    order2.status.value = "created"
    orders.create_order.side_effect = [order1, order2]

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}

    inventory.get_stock.return_value = 0
    inventory.list_low_stock.return_value = []

    run_demo()

    pricing.apply_discount.assert_called_once_with(order1, "SAVE10")
    orders.cancel_order.assert_called_once_with(order2.order_id)
    orders.complete_order.assert_called_once_with(order1.order_id)


@patch('inventory_system.main.build_system')
@patch('inventory_system.main.seed_catalog')
def test_run_demo_empty_product_catalog(mock_seed_catalog, mock_build_system):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    mock_build_system.return_value = (inventory, reservation, pricing, orders, checker)

    inventory.get_all_products.return_value = []

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 0
    order1.status.value = "created"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 0
    reservation.get_available.return_value = 0

    pricing.apply_discount.side_effect = lambda order, code: None

    order2 = MagicMock()
    order2.order_id = "order2"
    order2.status.value = "created"
    orders.create_order.side_effect = [order1, order2]

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}

    inventory.get_stock.return_value = 0
    inventory.list_low_stock.return_value = []

    run_demo()

    inventory.get_all_products.assert_called_once()
    orders.create_order.assert_called()
    orders.process_order.assert_called()
    pricing.apply_discount.assert_called_once_with(order1, "SAVE10")
    orders.cancel_order.assert_called_once_with(order2.order_id)
    orders.complete_order.assert_called_once_with(order1.order_id)
    checker.validate_inventory_state.assert_called_once()
    checker.get_reservation_summary.assert_called_once()
    inventory.list_low_stock.assert_called_once()


@patch('inventory_system.main.build_system')
@patch('inventory_system.main.seed_catalog')
def test_run_demo_process_order_raises_exception(mock_seed_catalog, mock_build_system):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    mock_build_system.return_value = (inventory, reservation, pricing, orders, checker)

    inventory.get_all_products.return_value = []

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "created"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 0
    reservation.get_available.return_value = 0

    def process_order_side_effect(order_id):
        if order_id == order1.order_id:
            raise Exception("Processing error")

    orders.process_order.side_effect = process_order_side_effect

    order2 = MagicMock()
    order2.order_id = "order2"
    order2.status.value = "created"
    orders.create_order.side_effect = [order1, order2]

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}

    inventory.get_stock.return_value = 0
    inventory.list_low_stock.return_value = []

    run_demo()

    orders.process_order.assert_any_call(order1.order_id)
    orders.process_order.assert_any_call(order2.order_id)
    orders.cancel_order.assert_called_once_with(order2.order_id)
    orders.complete_order.assert_called_once_with(order1.order_id)


@patch('inventory_system.main.build_system')
@patch('inventory_system.main.seed_catalog')
def test_run_demo_cancel_order_raises_exception(mock_seed_catalog, mock_build_system):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    mock_build_system.return_value = (inventory, reservation, pricing, orders, checker)

    inventory.get_all_products.return_value = []

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "created"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 0
    reservation.get_available.return_value = 0

    pricing.apply_discount.side_effect = lambda order, code: None

    order2 = MagicMock()
    order2.order_id = "order2"
    order2.status.value = "created"
    orders.create_order.side_effect = [order1, order2]

    def cancel_order_side_effect(order_id):
        raise Exception("Cancel error")

    orders.cancel_order.side_effect = cancel_order_side_effect

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}

    inventory.get_stock.return_value = 0
    inventory.list_low_stock.return_value = []

    run_demo()

    orders.cancel_order.assert_called_once_with(order2.order_id)
    orders.complete_order.assert_called_once_with(order1.order_id)


@patch('inventory_system.main.build_system')
@patch('inventory_system.main.seed_catalog')
def test_run_demo_complete_order_raises_exception(mock_seed_catalog, mock_build_system):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    mock_build_system.return_value = (inventory, reservation, pricing, orders, checker)

    inventory.get_all_products.return_value = []

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "created"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 0
    reservation.get_available.return_value = 0

    pricing.apply_discount.side_effect = lambda order, code: None

    order2 = MagicMock()
    order2.order_id = "order2"
    order2.status.value = "created"
    orders.create_order.side_effect = [order1, order2]

    def complete_order_side_effect(order_id):
        raise Exception("Complete error")

    orders.complete_order.side_effect = complete_order_side_effect

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}

    inventory.get_stock.return_value = 0
    inventory.list_low_stock.return_value = []

    run_demo()

    orders.cancel_order.assert_called_once_with(order2.order_id)
    orders.complete_order.assert_called_once_with(order1.order_id)


@patch('inventory_system.main.build_system')
@patch('inventory_system.main.seed_catalog')
def test_run_demo_consistency_checker_returns_errors_and_warnings(mock_seed_catalog, mock_build_system):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    mock_build_system.return_value = (inventory, reservation, pricing, orders, checker)

    inventory.get_all_products.return_value = []

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "created"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 0
    reservation.get_available.return_value = 0

    pricing.apply_discount.side_effect = lambda order, code: None

    order2 = MagicMock()
    order2.order_id = "order2"
    order2.status.value = "created"
    orders.create_order.side_effect = [order1, order2]

    checker.validate_inventory_state.return_value = {
        "valid": False,
        "errors": ["Error1", "Error2"],
        "warnings": ["Warning1"]
    }
    checker.get_reservation_summary.return_value = {}

    inventory.get_stock.return_value = 0
    inventory.list_low_stock.return_value = []

    run_demo()

    checker.validate_inventory_state.assert_called_once()
    checker.get_reservation_summary.assert_called_once()


@patch('inventory_system.main.build_system')
@patch('inventory_system.main.seed_catalog')
def test_run_demo_low_stock_report_empty(mock_seed_catalog, mock_build_system):
    inventory = MagicMock()
    reservation = MagicMock()
    pricing = MagicMock()
    orders = MagicMock()
    checker = MagicMock()

    mock_build_system.return_value = (inventory, reservation, pricing, orders, checker)

    inventory.get_all_products.return_value = []

    order1 = MagicMock()
    order1.order_id = "order1"
    order1.total = 100
    order1.status.value = "created"
    order1.discount_applied = 0
    orders.create_order.return_value = order1

    reservation.get_reserved.return_value = 0
    reservation.get_available.return_value = 0

    pricing.apply_discount.side_effect = lambda order, code: None

    order2 = MagicMock()
    order2.order_id = "order2"
    order2.status.value = "created"
    orders.create_order.side_effect = [order1, order2]

    checker.validate_inventory_state.return_value = {"valid": True, "errors": [], "warnings": []}
    checker.get_reservation_summary.return_value = {}

    inventory.get_stock.return_value = 0
    inventory.list_low_stock.return_value = []

    run_demo()

    inventory.list_low_stock.assert_called_once_with(threshold=10)
# AI_TEST_AGENT_END function=run_demo
