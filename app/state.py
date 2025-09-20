from typing import TypedDict, List, Annotated, Optional
from langgraph.graph.message import add_messages
from models.fabric_detail import ExtractedRequest
from models.supplierdetail import SupplierSearchResult
from models.quotedetail import GeneratedQuote
from models.nagotiation_model import NegotiationStrategy, DraftedMessage
from models.analyze_supplier_response_model import SupplierIntent, ExtractedTerms, NegotiationAnalysis
from models.contract_model import DraftedContract, ContractTerms, ContractMetadata, ContractReview
from datetime import datetime
from models.esclation_model import EscalationSummary, HumanInterventionRequest


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
    negotiation_history : List[dict]
    negotiation_status : str
    analysis_confidence : float
    last_analysis_timestamp : datetime

    # esclation to human fields

    escalation_summary : EscalationSummary
    intervention_request : HumanInterventionRequest
    
    # contract drafting fields
    drafted_contract : Optional[DraftedContract] = None
    contract_terms : Optional[ContractTerms] = None
    contract_metadata : Optional[ContractMetadata] = None
    contract_id : Optional[str] = None
    contract_ready : bool = False
    contract_confidence : float = 0.0
    contract_review : Optional[ContractReview] = None
    requires_legal_review : bool = True
    contract_generation_timestamp : Optional[datetime] = None
