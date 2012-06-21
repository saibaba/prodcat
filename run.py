import web

from catalog.catalog import Catalog
from catalog.attributes import AttributeType
from catalog.products import Product

class CatalogFE(object):
    def GET(self, path="/"):
        return Catalog().list(path)

    def PUT(self, path):
        return Catalog().create(path)

class AttributeTypeFE(object):
    def GET(self):
        return AttributeType().list()

    def POST(self):
        pass

class Manage(object):
    def GET(self):
        exit(0)

urls = (
    '/halt', 'Manage',
    '/catalog', 'CatalogFE',
    '/catalog/(.+)', 'CatalogFE',
    '/attribute_types', 'AttributeTypeFE',
    '/attribute_types/(.+)', 'AttributeTypeFE',
)


def test1():

    catalog = Catalog()
    catalogs = catalog.list()
    print "Catalogs: " , catalogs

    catalog.create("master/Computer/Home/Desktop")

    attribute_type = AttributeType()
    attribute_type.create("Description", "String")
    attribute_type.create("Status", "String")
    print attribute_type.list()

    node = catalog.get_node("master/Computer")
    catalog.add_attribute(node, "Status")

    node = catalog.get_node("master/Computer/Home/Desktop")
    catalog.add_attribute(node, "Description")
    print catalog.get_attributes(node)

    product = Product()
    product.create("Multimedia Server 2", dict(Description="Multimedia Server for audio editing", Status="Inactive"), "master/Computer/Home/Desktop")

app = web.application(urls, globals())
if __name__ == "__main__":
    # use tornado wsgi app.run()
    test1()

