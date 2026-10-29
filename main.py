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


# ==================================================
# 1. Model Client
# ==================================================

client = OpenAI(
    api_key="key",
    base_url="http://10.100.1.114:8000/v1"
)
MODEL_NAME = "Qwen/Qwen3.5-9B"


# ==================================================
# 2. Tool Registry
# ==================================================

registry = ToolRegistry()
read_tool = ReadFileTool("./workspace")
registry.register(read_tool)
tool_schemas = cast(
    list[ChatCompletionToolUnionParam],
    registry.get_schemas()
)


# ==================================================
# 3. History
# ==================================================

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


# ==================================================
# 4. Main Loop
# ==================================================

while True:
    user_input = input("\nUser: ").strip()
    if user_input.lower() in ["quit", "exit"]:
        break
    if not user_input:
        continue

    # 4.1 保存用户消息
    messages.append({
        "role": "user",
        "content": user_input
    })

    # 4.2 第一次调用模型
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=tool_schemas,
        tool_choice="auto",
        extra_body={
            "thinking": {
                "type": "disabled"
            }
        }
    )

    model_message = response.choices[0].message

    print(
        "\nFinish Reason:",
        response.choices[0].finish_reason
    )

    # ==================================================
    # 5. Tool Calling
    # ==================================================

    if model_message.tool_calls:
        print("\n[Agent] Model requested tool calls.")

        # 5.1 保存 Assistant 的完整 Tool Call 消息到 context 中
        tool_calls_data = [
            call.model_dump(exclude_none=True)
            for call in model_message.tool_calls
        ]

        messages.append(
            cast(
                ChatCompletionMessageParam,
                {
                    "role": "assistant",
                    "content": model_message.content,
                    "tool_calls": tool_calls_data
                }
            )
        )

        # 5.2 遍历并执行每个 Tool Call
        for call in model_message.tool_calls:

            print("\n========== TOOL CALL ==========")
            print("Tool ID:", call.id)

            try:
                if call.type != "function":
                    raise ValueError(
                        "Unsupported tool call type"
                    )

                tool_name = call.function.name

                # JSON 字符串转换为 Python 对象
                arguments = json.loads(
                    call.function.arguments
                )
                if not isinstance(arguments, dict):
                    raise ValueError(
                        "Tool arguments must be a JSON object"
                    )

                print("Tool Name:", tool_name)
                print("Arguments:", arguments)

                # 真正执行工具
                result = registry.execute(
                    tool_name,
                    arguments
                )

            except Exception as e:
                result = f"Tool execution error: {e}"

            print("Tool Result:", result)
            print("===============================")

            # 5.3 保存 Tool Observation
            messages.append(
                cast(
                    ChatCompletionMessageParam,
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": result
                    }
                )
            )

        # ==================================================
        # 6. 再次调用模型
        # ==================================================

        final_response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            extra_body={
                "thinking": {
                    "type": "disabled"
                }
            }
        )

        final_message = final_response.choices[0].message

        final_content = final_message.content or ""

        print("\nAssistant:", final_content)

        # 保存最终回答
        messages.append({
            "role": "assistant",
            "content": final_content
        })

    # ==================================================
    # 7. 模型没有调用工具
    # ==================================================

    else:

        model_content = model_message.content or ""
        print("\nAssistant:", model_content)

        messages.append({
            "role": "assistant",
            "content": model_content
        })

    # ==================================================
    # 8. 保存完整 History
    # ==================================================

    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            messages,
            f,
            ensure_ascii=False,
            indent=2
        )

print("\nAgent stopped.")