from db import db

def get_attributes_root():
    attributes  = None
    r = db.reference_node.relationships.outgoing
    for ri in r:
        relation_name = ri.type.name()
        print "root has rel:" , relation_name
        if relation_name == 'ATTRIBUTE_TYPES_ROOT' and ri.end['name'] == "ATTRIBUTE_TYPES": attributes = ri.end

    if attributes is None:
        print "No ATTRIBUTE_TYPES node, creating one..."
        attributes = db.node(name="ATTRIBUTE_TYPES")
        db.reference_node.ATTRIBUTE_TYPES_ROOT(attributes)

    return attributes

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
