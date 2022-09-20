import datetime
import json

import requests
import configparser

from peewee import *
from playhouse.db_url import connect

config = configparser.ConfigParser()
config.read('pantry.ini')
config_db = config['Database']

pantry_db = connect(config_db['DBURL'])


def connectDB():
    pantry_db.connect(reuse_if_open=True)


def disconnectDB():
    pantry_db.close()


class BasePantryModel(Model):
    class Meta:
        database = pantry_db


##
# Product
##

class Product(BasePantryModel):
    upc = CharField(primary_key=True)
    brand = CharField()
    name = CharField()
    thumbnail = CharField()

    def __repr__(self):
        return self.toJSON()

    def toJSON(self):
        temp_dict = { "upc" : self.upc, "brand": self.brand, "name": self.name, "thumbnail": self.thumbnail }
        return json.dumps(temp_dict)


def remove_product(product_id):
    del_product = Product.get(Product.id == product_id)
    remove_msg = "Removed {} '{} {}'".format(del_product.upc, del_product.brand, del_product.name)
    del_product.delete_instance()
    return(remove_msg)


def get_products():
    products = [x for x in Product.select().order_by(Product.brand)]
    products.sort(key=lambda item: item.name)
    return products


def retrieve_and_create_product(upc_value):
    print("UPC code is {}".format(upc_value))
    try:
        product_request = "http://world.openfoodfacts.org/api/v0/product/{}.json".format(upc_value)
        response = requests.get(product_request)
        data = response.json()
    except:
        return (False, "Error retrieving product data")

    try:
        brand = data['product']['brands']
    except KeyError:
        brand = "Unknown"

    try:
        name = data['product']['product_name']
    except KeyError:
        name = "Unknown" if brand != "Unknown" else ""

    try:
        kind = data['product']['category_properties']['ciqual_food_name:en']
    except KeyError:
        kind = ""

    try:
        thumbnail = data['product']['image_front_thumb_url']
    except KeyError:
        thumbnail = ""

    name = "{} {}".format(name, kind)
    product = Product.create(brand=brand, name=name, upc=upc_value, thumbnail=thumbnail)
    return product


##
# Pantry Item
##

class PantryItem(BasePantryModel):
    product = ForeignKeyField(Product, backref='items')
    id = BigAutoField(primary_key=True)
    storeDate = DateField(default=datetime.datetime.now)

def lookup_and_store_product(upc_value):
    try:
        product_record = Product.get(Product.upc == upc_value)
    except DoesNotExist:
        product_record = retrieve_and_create_product(upc_value=upc_value)

    pantry_item = PantryItem.create(product=product_record)
    return (True, product_record, "Added {} '{} {}'".format(upc_value, product_record.brand, product_record.name))

def remove_item(item_id):
    item_to_remove = PantryItem.get(id=item_id)
    item_name = item_to_remove.product.name
    item_brand = item_to_remove.product.brand
    item_to_remove.delete_instance()
    return (True, "Removed '{} {}'".format(item_brand, item_name))
