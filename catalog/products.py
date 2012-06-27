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
    def list(cls, category = None):
        if category is None:
            products = _get_products()
            return [ p for p in products]
        else:
            return Product._list_leaves(category)

    @classmethod
    def _list_leaves(cls, category):
        my_products = [ Product(rel.start['name']) for rel in category.get_node().relationships.incoming if rel.type.name() == "PRODUCT_CATEGORY" ]
        for child_category in category.child_categories():
            my_products  = my_products + Product.list(child_category)
        return my_products

    @classmethod
    def create(cls, name, attributes, catalog, category_path):
        with db.transaction:
            create_product(name, attributes, catalog, category_path)
        return Product(name)

    def __init__(self, name):
        self.node = None
        with db.transaction:
            products = _get_products()
            for p in products:
                if p['name'] == name:
                    self.node = p
                    break

    def get_category(self):
        for rel in self.node.relationships.outgoing:
            if rel.type.name() == "PRODUCT_CATEGORY" :
                return Catalog.Category(rel.end)

    def get_attributes(self):
        attributes = []
        for rel in self.node.relationships.outgoing:
            if rel.type.name() == "PRODUCT_CATEGORY" :
                attr_rels = self.get_category().get_attributes()
                for attr_rel in attr_rels:
                    attribute_type = attr_rel[0]
                    rel_for_attr = attr_rel[1]
                    attribute_value = self.node[rel_for_attr['Name']]
                    attributes.append( (attribute_type, rel_for_attr, attribute_value))
                break

        return attributes

    def is_modal(self):
        for a in self.get_attributes():
            if a[0]['type'] == "category_relationship":
                return True

        return False

    def __getitem__(self, key):
        return self.node[key]

    def enumerate(self):
        grv = {}
        rv = {}
        if not self.is_modal(): rv.append( self )

        for a in self.get_attributes():
            rel_name = a[1]['Name']
            print "Checking attribute:" , rel_name
            if a[0]['type'] == "category_relationship":
                print "Need to list products under category:" ,  a[2]
                category = self.get_category().get_catalog()
                print "...Need to list products under category:" ,  a[2]
                category  = category.get_category(a[2])
                print "got category...", category
                rv[rel_name] =  [ p.node['name'] for p in Product.list(category) ]
            else:
                grv[rel_name] =  rel_name

        return (grv, rv)
