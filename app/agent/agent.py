import json
import logging
from typing import List, Dict, Any, Optional
from app.llm_service import client
from app.agent.registry import registry
from app.agent.executor import execute_tool
from app.agent.prompts import get_system_prompt
from app.services import (
    task_service,
    event_service,
    memory_service,
    chat_history_service
)

logger = logging.getLogger(__name__)

def get_relevant_tools(user_message: str) -> List[Dict[str, Any]]:
    """
    Selects a subset of tools relevant to the user query.
    This prevents Groq tool use compiler limitations when handling too many tools.
    """
    msg_lower = user_message.lower()
    
    task_tools = ['create_task', 'list_tasks', 'complete_task', 'delete_task']
    habit_tools = ['create_habit', 'list_habits', 'log_habit', 'get_habit_streak']
    event_tools = ['create_event', 'list_events', 'upcoming_events']
    memory_tools = ['add_memory', 'list_memories', 'delete_memory']
    
    selected_names = set()
    
    is_task = any(kw in msg_lower for kw in ["task", "todo", "buy", "clean", "job", "work", "complete", "done", "finish", "pending", "remind"])
    is_habit = any(kw in msg_lower for kw in ["habit", "streak", "track", "log", "daily", "routine"])
    is_event = any(kw in msg_lower for kw in ["event", "meet", "appointment", "schedule", "calendar", "tomorrow", "today", "upcoming", "date", "time", "plan"])
    is_memory = any(kw in msg_lower for kw in ["memory", "remember", "forget", "recall", "fact", "tell you", "told you", "know about"])
    
    if is_task:
        selected_names.update(task_tools)
    if is_habit:
        selected_names.update(habit_tools)
    if is_event:
        selected_names.update(event_tools)
    if is_memory:
        selected_names.update(memory_tools)
        
    # Broad or general requests include lists across categories
    if not selected_names or any(kw in msg_lower for kw in ["today", "overview", "summary", "schedule", "do", "plan", "hello", "hi"]):
        selected_names.update(['list_tasks', 'list_habits', 'upcoming_events', 'list_memories'])
        if any(kw in msg_lower for kw in ["add", "create", "new"]):
            selected_names.update(['create_task', 'create_event', 'create_habit', 'add_memory'])
            
    if not selected_names:
        selected_names.update(['list_tasks', 'list_memories'])

    all_specs = registry.get_tool_specs()
    return [spec for spec in all_specs if spec['function']['name'] in selected_names]

def run_agent(user_message: str, user_id: int, history: Optional[List[Dict[str, Any]]] = None) -> str:
    """
    Runs the agent loop. Sends user message and history to the LLM with available tools.
    Executes tool calls requested by the LLM and feeds the results back until a final answer is returned.
    
    Args:
        user_message: The message input by the user.
        user_id: The database user ID of the requesting user.
        history: Optional list of past messages in the conversation.
        
    Returns:
        The final response text from the agent.
    """
    # 1. Load conversation history if not explicitly provided
    if history is None:
        try:
            history = chat_history_service.get_chat_history(user_id, limit=10)
        except Exception as e:
            logger.error(f"Error loading chat history: {e}")
            history = []

    # 2. Retrieve user context for system prompt injection
    try:
        memories = memory_service.list_memories(user_id)
    except Exception as e:
        logger.error(f"Error listing memories for context: {e}")
        memories = None
        
    try:
        tasks = task_service.list_tasks(user_id, status='pending')
    except Exception as e:
        logger.error(f"Error listing tasks for context: {e}")
        tasks = None
        
    try:
        events = event_service.upcoming_events(user_id, limit=5)
    except Exception as e:
        logger.error(f"Error listing events for context: {e}")
        events = None

    # 3. Prepare messages with dynamic system prompt
    system_prompt = get_system_prompt(
        current_time=None,
        memories=memories,
        tasks=tasks,
        events=events
    )
    
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    # 4. Add history
    if history:
        messages.extend(history)
        
    # 5. Add current user message
    messages.append({"role": "user", "content": user_message})
    
    # 6. Get available tools dynamically
    tools = get_relevant_tools(user_message)
    tool_args = {"tools": tools} if tools else {}
    
    max_iterations = 5
    iteration = 0
    
    while iteration < max_iterations:
        iteration += 1
        try:
            logger.info(f"Agent loop iteration {iteration} for user {user_id}")
            
            # Send message to Groq (Llama 3.3 70B)
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.0,
                **tool_args
            )
            
            assistant_message = completion.choices[0].message
            tool_calls = assistant_message.tool_calls
            
            # If model didn't call any tools, this is the final answer
            if not tool_calls:
                logger.info("Agent execution completed with final text response.")
                final_response = assistant_message.content or ""
                
                try:
                    chat_history_service.add_chat_message(user_id, "user", user_message)
                    chat_history_service.add_chat_message(user_id, "assistant", final_response)
                except Exception as history_err:
                    logger.error(f"Error saving chat message to history: {history_err}")
                    
                return final_response
                
            # If tool calls are requested, we must append the assistant message (with tool calls) to context
            assistant_msg_dict = {
                "role": "assistant",
                "content": assistant_message.content
            }
            
            # Build tool calls structure for API history
            tool_calls_list = []
            for tc in tool_calls:
                tool_calls_list.append({
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })
            assistant_msg_dict["tool_calls"] = tool_calls_list
            messages.append(assistant_msg_dict)
            
            # Execute each requested tool call
            for tc in tool_calls:
                tool_name = tc.function.name
                tool_args_str = tc.function.arguments
                
                try:
                    tool_arguments = json.loads(tool_args_str)
                    if not isinstance(tool_arguments, dict):
                        tool_arguments = {}
                except Exception as json_err:
                    logger.error(f"Failed to parse tool arguments JSON: {tool_args_str}. Error: {json_err}")
                    tool_arguments = {}
                    
                # Run the tool via Executor
                result = execute_tool(tool_name, tool_arguments, user_id=user_id)
                
                # Append tool result to context
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tool_name,
                    "content": json.dumps(result)
                })
                
        except Exception as e:
            logger.exception(f"Exception encountered in agent loop at iteration {iteration}: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
            
    logger.warning("Reached max iterations limit (5) in run_agent loop.")
    return "I apologize, but I reached my reasoning limit while trying to complete your request."
