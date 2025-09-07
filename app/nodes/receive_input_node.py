from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

from state import AgentState
import uuid

# # Pydantic Models for structured data
# class UserMessage(BaseModel):
#     """Model for incoming user messages"""
#     user_id: str = Field(..., description="Unique identifier for the trader/company")
#     message: str = Field(..., description="The raw text message from the user")
#     channel: Literal["whatsapp", "web_portal", "email", "api"] = Field(..., description="Communication channel")
#     timestamp: datetime = Field(default_factory=datetime.now, description="When the message was received")


def generate_item_id() -> str:
    """Generate unique item ID for the request"""
    return f"req_{str(uuid.uuid4())[:8]}"


def receive_input(state: AgentState):
    """
    Node 1: receive_input - Entry point of the LangGraph workflow
    
    Purpose:
    - Initialize the conversation state
    - Store raw user input for downstream processing
    - Set the next step in the workflow
    - Establish the foundation for all subsequent nodes
    
    Args:
        state: Current agent state (may be empty for initial call)
    
    Returns:
        dict: State updates to be merged into the current state
    """
    
    # Create the user message tuple for LangGraph message handling
    user_message = state['user_input']
    session_id = state.get("session_id") or str(uuid.uuid4())
    channel = state.get("channel") or "api"
    

    # This is initial input - normal flow
    assistant_message = f"Received your message via {channel}. Processing..."
    update_state = {
        'messages1': [user_message, assistant_message],
        'channel': 'whatsapp',
        'session_id': session_id,
        'next_step': 'intent_classification',
        'status': 'received_user_input',
    }

    return update_state
