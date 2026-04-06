from inventory_system.services.inventory_service import InventoryService
from inventory_system.services.order_service import OrderService
from inventory_system.services.pricing_service import PricingService
from inventory_system.core.reservation_manager import ReservationManager
from inventory_system.core.consistency_checker import ConsistencyChecker


def build_system():
    inventory = InventoryService()
    reservation = ReservationManager(inventory)
    pricing = PricingService(inventory)
    orders = OrderService(inventory, reservation, pricing)
    checker = ConsistencyChecker(inventory, orders)
    return inventory, reservation, pricing, orders, checker


def seed_catalog(inventory):
    inventory.add_product("P001", "Laptop", 999.99)
    inventory.add_product("P002", "Wireless Mouse", 29.99)
    inventory.add_product("P003", "Mechanical Keyboard", 79.99)
    inventory.add_product("P004", "USB-C Hub", 49.99)
    inventory.add_product("P005", "Monitor Stand", 39.99)

    inventory.update_stock("P001", 15)
    inventory.update_stock("P002", 80)
    inventory.update_stock("P003", 40)
    inventory.update_stock("P004", 60)
    inventory.update_stock("P005", 25)


def run_demo():
    inventory, reservation, pricing, orders, checker = build_system()
    seed_catalog(inventory)

    print("=== Inventory System Demo ===\n")

    print("--- Product Catalog ---")
    for product in inventory.get_all_products():
        print(f"  {product}")

    print("\n--- Creating Order ---")
    order1 = orders.create_order("USER-001", [
        {"product_id": "P001", "quantity": 2},
        {"product_id": "P002", "quantity": 3},
        {"product_id": "P004", "quantity": 1},
    ])
    print(f"  Created: {order1}")
    print(f"  Total: ${order1.total}")

    print("\n--- Processing Order ---")
    orders.process_order(order1.order_id)
    print(f"  Status: {order1.status.value}")
    print(f"  P001 reserved: {reservation.get_reserved('P001')}")
    print(f"  P001 available: {reservation.get_available('P001')}")

    print("\n--- Applying Discount ---")
    try:
        pricing.apply_discount(order1, "SAVE10")
        print(f"  Discounted total: ${order1.total}")
        print(f"  Discount applied: ${order1.discount_applied}")
    except Exception as e:
        print(f"  Discount error: {e}")

    print("\n--- Creating Second Order ---")
    order2 = orders.create_order("USER-002", [
        {"product_id": "P003", "quantity": 1},
        {"product_id": "P005", "quantity": 2},
    ])
    print(f"  Created: {order2}")
    orders.process_order(order2.order_id)
    print(f"  Processed: {order2.status.value}")

    print("\n--- Cancelling Second Order ---")
    orders.cancel_order(order2.order_id)
    print(f"  Status after cancel: {order2.status.value}")
    print(f"  P003 reserved after cancel: {reservation.get_reserved('P003')}")

    print("\n--- Completing First Order ---")
    orders.complete_order(order1.order_id)
    print(f"  Status: {order1.status.value}")
    print(f"  P001 stock after completion: {inventory.get_stock('P001')}")

    print("\n--- Consistency Check ---")
    result = checker.validate_inventory_state()
    print(f"  Valid: {result['valid']}")
    if result["errors"]:
        for err in result["errors"]:
            print(f"  Error: {err}")
    if result["warnings"]:
        for w in result["warnings"]:
            print(f"  Warning: {w}")

    print("\n--- Reservation Summary ---")
    summary = checker.get_reservation_summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\n--- Low Stock Report ---")
    low = inventory.list_low_stock(threshold=10)
    for p in low:
        print(f"  {p.product_id}: available={p.available_stock()}")


if __name__ == "__main__":
    run_demo()
