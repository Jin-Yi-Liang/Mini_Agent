from .registry import ToolRegistry
from .file_tools import ReadFileTool

def main():
    registry=ToolRegistry()
    read_tool=ReadFileTool("./workspace")

    registry.regist(read_tool)
    tool=registry.get("read_file")

    print(tool.name)
    print(tool is read_tool)

    schemas=registry.get_schema()
    print(len(schemas))

    result=registry.execute("read_file",{
        "path":"README.md"
    })
    print(result)


    # read_tool2=ReadFileTool("./workspace")
    # registry.regist(read_tool2)

if __name__=="__main__":
    main()