from typing import TypedDict, List, Annotated, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from models.fabric_detail import ExtractedRequest
from models.supplierdetail import SupplierSearchResult
from models.quotedetail import GeneratedQuote


class AgentState(TypedDict):
    """
    State structure for the procurement agent workflow.
    This defines the shared data structure passed between all nodes.
    """
    # Core identification
    user_id: str
    session_id: str
    channel: str
    
    # Message handling
    messages: Annotated[list, add_messages]
    user_input: str

    
    # Workflow control
    next_step: str

    extracted_parameters: Optional[ExtractedRequest] = None
    needs_clarification: bool = False
    clarification_questions: Optional[List[str]] = None
    missing_info: Optional[List[str]] = None

    # intent classification fields

    intent: Optional[str] = None
    intent_confidence: Optional[float] = None
    intent_reasoning: Optional[str] = None

    # supplier sourcing fields

    supplier_search_results : Optional[SupplierSearchResult] = None
    top_suppliers: Optional[List[dict]] = None
    search_confidence: Optional[float] = None
    market_insights: Optional[str] = None
    alternative_suggestions: Optional[List[str]] = None

    # quote geneation fields

    generated_quote : GeneratedQuote
    quote_document : str
    quote_id : str
    supplier_options : list[dict]
    estimated_savings : float
    