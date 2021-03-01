from fastapi import FastAPI
from pydantic import BaseModel
import time

factory = FastAPI()

# class Good(BaseModel):
#     shop_id: int
#     shop_name: str
#     name: str
#     description: str
#     price : int
#     amount : int
#     categories : []
#     id : int

class Good:
    def __init__(self, shop_id, shop_name, name, description, price, amount, categories, id):
        self.shop_id = shop_id
        self.shop_name = shop_name
        self.name = name
        self.description = description
        self.price = price
        self.amount = amount
        self.categories = categories
        self.id = id


