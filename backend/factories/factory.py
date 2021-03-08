import psycopg2

con = psycopg2.connect(
    database='backend_rtu',
    user='postgres',
    password='admin',
    host='127.0.0.1',
    port=5432
)
cur = con.cursor()

class Good:
    def __init__(self, shop_id, shop_name, name, description, amount, categories, id, amount_in_warehouse):
        self.shop_id = shop_id
        self.shop_name = shop_name
        self.name = name
        self.description = description
        #self.price = price
        self.amount = amount
        self.categories = categories
        self.id = id
        self.amount_in_warehouse = amount_in_warehouse


def shop_found(shop_id):
    cur.execute("select * from shops where shops.id=%s", [shop_id])
    shps = cur.fetchall()
    if shps is None or len(shps) == 0:
        return False
    else:
        return True


def factory_found(factory_name):
    cur.execute("select * from shops where shops.id=%s", [factory_name])
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
        good_object = Good(row[0], row[1], row[2], row[3], row[5], row[6], row[7], row[8])
        return good_object


class Factory:
    def __init__(self, name, perfomance):
        self.name = name
        self.perfomance = perfomance

    # def deliver_good_to_shop(self, shop_id, shop_name, good_name, good_description, good_categories, good_id):
    #     if not shop_found(shop_id):
    #         return "Shop not found"
    #     if get_shop_good(shop_id, good_id) == "No good found":
    #         cur.execute("insert into shops_goods values(%s, %s, %s, %s, %s, %s, %s, %s)", (shop_id, shop_name, good_name, good_description, None, self.perfomance, good_categories, good_id))
    #     else:
    #         cur.execute("update shops_goods set amount = amount + %s where shop_id = %s and id = %s", (self.perfomance, shop_id, good_id))
    #
    #
    # def store_good_in_warehouse(self, shop_id, shop_name, good_name, good_description, good_categories, good_id):
    #     if self.get_good_from_warehouse(good_id, shop_id) == "No good found":
    #         cur.execute("insert into factories_goods values(%s, %s, %s, %s, %s, %s, %s, %s)", (
    #         self.name, shop_id, shop_name, good_name, good_description, None, self.perfomance, good_categories, good_id))
    #     else:
    #         cur.execute("update factories_goods set good_amount = good_amount + %s where shop_id = %s and good_id = %s and factory_name = %s",
    #                     (self.perfomance, shop_id, good_id, self.name))
    #
    #
    # def get_good_from_warehouse(self, good_id, shop_id):
    #     cur.execute("select * from factories_goods where good_id = %s and shop_id = %s and factory_name = %s", (good_id, shop_id, self.name))
    #     for row in cur:
    #         if row[1] == shop_id and row[7] == good_id:
    #             return Good(row[1], row[2], row[3], row[4], row[5], row[6], row[7])
    #     return "No good found"
    def deliver_good_to_shop(self, shop_id, shop_name, good_name, good_description, good_categories, good_id):
        if not shop_found(shop_id):
            return "Shop not found"
        good = get_shop_good(shop_id, good_id)
        if good == "No good found":
            cur.execute("insert into shops_goods values(%s, %s, %s, %s, 0, %s, %s, %s, 0)", (shop_id, shop_name, good_name, good_description, self.perfomance, good_categories, good_id))
            con.commit()
        else:
            if good.amount_in_warehouse - self.perfomance >= 0:
                cur.execute("update shops_goods set amount = amount + %s, amount_in_warehouses = amount_in_warehouses - %s where shop_id = %s and id = %s", (self.perfomance, self.perfomance, shop_id, good_id))
                con.commit()
            else:
                cur.execute("update shops_goods set amount = amount + %s where shop_id = %s and id = %s", (self.perfomance, shop_id, good_id))
                con.commit()


    def store_good_in_warehouse(self, shop_id, shop_name, good_name, good_description, good_categories, good_id):
        if not shop_found(shop_id):
            return "Shop not found"
        if get_shop_good(shop_id, good_id) == "No good found":
            cur.execute("insert into shops_goods values(%s, %s, %s, %s, 0, 0, %s, %s, %s)", (shop_id, shop_name, good_name, good_description, good_categories, good_id, self.perfomance))
            con.commit()
        else:
            cur.execute("update shops_goods set amount_in_warehouses = amount_in_warehouses + %s where id = %s and shop_id = %s", (self.perfomance, good_id, shop_id))
            con.commit()


milk_factory = Factory("Danone", 3)
# milk_factory.deliver_good_to_shop(1, "Пятерочка", "Молоко", "Молоко компании Экомилк", ['Молоко', 'milk', 'Экомилк'], 4)
milk_factory.deliver_good_to_shop(2, "Дикси", "Сербская Брынза", "Сыр брынза сербская что еще непонятно", ['Сыр', 'молочные продукты'], 4)
#milk_factory.store_good_in_warehouse(2, "Дикси", "Сербская Брынза", "Сыр брынза сербская что еще непонятно", ['Сыр', 'молочные продукты'], 4)