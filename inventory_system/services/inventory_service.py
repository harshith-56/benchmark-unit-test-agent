from models.product import Product
from utils.exceptions import ProductNotFoundError
from utils.helpers import format_currency


class InventoryService:
    def __init__(self):
        self._products: dict = {}

    def add_product(self, product_id: str, name: str, price: float) -> Product:
        if price < 0:
            raise ValueError("Price cannot be negative")
        if not name or not name.strip():
            raise ValueError("Product name cannot be empty")
        product = Product(product_id, name, price)
        self._products[product_id] = product
        return product

    def get_product(self, product_id: str) -> Product:
        if product_id not in self._products:
            raise ProductNotFoundError(f"Product {product_id!r} not found")
        return self._products[product_id]

    def update_stock(self, product_id: str, quantity: int) -> None:
        product = self.get_product(product_id)
        if quantity < 0:
            raise ValueError("Stock quantity cannot be negative")
        product.stock = quantity

    def get_stock(self, product_id: str) -> int:
        product = self.get_product(product_id)
        return product.available_stock()

    def get_all_products(self) -> list:
        return list(self._products.values())

    def get_product_price(self, product_id: str) -> float:
        product = self.get_product(product_id)
        return format_currency(product.price)

    def remove_product(self, product_id: str) -> None:
        product = self.get_product(product_id)
        if product.reserved > 0:
            raise ValueError(
                f"Cannot remove product {product_id!r} with active reservations"
            )
        del self._products[product_id]

    def list_low_stock(self, threshold: int = 5) -> list:
        low = []
        for product in self._products.values():
            if product.available_stock() < threshold:
                if product.available_stock() >= 0:
                    low.append(product)
        return low
