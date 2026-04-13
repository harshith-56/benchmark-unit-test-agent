class InventoryError(Exception):
    pass


class InsufficientStockError(InventoryError):
    pass


class ProductNotFoundError(InventoryError):
    pass


class OrderNotFoundError(InventoryError):
    pass


class InvalidDiscountError(InventoryError):
    pass


class OrderStateError(InventoryError):
    pass
