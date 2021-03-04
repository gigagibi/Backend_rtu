import time

con = psycopg2.connect(
    database='backend_rtu',
    user='postgres',
    password='admin',
    host='127.0.0.1',
    port=5432
)
cur = con.cursor()

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


def shop_found(shop_id):
    cur.execute("select * from shops where shops.id=%s", [shop_id])
    shps = cur.fetchall()
    if shps is None or len(shps) == 0:
        return False
    else:
        return True


def get_shop_good(shop_id, good_id):
    if not shop_found(shop_id):
        return "Shop not found"
    cur.execute("select * from shops_goods where shop_id=%s and id=%s", (shop_id, good_id))
    row = cur.fetchone()
    if row is None or len(row) == 0:
        return "No good found"
    else:
        good_object = Good(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
        return good_object

class Factory:
    def __init__(self, name, perfomance):
        self.name = name
        self.perfomance = perfomance

    def deliver_good_to_shop(self, good, shop_id):
        if not shop_found(shop_id):
            return "Shop not found"
        if get_shop_good(shop_id, good.id) == "No good found":
            cur.execute("insert into shops_goods values(%s, %s, %s, %s, %s, %s, %s, %s)", (shop_id, good.shop_name, good.name, good.decsription, None, good.amount, good.categories, good.id))
        else:
            cur.execute("update shops_goods set amount = amount + %s where shop_id = %s and id = %s", (good.amount, shop_id, good.id))


    def store_good_in_warehouse(self, good, factory_name):
        if not shop_found(shop_id):
            return "Shop not found"
        if (get_factory_good(factory_name, good.id)):
            cur.execute("insert into factories_goods values(%s, %s, %s, %s, %s, %s, %s, %s)", (
            factory_name, good.shop_name, good.name, good.decsription, None, good.amount, good.categories, good.id))
        else:
            cur.execute("update factories_goods set amount = amount + %s where shop_id = %s and id = %s",
                        (good.amount, shop_id, good.id))

