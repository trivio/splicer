from splicer import Field, Schema
from splicer.adapters import Adapter
from splicer.ast import *
from splicer.codecs import schema_from_path
from splicer.compilers.local import relational_function  # type: ignore
from splicer.path import columns, pattern_regex, regex_str, tokenize_pattern


class DirAdapter(Adapter):
    def __init__(self, **relations):
        self._relations = {
            name: FileTable(name, **args) for name, args in relations.items()
        }

    @property
    def relations(self):
        return [(name, relation.schema) for name, relation in self._relations.items()]

    def schema(self, name):
        relation = self.get_relation(name)
        if relation.schema:
            return relation.schema
        elif relation.decode != "none":
            # todo: do the same thing as evaluate up to the point where we
            # list files
            return extract_expr_tree(relation)

    def get_relation(self, name):
        return self._relations.get(name)

    def table_scan(self, name, ctx):
        return self._relations.get(name)

    def has(self, name):
        return self._relations.has_key(name)

    def evaluate(self, loc):
        relation = self._relations[loc.node().name]

        op = Function("files", Const(relation.root_dir))

        if relation.pattern:
            loc = rewrite_tree(
                relation.path_schema.field_map.keys(),
                loc.replace(
                    Function(
                        "extract_path", op, Const(relation.root_dir + relation.pattern)
                    )
                ),
            )

        else:
            loc = loc.relpace(op)

        if relation.content_column:
            loc = loc.replace(
                Function("contents", loc.node(), Const(relation.content_column))
            )

        if relation.decode != "none":
            loc = loc.replace(
                Function(
                    "decode",
                    loc.node(),
                    Const(relation.decode),
                    Const(relation.schema),
                    Const("path"),
                )
            )

        return loc.leftmost_descendant()


class FileTable(object):
    def __init__(self, name, root_dir, **options):
        self.name = name

        if not root_dir.endswith("/"):
            root_dir += "/"
        self.root_dir = root_dir

        self.pattern = options.pop("pattern", None)

        if self.pattern:
            tokens = tokenize_pattern(self.pattern)
            self.path_schema = Schema(
                [Field(name=c, type="STRING") for c in columns(tokens)]
            )

        self.content_column = options.pop("content_column", None)
        self.filename_column = options.pop("filename_column", None)

        self.decode = options.pop("decode", "none")

        schema = options.pop("schema", None)
        if isinstance(schema, Schema):
            self.schema = schema
        else:
            self.schema = schema and Schema(**schema)

        if options:
            raise ValueError("Unrecognized options {}".format(options.keys()))


def extract_expr_tree(relation):
    op = Function("files", Const(relation.root_dir))

    if relation.pattern:
        return Function("extract_path", op, Const(relation.root_dir + relation.pattern))
    else:
        return op


def rewrite_tree(partioned_fields, query_loc):

    current = query_loc.node()
    loc = query_loc

    changes = []
    while True:
        next_loc = loc.ancestor(lambda l: isinstance(l.node(), SelectionOp))
        if next_loc is None:
            break
        else:
            loc = next_loc

        sel_op = loc.node()
        record_filter, key_filter = rewrite_bool_op(partioned_fields, sel_op.bool_op)

        if key_filter:
            changes.append(key_filter)
            if record_filter:
                loc = loc.replace(sel_op.new(bool_op=record_filter))
            else:
                # remove the sel_op
                loc = loc.replace(loc.down().node())

    loc = loc.find(lambda l: l.node() is current)
    assert loc, "Could not restore location"  # should never happen

    if changes:
        bool_op = changes.pop(0)
        while changes:
            bool_op = And(bool_op, changes.pop(0))

        return loc.replace(SelectionOp(current, bool_op))
    else:
        return loc


def rewrite_bool_op(partioned_fields, bin_op):
    bin_type = type(bin_op)

    if bin_type == And:
        recordfilter, keyfilter = rewrite_and_op(partioned_fields, bin_op)
    elif bin_type == Or:
        recordfilter, keyfilter = rewrite_or_op(partioned_fields, bin_op)
    elif issubclass(bin_type, BinaryOp):
        recordfilter, keyfilter = rewrite_binary_op(partioned_fields, bin_op)
    else:
        recordfilter = bin_op
        keyfilter = None
    return recordfilter, keyfilter


def is_partitionable(partioned_fields, op):
    """
    Returns true if the operation only uses variables from the key names
    and constants otherwise false
    """

    t = type(op)
    if t == Var:
        return op.path in partioned_fields
    elif t == Function:
        # all function args have to be partitionable
        return all(is_partitionable(partioned_fields, a) for a in op.args)
    elif t == Tuple:
        # all elements must be partitionable
        return all(is_partitionable(partioned_fields, e) for e in op.exprs)
    elif issubclass(t, Const):
        return True
    elif issubclass(t, BinaryOp):
        return all(is_partitionable(partioned_fields, e) for e in (op.lhs, op.rhs))
    else:
        raise RuntimeError("Can't determine if type %s is partitionable." % t)


def rewrite_binary_op(partioned_fields, op):
    if all(is_partitionable(partioned_fields, e) for e in (op.lhs, op.rhs)):
        return None, op
    else:
        return op, None


def rewrite_and_op(partioned_fields, op):
    def combine(exprs):
        l = len(exprs)
        if l == 0:
            return None
        elif l == 1:
            return exprs[0]
        else:
            return And(*exprs)

    lhs = rewrite_bool_op(partioned_fields, op.lhs)
    rhs = rewrite_bool_op(partioned_fields, op.rhs)

    return [combine(list(filter(None, exprs))) for exprs in zip(lhs, rhs)]


def rewrite_or_op(partioned_fields, op):
    rewrite = partial(rewrite_bool_op, partioned_fields)

    record_exprs, key_exprs = [
        filter(None, exprs) for exprs in zip(rewrite(op.lhs), rewrite(op.rhs))
    ]

    if len(record_exprs) == 0:
        l = len(key_exprs)
        if l == 1:
            return None, key_exprs[0]
        else:
            # this assumes keyexprs should be exactly 2
            return None, Or(*key_exprs)

    else:  # no benifit from using the key filter
        return op, None
