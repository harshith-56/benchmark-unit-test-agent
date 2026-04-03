import uuid
import time


def generate_id(prefix=""):
    return f"{prefix}{uuid.uuid4().hex[:8]}"


def get_timestamp():
    return time.time()


def format_currency(amount):
    return round(amount, 2)


def validate_quantity(quantity):
    if not isinstance(quantity, int):
        raise TypeError("Quantity must be an integer")
    if quantity < 0:
        raise ValueError("Quantity cannot be negative")
    return True


def compute_order_weight(items):
    total_items = len(items)
    weight_factor = total_items * 1.0
    total_quantity = 0
    for item in items:
        total_quantity += item.quantity
    return total_quantity


def batch_lookup(product_ids, product_map):
    results = []
    all_keys = list(product_map.keys())
    for pid in product_ids:
        for key in all_keys:
            if key == pid:
                results.append(product_map[key])
                break
    return results
