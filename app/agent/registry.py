from typing import Callable, Any, Dict, List, Type, Optional
from pydantic import BaseModel

class Tool:
    """
    Wraps a python function to act as an agent tool.
    Validates arguments using a Pydantic schema and formats the tool specification.
    """
    def __init__(
        self,
        name: str,
        description: str,
        args_schema: Type[BaseModel],
        func: Callable[..., Any],
        requires_user_id: bool = True
    ):
        self.name = name
        self.description = description
        self.args_schema = args_schema
        self.func = func
        self.requires_user_id = requires_user_id

    def execute(self, user_id: Optional[int], **kwargs) -> Any:
        """
        Executes the tool function with the provided keyword arguments.
        Automatically injects user_id if required.
        """
        # Validate arguments using the schema
        validated = self.args_schema(**kwargs)
        args_dict = validated.model_dump()

        if self.requires_user_id:
            if user_id is None:
                raise ValueError(f"Tool '{self.name}' requires a user_id but none was provided.")
            return self.func(user_id=user_id, **args_dict)
        else:
            return self.func(**args_dict)

    def to_tool_spec(self) -> Dict[str, Any]:
        """
        Returns the OpenAI/Groq function calling tool representation of this tool.
        """
        schema = self.args_schema.model_json_schema()
        cleaned_schema = self._clean_schema(schema)
        
        if cleaned_schema.get("type") == "object" and "required" not in cleaned_schema:
            cleaned_schema["required"] = []
            
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": cleaned_schema
            }
        }

    def _clean_schema(self, schema: Any) -> Any:
        """
        Recursively simplifies JSON Schema to make it fully compatible with Groq/Llama 3 tool use.
        Specifically flattens optional fields (e.g. 'anyOf' with null) and removes titles.
        """
        if not isinstance(schema, dict):
            return schema
            
        cleaned = {}
        for k, v in schema.items():
            if k == "title" and isinstance(v, str):
                continue
            if k == "default" and v is None:
                continue
                
            if k == "anyOf" and isinstance(v, list):
                # Filter out null type and find the actual type
                non_null = []
                for item in v:
                    if isinstance(item, dict) and item.get("type") != "null":
                        non_null.append(item)
                if len(non_null) == 1:
                    # Flatten the single non-null type into the current object keys
                    cleaned.update(self._clean_schema(non_null[0]))
                    continue
                elif len(non_null) > 1:
                    # Keep anyOf list but clean each schema
                    cleaned[k] = [self._clean_schema(item) for item in non_null]
                    continue

            # Recursively clean dict values
            if isinstance(v, dict):
                cleaned[k] = self._clean_schema(v)
            elif isinstance(v, list):
                cleaned[k] = [self._clean_schema(item) if isinstance(item, dict) else item for item in v]
            else:
                cleaned[k] = v
                
        return cleaned


class ToolRegistry:
    """
    Registry for managing available agent tools.
    """
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool with name '{tool.name}' is already registered.")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        return list(self._tools.values())

    def get_tool_specs(self) -> List[Dict[str, Any]]:
        return [tool.to_tool_spec() for tool in self.list_tools()]

    def register_tool(self, name: str, description: str, args_schema: Type[BaseModel], requires_user_id: bool = True):
        """
        Decorator to register a tool function in the registry.
        """
        def decorator(func: Callable[..., Any]):
            tool = Tool(
                name=name,
                description=description,
                args_schema=args_schema,
                func=func,
                requires_user_id=requires_user_id
            )
            self.register(tool)
            return func
        return decorator


# Global instance of the ToolRegistry
registry = ToolRegistry()
