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

# main loop

while True:
    user_input=input("\nUser:").strip()
    if user_input.lower() in ["quit","exit"]:
        break
    if not user_input:
        continue
    messages.append({
        "role":"user",
        "content":user_input
    })

    for i in range(0,MAX_STEP):
        print(f"Agent step:{i+1}")
        response=client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=tool_schemas,
            tool_choice="auto",
            extra_body={
                "thinking":{
                    "type":"disabled"
                }
            }
        )

        model_message=response.choices[0].message
        finish_reason=response.choices[0].finish_reason
        print(f"finish reason:{finish_reason}")
        if(finish_reason=="length"):
            print("model reach generation limit")
            break

        # tool call
        if model_message.tool_calls:
            print(f"tool_call:{model_message.tool_calls}")
            tool_calls_data=[
                call.model_dump(exclude_none=True)
                for call in model_message.tool_calls
            ]

            messages.append(cast(
                ChatCompletionMessageParam,
                {
                    "role":"assistant",
                    "content":model_message.content,
                    "tool_calls":tool_calls_data
                }
            ))

            for call in model_message.tool_calls:
                tool_id=call.id
                try:
                    if call.type!="function":
                        raise ValueError("unsupported tool type")
                    tool_name=call.function.name
                    tool_arguments=json.loads(call.function.arguments)
                    if not isinstance(tool_arguments,dict):
                        raise ValueError("tool atguments must be a JSON object")
                    result=registry.execute(tool_name,tool_arguments)
                except Exception as e:
                    result=f"tool execution error:{e}"

                messages.append(cast(
                    ChatCompletionMessageParam,
                    {
                        "role":"tool",
                        "tool_call_id":tool_id,
                        "content":result
                    }
                ))
            continue
        else:
            final_content=model_message.content or ""
            print(f"Assistant:{repr(final_content)}")
            messages.append({
                "role":"assistant",
                "content":final_content
            })
            break
    else:
        print(f"maximum steps reached:{MAX_STEP}")

    with open(CONTEXT_FILE,"w",encoding="utf-8") as f:
        json.dump(
            messages,
            f,ensure_ascii=False,
            indent=2
        )
print("\nAgent stopped.")
# CONTEXT_FILE.unlink()