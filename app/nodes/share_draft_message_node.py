from composio import Composio
from composio_langchain import LangchainProvider
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState
from langchain_core.tools import tool
from langgraph.types import Command, interrupt
from langgraph.prebuilt import ToolNode

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize model and composio
model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
composio = Composio(provider=LangchainProvider())

composio_tools = composio.tools.get(
    user_id="0000-0000-0000",  # replace with your composio user_id
    tools=["GMAIL_SEND_EMAIL"]
)

@tool
def get_supplier_response_tool(query: str) -> str:
    """Request suuplier to give the response"""
    human_response = interrupt({"query": query})
    return human_response["data"]

# Combine all tools
all_tools = [get_supplier_response_tool] + composio_tools

# Custom tool node that handles both human assistance and composio tools
def custom_tool_node(state: AgentState):
    # Get the last message which should be an AI message with tool calls
    if not state.get("msgs") or len(state["msgs"]) == 0:
        return {"msgs": [], "error": "No messages in state"}
    
    last_message = state["msgs"][-1]
    
    # Check if last message has tool calls (it should be an AIMessage)
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        tool_call = last_message.tool_calls[0]
        
        if tool_call["name"] == "get_supplier_response_tool":
            # Handle human assistance tool specially
            query = tool_call["args"]["query"]
            human_response_data = interrupt({"query": query})
            
            # Handle different data structures for resume
            if isinstance(human_response_data, dict):
                if "data" in human_response_data:
                    response_text = human_response_data["data"]
                elif "supplier_response" in human_response_data:
                    response_text = human_response_data["supplier_response"]
                else:
                    # If it's a direct string or other structure, use it directly
                    response_text = str(human_response_data)
            else:
                response_text = str(human_response_data)
            
            # Create tool message
            from langchain_core.messages import ToolMessage
            tool_message = ToolMessage(
                content=response_text,
                tool_call_id=tool_call["id"]
            )
            
            # Return updated state with both the tool message and human response stored
            return {
                "msgs": [tool_message],
                "human_response": response_text
            }
        else:
            # Handle Composio tools using regular ToolNode
            # Create a new state with only AI messages for the tool node
            tool_state = {
                "messages": state["msgs"]  # Use the correct key for ToolNode
            }
            composio_tool_node = ToolNode(tools=composio_tools)
            try:
                result = composio_tool_node.invoke(tool_state)
                # Map back to our state structure
                if "messages" in result:
                    return {"msgs": result["messages"]}
                return result
            except Exception as e:
                print(f"Error in composio_tool_node: {e}")
                return {"msgs": [], "error": str(e)}
    
    # If no tool calls or wrong message type, return error
    return {"msgs": [], "error": "Last message is not an AIMessage with tool calls"}

def share_draft_message(state: AgentState):
    """share draft message function that processes user input and calls appropriate tools"""

    draft_message = state['drafted_message']['message_body']

    supplier_name = 'sir'
    company = state.get('user_company', 'biba texttile')
    email = state.get('supplier_email', 'tybhsn001@gmail.com')

    message_to_send = f"""
Dear {supplier_name}

{draft_message}

Best regard {company}
    """

    # Create system prompt - LLM can call any tool it needs
    system_prompt = f"""You are an email processing assistant. You have access to all these tools:
    - GMAIL_SEND_EMAIL: to send emails
    - get_supplier_response_tool: to get the supplier response

    Your task:
    1. Send this email content: "{message_to_send}" to email: "{email}"
    2. After sending, use get_supplier_response_tool tool to get supplier's response
    3. Use any other tools as needed

    call the tools in sequence and step by step as follow the pattern"""
    
    # Create prompt with system message
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}"),
    ])

    # Format messages
    formatted_messages = prompt.format_messages(messages=state["msgs"])
    
    # Get response from model with all tools available
    response = model.bind_tools(all_tools).invoke(formatted_messages)
    return {"msgs": [response]}