from composio import Composio
from composio_langchain import LangchainProvider
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

from langchain_core.prompts import ChatPromptTemplate
from state import AgentState

# Load environment variables
load_dotenv()

# Initialize model and composio
model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
composio = Composio(provider=LangchainProvider())


tools_list = composio.tools.get(
    user_id="0000-0000-0000",  # replace with your composio user_id
    tools=["TEXT_TO_PDF_CONVERT_TEXT_TO_PDF", "GMAIL_SEND_EMAIL", "GOOGLEDRIVE_UPLOAD_FILE"]
)

# Bind tools with the model
llm_with_tools = model.bind_tools(tools_list)


def send_output_to_user(state: AgentState):
    """The function that calls appropriate tools to convert quote document to PDF and send it to user via email"""

    document = state.get('quote_document', 'the quote could not generated')
    email = 'tybhsn001@gmail.com'

    # Create system prompt focused on the specific task
    system_prompt = f"""You are a PDF processing assistant. Your only job is to:
    1. Convert text content to PDF
    2. Send the PDF via email

    The text content is "{document}" and email address is "{email}". You should:
    1. First use TEXT_TO_PDF_CONVERT_TEXT_TO_PDF to convert the text to PDF
    2. Then use GMAIL_SEND_EMAIL to send the PDF to the specified email address

    Use GOOGLEDRIVE_UPLOAD_FILE if needed.

    Always follow this sequence and be concise in your responses."""
    # Create prompt with system message
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("placeholder", "{messages}"),
    ])

    # Format messages
    formatted_messages = prompt.format_messages(messages=state["messages"])
    
    # Get response from model
    response = llm_with_tools.invoke(formatted_messages)
    
    # Mark that quote has been sent and workflow should continue for negotiation
    return {
        "messages": [response],
        "quote_sent": True,
        "workflow_phase": "awaiting_negotiation",
        "next_step": "negotiate_quote",
        "status": "quote_sent_awaiting_negotiation"
    }
