from db import db

def subreference(subrel_name, subnode_name):

    node = None

    r = db.reference_node.relationships.outgoing
    for ri in r:
        if ri.type.name() == subrel_name and ri.end['name'] == subnode_name:
            node =  ri.end
            break

    if node is None:
        node = db.node(name=subnode_name)
        db.reference_node.relationships.create(subrel_name, node)

    return node

def childnode(parent, node_name, rel_name):

    n = None
    for r in parent.relationships.outgoing:
        if r.type.name() == rel_name and node_name == r.end['name']:
            n = r.end
            break

    if n is None:
        n = db.node(name=node_name)
        parent.relationships.create(rel_name, n)

    return n
        
def createnodes(parent, node_names, rel_name):
    
    node = parent
    for node_name in node_names:
        node = childnode(node, node_name, rel_name)

    return None
