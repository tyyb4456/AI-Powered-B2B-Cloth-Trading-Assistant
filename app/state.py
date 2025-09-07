from typing import TypedDict, List, Annotated, Optional
from langgraph.graph.message import add_messages
from models.fabric_detail import ExtractedRequest
from models.supplierdetail import SupplierSearchResult
from models.quotedetail import GeneratedQuote
from models.nagotiation_model import NegotiationStrategy, DraftedMessage
from models.analyze_supplier_response_model import SupplierIntent, ExtractedTerms, NegotiationAnalysis
from datetime import datetime


class AgentState(TypedDict):
    """
    State structure for the procurement agent workflow.
    This defines the shared data structure passed between all nodes.
    """
    # Core identification
    user_id: str
    session_id: str
    channel: str
    status : str
    recipient_email = str
    
    # Message handling
    messages1 : Annotated[list, add_messages] # for nodes ( assistant messages )
    messages : Annotated[list, add_messages] # for branch a tools 
    # messages2 : Annotated[list, add_messages] # for branch b nodes
    msgs : Annotated[list, add_messages] # for branch b tools 
    
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

    # quote generation fields
    generated_quote : GeneratedQuote
    quote_document : str
    quote_id : str
    supplier_options : list[dict]
    estimated_savings : float

    # draft nagotiation fields

    drafted_message : DraftedMessage
    negotiation_strategy : NegotiationStrategy
    message_id : str
    message_ready : bool
    last_message_confidence : float
    supplier_response : str

    # analyze supplier response fields 

    supplier_intent : SupplierIntent
    extracted_terms : ExtractedTerms
    negotiation_analysis : NegotiationAnalysis
    negotiation_advice : str
    negotiation_history : dict
    negotiation_status : str
    analysis_confidence : float
    last_analysis_timestamp : datetime
    
    # Persistence and workflow continuation fields
    quote_sent: Optional[bool] = False
    workflow_phase: Optional[str] = "initial"
    awaiting_user_input: Optional[bool] = False
    human_response: Optional[str] = None
    
