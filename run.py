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
    AttributeType.create("Processor", "category_relationship")

    print AttributeType.list()

    computer = master.get_node("Computer")
    master.add_attribute(computer, "Status")
    master.add_attribute(computer, "Processor")

    master.create_categories("Processors/Intel")
    Product.create("Core Duo i5", dict(Description="i5 processor"), master, "Processors/Intel")

    desktop = master.get_node("Computer/Home/Desktop")
    master.add_attribute(desktop, "Description")
    print master.get_attributes(desktop)

    Product.create("Multimedia Server 1", dict(Description="Multimedia Server for video editing", Status="Active", Processor="Processors/Intel"), master, "Computer/Home/Desktop")
    Product.create("Multimedia Server 2", dict(Description="Multimedia Server for audio editing", Status="Inactive", Processor="Processors/Intel"), master, "Computer/Home/Desktop")

app = web.application(urls, globals())
if __name__ == "__main__":
    # use tornado wsgi app.run()
    test1()

