from db import db
from util.neoutil import subreference, childnode

def _get_attributes_root():
    return subreference("ATTRIBUTE_TYPES_ROOT", "ATTRIBUTE_TYPES")

def _get_attributes():
    attributes_root = _get_attributes_root()
    return [r.end for r in attributes_root.relationships.outgoing if r.type.name() == "ATTRIBUTE_TYPE"]

def _create_attribute(name, typ):

    attributes_root = _get_attributes_root()
    attribute = childnode(attributes_root, name, "ATTRIBUTE_TYPE", type=typ)
    return attribute

class AttributeType(object):

    @classmethod
    def list(self):
        attributes = None
        with db.transaction:
            attributes = _get_attributes()
        return [ (a['name'], a['type']) for a in attributes]

    @classmethod
    def create(cls, name, typ):
        attribute = None
        with db.transaction:
            attribute = _create_attribute(name, typ)
        return AttributeType(name)

    def __init__(self, name):
        self.attribute = None
        with db.transaction:
            attributes = _get_attributes()
            for a in attributes:
                if a['name'] == name:
                    self.attribute = a
                    break

    def __getitem__(self, key):
        return self.attribute[key]

    def node(self):
        return self.attribute
