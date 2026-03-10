from tree_sitter import Language, Parser, QueryCursor, Query
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
                    parameters: (parameter_list
                        (parameter_declaration
                            type: (primitive_type)
                            declarator: (identifier)
                        )
                    )*
                )

                body: (compound_statement
                    (statement
                        (call_expression
                            function: (identifier) @called
                            (#any-of? @called 
                                "_pdep_u64"
                            )
                        )
                    )
                )
            ) @functions
            """,
        )

    def filter(self, code: str) -> Result[bool, str]:
        tree = self.parser.parse(bytes(code, "utf8"))
        cursor = QueryCursor(self.query)
        captures = cursor.captures(tree.root_node)
        return Ok("functions" in captures)
