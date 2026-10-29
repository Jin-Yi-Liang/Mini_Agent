from .registry import ToolRegistry
from .file_tools import ReadFileTool
from .test_base import TestReadTool

def main():
    registry=ToolRegistry()
    read_tool=ReadFileTool("./workspace")
    test_read_tool=TestReadTool()

    registry.register(read_tool)
    registry.register(test_read_tool)
    tool=registry.get("read_file")

    print(tool.name)
    print(tool is read_tool)

    schemas=registry.get_schemas()
    print(schemas)

    result=registry.execute("read_file",{
        "path":"README.md"
    })
    print(result)


    # read_tool2=ReadFileTool("./workspace")
    # registry.regist(read_tool2)

if __name__=="__main__":
    main()