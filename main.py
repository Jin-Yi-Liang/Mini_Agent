import os
import json
from pathlib import Path
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from typing import cast

# client
client=OpenAI(
    api_key=os.environ["DEEPSEEK_API_KEY"],
    base_url="http://10.100.1.114:8000/v1"
)

# context
CONTEXT_FILE=Path("context.json")
messges:list[ChatCompletionMessageParam]

if CONTEXT_FILE.exists():
    with open(CONTEXT_FILE,"r",encoding="utf-8") as f:
        messages=cast(
            list[ChatCompletionMessageParam],
            json.load(f)
        )
else:
    messages=cast(
        list[ChatCompletionMessageParam],
        [{
            "role":"system",
            "content":"you are a teacher in machine learning,you can only answer me in your parameter memory,which means you can not use web search tool"
        }]
    )

    with open(CONTEXT_FILE,"w",encoding="utf-8") as f:
        json.dump(messages,f,ensure_ascii=True,indent=2)

# main loop
while True:
    user_input=input("\nUser: ").strip()

    if user_input.lower() in ["quit","exit"]:
        break
    if not user_input:
        continue

    messages.append({
        "role":"user",
        "content":user_input
    })

    response=client.chat.completions.create(
        model="Qwen/Qwen3.5-9B",
        messages=messages,
        extra_body={
            "thinking":{
                "type":"disabled"
            }
        }
    )

    model_message=response.choices[0].message
    model_content=model_message.content or ""
    print("model:",model_content)

    messages.append({
        "role":"assistant",
        "content":model_content
    })

    with open(CONTEXT_FILE,"w",encoding="utf-8") as f:
        json.dump(messages,f,ensure_ascii=False,indent=2)

if CONTEXT_FILE.exists():
    CONTEXT_FILE.unlink()
messages.clear()