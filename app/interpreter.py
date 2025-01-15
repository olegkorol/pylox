from typing import Any
from app.types import TokenType, Token
from app.utils import pretty_print, LoxRuntimeError
from app.grammar.expressions import Assign, Expr, Grouping, Binary, Logical, Unary, Literal, ExprVisitor, Variable
from app.grammar.statements import Stmt, Print, Expression, StmtVisitor, Var, Block, If
from app.environment import Environment

class Interpreter(ExprVisitor, StmtVisitor):
	_environment = Environment()

	def interpret(self, statements: list[Stmt]) -> Any:
		for statement in statements:
			self.execute(statement)

	# def interpret_expr(self, expr: Expr) -> None:
	# 	value = self.evaluate(expr)
	# 	print(self._stringify(value))

	def evaluate(self, expr: Expr) -> Any:
		return expr.accept(self)
	
	def execute(self, stmt: Stmt) -> Any:
		stmt.accept(self)

	def execute_block(self, statements: list[Stmt], environment: Environment) -> Any:
		previous: Environment = self._environment

		try:
			self._environment = environment
			for statement in statements:
				self.execute(statement)
		finally:
			self._environment = previous
			return

	@staticmethod
	def _stringify(value: Any):
		if value == None:
			return 'nil'
		else:
			return pretty_print(value)
	
	@staticmethod
	def _isTruthy(value: Any):
		if value is None:
			return False
		if value == 'nil':
			return False
		if isinstance(value, bool):
			return value
		if value == 'true':
			return True
		if value == 'false':
			return False
		return True
	
	@staticmethod
	def _checkNumberOperands(operator: Token, left: Any, right: Any):
		if (
			(isinstance(left, (int, float)) and not isinstance(left, bool)) and
			(isinstance(right, (int, float)) and not isinstance(right, bool))
		):
			return
		else:
			raise LoxRuntimeError(operator, "Operands must be numbers.")
	
	# ----- Handles statements (StmtVisitor) -----

	def visit_var_stmt(self, stmt: Var) -> Any:
		value = None
		if stmt.initializer is not None:
			value = self.evaluate(stmt.initializer)
		self._environment.define(stmt.name.lexeme, value)
		return None
	
	def visit_expression_stmt(self, stmt: Expression) -> None:
		self.evaluate(stmt.expression)
	
	def visit_print_stmt(self, stmt: Print) -> None:
		value = self.evaluate(stmt.expression)
		print(self._stringify(value))

	def visit_block_stmt(self, stmt: Block) -> None:
		new_environment = Environment(self._environment)
		self.execute_block(stmt.statements, new_environment)

	def visit_if_stmt(self, stmt: If) -> Any:
		if self._isTruthy(self.evaluate(stmt.condition)):
			self.execute(stmt.thenBranch)
		elif stmt.elseBranch is not None:
			self.execute(stmt.elseBranch)
		else:
			return None

	# ----- Handles expressions (ExprVisitor) -----

	def visit_literal(self, expr: Literal) -> Any:
		return expr.value
	
	def visit_logical(self, expr: Logical) -> Any:
		left: Expr = self.evaluate(expr.left)

		match expr.operator.type:
			case TokenType.OR:
				if self._isTruthy(left):
					return left
			case TokenType.AND:
				if not self._isTruthy(left):
					return left
		
		return self.evaluate(expr.right)

	def visit_grouping(self, expr: Grouping) -> Any:
		return self.evaluate(expr.expression)
	
	def visit_unary(self, expr: Unary) -> Any:
		right = self.evaluate(expr.right)

		match expr.operator.type:
			case TokenType.MINUS:
				# bool is a subclass of int in Python, hence the explicit exclusion
				if isinstance(right, (int, float)) and not isinstance(right, bool):
					return -(right)
				else:
					raise LoxRuntimeError(expr.operator, "Operand must be a number.")
			case TokenType.BANG:
				return not self._isTruthy(right)
			case _:
				return "nil"
	
	def visit_variable(self, expr: Variable) -> Any:
		return self._environment.get(expr.name)
	
	def visit_binary(self, expr: Binary) -> Any:
		left = self.evaluate(expr.left)
		right = self.evaluate(expr.right)

		match expr.operator.type:
			case TokenType.PLUS:
				if isinstance(left, str) and isinstance(right, str):
					return left + right
				elif (
					(isinstance(left, (int, float)) and not isinstance(left, bool)) and
					(isinstance(right, (int, float)) and not isinstance(right, bool))
				):
					return left + right
				else:
					raise LoxRuntimeError(expr.operator, "Operands must be two numbers or two strings.")
			case TokenType.MINUS:
				self._checkNumberOperands(expr.operator, left, right)
				return left - right
			case TokenType.STAR:
				self._checkNumberOperands(expr.operator, left, right)
				return left * right
			case TokenType.SLASH:
				self._checkNumberOperands(expr.operator, left, right)
				return left / right
			case TokenType.GREATER:
				self._checkNumberOperands(expr.operator, left, right)
				return left > right
			case TokenType.GREATER_EQUAL:
				self._checkNumberOperands(expr.operator, left, right)
				return left >= right
			case TokenType.LESS:
				self._checkNumberOperands(expr.operator, left, right)
				return left < right
			case TokenType.LESS_EQUAL:
				self._checkNumberOperands(expr.operator, left, right)
				return left <= right
			case TokenType.BANG_EQUAL:
				return left != right
			case TokenType.EQUAL_EQUAL:
				return left == right
			case _:
				return None
			
	def visit_assign(self, expr: Assign) -> Any:
		value = self.evaluate(expr.value)
		self._environment.assign(expr.name, value)
		return value
