import json
from typing import cast

from openai import OpenAI

from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionToolUnionParam,
)

from tools.registry import ToolRegistry

class ReactAgent:
    def __init__(
            self,
            client:OpenAI,
            model_name:str,
            registry:ToolRegistry,
            messages:list[ChatCompletionMessageParam],
            max_step:int=8):
        self.client=client
        self.model_name=model_name
        self.registry=registry
        self.messages=messages
        self.max_step=max_step

    def run(self,task:str)->str|None:
        if not task.strip():
            raise ValueError("Task can not be blank")
        self.messages.append({
            "role":"user",
            "content":task
        })

        for i in range(0,self.max_step):
            print(f"Agent step:{i+1}")
            response=self.client.chat.completions.create(
                model=self.model_name,
                messages=self.messages,
                tools=cast(list[ChatCompletionToolUnionParam],self.registry.get_schemas()),
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
                return None
    
            # tool call
            if model_message.tool_calls:
                print(f"tool_call:{model_message.tool_calls}")
                tool_calls_data=[
                    call.model_dump(exclude_none=True)
                    for call in model_message.tool_calls
                ]
    
                self.messages.append(cast(
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
                        result=self.registry.execute(tool_name,tool_arguments)
                    except Exception as e:
                        result=f"tool execution error:{e}"
    
                    self.messages.append(cast(
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
                self.messages.append({
                    "role":"assistant",
                    "content":final_content
                })
                return final_content
        else:
            print(f"maximum steps reached:{i}")
            return None
