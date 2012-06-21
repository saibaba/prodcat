from db import db

from catalog import Catalog, get_attributes, is_leaf

def get_products_root():
    products  = None
    r = db.reference_node.relationships.outgoing
    for ri in r:
        relation_name = ri.type.name()
        if relation_name == 'PRODUCTS_ROOT' and ri.end['name'] == "PRODUCTS": products = ri.end

    if products is None:
        print "No PRODUCTS node, creating one..."
        products = db.node(name="PRODUCTS")
        db.reference_node.PRODUCTS_ROOT(products)

    return products

def get_products():
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

def create_product(name, attributes, category_path):

    product = None

    category = Catalog().get_node(category_path)
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

    def list(self):
        attributes = None
        with db.transaction:
            attributes = get_attributes()
        return [ (a['name'], a['type']) for a in attributes]

    def get(self, name):
        attribute = None
        with db.transaction:
            attributes = get_attributes()
            for a in attributes:
                if a['name'] == name:
                    attribute = a
                    break

        return attribute

    def create(self, name, attributes, category_path):
        product = None
        with db.transaction:
            product = create_product(name, attributes, category_path)
        return product
