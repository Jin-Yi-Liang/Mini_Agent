from base import BaseTool
class TestReadTool(BaseTool):
    @property
    def name(self)->str:
        return "test tool"

    @property
    def description(self):
        return "test tool:when you need to read a file use this tool"

    @property
    def parameters(self)->dict:
        return {
            "type":"object",
            "properties":{
                "type":"string",
                "description":"the file path that need to read"
            },
            "required":["path"],
            "additionProperties":False
        }

    def execute(self,arguments):
        return "use test tool and arguments is ",arguments

test=TestReadTool()
print(test.name)
print(test.description)
print(test.parameters)
print(test.execute({"path":"jjj"}))