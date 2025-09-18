from langchain_core.messages import SystemMessage
from utils.state import State
from utils.llm import llm_with_tools 

def assistant(state: State):
    """Main assistant function that calls the model"""
    
    # Add system message if it's the first interaction
    messages = state['messages']
    if not any(isinstance(msg, SystemMessage) for msg in messages):
        system_prompt = """You are a helpful medical assistant for Community Health Center Harichandanpur in Keonjhar, Odisha.
You have access to tools that can help you:
1. Search hospital policies and procedures
2. Get current date and time
3. Get information about the hospital owner Dr. Harshin
Always use the appropriate tools to provide accurate information. Be professional, helpful, and caring in your responses. If medical advice is requested that requires professional diagnosis, remind users to consult with healthcare professionals."""
        messages = [SystemMessage(content=system_prompt)] + messages
   
    return {"messages": [llm_with_tools.invoke(messages)]}