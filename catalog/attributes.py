from db import db
from util.neoutil import subreference

def get_attributes_root():
    return subreference("ATTRIBUTE_TYPES_ROOT", "ATTRIBUTE_TYPES")

def get_attributes():
    attributes_root = get_attributes_root()
    return [r.end for r in attributes_root.relationships.outgoing if r.type.name() == "ATTRIBUTE_TYPE"]

def create_attribute(name, typ):

    attributes_root = get_attributes_root()

    attribute = None
    for r in attributes_root.relationships.outgoing:
        relation_name = r.type.name()
        if relation_name == "ATTRIBUTE_TYPE" and r.end['name'] == name:
            attribute = r.end
            break

    if attribute is None:
        attribute = db.node(name=name, type=typ)
        attributes_root.ATTRIBUTE_TYPE(attribute)

    return attribute

class AttributeType(object):

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

    def create(self, name, typ):
        attribute = None
        with db.transaction:
            attribute = create_attribute(name, typ)
        return attribute
