from db import db

from catalog import get_attributes, is_leaf
from util.neoutil import subreference

def get_products_root():
    return subreference('PRODUCTS_ROOT','PRODUCTS')

def _get_products():
    products_root = get_products_root()
    return [r.end for r in products_root.relationships.outgoing if r.type.name() == "PRODUCT"]

def get_product(name):
    products_root = get_products_root()
    product = None
    for r in products_root.relationships.outgoing:
        if r.type.name() == "PRODUCT" and r.end['name'] == name:
            product = r.end
            break

    return product

def create_product(name, attributes, catalog, category_path):

    product = None

    category = catalog.get_node(category_path)
    if not is_leaf(category):
        raise Exception("Category path %s does not point to leaf!" % (category_path,))

    category_attributes = get_attributes(category)

    product = get_product(name)

    if product is None:
        
        products_root = get_products_root()

        product = db.node(name=name)
        product.CATEGORY(category)
        products_root.PRODUCT(product)

        for ca in category_attributes:
            #attribute_type = ca[0]
            relation = ca[1]
            # TODO validate type
            # validate required
            product[relation['Name']] = attributes[relation['Name']]

    return product

class Product(object):

    @classmethod
    def list(cls):
        products = _get_products()
        return [ p['name'] for p in products]

    def __init__(self, name):
        self.product = None
        with db.transaction:
            products = _get_products()
            for p in products:
                if p['name'] == name:
                    self.product = p
                    break

    @classmethod
    def create(cls, name, attributes, catalog, category_path):
        with db.transaction:
            create_product(name, attributes, catalog, category_path)
        return Product(name)

