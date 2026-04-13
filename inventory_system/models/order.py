from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class OrderItem:
    def __init__(self, product_id: str, quantity: int):
        self.product_id = product_id
        self.quantity = quantity

    def to_dict(self) -> dict:
        return {"product_id": self.product_id, "quantity": self.quantity}

    def __repr__(self):
        return f"OrderItem(product_id={self.product_id!r}, quantity={self.quantity})"


class Order:
    def __init__(self, order_id: str, user_id: str, items: list):
        self.order_id = order_id
        self.user_id = user_id
        self.items = items
        self.status = OrderStatus.PENDING
        self.total = 0.0
        self.discount_applied = 0.0
        self.created_at = None

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id,
            "user_id": self.user_id,
            "items": [item.to_dict() for item in self.items],
            "status": self.status.value,
            "total": self.total,
            "discount_applied": self.discount_applied,
        }

    def __repr__(self):
        return (
            f"Order(id={self.order_id!r}, user={self.user_id!r}, "
            f"status={self.status.value!r}, total={self.total})"
        )
