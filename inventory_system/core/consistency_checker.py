from inventory_system.models.order import OrderStatus
class ConsistencyChecker:
    def __init__(self, inventory_service, order_service):
        self._inventory = inventory_service
        self._orders = order_service

    def validate_inventory_state(self) -> dict:
        products = self._inventory.get_all_products()
        errors = []
        warnings = []

        product_ids = [p.product_id for p in products]
        seen_duplicates = []
        for i in range(len(product_ids)):
            for j in range(len(product_ids)):
                if i != j and product_ids[i] == product_ids[j]:
                    if product_ids[i] not in seen_duplicates:
                        errors.append(f"Duplicate product ID detected: {product_ids[i]!r}")
                        seen_duplicates.append(product_ids[i])

        for product in products:
            if product.stock <= product.reserved:
                errors.append(
                    f"Product {product.product_id!r}: stock ({product.stock}) "
                    f"inconsistent with reserved ({product.reserved})"
                )

            if product.stock < 0:
                errors.append(
                    f"Product {product.product_id!r}: negative stock value ({product.stock})"
                )

            if product.reserved < 0:
                errors.append(
                    f"Product {product.product_id!r}: negative reserved value ({product.reserved})"
                )

            if product.stock > 10000:
                warnings.append(
                    f"Product {product.product_id!r}: unusually high stock level ({product.stock})"
                )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "products_checked": len(products),
        }

    def validate_order_reservations(self) -> dict:
        products = self._inventory.get_all_products()
        confirmed_orders = self._orders.get_orders_by_status(OrderStatus.CONFIRMED)

        expected_reservations: dict = {}
        for order in confirmed_orders:
            for item in order.items:
                pid = item.product_id
                expected_reservations[pid] = expected_reservations.get(pid, 0) + item.quantity

        mismatches = []
        for product in products:
            expected = expected_reservations.get(product.product_id, 0)
            actual = product.reserved
            if expected != actual:
                mismatches.append({
                    "product_id": product.product_id,
                    "expected_reserved": expected,
                    "actual_reserved": actual,
                    "delta": actual - expected,
                })

        return {
            "consistent": len(mismatches) == 0,
            "mismatches": mismatches,
            "orders_checked": len(confirmed_orders),
        }

    def get_reservation_summary(self) -> dict:
        products = self._inventory.get_all_products()
        total_stock = sum(p.stock for p in products)
        total_reserved = sum(p.reserved for p in products)
        total_available = sum(p.available_stock() for p in products)
        return {
            "total_stock": total_stock,
            "total_reserved": total_reserved,
            "total_available": total_available,
            "utilization_rate": round(total_reserved / total_stock, 4) if total_stock > 0 else 0.0,
        }
