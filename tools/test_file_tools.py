from .file_tools import ReadFileTool

def main():
    tool=ReadFileTool("./workspace")

    print(tool.name)
    print(tool.description)
    print(tool.parameters)
    print(tool.to_schema())

    result=tool.execute({
        "path":123
    })
    print(result)

if __name__=="__main__":
    main()