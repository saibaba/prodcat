from db import db

from catalog import Catalog
from util.neoutil import subreference

def _get_products_root():
    return subreference('PRODUCTS_ROOT','PRODUCTS')

def _get_products():
    products_root = _get_products_root()
    return [r.end for r in products_root.relationships.outgoing if r.type.name() == "PRODUCT"]

def _get_product(name):
    products_root = _get_products_root()
    product = None
    for r in products_root.relationships.outgoing:
        if r.type.name() == "PRODUCT" and r.end['name'] == name:
            product = r.end
            break

    return product

def create_product(name, attributes, catalog, category_path):

    product = None

    category = catalog.get_category(category_path)
    if not category.is_leaf():
        raise Exception("Category path %s does not point to leaf!" % (category_path,))

    category_attributes = category.get_attributes()

    product = _get_product(name)

    if product is None:
        
        products_root = _get_products_root()

        product = db.node(name=name)
        product.PRODUCT_CATEGORY(category.get_node())
        products_root.PRODUCT(product)

        for ca in category_attributes:
            #attribute_type = ca[0]
            relation = ca[1]
            # TODO validate type
            # validate required
            attribute_value = attributes[relation['Name']]
            product[relation['Name']] = attribute_value
            attribute_type = ca[0]
            if attribute_type['type'] == "category_relationship":
                rel_category = catalog.get_category(attribute_value)
                product.relationships.create(relation['Name'], rel_category.get_node()) 

    return product

class Product(object):

    @classmethod
    def list(cls):
        products = _get_products()
        return [ p['name'] for p in products]

    @classmethod
    def create(cls, name, attributes, catalog, category_path):
        with db.transaction:
            create_product(name, attributes, catalog, category_path)
        return Product(name)

    def __init__(self, name):
        self.product = None
        with db.transaction:
            products = _get_products()
            for p in products:
                if p['name'] == name:
                    self.product = p
                    break

    def get_attributes(self):
        attributes = None
        for rel in self.product.relationships.outgoing:
            if rel.type.name() == "PRODUCT_CATEGORY" :
                attributes = Catalog.get_category(rel.end['name'])

        return attributes

    def is_modal(self):
        for a in self.get_attributes():
            if a[0]['type'] == "category_relationship":
                return True

        return False

