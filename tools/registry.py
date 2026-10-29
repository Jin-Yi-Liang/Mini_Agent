from .base import BaseTool

class ToolRegistry:
    def __init__(self):
        self.tools:dict[str,BaseTool]={}

    def register(self,tool:BaseTool)->None:   
        if tool.name in self.tools:
            raise ValueError(
                f"Tool {tool.name} already registed"
            )
        self.tools[tool.name]=tool

    def get(self,name:str)->BaseTool:
        if name not in self.tools:
            raise KeyError(
                f"tool {name} not found"
            )
        return self.tools[name]

    def get_schemas(self)->list[dict]:
        schemas=[]
        for tool in self.tools.values():
            schemas.append(tool.to_schema())
        return schemas

    def execute(self,tool_name:str,arguments:dict)->str:
        tool=self.get(tool_name)
        result=tool.execute(arguments)
        if not result:
            raise ValueError("Error:Tool execute error.The return value of tool execution is null")
        return result