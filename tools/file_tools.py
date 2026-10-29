from pathlib import Path
from .base import BaseTool

class ReadFileTool(BaseTool):
    def __init__(self,workspace:str):
        self.workspace=Path(workspace).resolve()

        if not self.workspace.is_dir():
            raise ValueError(
                f"working space is not exists:{self.workspace}"
            )

    @property
    def name(self)->str:
        return "read_file"

    @property
    def description(self)->str:
        return "read specific file in your working space"

    @property
    def parameters(self)->dict:
        return {
            "type":"object",
            "properties":{
                "path":{
                    "type":"string",
                    "description":"the relative file path based on your working space"
                }
            },
            "required":["path"],
            "additionalProperties":False
        }

    def execute(self,arguments:dict):
        ## get target file path and valid it
        path=arguments.get("path")
        if not isinstance(path,str) or not path.strip():
            return "Error:path must be non-blanking string"

        requested=Path(path)
        if(requested.is_absolute()):
            return "Error:please use the relative path based on your working space"
        
        target=(self.workspace/path).resolve()
        if not target.is_relative_to(self.workspace):
            return "Error:you are forbidden to access files out of your working space"

        if not target.is_file():
            return f"Error:file does not existed or not a normal file:{target}"

        ## try to read file from file-system
        try:
            content=target.read_text(encoding="utf-8")
            return content
        except UnicodeDecodeError:
            return f"Error:file {target} is not a valid utf-8 text file"
        except OSError as e:
            return f"Error:read file failed due to os:{e}"
        