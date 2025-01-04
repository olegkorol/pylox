from app.grammar.expressions import ExprVisitor, Expr, Grouping, Binary, Unary, Literal
from app.utils import pretty_print

class AstPrinter(ExprVisitor):
    """
    This class is an implementation of the visitor interface.
    It is used to print an AST in a human-readable Lisp-like format.
    """
    def print(self, expr: Expr) -> str:
        return expr.accept(self)
    
    def visit_binary(self, expr: Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping(self, expr: Grouping) -> str:
        return self._parenthesize('group', expr.expression)

    def visit_literal(self, expr: Literal) -> str:
        if expr.value == None:
            return 'nil'
        if isinstance(expr.value, bool):
            return pretty_print(expr.value)
        return str(expr.value)

    def visit_unary(self, expr: Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        parts = [name]
        for expr in exprs:
            parts.append(expr.accept(self))
        # print(f"-> {parts}")
        return f'({" ".join(parts)})'