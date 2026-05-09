from enum import StrEnum


class StreamEvent(StrEnum):
    CHAT_MODEL_STREAM = "on_chat_model_stream"
    CHAT_MODEL_START = "on_chat_model_start"
    CHAT_MODEL_END = "on_chat_model_end"
    TOOL_START = "on_tool_start"
    TOOL_END = "on_tool_end"
