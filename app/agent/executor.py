import logging
from typing import Dict, Any, Optional
from app.agent.registry import registry

# Import tools module to ensure all tools are decorated and registered
import app.agent.tools

logger = logging.getLogger(__name__)

def execute_tool(name: str, arguments: Optional[Dict[str, Any]], user_id: Optional[int] = None) -> Any:
    """
    Executes a registered tool by name with the given arguments.
    Injects user_id if the tool requires it.
    
    Args:
        name: Name of the tool to execute.
        arguments: Keyword arguments to pass to the tool.
        user_id: The ID of the user requesting the tool execution.
        
    Returns:
        The result of the tool execution, or a dictionary describing the failure.
    """
    if not arguments:
        arguments = {}

    tool = registry.get_tool(name)
    if not tool:
        logger.error(f"Execution failed: Tool '{name}' not found in registry.")
        return {
            "success": False,
            "error": f"Tool '{name}' is not registered."
        }

    try:
        logger.info(f"Executing tool '{name}' (user_id={user_id}) with arguments: {arguments}")
        result = tool.execute(user_id=user_id, **arguments)
        return result
    except Exception as e:
        logger.exception(f"Error executing tool '{name}' with arguments {arguments}: {e}")
        return {
            "success": False,
            "error": f"Execution failed: {str(e)}"
        }
