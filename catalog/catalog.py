from db import db
from attributes import AttributeType
from util.neoutil import subreference, childnode, createnodes
from functools import partial

_get_catalogs_root = partial( subreference, "CATALOGS_ROOT", "CATALOGS" )

def _get_catalog(name):
    return childnode(_get_catalogs_root(), name, "CATALOG")

def _create_category(node, name):
    return childnode(node, name, "CATEGORY")

def _create_path(catalog_name, categories):
    with db.transaction:
       catalog = _get_catalog(catalog_name)
       createnodes(catalog, categories, "CATEGORY") 

def get_attributes(node):
    attributes_from_parent = [ a for r in node.relationships.incoming if r.type.name() == "CATEGORY" for a in get_attributes(r.start)]
    my_attributes = [(r.end, r)  for r in node.relationships.outgoing if r.type.name() == "ATTRIBUTE_TYPE" ]
    return attributes_from_parent + my_attributes

def _add_attribute(node, attribute, name = None, dflt = None, required = False):

    with db.transaction:
        current_attribute_names = [a[0]['name'] for a in get_attributes(node)]
        if attribute['name'] not in current_attribute_names:
            r = node.ATTRIBUTE_TYPE(attribute)
            r['Required'] = required
            r['Name'] = name if name is not None else attribute['name']
            r['DefaultValue'] = dflt

def is_leaf(node):
    leaf = True
    for r in node.relationships.outgoing:
        if r.type.name() == "CATEGORY":
            leaf = False
            break

    return leaf

class Catalog(object):

    def list(self, path = "/"):
        top_catalogs = []
        with db.transaction:
            catalogs_node = _get_catalogs_root()
            for r in catalogs_node.relationships.outgoing:
                relation_name = r.type.name()
                if relation_name == "CATALOG":
                    print "Got catalog with name:" , type(r.end['name'])
                    top_catalogs.append( "http://host:port/" + r.end['name'] )

        return top_catalogs

    def _search_in_children(self, start_node, paths):

        node = None

        if len(paths) == 0:
            return node

        for r in start_node.relationships.outgoing:
           relation_name = r.type.name()
           if (relation_name == "CATALOG" or relation_name == "CATEGORY") and r.end['name'] == paths[0]:
               if len(paths) == 1:
                   node = r.end
               else:
                   node = self._search_in_children(r.end, paths[1:])
               if node is not None:
                   break

        return node

    def get_node(self, path):
        paths = path.split("/")
        root = _get_catalogs_root()
        return self._search_in_children(root, paths)

    def create(self, path):
        print "path to put:", path
        data = path.split("/")
        catalog_name = data[0]
        categories = data[1:]
        _create_path(catalog_name, categories)
        return "Done"

    def add_attribute(self, node, attribute_type_name):
        attribute_type = AttributeType().get(attribute_type_name)
        _add_attribute(node, attribute_type)

    def get_attributes(self, node):
        return [a[0]['name'] for a in get_attributes(node)]

