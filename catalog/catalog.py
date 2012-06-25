from db import db
from attributes import AttributeType
from util import has_matching
from util.neoutil import subreference, childnode, createnodes
from functools import partial

_get_catalogs_root = partial( subreference, "CATALOGS_ROOT", "CATALOGS" )

def _get_catalog(name):
    return childnode(_get_catalogs_root(), name, "CATALOG")

def _create_category(node, name):
    return childnode(node, name, "CATEGORY")

def _create_path(catalog_name, categories):
    node  = None
    with db.transaction:
       catalog = _get_catalog(catalog_name)
       node = createnodes(catalog, categories, "CATEGORY") 
    return node

def get_attributes(node):
    attributes_from_parent = [ a for rel in node.relationships.incoming if rel.type.name() == "CATEGORY" for a in get_attributes(rel.start)]
    my_attributes = [(rel.end, rel)  for rel in node.relationships.outgoing if rel.type.name() == "ATTRIBUTE_TYPE"]
    return attributes_from_parent + my_attributes

def _add_attribute(node, attribute, name = None, dflt = None, required = False, final = False):

    with db.transaction:
        current_attribute_names = [a[0]['name'] for a in get_attributes(node)]
        if attribute['name'] not in current_attribute_names:
            rel_name = name if name is not None else attribute['name']
            node.ATTRIBUTE_TYPE(attribute.node(), Required=required,Name=rel_name,DefaultValue=dflt, Final=final)

def is_leaf(node):
    return not has_matching(node.relationships.outgoing, lambda rel: rel.type.name() == "CATEGORY")

class Catalog(object):

    @classmethod
    def list(cls):
        top_catalogs = []
        with db.transaction:
            catalogs_node = _get_catalogs_root()
            for rel in catalogs_node.relationships.outgoing:
                if rel.type.name() == "CATALOG":
                    print "Got catalog with name:" , type(rel.end['name'])
                    top_catalogs.append( "http://host:port/" + rel.end['name'] )

        return top_catalogs

    @classmethod
    def create(cls, catalog_name, categories_path = None):
        categories = categories_path.split("/") if categories_path is not None else []
        _create_path(catalog_name, categories)
        return Catalog(catalog_name)

    def __init__(self, catalog_name):
        self.catalog_node = None
        self.catalog_name = catalog_name
        root = _get_catalogs_root()
        for rel in root.relationships.outgoing:
            if rel.type.name() == "CATALOG" and rel.end['name'] == catalog_name:
                self.catalog_node = rel.end
                break

        if self.catalog_node is None:
            raise Exception("Named catalog does not exist: %s" % (catalog_name,) )

    def _search_in_children(self, start_node, paths):

        node = None

        if len(paths) == 0:
            return node

        for rel in start_node.relationships.outgoing:
           relation_name = rel.type.name()
           if (relation_name == "CATALOG" or relation_name == "CATEGORY") and rel.end['name'] == paths[0]:
               if len(paths) == 1:
                   node = rel.end
               else:
                   node = self._search_in_children(rel.end, paths[1:])
               if node is not None:
                   break

        return node

    def create_categories(self, categories_path):
        categories = categories_path.split("/")
        return _create_path(self.catalog_name, categories)

    def get_node(self, categories_path):
        paths = categories_path.split("/")
        return self._search_in_children(self.catalog_node, paths)

    def add_attribute(self, node, attribute_type_name):
        attribute_type = AttributeType(attribute_type_name)
        _add_attribute(node, attribute_type)

        return attribute_type

    def get_attributes(self, node):
        return [a[0]['name'] for a in get_attributes(node)]

