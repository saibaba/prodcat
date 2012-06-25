import web

from catalog.catalog import Catalog
from catalog.attributes import AttributeType
from catalog.products import Product

class CatalogFE(object):
    def GET(self, path="/"):
        return Catalog.list(path)

    def PUT(self, path):
        return Catalog.create(path)

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

    catalogs = Catalog.list()
    print "Catalogs: " , catalogs

    master = Catalog.create("master", "Computer/Home/Desktop")

    AttributeType.create("Description", "String")
    AttributeType.create("Status", "String")
    print AttributeType.list()

    node = master.get_node("Computer")
    master.add_attribute(node, "Status")

    node = master.get_node("Computer/Home/Desktop")
    master.add_attribute(node, "Description")
    print master.get_attributes(node)

    product = Product.create("Multimedia Server 2", dict(Description="Multimedia Server for audio editing", Status="Inactive"), master, "Computer/Home/Desktop")

app = web.application(urls, globals())
if __name__ == "__main__":
    # use tornado wsgi app.run()
    test1()

