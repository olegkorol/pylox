from typing import Any


def pretty_print(value: Any):
	"""
	Pretty-printer to satisfy:
	> For the number literals, the tester will check that the program prints the number
	  with the minimum number of decimal places without losing precision.
	  (For example, 10.40 should be printed as 10.4).
	"""
	match value:
		case float():
			return f"{value:g}"
		case None:
			return "nil"
		case bool():
			return str(value).lower()
		case _:
			return value