from langgraph.prebuilt import ToolNode
from backend.src.tools.calculator_tool import calculator_tool
from backend.src.tools.datetime_tool import datetime_tool
from backend.src.tools.weather_tool import weather_tool
from backend.src.tools.note_tool import (note_create,
                                         note_read,
                                         note_update,
                                         note_delete,
                                         note_list)


tools = [calculator_tool,
        datetime_tool,
        weather_tool,
        
        note_create,
        note_read,
        note_update,
        note_delete,
        note_list]

tools_node = ToolNode(tools, name="tools")