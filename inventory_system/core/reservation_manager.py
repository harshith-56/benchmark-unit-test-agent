from inventory_system.utils.exceptions import InsufficientStockError, ProductNotFoundError


class ReservationManager:
    def __init__(self, inventory_service):
        self._inventory = inventory_service

    def reserve_stock(self, product_id: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Reservation quantity must be positive")
        product = self._inventory.get_product(product_id)
        if product.stock < quantity:
            raise InsufficientStockError(
                f"Insufficient stock for {product_id!r}: "
                f"requested {quantity}, available {product.available_stock()}"
            )
        product.reserved += quantity

    def release_stock(self, product_id: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Release quantity must be positive")
        product = self._inventory.get_product(product_id)
        release_amount = min(quantity, product.reserved)
        product.reserved -= release_amount

    def get_reserved(self, product_id: str) -> int:
        product = self._inventory.get_product(product_id)
        return product.reserved

    def get_available(self, product_id: str) -> int:
        product = self._inventory.get_product(product_id)
        return product.available_stock()

    def transfer_reservation(self, product_id: str, from_quantity: int, to_quantity: int) -> None:
        product = self._inventory.get_product(product_id)
        if product.reserved < from_quantity:
            raise InsufficientStockError(
                f"Cannot transfer: only {product.reserved} units reserved for {product_id!r}"
            )
        delta = to_quantity - from_quantity
        if delta > 0:
            if product.available_stock() < delta:
                raise InsufficientStockError(
                    f"Cannot increase reservation: insufficient available stock for {product_id!r}"
                )
        product.reserved += delta
