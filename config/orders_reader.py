import pandas as pd
from typing import List
import os

class OrdersReader:
    def __init__(self, orders_path: str = "Orders.xlsx"):
        if not os.path.exists(orders_path):
            raise FileNotFoundError(f"Orders file not found: {orders_path}")
        self.orders_df = pd.read_excel(orders_path)

    def get_orders(self) -> List[Order]:
        return [
            Order(
                number=str(row['number']),
                lots_count=int(row['lots_count'])
            )
            for _, row in self.orders_df.iterrows()
        ]