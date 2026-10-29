from .base import BaseTool
class TestReadTool(BaseTool):
    @property
    def name(self)->str:
        return "test_read_tool"

    @property
    def description(self):
        return "it is just a test tool.when you need to read a file, use this tool"

    @property
    def parameters(self)->dict:
        return {
            "type":"object",
            "properties":{
                "path":{
                    "type":"string",
                    "description":"the file path that need to read"
                }
            },
            "required":["path"],
            "additionalProperties":False
        }

    def execute(self,arguments):
        return f"use test tool and arguments is {arguments}"




def main():
    test=TestReadTool()
    schema=test.to_schema()
    print(schema)


if __name__=="__main__":
    main()