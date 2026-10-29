from abc import ABC,abstractmethod

class BaseTool(ABC):

    @property
    @abstractmethod
    def name(self)->str:
        pass

    @property
    @abstractmethod
    def description(self)->str:
        pass

    @property
    @abstractmethod
    def parameters(self)->dict:
        pass

    @abstractmethod
    def execute(self,arguments:dict):
        pass

    def to_schema(self)->dict:
        return {
            "type":"function",
            "function":{
                "name":self.name,
                "description":self.description,
                "parameters":self.parameters
            }
        }