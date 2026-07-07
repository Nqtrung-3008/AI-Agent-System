from langchain_core.tools import tool
from datetime import datetime, timedelta



@tool
def datetime_tool(expression: str) -> str:
    """
    Evaluate datetime expressions.

    Supported:
    - now
    - today
    - tomorrow
    - yesterday
    - +, -, *, /
    - timedelta(days=1), timedelta(hours=1), etc.

    Example:
    now + timedelta(days=1)
    today - timedelta(weeks=1)
    """

    SAFE_FORMS = {
        "now": datetime.now(),
        "today": datetime.now().date(),
        "tomorrow": datetime.now().date() + timedelta(days=1),
        "yesterday": datetime.now().date() - timedelta(days=1),
        "timedelta": timedelta,
    }

    try:
        result = eval(expression, {"__builtins__": None}, SAFE_FORMS)
        return result.isoformat() if hasattr(result, "isoformat") else str(result)
    except Exception as exc:
        return f"Datetime error: {exc}"