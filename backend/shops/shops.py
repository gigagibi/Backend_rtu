import datetime
from fastapi import FastAPI
import psycopg2
import random
import time

# error_flag = True
# while error_flag:
#     try:
#         con = psycopg2.connect(
#             database='backend_rtu',
#             user='postgres',
#             password='admin',
#             host='127.0.0.1',
#             port=5432
#         )
#     except psycopg2.OperationalError:
#         print('Error')
#         continue
#     else:
#         error_flag = False


# time.sleep(25)
con = psycopg2.connect(
    database='backend_rtu',
    user='postgres',
    password='admin',
    host='0.0.0.0',
    port=5432
)

cur = con.cursor()
shops = FastAPI()


# con = []
# cur = []

class User:
    def __init__(self, user_id, cart):
        self.user_id = user_id
        self.cart = cart


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


class Shop:
    def __init__(self, id, name, address, phone_number):
        self.id = id
        self.name = name
        self.address = address
        self.phone_number = phone_number


class Cart:
    def __init__(self, id, user_id, good_id, purchased_amount, shop_id):
        self.id = id
        self.user_id = user_id
        self.good_id = good_id
        self.purchased_amount = purchased_amount
        self.shop_id = shop_id


# поиск магазина
def shop_found(shop_id):
    cur.execute("select * from shops where shops.id=%s", [shop_id])
    shps = cur.fetchall()
    if shps is None or len(shps) == 0:
        return False
    else:
        return True


# проверяет, существует ли пользователь с данным id (не endpoint)
def authorized(user_id):
    cur.execute("select id from buys_users where id = %s", [user_id])
    idd = cur.fetchone()
    if idd is None:
        return False
    else:
        return True


# получение id всех чеков (не endpoint)
def get_receipts_ids():
    cur.execute("select id from buys_receipts")
    return cur.fetchall()


# проверяет, существует ли чек (не endpoint)
def find_in_receipts(receipt_id):
    receipts_ids = get_receipts_ids()
    for id in receipts_ids:
        if id == receipt_id:
            return True
    return False


# получение id всех корзин (не endpoint)
def get_carts_ids():
    cur.execute("select id from shops_cart")
    return cur.fetchall()


# проверяет, существует ли корзина (не endpoint)
def find_in_carts(cart_id):
    carts_ids = get_carts_ids()
    for id in carts_ids:
        if id == cart_id:
            return True
    return False


# метод получения всех магазинов
@shops.get("/shops")
async def get_shops():
    shps = []
    cur.execute("select * from shops")
    for row in cur:
        shop_object = Shop(row[0], row[1], row[2], row[3])
        shps.append(shop_object)
    if cur.fetchall() is not None:
        return shps
    else:
        return "No shops"


# метод поиска магазина по id
@shops.get("/shops/{shop_id}")
async def get_shop(shop_id: int):
    cur.execute("select * from shops where shops.id=%s", [shop_id])
    row = cur.fetchone()
    if row is not None:
        shop_object = Shop(row[0], row[1], row[2], row[3])
        return shop_object
    else:
        return "Shop not found"


# метод для получения товаров из магазина (не endpoint, вызывается в async endpoint методе)
def gsgs(shop_id):
    cur.execute("select * from shops where shops.id=%s", [shop_id])
    shps = cur.fetchall()
    if shps is None or len(shps) == 0:
        return "No shop found"
    goods = []
    cur.execute("select * from shops_goods where shop_id = %s",
                [shop_id])
    for row in cur:
        goods.append(Good(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
    if cur.fetchall() is not None:
        return goods
    else:
        return "No goods in this shop"


# метод для получения товаров из магазина
@shops.get("/shops/{shop_id}/goods")
async def get_shop_goods(shop_id: int):
    return gsgs(shop_id)


# метод для получения товара из магазина (не endpoint, вызывается в async endpoint методе)
def gsg(shop_id, good_id):
    if not shop_found(shop_id):
        return "Shop not found"
    cur.execute("select * from shops_goods where shop_id=%s and id=%s", (shop_id, good_id))
    row = cur.fetchone()
    if row is None or len(row) == 0:
        return "No good found"
    else:
        good_object = Good(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
        return good_object


# метод для получения товара из магазина
@shops.get("/shops/{shop_id}/goods/{good_id}")
async def get_shop_good(shop_id: int, good_id: int):
    return gsg(shop_id, good_id)


# метод для получения пользовательской корзины из магазина (не endpoint, вызывается в async endpoint методе)
def gcfs(shop_id, user_id):
    if not authorized(user_id):
        return "User not found. Please, type your correct id or register in the system in /register/?id={your_id} URL"
    if not shop_found(shop_id):
        return "Shop not found"
    cart_dict = {}
    cur.execute("select * from shops_cart where user_id=%s and shop_id = %s", (user_id, shop_id))
    row = cur.fetchall()
    cart = []
    if row is not None:
        for r in row:
            cart_object = Cart(r[0], r[1], r[2], r[3], r[4])
            cart.append(cart_object)
        return cart
    else:
        return "No cart found"


# метод для получения пользовательской корзины из магазина
@shops.get("/shops/{shop_id}/cart")
async def get_cart_from_shop(shop_id: int, user_id: int):
    return gcfs(shop_id, user_id)


# метод для удаления корзины пользователя
@shops.delete("/shops/{shop_id}/goods/{good_id}/delete_cart")
async def clear_cart(user_id: int, shop_id):
    if not authorized(user_id):
        return "User not found. Please, type your correct id or register in the system in /register/?id={your_id} URL"
    if not shop_found(shop_id):
        return "Shop not found"
    cur.execute("delete from shops_cart where user_id = %s and shop_id = %s", (user_id, shop_id))
    con.commit()


# метод для добавления товара в корзину пользователя
@shops.post("/shops/{shop_id}/goods/{good_id}/add_to_cart")
async def add_good_to_cart(shop_id: int, good_id: int, user_id: int, purchased_amount: int):
    if not authorized(user_id):
        return "User not found. Please, type your correct id or register in the system in /register/?id={your_id} URL"
    if not shop_found(shop_id):
        return "Shop not found"
    good_object = gsg(shop_id, good_id)
    if good_object == "No good found" or good_object == "No shop found":
        return good_object
    if good_object.amount - purchased_amount > 0:
        generated_cart_id = random.randint(0, 2000000000)
        while find_in_carts(generated_cart_id):
            generated_cart_id = random.randint(0, 2000000000)
        cart_goods = get_goods_from_cart(shop_id, user_id)
        good_is_in_cart = False
        if cart_goods == "No cart found" or cart_goods == "Shop not found" or cart_goods == "User not found. Please, type your correct id or register in the system in /register/?id={your_id} URL":
            return cart_goods
        for good in cart_goods[0]:
            if good.id == good_id:
                good_is_in_cart = True
                break
        if not good_is_in_cart:
            cur.execute("insert into shops_cart values(%s, %s, %s, %s, %s)",
                        (generated_cart_id, user_id, good_id, purchased_amount, shop_id))
            con.commit()
        else:
            cur.execute("update shops_cart set purchased_amount = purchased_amount + %s where good_id = %s and user_id "
                        "= %s and shop_id = %s", (purchased_amount, good_id, user_id, shop_id))
            con.commit()
        return "Good was added to your cart"
    else:
        return "Not enough goods in shop"


# метод для получения товаров из корзины пользователя (не endpoint, вызывается в sync endpoint методе)
def get_goods_from_cart(shop_id, user_id):
    if not authorized(user_id):
        return "User not found. Please, type your correct id or register in the system in /register/?id={your_id} URL"
    if not shop_found(shop_id):
        return "Shop not found"
    cart = gcfs(shop_id, user_id)
    if cart == "No cart found":
        return cart
    goods = []
    goods_purchased_amount = []
    for cart_row in cart:
        goods.append(gsg(shop_id, cart_row.good_id))
        goods_purchased_amount.append(cart_row.purchased_amount)
    return [goods, goods_purchased_amount]


# метод для покупки товаров из корзины
@shops.post("/shops/{shop_id}/buy_cart")
async def buy_cart(shop_id: int, user_id: int, payed_by_card: bool):
    if not authorized(user_id):
        return "User not found. Please, type your correct id or register in the system in /register/?id={your_id} URL"
    if not shop_found(shop_id):
        return "Shop not found"
    generated_receipt_id = random.randint(0, 2000000000)
    while find_in_receipts(generated_receipt_id):
        generated_receipt_id = random.randint(0, 2000000000)
    goods = get_goods_from_cart(shop_id, user_id)
    for i in range(0, len(goods[0])):
        cur.execute("insert into buys_receipts values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (
            generated_receipt_id, shop_id, goods[0][i].shop_name, datetime.datetime.now(), goods[0][i].name,
            goods[1][i],
            goods[0][i].categories, goods[0][i].id, user_id, payed_by_card))
        con.commit()
    cur.execute("delete from shops_cart where shop_id=%s and user_id=%s", (shop_id, user_id))
    con.commit()
    return "You've buyed all goods from your cart"
