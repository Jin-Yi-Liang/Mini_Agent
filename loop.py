import json
from pathlib import Path
from typing import cast

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolUnionParam,
)

from tools.registry import ToolRegistry
from tools.file_tools import ReadFileTool
from agent.react import ReactAgent


client = OpenAI(
    api_key="key",
    base_url="http://10.100.1.114:8000/v1"
)
MODEL_NAME = "Qwen/Qwen3.5-9B"
MAX_STEP=8

registry = ToolRegistry()
read_tool = ReadFileTool("./workspace")
registry.register(read_tool)
tool_schemas = cast(
    list[ChatCompletionToolUnionParam],
    registry.get_schemas()
)

CONTEXT_FILE = Path("context.json")
if CONTEXT_FILE.exists():
    with open(CONTEXT_FILE, "r", encoding="utf-8") as f:
        messages = cast(
            list[ChatCompletionMessageParam],
            json.load(f)
        )
else:
    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": (
                "You are a coding assistant. "
                "You can use the provided tools to inspect files in the workspace. "
                "When the user asks about file contents, use a tool to read the file. "
                "Do not invent file contents."
            )
        }
    ]

agent=ReactAgent(client,MODEL_NAME,registry,messages,MAX_STEP)

# main loop
while True:
    user_input=input("\nUser:").strip()
    if user_input.lower() in ["quit","exit"]:
        break

    agent.run(user_input)
   
    with open(CONTEXT_FILE,"w",encoding="utf-8") as f:
        json.dump(
            messages,
            f,ensure_ascii=False,
            indent=2
        )
        
print("\nAgent stopped.")
# CONTEXT_FILE.unlink()