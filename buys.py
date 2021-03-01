import datetime
import json
from typing import Optional

from fastapi import FastAPI, HTTPException
from psycopg2.extras import DictCursor
from pydantic import BaseModel
import psycopg2

con = psycopg2.connect(
    database='backend_rtu',
    user='postgres',
    password='admin',
    host='127.0.0.1',
    port=5432
)
cur = con.cursor()

buys = FastAPI()


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


class User:
    def __init__(self, id, receipt_number):
        self.id = id


class Receipt:
    def __init__(self, id, shop_id, shop_name, buy_date, good_name, amount, categories, good_id, user_id):
        self.id = id
        self.shop_id = shop_id
        self.shop_name = shop_name
        self.buy_date = buy_date
        self.good_name = good_name
        self.amount = amount
        self.categories = categories
        self.good_id = good_id
        self.user_id = user_id


def authorized(user_id):
    cur.execute("select id from buys_users where id = %s", [user_id])
    idd = cur.fetchone()
    if idd is None:
        return False
    else:
        return True


@buys.post("/register")
async def register_user(user_id: int):
    if authorized(user_id):
        return "This id is already used"
    else:
        cur.execute("insert into buys_users values(%s)", [user_id])
        con.commit()
        return "You have successfully registered. Use your id for authorization, and dont tell it anyone"


@buys.get("/buys/{user_id}/receipts")
async def get_user_receipts_ids(user_id: int):
    if not authorized(user_id):
        return "User not found. Please, type your correct id or register in the system in /register/?id={your_id} URL"
    receipts = []
    cur.execute("select id from buys_receipts where user_id = %s", [user_id])
    for row in cur:
        receipts.append({"receipt_id": row[0]})
    if len(receipts) > 0:
        return receipts
    else:
        return "No receipts found"


@buys.delete("/buys/{user_id}/receipts/{receipt_id}")
async def delete_user_receipt(user_id: int, receipt_id: int):
    if not authorized(user_id):
        return "User not found. Please, type your correct id or register in the system in /register/?id={your_id} URL"
    cur.execute("delete from buys_receipts where id = %s and user_id=%s", (receipt_id, user_id))
    con.commit()
    return get_user_goods()


@buys.delete("/buys/{user_id}/receipts")
async def delete_all_user_receipts(user_id: int):
    if not authorized(user_id):
        return "User not found. Please, type your correct id or register in the system in /register/?id={your_id} URL"
    cur.execute("delete from buys_receipts where user_id=%s", [user_id])
    con.commit()
    return get_user_goods()


@buys.get("/buys/{user_id}/receipts/{receipt_id}")
async def get_user_receipt_goods(user_id: int, receipt_id: int):
    goods = []
    if not authorized(user_id):
        return "User not found. Please, type your correct id or register in the system in /register/?id={your_id} URL"
    cur.execute("select * from buys_receipts where id=%s and user_id=%s", (receipt_id, user_id))
    for row in cur:
        goods.append({"id": row[0], "shop_id": row[1], "shop_name": row[2], "buy_date": row[3], "good_name": row[4],
                      "amount": row[5], "categories": row[6]})
    if len(goods) != 0:
        return goods
    else:
        return "No goods found"


@buys.post("/buys/{user_id}/receipts/add_category")
async def add_good_category(user_id: int, good_id: int, category: str):
    cur.execute("update buys_receipts set categories[array_length(categories, 1) + 1] = %s where user_id=%s and "
                "good_id = %s", (category, user_id, good_id))
    con.commit()
    return "Category was successfully added"


@buys.get("/buys/{user_id}/goods")
async def get_user_goods(user_id: int, good_id: Optional[int] = None, good_name: Optional[str] = None,
                         category: Optional[str] = None):
    receipts = []
    if not authorized(user_id):
        return "User not found. Please, type your correct id or register in the system in /register/?id={your_id} " \
               "URL "
    cur.execute(
        "select * from buys_receipts where user_id = %s or good_id = %s or good_name = %s or array_to_string("
        "categories, ' ') = %s",
        (user_id, good_id, good_name, category))
    for row in cur:
        receipts.append(Receipt(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))
    if len(receipts) != 0:
        return receipts
    else:
        return "No goods found"
