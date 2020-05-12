from dataclasses import dataclass

from graphviz import Digraph


@dataclass
class Leaf:
    byte: str
    count: int


@dataclass
class Node:
    left: Leaf
    right: Leaf
    count: int


def chunks(l, n):
    # https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    for i in range(0, len(l), n):
        yield l[i : i + n]


def build_tree(original):
    original_bytes = [b for b in bytearray(original.encode())]
    unique_bytes = set(original_bytes)

    def build_leaf(b):
        return Leaf(byte=b, count=original_bytes.count(b))

    nodes = [build_leaf(b) for b in unique_bytes]
    nodes.sort(key=lambda n: n.count, reverse=True)

    while True:
        node1 = nodes.pop()
        node2 = nodes.pop()
        nodes.append(Node(left=node1, right=node2, count=node1.count + node2.count))
        if len(nodes) == 1:
            break

    return nodes


def render_tree(nodes):
    dot = Digraph()

    def node_meta(node):
        if isinstance(node, Leaf):
            description = f"{node.byte}\n(n={node.count})"
        else:
            description = f"(n={node.count})"

        return str(id(node)), description

    def walk_tree(tree):
        if isinstance(tree, list):
            for t in tree:
                walk_tree(t)

        if isinstance(tree, Leaf):
            id, description = node_meta(tree)
            dot.node(id, description)

        if isinstance(tree, Node):
            id, description = node_meta(tree)
            dot.node(id, description)

            walk_tree(tree.left)
            left_id, __ = node_meta(tree.left)
            dot.edge(id, left_id, "0")

            walk_tree(tree.right)
            right_id, __ = node_meta(tree.right)
            dot.edge(id, right_id, "1")

    walk_tree(nodes)
    dot.render("test-output/round-table.gv", view=True)


def main():
    original_data = "abbcccc"
    tree = build_tree(original_data)
    print(tree)
    render_tree(tree)


if __name__ == "__main__":
    main()
