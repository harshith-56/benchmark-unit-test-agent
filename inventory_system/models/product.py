class Product:
    def __init__(self, product_id: str, name: str, price: float):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock = 0
        self.reserved = 0

    def available_stock(self) -> int:
        return self.stock - self.reserved

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "reserved": self.reserved,
            "available": self.available_stock(),
        }

    def __repr__(self):
        return (
            f"Product(id={self.product_id!r}, name={self.name!r}, "
            f"price={self.price}, stock={self.stock}, reserved={self.reserved})"
        )
