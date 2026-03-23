from tree_sitter import Language, Parser, QueryCursor, Query, Node
import tree_sitter_c as ts_c

from .code_filter import CodeFilter
from ...utils.result import Result, Ok


class TreesitterCodeFilter(CodeFilter):
    def __init__(self, args) -> None:
        super().__init__(args)
        self.lang = Language(ts_c.language())
        self.parser = Parser(self.lang)
        self.query = Query(
            self.lang,
            """
            (function_definition
                type: (primitive_type)

                declarator: (function_declarator
                    declarator: (identifier)
                    parameters: (parameter_list) @parameters
                )
            ) @functions
            """,
        )

    def filter(self, code: str, item) -> Result[bool, str]:
        source_bytes = code.encode("utf8")
        tree = self.parser.parse(source_bytes)
        cursor = QueryCursor(self.query)
        matches = cursor.matches(tree.root_node)

        for _, captures in matches:
            parameters = captures.get("parameters") or []
            functions = captures.get("functions") or []

            if len(parameters) != 1 or len(functions) != 1:
                continue

            if self._is_parameters_all_primative(parameters[0]) and self._calls_intrinsic(
                functions[0], item.name
            ):
                return Ok(True)
        return Ok(False)

    def _calls_intrinsic(self, node: Node, intrinsic: str) -> bool:
        if node.type == "call_expression":
            fn = node.child_by_field_name("function")
            if (
                fn
                and fn.type == "identifier"
                and fn.text
                and fn.text.decode() == intrinsic
            ):
                return True
        return any(self._calls_intrinsic(child, intrinsic) for child in node.children)

    def _is_parameters_all_primative(self, node: Node) -> bool:
        assert node.grammar_name == "parameter_list"

        for child in node.children:
            if child.grammar_name != "parameter_declaration":
                continue
            if not self._is_parameter_declaration_primative(child):
                return False

        return True

    def _is_parameter_declaration_primative(self, node: Node) -> bool:
        assert node.grammar_name == "parameter_declaration"

        type_node = node.child_by_field_name("type")
        declarator_node = node.child_by_field_name("declarator")

        return (
            type_node is not None
            and type_node.type == "primitive_type"
            and declarator_node is not None
            and declarator_node.type == "identifier"
        )

    def print_node(self, node: Node, depth: int = 0):
        print(" " * depth, node.type)
        for child in node.children:
            self.print_node(child, depth + 2)

    def build_intrinsic_list(self) -> str:
        return "".join(f'"{intrin}"\n' for intrin in self.args.intrinsics)
