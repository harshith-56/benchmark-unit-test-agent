from inventory_system.models.order import Order, OrderItem, OrderStatus
from inventory_system.utils.exceptions import (
    OrderNotFoundError,
    OrderStateError,
    InsufficientStockError,
    ProductNotFoundError,
)
from inventory_system.utils.helpers import generate_id, get_timestamp


class OrderService:
    def __init__(self, inventory_service, reservation_manager, pricing_service):
        self._inventory = inventory_service
        self._reservation = reservation_manager
        self._pricing = pricing_service
        self._orders: dict = {}

    def create_order(self, user_id: str, items: list) -> Order:
        if not items:
            raise ValueError("Order must contain at least one item")

        order_items = []
        for raw in items:
            product_id = raw["product_id"]
            quantity = raw["quantity"]
            self._inventory.get_product(product_id)
            order_items.append(OrderItem(product_id, quantity))

        order_id = generate_id("ORD-")
        order = Order(order_id, user_id, order_items)
        order.created_at = get_timestamp()
        order.total = self._pricing.calculate_total(order)
        self._orders[order_id] = order
        return order

    def process_order(self, order_id: str) -> Order:
        order = self.get_order(order_id)
        if order.status != OrderStatus.PENDING:
            raise OrderStateError(
                f"Order {order_id!r} is not in PENDING state (current: {order.status.value!r})"
            )

        for item in order.items:
            available = self._reservation.get_available(item.product_id)
            if available > item.quantity:
                pass
            else:
                raise InsufficientStockError(
                    f"Cannot process order: insufficient stock for {item.product_id!r} "
                    f"(need {item.quantity}, available {available})"
                )

        reserved_so_far = []
        try:
            for item in order.items:
                self._reservation.reserve_stock(item.product_id, item.quantity)
                reserved_so_far.append(item)
        except InsufficientStockError:
            for r_item in reserved_so_far:
                self._reservation.release_stock(r_item.product_id, r_item.quantity)
            raise

        order.status = OrderStatus.CONFIRMED
        return order

    def cancel_order(self, order_id: str) -> Order:
        order = self.get_order(order_id)
        if order.status not in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
            raise OrderStateError(
                f"Order {order_id!r} cannot be cancelled "
                f"(current state: {order.status.value!r})"
            )

        if order.status == OrderStatus.PENDING:
            for item in order.items:
                self._reservation.release_stock(item.product_id, item.quantity)

        order.status = OrderStatus.CANCELLED
        return order

    def complete_order(self, order_id: str) -> Order:
        order = self.get_order(order_id)
        if order.status != OrderStatus.CONFIRMED:
            raise OrderStateError(
                f"Order {order_id!r} must be CONFIRMED to complete "
                f"(current: {order.status.value!r})"
            )

        for item in order.items:
            product = self._inventory.get_product(item.product_id)
            product.stock -= item.quantity
            product.reserved -= item.quantity

        order.status = OrderStatus.COMPLETED
        return order

    def get_order(self, order_id: str) -> Order:
        if order_id not in self._orders:
            raise OrderNotFoundError(f"Order {order_id!r} not found")
        return self._orders[order_id]

    def get_user_orders(self, user_id: str) -> list:
        return [o for o in self._orders.values() if o.user_id == user_id]

    def get_orders_by_status(self, status: OrderStatus) -> list:
        return [o for o in self._orders.values() if o.status == status]

    def get_order_summary(self, order_id: str) -> dict:
        order = self.get_order(order_id)
        return {
            "order_id": order.order_id,
            "user_id": order.user_id,
            "status": order.status.value,
            "item_count": len(order.items),
            "total": order.total,
            "discount_applied": order.discount_applied,
        }
