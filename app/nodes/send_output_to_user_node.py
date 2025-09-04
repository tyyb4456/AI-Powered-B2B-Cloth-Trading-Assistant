from composio import Composio
from composio_langchain import LangchainProvider
from datetime import datetime
from langchain.chat_models import init_chat_model
from state import AgentState
from dotenv import load_dotenv


load_dotenv()

model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")
composio = Composio(provider=LangchainProvider())


def tool_s():
    tool_list = composio.tools.get(
        user_id="0000-0000-0000",  # replace with your composio user_id
        tools=["TEXT_TO_PDF_CONVERT_TEXT_TO_PDF", "GMAIL_SEND_EMAIL", "GOOGLEDRIVE_UPLOAD_FILE"]
    )
    return tool_list

tools_list = tool_s()

# Bind tools with the model
llm_with_tools = model.bind_tools(tools_list)

def document_sender(state: AgentState):
    """
    Process document conversion, upload to Google Drive, and email sharing.
    
    Args:
        state (AgentState): Current agent state containing document and other data
        
    Returns:
        dict: Updated state with assistant message
    """
    document = state.get('quote_document', "")
    recipient_email = state.get('recipient_email', 'tybhsn001@gmail.com')
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"Quote_Document_{current_time}.pdf"
    
    # Validate inputs
    if not document or document.strip() == "":
        return {
            'messages': [{"role": "assistant", "content": "Error: No document content provided for conversion."}]
        }
    
    # Enhanced prompt with clear instructions and error handling
    prompt = f"""You must use the available tools to process this document. Execute these steps:

Step 1: Use TEXT_TO_PDF_CONVERT_TEXT_TO_PDF to convert this content to PDF:
Content: {document}

Step 2: Use GOOGLEDRIVE_UPLOAD_FILE to upload the PDF to Google Drive

Step 3: Use GMAIL_SEND_EMAIL to send the document link to {recipient_email}
Subject: "Textile Procurement Quote - {filename}"
Body: "Please find attached your textile procurement quote. You can access the PDF document via the Google Drive link provided."

Execute these tools now."""

    try:
        # Use the model with tools bound
        response = llm_with_tools.invoke(prompt)

        return {
            'messages': [response]
        }
    except Exception as e:
        error_message = f"Error in document processing: {str(e)}"
        return {
            'messages': [{"role": "assistant", "content": error_message}]
        }