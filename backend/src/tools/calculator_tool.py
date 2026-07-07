from langchain_core.tools import tool
import math, statistics

SAFE_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,

    "sqrt": math.sqrt,
    "pow": pow,
    "factorial": math.factorial,

    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,

    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,

    "log": math.log,
    "log10": math.log10,
    "ln": math.log,

    "floor": math.floor,
    "ceil": math.ceil,

    "mean": statistics.mean,
    "median": statistics.median,
    "stdev": statistics.stdev,
    "variance": statistics.variance,

    "pi": math.pi,
    "e": math.e,
}

@tool
def calculator_tool(expression: str) -> float:
    """
    Evaluate mathematical expressions.

    Supported:
    - + - * / %
    - **
    - sqrt()
    - sin(), cos(), tan()
    - log(), log10()
    - factorial()
    - abs()
    - round()
    - min(), max()
    - pi, e

    Example:
    sqrt(16)
    2**10
    sin(pi/2)
    """
    
    try:
        result = eval(expression, {"__builtins__": None}, SAFE_FUNCTIONS)
        return str(result)
    except Exception as exc:
        return f"Calculator error: {exc}"