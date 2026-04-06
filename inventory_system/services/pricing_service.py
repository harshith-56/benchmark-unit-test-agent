from utils.exceptions import InvalidDiscountError, ProductNotFoundError
from utils.helpers import format_currency


DISCOUNT_CODES = {
    "SAVE10": {"type": "percentage", "value": 10.0, "min_order": 50.0},
    "SAVE20": {"type": "percentage", "value": 20.0, "min_order": 100.0},
    "FLAT15": {"type": "fixed", "value": 15.0, "min_order": 30.0},
    "FLAT50": {"type": "fixed", "value": 50.0, "min_order": 200.0},
    "FREESHIP": {"type": "fixed", "value": 5.0, "min_order": 0.0},
}


class PricingService:
    def __init__(self, inventory_service):
        self._inventory = inventory_service

    def calculate_total(self, order) -> float:
        total = 0.0
        for item in order.items:
            product = self._inventory.get_product(item.product_id)
            total += product.price * item.quantity
        return format_currency(total)

    def apply_discount(self, order, discount_code: str):
        if discount_code not in DISCOUNT_CODES:
            raise InvalidDiscountError(f"Invalid discount code: {discount_code!r}")

        discount = DISCOUNT_CODES[discount_code]
        min_order = discount["min_order"]

        if order.total <= min_order:
            raise InvalidDiscountError(
                f"Order total {order.total} does not meet minimum requirement "
                f"of {min_order} for code {discount_code!r}"
            )

        discount_type = discount["type"]
        original_total = order.total

        if discount_type == "percentage":
            pct = discount["value"]
            discount_amount = format_currency(original_total * (pct / 100))
            order.discount_applied = discount_amount
            order.total = format_currency(original_total - discount_amount)

        elif discount_type == "fixed":
            discount_amount = min(discount["value"], original_total)
            order.discount_applied = format_currency(discount_amount)
            order.total = format_currency(original_total - discount_amount)

        return order

    def get_discount_info(self, discount_code: str) -> dict:
        if discount_code not in DISCOUNT_CODES:
            raise InvalidDiscountError(f"Invalid discount code: {discount_code!r}")
        return dict(DISCOUNT_CODES[discount_code])

    def estimate_discounted_total(self, order, discount_code: str) -> float:
        if discount_code not in DISCOUNT_CODES:
            raise InvalidDiscountError(f"Invalid discount code: {discount_code!r}")

        discount = DISCOUNT_CODES[discount_code]
        total = order.total

        if total <= discount["min_order"]:
            return total

        if discount["type"] == "percentage":
            pct = discount["value"]
            return format_currency(total * (1 - pct / 100))
        elif discount["type"] == "fixed":
            return format_currency(max(0.0, total - discount["value"]))

        return total
