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


def render_tree(node):
    dot = Digraph()

    def node_meta(n):
        if isinstance(n, Leaf):
            description = f"{chr(n.byte)}\n(n={n.count})"
        else:
            description = f"(n={n.count})"

        return str(id(n)), description

    def walk(n):
        if isinstance(n, Leaf):
            id, description = node_meta(n)
            dot.node(id, description)

        if isinstance(n, Node):
            id, description = node_meta(n)
            dot.node(id, description)

            walk(n.left)
            left_id, __ = node_meta(n.left)
            dot.edge(id, left_id, "0")

            walk(n.right)
            right_id, __ = node_meta(n.right)
            dot.edge(id, right_id, "1")

    walk(node)
    dot.render("data_compressor/render.gv", view=True)


class Compressor:
    @classmethod
    def build_tree(cls, original):
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

        return nodes[0]

    @classmethod
    def build_table(cls, node):
        lookup_table = {}

        def walk(n, path=[]):
            if isinstance(n, Leaf):
                lookup_table[n.byte] = path
            else:
                walk(n.left, path + [0])
                walk(n.right, path + [1])

        walk(node)
        return lookup_table

    @classmethod
    def compress(cls, original):
        tree = Compressor.build_tree(original)
        table = Compressor.build_table(tree)

        # We can use bin packing to represent an array of bits
        # and write it to file, which will represent the compressed
        # form of our data. We'll skip that step for now.
        for datum in original:
            key = ord(datum)
            bits = table[key]
            print(bits)


def main():
    original_data = "abbcccc"
    tree = Compressor.build_tree(original_data)
    render_tree(tree)
    Compressor.compress(original_data)


if __name__ == "__main__":
    main()
