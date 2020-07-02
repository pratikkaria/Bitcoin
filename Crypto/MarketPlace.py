from typing import List, Dict

class Seller:
    def __init__(self, itemListWithPrice: Dict[str, int]):
        self.availableItems: Dict[str, int] = itemList


class Buyer:
    def __init__(self, requiredItem: str):
        self.requiredItem = requiredItem


class Contract:
    def __init__(self, state: str):
        self.state = "Available"
